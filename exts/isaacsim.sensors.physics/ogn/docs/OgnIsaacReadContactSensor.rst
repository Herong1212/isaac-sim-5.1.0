.. _isaacsim_sensors_physics_IsaacReadContactSensor_1:

.. _isaacsim_sensors_physics_IsaacReadContactSensor:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Read Contact Sensor Node
    :keywords: lang-en omnigraph node isaacPhysicsSensor physics isaac-read-contact-sensor


Isaac Read Contact Sensor Node
==============================

.. <description>

Node that reads out contact sensor data

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.sensors.physics<ext_isaacsim_sensors_physics>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Contact Sensor Prim (*inputs:csPrim*)", "``target``", "USD prim reference to contact sensor prim", "None"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Use Latest Data (*inputs:useLatestData*)", "``bool``", "True to use the latest data from the physics step, False to use the data measured by the sensor", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when sensor has data", "None"
    "In Contact (*outputs:inContact*)", "``bool``", "Bool that registers current sensor contact", "False"
    "Sensor Time (*outputs:sensorTime*)", "``float``", "Sensor reading timestamp", "0.0"
    "Force Value (*outputs:value*)", "``float``", "Contact force value reading (N)", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.sensors.physics.IsaacReadContactSensor"
    "Version", "1"
    "Extension", "isaacsim.sensors.physics"
    "Icon", "ogn/icons/isaacsim.sensors.physics.IsaacReadContactSensor.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Read Contact Sensor Node"
    "Categories", "isaacPhysicsSensor"
    "Generated Class Name", "OgnIsaacReadContactSensorDatabase"
    "Python Module", "isaacsim.sensors.physics"

