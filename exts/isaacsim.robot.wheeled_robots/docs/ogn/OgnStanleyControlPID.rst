.. _isaacsim_robot_wheeled_robots_StanleyControlPID_1:

.. _isaacsim_robot_wheeled_robots_StanleyControlPID:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Stanley Control PID
    :keywords: lang-en omnigraph node isaacWheeledRobots wheeled_robots stanley-control-p-i-d


Stanley Control PID
===================

.. <description>

Drive to Target Steering

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
    "Current Speed (*inputs:currentSpeed*)", "``vectord[3]``", "Current linear velocity of the robot", "[0.0, 0.0, 0.0]"
    "Draw Path (*inputs:drawPath*)", "``bool``", "Draw the provided path curve onto the stage", "False"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution", "None"
    "Gains (*inputs:gains*)", "``double[3]``", "control, velocity and steering gains", "[0.5, 0.1, 0.0872665]"
    "Max Velocity (*inputs:maxVelocity*)", "``double``", "Maximum linear velocity of the robot", "1.5"
    "Path Arrays (*inputs:pathArrays*)", "``double[]``", "The path v, x, y, and yaw arrays", "[]"
    "Reached Goal (*inputs:reachedGoal*)", "``bool[]``", "Position and orientation thresholds at target", "[False, False]"
    "Step (*inputs:step*)", "``double``", "Step", "0.16666666667"
    "Target (*inputs:target*)", "``double[3]``", "Target position and orientation", "[0, 0, 0]"
    "Target Changed (*inputs:targetChanged*)", "``bool``", "Target position/orientation has changed", "False"
    "Thresholds (*inputs:thresholds*)", "``double[2]``", "Position and orientation thresholds at target", "[0.1, 0.1]"
    "Wheel Base (*inputs:wheelBase*)", "``double``", "Distance between the centers of the front and rear wheels", "0.4132"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Angular Velocity (*outputs:angularVelocity*)", "``double``", "Current angular speed for robot drive", "None"
    "Exec Out (*outputs:execOut*)", "``execution``", "The output execution", "None"
    "Linear Velocity (*outputs:linearVelocity*)", "``double``", "Current forward speed for robot drive", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.robot.wheeled_robots.StanleyControlPID"
    "Version", "1"
    "Extension", "isaacsim.robot.wheeled_robots"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Stanley Control PID"
    "Categories", "isaacWheeledRobots"
    "__categoryDescriptions", "isaacWheeledRobots,robot path planning inside Isaac Sim"
    "Generated Class Name", "OgnStanleyControlPIDDatabase"
    "Python Module", "isaacsim.robot.wheeled_robots"

