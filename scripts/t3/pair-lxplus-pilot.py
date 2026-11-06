#!/usr/bin/env python3
"""Print a pilot pairing code only in the user's own terminal; --check mints none."""

import argparse
import shlex
import subprocess


REMOTE = r'''
import json, os, pathlib, socket, sys, urllib.request
manifest = pathlib.Path('/afs/cern.ch/user/c/cgupta/private/t3-account-setup.json')
data = json.loads(manifest.read_text())
if socket.getfqdn() != data['pilot_host']:
    raise SystemExit('SSH reached another node. Ask the setup thread to restore the pilot there.')
root = pathlib.Path(data['pilot_root'])
with urllib.request.urlopen('http://127.0.0.1:3783/.well-known/t3/environment', timeout=5) as response:
    descriptor = json.load(response)
if sys.argv[1] == 'check':
    print(json.dumps({'host':socket.getfqdn(), 'environmentId':descriptor['environmentId'], 'serverVersion':descriptor['serverVersion']}))
else:
    env = os.environ.copy()
    env['T3CODE_HOME'] = str(root/'state')
    env['LD_LIBRARY_PATH'] = str(root/'runtime/lib')
    binary = str(root/'runtime/t3')
    args = [binary, 'pair', '--base-dir', str(root/'state'), '--label', 'laptop-pilot', '--ttl', '10m']
    for scope in ['orchestration:read','orchestration:operate','providers:manage','terminal:read','terminal:operate','filesystem:read','filesystem:write','diagnostics:read','access:read']:
        args += ['--scope', scope]
    os.execve(binary, args, env)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    command = ["ssh", "-S", "/home/cgupta/.ssh/cm-cgupta@lxplus.cern.ch:22"]
    for option in ["ControlMaster=no", "ControlPersist=no", "BatchMode=yes", "PreferredAuthentications=none", "GSSAPIAuthentication=no", "PubkeyAuthentication=no", "PasswordAuthentication=no", "KbdInteractiveAuthentication=no", "StrictHostKeyChecking=yes", "UpdateHostKeys=no"]:
        command += ["-o", option]
    remote = "python3 -c " + shlex.quote(REMOTE) + " " + ("check" if args.check else "pair")
    raise SystemExit(subprocess.run(command + ["lxplus", remote]).returncode)


if __name__ == "__main__":
    main()
