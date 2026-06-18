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

- **ccache wired in** (2026-06-18): `ccache` installed in `Dockerfile.base` + `Dockerfile.RL9.base`; `ENV PATH=/usr/lib64/ccache:$PATH` (RHEL ccache compiler wrappers), `CCACHE_DIR=/home/centos/.ccache` (build user's home, `chown $BUILD_USER` so a named volume inherits ownership), `CCACHE_MAXSIZE=3G`. Persistent cache volumes added to compose: `ccache10rocky` (docker-compose.yml) and `ccache9rocky` (docker-compose.RL9.yml), shared by the `*build` and `*buildreloc` services.
  - **Win:** within one rpmbuild the 4 SAPI passes (apache/cli/cgi/fpm) compile the same sources → ~3 of 4 core compiles become cache hits; across runs (volume-persisted) iterative spec-tuning rebuilds are near-instant for unchanged TUs. CI runners get the within-build win only (fresh volume each run).
  - **No spec change needed** — PATH wiring routes `gcc`/`g++` through the ccache wrappers transparently; `%configure` detects them as the compiler.

## Candidate (not yet applied — operator decision)
- **opcache JIT** — not configured (off). Capstone is built so JIT is available; `opcache.jit=tracing` + `opcache.jit_buffer_size` helps CLI/compute, ~neutral for typical web. Keep off by default; document as a per-deployment tunable.
- **`pcre.jit=0`** (SOURCES/php.ini) — disabled long ago for an SELinux AVC; likely fixed now, re-enabling is a small free regex win (verify SELinux first).

## Verified already-optimal (no action)

- `make test` is gated behind `%if %{with_test}` — normal builds skip it.
- Shared extensions are built **once** (in the CGI pass); other SAPIs use `$without_shared`.
- debuginfo disabled (`debug_package %{nil}`), `%{?_smp_mflags}` parallelism, hardened build on.
- **LTO intentionally disabled** (`%define _lto_cflags %{nil}`) — the upstream/Remi default (PHP+LTO has been problematic); leave it.

See [[review-8.5-assets]] for the feature/extension review.
