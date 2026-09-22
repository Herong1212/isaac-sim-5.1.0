.. _isaacsim_ros2_bridge_ROS2SubscribeTransformTree_1:

.. _isaacsim_ros2_bridge_ROS2SubscribeTransformTree:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Subscribe Transform Tree
    :keywords: lang-en omnigraph node isaacRos2:subscriber bridge r-o-s2-subscribe-transform-tree


ROS2 Subscribe Transform Tree
=============================

.. <description>

This node subscribes to a ROS2 Transform Tree

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.ros2.bridge<ext_isaacsim_ros2_bridge>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Articulation Roots (*inputs:articulationRoots*)", "``token[]``", "Array of articulation root prims that will be modified", "[]"
    "Context (*inputs:context*)", "``uint64``", "ROS2 context handle, Default of zero will use the default global context", "0"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port.", "None"
    "Frame Names Map (*inputs:frameNamesMap*)", "``token[]``", "Array of [prim_path_0, frame_name_0, prim_path_1, frame_name_1, ...].", "[]"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be processed. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "tf"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when a new message is received", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2SubscribeTransformTree"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2SubscribeTransformTree.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Subscribe Transform Tree"
    "Categories", "isaacRos2:subscriber"
    "Generated Class Name", "OgnROS2SubscribeTransformTreeDatabase"
    "Python Module", "isaacsim.ros2.bridge"

