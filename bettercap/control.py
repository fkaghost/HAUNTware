# bettercap/control.py
import subprocess
import time
import requests

BETTERCAP_API = "http://127.0.0.1:8081/api"

_proc = None


def start_bettercap():
    """
    Start bettercap with the http-ui caplet.
    Returns True if the API becomes reachable, False otherwise.

    NOTE: This calls 'sudo bettercap', so either:
      - run HAUNTware with sudo, OR
      - configure passwordless sudo for bettercap.
    """
    global _proc

    if _proc is not None and _proc.poll() is None:
        return True  # already running

    _proc = subprocess.Popen(
        ["sudo", "bettercap", "-caplet", "http-ui"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for the API to come online
    for _ in range(40):
        try:
            r = requests.get(f"{BETTERCAP_API}/session", timeout=0.5)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.5)

    return False


def stop_bettercap():
    """Stop bettercap if it was started by this module."""
    global _proc

    if _proc is None:
        return

    try:
        _proc.terminate()
        _proc.wait(timeout=5)
    except Exception:
        try:
            _proc.kill()
        except Exception:
            pass
    finally:
        _proc = None


def bettercap_is_running():
    """Return True if our bettercap process is still alive."""
    return _proc is not None and _proc.poll() is None
