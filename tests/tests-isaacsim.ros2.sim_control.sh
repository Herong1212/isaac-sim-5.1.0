#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
export RESOURCE_NAME="IsaacSim"
export ROS_DISTRO=humble
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=$((($RANDOM % 18) + 80))
INTERNAL_LIBS=$(readlink -f $SCRIPT_DIR/../exts/isaacsim.ros2.bridge/humble/lib)
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$INTERNAL_LIBS

exec "$SCRIPT_DIR/../kit/kit"  --empty --enable omni.kit.test --/exts/omni.kit.test/testExtEnableProfiler=0 --/exts/omni.kit.test/testExtArgs/0="--no-window" --/exts/omni.kit.test/testExtArgs/1="--allow-root" --/exts/omni.kit.test/runTestsAndQuit=true --/exts/omni.kit.test/testExts/0='isaacsim.ros2.sim_control' --ext-folder "$SCRIPT_DIR/../exts"  --ext-folder "$SCRIPT_DIR/../extscache"  --ext-folder "$SCRIPT_DIR/../extsDeprecated"  --ext-folder "$SCRIPT_DIR/../apps"  --/app/enableStdoutOutput=0 --no-window --allow-root --/telemetry/mode=test --/crashreporter/data/testName="ext-test-isaacsim.ros2.sim_control" "$@"
