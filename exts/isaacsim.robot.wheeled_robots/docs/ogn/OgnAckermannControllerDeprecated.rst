.. _isaacsim_robot_wheeled_robots_AckermannControllerDeprecated_1:

.. _isaacsim_robot_wheeled_robots_AckermannControllerDeprecated:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Ackermann Controller Deprecated
    :keywords: lang-en omnigraph node isaacWheeledRobots wheeled_robots ackermann-controller-deprecated


Ackermann Controller Deprecated
===============================

.. <description>

NOTE: DEPRECATED Ackermann Controller. Please you replace with the AckermannController OmniGraph node instead.

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.robot.wheeled_robots<ext_isaacsim_robot_wheeled_robots>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "DT (*inputs:DT*)", "``double``", "Delta time for the simulation step", "0.0"
    "Acceleration (*inputs:acceleration*)", "``double``", "Desired forward acceleration for the robot in m/s^2", "1.0"
    "Current Linear Velocity (*inputs:currentLinearVelocity*)", "``vectord[3]``", "Current linear velocity of the robot in m/s", "[0.0, 0.0, 0.0]"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution", "None"
    "Invert Steering Angle (*inputs:invertSteeringAngle*)", "``bool``", "Flips the sign of the steering angle, Set to true for rear wheel steering", "False"
    "Max Wheel Rotation (*inputs:maxWheelRotation*)", "``double``", "Maximum angle of rotation for the front wheels in radians", "6.28"
    "Max Wheel Velocity (*inputs:maxWheelVelocity*)", "``double``", "Maximum angular velocity of the robot wheel in rad/s", "100000"
    "Speed (*inputs:speed*)", "``double``", "Desired forward speed in m/s", "1.0"
    "Steering Angle (*inputs:steeringAngle*)", "``double``", "Desired virtual angle in radians. Corresponds to the yaw of a virtual wheel located at the center of the front axle. By default it is positive for turning left and negative for turning right for front wheel drive.", "0.0"
    "Track Width (*inputs:trackWidth*)", "``double``", "Distance between the left and right rear wheels of the robot in meters", "0.0"
    "Turning Wheel Radius (*inputs:turningWheelRadius*)", "``double``", "Radius of the front wheels of the robot in meters", "0.0"
    "Use Acceleration (*inputs:useAcceleration*)", "``bool``", "Use acceleration as an input, Set to false to use speed as input instead", "False"
    "Wheel Base (*inputs:wheelBase*)", "``double``", "Distance between the front and rear axles of the robot in meters", "0.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "The output execution", "None"
    "Left Wheel Angle (*outputs:leftWheelAngle*)", "``double``", "Angle for the left turning wheel in radians", "None"
    "Right Wheel Angle (*outputs:rightWheelAngle*)", "``double``", "Angle for the right turning wheel in radians", "None"
    "Wheel Rotation Velocity (*outputs:wheelRotationVelocity*)", "``double``", "Angular velocity for the turning wheels in rad/s", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.robot.wheeled_robots.AckermannControllerDeprecated"
    "Version", "1"
    "Extension", "isaacsim.robot.wheeled_robots"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Ackermann Controller Deprecated"
    "hidden", "true"
    "Categories", "isaacWheeledRobots"
    "__categoryDescriptions", "isaacWheeledRobots,Ackermann controller for wheels in Isaac Sim"
    "Generated Class Name", "OgnAckermannControllerDeprecatedDatabase"
    "Python Module", "isaacsim.robot.wheeled_robots"

