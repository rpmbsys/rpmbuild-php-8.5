---
name: Build optimizations
description: Build-time/dependency optimizations for the PHP 8.5 build. mysql*-devel dropped from the base Dockerfiles because the build uses mysqlnd (no libmysqlclient needed). Tracks applied and candidate optimizations.
type: project
---
## Applied

- **Dropped `mysql*-devel` from the base Dockerfiles** (2026-06-18): `mysql8.4-devel` from `Dockerfile.base`, `mysql-devel` from `Dockerfile.RL9.base`.
  - **Why safe:** the spec builds with `--with-mysqli=mysqlnd` and `--with-pdo-mysql=mysqlnd` (php.spec ~943–944). **mysqlnd is the bundled native driver — it does not link `libmysqlclient`**, so no MySQL client dev package is needed to compile. The only consumer of `mysql_config` is the socket-path default `%global mysql_sock %(mysql_config --socket 2>/dev/null || echo /var/lib/mysql/mysql.sock)` (php.spec ~122), which falls back gracefully.
  - **Only effect:** the compiled-in default socket becomes `/var/lib/mysql/mysql.sock` (the RHEL standard; overridable at runtime via `mysqli.default_socket` / `pdo_mysql.default_socket`).
  - **Win:** smaller/faster base image, fewer build deps, and removes reliance on the custom `mysql8.4-devel` package.
  - **Matching spec cleanup:** dropped the now-dead `%global mysql_config` macro + comment (never referenced; pointed at a binary no longer installed) and replaced the `%(mysql_config --socket || echo …)` detection with the literal `%global mysql_sock /var/lib/mysql/mysql.sock` (the fallback it would always hit now). `%{mysql_sock}` is still used at `--with-mysql-sock`. The spec has **no** mysql/mariadb `BuildRequires`, so the build doesn't fail without the dev package.

## Candidate (not yet applied — operator decision)

- **ccache** — not used today. The four SAPI builds (apache/cli/cgi/fpm) each compile the PHP core from the same sources; ccache turns repeats + iterative rebuilds into cache hits. Needs `ccache` in the `aursu/rpmbuild` base + CC/PATH wiring. Biggest speedup for the manual build loop.
- **opcache JIT** — not configured (off). Capstone is built so JIT is available; `opcache.jit=tracing` + `opcache.jit_buffer_size` helps CLI/compute, ~neutral for typical web. Keep off by default; document as a per-deployment tunable.
- **`pcre.jit=0`** (SOURCES/php.ini) — disabled long ago for an SELinux AVC; likely fixed now, re-enabling is a small free regex win (verify SELinux first).

## Verified already-optimal (no action)

- `make test` is gated behind `%if %{with_test}` — normal builds skip it.
- Shared extensions are built **once** (in the CGI pass); other SAPIs use `$without_shared`.
- debuginfo disabled (`debug_package %{nil}`), `%{?_smp_mflags}` parallelism, hardened build on.
- **LTO intentionally disabled** (`%define _lto_cflags %{nil}`) — the upstream/Remi default (PHP+LTO has been problematic); leave it.

See [[review-8.5-assets]] for the feature/extension review.
