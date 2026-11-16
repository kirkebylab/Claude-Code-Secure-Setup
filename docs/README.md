# docs/ — the guides

Four documents. Which one you want depends on what you are trying to do.

| If you want to... | Read |
| :---------------- | :--- |
| Work out why Claude says it cannot do something | [WHEN-CLAUDE-IS-BLOCKED.md](WHEN-CLAUDE-IS-BLOCKED.md) |
| Record how AI was used, for a paper or for your own notes | [AI-USE-LOG.md](AI-USE-LOG.md) |
| Set up or understand the sandbox | [SANDBOX-SETUP.md](SANDBOX-SETUP.md) |
| Change a rule, or understand a setting | [SETTINGS-EXPLAINED.md](SETTINGS-EXPLAINED.md) |
| See what the first-run script creates | [settings.local.example.json](settings.local.example.json) |

## Start here if you are new

Read the [main README](../README.md) first, then run the six tests. Nothing else in
this folder matters until those pass.

## The short version

Two separate locks protect you, and they cover each other's gaps:

1. **Permission rules** in `.claude/settings.json` check every action Claude's own
   tools take, before they happen.
2. **The sandbox** is a fence your operating system builds around every command
   Claude runs, enforced by the operating system rather than by Claude behaving well.

A rule change that **restricts** Claude goes in `.claude/settings.json`. A change that
**opens access up** goes in `.claude/settings.local.json`, your personal file that git
never carries. [SETTINGS-EXPLAINED.md](SETTINGS-EXPLAINED.md) explains why, and has
copy-and-paste recipes.

**After any change:** restart Claude Code, type `/doctor`, then run `/test-setup` and
let it add the result to [SECURITY-CHECKS.md](../SECURITY-CHECKS.md). One missing comma
in a settings file makes Claude Code ignore the whole file silently, and the tests are
how you catch that.

## Related files outside this folder

| File | What it is |
| :--- | :--------- |
| [../SECURITY-CHECKS.md](../SECURITY-CHECKS.md) | Dated log of every time the six tests were run |
| [../CLAUDE.md](../CLAUDE.md) | The instructions Claude reads at the start of every session |
| [../prompts/README.md](../prompts/README.md) | The ready-made prompts and slash commands |
| [../tools/README.md](../tools/README.md) | Command-line tools for verifying and fetching papers |
