.. _omni_replicator_core_OgnSampleCombine_1:

.. _omni_replicator_core_OgnSampleCombine:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sample Combine
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-sample-combine


Sample Combine
==============

.. <description>

This node takes in any sample nodes' output or number as input, and output them.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Num Input Nodes (*inputs:numInputNodes*)", "``int``", "Number of input sample nodes", "0"
    "Num Samples (*inputs:numSamples*)", "``int``", "number of samples to generate", "1"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Samples (*outputs:samples*)", "``any``", "sampled results", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSampleCombine"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Sample Combine"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSampleCombineDatabase"
    "Python Module", "omni.replicator.core"

