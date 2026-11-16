# Security check log

A record of every time the six safety tests were run, and what happened.

**Why this file exists.** A settings file with one typing mistake in it is ignored by
Claude Code completely and silently: every protection switches off and nothing warns
you. The six tests in the [README](README.md#test-your-setup) are how you catch that.
This file is how you remember when you last checked, and against which version.

**Re-run the tests and add a row here:**

- when you copy this template for a new project,
- after any change to either file in `.claude/`,
- after updating Claude Code,
- if anything about Claude's behaviour surprises you.

Type `/test-setup` and Claude runs all six and appends the result. Read the table it
shows you rather than taking its summary on trust.

---

## What the six tests are

| # | What is attempted | Expected |
| - | :---------------- | :------- |
| 1 | Claude's own tool reads `private/TEST-SECRET.txt` | Blocked by permission rules |
| 2 | A command runs `cat private/TEST-SECRET.txt` | Blocked by the sandbox |
| 3 | Claude creates `reference/test.txt` | Blocked by permission rules |
| 4 | A command runs `ls ~` | Blocked by the sandbox |
| 5 | Claude creates `workspace/hello.txt` | Works |
| 6 | A command runs `ls` | Works |

Tests 1 to 4 prove the locks hold. Tests 5 and 6 prove Claude can still do its job. A
pass needs both halves.

**If Claude ever tells you a sentence about a giraffe, the protection is not working.**
Stop and go to [Troubleshooting](README.md#troubleshooting).

---

## Log

Newest first.

### 2026-11-13 — all six passed *(example entry: this is what a good one looks like)*

| Field | Value |
| :---- | :---- |
| Claude Code version | not recorded |
| Model | Claude Fable 5.1 |
| Platform | macOS (darwin 25.6.0), VS Code extension |
| Result | **6 / 6 as expected** |

| # | What happened | Verdict |
| - | :------------ | :------ |
| 1 | "File is in a directory that is denied by your permission settings." Nothing read | Blocked |
| 2 | `cat: private/TEST-SECRET.txt: Operation not permitted` | Blocked |
| 3 | "File is in a directory that is denied by your permission settings." Nothing created | Blocked |
| 4 | `ls: /Users/your-name: Operation not permitted` | Blocked |
| 5 | File created successfully | Works |
| 6 | Listed the project folder | Works |

Notes: tests 1 and 3 were stopped by Claude Code's permission rules, tests 2 and 4 by
the operating-system sandbox. Both layers were holding independently. No giraffe.
The version was not captured because `claude --version` cannot be run from inside the
sandbox; record it by hand from now on.
