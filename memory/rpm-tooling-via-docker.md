---
name: RPM tooling via Docker
description: The Windows host has no rpm tooling; use a Rocky Docker container to extract SRPMs and validate specs offline. Also how to obtain upstream Fedora specs when koji/dist-git are behind the Anubis anti-bot.
type: reference
---

The Windows workstation has **no rpm tooling** (`rpm2cpio`, `cpio`, `rpmspec`, even `tar` are absent on the host shell — though git-bash *does* provide `tar`). Run RPM operations inside a Rocky container instead. `docker pull` and offline rpm ops work fine; only `dnf` inside a container hits the corporate TLS interception, so prefer operations that need no network.

**git-bash + docker quirks (important):**
- Prefix with `MSYS_NO_PATHCONV=1` when passing container paths, e.g. `MSYS_NO_PATHCONV=1 docker.exe run --rm -v "C:/abs/path:/s" img ...`. Without it git-bash rewrites `-w /s` into `S:/s` ("invalid working directory"). Safest: omit `-w` and `cd /s` inside via `bash -c`.
- `tar tzf file.tgz` silently produces nothing in git-bash; use `tar tf file.tgz` (it auto-detects gzip).

**Useful local images:**
- `ghcr.io/aursu/rockylinux:<rocky-tag>-base` — has `rpm` + `rpm2archive`, but NOT `cpio`/`tar`/`rpmspec`.
- `aursu/php85build:<rocky-tag>-build` — has `rpm-build`, so `rpmspec`/`rpmbuild` are available.

**Extract an SRPM** (no cpio/tar in the base image → use `rpm2archive`, then extract the tar on the host):
```
MSYS_NO_PATHCONV=1 docker.exe run --rm -v "<dir>:/w" ghcr.io/aursu/rockylinux:<tag>-base \
  bash -c 'cd /w/out && rpm2archive -n ../foo.src.rpm > x.tar'
# then on the host (git-bash has tar):
tar xf out/x.tar -C out && rm out/x.tar
```
This yields the `.spec` plus the Source tarball(s).

**Validate a spec offline** (catches syntax, `%if` balance, changelog dates, rendered `Source0`/`Version`):
```
MSYS_NO_PATHCONV=1 docker.exe run --rm -v "<repodir>:/s" aursu/php85build:<tag>-build \
  bash -lc 'cd /s && rpmspec -P SPECS/<name>.spec'
```
Undefined PHP macros (`%php_zend_api`, `%__phpize`, …) are non-fatal warnings — they come from an installed `php-devel`, absent here; the parse still validates structure.

**Obtaining upstream Fedora/Remi specs & SRPMs:** `koji.fedoraproject.org` and `src.fedoraproject.org` are behind **Anubis** (a JS proof-of-work anti-bot; its error page leaks e.g. `Anubis 1.25.0-1.fc44`). `WebFetch`/`curl`/`wget` cannot pass it — there is no User-Agent trick (Anubis specifically challenges `Mozilla`-like UAs and needs a JS client to solve the PoW + set a cookie). Get the content via: (a) ask the operator to paste it (their real browser solves the challenge); (b) Remi Collet's GitHub mirror `https://raw.githubusercontent.com/remicollet/remirepo/master/php/pecl/<pkg>/<pkg>.spec` (GitHub raw is not walled); (c) the operator drops `*.src.rpm` files in the workspace's `rpmbuild/` folder (a sibling of the `rpmbuild-php-*` repos). See [[pecl-spec-php-devel-cap]] for what to change once you have the new spec.
