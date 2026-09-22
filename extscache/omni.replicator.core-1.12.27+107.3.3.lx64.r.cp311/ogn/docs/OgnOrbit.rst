.. _omni_replicator_core_OgnOrbit_1:

.. _omni_replicator_core_OgnOrbit:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Compute Orbit Position
    :keywords: lang-en omnigraph node Replicator core ogn-orbit


Compute Orbit Position
======================

.. <description>

Compute prim position in the form of an orbit around a central point.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Azimuth (*inputs:azimuth*)", "``float[]``", "Horizontal angle in degrees.", "[]"
    "Barycentre Coordinates (*inputs:barycentreCoordinates*)", "``float[3]``", "The barycentre position expressed in (x, y, z) coordinates.", "[0.0, 0.0, 0.0]"
    "Barycentre Mode (*inputs:barycentreMode*)", "``token``", "Determine whether to use barycentrePrim or barycentreCoordinates as the orbit barycentre.", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "", "Metadata", "*literalOnly* = 1", ""
    "", "Metadata", "*allowedTokens* = Prim,Coordinates", ""
    "Barycentre Prim (*inputs:barycentrePrim*)", "``target``", "The barycentre prim that the prims will orbit around", "None"
    "Distance (*inputs:distance*)", "``float[]``", "Distance from barycentre.", "[]"
    "Elevation (*inputs:elevation*)", "``float[]``", "Vertical angle in degrees.", "[]"
    "Exec (*inputs:exec*)", "``execution``", "exec", "None"
    "Prims (*inputs:prims*)", "``target``", "The prims orbit position is to be computed", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "exec", "None"
    "Values (*outputs:values*)", "``double[3][]``", "Position values of prims orbiting around a barycentre point.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnOrbit"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Compute Orbit Position"
    "Categories", "Replicator"
    "__categoryDescriptions", "Replicator,Orbit"
    "Generated Class Name", "OgnOrbitDatabase"
    "Python Module", "omni.replicator.core"

