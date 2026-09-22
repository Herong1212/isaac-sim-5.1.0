#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
export RESOURCE_NAME="IsaacSim"

exec "$SCRIPT_DIR/../kit/kit" "$SCRIPT_DIR/../apps/isaacsim.exp.full.streaming.kit" --ext-folder "$SCRIPT_DIR/../exts" --ext-folder "$SCRIPT_DIR/../extscache" --ext-folder "$SCRIPT_DIR/../extsDeprecated" --ext-folder "$SCRIPT_DIR/../apps" --no-window --/app/quitAfter=100 --/app/file/ignoreUnsavedOnExit=1 "$@"
