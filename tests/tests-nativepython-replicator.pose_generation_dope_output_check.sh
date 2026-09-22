#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
SAMPLE_DIR=$SCRIPT_DIR/../

"$SCRIPT_DIR/../python.sh" -m pip install -r $SCRIPT_DIR/../requirements.txt
"$SCRIPT_DIR/../python.sh" $SAMPLE_DIR/standalone_examples/replicator/pose_generation/pose_generation.py --test --writer DOPE --output_folder _out_dope_test $@ --no-window
        