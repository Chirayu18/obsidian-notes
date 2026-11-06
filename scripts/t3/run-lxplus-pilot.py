#!/usr/bin/env python3
"""Run the staged SSH-only pilot in the foreground for at most 30 minutes."""

import shlex
import subprocess


REMOTE = r'''
import datetime,json,os,pathlib,signal,socket,subprocess,time,urllib.request
data=json.loads(pathlib.Path('/afs/cern.ch/user/c/cgupta/private/t3-account-setup.json').read_text())
if socket.getfqdn()!=data['pilot_host']:
    raise SystemExit('SSH reached another node. Restage the pilot before starting it.')
root=pathlib.Path(data['pilot_root'])
os.umask(0o077)
check=socket.socket();check.bind(('127.0.0.1',3783));check.close()
env=os.environ.copy()
env['T3CODE_HOME']=str(root/'state')
env['T3CODE_CLI_PATH']=str(root/'runtime/t3')
env['LD_LIBRARY_PATH']=str(root/'runtime/lib')
env['PATH']=str(root/'runtime')+':'+str(pathlib.Path.home()/'.local/bin')+':'+env.get('PATH','/usr/bin:/bin')
env['OTEL_SDK_DISABLED']='true'
log=(root/'server.log').open('a')
args=[str(root/'runtime/t3'),'serve','--host','127.0.0.1','--port','3783','--base-dir',str(root/'state'),str(root/'workspace')]
p=subprocess.Popen(args,cwd=str(root/'workspace'),env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log)
metadata={'supervisor_pid':os.getpid(),'server_pid':p.pid,'host':socket.getfqdn(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'maximum_seconds':1800}
(root/'process.json').write_text(json.dumps(metadata))
def stop(signum,frame):raise KeyboardInterrupt
for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,stop)
try:
    for attempt in range(60):
        if p.poll() is not None:raise SystemExit('Server exited; private server.log retained')
        try:
            with urllib.request.urlopen('http://127.0.0.1:3783/.well-known/t3/environment',timeout=1) as response:d=json.load(response)
            print(json.dumps({'ready':True,'process':metadata,'environmentId':d['environmentId'],'serverVersion':d['serverVersion']}),flush=True)
            break
        except Exception:time.sleep(0.5)
    else:raise SystemExit('Server startup timed out; private server.log retained')
    deadline=time.monotonic()+1800
    while p.poll() is None and time.monotonic()<deadline:time.sleep(1)
except KeyboardInterrupt:pass
finally:
    if p.poll() is None:
        p.terminate()
        try:p.wait(timeout=15)
        except subprocess.TimeoutExpired:p.kill();p.wait()
    log.close()
    print(json.dumps({'pilot_server_stopped':True,'returncode':p.returncode}),flush=True)
'''


if __name__ == "__main__":
    command = ["ssh", "-S", "/home/cgupta/.ssh/cm-cgupta@lxplus.cern.ch:22"]
    for option in ["ControlMaster=no", "ControlPersist=no", "BatchMode=yes", "PreferredAuthentications=none", "GSSAPIAuthentication=no", "PubkeyAuthentication=no", "PasswordAuthentication=no", "KbdInteractiveAuthentication=no", "StrictHostKeyChecking=yes", "UpdateHostKeys=no", "ExitOnForwardFailure=yes"]:
        command += ["-o", option]
    command += ["-L", "127.0.0.1:3783:127.0.0.1:3783", "lxplus", "python3 -c " + shlex.quote(REMOTE)]
    raise SystemExit(subprocess.run(command).returncode)
