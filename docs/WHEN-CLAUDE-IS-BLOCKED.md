# When Claude says it cannot do something

Most of the time this is the protection working, not a fault. This page helps you tell
the difference in about thirty seconds, without needing to understand the settings files.

Find the line that sounds like what you are seeing.

---

## "I am not permitted to read that" / "that folder is denied"

**Which folder was it?**

| Folder | Verdict |
| :----- | :------ |
| `private/` | **Correct.** Claude can never read or change anything here. This is the whole point |
| `reference/` | **Correct** if Claude was trying to *change* something. It is allowed to read |
| `.claude/` or `CLAUDE.md` | **Correct.** Claude cannot rewrite its own rules |
| A `.env` file, or anything ending `.key`, `.pem`, `.p12`, `.pfx` | **Correct.** These are where passwords and keys live |
| `workspace/` | **Not expected.** See [Troubleshooting](../README.md#troubleshooting) |

**What to do:** nothing, in the first four cases. If Claude needs something that lives in
`private/`, tell it the one specific non-secret detail it needs. Do not move the file
out, and do not paste a password into the chat.

---

## "Operation not permitted" from a command

The operating-system sandbox stopped a command. Ask one question: **was the command
reaching outside this project?**

- **Reaching into your home folder** (Documents, Desktop, Downloads, another project,
  a settings file): correct. That is the fence doing its job.
- **Reaching into `private/` or `reference/`**: correct.
- **Working inside this project and still failing:** something is wrong. Usually
  `.claude/settings.local.json` is missing. Close and reopen Claude Code once; a script
  recreates it. Still failing? See
  ["Commands cannot read the project at all"](SETTINGS-EXPLAINED.md#commands-cannot-read-the-project-at-all).

---

## "A command wants to access example.com"

Commands cannot reach any website until you approve it. You are being asked because this
is the first time.

**Approve it if** you recognise the site and it fits what you asked for. Installing
Python packages really does need `pypi.org`. Searching for papers really does need
`eutils.ncbi.nlm.nih.gov`.

**Do not approve it if** the site has nothing to do with your request, or you have never
heard of it. Say no and ask Claude why it wants that site.

**Remember:** approving a site means data can be *sent* there as well as fetched. Choose
"don't ask again" only for sites you will use constantly.

---

## "A tool cannot be found" or "python: not permitted"

The tool is installed inside your home folder, which commands cannot reach. This is a
real limitation, not a mistake. The fix is to re-open just that one tool's folder:
[Recipe 3](SETTINGS-EXPLAINED.md#recipe-3-a-tool-installed-in-your-home-folder-will-not-run).

---

## Claude says a website refused it

Some websites block automated access, or need a subscription. This is the website's
decision, not your settings.

**This is where to be careful.** Claude is told never to work around a refusal: not to
disguise itself as a browser, not to look for a mirror that serves the same content
without the control, and never to use a pirate site. If Claude ever offers to do
something along those lines, say no.

The right outcome is that Claude tells you what it could not get and hands you a link.
You can usually open it in one click, especially with a university login.

---

## Claude asks before deleting, pushing, or starting git

`rm`, `git push`, `git reset --hard`, `git clean` and `git init` always stop and ask.
Read what the command will do before saying yes. Deleting and publishing are the two
things that are hardest to undo.

The real protection against losing work is committing to git often. Type `/save-work`.

---

## Something that should be blocked was **not** blocked

This is the one that matters. In particular:

- Claude read `private/TEST-SECRET.txt`
- Claude changed a file in `reference/`
- A command listed your home folder
- **Claude told you a sentence about a giraffe**

**Stop using the project for real work** and go to
[Troubleshooting](../README.md#troubleshooting). The usual cause is a typing mistake in
`.claude/settings.json`: one missing comma makes Claude Code ignore the whole file, with
no warning, and every protection switches off at once.

Type `/doctor` to check the settings files, then `/test-setup` to re-run all six tests.

---

## None of the above

Tell Claude plainly what you expected and what happened instead, and ask it to explain
which rule stopped it. It can read the settings files even though it cannot change them,
so it can usually point at the exact line.

If you think a rule genuinely needs changing,
[SETTINGS-EXPLAINED.md](SETTINGS-EXPLAINED.md) has copy-and-paste recipes for the common
cases. Change the files yourself, restart Claude Code, then run `/test-setup` and add the
result to [SECURITY-CHECKS.md](../SECURITY-CHECKS.md).
