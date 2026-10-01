# The settings files explained

Two files in the `.claude/` folder hold the rules for this project:

| File | Its job |
| :--- | :------ |
| `settings.json` | The rulebook. Everything that **restricts** Claude |
| `settings.local.json` | A short personal file. The few things that **open access up**, above all re-opening this project inside your blocked home folder |

This page explains every part of both in plain English, then gives
copy-and-paste recipes for the changes people most often need.

Claude cannot edit either file. Only you can. That is deliberate: a rulebook the
contractor can rewrite is not much of a rulebook.

---

## Before you edit: five rules for not breaking it

Both files are written in a format called JSON, which is fussy. **If
`settings.json` contains a mistake, Claude Code ignores the whole file without
telling you, and every protection silently switches off.** (A mistake in
`settings.local.json` fails the safe way round: the project stays blocked and
Claude cannot work until you fix it.) So:

1. **Make a copy first** (`settings.json` → `settings-backup.json`) so you can
   always go back.
2. Text goes in straight double quotes: `"like this"`. Not 'single' quotes, not
   “curly” quotes. Use a plain text editor such as VS Code, never Word or Pages.
3. Items in a list are separated by commas, and **the last item has no comma
   after it**. This is the mistake nearly everyone makes.
4. You cannot add notes or comments inside the file.
5. After saving: **close and reopen Claude Code, type `/doctor` to check for
   mistakes, then re-run the test in the [main README](../README.md#test-your-setup).**

---

## How rules are decided

Every rule is one of three kinds:

| Kind      | Meaning                          |
| :-------- | :------------------------------- |
| **deny**  | Never. No prompt, no exceptions  |
| **ask**   | Stop and ask me every time       |
| **allow** | Go ahead without asking          |

When more than one rule matches, **deny beats ask, and ask beats allow.** This
holds across every settings file on your computer. It means:

- Nothing you click "always allow" on can ever unlock a denied folder.
- To loosen a deny rule you must delete it from this file by hand.

Anything with no matching rule falls back to Claude Code's normal behaviour:
reading inside the project is fine, editing asks first, and commands run inside
the sandbox.

---

## How paths are written (read this, it is confusing)

There are two halves to the file and, unhelpfully, they write paths differently.

**In the `permissions` half** (rules for Claude's own tools):

| You write             | It means                                   |
| :-------------------- | :----------------------------------------- |
| `/private/**`         | The `private` folder **in this project**, and everything inside it |
| `~/.ssh/**`           | The `.ssh` folder in your home folder, and everything inside it |
| `//Users/sam/taxes/**`| A full path from the very top of the computer. Note the **two** slashes |
| `.env`                | Any file with this name, anywhere in the project |
| `**/*.pem`            | Any file ending in `.pem`, anywhere in the project |

`**` means "everything inside, however deep".

**In the `sandbox` half** (rules for commands):

| You write      | It means                                  |
| :------------- | :---------------------------------------- |
| `./private`    | The `private` folder in this project      |
| `~/.ssh`       | The `.ssh` folder in your home folder     |
| `/tmp/build`   | A full path from the top of the computer. **One** slash here |

The trap: a single leading `/` means "this project" in the top half and "the top
of the computer" in the bottom half.

---

## The file, part by part

### `permissions` — rules for Claude's own tools

```json
"defaultMode": "default",
```
Start every session in the normal, careful mode: Claude asks before editing
files.

```json
"disableBypassPermissionsMode": "disable",
"disableAutoMode": "disable",
```
Claude Code has two hands-off modes. *Bypass* skips every safety prompt. *Auto*
lets an automated reviewer approve actions instead of you. Both are switched off
here so that **you** stay the one who approves things. Auto mode is a reasonable
thing to turn back on once you are comfortable (delete that one line); bypass
mode is not.

**One line you will not find here: `blockReadsOutsideWorkingDirectories`.** It is
left out on purpose. Without it, Claude's read and search tools **ask you first**
before reading anything outside this project, and you can say no. (This is about
Claude's own tools. *Commands* are blocked from your home folder separately, by
the sandbox section further down.)

**Do not add it.** Writing `"blockReadsOutsideWorkingDirectories": true` here
sounds stricter (those tools would refuse outright instead of asking), but it was
tested with this template and it breaks it: while it is on, Claude Code discards
the "re-open this project" lines in `settings.local.json`, and commands can no
longer read the project at all. The
[sandbox guide](SANDBOX-SETUP.md#why-claudes-own-tools-ask-instead-of-refusing)
has the details. To make Claude's own tools refuse particular folders outright,
use [Recipe 9](#recipe-9-make-claudes-own-tools-refuse-a-personal-folder)
instead.

```json
"allow": [],
```
Empty on purpose. Nothing is pre-approved. Recipes below add to it.

```json
"ask": [
  "Bash(rm *)",
  "Bash(git push *)",
  "Bash(git reset --hard *)",
  "Bash(git clean *)"
],
```
Four commands that always stop and ask, even inside the sandbox: deleting files,
publishing your work to the internet, and two git commands that throw away
changes. `Bash(...)` means "a command Claude runs".

These are speed bumps, not walls. There are other ways to delete a file than
`rm`. The real protection against losing work is committing to git regularly.

```json
"deny": [
  "Read(/private/**)",
  "Edit(/private/**)",
```
**The private zone.** Claude cannot read anything in `private/`, and cannot
create or change anything there either.

```json
  "Edit(/reference/**)",
```
**The read-only zone.** Reading is fine; changing is never allowed. `Edit` covers
every way Claude has of writing a file: editing, creating, and overwriting.

```json
  "Edit(/.claude/**)",
  "Edit(/CLAUDE.md)",
  "Edit(/.mcp.json)",
```
**Claude cannot change its own rules.** Not this settings file, not its
instruction sheet (`CLAUDE.md`), and not `.mcp.json`, the file that would plug
in extra tools.

```json
  "Read(.env)",
  "Read(.env.*)",
  "Read(**/*.pem)",   ... and similar lines
  "Read(**/secrets/**)",
  "Read(**/credentials.json)",
```
**Secret files anywhere in the project.** `.env` files are where programmers
keep passwords and API keys. The `.pem`, `.key`, `.p12`, `.pfx` and `id_rsa`
lines are types of digital key.

The `.env.*` line blocks **every** file whose name starts with `.env.`, and that
includes `.env.example`, the name programmers often give to a harmless file of
placeholder values showing which settings exist. One name cannot be carved out
of a deny rule: an exception line was tried and it did not work, because deny
always wins. So in this template, give that placeholder file a name that does
not start with `.env`: **`env.example`**. Claude can read and write a file with
that name. This was tested.

```json
  "Read(~/.ssh/**)",
  "Read(~/.aws/**)",   ... and similar lines
```
**Well-known places in your home folder where login details live**: keys for
servers, cloud accounts, GitHub, and package sites. Commands are already blocked
from your whole home folder by the sandbox section further down, so for commands
these lines are a second lock. For Claude's *own* tools they are the main lock:
without them those tools would only ask before reading these folders; with them
they refuse. They also stay in force if you ever re-open part of your home
folder.

```json
  "Bash(sudo *)"
]
```
`sudo` means "run this with full administrator power over the computer". Never.

### `sandbox` — the fence around commands

```json
"enabled": true,
"failIfUnavailable": true,
```
Turn the sandbox on, and if it cannot start, **refuse to run at all** rather than
quietly carrying on without it.

```json
"autoAllowBashIfSandboxed": true,
```
Commands that stay inside the fence run without asking you each time. This is
what makes the sandbox pleasant to use: the fence does the protecting, so you are
not clicking "yes" fifty times an hour (which is how people end up approving
things without reading them). Prefer to approve every command yourself? Change
`true` to `false`.

```json
"allowUnsandboxedCommands": false,
"excludedCommands": [],
```
Strict mode. If the fence blocks a command, Claude cannot simply re-run it
outside the fence. `excludedCommands` is the list of commands permitted to run
with no fence; it is empty, and best left that way.

```json
"filesystem": {
  "denyRead": ["~/"],
```
**Block commands from reading your entire home folder.** `~/` is shorthand for
your home folder: Documents, Desktop, Downloads, cloud drives, hidden settings
files, other projects, all of it.

Your project lives inside your home folder too, so on its own this line would
block the project as well. The matching "re-open this project" line lives in the
second file, `settings.local.json`, [explained below](#the-second-file-settingslocaljson).
When a blocked area and a re-opened area overlap, **the more specific one wins**.
That is why this project is readable although it sits inside your blocked home
folder, and why `private/` stays blocked although it sits inside the readable
project.

```json
  "denyWrite": ["./reference", "./private"],
  "allowWrite": []
},
```
Commands can write inside this project only, and not in these two folders.
Claude Code also automatically protects its own rule files from commands.

```json
"network": {
  "allowedDomains": []
},
```
The list of websites commands may contact without asking. Empty, so the first
time any command wants any website, you get a prompt.

```json
"credentials": {
  "envVars": [ { "name": "GITHUB_TOKEN", "mode": "deny" }, ... ]
}
```
Some programs keep passwords in your computer's memory as "environment
variables". These lines hide the most common ones from commands Claude runs.
Harmless if you do not have any.

### The last two lines

```json
"enableAllProjectMcpServers": false,
"disableClaudeAiConnectors": true
```
MCP servers and connectors are add-ons that give Claude extra abilities, such as
reaching your Google Drive, email, or calendar. They are powerful, and they
operate completely outside the folder rules above. The first line means add-ons
bundled with a project are never switched on without asking you. The second
switches off, **inside this project only**, any connectors you have set up on
claude.ai. To use your connectors here, change `true` to `false`.

### The second file: `settings.local.json`

This is the whole file as it ships:

```json
{
  "sandbox": {
    "filesystem": {
      "allowRead": [
        ".",
        "~/.gitconfig",
        "~/.gitignore_global",
        "~/.config/git"
      ]
    }
  }
}
```

`allowRead` re-opens places inside a blocked area, for commands:

- `.` means "this project folder", wherever it happens to be. You never need to
  change it when you copy the template somewhere new.
- The other three are git's own settings files: your name and email for commits,
  and a list of file types git should ignore. Git refuses to run at all if it
  cannot read them. If you keep anything sensitive in them, take them out of the
  list and run git yourself in a normal terminal instead.

**Why is this a separate file?** When this template was tested, Claude Code
ignored `allowRead` written in `settings.json` and applied it from this file.
`settings.json` is the *shared* file that travels with a project;
`settings.local.json` is *your* file on *your* computer. The likely reasoning is
that a project you download should not be able to open up your computer on its
own say-so.

Three things follow from that:

- **Git never carries this file** (it is listed in `.gitignore`, and Claude Code
  stops treating it as yours if git tracks it). A spare copy lives at
  `docs/settings.local.example.json`.
- **Claude Code writes to this file too.** When you click "Yes, and don't ask
  again" on a prompt, the choice is saved here, in a `"permissions"` section
  alongside the `"sandbox"` one. Open the file now and then to see what you have
  approved, and delete any line you no longer want, but leave the `"sandbox"`
  section alone. Nothing in this file can override a `deny` rule in
  `settings.json`.
- **If it goes missing, nothing is exposed.** Everything simply stays blocked,
  this project included, and test 6 fails until you put the file back.

---

## Recipes

Each recipe shows what part of a file should look like **after** the change. Find
the matching piece in your file and make it look the same. Mind the commas.

**Which file?** Each recipe says. The rule of thumb:

- A change that **restricts** Claude goes in `settings.json`. These were tested
  and they work.
- A change that **opens access up** goes in `settings.local.json`. Only one such
  setting has actually been tested (`allowRead`: ignored in `settings.json`,
  applied from `settings.local.json`). Recipes 2, 4, 5 and 6 use other
  access-opening settings that have **not** been tested in either file, so they
  are placed where the tested one worked. If one of them seems to do nothing, it
  is not you. For a website you can always just approve it when the prompt
  appears.

Recipes for `settings.local.json` show the **whole file**, because its nesting is
easy to get wrong. If Claude Code has added a `"permissions"` section to your
copy, keep that section and change only the `"sandbox"` part.

### Recipe 1: Protect another folder

*File: `settings.json`.*

Read-only, like `reference/` — for a folder called `originals`. One line in the
`deny` list and one entry in `denyWrite`:

```json
"Edit(/reference/**)",
"Edit(/originals/**)",
```
```json
"denyWrite": ["./reference", "./private", "./originals"],
```

No access at all, like `private/` — for a folder called `clients`. Two lines in
the `deny` list:

```json
"Read(/private/**)",
"Edit(/private/**)",
"Read(/clients/**)",
"Edit(/clients/**)",
```
```json
"denyWrite": ["./reference", "./private", "./clients"],
```

You do not need to add a no-access folder to `denyRead`. Claude Code copies
`Read` deny rules into the sandbox for you. Do consider adding a line for it to
`.gitignore` so it is never uploaded.

Afterwards, put a test file in the new folder and try tests 1 to 3 from the
README against it.

### Recipe 2: Pre-approve a website

*File: `settings.local.json`. Not tested: see "Which file?" above.*

So commands can reach it without a prompt. Be specific, and only add sites you
would approve anyway. The simplest route needs no editing at all: when the prompt
appears, choose "Yes, and don't ask again" and Claude Code records it for you.
To do it by hand, the whole file becomes:

```json
{
  "sandbox": {
    "filesystem": {
      "allowRead": [
        ".",
        "~/.gitconfig",
        "~/.gitignore_global",
        "~/.config/git"
      ]
    },
    "network": {
      "allowedDomains": ["registry.npmjs.org", "pypi.org", "files.pythonhosted.org"]
    }
  }
}
```

Those three cover installing JavaScript and Python packages. `*.example.com`
allows every sub-site of `example.com`. Remember that an approved site is a place
data can be sent as well as fetched.

### Recipe 3: A tool installed in your home folder will not run

*File: `settings.local.json`. Tested: this is the same setting that re-opens the
project.*

Some programming tools install themselves inside your home folder, which is
blocked, so commands cannot find or start them. Re-open just that tool's folder
by adding it to `allowRead`. Add the narrowest folder that works: the tool's own
folder, never `~/` itself. For example, for Node installed with `nvm` and Python
installed with `pyenv`:

```json
{
  "sandbox": {
    "filesystem": {
      "allowRead": [
        ".",
        "~/.gitconfig",
        "~/.gitignore_global",
        "~/.config/git",
        "~/.nvm",
        "~/.pyenv"
      ]
    }
  }
}
```

Other common ones: `~/.rustup` and `~/.cargo/bin` (Rust), `~/.bun` (Bun),
`~/.local/bin` (assorted tools). Not sure where a tool lives? In a normal
terminal, type `which` and the tool's name, for example `which node`. If the
answer starts with `/Users/your-name/` or `/home/your-name/`, it is in your home
folder.

These folders hold programs, not personal files. Still, look before you add one.

### Recipe 4: Installing packages fails because of a cache folder

*File: `settings.local.json`. The `allowWrite` part is not tested: see "Which
file?" above.*

Package installers keep a cache in your home folder, which commands can neither
read nor write. Often you can simply ignore the warning: most installers carry on
without their cache. If an install really does fail, open up that one folder for
reading and writing. For `npm`:

```json
{
  "sandbox": {
    "filesystem": {
      "allowRead": [
        ".",
        "~/.gitconfig",
        "~/.gitignore_global",
        "~/.config/git",
        "~/.npm"
      ],
      "allowWrite": ["~/.npm"]
    }
  }
}
```

For Python's `pip` on a Mac the folder is `~/Library/Caches/pip`; on Linux it is
`~/.cache/pip`.

A tidier alternative for Python: ask Claude to create a "virtual environment"
inside `workspace/`. Packages then install inside the project, where reading and
writing are already allowed.

### Recipe 5: Let a local development server run

*File: `settings.local.json`. Not tested: see "Which file?" above.*

If you are building a website and want to preview it on your own computer:

```json
{
  "sandbox": {
    "filesystem": {
      "allowRead": [
        ".",
        "~/.gitconfig",
        "~/.gitignore_global",
        "~/.config/git"
      ]
    },
    "network": {
      "allowLocalBinding": true
    }
  }
}
```

### Recipe 6: A command that cannot work inside the fence

*File: `settings.local.json`. Not tested: see "Which file?" above.*

Try everything else first. Running the command yourself in a normal terminal is
nearly always the better answer.

```json
{
  "sandbox": {
    "excludedCommands": ["docker *"],
    "filesystem": {
      "allowRead": [
        ".",
        "~/.gitconfig",
        "~/.gitignore_global",
        "~/.config/git"
      ]
    }
  }
}
```

Understand the trade: a command listed here runs with **no fence at all**, and so
does anything it starts. Docker in particular can reach your whole computer. Keep
this list as short as you possibly can.

### Recipe 7: Use your claude.ai connectors in this project

*File: `settings.json`. Change the last line of the file:*

```json
"disableClaudeAiConnectors": false
```

Connectors reach whatever *they* are connected to (your Drive, your mail). The
folder rules in this file do not apply to them.

### Recipe 8: Block an external drive

*File: `settings.json`. Restricting settings like this one were tested and work.*

Your home folder is blocked, but an external drive or USB stick is not part of
your home folder. If you keep personal files on one, add it to `denyRead`. On a
Mac, drives appear under `/Volumes/` followed by the drive's name:

```json
"denyRead": ["~/", "/Volumes/My Backup Drive"],
```

Note the single `/` at the start: in this half of the file that means "from the
top of the computer". Afterwards check it the same way as test 4, for example
`ls "/Volumes/My Backup Drive"`.

### Recipe 9: Make Claude's own tools refuse a personal folder

*File: `settings.json`. This kind of rule was tested on `private/`; it has not
been tested on home-folder paths.*

Commands are already blocked from your whole home folder. Claude's *own* reading
tools are not blocked there; they ask you first. To make them refuse a folder
outright, with no prompt, add a `Read` line for it to the `deny` list:

```json
"Read(~/.git-credentials)",
"Read(~/Documents/**)",
"Read(~/Downloads/**)",
"Read(~/Pictures/**)",
"Bash(sudo *)"
```

Two warnings:

- **Never add a line that covers the folder this project lives in.** Deny rules
  beat everything, so if this project is at `~/Desktop/my-project`, a line for
  `~/Desktop/**` locks Claude out of the project, and so would `Read(~/**)`.
- Do not reach for `blockReadsOutsideWorkingDirectories` instead. It breaks this
  template, which is why it is left out: see the explanation of that setting
  near the top of this page.

To check it, ask Claude to read a file in that folder. It should be refused
straight away, with no prompt.

---

## Commands cannot read the project at all

**Symptom:** test 6 in the README fails. Even a plain `ls` says "Operation not
permitted", `git` may complain it cannot access `.gitconfig`, and scripts in
`workspace/` will not run. Meanwhile tests 1 to 4 pass.

**What it means:** your home folder is blocked, which is right, but this project
has not been re-opened inside it. The locks are all still holding; Claude just
cannot work. Nothing has been exposed.

Work down this list and stop as soon as test 6 passes. Close and reopen Claude
Code after each change.

**Step 1. Is `settings.local.json` there?** Look in the `.claude` folder (on a
Mac, press `Cmd` + `Shift` + `.` in Finder to show hidden files). If the file is
missing, copy `docs/settings.local.example.json` into `.claude/` and rename the
copy to `settings.local.json`. This is the usual cause when the template came
from GitHub, because git never carries that file.

**Step 2. Does it still have its `"sandbox"` section?** Open it and compare it
with [the listing above](#the-second-file-settingslocaljson). It must contain the
`"allowRead"` list with `"."` in it. If it has been damaged, or you are not sure,
the quickest fix is to replace the `"sandbox"` section with the one from
`docs/settings.local.example.json`. Check the commas and brackets: a single
mistake makes Claude Code ignore the whole file.

**Step 3. Is git tracking the file?** It should not be. If you deliberately added
`settings.local.json` to git, Claude Code stops treating it as your personal file
and may hold back what is in it. Ask Claude to "stop tracking
.claude/settings.local.json in git without deleting it".

**Step 4. Has the stricter switch been added?** Search `settings.json` for
`blockReadsOutsideWorkingDirectories`. The template does not include that line.
If it is there and set to `true`, delete the whole line: it makes Claude Code
discard the re-open lines from Step 2, which produces exactly this symptom. This
was tested.

**Step 5. Look at what the sandbox thinks.** Type `/doctor` to check both files
for mistakes. Then type `/sandbox`, open the **Config** tab, and look for this
project's folder among the paths that are re-allowed for reading.

When test 6 passes, run the other five as well, to make sure the locks still
hold.

---

Official reference: <https://code.claude.com/docs/en/settings> and
<https://code.claude.com/docs/en/permissions>
