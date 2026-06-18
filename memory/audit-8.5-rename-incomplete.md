---
name: 8.5 rename incomplete
description: rpmbuild-php-8.5 was bootstrapped by copying php-8.4 and replacing 8.4→8.5, but the replacement only landed in Dockerfile/compose/CI/some SOURCES; SPECS/php.spec is still entirely 8.4. Build would fail at %prep. Audit 2026-06-17.
type: project
---
**Audit date:** 2026-06-17. **Target:** PHP 8.5.7, spec stays `SPECS/php.spec`, default `main_name php`.

The 8.4→8.5 rename landed in `Dockerfile`, `Dockerfile.base`, `docker-compose*.yml`, `build/`, `run/`, `.github/workflows/*` (all say `php85build` / `php85custom`), and **new** 8.5 source files were *added* to `SOURCES/`. But `SPECS/php.spec` was never touched — it still contains zero `8.5` strings. A build today fails in `%prep` (GPG verify of a non-existent tarball; then missing patches).

## Severity 1 — build-breaking (spec references files that no longer exist in SOURCES/)

`Version: 8.4.19` (spec line ~145) makes `Source0`/`Source21` resolve to `php-8.4.19.tar.xz[.asc]`, which were deleted. `%prep` runs `gpgverify` on them → immediate fail. Likewise these `%patch -PN` files are gone (replaced by `php-8.5.0-*` that the spec does NOT reference):

| Spec ref (missing) | Replacement present (orphaned) |
|---|---|
| `php-8.4.19.tar.xz` / `.asc` (Source0/21, via `Version:`) | `php-8.5.7.tar.xz` / `.asc` |
| `php-8.3.3-parser.patch` (Patch41) | `php-8.5.0-parser.patch` |
| `php-8.4.0-systzdata-v24.patch` (Patch42) | `php-8.5.0-systzdata-v24.patch` |
| `php-8.4.0-ldap_r.patch` (Patch45) | `php-8.5.0-ldap_r.patch` |
| `php-8.3.0-openssl-ec-param.patch` (Patch48) | `php-8.5.0-openssl-ec-param.patch` |
| `php-8.4.0-includedir.patch` (Patch5, non-reloc) | `php-8.5.0-includedir.patch` |
| `php84-10-opcache.ini` (Source150, reloc) | `php85-10-opcache.ini` |
| `php84-20-ffi.ini` (Source153, reloc) | `php85-20-ffi.ini` |

Fix = bump `Version:` to 8.5.7 and repoint these 8 Patch/Source lines to their 8.5 names.

## Severity 2 — orphaned new files (present, never wired into the spec)

- `php-8.5.0-embed.patch` — NEW for 8.5, no `PatchN:` decl and no `%patch` line. Decide whether 8.5 needs it; if so add a Patch number + apply in `%prep`.
- `php.tmpfiles` — NEW, not referenced. Likely a systemd `tmpfiles.d` snippet for the fpm runtime dir; needs `SourceN:` + install + `%files` if intended.

## Severity 3 — half-done relocation rename + leftover 8.4 files

- Only two relocation sources were renamed to `php85-*` (`opcache`, `ffi`). The rest are still `php84-*` AND still referenced by the spec: `php84-php.conf`, `php84-macros.php`, `php84-php-fpm{,-www}.conf`, `php84-php-fpm.{service,logrotate,wants}`, `php84-nginx-{fpm,php}.conf`, `php84-php-7.2.0-includedir.patch`. The relocation block also hardcodes `program_suffix 84` / `main_name php84`. So `--with relocation` would build **php84** packages from 8.5.7 source unless the whole reloc block + these filenames go to 85.
- Leftover 8.4 patches still referenced and still present (so non-breaking, just stale names): `php-8.4.0-httpd.patch` (P1), `php-8.4.0-libdb.patch` (P8), `php-8.4.0-phpize.patch` (P43), `php-8.4.0-phpinfo.patch` (P47). No `php-8.5.0-*` equivalents were created for these.

