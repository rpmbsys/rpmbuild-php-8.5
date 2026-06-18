# rpmbuild-php-8.5 — memory index

One line per memory. Read the linked file for detail. See [`../CLAUDE.md`](../CLAUDE.md) for repo overview.

- [Public RPM changelog author identity](changelog-author-identity.md) — new %changelog entries use Alexander Ursu <alexander.ursu@gmail.com>, never the private work email configured in git (ships in the RPM; repos are public/vendor-neutral).
- [Upstream PHP reference links](upstream-php-references.md) — curated index of authoritative upstream sources (externals.io threads, official changelog/INI docs, in-tree UPGRADING/NEWS) backing build decisions. Seeded with the max_memory_limit ML thread (externals.io/message/127108).
- [php.ini max_memory_limit is NEW in 8.5](ini-max_memory_limit.md) — keep it; it's a legitimate new 8.5.0 startup-only cap on memory_limit (verified vs source), not a removed/bogus directive.
- [Build optimizations](build-optimizations.md) — dropped mysql*-devel from base Dockerfiles (mysqlnd needs no libmysqlclient); ccache/JIT/pcre.jit listed as candidates; LTO intentionally off.
- [8.5 assets relevance review](review-8.5-assets.md) — patches/spec-settings/config/extensions reviewed for 8.5 currency + top-20 framework coverage (2026-06-18). Coverage excellent; action items: drop dba/db4, verify ldap_r + --with-mhash, re-eval system-php-parser patch, remove bogus max_memory_limit ini line.
- [8.5 rename audit (RESOLVED 2026-06-17)](audit-8.5-rename-incomplete.md) — repo was copied from php-8.4; the spec rename was incomplete (still 8.4 names/refs). All Sev-1/2/3 findings fixed same day (upver 8.5.7, 8.5.0/php85 refs, verified api/zend/pdo vers, tmpfiles co-install, dead Patch6/major_version removed). Only cosmetic 8.4.0 patch filenames remain; not yet built.
