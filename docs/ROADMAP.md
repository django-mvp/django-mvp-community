# Roadmap — django-mvp-community

<!--
  The order the work happens in, and what each release is gated on.

  This file is written against GOALS.md and is the only place a release plan
  lives. It holds briefs, not specifications: each item says what a person gets
  and why it comes when it does, in enough detail that someone could pick it up
  and write the specification without asking what was meant.

  Rules:
  - Items are R1, R2, R3 …, assigned once and never reused. They are cited from
    issues and pull requests.
  - Each item names the goals it advances, by ID.
  - Group items under the release they are gated on, not under a date. This
    package has no delivery dates and inventing them would only make the file
    wrong.
  - Status is derived from the item's issues, not asserted here. An item is
    delivered when its issues are closed; saying so twice creates two answers
    that drift.
  - An item that is no longer wanted is rewritten or deleted, not struck
    through. Git already records what it said.
  - Write in plain language, for a reader who has not seen the code. An item
    titled after a module name tells them nothing.

  The versioning table below is the standard and applies as written. Replace
  everything under it.
-->

This document is designed against [GOALS.md](../GOALS.md). See also
[CONTEXT.md](../CONTEXT.md) for vocabulary and
[CONSTITUTION.md](../CONSTITUTION.md) for the standards every change is held to.

## Versioning

Releases are gated on goal importance, not on a count of features.

| Version | Gate |
|---|---|
| `0.0.x` | Building toward the Essential goals. Pre-viable, expect churn, nothing published |
| `0.1.0` | All Essential goals delivered. The minimum usable release, and the first publish |
| `0.1.x` → `0.x` | Advancing the Expected goals, at whatever granularity the work takes |
| `1.0.0` | All Expected goals delivered. The complete, dependable release |
| `1.x` | Stable line: fixes and additive features only |
| `2.0` | The next major, where breaking changes go |

A goal is not one minor release: some take several, and one release can move
two. Once `1.0` ships, a breaking change never goes out as `1.x` — it waits for
the next major.

## Essential goals: v0.1.0

Everything needed to reach a minimum usable release.

### R1 — <what a person gets, in plain language>

*advances G1*

<!--
  Two or three paragraphs. What exists afterwards that did not before, what it
  is for, and what it deliberately does not cover. Name the alternative that
  was considered and set aside, if there was one — that is the part a reader
  cannot reconstruct.
-->

## Expected goals: v1.0.0

<!-- Items gated on the complete release. Same shape. -->
