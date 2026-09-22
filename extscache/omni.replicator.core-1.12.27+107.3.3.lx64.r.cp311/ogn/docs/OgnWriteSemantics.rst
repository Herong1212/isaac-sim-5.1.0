.. _omni_replicator_core_OgnWriteSemantics_3:

.. _omni_replicator_core_OgnWriteSemantics:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Semantics
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-write-semantics


Write Semantics
===============

.. <description>

This node writes the supplied semantics to specified prims.

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
    "Mode (*inputs:mode*)", "``token``", "Semantics modification mode. Select from [add, replace, clear]", "add"
    "", "Metadata", "*allowedTokens* = add,replace,clear", ""
    "Prims (*inputs:prims*)", "``target``", "Prim(s) to set semantics", "None"
    "Semantics (*inputs:semantics*)", "``token[]``", "Semantic key-value pairs separated by a colon (eg. class:car). DEPRECATED: Use the new semantics format instead.", "[]"
    "Semantics Values (*inputs:semantics_values*)", "``string``", "Dictionary of semantic key and values as a string. Eg. `""{'class': ['car', 'vehicle'], 'material': 'metal'}""`", ""


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

    "Unique ID", "omni.replicator.core.OgnWriteSemantics"
    "Version", "3"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Write Semantics"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnWriteSemanticsDatabase"
    "Python Module", "omni.replicator.core"

