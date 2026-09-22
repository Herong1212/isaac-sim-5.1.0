#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
SAMPLE_DIR=$SCRIPT_DIR/../

"$SCRIPT_DIR/../python.sh" -m pip install -r $SCRIPT_DIR/../requirements.txt
"$SCRIPT_DIR/../python.sh" $SAMPLE_DIR/standalone_examples/benchmarks/benchmark_sdg.py --num-frames 10 --num-cameras 2 --resolution 1280 720 --asset-count 10 --annotators rgb distance_to_camera --disable-viewport-rendering --delete-data-when-done --headless --print-results $@ --no-window
        