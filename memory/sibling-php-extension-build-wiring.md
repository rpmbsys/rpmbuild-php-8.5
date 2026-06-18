---
name: sibling PHP extension build wiring
description: How the sibling rpmbuild-php-* extension/PEAR repos wire per-PHP-version RPM builds (docker-compose.phpNN.yml, build/phpNN dirs, GitHub workflow matrix), and the 2026-06-18 drop-8.1/add-8.5 migration across all of them.
type: project
---

This repo (`rpmbuild-php-8.5`) builds the **base PHP 8.5 RPMs**. Sitting next to it in the same parent folder are the per-extension / PEAR repos that build *against* a PHP version: `../rpmbuild-php-pear` and the PECL set `../rpmbuild-php-{amqp,apcu,geoip,igbinary,imagick,memcached,msgpack,pcov,redis6,xdebug}`. Each is its own git repo with an `rpmbuild/` submodule (the build harness — do **not** edit it for version changes). Paths below are written relative to this repo's parent, i.e. all repos are siblings.

## Per-PHP-version wiring (in each extension/PEAR repo root)

- `docker-compose.phpNN.yml` (NN = 82/83/84/85): defines `rocky9build` + `rocky10build` services. PHP version is encoded only in a build arg — extensions use `image: php[-<dep>]-8.N` (e.g. `php-8.4`, `php-apcu-8.4`, `php-msgpack-8.4`); PEAR uses `buildrepo: php84build`.
- `.github/workflows/build.yaml`: a `test` job with a matrix of `{compose-file, repo: phpNNcustom, build, uploader, repo_path}` rows (one per version × rocky9/rocky10). Repos that publish intermediate base images also have a `docker` job whose matrix lists `build/phpNN/docker-compose.yml`.

## Base-image chain (pearbuild → peclbuild tags)

`php-pear` (`../rpmbuild-php-pear`, `build/phpNN/`) → apcu → igbinary → msgpack → … The repos that carry their own `build/phpNN/` subdirs (Dockerfile + docker-compose.yml publishing `aursu/pearbuild:` / `aursu/peclbuild:` base tags) are: **pear, apcu, igbinary, msgpack**. The other extensions just consume those bases through their top-level `image:` arg.

**Inter-extension dependency edges** (each downstream build's `image:` FROMs an upstream extension's published peclbuild tag):
- **msgpack depends on igbinary** (FROMs the igbinary peclbuild base; msgpack also BuildRequires igbinary).
- **redis6 and memcached depend on msgpack** (FROM the msgpack peclbuild base).
- apcu and igbinary build on the pear/`php` base.
- Build/pull order: **pear → apcu/igbinary → msgpack → {memcached, redis6}**.

**Cascade failure (observed 2026-06-18):** these bases are *pulled*, not rebuilt, at each step. If an upstream extension's image isn't published, every downstream build fails at `docker pull` of the missing base — NOT because of its own code. When igbinary's 8.5 build failed (source incompat — see [[pecl-spec-php-devel-cap]]), `peclbuild:…-php-igbinary-8.5` was never pushed, so msgpack, then redis6 + memcached, all "failed" on 8.5 solely for lack of a base image. **Before treating a downstream extension's failure as its own bug, check whether its base image actually exists.** Fix is to build+publish the chain in order, then re-run the downstream repos.

## Adding / dropping a PHP version (mechanical)

- New `docker-compose.phpNN.yml` = copy the highest existing version's file and bump, e.g. `s/php85/php86/g; s/8\.5/8.6/g` (covers both `phpNNbuild` and `-8.N` tag forms).
- For pear/apcu/igbinary/msgpack also create `build/phpNN/` by applying the same two seds to `build/<highest>/{Dockerfile,docker-compose.yml}`.
- Workflow: a global text replace of the dropped version onto the new one in `build.yaml` rewrites the dropped version's matrix rows (and `build/<old>/...` docker-job entries). Matrix row order doesn't affect correctness.
- Delete the dropped `docker-compose.phpNN.yml` and `build/phpNN/`.

## Current state

**Supported PHP set: 8.2 / 8.3 / 8.4 / 8.5.** On **2026-06-18** PHP 8.1 was dropped and 8.5 added across all 11 sibling repos (`pear`, `amqp`, `apcu`, `geoip`, `igbinary`, `imagick`, `memcached`, `msgpack`, `pcov`, `redis6`, `xdebug`) using the procedure above. `../rpmbuild-php-redis5` exists with the same structure but is legacy and was deliberately left untouched (redis6 supersedes it). `../rpmbuild-php-geoip/SPECS/docker-compose.php84.yml` is a stray duplicate not referenced by any workflow. As of 2026-06-18 those edits were applied to the working trees but not yet committed in the individual repos.

Version pins live in each repo's `.env` (`RL9`/`RL9TAG`/`RL10`/`RL10TAG`), duplicated as literals in each `build.yaml` env block. Current: RL9=9.7.20251123, RL10=10.1.20251126.
