.. _isaacsim_ros2_bridge_ROS2SubscribeAckermannDrive_1:

.. _isaacsim_ros2_bridge_ROS2SubscribeAckermannDrive:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Subscribe AckermannDrive
    :keywords: lang-en omnigraph node isaacRos2:subscriber bridge r-o-s2-subscribe-ackermann-drive


ROS2 Subscribe AckermannDrive
=============================

.. <description>

This node subscribes to a ROS2 AckermannDriveStamped message

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.ros2.bridge<ext_isaacsim_ros2_bridge>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Context (*inputs:context*)", "``uint64``", "ROS2 context handle, Default of zero will use the default global context", "0"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port.", "None"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be processed. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "ackermann_cmd"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Acceleration (*outputs:acceleration*)", "``double``", "Desired acceleration in m/s^2", "0.0"
    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when a new message is received", "None"
    "Frame Id (*outputs:frameId*)", "``string``", "FrameId for ROS2 message", ""
    "Jerk (*outputs:jerk*)", "``double``", "Desired jerk in m/s^3", "0.0"
    "Speed (*outputs:speed*)", "``double``", "Desired forward speed in m/s", "0.0"
    "Steering Angle (*outputs:steeringAngle*)", "``double``", "Desired virtual angle in radians. Corresponds to the yaw of a virtual wheel located at the center of the front axle", "0.0"
    "Steering Angle Velocity (*outputs:steeringAngleVelocity*)", "``double``", "Desired rate of change of virtual angle in rad/s. Corresponds to the yaw of a virtual wheel located at the center of the front axle", "0.0"
    "Time Stamp (*outputs:timeStamp*)", "``double``", "Timestamp of message in seconds", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2SubscribeAckermannDrive"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2SubscribeAckermannDrive.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Subscribe AckermannDrive"
    "Categories", "isaacRos2:subscriber"
    "Generated Class Name", "OgnROS2SubscribeAckermannDatabase"
    "Python Module", "isaacsim.ros2.bridge"

