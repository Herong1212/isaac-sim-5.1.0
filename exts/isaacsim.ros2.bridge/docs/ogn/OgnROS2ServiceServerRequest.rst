.. _isaacsim_ros2_bridge_OgnROS2ServiceServerRequest_1:

.. _isaacsim_ros2_bridge_OgnROS2ServiceServerRequest:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Service Server Request
    :keywords: lang-en omnigraph node isaacRos2:service bridge ogn-r-o-s2-service-server-request


ROS2 Service Server Request
===========================

.. <description>

This node is a generic service server that provides interface for a ROS service. The request/response fields of the service are parsed and are made accessible via the node based on the service specified from messagePackage, messageSubfolder, messageName. The server receives a request (accessible from the node outputs). To receive the response this node should be connected to a OgnROS2ServiceServerResponse node through the serverHandle input. The OgnROS2ServiceServerResponse node is responsible for providing the response.

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
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Message Name (*inputs:messageName*)", "``string``", "Service name (e.g.: AddTwoInts for example_interfaces/srv/AddTwoInts)", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Message Package (*inputs:messagePackage*)", "``string``", "Package name (e.g.: example_interfaces for example_interfaces/srv/AddTwoInts)", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Message Subfolder (*inputs:messageSubfolder*)", "``string``", "Subfolder name (e.g.: srv for example_interfaces/srv/AddTwoInts)", "srv"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Name of ROS2 Node, prepends any topic published/subscribed by the node name", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Service Name (*inputs:serviceName*)", "``string``", "Name of ROS2 Service", "/service_name"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "On Received (*outputs:onReceived*)", "``execution``", "Output execution triggers when a request is received", "None"
    "Server Handle (*outputs:serverHandle*)", "``uint64``", "handle to the server", "0"
    "", "Metadata", "*displayGroup* = parameters", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.OgnROS2ServiceServerRequest"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.OgnROS2ServiceServerRequest.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Service Server Request"
    "Categories", "isaacRos2:service"
    "Generated Class Name", "OgnROS2ServiceServerRequestDatabase"
    "Python Module", "isaacsim.ros2.bridge"

