#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
export RESOURCE_NAME="IsaacSim"

exec "$SCRIPT_DIR/../kit/kit" "$SCRIPT_DIR/../apps/isaacsim.exp.selector.kit" --ext-folder "$SCRIPT_DIR/../exts" --ext-folder "$SCRIPT_DIR/../extscache" --ext-folder "$SCRIPT_DIR/../extsDeprecated" --ext-folder "$SCRIPT_DIR/../apps" --/app/quitAfter=500 --/persistent/ext/isaacsim.app.selector/auto_start=false --/persistent/ext/isaacsim.app.selector/show_console=true --/persistent/ext/isaacsim.app.selector/persistent_selector=false "$@"
