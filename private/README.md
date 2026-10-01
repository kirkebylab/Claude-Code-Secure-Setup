# private/ — Claude has NO access to this folder

Claude cannot read, search, list, create, edit, or delete anything in here.

Use it for files that need to sit alongside your project but that Claude should
never see. For example:

- Passwords, API keys, and login details
- Client or customer information
- Financial or legal documents
- Personal notes

| Claude can read files here | Claude can create, edit, or delete files here |
| :------------------------: | :-------------------------------------------: |
|           **No**           |                     **No**                    |

How it is enforced:

- Claude's file tools are blocked by deny rules in `.claude/settings.json`.
- Commands Claude runs are blocked by the sandbox (your operating system
  enforces this, so it holds even if a command tries to be sneaky).

Good to know:

- Everything in this folder except this README and `TEST-SECRET.txt` is ignored
  by git, so it will not be uploaded if you publish the project to GitHub.
- `TEST-SECRET.txt` is a harmless test file. The main README shows how to use it
  to check that the protection is really working. Keep it.
- This protects files from **Claude Code in this project**. It does not encrypt
  them or hide them from other apps or people using your computer.
- Since Claude cannot read this README, it will not know what is in here. That is
  the point.
