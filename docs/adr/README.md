# Decision records

One file per architecturally significant decision, named
`NNNN-kebab-slug.md` — four digits, zero-padded, sequential, never reused.

## What earns a record

A decision goes here when it is all three of:

1. **Durable** — it constrains future work. It has to be abided by, or
   deliberately overturned.
2. **Architectural** — it shapes structure, a public interface, a dependency, a
   data model, or a convention others follow. Not a detail sealed inside one
   function.
3. **Non-obvious** — a reasonable engineer would later ask "why this way?".

Fail any one and it is a comment next to the code instead. A directory of
records for choices nobody would question is a directory nobody reads.

Standing *rules* are not decisions: they belong in `CONSTITUTION.md`. The
difference is that a rule applies to every change, and a decision was made once.

## Superseding

Never delete or rewrite a landed record. When a later decision overturns one,
set the old record's status to `superseded by NNNN` and add a line pointing at
the new one, which in turn names what it replaces. The history of a decision is
the useful part.

Numbers are claimed when the file lands on the main branch, not when the branch
is created. Two branches open at once will otherwise both take the next number
and collide silently.

## Template

```markdown
# ADR NNNN — <short decision title>

**Status:** accepted <!-- accepted | superseded by NNNN | deprecated -->

## Decision

What was decided, as a standing rule in the present tense. Name the concrete
thing — the class, the field, the boundary, the dependency — not the
deliberation. A reader should be able to act on this without reading the Why.

## Why

The forces that made this the right call: the constraint, the alternatives
weighed, and what tipped it. Enough that a future engineer does not have to
argue it from scratch.

## Revisit if

The condition under which this stops holding — the assumption that, if it
breaks, reopens the question. Omit only if genuinely none applies.
```
