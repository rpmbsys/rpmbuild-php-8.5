---
name: 8.5 assets relevance review
description: Full review of rpmbuild-php-8.5 assets (patches, spec configure flags/settings, config files, extension set) for currency on PHP 8.5 and coverage of the top-20 PHP web frameworks. Dated 2026-06-18.
type: project
---
Review of whether the long-lived (since 5.6) build assets are still relevant for **PHP 8.5**, and whether the built extension set covers the popular web frameworks/SDKs. Dated 2026-06-18.

## Patches — keep / review / drop

| Patch (spec #) | Purpose | Verdict |
|---|---|---|
| `php-8.4.0-httpd.patch` (P1, .mpmcheck) | relax Apache MPM prefork build check | **KEEP** (rename to 8.5.0 cosmetic) |
| `php-8.5.0-includedir.patch` (P5) / `php85-php-8.5.0-includedir.patch` (P405) | includedir → `/usr/include/php[85]` | **KEEP** |
| `php-8.4.0-libdb.patch` (P8) | make ext/dba build against libdb | **DROP candidate** — only needed if dba/db4 kept; see dba below |
| ~~`php-8.5.0-parser.patch` (P41)~~ | gen_stub.php uses *system* nikic/php-parser | **REMOVED 2026-06-18** — conditional Fedora-ism (`/usr/share/php/PhpParser5`); no system parser here, gen_stub doesn't run from a release tarball. Dropped Patch41 decl + `%patch -P41` + file + the `Recommends: php-nikic-php-parser5` weak dep |
| `php-8.5.0-systzdata-v24.patch` (P42) | ext/date uses **system tzdata** not bundled | **KEEP** (important; revision v24 applies clean to 8.5) |
| `php-8.4.0-phpize.patch` (P43, .headers) | phpize header/version handling | **KEEP** |
| `php-8.5.0-ldap_r.patch` (P45) | use `-lldap_r` **if present** | **KEEP** (verified 2026-06-18 vs source) — patch is conditional: the `-lldap_r` branch only fires `if test -f $LDAP_LIBDIR/libldap_r.so`; on Rocky 9/10 (OpenLDAP 2.6, no separate `_r` lib) it falls through to the normal `-llber -lldap` branch. Harmless. |
| `php-8.4.0-phpinfo.patch` (P47) | hide "Configure Command" + full gcc ver from phpinfo | **KEEP** (privacy/cosmetic) |
| `php-8.5.0-openssl-ec-param.patch` (P48) | warn on missing EC curve_name (RHEL crypto policy) | **KEEP** (correctly updated to patch 8.5's split `openssl_backend_v1/v3.c`) |
| `php-5.6.31-no-scan-dir-override.patch` (P60) | prevent `PHP_INI_SCAN_DIR` env override | **REVIEW** — ancient; applies clean but verify semantics still hold on 8.5 `main/php_ini.c` |
| `php-7.4.0-datetests.patch` (P300) | adjust 3 failing date `.phpt` | **KEEP** (test-only; harmless, only used with `--with test`) |
| `php-8.5.7-relocation.patch` (P409) | program-suffix relocation for php85 | **KEEP** (rebased + tabs fixed 2026-06-18; **renamed** 7.0.8→8.5.7 since it was actually revised — see naming convention below) |

**Patch filename convention (operator):** the version in a patch name marks **when the patch was last revised**, not the target series. Patches that still apply unchanged keep their old names (`php-5.6.31-no-scan-dir-override`, the `php-8.4.0-*` set). Only patches actually re-touched for 8.5 get bumped — hence relocation → `8.5.7` (just rebased) while `php-8.4.0-httpd/libdb/phpize/phpinfo` stay. Patches are sourced from the Fedora Project Koji system.

## Spec settings (configure) — notes for 8.5

- **Modern & 8.5-aware:** `--with-external-uriparser` (new ext/uri in 8.5), `--with-capstone` (JIT disasm), `--with-openssl-argon2 --without-password-argon2` (8.4+ argon2 via OpenSSL), `--with-external-pcre/-libcrypt`, `--with-system-tzdata/-ciphers`, mysqlnd-only. Good.
- **No removed-extension flags** — no json/xmlrpc/wddx/interbase/recode/pspell-removed configure attempts. Clean.
- **`--with-mhash`** — verified 2026-06-18 vs source: still a valid `PHP_ARG_WITH` in `ext/hash/config.m4`, but emits "deprecated as of PHP 8.1.0" at configure and only provides the legacy `mhash()`/`mhash_keygen_s2k()` BC functions (E_DEPRECATED at runtime). No top-20 framework uses them. **DROP candidate** — harmless on 8.5, will hard-error when PHP 9 removes it.
- **`--enable-dba --with-db4=%{_prefix}` + `libdb-devel` BR + the libdb patch** — Berkeley DB. **Build risk on Rocky 10** (libdb is being retired by distros) AND essentially **no web framework uses ext/dba**. Strong DROP candidate (removes a BR, a patch, and a fragile dep). gdbm could remain if any dba wanted.
- `--without-readline` + libedit — correct for RHEL.
- BuildRequires look current (capstone>=3.0, liburiparser, oniguruma, icu, sqlite3, libxcrypt).

## Config / resource files

- `10-opcache.ini`, `20-ffi.ini` — current (include recent opcache options: file_cache_read_only, validate_permission, preload). Good.
- `php.ini` — no legacy removed directives (no magic_quotes/safe_mode/track_errors). `expose_php = On` (consider Off, policy). **CORRECTION:** `max_memory_limit = -1` was initially mis-flagged as bogus — it is a **legitimate NEW PHP 8.5.0 directive** (kept, matches upstream php.ini-production). See [[ini-max_memory_limit]].
- `php-fpm-www.conf` — modern (`listen = /run/php-fpm/www.sock`).

## Extension coverage vs top-20 PHP web frameworks/SDKs

**Built (static in -common or shared subpkgs):** Core/SPL/standard/date/hash/json/pcre/filter/random, ctype, fileinfo, iconv, tokenizer, session, libxml, **sqlite3+pdo_sqlite**, phar, mysqlnd/mysqli/pdo_mysql, curl, openssl, zlib, bz2, zip, gd(+freetype/jpeg/webp/png), intl, mbstring(+mbregex), gettext, exif, calendar, ftp, soap, pdo, opcache, dom/simplexml/xmlreader/xmlwriter/xsl, pgsql/pdo_pgsql, odbc/pdo_odbc, bcmath, ldap, sysv*/shmop/posix, **pcntl (CLI)**, sodium, ffi, tidy, sockets. PECL add-ons (redis, imagick, apcu, igbinary, msgpack, amqp, pcov, xdebug, geoip) are **separate sibling repos** (correct).

**Coverage verdict: excellent.** Every hard requirement of Laravel, Symfony, WordPress/WooCommerce, Drupal, **Magento 2** (most demanding: bcmath/intl/soap/xsl/sodium/sockets/ftp — all present), Shopware, PrestaShop, CodeIgniter/CakePHP/Yii/Laminas, Composer/PHPUnit, and the Guzzle/AWS/Stripe SDKs is satisfied.

**Gaps / candidates:**
- **gmp** — NOT built. Not a hard dep of any top-20 framework; optional add for some math/crypto libs (phpseclib/Brick\Math fall back without it). LOW priority.
- **dba/odbc/tidy/calendar/ftp/gettext** — vestigial for modern web stacks. odbc/tidy are separable shared subpkgs (harmless, optional at install). **dba is the one to actually drop** (see above).
- Confirm at build that **sqlite3/pdo_sqlite** land in `php-common` (they Provide it; static) — critical for Laravel default/testing DB and Drupal.

## Suggested action list (priority order)

1. ~~Decide dba/db4~~ — **DONE 2026-06-18**: dropped `--enable-dba --with-db4 --with-gdbm`, `php-8.4.0-libdb.patch` (P8), `libdb-devel`+`gdbm-devel` BR, `Provides: php-dba`; removed `libdb-devel`+`gdbm-devel` from `Dockerfile.base` and `Dockerfile.RL9.base`. `Obsoletes: php-dba` kept for upgrade cleanup.
2. ~~Verify `ldap_r` patch~~ — **DONE** (verified safe/conditional; KEEP).
3. ~~`--with-mhash`~~ — **DONE 2026-06-18**: dropped the flag + `Provides: php-mhash`.
4. ~~Re-evaluate system-php-parser patch~~ — **DONE** (removed 2026-06-18).
5. ~~Remove max_memory_limit ini line~~ — **CANCELLED**: it's a legit new 8.5 directive, kept ([[ini-max_memory_limit]]). (Do **not** rename the `php-8.4.0-*` patches — per convention they keep the version at which they were last revised.)
6. Optional: add **gmp** if any internal SDK needs it.
