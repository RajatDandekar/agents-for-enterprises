"""A transparent stdio relay that records the raw MCP JSON-RPC between a host and our server.

    python stdio_tee.py --log wire.jsonl -- <python> -m ledgerline.toolbox.mcp --user ECLARKE --tools check_stock

The host (Claude Code, or mcp_raw.py) starts this instead of the server. Every line the host writes to the server
(">") and every line the server writes back ("<") is passed through unchanged and appended to the log with a
timestamp. Nothing is parsed or rewritten, so the log is exactly what went over the pipe.
"""
import json
import subprocess
import sys
import threading
import time

argv = sys.argv[1:]
log = argv[argv.index("--log") + 1]
cmd = argv[argv.index("--") + 1:]
t0 = time.time()
lock = threading.Lock()
child = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


def rec(direction, line: bytes):
    with lock, open(log, "a") as f:
        f.write(json.dumps({"t": round(time.time() - t0, 4), "dir": direction,
                            "line": line.decode("utf-8", "replace").rstrip("\n")}) + "\n")


def down():  # host -> server
    for line in sys.stdin.buffer:
        rec(">", line)
        child.stdin.write(line)
        child.stdin.flush()
    child.stdin.close()


threading.Thread(target=down, daemon=True).start()
for line in child.stdout:  # server -> host
    rec("<", line)
    sys.stdout.buffer.write(line)
    sys.stdout.buffer.flush()
child.wait()
