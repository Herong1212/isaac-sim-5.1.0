.. _isaacsim_robot_wheeled_robots_HolonomicController_2:

.. _isaacsim_robot_wheeled_robots_HolonomicController:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Holonomic Controller
    :keywords: lang-en omnigraph node isaacWheeledRobots wheeled_robots holonomic-controller


Holonomic Controller
====================

.. <description>

Holonomic Controller

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.robot.wheeled_robots<ext_isaacsim_robot_wheeled_robots>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Angular Gain (*inputs:angularGain*)", "``double``", "Angular gain", "1"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution", "None"
    "Velocity Commands for the vehicle (*inputs:inputVelocity*)", "``double[3]``", "Velocity in x and y (m/s) and rotation (rad/s)", "[0.0, 0.0, 0.0]"
    "Linear Gain (*inputs:linearGain*)", "``double``", "Linear gain", "1"
    "Max Angular Speed (*inputs:maxAngularSpeed*)", "``double``", "Maximum angular rotation speed allowed for the vehicle in rad/s", "100000"
    "Max Linear Speed (*inputs:maxLinearSpeed*)", "``double``", "Maximum speed allowed for the vehicle in m/s", "100000"
    "Max Wheel Speed (*inputs:maxWheelSpeed*)", "``double``", "Maximum rotation speed allowed for the wheel joints in rad/s", "100000"
    "Mecanum Angles (*inputs:mecanumAngles*)", "``double[]``", "Angles of the mecanum wheels with respect to wheel's rotation axis in radians", "[]"
    "Up Axis (*inputs:upAxis*)", "``double[3]``", "The rotation axis of the vehicle", "[0.0, 0.0, 1.0]"
    "Wheel Axis (*inputs:wheelAxis*)", "``double[3]``", "The rotation axis of the wheels", "[1.0, 0.0, 0.0]"
    "Wheel Orientations (*inputs:wheelOrientations*)", "``double[4][]``", "Orientation of the wheel with respect to chassis' center of mass frame", "[]"
    "Wheel Positions (*inputs:wheelPositions*)", "``double[3][]``", "Position of the wheel with respect to chassis' center of mass in meters", "[]"
    "Wheel Radius (*inputs:wheelRadius*)", "``double[]``", "An array of wheel radius in meters", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Joint Velocity Command (*outputs:jointVelocityCommand*)", "``double[]``", "Velocity commands for the wheels joints", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.robot.wheeled_robots.HolonomicController"
    "Version", "2"
    "Extension", "isaacsim.robot.wheeled_robots"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Holonomic Controller"
    "Categories", "isaacWheeledRobots"
    "__categoryDescriptions", "isaacWheeledRobots,robot controller inside Isaac Sim"
    "Generated Class Name", "OgnHolonomicControllerDatabase"
    "Python Module", "isaacsim.robot.wheeled_robots"

