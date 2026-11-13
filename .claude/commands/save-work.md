---
description: Save (commit) my work with git, after checking for passwords and keys
disable-model-invocation: true
---
Please save my work with git.

1. If this folder is not a git repository yet, tell me, and ask me before you run `git init` (exactly that, with nothing added).
2. If nothing has changed since the last save, just say so and stop.
3. Show me, in plain language, which files have changed and what changed in each.
4. Check the changes for anything that looks like a password, API key, or token. If you find one, stop and tell me which file it is in. Do not save.
5. Save (commit) the changes with a short message that says what changed and why. Never use `git add -f` or `--force`: some files are deliberately kept out of git, such as everything in private/.
6. Do not upload (push) anything.
7. Tell me in one or two sentences what you saved, and how I could undo it if I change my mind.