## Severity 4 — metadata / housekeeping

- `%changelog` top is `8.4.19-1` (Remi). No `8.5.7-1` entry; `%global rpmrel` still `1`. CI derives image tags from `Version:`+`rpmrel`, so the runtime/dev images would be tagged `8.4.19-1` until the spec is bumped.
- `rpmbuild/` submodule is **uninitialized** (`git submodule status` shows leading `-`). Needs `git submodule update --init` before the uploader step or any local build.

## Resolution (2026-06-17, same session)

The operator worked through the findings and they are now **resolved**:
- `Version` → `%global upver 8.5.7` / `Version: %{upver}`; Source0/21 resolve to the real tarball + `.asc`.
- All Sev-1 patch/source refs repointed to `php-8.5.0-*` / `php85-*`; the relocation block fully renamed (`program_suffix 85`, `main_name php85`, all `php85-*` sources incl. `php85-php-7.2.0-includedir.patch`).
- `apiver`/`zendver` = `20250925`, `pdover` = `20240423` — **verified against the 8.5.7 tarball** (`main/php.h`, `Zend/zend_modules.h`, `ext/pdo/php_pdo_driver.h`).
- `php.tmpfiles` wired (Source15 base / Source115 relocation); relocation installs/owns `php%{program_suffix}.conf` so `php85`+`php84` co-install cleanly.
- `php-8.5.0-embed.patch` removed (file + `Patch6:` decl) — this fork doesn't build the embed SAPI, and the 8.4 base never applied it. Patch decl/apply sets now match.
- `major_version` / `%bcond_with rename` removed as unused (this fork's relocation = rename only).
- New `8.5.7-1` changelog entry added; history preserved.

**Remaining (cosmetic only):** 4 patches keep `php-8.4.0-*` filenames (Patch1 httpd, Patch8 libdb, Patch43 phpize, Patch47 phpinfo) — referenced and present, content-identical, so functional; rename to `php-8.5.0-*` is optional tidiness. **Not yet built** — spec is consistent but an actual `docker compose` build run is the next validation step.

## Relocation-patch verification (2026-06-18)

Audited the `--with relocation` path specifically:
- **`%patch405` / `%patch409` used the removed old-style syntax** → fixed to `%patch -P405` / `%patch -P409`. The old `%patchN` form errors on rpm 4.18+ (Rocky 10 = rpm 4.20); every `%patch` in the spec is now uniform `-P`.
- `Patch405` renamed to `php85-php-8.5.0-includedir.patch` (spec + file agree).
- **TAB hazard (important):** `php-7.0.8-relocation.patch` had all literal TABs stripped (an easy Windows-editing artifact), so its `Makefile.frag` / `.c` hunks silently failed to apply (space≠tab context mismatch) while the no-indent hunks passed. Operator restored the tabs (83 tab-lines). **When editing any patch in `SOURCES/`, preserve literal TABs** or tab-indented hunks break. The `includedir`/`configure.ac` patches are immune (autoconf is space-indented).
- **Verified end-to-end:** the full `%prep` patch sequence applies cleanly at **fuzz=0** for BOTH the default build and the relocation build (2026-06-18).
- **Why this stayed hidden:** CI (`build.yaml`) only builds the default `rocky10build`/`rocky9build`; the `rocky10buildreloc` service is **never invoked**. The operator builds the relocation (`php85`-suffixed) variant **manually**, so relocation breakage never surfaces in CI — verify it by hand after touching any relocation source/patch.

## How to apply

- The cleanest reference for a *fully* renamed sibling is `../rpmbuild-php-8.3` (`php83.spec`) and `../rpmbuild-php-8.4` (the copy source).
- Spec is now buildable on paper; next step is the local build (`docker compose -f docker-compose.base.yml build rocky10base` → `docker compose build rocky10build` → `docker compose up --exit-code-from rocky10build rocky10build`) after `git submodule update --init`.
