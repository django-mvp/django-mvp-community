# Tasks — 003 Queue, log and send a project's email through the mail extra

**Branch**: `003-mail-queue-and-delivery-log` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task with behaviour follows the red-green-refactor cycle of Article I. A task is done when its tests pass, the tree is green and the work is committed.

## Order

US1 → US2 → US3.

---

## Phase 1: User Story 1 — A developer sends the project's email through the mail extra (P1)

Issue: #20. Delivers FR-001 to FR-008, FR-012, FR-013.

### Group 1

- [ ] T001 [US1] The extra and the demo's configuration

**Files**: `pyproject.toml`, `uv.lock`, `demo/settings.py`, `demo/urls.py`, `tests/test_demo.py`

The extra's two packages, `mail` in the development extras, deptry `DEP002`. The demo configured per plan, *The demo*. Tests 1 to 3 of plan, *Tests*.

- [ ] T002 [US1] Stored templates in the layout, and the demo's seed

**Files**: `demo/management/commands/seed_mail.py`, `tests/test_demo.py`

Tests 4 and 5 of plan, *Tests*, then the command (no test of its own).

- [ ] T003 [US1] Documentation: installing, the settings, sending the queue, sending a stored template

**Files**: `docs/developer/mail.md`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`, `docs/ROADMAP.md`

Sections 1, 2, 3 and 6 of plan, *Documentation*. README, CHANGELOG, CONTEXT.md, and R2's brief.

---

## Phase 2: User Story 2 — Staff check what was sent and whether it arrived (P1)

Issue: #21. Delivers FR-005, FR-010, FR-011.

- [ ] T004 [US2] Documentation: checking what was sent

**Files**: `docs/developer/mail.md`

Section 4 of plan, *Documentation*. No test: the admin is django-post-office's.

---

## Phase 3: User Story 3 — Staff change an email's wording and its translations without a deploy (P2)

Issue: #22. Delivers FR-007, FR-009, FR-011.

- [ ] T005 [US3] Documentation: writing a stored template

**Files**: `docs/developer/mail.md`

Section 5 of plan, *Documentation*. No test: the admin and template validation are django-post-office's.

---

## Review fixes

- [x] T006 [US3] An edit to a translation reaches the next email, and the send example names no language for the template's own wording

**Files**: `tests/test_demo.py`, `docs/developer/mail.md`
