#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
if [ ! -z "$OMNI_KIT_LD_PRELOAD" ]; then
    export LD_PRELOAD="$OMNI_KIT_LD_PRELOAD:$LD_PRELOAD"
fi
if [ "$_MR_BUILD_WITH_ASAN" == "true" ]; then
    export LIB_ASAN_PATH=$SCRIPT_DIR/libasan.so.6
    export ASAN_OPTIONS="protect_shadow_gap=0:halt_on_error=0:detect_leaks=1"
    export LSAN_OPTIONS="exitcode=0"
    if [ "$LD_PRELOAD" != *"libasan.so"* ]; then
        export LD_PRELOAD="${LIB_ASAN_PATH}${LD_PRELOAD:+:$LD_PRELOAD}"
    fi
    echo "ASAN_OPTIONS=${ASAN_OPTIONS}"
    echo "LSAN_OPTIONS=${LSAN_OPTIONS}"
    echo "LIB_ASAN_PATH=${LIB_ASAN_PATH}"
    echo "LD_PRELOAD=${LD_PRELOAD}"
fi
${EXEC:-exec} "$SCRIPT_DIR//kit" "$SCRIPT_DIR/apps/omni.app.dev.kit"  "$@"
