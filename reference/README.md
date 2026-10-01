# reference/ — Claude can read, but can NEVER change files here

Put things here that Claude should look at but must not touch. For example:

- A contract, brief, or spec you want Claude to follow
- Original data files you don't want accidentally altered
- Example code or documents to copy the style of
- Brand guidelines, notes, research

| Claude can read files here | Claude can create, edit, or delete files here |
| :------------------------: | :-------------------------------------------: |
|             Yes            |                     **No**                    |

How it is enforced:

- Claude's editing tools are blocked from this folder by a deny rule in
  `.claude/settings.json`.
- Commands Claude runs are blocked from writing here by the sandbox (your
  operating system enforces this).

Only you can add, change, or remove files in this folder. Do it the normal way,
using Finder / File Explorer or your editor.

Remember: anything in this folder can be read by Claude, which means its
contents may be sent to Anthropic as part of your conversation. If a file is
truly confidential, it belongs in `private/` instead.
