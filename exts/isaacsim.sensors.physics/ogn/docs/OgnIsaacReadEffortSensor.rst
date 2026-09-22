.. _isaacsim_sensors_physics_IsaacReadEffortSensor_1:

.. _isaacsim_sensors_physics_IsaacReadEffortSensor:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Read Effort Node
    :keywords: lang-en omnigraph node isaacPhysicsSensor physics isaac-read-effort-sensor


Isaac Read Effort Node
======================

.. <description>

Node that reads out joint effort values

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.sensors.physics<ext_isaacsim_sensors_physics>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Enabled (*inputs:enabled*)", "``bool``", "True to enable sensor, False to disable the sensor", "True"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Prim Path (*inputs:prim*)", "``target``", "Path to the joint getting measured", "None"
    "Sensor Period (*inputs:sensorPeriod*)", "``float``", "Downtime between sensor readings", "0"
    "Use Latest Data (*inputs:useLatestData*)", "``bool``", "True to use the latest data from the physics step, False to use the data measured by the sensor", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when sensor has data", "None"
    "Sensor Time (*outputs:sensorTime*)", "``float``", "Timestamp of the sensor reading", "0"
    "Effort Value (*outputs:value*)", "``float``", "Effort value reading", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.sensors.physics.IsaacReadEffortSensor"
    "Version", "1"
    "Extension", "isaacsim.sensors.physics"
    "Icon", "ogn/icons/isaacsim.sensors.physics.IsaacReadEffortSensor.svg"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Read Effort Node"
    "Categories", "isaacPhysicsSensor"
    "Generated Class Name", "OgnIsaacReadEffortSensorDatabase"
    "Python Module", "isaacsim.sensors.physics"

