# Domain docs

Where this repository's domain documentation lives, and how to use it before
changing anything.

## Read these first

- **`CONTEXT.md`** at the repository root — the vocabulary.
- **`docs/adr/`** — the decision records that touch the area you are about to
  work in.

If either is missing, carry on without it. Do not stop to flag its absence or
propose creating one upfront; they are written when there is something real to
put in them.

## Layout

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-a-decision.md
│   └── 0002-another-decision.md
└── mvp_community/
```

## Use the vocabulary

When your output names a domain concept — an issue title, a proposal, a
hypothesis, a test name — use the term as `CONTEXT.md` defines it. Do not drift
to a synonym the file explicitly rules out.

A concept you need that is not in the glossary yet is a signal. Either you are
inventing language the project does not use, which is worth reconsidering, or
there is a real gap, which is worth naming.

## Flag conflicts with a decision record

If what you are about to do contradicts a landed record, say so rather than
quietly overriding it:

> Contradicts ADR 0007, which rules this out — but worth reopening because…
