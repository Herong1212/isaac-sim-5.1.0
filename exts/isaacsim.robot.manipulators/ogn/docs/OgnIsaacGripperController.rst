.. _isaacsim_robot_manipulators_IsaacGripperController_1:

.. _isaacsim_robot_manipulators_IsaacGripperController:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Gripper Controller Node
    :keywords: lang-en omnigraph node isaacRobotManipulators manipulators isaac-gripper-controller


Isaac Gripper Controller Node
=============================

.. <description>

Isaac Sim Gripper Controller Node

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.robot.manipulators<ext_isaacsim_robot_manipulators>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Articulation Root Prim (*inputs:articulationRootPrim*)", "``target``", "Articulation root prim of the robot", "None"
    "Close (*inputs:close*)", "``execution``", "close gripper call", "None"
    "Close Position (*inputs:closePosition*)", "``double[]``", "closing position for the gripper joints, will use the joint limit if not provided", "None"
    "Exec In (*inputs:execIn*)", "``execution``", "tick", "None"
    "Gripper Prim (*inputs:gripperPrim*)", "``target``", "The gripper's root link prim", "None"
    "Gripper Speed (*inputs:gripperSpeed*)", "``double[]``", "gripper speed (distance per frame)", "[]"
    "Joint Names (*inputs:jointNames*)", "``token[]``", "gripper joint names", "[]"
    "Open (*inputs:open*)", "``execution``", "open gripper call", "None"
    "Open Position (*inputs:openPosition*)", "``double[]``", "maximum opening position for the gripper joints, will use the joint limit if not provided", "None"
    "Stop (*inputs:stop*)", "``execution``", "stop gripper call", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Joint Names (*outputs:jointNames*)", "``token[]``", "gripper joint names", "None"
    "Position Commands (*outputs:positionCommands*)", "``double[]``", "joint commands to the articulation controller", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.robot.manipulators.IsaacGripperController"
    "Version", "1"
    "Extension", "isaacsim.robot.manipulators"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Gripper Controller Node"
    "Categories", "isaacRobotManipulators"
    "__categoryDescriptions", "isaacRobotManipulators,Controller for Grippers"
    "Generated Class Name", "OgnIsaacGripperControllerDatabase"
    "Python Module", "isaacsim.robot.manipulators"

