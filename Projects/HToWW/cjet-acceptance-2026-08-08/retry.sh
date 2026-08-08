#!/bin/bash
# Retry loop for the two signal-only variants.
#
# The private H+c NanoAOD lives on maite.iihe.ac.be (per-era redirector for postEE) and
# xrootd reads there time out intermittently: "XRootD error: [ERROR] Operation expired".
# This is transient, so just resubmit the whole (small, 6-job) variant until every
# partition dir 0..6 exists on EOS, up to MAX_TRIES.
set -u
export X509_USER_PROXY=/afs/cern.ch/user/c/cgupta/private/x509up_u151861
cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
MM=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
LOG=/tmp/cjet_study
MAX_TRIES=6

npart() {  # how many of the 7 partition dirs exist
  ls -d /eos/user/c/cgupta/higgscharm/outputs/$1/2022postEE/HplusCharm_HtoWW* 2>/dev/null | wc -l
}

for wf in hww_2dcat_nocjet hww_2dcat_looseWP; do
  for try in $(seq 1 $MAX_TRIES); do
    n=$(npart $wf)
    echo "$(date '+%F %T') $wf try=$try partitions=$n/7" | tee -a $LOG/retry.log
    [ "$n" -ge 7 ] && { echo "$wf COMPLETE" | tee -a $LOG/retry.log; break; }
    # wait for any of this workflow's jobs still in the queue
    while condor_q -nobatch 2>/dev/null | grep -q "$wf"; do sleep 60; done
    n=$(npart $wf)
    [ "$n" -ge 7 ] && { echo "$wf COMPLETE" | tee -a $LOG/retry.log; break; }
    echo "$(date '+%F %T') resubmitting $wf" | tee -a $LOG/retry.log
    timeout 3600 $MM run -n b_hive python3 runner.py --workflow "$wf" \
        --year 2022postEE --submit --eos --output_format parquet \
        >> $LOG/retry_$wf.log 2>&1
    sleep 120
  done
done
echo "$(date '+%F %T') RETRY_DONE nocjet=$(npart hww_2dcat_nocjet)/7 looseWP=$(npart hww_2dcat_looseWP)/7" | tee -a $LOG/retry.log
