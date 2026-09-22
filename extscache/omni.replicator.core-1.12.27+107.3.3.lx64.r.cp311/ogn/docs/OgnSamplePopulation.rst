.. _omni_replicator_core_OgnSamplePopulation_2:

.. _omni_replicator_core_OgnSamplePopulation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Randomize Population
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-sample-population


Randomize Population
====================

.. <description>

This node generates a random sample of assets from a weighted list of assets.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Execution in", "None"
    "Mode (*inputs:mode*)", "``token``", "Sampling mode", "point_instance"
    "Paths (*inputs:paths*)", "``token[]``", "Paths from which to instantiate a population", "[]"
    "Population Name (*inputs:populationName*)", "``string``", "Name of population", ""
    "Population Path (*inputs:populationPath*)", "``target``", "Prim path to population prim", "None"
    "", "Metadata", "*hidden* = true", ""
    "Prims (*inputs:prims*)", "``target``", "Paths to prims in the scene, but provided in the form of target", "None"
    "Semantics (*inputs:semantics*)", "``token[]``", "Semantic key-value pairs separated by a colon (eg. class:car)", "[]"
    "Use Cache (*inputs:useCache*)", "``bool``", "Cache assets to speed up randomization", "True"
    "With Replacements (*inputs:withReplacements*)", "``bool``", "Use replacements to avoid duplicates", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Execution out", "None"
    "Prims (*outputs:prims*)", "``target``", "Sampled prims", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSamplePopulation"
    "Version", "2"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Randomize Population"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSamplePopulationDatabase"
    "Python Module", "omni.replicator.core"

