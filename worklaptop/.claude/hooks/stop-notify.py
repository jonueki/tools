import sys
import json
import subprocess
import time

d = json.load(sys.stdin)
cwd = d.get("cwd", "")
project = cwd.split("/")[-1] if cwd else "Claude Code"
transcript = d.get("transcript_path", "")


def latest_assistant_text():
    """Return the latest assistant text from the transcript, or None.

    Scopes to text emitted after the most recent real user message so we
    don't surface text from a previous turn.
    """
    try:
        with open(transcript) as f:
            lines = [json.loads(l) for l in f if l.strip()]
    except Exception:
        return None

    start = 0
    for i in range(len(lines) - 1, -1, -1):
        obj = lines[i]
        if obj.get("type") != "user":
            continue
        content = obj.get("message", {}).get("content", "")
        if isinstance(content, str):
            start = i + 1
            break
        if isinstance(content, list) and not any(
            b.get("type") == "tool_result" for b in content
        ):
            start = i + 1
            break

    latest = None
    for obj in lines[start:]:
        if obj.get("type") != "assistant":
            continue
        for block in obj.get("message", {}).get("content", []):
            if block.get("type") == "text" and block.get("text", "").strip():
                latest = block["text"].strip()
    return latest


last_msg = None
if transcript:
    # The Stop hook can fire before the final assistant message is flushed
    # to the transcript. Poll briefly for new text to appear.
    deadline = time.time() + 3.0
    while True:
        last_msg = latest_assistant_text()
        if last_msg or time.time() >= deadline:
            break
        time.sleep(0.1)

if not last_msg:
    last_msg = "Task complete"

display = last_msg.split("\n")[0][:80]
safe_msg = display.replace("\\", "\\\\").replace('"', '\\"')
safe_project = project.replace("\\", "\\\\").replace('"', '\\"')

subprocess.run([
    "osascript", "-e",
    f'display notification "{safe_msg}" with title "{safe_project}" subtitle "Task complete" sound name "Glass"'
])
