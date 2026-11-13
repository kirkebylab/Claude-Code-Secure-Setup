#!/bin/sh
# First-run setup for this template.
#
# Claude Code runs this script automatically at the start of every session
# (see "hooks" in .claude/settings.json). It does one thing: if the personal
# settings file .claude/settings.local.json is missing, it creates it.
#
# Why: that file re-opens this project inside your blocked home folder, so the
# commands Claude runs can read the project. Git never carries the file, so a
# fresh copy of the template from GitHub arrives without it.
#
# If the file already exists, the script leaves it alone and prints nothing.
#
# The file's contents are written out below rather than copied from somewhere
# else, and this script lives in .claude/, which Claude cannot change. So only
# you can change what gets created.
#
# To run it by hand (for example if the automatic run did not happen), open a
# terminal in the project folder and type:  sh .claude/hooks/first-run-setup.sh

set -eu

project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
target="$project_dir/.claude/settings.local.json"

# Already there (or a link to somewhere else)? Do nothing.
if [ -e "$target" ] || [ -L "$target" ]; then
  exit 0
fi

# Refuse to run from the wrong folder.
if [ ! -f "$project_dir/.claude/settings.json" ]; then
  echo "first-run-setup: cannot find .claude/settings.json in $project_dir" >&2
  exit 1
fi

# set -C: fail rather than overwrite if the file appears in the meantime.
set -C
cat > "$target" <<'EOF'
{
  "sandbox": {
    "excludedCommands": ["git init"],
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
EOF
set +C

# Tell you (systemMessage) and Claude (additionalContext) what just happened.
cat <<'EOF'
{"systemMessage": "First-run setup: created .claude/settings.local.json so Claude can work in this project. If Claude's commands fail with \"Operation not permitted\", close and reopen Claude Code once.", "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "The first-run setup script has just created .claude/settings.local.json, which re-opens this project for sandboxed commands. If a command fails with \"Operation not permitted\" on this project folder during this session, the new file has probably not been picked up yet: tell the user to close and reopen Claude Code once, then try again. Do not look for a workaround."}}
EOF
