#!/usr/bin/env python3
"""Human-run OAuth recovery for cswap slot 2; keep tokens out of chat and Git."""

import argparse
import json
import os
from pathlib import Path
import subprocess


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify prerequisites without starting login.")
    args = parser.parse_args(argv)
    home = Path.home()
    claude = home / ".local/bin/claude"
    cswap = home / ".local/bin/cswap"
    xdg = os.environ.get("XDG_DATA_HOME", "")
    data_home = Path(os.path.expanduser(xdg)) if xdg else home / ".local/share"
    if not data_home.is_absolute():
        data_home = home / ".local/share"
    sequence = json.loads((data_home / "claude-swap/sequence.json").read_text())
    original_slot = sequence.get("activeAccountNumber")
    account2 = sequence.get("accounts", {}).get("2")
    if original_slot is None or not account2 or str(original_slot) == "2":
        raise SystemExit("Account layout changed. Ask the setup thread to re-check first.")
    if os.environ.get("CLAUDE_CONFIG_DIR"):
        raise SystemExit("Run in a normal laptop terminal without CLAUDE_CONFIG_DIR set.")
    status = subprocess.run([str(claude), "auth", "status"], capture_output=True, text=True)
    identity = json.loads(status.stdout) if status.returncode == 0 else {}
    expected_active = sequence["accounts"][str(original_slot)]["email"]
    if not identity.get("loggedIn") or identity.get("email") != expected_active:
        raise SystemExit("Default Claude login changed. No account was modified.")
    if args.check:
        print(f"Ready: current cswap slot {original_slot} is authenticated; recovery targets slot 2. No login attempted.")
        return
    print("Use this while Claude turns are idle. Sign in as cswap account 2.", flush=True)
    print("Keep authorization URLs/codes in this terminal and your browser.", flush=True)
    try:
        login = subprocess.run([str(claude), "auth", "login"])
        if login.returncode:
            raise RuntimeError("Login did not complete; account 2's stored slot was left unchanged.")
        status = subprocess.run([str(claude), "auth", "status"], capture_output=True, text=True)
        identity = json.loads(status.stdout) if status.returncode == 0 else {}
        if not identity.get("loggedIn") or identity.get("email") != account2["email"]:
            raise RuntimeError("The selected login is not cswap account 2; its stored slot was left unchanged.")
        legacy = home / ".claude/.config.json"
        global_config = legacy if legacy.is_file() and legacy.stat().st_size else home / ".claude.json"
        oauth = json.loads(global_config.read_text()).get("oauthAccount", {})
        for stored_key, live_key in [("uuid", "accountUuid"), ("organizationUuid", "organizationUuid")]:
            if account2.get(stored_key) and oauth.get(live_key) != account2[stored_key]:
                raise RuntimeError("Account/workspace identity did not match slot 2; its stored slot was left unchanged.")
        subprocess.run([str(cswap), "add", "--slot", "2"], check=True)
    finally:
        # Use cswap's own locks and credential handling, never copy auth files.
        restore = subprocess.run([str(cswap), "switch", str(original_slot)])
        if restore.returncode:
            raise RuntimeError("Restoring the original account needs attention; no further action was attempted.")
    print("Recovery flow finished. Ask the setup thread to verify account 2's status.")


if __name__ == "__main__":
    main()
