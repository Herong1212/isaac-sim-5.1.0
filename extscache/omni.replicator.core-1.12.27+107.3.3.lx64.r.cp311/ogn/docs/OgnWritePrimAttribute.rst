.. _omni_replicator_core_OgnWritePrimAttribute_1:

.. _omni_replicator_core_OgnWritePrimAttribute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Prim Attribute
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-write-prim-attribute


Write Prim Attribute
====================

.. <description>

This node writes to a specified attribute on specified prims.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute (*inputs:attribute*)", "``string``", "Name of attribute that is to be written", ""
    "Attribute Type (*inputs:attributeType*)", "``string``", "Attribute type, optional if attribute already exists on prim", ""
    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Prims (*inputs:prims*)", "``target``", "Prim(s) to set attribute", "None"
    "Values (*inputs:values*)", "``any``", "Values to be assigned to the attribute", "None"


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

    "Unique ID", "omni.replicator.core.OgnWritePrimAttribute"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Write Prim Attribute"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnWritePrimAttributeDatabase"
    "Python Module", "omni.replicator.core"

