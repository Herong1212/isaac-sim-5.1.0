#!/usr/bin/env bash
set -e

MY_DIR=$(realpath $(dirname ${BASH_SOURCE}))
source "${MY_DIR}/python.sh" "${MY_DIR}/pythonapps/examples/example.py" $@
