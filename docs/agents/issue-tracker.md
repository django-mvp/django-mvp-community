# Issue tracker: GitHub

Issues for this repository live as GitHub issues. Use the `gh` CLI for every
operation. It infers the repository from `git remote -v` when run inside a
clone.

## Conventions

- **Create:** `gh issue create --title "..." --body "..."`. Use a heredoc for a
  multi-line body.
- **Read:** `gh issue view <number> --comments`.
- **List:**
  `gh issue list --state open --json number,title,body,labels,comments`, with
  `--label` and `--state` filters.
- **Comment:** `gh issue comment <number> --body "..."`
- **Label:** `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close:** `gh issue close <number> --comment "..."`

## Closing keywords

A pull request closes an issue only where a closing keyword names it directly.
`Closes #4, #5` closes `#4` and leaves `#5` open — each number needs its own
keyword: `Closes #4, closes #5`.

The keywords fire from ordinary prose too, in a pull request body or a comment.
A sentence reading "this also fixes #12" closes `#12` on merge, whether or not
that was the intention.

## Pull requests as a request surface

**No.** External pull requests are not treated as feature requests here. Set
this to yes if that changes, and triage them through the same labels as issues
using the `gh pr` equivalents.

GitHub shares one number space across issues and pull requests, so a bare `#42`
may be either. Resolve it with `gh pr view 42` and fall back to
`gh issue view 42`.
