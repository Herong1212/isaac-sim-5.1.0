.. _isaacsim_robot_wheeled_robots_AckermannController_2:

.. _isaacsim_robot_wheeled_robots_AckermannController:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Ackermann Controller
    :keywords: lang-en omnigraph node isaacWheeledRobots wheeled_robots ackermann-controller


Ackermann Controller
====================

.. <description>

Ackermann Controller

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.robot.wheeled_robots<ext_isaacsim_robot_wheeled_robots>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Acceleration (*inputs:acceleration*)", "``double``", "Magnitude of acceleration for the robot in m/s^2. Set to 0.0 to instantly set velocity to desired forward speed", "0.0"
    "Back Wheel Radius (*inputs:backWheelRadius*)", "``double``", "Radius of the back wheels of the robot in meters", "0.0"
    "Dt (*inputs:dt*)", "``double``", "Delta time for the simulation step", "0.0"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution", "None"
    "Front Wheel Radius (*inputs:frontWheelRadius*)", "``double``", "Radius of the front wheels of the robot in meters", "0.0"
    "Invert Steering (*inputs:invertSteering*)", "``bool``", "Flips the sign of the steering angle, Set to true for rear wheel steering", "False"
    "Max Acceleration (*inputs:maxAcceleration*)", "``double``", "Maximum magnitude of acceleration for the robot in m/s^2. Parameter is ignored if set to 0.0", "0.0"
    "Max Steering Angle Velocity (*inputs:maxSteeringAngleVelocity*)", "``double``", "Maximum magnitude of desired rate of change for steering angle in rad/s. Parameter is ignored if set to 0.0", "0.0"
    "Max Wheel Rotation (*inputs:maxWheelRotation*)", "``double``", "Magnitude of maximum angle of rotation for the front wheels in radians. Parameter is ignored if set to 0.0", "6.28"
    "Max Wheel Velocity (*inputs:maxWheelVelocity*)", "``double``", "Maximum magnitude of angular velocity of the robot wheel in rad/s. Parameter is ignored if set to 0.0", "0.0"
    "Speed (*inputs:speed*)", "``double``", "Desired forward speed in m/s", "0.0"
    "Steering Angle (*inputs:steeringAngle*)", "``double``", "Desired virtual angle in radians. Corresponds to the yaw of a virtual wheel located at the center of the front axle. By default it is positive for turning left and negative for turning right for front wheel drive.", "0.0"
    "Steering Angle Velocity (*inputs:steeringAngleVelocity*)", "``double``", "Magnitude of desired rate of change for steering angle in rad/s. Set to 0.0 to instantly snap wheels to desired steering angle", "0.0"
    "Track Width (*inputs:trackWidth*)", "``double``", "Distance between the left and right rear wheels of the robot in meters", "0.0"
    "Wheel Base (*inputs:wheelBase*)", "``double``", "Distance between the front and rear axles of the robot in meters", "0.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "The output execution", "None"
    "Wheel Angles (*outputs:wheelAngles*)", "``double[]``", "Angles of the left and right turning wheels in radians. In specific order:  left_wheel_angle,  right_wheel_angle", "None"
    "Wheel Rotation Velocity (*outputs:wheelRotationVelocity*)", "``double[]``", "Angular velocity for the turning wheels in rad/s. In specific order:  front left wheel, front right wheel, back left wheel, back right wheel", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.robot.wheeled_robots.AckermannController"
    "Version", "2"
    "Extension", "isaacsim.robot.wheeled_robots"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Ackermann Controller"
    "Categories", "isaacWheeledRobots"
    "__categoryDescriptions", "isaacWheeledRobots,Ackermann controller for wheels in Isaac Sim"
    "Generated Class Name", "OgnAckermannControllerDatabase"
    "Python Module", "isaacsim.robot.wheeled_robots"

