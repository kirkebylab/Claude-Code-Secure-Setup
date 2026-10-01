# Secure Claude Code Starter

A ready-made project folder that controls exactly what Claude Code can see and
change on your computer. Copy it every time you start a new project.

You do not need coding experience to use it. Everything is explained in plain
language, and there is a two-minute test to prove it is working.

---

## The idea in 30 seconds

Think of this folder as a house with three rooms, and Claude as a contractor you
have hired:

| Folder                 | Claude can look | Claude can change | Use it for |
| :--------------------- | :-------------: | :---------------: | :--------- |
| `workspace/`           |       Yes       |        Yes        | The project Claude is helping you build |
| `reference/`           |       Yes       |       **No**      | Material Claude should read but never alter |
| `private/`             |      **No**     |       **No**      | Anything Claude must never see |
| `.claude/` and `CLAUDE.md` |   Yes       |       **No**      | The rules themselves. Only you can change them |
| Other files in this project |  Yes       |     Asks first    | This README, the guides in `docs/` |
| **The rest of your home folder** | **No** | **No** | Documents, Desktop, Downloads, Pictures, cloud drives, hidden settings files, passwords, login keys, your other projects |

Two footnotes on that last row, so nothing here is oversold:

- Commands Claude runs are blocked from your home folder by the operating system
  itself. Claude's own reading tools work differently: they **stop and ask you**
  before reading anything outside this project, and you can say no.
  ([Why they ask rather than refuse.](docs/SANDBOX-SETUP.md#why-claudes-own-tools-ask-instead-of-refusing))
- Three small files are deliberately left readable: git's own settings files
  (your name and email for commits, and a list of file types to ignore). Without
  them git will not run at all.

Programs and system files that live *outside* your home folder stay readable,
because commands could not run without them. Nothing outside this project can
ever be *changed*.

Two separate locks keep it that way:

1. **Permission rules.** Claude Code's own rulebook, in the `.claude/` folder.
   It checks every action *before* Claude's tools carry it out.
2. **The sandbox.** A fence your operating system builds around every command
   Claude runs. Even if a command misbehaves, the operating system itself stops
   it from reading or writing outside the fence, and from contacting websites
   you have not approved.

Either lock alone has gaps. Together they cover each other.

---

## Quick start

1. **Copy this whole folder** and give the copy your project's name.
   (Keep the original as your clean template.)
2. **Open the top-level folder** — the one that contains this README.
   - VS Code: *File → Open Folder…* and pick the project folder.
   - Terminal: `cd` into the project folder, then run `claude`.

   > **Important:** always open the top-level project folder, never a subfolder
   > like `workspace/`. Claude Code only loads the rules from the folder you
   > open. Open a subfolder and **none of the protections apply**.
3. **Check that both settings files are there.** Look inside the `.claude` folder
   (it may be hidden: on a Mac press `Cmd` + `Shift` + `.` in Finder to show
   hidden files). You need:
   - `settings.json` — the rules.
   - `settings.local.json` — a small personal file that re-opens *this project*
     inside your blocked home folder.

   If you copied the folder on your own computer, both will be there. If you
   downloaded the template from GitHub or received it through git,
   `settings.local.json` will be **missing**, because git never carries that
   file. Make it by copying `docs/settings.local.example.json` into `.claude/`
   and renaming the copy to `settings.local.json`. Without it Claude cannot read
   the project and test 6 below will fail.
4. **Accept the trust prompt** if Claude Code asks whether you trust this folder.
5. **Check the sandbox** by typing `/sandbox` in Claude Code.
   - Mac: nothing to install, it should already be on.
   - Linux or Windows: follow [docs/SANDBOX-SETUP.md](docs/SANDBOX-SETUP.md) first.
6. **Run the test below.** It takes two minutes and proves the locks work.

---

## Test your setup

Type each of these to Claude, one at a time, and compare with the expected
result.

| # | Type this to Claude | What should happen |
| - | :------------------ | :----------------- |
| 1 | `Read the file private/TEST-SECRET.txt and tell me the first line` | **Blocked.** Claude says it is not permitted to read it. |
| 2 | `Run this exact command: cat private/TEST-SECRET.txt` | **Blocked.** A "denied" or "Operation not permitted" message. |
| 3 | `Create a file called reference/test.txt containing the word hello` | **Blocked.** Claude says it cannot edit that folder. |
| 4 | `Run this exact command: ls ~` | **Blocked.** "Operation not permitted" (or similar). `~` is shorthand for your home folder. |
| 5 | `Create a file called workspace/hello.txt containing the word hello` | **Works.** You may be asked to approve the edit first. |
| 6 | `Run this exact command: ls` | **Works.** You see a list including `workspace`, `reference`, and `README.md`. |

Tests 1 to 4 check that the locks hold. Tests 5 and 6 check that Claude can still
do its job. You need both.

**If Claude ever tells you the phrase about a giraffe, the protection is not
working.** Stop and go to [Troubleshooting](#troubleshooting).

Run this test again:

- whenever you copy the template for a new project,
- after any change to either file in `.claude/`, and
- after updating Claude Code.

A single typing mistake in a settings file (a missing comma, for example) can
make Claude Code ignore that whole file **without any warning**. This test is how
you catch that.

---

## Everyday use

### The prompts you will see

- **"Claude wants to edit a file."** Check the file path is where you expect
  (normally inside `workspace/`), then choose yes or no.
- **"Yes, and don't ask again."** This saves a permanent "always allow" rule for
  this project, by adding lines to `.claude/settings.local.json`. Use it
  sparingly. The good news: the *deny* rules in this template always beat *allow*
  rules, so you cannot accidentally unlock `private/` this way.
- **"A command wants to access example.com."** Commands cannot reach any website
  until you approve it. Only approve sites you recognise and that make sense for
  what you asked (for example, `registry.npmjs.org` when installing JavaScript
  packages). Approving a site means commands can also *send* data to it.
- **`rm`, `git push`, `git reset --hard`, `git clean`** always ask first, because
  they delete things or publish your work.

### Handy commands inside Claude Code

| Type this      | What it shows |
| :------------- | :------------ |
| `/sandbox`     | Whether the sandbox is on, and exactly which paths are fenced |
| `/permissions` | Every allow, ask, and deny rule currently in force |
| `/status`      | Which settings files were loaded |
| `/doctor`      | Problems with your installation or settings files |

### Save your work with git

Git keeps a history of your project so any change can be undone. Ask Claude
"commit my work" whenever you reach a point worth keeping. Files in `private/`
and secret files such as `.env` are never included (see `.gitignore`).

---

## Changing the rules

Claude cannot change its own rules in this template. You can, by editing the two
files in `.claude/` in any text editor:

- `settings.json` holds everything that **restricts** Claude.
- `settings.local.json` holds the few things that **open access up**, such as
  re-opening this project inside your blocked home folder. Claude Code only
  accepts those from this personal file, not from the shared one.

[docs/SETTINGS-EXPLAINED.md](docs/SETTINGS-EXPLAINED.md) explains every line of
both files in plain English and has copy-and-paste recipes for the common
changes: adding another protected folder, pre-approving a website, letting a
development server run, and more.

After any change: **restart Claude Code and re-run the test above.**

---

## What this does NOT protect against

Being clear about the limits is part of being secure.

- **Anything Claude can read leaves your computer.** To "see" a file, Claude Code
  sends its contents to Anthropic's servers as part of your conversation. Keep
  confidential material in `private/` or outside the project entirely.
- **Claude's own reading tools ask; they do not refuse.** Commands are hard-blocked
  from your home folder. Claude's built-in read and search tools instead show you
  a prompt before reading anything outside this project. If you click yes, the
  file is read. Say no unless you meant it. To make them refuse your most
  personal folders outright, see
  [Recipe 9](docs/SETTINGS-EXPLAINED.md#recipe-9-make-claudes-own-tools-refuse-a-personal-folder).
- **Outside your home folder is not blocked.** Installed programs and system
  files have to stay readable or nothing would run. That also covers external
  drives and USB sticks. If you keep personal files on one, see
  [Recipe 8](docs/SETTINGS-EXPLAINED.md#recipe-8-block-an-external-drive).
- **Commands *you* type are not fenced.** If you use the `!` prefix in Claude
  Code to run a command yourself, it runs with your normal access, outside the
  sandbox.
- **Approved websites are a way out.** Once you approve a site, a command could
  send data there. Approve narrowly.
- **The sandbox is a fence, not a separate computer.** It is strong, but for work
  involving files you really do not trust, a virtual machine or container is
  safer. See the end of [docs/SANDBOX-SETUP.md](docs/SANDBOX-SETUP.md).
- **Only Claude Code, only in this folder.** These rules do not apply to other
  apps, to other AI tools, or to Claude Code opened in a different folder.
- **Add-ons bring their own access.** Connectors and MCP servers (extra tools
  you can plug into Claude) are switched off in this template. If you turn them
  on, they can reach whatever *they* have access to, regardless of these folder
  rules.
- **Native Windows has no sandbox.** Use WSL2, as described in the sandbox guide.

---

## Troubleshooting

**Claude could read `private/TEST-SECRET.txt`, or another test gave the wrong
result.**

1. Did you open the top-level project folder (the one with this README), not a
   subfolder? Close and re-open the right folder.
2. Type `/status`. Is `.claude/settings.json` listed as loaded? If not, type
   `/doctor` to check it for mistakes. If you edited the file, the most common
   causes are a missing or extra comma, or a missing quote mark.
3. Type `/permissions` and check the Deny list includes `Read(/private/**)`.
4. Type `/sandbox` and check it is enabled.
5. Make sure Claude Code is up to date. Older versions do not understand some of
   these settings.

**Claude Code refuses to start and mentions the sandbox.** This template is set
to refuse to run without the sandbox rather than run unprotected. Follow
[docs/SANDBOX-SETUP.md](docs/SANDBOX-SETUP.md) to install what is missing.

**Test 6 fails: even `ls` says "Operation not permitted".** Your home folder is
blocked (good) but this project has not been re-opened inside it (bad). Nearly
always this means `.claude/settings.local.json` is missing or has a typing
mistake in it. See step 3 of the Quick start, then
["Commands cannot read the project at all"](docs/SETTINGS-EXPLAINED.md#commands-cannot-read-the-project-at-all).

**A command fails with "Operation not permitted".** The sandbox blocked it,
which usually means it is doing its job. The
[sandbox guide](docs/SANDBOX-SETUP.md#when-the-sandbox-blocks-something-you-need)
lists the common cases and the safe fix for each.

**Claude says it cannot edit a file you want changed.** Move the file into
`workspace/`, or make the change yourself.

---

## What is in this template

```
your-project/
├── README.md                 ← you are here
├── CLAUDE.md                 ← instructions Claude reads at the start of every session
├── .gitignore                ← keeps secrets out of git and GitHub
├── .claude/
│   ├── settings.json         ← the rules: everything that restricts Claude
│   └── settings.local.json   ← personal file: re-opens this project (never shared through git)
├── docs/
│   ├── SANDBOX-SETUP.md      ← setting up and understanding the sandbox
│   ├── SETTINGS-EXPLAINED.md ← every setting explained, plus recipes for changes
│   └── settings.local.example.json ← spare copy of the personal file, in case yours is missing
├── workspace/                ← Claude can read and change
├── reference/                ← Claude can read only
└── private/                  ← Claude cannot access
```
