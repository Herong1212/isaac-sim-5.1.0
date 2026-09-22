.. _isaacsim_ros2_bridge_ROS2Publisher_1:

.. _isaacsim_ros2_bridge_ROS2Publisher:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Publisher
    :keywords: lang-en omnigraph node isaacRos2:publisher bridge r-o-s2-publisher


ROS2 Publisher
==============

.. <description>

This node publishes any existing ROS2 message

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
    "", "Metadata", "*displayGroup* = parameters", ""
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port.", "None"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Message Name (*inputs:messageName*)", "``string``", "Message name (e.g.: Int32 for std_msgs/msg/Int32)", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Message Package (*inputs:messagePackage*)", "``string``", "Message package (e.g.: std_msgs for std_msgs/msg/Int32)", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Message Subfolder (*inputs:messageSubfolder*)", "``string``", "Message subfolder (e.g.: msg for std_msgs/msg/Int32)", "msg"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be processed. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "topic"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when a new message is published", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2Publisher"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2Publisher.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Publisher"
    "Categories", "isaacRos2:publisher"
    "Generated Class Name", "OgnROS2PublisherDatabase"
    "Python Module", "isaacsim.ros2.bridge"

