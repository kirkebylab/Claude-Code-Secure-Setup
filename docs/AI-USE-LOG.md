# Recording how AI was used

This project keeps a running record of what Claude did, in
`workspace/ai-use-log/`. It exists for two reasons:

1. **Reporting AI use in a paper or thesis.** Journals increasingly require you to name
   the tool and model, describe what it was used for, and confirm that the authors take
   responsibility. `workspace/ai-use-log/DISCLOSURE.md` holds a statement you can paste.
2. **Retracing your steps.** "Why is this file here, and where did that number come
   from" is a hard question six months later.

## The two halves

The record has a mechanical half and a narrative half, and they are kept separate on
purpose, because they are trustworthy in different ways.

| Half | Written by | Contains | Trust it because |
| :--- | :--------- | :------- | :--------------- |
| `YYYY-MM-DD-auto.md` | `log-session.sh` | Commits made, files touched | A machine produced it from git |
| `YYYY-MM-DD-NN-topic.md` | Claude | What was asked, what was done, what went wrong | Claude wrote it, so read it critically |

**Claude cannot read the conversation back.** It has no access to the transcript, so
its half is written from memory and is a reconstruction. The rules below require it to
say so and to avoid inventing detail. If the two halves disagree about what changed,
believe the automatic one.

---

## Setting it up

Two short blocks need pasting into files that Claude is not allowed to edit. That
restriction is deliberate: Claude cannot quietly change what gets recorded about it.

### 1. Make it run automatically

Open `.claude/settings.json` and find the `"hooks"` section. It currently has one
`SessionStart` hook. Add a `SessionEnd` hook so the whole section looks like this:

```json
"hooks": {
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "sh \"$CLAUDE_PROJECT_DIR/.claude/hooks/first-run-setup.sh\""
        }
      ]
    }
  ],
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "sh \"$CLAUDE_PROJECT_DIR/log-session.sh\""
        }
      ]
    }
  ]
},
```

Mind the comma after the closing `]` of `SessionStart`. Save, restart Claude Code, then
type `/doctor` to confirm the file still parses.

### 2. Tell Claude to write the narrative half

Open `CLAUDE.md` and add this section:

```markdown
## Recording AI use

This project keeps a record of what you did, in `workspace/ai-use-log/`.

Before you finish a piece of substantial work, add or update a session record there,
following `docs/AI-USE-LOG.md`. Substantial means: you changed several files, ran a
search or analysis, or produced something I might later cite or report.

You cannot read our conversation back, so write it from memory and say so. Never
invent detail you do not have. Always include what went wrong, what you retried, and
what you could not do.
```

That is all Claude needs in `CLAUDE.md`; the detail lives here.

---

## What Claude should write

When adding a session record, create
`workspace/ai-use-log/sessions/YYYY-MM-DD-NN-short-topic.md`, numbering from 01 within
a day, and include:

1. **A header** marking it a reconstruction, with the date, the model, and the Claude
   Code version. You cannot read the version from inside the sandbox, so ask for it and
   write "not recorded" if none is given.
2. **What was asked**, in order, in the user's words as closely as possible. Mark
   anything reconstructed rather than quoted.
3. **What was done**: files created, changed or deleted; commands that mattered; every
   website contacted and why.
4. **What was produced**, with file paths.
5. **What went wrong or could not be done.** Anything retried, any approach that
   failed, anything blocked by permissions or by a website, anything unverified. This
   section is the point of the exercise. A record without one is not worth keeping.
6. **What needs a human**: anything still to check, decide or finish.
7. **The commits**, by short hash and subject.

Then rewrite `DISCLOSURE.md` so it covers every session: a paste-ready paragraph naming
tool, model, purpose and human oversight; a table of sessions; and a plain statement of
what the AI did *not* do, where that affects how the work should be read.

### Two rules that matter

**Never put secrets in the log.** No passwords, keys or tokens, even if one appeared in
a command. Write `[redacted]` and name the file it came from.

**Do not tidy the history.** If an approach failed, or a first attempt was wrong, that
belongs in the record. The log is only useful if it is candid.

---

## If you want the verbatim transcript

Claude Code keeps raw session transcripts outside this project, under
`~/.claude/projects/`, in a folder named after this project's path. Claude cannot read
them: the sandbox blocks its commands from your home folder, by design. To archive them
yourself, in a terminal outside Claude Code:

```bash
mkdir -p workspace/ai-use-log/transcripts
cp ~/.claude/projects/<this-project-folder>/*.jsonl workspace/ai-use-log/transcripts/
```

Look before sharing. A transcript contains everything that was pasted into the
conversation.

## Running the automatic half by hand

```bash
sh log-session.sh
```

It appends any commits made since it last ran. Running it twice does nothing the second
time. It never fails a session: if anything goes wrong it reports and exits cleanly.
