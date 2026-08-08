#!/bin/bash
# Retry loop for the two signal-only variants.
#
# The private H+c NanoAOD lives on maite.iihe.ac.be (per-era redirector for postEE) and
# xrootd reads there time out intermittently: "XRootD error: [ERROR] Operation expired".
# Transient -> resubmit the whole (small, 6-job) variant until all 7 partition dirs
# exist on EOS, up to MAX_TRIES.
#
# NOTE: wait on the CLUSTER ID from the submit output. `condor_q -nobatch | grep <wf>`
# does NOT work -- the queue listing shows the executable, not the workflow name, so it
# matches nothing and we would resubmit on top of jobs still waiting for a slot.
set -u
export X509_USER_PROXY=/afs/cern.ch/user/c/cgupta/private/x509up_u151861
cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
MM=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
LOG=/tmp/cjet_study
MAX_TRIES=8

npart() { ls -d /eos/user/c/cgupta/higgscharm/outputs/$1/2022postEE/HplusCharm_HtoWW* 2>/dev/null | wc -l; }

wait_cluster() {  # $1 = cluster id; block until it leaves the queue
  local c=$1
  [ -z "$c" ] && { sleep 300; return; }
  while [ "$(condor_q "$c" -af ProcId 2>/dev/null | wc -l)" -gt 0 ]; do sleep 120; done
}

for wf in hww_2dcat_nocjet hww_2dcat_looseWP; do
  for try in $(seq 1 $MAX_TRIES); do
    n=$(npart $wf)
    echo "$(date '+%F %T') $wf try=$try partitions=$n/7" | tee -a $LOG/retry.log
    [ "$n" -ge 7 ] && { echo "$wf COMPLETE" | tee -a $LOG/retry.log; break; }
    # if a previous attempt's cluster is still queued, wait for it before resubmitting
    last=$(grep -oE "submitted to cluster [0-9]+" $LOG/retry_$wf.log 2>/dev/null | tail -1 | grep -oE "[0-9]+")
    [ -n "$last" ] && { echo "  waiting on cluster $last" | tee -a $LOG/retry.log; wait_cluster "$last"; }
    n=$(npart $wf)
    [ "$n" -ge 7 ] && { echo "$wf COMPLETE" | tee -a $LOG/retry.log; break; }
    echo "$(date '+%F %T') resubmitting $wf ($n/7)" | tee -a $LOG/retry.log
    timeout 3600 $MM run -n b_hive python3 runner.py --workflow "$wf" \
        --year 2022postEE --submit --eos --output_format parquet \
        >> $LOG/retry_$wf.log 2>&1
    sleep 60
  done
done
echo "$(date '+%F %T') RETRY_DONE nocjet=$(npart hww_2dcat_nocjet)/7 looseWP=$(npart hww_2dcat_looseWP)/7" | tee -a $LOG/retry.log
