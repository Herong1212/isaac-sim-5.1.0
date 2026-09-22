.. _isaacsim_sensors_physx_IsaacReadLightBeam_1:

.. _isaacsim_sensors_physx_IsaacReadLightBeam:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Read LightBeam Sensor Node
    :keywords: lang-en omnigraph node isaacPhysxSensor physx isaac-read-light-beam


Isaac Read LightBeam Sensor Node
================================

.. <description>

Node that reads out light beam sensor data

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.sensors.physx<ext_isaacsim_sensors_physx>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Light Beam Prim (*inputs:lightbeamPrim*)", "``target``", "Usd prim reference to the light beam prim", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Beam End Points (*outputs:beamEndPoints*)", "``pointf[3][]``", "Array containing end points of each beam", "[]"
    "Beam Hit Data (*outputs:beamHitData*)", "``bool[]``", "Array of bools that registers if a light beam is broken", "[]"
    "Beam Origins (*outputs:beamOrigins*)", "``pointf[3][]``", "Array containing origins of each beam", "[]"
    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when sensor has data", "None"
    "Hit Pos Data (*outputs:hitPosData*)", "``pointf[3][]``", "Array containing hit position data", "[]"
    "Linear Depth Data (*outputs:linearDepthData*)", "``float[]``", "Array containing linear depth data", "[]"
    "Num Rays (*outputs:numRays*)", "``int``", "The number of rays in light curtain", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.sensors.physx.IsaacReadLightBeam"
    "Version", "1"
    "Extension", "isaacsim.sensors.physx"
    "Icon", "ogn/icons/isaacsim.sensors.physx.IsaacReadLightBeam.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Read LightBeam Sensor Node"
    "Categories", "isaacPhysxSensor"
    "Generated Class Name", "OgnIsaacReadLightBeamSensorDatabase"
    "Python Module", "isaacsim.sensors.physx"

