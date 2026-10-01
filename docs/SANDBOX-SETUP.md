# Sandbox setup

## What the sandbox is

When Claude works on your project it often needs to run commands: installing a
package, running a script, using git. A command is a small program, and programs
can do more than their name suggests.

The **sandbox** is a fence that your operating system builds around every
command Claude runs. Inside the fence a command can do its job. It cannot climb
out, no matter what it tries, because the operating system itself says no. It
does not rely on Claude behaving well or on you spotting a bad command.

In this template the fence is set up like this:

| A command run by Claude can...                 |        |
| :--------------------------------------------- | :----- |
| Read files in this project                     | Yes, except `private/` and secret files like `.env` |
| Create and change files in this project        | Yes, except `reference/`, `private/`, and Claude's own rule files |
| Read anything else in your home folder: Documents, Desktop, Downloads, cloud drives, hidden settings files, passwords, keys, other projects | **No**. The only exceptions are git's three small settings files. See [how](#how-the-home-folder-block-works) |
| Read installed programs and system files outside your home folder | Yes. Commands could not run otherwise |
| Change anything outside this project           | **No** |
| Contact a website                              | Only after you approve that site |
| Run outside the sandbox if the sandbox gets in the way | **No** (strict mode) |
| Run at all if the sandbox cannot start         | **No** (Claude Code refuses to start) |

---

## Step 1. Get your computer ready

### Mac

Nothing to install. macOS has the needed technology (called Seatbelt) built in.
Go to Step 2.

### Linux

Install two small helper programs. Open a terminal and run the line for your
system:

```bash
# Ubuntu or Debian
sudo apt-get install bubblewrap socat

# Fedora
sudo dnf install bubblewrap socat
```

`bubblewrap` builds the fence around files. `socat` lets Claude Code control
which websites commands can reach.

**Ubuntu 24.04 or newer only:** Ubuntu blocks a feature bubblewrap needs. Check
with:

```bash
sysctl kernel.apparmor_restrict_unprivileged_userns
```

- If it prints `0`, or says `No such file or directory`, you are fine. Skip ahead.
- If it prints `1`, run these two commands to give bubblewrap (and only
  bubblewrap) permission:

```bash
sudo tee /etc/apparmor.d/bwrap > /dev/null <<'EOF'
abi <abi/4.0>,
include <tunables/global>

profile bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
  include if exists <local/bwrap>
}
EOF

sudo systemctl reload apparmor
```

Then restart Claude Code and go to Step 2.

### Windows

The sandbox does not work on Windows directly. It works inside **WSL2**, a free
Microsoft feature that runs Linux inside Windows.

1. Open **PowerShell as Administrator** and run `wsl --install`. Restart when
   asked. This installs Ubuntu.
2. Open **Ubuntu** from the Start menu and create a username and password.
3. Check the version: in PowerShell run `wsl -l -v`. The VERSION column must say
   **2**. (Version 1 cannot run the sandbox.)
4. Inside Ubuntu, install Claude Code, then follow the **Linux** steps above.
5. Keep your project **inside Ubuntu's own files** (for example
   `~/projects/my-project`), not under `/mnt/c/...`. It is faster and the fence
   works more predictably.

If you open this project with Claude Code on plain Windows, it will refuse to
start. That is deliberate: this template would rather not run than run
unprotected.

---

## Step 2. Confirm the sandbox is on

1. Open the top-level project folder in Claude Code.
2. Type `/sandbox`.

You will see a panel with tabs:

- **Mode** — should show the sandbox is enabled with *auto-allow*. Auto-allow
  means commands that stay inside the fence run without interrupting you. Anything
  that needs to step outside still asks.
- **Overrides** — should show **strict sandbox mode**. Claude cannot re-run a
  blocked command outside the fence.
- **Config** — lists the exact folders that are readable, writable, and denied on
  your computer. Worth a look: you should see your `private` and `reference`
  folders in the denied lists.
- **Dependencies** (Linux only) — appears only if something from Step 1 is
  missing, and tells you what.

If `/sandbox` is not available in the VS Code panel, open VS Code's built-in
terminal (*Terminal → New Terminal*), run `claude`, and type it there.

> **Do not change the mode in this panel unless you mean to.** Choices you make
> there are saved to `.claude/settings.local.json` and override the template.

## Step 3. Prove it

