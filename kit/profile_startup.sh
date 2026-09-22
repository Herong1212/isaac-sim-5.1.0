#!/bin/bash
set -e

echo ${BASH_SOURCE}
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
PROFILE_FILE=${SCRIPT_DIR}/startup_profile.gz

rm -f ${PROFILE_FILE}

# Uncomment line below to enable python profiler (slower). Or set it before running this script.
# export CARB_PROFILING_PYTHON=1

"$SCRIPT_DIR/kit" --/plugins/carb.profiler-cpu.plugin/saveProfile=1 --/app/file/ignoreUnsavedOnExit=1 --/plugins/carb.profiler-cpu.plugin/compressProfile=1 --/app/profileFromStart=1 --/plugins/carb.profiler-cpu.plugin/filePath="${PROFILE_FILE}" --/app/quitAfter=50 "$@"
"$SCRIPT_DIR/dev/repo.sh" tracetools tracy ${PROFILE_FILE}
