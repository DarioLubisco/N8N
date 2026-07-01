---
name: launch-cursor
description: Launches the Cursor IDE AppImage in the background.
---

# Launch Cursor IDE

This skill runs the Cursor AppImage located at `/home/synapse/Downloads/Cursor.AppImage` in the background, fully detached.

## Instructions
1. Use the `run_command` tool to execute:
   `nohup /home/synapse/Downloads/Cursor.AppImage > /dev/null 2>&1 &`
2. Wait 500ms before async to ensure it detaches properly.
3. If credentials are ever required for similar GUI tasks, rely on the system's GUI polkit prompts (e.g., `pkexec`) so the user can enter their password directly in the UI instead of the chat.

## Constraints
- Do NOT ask for the user's system password in the chat.
- Always use `nohup` and background the process (`&`) so it doesn't block the agent.
