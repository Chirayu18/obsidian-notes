#!/bin/bash
# Overnight driver: submit the three c-jet acceptance variants for 2022postEE.
# Runs inside tmux so it survives ssh disconnects.
#
# NOTE: X509_USER_PROXY must point at the AFS copy. The default proxy lives at
# /tmp/x509up_u<uid> on ONE lxplus node, so a reconnect to a different node loses it;
# the AFS copy is shared across nodes and is what submit_condor.py itself writes.
set -u
export X509_USER_PROXY=/afs/cern.ch/user/c/cgupta/private/x509up_u151861
cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
MM=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
LOG=/tmp/cjet_study
mkdir -p $LOG

voms-proxy-info -exists -valid 0:20 || { echo "FATAL: no valid proxy" | tee -a $LOG/driver.log; exit 1; }
echo "proxy OK, $(voms-proxy-info --timeleft)s left" | tee -a $LOG/driver.log

run() {
  local wf=$1
  echo "=== $(date '+%F %T')  SUBMIT $wf ===" | tee -a $LOG/driver.log
  timeout 7200 $MM run -n b_hive python3 runner.py \
      --workflow "$wf" --year 2022postEE --submit --eos --output_format parquet \
      > $LOG/sub_$wf.log 2>&1
  local rc=$?
  echo "=== $(date '+%F %T')  $wf exit=$rc ===" | tee -a $LOG/driver.log
  tail -4 $LOG/sub_$wf.log | tee -a $LOG/driver.log
  condor_q -totals 2>&1 | grep cgupta | tee -a $LOG/driver.log
}

run hww_2dcat_nocjet
run hww_2dcat_looseWP
run hww_2dcat_nocjet_kin

echo "=== $(date '+%F %T')  ALL_SUBMITTED ===" | tee -a $LOG/driver.log
