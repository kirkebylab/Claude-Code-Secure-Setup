#!/bin/sh
# Record the mechanical facts of a working session into workspace/ai-use-log/.
#
# WHAT THIS CAPTURES
#   The things a machine can know for certain: the date, which git commits were made,
#   which files changed, and how much. It does NOT describe what was asked or why
#   anything was done. Claude writes that part; see docs/AI-USE-LOG.md.
#
# HOW IT RUNS
#   Claude Code calls it automatically at the end of a session, if you have added the
#   SessionEnd hook described in docs/AI-USE-LOG.md. You can also run it by hand:
#
#       sh log-session.sh
#
# SAFETY
#   It only ever appends to workspace/ai-use-log/. It never fails a session: any
#   problem is reported and the script still exits 0, because a logging glitch must
#   not interrupt your work.

set -u

project_dir="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")" && pwd)}"
cd "$project_dir" 2>/dev/null || exit 0

log_dir="workspace/ai-use-log"
sessions_dir="$log_dir/sessions"
state_file="$log_dir/.last-logged-commit"

[ -d workspace ] || exit 0
mkdir -p "$sessions_dir" 2>/dev/null || exit 0

# No git repository yet means nothing mechanical to record.
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  exit 0
fi

today=$(date +%Y-%m-%d)
head_commit=$(git rev-parse --short HEAD 2>/dev/null) || exit 0
last_logged=""
[ -f "$state_file" ] && last_logged=$(cat "$state_file" 2>/dev/null)

if [ "$head_commit" = "$last_logged" ]; then
  # Nothing new has been committed since the last time this ran.
  exit 0
fi

if [ -n "$last_logged" ] && git cat-file -e "$last_logged" 2>/dev/null; then
  range="$last_logged..HEAD"
else
  range="HEAD"
fi

commit_count=$(git log --oneline "$range" 2>/dev/null | wc -l | tr -d ' ')
[ "${commit_count:-0}" -eq 0 ] && exit 0

target="$sessions_dir/$today-auto.md"

# Decide this before the redirection below, which creates the file.
needs_header=yes
[ -f "$target" ] && needs_header=no

{
  if [ "$needs_header" = yes ]; then
    printf '# %s — automatic record\n\n' "$today"
    printf '> Written by `log-session.sh`, not by Claude. These are the mechanical\n'
    printf '> facts only: what was committed and which files changed. For what was\n'
    printf '> asked and why, see the companion record Claude writes for the same date.\n\n'
  fi
  printf '## Commits recorded at %s\n\n' "$(date +%H:%M)"
  printf '| Commit | Subject |\n| :----- | :------ |\n'
  git log --format='| `%h` | %s |' "$range" 2>/dev/null
  file_list=$(git log --name-only --format='' "$range" 2>/dev/null \
              | grep -v '^$' | sort -u)
  file_count=$(printf '%s\n' "$file_list" | grep -c . 2>/dev/null || echo 0)
  printf '\n%s file(s) touched by these commits:\n\n```\n' "$file_count"
  printf '%s\n' "$file_list" | head -60
  [ "$file_count" -gt 60 ] && printf '... and %s more\n' "$((file_count - 60))"
  printf '```\n\n'
} >> "$target" 2>/dev/null || exit 0

echo "$head_commit" > "$state_file" 2>/dev/null
echo "ai-use-log: recorded $commit_count commit(s) in $target"
exit 0
