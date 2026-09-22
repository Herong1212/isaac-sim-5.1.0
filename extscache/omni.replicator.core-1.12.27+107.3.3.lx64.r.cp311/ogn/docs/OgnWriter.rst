.. _omni_replicator_core_OgnWriter_2:

.. _omni_replicator_core_OgnWriter:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Writer
    :keywords: lang-en omnigraph node Replicator:Annotators compute-on-request core ogn-writer


Writer
======

.. <description>

This node counts the number of times it is computed since being reset

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Data Structure (*inputs:dataStructure*)", "``token``", "Specify the type of data structure to produce.", "legacy"
    "", "Metadata", "*allowedTokens* = legacy,renderProduct,annotator", ""
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Reference Time Denominator (*inputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "0"
    "Reference Time Numerator (*inputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "0"
    "Reset (*inputs:renderProducts*)", "``token[]``", "Reset the internal counter", "[]"
    "Writer Id (*inputs:writerId*)", "``string``", "Unique id of writer", ""
    "Writer Name (*inputs:writerName*)", "``token``", "Name of writer", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnWriter"
    "Version", "2"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Writer"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnWriterDatabase"
    "Python Module", "omni.replicator.core"

