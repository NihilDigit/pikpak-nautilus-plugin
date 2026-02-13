#!/usr/bin/env python3
import subprocess
import sys
import time
from pathlib import Path
import fcntl

try:
    from .notify import send_notification
except ImportError:
    from notify import send_notification


def main(timeout_seconds=5):
    state_dir = Path("/tmp/pikpak_refresh")
    state_dir.mkdir(parents=True, exist_ok=True)
    last_req = state_dir / "last_req"
    lock_file = state_dir / "lock"

    try:
        lock_fd = lock_file.open("w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return 0

    try:
        while True:
            try:
                last = int(last_req.read_text().strip() or "0")
            except Exception:
                last = 0
            now = int(time.time())
            if now - last >= timeout_seconds:
                result = subprocess.run(
                    ["bash", "-c", "rclone rc vfs/forget && rclone rc vfs/refresh recursive=true asynchronous=true"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    send_notification("Rclone", "Cache refreshed.")
                else:
                    error = result.stderr or "Refresh failed"
                    send_notification("Rclone Error", error[:100])
                break
            time.sleep(2)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()

    return 0


if __name__ == "__main__":
    try:
        timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    except Exception:
        timeout = 5
    raise SystemExit(main(timeout))
