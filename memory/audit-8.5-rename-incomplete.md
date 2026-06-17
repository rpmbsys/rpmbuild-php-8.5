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

## How to apply

- Before ANY build attempt: bump `Version:`→8.5.7, repoint the 8 Sev-1 refs, decide on `php-8.5.0-embed.patch` + `php.tmpfiles`, add a changelog entry.
- The cleanest reference for what a *fully* renamed sibling looks like is `../rpmbuild-php-8.3` (`php83.spec`) and `../rpmbuild-php-8.4` (the copy source). Diff `php.spec` against `../rpmbuild-php-8.4/SPECS/php84.spec` to see exactly what the copy changed (answer: only the filename).
- User chose **audit-report-only** for the 2026-06-17 pass — fixes were NOT applied. Re-confirm scope before editing the spec.
