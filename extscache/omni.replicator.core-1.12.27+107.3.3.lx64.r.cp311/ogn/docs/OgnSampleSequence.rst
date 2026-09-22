.. _omni_replicator_core_OgnSampleSequence_1:

.. _omni_replicator_core_OgnSampleSequence:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sequence Sampling
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-sample-sequence


Sequence Sampling
=================

.. <description>

This node generates samples by returning items from a sample set sequentially.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Items (*inputs:items*)", "``any``", "The ordered items to be sampled", "None"
    "Ordered (*inputs:ordered*)", "``bool``", "Whether to return the item in ordered", "True"
    "Seed (*inputs:seed*)", "``int``", "Random Number Generator seed. A value of less than 0 will indicate using the global seed.", "-1"
    "Stride (*inputs:stride*)", "``int``", "Number of values to pull from 'inputs:items' per sample.", "1"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Samples (*outputs:samples*)", "``any``", "Sampled results", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSampleSequence"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Sequence Sampling"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSampleSequenceDatabase"
    "Python Module", "omni.replicator.core"

