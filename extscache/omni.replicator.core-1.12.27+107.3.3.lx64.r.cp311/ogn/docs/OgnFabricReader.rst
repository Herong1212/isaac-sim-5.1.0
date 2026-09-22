.. _omni_replicator_core_FabricReader_1:

.. _omni_replicator_core_FabricReader:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Fabric Reader
    :keywords: lang-en omnigraph node Replicator core fabric-reader


Fabric Reader
=============

.. <description>

Annotator node to read arbitrary attributes from the fabric.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute (*inputs:attribute*)", "``token``", "Name of the attributes wanted.", ""
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Gpu (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations.", "0"
    "Prims (*inputs:prims*)", "``target``", "Array of prim paths where you want to extract attribute value from", "None"
    "Rp (*inputs:rp*)", "``uint64``", "Render results", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Data (*outputs:data*)", "``uchar[]``", "Output data", "[]"
    "Data Type (*outputs:dataType*)", "``token``", "Defines the data type", "uint8"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.FabricReader"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""primAttributeDS""]"
    "Categories", "Replicator"
    "__categoryDescriptions", "Replicator,Fabric Reader"
    "Generated Class Name", "OgnFabricReaderDatabase"
    "Python Module", "omni.replicator.core"

