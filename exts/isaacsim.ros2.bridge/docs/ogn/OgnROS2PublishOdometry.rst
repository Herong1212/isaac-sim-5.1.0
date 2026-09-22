.. _isaacsim_ros2_bridge_ROS2PublishOdometry_1:

.. _isaacsim_ros2_bridge_ROS2PublishOdometry:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Publish Odometry
    :keywords: lang-en omnigraph node isaacRos2:publisher bridge r-o-s2-publish-odometry


ROS2 Publish Odometry
=====================

.. <description>

This node publishes odometry as a ROS2 Odometry message

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.ros2.bridge<ext_isaacsim_ros2_bridge>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Angular Velocity (*inputs:angularVelocity*)", "``vectord[3]``", "Angular velocity vector in rad/s", "[0.0, 0.0, 0.0]"
    "Chassis Frame Id (*inputs:chassisFrameId*)", "``string``", "FrameId for robot chassis frame", "base_link"
    "Context (*inputs:context*)", "``uint64``", "ROS2 context handle, Default of zero will use the default global context", "0"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Linear Velocity (*inputs:linearVelocity*)", "``vectord[3]``", "Linear velocity vector in m/s", "[0.0, 0.0, 0.0]"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Odom Frame Id (*inputs:odomFrameId*)", "``string``", "FrameId for ROS2 odometry message", "odom"
    "Orientation (*inputs:orientation*)", "``quatd[4]``", "Orientation as a quaternion (IJKR)", "[0.0, 0.0, 0.0, 1.0]"
    "Position (*inputs:position*)", "``vectord[3]``", "Position vector in meters", "[0.0, 0.0, 0.0]"
    "Publish Raw Velocities (*inputs:publishRawVelocities*)", "``bool``", "When enabled, linear and angular velocities are published as provided, without transformation. When disabled, the given world velocities are projected into the robot's frame before publishing.", "False"
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Robot Front (*inputs:robotFront*)", "``vectord[3]``", "The front of the robot. The robotFront vector utilizes x and y, and drops the z component. We assume a robotUp vector of [0.0, 0.0, 1.0] to project given world linear and angular velocities into the robot's local frame.", "[1.0, 0.0, 0.0]"
    "Timestamp (*inputs:timeStamp*)", "``double``", "ROS2 Timestamp in seconds", "0.0"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "odom"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2PublishOdometry"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2PublishOdometry.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Publish Odometry"
    "Categories", "isaacRos2:publisher"
    "Generated Class Name", "OgnROS2PublishOdometryDatabase"
    "Python Module", "isaacsim.ros2.bridge"

