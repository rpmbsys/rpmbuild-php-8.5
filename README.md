## PHP 8.5 RPM Build Process

This repository contains Docker-based infrastructure to build the **PHP 8.5**
RPM package set (currently **8.5.7**) and the Docker images that wrap it, for
**Rocky Linux 9 and 10**.

You can run the build locally or use the automated GitHub Actions workflow.

---

## Requirements (one-time per build host)

### 1. Docker

Install **Docker CE 20.10.0+** following the official guide:  
https://docs.docker.com/engine/install/

### 2. Add current user to Docker group

```bash
sudo usermod -aG docker $(whoami)
```

Then **logout and login again** to apply changes.

### 3. Enable and start Docker daemon

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

## Repository Setup

Clone the repository with all submodules (the `rpmbuild/` submodule carries the
build harness and RPM uploader and must be checked out):

```bash
git clone --recursive https://github.com/rpmbsys/rpmbuild-php-8.5.git
cd rpmbuild-php-8.5
```

If you already cloned without `--recursive`:

```bash
git submodule update --init
```

---

## Build Process

Rocky 9 and Rocky 10 builds are driven by **separate compose files**:

| Target   | Build-env (base) image          | RPM build                |
|----------|---------------------------------|--------------------------|
| Rocky 10 | `docker-compose.base.yml`       | `docker-compose.yml`     |
| Rocky 9  | `docker-compose.base.yml`       | `docker-compose.RL9.yml` |

### 1. Build the base (build-env) images

```bash
docker compose -f docker-compose.base.yml build --no-cache --pull
```

This builds `aursu/php85build:<rocky-tag>-base` for both Rocky 9 and Rocky 10
(`rocky9base` / `rocky10base`).

### 2. Build the rpmbuild runner image

```bash
# Rocky 10
docker compose build
# Rocky 9
docker compose -f docker-compose.RL9.yml build
```

### 3. Run the build

Each compose file exposes a default build service and a `*reloc` variant. The
default builds the system PHP; the `*reloc` service runs `rpmbuild --with
relocation` to produce the suffixed, parallel-installable `php85-*` package set.

```bash
# Rocky 10 — system PHP
docker compose up --exit-code-from rocky10build rocky10build
# Rocky 10 — relocated (php85-suffixed, parallel-installable)
docker compose up --exit-code-from rocky10buildreloc rocky10buildreloc

# Rocky 9 — system PHP
docker compose -f docker-compose.RL9.yml up --exit-code-from rocky9build rocky9build
# Rocky 9 — relocated
docker compose -f docker-compose.RL9.yml up --exit-code-from rocky9buildreloc rocky9buildreloc
```

### 4. Wait for completion

```bash
docker compose ps
```

Wait until the build container exits with status `Exit 0`.

---

## Accessing RPM Packages

Resulting `.rpm` files land in named Docker volumes:

- For **Rocky 9**: `rpm9rocky`
- For **Rocky 10**: `rpm10rocky`

(mounted at `/home/centos/rpmbuild/RPMS`). A separate `ccache*rocky` volume
persists the compiler cache between builds.

To list / extract them:

```bash
docker run --rm -v rpm9rocky:/data alpine ls /data
docker run --rm -v rpm10rocky:/data alpine ls /data
```

---

## Clean Up

To stop and remove build containers:

```bash
docker compose down
docker compose -f docker-compose.RL9.yml down
```

To also remove images:

```bash
docker image prune
# or more selectively:
docker rmi <image_name>
```

---

## GitHub Actions (CI/CD)

This repository supports automated builds via GitHub Actions.

On push, it:
- Builds the base/build-env images and RPMs for Rocky 9 & 10.
- Uploads the RPMs to Artifactory (JFrog repo `php85custom`).
- Pushes the build-env image to Docker Hub (`aursu/php85build`) and the
  runtime/dev images to GHCR (`ghcr.io/rpmbsys/php85build`).
- Supports `skip-rpm-*` branches to skip the RPM build job.

Workflow file: `.github/workflows/build.yaml` (`cleanup.yml` prunes old GHCR images).

---

## Notes

- Ensure you have enough free space (~5–10 GB recommended).
- Version/base pins live in `.env` (`RL9`/`RL9TAG`/`RL10`/`RL10TAG`); the PHP
  version is set by the tarball in `SOURCES/` and `Version:` in `SPECS/php.spec`.
- These RPMs feed the sibling PHP-extension build repos
  (`rpmbuild-php-redis6`, `-imagick`, `-apcu`, …), which build against the
  `php85custom` package set.