Run the six-line test in the [main README](../README.md#test-your-setup). Tests
2, 4 and 6 specifically check the sandbox: two things it must block, and one
thing it must allow.

---

## When the sandbox blocks something you need

An "Operation not permitted" message usually means the fence is working. Here
are the common cases and the safest fix for each. Fixes are made by you, in the
two settings files in `.claude/`; the exact text to paste, and which file it goes
in, is in [SETTINGS-EXPLAINED.md](SETTINGS-EXPLAINED.md#recipes).

| What you see | Why | Safest fix |
| :----------- | :-- | :--------- |
| A prompt asking to allow a website | Commands cannot reach any site until you say so | Approve it if you recognise it and it fits the task. Choose "don't ask again" only for sites you will use constantly |
| Even `ls` fails, in the project folder itself | Your home folder is blocked but this project was not re-opened inside it. Usually `.claude/settings.local.json` is missing or has a typing mistake | See ["Commands cannot read the project at all"](SETTINGS-EXPLAINED.md#commands-cannot-read-the-project-at-all) |
| `node`, `python`, or another tool "cannot be found" or is "not permitted" | That tool was installed inside your home folder, which is blocked | Re-open just that tool's folder (Recipe 3) |
| Installing packages fails on a cache folder | Package managers keep a cache in your home folder, which commands can neither read nor write | Often you can ignore it: most installers carry on without their cache. Otherwise open up that one folder (Recipe 4) |
| A local web server will not start ("address" or "bind" error) | Opening a network port is off by default | Turn on `allowLocalBinding` (Recipe 5) |
| `git` fails with `unable to unlink old` | Git tried to replace a protected file | Run that one git command yourself in a normal terminal |
| `docker` does not work | Docker cannot run inside the fence | Run docker commands yourself, or see Recipe 6 and understand the trade-off first |
| `gh` (GitHub's tool) fails with a certificate error on Mac | A known incompatibility | Run `gh` commands yourself in a normal terminal |
| `open`, or a login that opens your browser, fails on Mac | Launching other apps is blocked, because an app launched this way is outside the fence | Do that step yourself |

Two fixes to **avoid**, because they quietly remove the protection:

- Setting `"enabled": false` or `"allowUnsandboxedCommands": true`.
- Adding everyday commands to `excludedCommands`. A command listed there runs
  with **no fence at all**, and so does everything it launches.

---

## How the home-folder block works

Your project almost certainly lives somewhere inside your home folder (on the
Desktop, in Documents, in a Projects folder). So the fence has to do two things
at once: block the whole home folder, and re-open just this project inside it.
It takes two files to do that:

| File | What it says | Why it is there |
| :--- | :----------- | :-------------- |
| `.claude/settings.json` | Block the entire home folder (`"denyRead": ["~/"]`) | Settings that *restrict* Claude work from this shared file |
| `.claude/settings.local.json` | Re-open this project folder, plus git's three small settings files (`allowRead`) | In testing, Claude Code ignored this re-opening setting when it came from the shared file, and accepted it from this personal one. The likely reason: a project you downloaded should not be able to open up your computer by itself; only you can |

When a blocked area and a re-opened area overlap, the more specific one wins.
That is why this project is readable even though it sits inside the blocked home
folder, and why `private/` stays blocked even though it sits inside the readable
project.

This was tested on a Mac with the VS Code version of Claude Code: with both
files in place, commands could list and run things in the project, and were
refused on the home folder itself, Documents, Downloads, Desktop, Library,
hidden settings files, and the key folders.

Things worth knowing:

- **The personal file never travels through git.** That is deliberate (if git
  tracks the file, Claude Code stops treating it as yours). Copying the project
  folder on your own computer keeps it. Downloading the template from GitHub does
  not, so recreate it from `docs/settings.local.example.json`. Step 3 of the
  Quick start in the main README walks through it.
- **The `.` in that file means "this project folder", wherever it is.** You do
  not need to edit it when you copy the template to a new place.
- **Other projects are blocked too.** A project in `~/Projects/a` cannot be read
  from a Claude session opened in `~/Projects/b`.
- **If the personal file goes missing, the failure is safe.** Everything stays
  blocked, including the project, so Claude simply cannot work until you put it
  back. Nothing gets exposed.

---

## Why Claude's own tools ask instead of refusing

The sandbox covers *commands*. Claude's built-in tools for reading and searching
files are governed by the permission rules instead, and for anything outside this
project they **stop and ask you**. If you say no, nothing is read.

There is a setting that looks like the obvious way to make them refuse outright:
`"blockReadsOutsideWorkingDirectories": true`. **This template leaves it out on
purpose. Do not add it.** It was
tested with this template (on a Mac, with the VS Code version of Claude Code) and
it breaks it: while the switch is on, Claude Code discards the lines in
`settings.local.json` that re-open this project, so commands can no longer read
the project at all. Test 6 fails, scripts will not run, and git stops working.
It fails the safe way round (everything stays locked, nothing is exposed), but
Claude cannot do any work.

Leaving it out costs nothing on the commands side. Commands are blocked from your
whole home folder by the `denyRead` line, which is separate from this switch.

If you want Claude's own tools to refuse particular folders outright, rather than
ask, you can name them:
[Recipe 9](SETTINGS-EXPLAINED.md#recipe-9-make-claudes-own-tools-refuse-a-personal-folder).

It is worth re-testing the switch after a Claude Code update, since this may
change. In `settings.json`, add `"blockReadsOutsideWorkingDirectories": true,` on
its own line just above `"allow": [],` (mind the comma at the end). Restart and
run test 6. If `ls` works, keep it. If not, delete the line again.

---

## Optional: tighter network control

By default, a command that wants a new website makes Claude Code ask you. If you
would rather unknown sites were **refused outright, with no prompt**, you can
turn on a strict allowlist.

This one setting cannot go in the project file (Claude Code ignores it there, so
that a downloaded project cannot change it). It goes in your personal settings
file, which applies to all your projects:

- Mac and Linux: `~/.claude/settings.json`
- Create the file if it does not exist.

```json
{
  "sandbox": {
    "network": {
      "strictAllowlist": true
    }
  }
}
```

With this on, only sites listed under `allowedDomains` in
`.claude/settings.json` can be reached by commands. You will need to add sites
there yourself (Recipe 2). Requires a recent version of Claude Code.

---

## What the sandbox does not do

- It fences **commands**. Claude's built-in file tools (read, edit, search) are
  governed by the permission rules instead. This template sets both, so the
  result is the same, but it is why both halves of `settings.json` matter.
- It does not inspect the *contents* of traffic to a site you have approved. If
  you approve a site, data can be sent to it. Approving a very broad site such as
  `github.com` is a bigger opening than approving a narrow one.
- It does not cover commands **you** type using the `!` prefix.
- It is not a separate computer. For work with files or code you actively
  distrust, run Claude Code inside a virtual machine or a container, so that
  even a complete failure of the fence exposes nothing of yours. Anthropic
  documents these options at <https://code.claude.com/docs/en/sandbox-environments>.

Official reference for everything on this page:
<https://code.claude.com/docs/en/sandboxing>
