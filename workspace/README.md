# workspace/ — Claude can read AND change files here

This is where your actual project lives. Put your code, documents, and anything
else you want Claude to work on in this folder.

| Claude can read files here | Claude can create, edit, and delete files here |
| :------------------------: | :--------------------------------------------: |
|             Yes            |                       Yes                      |

Tips:

- Claude still asks before it edits a file with its editing tools, so you get a
  chance to say no.
- Commands Claude runs (for example, a script that generates files) can change
  things in this folder without asking first. They are fenced in by the sandbox,
  so they cannot reach outside this project.
- Deleting with `rm` always asks you first.
- Save your progress often with git (or just ask Claude: "commit my work"). That
  way any change can be undone.

You can delete this README once you know how the folder works.
