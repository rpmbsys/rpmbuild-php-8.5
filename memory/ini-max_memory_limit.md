---
name: php.ini max_memory_limit is NEW in 8.5 (kept, not dropped)
description: max_memory_limit in SOURCES/php.ini is a legitimate NEW PHP 8.5.0 INI directive (a startup-only hard ceiling on memory_limit), NOT a discontinued/bogus setting. Verified against 8.4.19 vs 8.5.7 source 2026-06-18. Keep it.
type: reference
---
## Verdict: KEEP `max_memory_limit = -1` in `SOURCES/php.ini`

During the 8.5 asset review this line was initially (and wrongly) flagged as a bogus/removed directive. Checking the **real PHP source** reversed that: it is a **brand-new directive introduced in PHP 8.5.0**, not a removed one.

## Evidence (source-verified 2026-06-18)

- **Absent in 8.4.19**, **present in 8.5.7**: `grep max_memory_limit` → 0 hits in `php-8.4.19/main/main.c` and its `php.ini-production`; multiple hits in 8.5.7.
- Registered as a core INI entry: `php-8.5.7/main/main.c:865`
  `PHP_INI_ENTRY("max_memory_limit", "-1", PHP_INI_SYSTEM, OnChangeMaxMemoryLimit)` — **`PHP_INI_SYSTEM`** = startup-only (set in php.ini / httpd conf / `-d`, not per-request `ini_set`).
- Global: `php-8.5.7/main/php_globals.h` (`zend_long max_memory_limit;`).
- Upstream ships it in `php-8.5.7/php.ini-production` (line 431, `max_memory_limit = -1`) — so this repo's php.ini matches upstream defaults.

## What it does

An administrator-set **hard ceiling** on what `memory_limit` may be raised to (at startup or at runtime via `ini_set`). If something tries to set `memory_limit` above `max_memory_limit`, PHP emits a warning and clamps `memory_limit` to `max_memory_limit`. `-1` (default) = **no enforcement** — behaves exactly as pre-8.5. Useful on shared hosting / multi-tenant FPM pools to stop a pool/script from exceeding an operator-imposed cap.

## References

- PHP source `UPGRADING` (8.5): *"Added startup-only `max_memory_limit` INI setting to control the maximum `memory_limit` that may be configured at startup or runtime. Exceeding this value emits a warning, unless set to -1, and sets `memory_limit` to the current `max_memory_limit` instead."* — ML discussion: https://externals.io/message/127108
- Official changelog: https://www.php.net/ChangeLog-8.php (8.5.0 entries)
- Core INI directives reference: https://www.php.net/manual/en/ini.core.php

## Note

There was **no "removal" changelog to cite** — the premise (discontinued feature) was inverted; this is an *addition*. Leaving `max_memory_limit = -1` is correct and upstream-aligned. The only PHP memory directive ever named is `memory_limit`; `max_memory_limit` is its new companion, not a typo.
