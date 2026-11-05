#!/bin/bash
cd /eos/user/c/cgupta/HToWW/b-hive
source /afs/cern.ch/user/c/cgupta/.bashrc
micromamba activate b_hive
source setup.sh
law index
./train_v11_2dcats.sh
