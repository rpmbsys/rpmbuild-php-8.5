---
name: Upstream PHP reference links
description: Curated index of authoritative upstream PHP sources (RFCs, externals.io mailing-list threads, official changelogs/docs) that justify build/spec/ini decisions in this repo. Add to it as new decisions are researched.
type: reference
---
Authoritative external sources backing decisions in this repo. Prefer these over memory/assumptions when (re)assessing a flag, directive, or patch. Verified against the PHP source tree where possible.

## Mailing-list (externals.io) discussions

- **`max_memory_limit` INI setting (new in 8.5.0)** — https://externals.io/message/127108
  Startup-only (`PHP_INI_SYSTEM`) hard ceiling on what `memory_limit` may be raised to; `-1` = no enforcement. Cited verbatim in the 8.5.7 source `UPGRADING`. See [[ini-max_memory_limit]].

## Official PHP references

- **8.x changelog (per-release notes):** https://www.php.net/ChangeLog-8.php
- **Core INI directives (authoritative list + scope/default):** https://www.php.net/manual/en/ini.core.php
- **8.5 migration guide (what's new / changed):** https://www.php.net/manual/en/migration85.php

## In-tree references (ship inside the release tarball — check these first)

- `UPGRADING` — new/changed INI settings, ext changes, BC notes per release (this is where the `max_memory_limit` link above came from).
- `NEWS` — bugfix/feature log per release (e.g. GH-#### issue references).
- `php.ini-production` / `php.ini-development` — upstream's recommended defaults; compare `SOURCES/php.ini` against these.

## How to use

When questioning whether a flag/directive/patch is still current, verify against the **in-tree** files first (extract the tarball, grep `UPGRADING`/`NEWS`/`config.m4`), then cross-check the official changelog. Record any non-obvious finding here with its source URL so it isn't re-litigated.
