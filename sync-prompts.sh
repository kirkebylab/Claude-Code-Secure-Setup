#!/bin/sh
# Copy each prompt in prompts/ into its slash command in .claude/commands/.
#
# WHY THIS EXISTS
# Editing a file in prompts/ does not change its slash command. The command is a
# separate copy in .claude/commands/, and Claude is not allowed to write there, so
# the two drift apart the moment a prompt is improved. This script re-copies them.
#
# It keeps the few lines at the top of each command file (the "frontmatter" between
# --- markers) which give the command its description in the / menu. Only the body
# is replaced.
#
# RUN IT YOURSELF, in a terminal opened in this project folder:
#
#     sh sync-prompts.sh
#
# Claude cannot run it for you: the sandbox blocks writes to .claude/, which is
# deliberate. Running it is how you approve the change.
#
# Afterwards, restart Claude Code so it picks up the new command text.

set -eu

cd "$(dirname "$0")"

if [ ! -d prompts ] || [ ! -d .claude/commands ]; then
  echo "sync-prompts: run this from the project folder (the one with prompts/ in it)" >&2
  exit 1
fi

changed=0
unchanged=0
created=0
no_frontmatter=""

for prompt in prompts/*.md; do
  name=$(basename "$prompt")
  [ "$name" = "README.md" ] && continue
  command_file=".claude/commands/$name"

  # Pull the frontmatter off the existing command, if it has any.
  frontmatter=""
  if [ -f "$command_file" ]; then
    first_line=$(head -n 1 "$command_file")
    if [ "$first_line" = "---" ]; then
      frontmatter=$(awk 'NR==1 && $0=="---" {print; next}
                         /^---$/ && !done {print; done=1; next}
                         !done {print}' "$command_file")
    else
      no_frontmatter="$no_frontmatter ${name%.md}"
    fi
  fi

  # Build beside the target so the final move is atomic and stays on one filesystem.
  tmp="$command_file.sync-tmp"
  trap 'rm -f "$tmp"' EXIT INT TERM
  : > "$tmp"
  if [ -n "$frontmatter" ]; then
    printf '%s\n' "$frontmatter" > "$tmp"
  fi
  cat "$prompt" >> "$tmp"

  if [ ! -f "$command_file" ]; then
    mv "$tmp" "$command_file"
    echo "created  /${name%.md}"
    created=$((created + 1))
  elif cmp -s "$tmp" "$command_file"; then
    rm -f "$tmp"
    unchanged=$((unchanged + 1))
  else
    mv "$tmp" "$command_file"
    echo "updated  /${name%.md}"
    changed=$((changed + 1))
  fi
done

echo
echo "$changed updated, $created created, $unchanged already current."

if [ -n "$no_frontmatter" ]; then
  echo
  echo "WARNING: these commands have no frontmatter:$no_frontmatter"
  echo
  echo "Without it a command has no description in the / menu, and loses"
  echo "'disable-model-invocation: true', which means Claude may run it on its own"
  echo "initiative rather than only when you type it. That usually happens when a"
  echo "prompt is copied over a command by hand."
  echo
  echo "To fix, open each file listed above in .claude/commands/ and put these lines"
  echo "at the very top:"
  echo
  echo "  ---"
  echo "  description: One line saying what the command does"
  echo "  disable-model-invocation: true"
  echo "  ---"
fi
if [ "$changed" -gt 0 ] || [ "$created" -gt 0 ]; then
  echo
  echo "Restart Claude Code so the new command text is loaded."
  if [ "$created" -gt 0 ]; then
    echo "A newly created command has no description in the / menu. To add one, open"
    echo ".claude/commands/<name>.md and put these three lines at the very top:"
    echo
    echo "  ---"
    echo "  description: One line saying what the command does"
    echo "  disable-model-invocation: true"
    echo "  ---"
  fi
fi
