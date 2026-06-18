---
name: Public RPM changelog author identity
description: %changelog entries in the rpmbuild-* spec files must be authored as Alexander Ursu <alexander.ursu@gmail.com> — NOT the private work email configured in git — because the changelog ships inside the RPM and these are public, vendor-neutral repos.
type: feedback
---
Use **`Alexander Ursu <alexander.ursu@gmail.com>`** as the `%changelog` author for new entries in this (and sibling `rpmbuild-*`) spec files.

**Why:** the `%changelog` author line is embedded in the built RPM and is visible to every consumer via `rpm -q --changelog`. These repos are public and vendor-neutral, so the **private work email configured in git** (a corporate address) must **not** appear there — it would leak a company reference. Use the public gmail identity instead. (Confirmed by the operator 2026-06-18 when adding the 8.5.7-3 entry.)

**How to apply:** when bumping `%global rpmrel` for a local packaging change, add the dated entry with this identity and the correct weekday. Upstream entries (Remi Collet) are left as-is; only new *local* entries use this identity. See [[review-8.5-assets]] for the kind of changes that warrant a release bump.

**Which `%changelog` entries to include (operator convention):** when updating a spec to a new upstream version, copy the **upstream** changelog entries that matter (the new version entries since our last one — typically just the one or two, not the whole history) verbatim with their original author/date. Add an entry under the gmail identity **only when applying genuinely unique local logic** (a downstream-only patch, a deviation from upstream behaviour). A change that merely matches what upstream already does (e.g. raising the `php-devel` cap to `< 8.6` when rawhide already has `< 8.6` — see [[pecl-spec-php-devel-cap]]) is NOT unique logic → no own entry; just take upstream's version entry.

**Same identity applies to git commits in these public repos.** The machine's global git identity is the private work email (a corporate address) — that must NOT land in the public `rpmbsys/*` repos (author *or* committer). Before committing here, set the repo-local identity: `git config user.name "Alexander Ursu"; git config user.email "alexander.ursu@gmail.com"` (this sets the committer; also pass `--author="Alexander Ursu <alexander.ursu@gmail.com>"` for the author). On 2026-06-18 the 8.1→8.5 migration was first committed with the work email across all sibling repos and this one, then had to be amended + force-pushed — set the repo-local config up front to avoid the redo.
