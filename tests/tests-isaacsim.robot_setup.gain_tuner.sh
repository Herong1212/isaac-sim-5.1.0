#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
export RESOURCE_NAME="IsaacSim"

exec "$SCRIPT_DIR/../kit/kit"  --empty --enable omni.kit.test --/exts/omni.kit.test/testExtEnableProfiler=0 --/exts/omni.kit.test/testExtArgs/0="--no-window" --/exts/omni.kit.test/testExtArgs/1="--allow-root" --/exts/omni.kit.test/runTestsAndQuit=true --/exts/omni.kit.test/testExts/0='isaacsim.robot_setup.gain_tuner' --ext-folder "$SCRIPT_DIR/../exts"  --ext-folder "$SCRIPT_DIR/../extscache"  --ext-folder "$SCRIPT_DIR/../extsDeprecated"  --ext-folder "$SCRIPT_DIR/../apps"  --/app/enableStdoutOutput=0 --no-window --allow-root --/telemetry/mode=test --/crashreporter/data/testName="ext-test-isaacsim.robot_setup.gain_tuner" "$@"
