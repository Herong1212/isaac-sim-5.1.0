.. _omni_syntheticdata_SdTestStageManipulationScenarii_1:

.. _omni_syntheticdata_SdTestStageManipulationScenarii:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Test Stage Manipulation Scenarii
    :keywords: lang-en omnigraph node graph:simulation,internal:test syntheticdata sd-test-stage-manipulation-scenarii


Sd Test Stage Manipulation Scenarii
===================================

.. <description>

Synthetic Data test node applying randomly some predefined stage manipulation scenarii

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Random Seed (*inputs:randomSeed*)", "``int``", "Random seed", "0"
    "World Prim Path (*inputs:worldPrimPath*)", "``token``", "Path of the world prim : contains every modifiable prim, cannot be modified", ""


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Frame Number (*state:frameNumber*)", "``uint64``", "Current frameNumber (number of invocations)", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdTestStageManipulationScenarii"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "Categories", "graph:simulation,internal:test"
    "Generated Class Name", "OgnSdTestStageManipulationScenariiDatabase"
    "Python Module", "omni.syntheticdata"

