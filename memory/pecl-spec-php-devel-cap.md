---
name: PECL spec php-devel version cap
description: Fedora php-pecl-* specs cap BuildRequires php-devel below the next PHP major; building against a freshly-released PHP needs that cap raised by hand. Plus the repo-local spec deltas to preserve when updating an extension.
type: project
---

Fedora/remirepo `php-pecl-*` specs carry `BuildRequires: (php-devel >= X with php-devel < Y)` where **Y tracks Fedora's *system* PHP, not the extension's real PHP support.** Building against a just-released PHP fails in `%prep`/dep-resolution with e.g.:
```
error: Failed build dependencies:
	(php-devel >= 8.0 with php-devel < 8.5) is needed by php-pecl-xdebug-...
```
even on the *latest* SRPM. Fix: confirm the extension actually supports the new PHP (e.g. xdebug.org/docs/compat — Xdebug 3.5.x supports PHP 8.1–8.5), then raise the cap (`< 8.5` → `< 8.6`). Fedora **rawhide** bumps to `< 8.6` once 8.5 lands, but stable/remirepo branches (e.g. the `fc43` SRPM) lag at `< 8.5`. So **raising the cap is a recurring manual step each PHP cycle** for every extension whose spec still caps.

**Two independent 8.5 blockers — don't conflate them.** (1) the `php-devel < Y` *cap* (above); (2) **source-level API breakage** — an extension with no version cap can still fail to compile on a new PHP because internals changed. So "uncapped" does NOT mean "builds on 8.5"; check the extension's actual 8.5 patches/release. Fix #2 by pulling the newer Fedora/remirepo release that adds the compat patches.

**Done 2026-06-18:**
- **xdebug** (`rpmbuild-php-xdebug`): cap blocker. Updated `php-pecl-xdebug.spec` 3.5.0→3.5.3, cap `< 8.5`→`< 8.6`, switched `Source0` from git-commit snapshot to release-tag archive (`archive/<ver>/xdebug-<ver>.tar.gz`, extracts to `xdebug-<ver>/`), swapped `SOURCES/` tarball. Changelog: Remi's upstream `3.5.3-1` entry verbatim — cap bump matches rawhide so no own entry (see [[changelog-author-identity]]).
- **igbinary** (`rpmbuild-php-igbinary`): source blocker, not a cap (it was already `php-devel >= 7.0`, uncapped). 3.2.16 source wouldn't compile on 8.5 (removed `ext/standard/php_smart_string.h`). Adopted Fedora `3.2.16-7` spec wholesale (no repo-local deltas) which adds PR398 (`Zend/zend_smart_string.h` header fix) + PR399 (test fixes); copied `398.patch`/`399.patch` into `SOURCES/`.

Both validated with `rpmspec -P` (see [[rpm-tooling-via-docker]]). Still at latest provided versions and presumed fine: pear/amqp/apcu/geoip/imagick/memcached/redis6. **Untested on 8.5: msgpack, pcov** (uncapped, but per the lesson above that's no guarantee — watch their CI).

**Repo-local spec deltas to PRESERVE when updating (do NOT wholesale-replace with the Fedora spec):**
- The `%global php_base php` + `%{php_base}-devel`/`-xml`/`-soap` mechanism (relocation / parallel-install). Current upstream rawhide also carries `php_base` and the `%if "%{php_base}" != "php"` rename block — but our spec may be on an *older* structure.
- xdebug keeps `Name: %{php_base}-pecl-xdebug` (no trailing "3"); upstream rawhide is `%{php_base}-pecl-xdebug3`. Keeping our name avoids changing the produced RPM name that downstream repos expect.
- Conventions vary per repo: memcached etc. are plainer (no `php_base`, `php-devel >= 7`, no upper cap). **Mirror the file you are editing, not a different sibling.**
- Upstream has moved to forge macros (`%forgemeta`/`%forgesetup`/`%forgesource`); our xdebug spec still uses the manual `%setup -qc` + out-of-source `src` dir. Both work; re-syncing to the forge model is an optional future cleanup, not required.
