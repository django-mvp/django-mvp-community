# Triage labels

An issue carries exactly one of these at a time. They are states, not tags: an
issue that is both `needs-info` and `ready-for-agent` is one whose state nobody
decided.

| Label | Meaning |
| --- | --- |
| `needs-triage` | Not yet evaluated. Every new issue starts here |
| `needs-info` | Waiting on the reporter. Nothing can be decided until they answer |
| `ready-for-agent` | Fully specified. Someone could pick it up without asking a question |
| `ready-for-human` | Needs a person — a judgment call, a credential, or a decision about direction |
| `wontfix` | Will not be actioned, with a comment saying why |

`ready-for-agent` is the load-bearing one. It is a claim that the issue names
what to change, what the result should be, and how to tell it worked. An issue
labelled that way while still ambiguous produces work nobody asked for.

Edit the label strings above if this repository uses different ones, and keep
the meanings.
