.. _omni_replicator_core_OgnSampleLight_1:

.. _omni_replicator_core_OgnSampleLight:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Randomize light properties
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-sample-light


Randomize light properties
==========================

.. <description>

This node randomizes the properties of light prims.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Color Max (*inputs:colorMax*)", "``float[3]``", "The maximum R, G, B values of light color. Scale is from 0 to 1", "[1, 1, 1]"
    "Color Min (*inputs:colorMin*)", "``float[3]``", "The minimum R, G, B values of light color. Scale is from 0 to 1", "[0, 0, 0]"
    "Enable Temperature (*inputs:enableTemperature*)", "``bool``", "Enable if temperature of light needs to be randomized", "False"
    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Intensity Range (*inputs:intensityRange*)", "``float[2]``", "First element contains the min value for intensity, second element contains max value", "[1, 100000]"
    "Prims (*inputs:prims*)", "``target``", "prim(s) to set location", "None"
    "Seed (*inputs:seed*)", "``int``", "Random Number Generator seed. A value of less than 0 will indicate using the global seed.", "-1"
    "Temperature Range (*inputs:temperatureRange*)", "``float[2]``", "Range of light temperature randomization. Will only be used if inputs:enableTemperature is enabled", "[1000, 10000]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSampleLight"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Randomize light properties"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSampleLightDatabase"
    "Python Module", "omni.replicator.core"

