.. _isaacsim_robot_wheeled_robots_CheckGoal2D_1:

.. _isaacsim_robot_wheeled_robots_CheckGoal2D:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Check Goal 2D
    :keywords: lang-en omnigraph node isaacWheeledRobots wheeled_robots check-goal2-d


Check Goal 2D
=============

.. <description>

Check if wheeled robot has reached goal

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
    "Target (*inputs:target*)", "``double[3]``", "Target position and orientation", "[0, 0, 0]"
    "Target Changed (*inputs:targetChanged*)", "``bool``", "Target position/orientation has changed", "False"
    "Thresholds (*inputs:thresholds*)", "``double[2]``", "Position and orientation thresholds at target", "[0.1, 0.1]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "The output execution", "None"
    "Reached Goal (*outputs:reachedGoal*)", "``bool[]``", "Reached position and orientation goals", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.robot.wheeled_robots.CheckGoal2D"
    "Version", "1"
    "Extension", "isaacsim.robot.wheeled_robots"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Check Goal 2D"
    "Categories", "isaacWheeledRobots"
    "__categoryDescriptions", "isaacWheeledRobots,robot path planning inside Isaac Sim"
    "Generated Class Name", "OgnCheckGoal2DDatabase"
    "Python Module", "isaacsim.robot.wheeled_robots"

