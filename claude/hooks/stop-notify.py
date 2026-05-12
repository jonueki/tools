import sys
import json
import subprocess

d = json.load(sys.stdin)
cwd = d.get("cwd", "")
project = cwd.split("/")[-1] if cwd else "Claude Code"
transcript = d.get("transcript_path", "")

last_msg = "Task complete"
if transcript:
    try:
        with open(transcript) as f:
            lines = f.readlines()
        for line in reversed(lines):
            obj = json.loads(line)
            if obj.get("type") == "assistant":
                for block in reversed(obj.get("message", {}).get("content", [])):
                    if block.get("type") == "text" and block.get("text", "").strip():
                        last_msg = block["text"].strip().split("\n")[0][:80]
                        break
                else:
                    continue
                break
    except Exception:
        pass

subprocess.run([
    "terminal-notifier",
    "-title", project,
    "-message", "Task complete",
    "-subtitle", last_msg,
    "-sound", "Glass"
])
