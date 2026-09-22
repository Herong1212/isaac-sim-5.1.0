.. _omni_replicator_core_OgnPrimPaths_1:

.. _omni_replicator_core_OgnPrimPaths:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: PrimPaths
    :keywords: lang-en omnigraph node Replicator:Annotators core ogn-prim-paths


PrimPaths
=========

.. <description>

Return Prim Path Tokens from InstancePrimPathsPtr

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Num Semantics (*inputs:numSemantics*)", "``uint``", "Number of instances prim in the instance arrays", "0"
    "Semantic Prim Path Ptr (*inputs:semanticPrimPathPtr*)", "``uint64``", "Array pointer of numInstances uint64_t containing the prim path tokens for every instance prims", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Prim Paths (*outputs:primPaths*)", "``token[]``", "Prim paths corresponding to each bounding box.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnPrimPaths"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "PrimPaths"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnPrimPathsDatabase"
    "Python Module", "omni.replicator.core"

