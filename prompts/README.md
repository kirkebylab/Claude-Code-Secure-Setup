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
| `/literature-review your topic` | Finds, downloads, summarises, and ranks papers on a topic | [literature-review.md](literature-review.md) |

**2. Copy and paste.** Open a prompt file, select everything, copy it, and paste
it into the Claude chat box. Replace anything in `[SQUARE BRACKETS]` first.

## Things to know

- Claude can read this folder, and asks you before changing anything in it.
  The slash-command copies in `.claude/commands/` can only be changed by you.
- Editing a prompt here does **not** change its slash command. The command
  file in `.claude/commands/` has the same text with a few extra lines at the
  top. Change both, or ask Claude to prepare the updated command file for you
  to copy in.
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
   cp prompts/weekly-summary.md .claude/commands/
   ```

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
