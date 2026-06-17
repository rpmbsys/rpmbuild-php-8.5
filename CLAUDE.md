# rpmbuild-php-8.5 — PHP 8.5 RPM build project

Builds the **PHP 8.5** RPM package set for Rocky Linux 9 & 10, plus the Docker images that wrap them. One member of the `rpmbuild-php-*` family (8.1 → 8.5). This repo was bootstrapped by copying `rpmbuild-php-8.4` and search/replacing 8.4→8.5 — **the rename is incomplete; see [`memory/audit-8.5-rename-incomplete.md`](memory/audit-8.5-rename-incomplete.md) before building.**

## Purpose

Produce `php85*` RPMs (cli, common, fpm, cgi, devel, opcache, and the per-extension subpackages) and publish:

1. **RPMs** → JFrog/Artifactory repo `php85custom` (`https://rpmb.jfrog.io`), via the `rpmbuild/` submodule's uploader.
2. **Build-env image** `aursu/php85build:<rocky-tag>-build` → Docker Hub.
3. **Runtime / dev images** `ghcr.io/rpmbsys/php85build:<rocky-tag>-runtime|dev` → GHCR.

These RPMs feed downstream PHP-extension build repos (`rpmbuild-php-redis6`, `-imagick`, `-apcu`, …) and any image layer that installs PHP from the `php85custom` repo.

## Stack

| Aspect | Choice |
|---|---|
| Build tool | `rpmbuild` inside Docker, orchestrated by docker-compose |
| Spec | `SPECS/php.spec` (single spec; **note**: siblings use `phpNN.spec`, this repo intentionally keeps `php.spec`) |
| Target version | **8.5.7** (tarball lives in `SOURCES/`) |
| CI | GitHub Actions `.github/workflows/build.yaml`, runs on every push (`ubuntu-latest`) |
| RPM publish target | JFrog Artifactory repo `php85custom` |
| Image publish targets | `aursu/php85build` (Docker Hub), `ghcr.io/rpmbsys/php85build` (GHCR) |
| Upstream base image | `aursu/rpmbuild:<rocky-tag>-build` → from [`docker-rpmbuild`](https://github.com/aursu/docker-rpmbuild) (the `rpmbuild/` submodule) |
| Branch | `main`; `skip-rpm-*` branches skip the RPM `test` job (see `if: ! startsWith(...,'skip-rpm-')`) |
| Remote | `origin` → `git@github.com:rpmbsys/rpmbuild-php-8.5.git` (public) |

> **Scope rule:** this is a **vendor-neutral, public** repo. Keep it project- and company-agnostic — no organization-internal names, hostnames, or registries in any tracked file (including this one and `memory/`).

## Layout

```
.
├── SPECS/php.spec              The PHP spec (based on Remi Collet's Fedora/RHEL spec)
├── SOURCES/                    Tarball + .asc + keyring + patches + config templates
│                               (default php-* names; php85-* / php-7.0.8-relocation = relocation build)
├── Dockerfile                  rpmbuild runner: FROM aursu/php85build:${os}-base, runs `rpmbuild php.spec`
├── Dockerfile.base             Build-env image (RL10): FROM aursu/rpmbuild:${os}-build + PHP build deps
├── Dockerfile.RL9.base         Build-env image (RL9)
├── docker-compose.yml          rocky10build / rocky10buildreloc (the RPM build)
├── docker-compose.RL9.yml      Rocky 9 build
├── docker-compose.base.yml     Builds aursu/php85build:<tag>-base from Dockerfile*.base
├── build/                      Publishes the -build base image to Docker Hub
├── run/                        Builds & publishes runtime + dev images to GHCR (run/dev/, run/system/)
├── rpmbuild/                   git submodule → aursu/docker-rpmbuild (uploader image lives here)
├── .env                        Pins RL9TAG / RL10TAG (upstream Rocky base versions)
└── .github/workflows/          build.yaml (RPM+image pipeline), cleanup.yml (GHCR prune)
```

## Build pipeline (CI = `build.yaml`, on push)

1. **test** (matrix RL10 + RL9): build base (`docker-compose.base.yml`) → build runner (`docker-compose.yml`) → `up --exit-code-from` to run `rpmbuild` → upload RPMs to JFrog via `rpmbuild/` uploader. **This is the job that actually produces the RPMs.**
2. **build**: push `aursu/php85build:*-build` (Docker Hub).
3. **runtime / dev**: build + push GHCR runtime/dev images, tagged from `Version:` + `%global rpmrel` parsed out of the spec.

## Local build (mirror of CI step 1)

```bash
# from repo root
git submodule update --init                 # rpmbuild/ is currently NOT checked out
docker compose -f docker-compose.base.yml build rocky10base   # build env
docker compose build rocky10build                              # rpmbuild runner
docker compose up --exit-code-from rocky10build rocky10build   # produce RPMs (volume rpm10rocky)
# relocated (php85-suffixed, parallel-installable) variant:
docker compose up --exit-code-from rocky10buildreloc rocky10buildreloc
```

RPMs land in the named Docker volume `rpm10rocky` (`:/home/centos/rpmbuild/RPMS`).

## Spec conventions worth knowing

- **Two build modes.** Default → `main_name php` (the system PHP). `--with relocation` → a suffixed, parallel-installable package (`program_suffix`, e.g. `php85`) with its own sysconfdir/datadir and the `php85-*` source variants + `php-7.0.8-relocation.patch` / `php84-php-7.2.0-includedir.patch`.
- **Feature toggles** are `%global with_<feature> 0%{!?_without_<feature>:1}` — disable with `rpmbuild --without <feature>`; `cgi`/`fpm`/`test` are opt-in via `--with`.
- **GPG verify runs in `%prep`** against `Source0`/`Source21` using `Source20` (`php-keyring.gpg`) — the tarball, its `.asc`, and `Version:` must all agree or `%prep` fails.
- **Patches are applied explicitly** (`%patch -PN`), not via `%autosetup`. A patch file present in `SOURCES/` but not declared `PatchN:` + applied does nothing.

## Conventions

- **Manual + CI builds.** Push triggers CI; locally run the compose steps above.
- **Version bumps coordinate with the family.** `.env`/`build/.env`/`run/.env` pin the upstream Rocky tag; bump them together (sed across `*/Dockerfile* */.github/*/*.yaml */.env */build/.env */build/*/.env`).
- **CI secrets** (JFrog `BINTRAY_*`, `DOCKER_*`) come from GitHub Actions secrets, never the repo.
- **`rpmbuild/` is a submodule** → `aursu/docker-rpmbuild`; it must be checked out for the uploader step and local builds.

## Sibling repos

- `rpmbuild-php-8.4` — the repo this one was copied from.
- `rpmbuild-php-8.3` — cleanest reference for the completed `phpNN` rename pattern (its spec is `php83.spec`).
- `rpmbuild-php-{redis6,imagick,apcu,memcached,igbinary,msgpack,amqp,pcov,xdebug,geoip,pear}` — PHP extensions built against these RPMs; same `rpmbuild/` submodule pattern.

## Reading order for a new responder

1. This file.
2. [`memory/MEMORY.md`](memory/MEMORY.md) → [`memory/audit-8.5-rename-incomplete.md`](memory/audit-8.5-rename-incomplete.md) — current state & known gaps.
3. [`SPECS/php.spec`](SPECS/php.spec) — the artifact under audit.
4. `.github/workflows/build.yaml` — the canonical build sequence.
