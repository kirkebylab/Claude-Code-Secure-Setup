# prompts/ — ready-made instructions for Claude

Each file in this folder is one prompt: a full set of instructions you can give
Claude in one go. There are two ways to use them.

**1. Type a slash command (easiest).** Every prompt here is also installed as a
command in `.claude/commands/`. Type `/` in Claude Code and pick one:

| Type this | What Claude does | Prompt |
| :-------- | :--------------- | :----- |
| `/test-setup` | Runs the six safety tests from the main README and reports pass or fail | [test-setup.md](test-setup.md) |
| `/save-work` | Checks your changes for passwords and keys, then saves them with git | [save-work.md](save-work.md) |
| `/qpcr-demo` | Walks you through analysing the fake qPCR dataset in `reference/` | [qpcr-demo.md](qpcr-demo.md) |
| `/literature-review your topic` | Finds, verifies, downloads, summarises, and ranks papers on a topic | [literature-review.md](literature-review.md) |

The literature-review prompt ends with a field guide telling Claude how to fetch full
texts properly: which official open-access services to use, which routes are dead ends,
and where to stop. It is part of that prompt, not a separate file.

**2. Copy and paste.** Open a prompt file, select everything, copy it, and paste
it into the Claude chat box. Replace anything in `[SQUARE BRACKETS]` first.

## Things to know

- Claude can read this folder, and asks you before changing anything in it.
  The slash-command copies in `.claude/commands/` can only be changed by you.
- Editing a prompt here does **not** change its slash command. The command is a
  separate copy in `.claude/commands/`, and Claude is not allowed to write there,
  so the two drift apart as soon as a prompt is improved. To re-copy them all,
  open a terminal in the project folder and run:

  ```bash
  sh sync-prompts.sh
  ```

  It keeps the few lines at the top of each command file (the description shown
  in the `/` menu) and replaces only the body. Restart Claude Code afterwards.
  You run it yourself: the sandbox stops Claude writing to `.claude/`, which is
  the point.
- If a command loses those top lines it also loses
  `disable-model-invocation: true`, which means Claude may decide to run it on
  its own rather than waiting for you to type it. `sync-prompts.sh` warns you
  when a command is missing them.
- Some prompts need the internet (the literature review, and installing Python
  packages for the qPCR demo). Claude Code asks you to approve each website the
  first time. Approve only sites that make sense for the task.
- Everything Claude reads, including downloaded papers, is sent to Anthropic as
  part of the conversation.

## Adding your own prompt

1. Create a new file in this folder, for example `weekly-summary.md`. Write it
   as if you were briefing a capable new colleague: what you want, where the
   input is, where the output should go (somewhere in `workspace/`), and what
   "done" looks like.
2. To make it a slash command too, copy it into `.claude/commands/`. Only you
   can do this; Claude cannot. The file name becomes the command name, so
   `weekly-summary.md` becomes `/weekly-summary`. In VS Code's terminal
   (*Terminal → New Terminal*, which opens in the project folder):

   ```bash
   sh sync-prompts.sh
   ```

   That copies every prompt into `.claude/commands/`, creating any that are missing.

3. Optional: open the copy in `.claude/commands/` and add these lines at the
   very top. The first gives the command a description in the `/` menu; the
   second means Claude runs it only when you type it, never on its own.

   ```
   ---
   description: One line saying what the command does
   disable-model-invocation: true
   ---
   ```

If the new command does not appear when you type `/`, close and reopen Claude
Code.
