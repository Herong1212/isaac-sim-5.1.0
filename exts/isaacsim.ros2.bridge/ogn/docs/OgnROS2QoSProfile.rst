.. _isaacsim_ros2_bridge_ROS2QoSProfile_1:

.. _isaacsim_ros2_bridge_ROS2QoSProfile:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 QoS Profile
    :keywords: lang-en omnigraph node isaacRos2 bridge r-o-s2-qo-s-profile


ROS2 QoS Profile
================

.. <description>

This node generates a JSON config of a QoS Profile

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.ros2.bridge<ext_isaacsim_ros2_bridge>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Create Profile (*inputs:createProfile*)", "``token``", "Preset profile configs. Choosing a QoS profile will update the policies accordingly.", "Default for publishers/subscribers"
    "", "Metadata", "*allowedTokens* = Default for publishers/subscribers,Services,Sensor Data,System Default,Custom", ""
    "Deadline (*inputs:deadline*)", "``double``", "Deadline policy. Defined in seconds", "0.0"
    "Depth (*inputs:depth*)", "``uint64``", "Depth (Queue size) policy. Only honored if the'history' policy was set to 'keepLast'.", "10"
    "Durability (*inputs:durability*)", "``token``", "Durability policy", "volatile"
    "", "Metadata", "*allowedTokens* = systemDefault,transientLocal,volatile,unknown", ""
    "History (*inputs:history*)", "``token``", "History policy", "keepLast"
    "", "Metadata", "*allowedTokens* = systemDefault,keepLast,keepAll,unknown", ""
    "Lease Duration (*inputs:leaseDuration*)", "``double``", "Lease Duration policy. Defined in seconds", "0.0"
    "Lifespan (*inputs:lifespan*)", "``double``", "Lifespan policy. Defined in seconds", "0.0"
    "Liveliness (*inputs:liveliness*)", "``token``", "Liveliness policy", "systemDefault"
    "", "Metadata", "*allowedTokens* = systemDefault,automatic,manualByTopic,unknown", ""
    "Reliability (*inputs:reliability*)", "``token``", "Reliability policy", "reliable"
    "", "Metadata", "*allowedTokens* = systemDefault,reliable,bestEffort,unknown", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Qos Profile (*outputs:qosProfile*)", "``string``", "QoS profile config", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2QoSProfile"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2QoSProfile.svg"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 QoS Profile"
    "Categories", "isaacRos2"
    "Generated Class Name", "OgnROS2QoSProfileDatabase"
    "Python Module", "isaacsim.ros2.bridge"

