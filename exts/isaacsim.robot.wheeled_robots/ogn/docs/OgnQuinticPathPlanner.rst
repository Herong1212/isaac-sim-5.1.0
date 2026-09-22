.. _isaacsim_robot_wheeled_robots_QuinticPathPlanner_1:

.. _isaacsim_robot_wheeled_robots_QuinticPathPlanner:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Quintic Path Planner
    :keywords: lang-en omnigraph node isaacWheeledRobots wheeled_robots quintic-path-planner


Quintic Path Planner
====================

.. <description>

Quintic Path Planner For Wheeled robots

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.robot.wheeled_robots<ext_isaacsim_robot_wheeled_robots>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Current Orientation (*inputs:currentOrientation*)", "``quatd[4]``", "Current rotation of the robot as a quaternion (recommended to use Get Prim Local to World Transform node)", "[0.0, 0.0, 0.0, 0.0]"
    "Current Position (*inputs:currentPosition*)", "``vectord[3]``", "Current position of the robot (recommended to use Get Prim Local to World Transform node)", "[0.0, 0.0, 0.0]"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution", "None"
    "Goal Accel (*inputs:goalAccel*)", "``double``", "Goal acceleration", "0.02"
    "Goal Velocity (*inputs:goalVelocity*)", "``double``", "Goal velocity", "0.5"
    "Initial Accel (*inputs:initialAccel*)", "``double``", "Initial acceleration", "0.02"
    "Initial Velocity (*inputs:initialVelocity*)", "``double``", "Initial velocity", "0.5"
    "Max Accel (*inputs:maxAccel*)", "``double``", "Max acceleration", "1.5"
    "Max Jerk (*inputs:maxJerk*)", "``double``", "Max jerk", "0.3"
    "Step (*inputs:step*)", "``double``", "Step", "0.16666666667"
    "Target Orientation (*inputs:targetOrientation*)", "``quatd[4]``", "Target orientation (used if no targetPrim provided)", "[0.0, 0.0, 0.0, 0.0]"
    "Target Position (*inputs:targetPosition*)", "``vectord[3]``", "Target position (used if no targetPrim provided)", "[0.0, 0.0, 0.0]"
    "Target Prim (*inputs:targetPrim*)", "``target``", "USD prim reference to the goal position/orientation prim", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "The output execution", "None"
    "Path Arrays (*outputs:pathArrays*)", "``double[]``", "The path v, x, y, and yaw arrays", "None"
    "Target (*outputs:target*)", "``double[3]``", "Target position and orientation", "None"
    "Target Changed (*outputs:targetChanged*)", "``bool``", "Target position/orientation has changed", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.robot.wheeled_robots.QuinticPathPlanner"
    "Version", "1"
    "Extension", "isaacsim.robot.wheeled_robots"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Quintic Path Planner"
    "Categories", "isaacWheeledRobots"
    "__categoryDescriptions", "isaacWheeledRobots,robot path planning inside Isaac Sim"
    "Generated Class Name", "OgnQuinticPathPlannerDatabase"
    "Python Module", "isaacsim.robot.wheeled_robots"

