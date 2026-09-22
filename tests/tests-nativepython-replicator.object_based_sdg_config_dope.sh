#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
SAMPLE_DIR=$SCRIPT_DIR/../

"$SCRIPT_DIR/../python.sh" -m pip install -r $SCRIPT_DIR/../requirements.txt
"$SCRIPT_DIR/../python.sh" $SAMPLE_DIR/standalone_examples/replicator/object_based_sdg/object_based_sdg.py --config standalone_examples/replicator/object_based_sdg/config/object_based_sdg_dope_config.yaml $@ --no-window
        