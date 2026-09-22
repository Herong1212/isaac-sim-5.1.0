.. _isaacsim_ros2_bridge_ROS2Context_2:

.. _isaacsim_ros2_bridge_ROS2Context:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Context
    :keywords: lang-en omnigraph node isaacRos2 bridge r-o-s2-context


ROS2 Context
============

.. <description>

This node creates a ROS2 Context for a given domain ID

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.ros2.bridge<ext_isaacsim_ros2_bridge>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Domain Id (*inputs:domain_id*)", "``uchar``", "Domain ID for ROS context", "0"
    "Use Domain ID Env Var (*inputs:useDomainIDEnvVar*)", "``bool``", "Set to true to use ROS_DOMAIN_ID environment variable if set. Defaults to domain_id if not found", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Context (*outputs:context*)", "``uint64``", "handle to initialized ROS2 context", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2Context"
    "Version", "2"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2Context.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Context"
    "Categories", "isaacRos2"
    "Generated Class Name", "OgnROS2ContextDatabase"
    "Python Module", "isaacsim.ros2.bridge"

