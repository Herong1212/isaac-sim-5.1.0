#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
SAMPLE_DIR=$SCRIPT_DIR/../

"$SCRIPT_DIR/../python.sh" -m pip install -r $SCRIPT_DIR/../requirements.txt
"$SCRIPT_DIR/../python.sh" $SAMPLE_DIR/standalone_examples/testing/external_workflow_tests/ar/ar_sdg_test.py --scene $SAMPLE_DIR/standalone_examples/testing/external_workflow_tests/ar/data/physics_GPU.usda --num_datasets 3 --num_frames 3 --windowed --test --output _out_ar_test $@ --no-window
        