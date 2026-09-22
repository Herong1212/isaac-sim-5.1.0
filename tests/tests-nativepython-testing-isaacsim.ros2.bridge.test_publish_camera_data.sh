#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
SAMPLE_DIR=$SCRIPT_DIR/../
export ROS_DISTRO=humble
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=$((($RANDOM % 18) + 80))
INTERNAL_LIBS=$(readlink -f $SCRIPT_DIR/../exts/isaacsim.ros2.bridge/humble/lib)
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$INTERNAL_LIBS

"$SCRIPT_DIR/../python.sh" -m pip install -r $SCRIPT_DIR/../requirements.txt
"$SCRIPT_DIR/../python.sh" $SAMPLE_DIR/standalone_examples/testing/isaacsim.ros2.bridge/test_publish_camera_data.py --test-steps=5 $@ --no-window
        