import os
import subprocess


def _ensure_dbus_env():
    if "DBUS_SESSION_BUS_ADDRESS" not in os.environ:
        runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
        if runtime_dir:
            os.environ["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={runtime_dir}/bus"


def send_notification(summary, body=""):
    """Send a desktop notification. Non-blocking, fire-and-forget."""
    _ensure_dbus_env()
    args = ["notify-send", summary]
    if body:
        args.append(body)
    try:
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
