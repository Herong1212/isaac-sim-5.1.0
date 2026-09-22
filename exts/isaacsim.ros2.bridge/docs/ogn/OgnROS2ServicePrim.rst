.. _isaacsim_ros2_bridge_ROS2ServicePrim_1:

.. _isaacsim_ros2_bridge_ROS2ServicePrim:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Service Prim
    :keywords: lang-en omnigraph node isaacRos2:service bridge r-o-s2-service-prim


ROS2 Service Prim
=================

.. <description>

This node provides the services to list prims and all their attributes, as well as read and write a specific attribute

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
    "Get Attribute Service Name (*inputs:getAttributeServiceName*)", "``string``", "Name of the ROS2 service to read a specific prim attribute", "get_prim_attribute"
    "Get Attributes Service Name (*inputs:getAttributesServiceName*)", "``string``", "Name of the ROS2 service to list all specific prim's attributes", "get_prim_attributes"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any service name by the node namespace", ""
    "Prims Service Name (*inputs:primsServiceName*)", "``string``", "Name of the ROS2 service to list all prims in the current stage", "get_prims"
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Set Attribute Service Name (*inputs:setAttributeServiceName*)", "``string``", "Name of the ROS2 service to write a specific prim attribute", "set_prim_attribute"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when a response has been submitted", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2ServicePrim"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2ServicePrim.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Service Prim"
    "Categories", "isaacRos2:service"
    "Generated Class Name", "OgnROS2ServicePrimDatabase"
    "Python Module", "isaacsim.ros2.bridge"

