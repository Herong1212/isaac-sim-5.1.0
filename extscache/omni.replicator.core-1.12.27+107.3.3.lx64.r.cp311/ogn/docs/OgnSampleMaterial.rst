.. _omni_replicator_core_OgnSampleMaterial_1:

.. _omni_replicator_core_OgnSampleMaterial:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Material Randomizer Node
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-sample-material


Material Randomizer Node
========================

.. <description>

Randomizes the material on the prims.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Material Paths (*inputs:materialPaths*)", "``token[]``", "material paths to be sampled", "[]"
    "Material Prim (*inputs:materialPrim*)", "``target``", "materials to be sampled", "None"
    "Max Cached Materials (*inputs:maxCachedMaterials*)", "``uint``", "Maximum number of cached generated materials. A higher value allows more cached manterials  to remain in the scene, reducing number of materials created per call at the expense of memory usage.  This value only applies to materials specified from MDL paths.", "0"
    "Prims (*inputs:prims*)", "``target``", "prim(s) to set material", "None"
    "Seed (*inputs:seed*)", "``int``", "Random Number Generator seed. A value of less than 0 will indicate using the global seed.", "-1"
    "Use Material Prim (*inputs:useMaterialPrim*)", "``bool``", "Use materialPrim, otherwise use materialPaths", "False"


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

    "Unique ID", "omni.replicator.core.OgnSampleMaterial"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Material Randomizer Node"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSampleMaterialDatabase"
    "Python Module", "omni.replicator.core"

