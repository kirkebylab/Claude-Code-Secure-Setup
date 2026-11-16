# ai-use-log/ — a record of how AI was used

What this folder is for:

1. **Reporting AI use in a paper or thesis.** Most journals now ask you to name the
   tool and model, say what it was used for, and confirm that the authors take
   responsibility for the content. `DISCLOSURE.md` holds a paste-ready statement.
2. **Retracing your steps.** Months later, "why is this file here and where did that
   number come from" is a hard question. The session records answer it.

## What is in here

| File | What it is | Written by |
| :--- | :--------- | :--------- |
| `DISCLOSURE.md` | A statement you can paste into a methods or acknowledgements section | Claude |
| `sessions/YYYY-MM-DD-auto.md` | Commits made and files touched | `log-session.sh` |
| `sessions/YYYY-MM-DD-NN-topic.md` | What was asked, what was done, what went wrong | Claude |

Both halves are produced without you asking, once the setup in
[docs/AI-USE-LOG.md](../../docs/AI-USE-LOG.md) is done. The automatic half runs at the
end of each session; the narrative half is written by Claude after substantial work.

The two are kept separate on purpose. The automatic half comes from git and is simply
true. The narrative half is Claude's account and should be read critically. Where they
disagree about what changed, believe the automatic one.

## What these records are, and are not

**They are reconstructions, not transcripts.** Claude cannot read our conversation
back; it has no access to the transcript. Each record is written from what Claude
remembers of the session, and says so. Parts that are uncertain are marked as
uncertain.

**The git history is the authoritative record of what changed.** Every session record
lists the commits it produced. If a record and the commits disagree, believe the
commits: they are a machine-made record of the files, while the session notes are
Claude's account of the reasoning.

**If you want a verbatim archive**, Claude Code keeps raw session transcripts outside
this project, under `~/.claude/projects/` in a folder named after this project's path.
Claude cannot reach them, because the sandbox blocks its commands from your home
folder, and that is deliberate. To keep copies, run this in a terminal outside Claude
Code:

```bash
mkdir -p workspace/ai-use-log/transcripts
cp ~/.claude/projects/<this-project-folder>/*.jsonl workspace/ai-use-log/transcripts/
```

Look at them before sharing. A transcript contains anything that was pasted into the
conversation.

## A note on honesty

These records are only worth keeping if they include the parts that went badly. Each
one has a section for what went wrong, what was retried, and what could not be done.
If a record contains no such section, be suspicious of it.
