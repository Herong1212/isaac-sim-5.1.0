.. _omni_replicator_core_OgnSampleChoice_1:

.. _omni_replicator_core_OgnSampleChoice:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Multinomial Distribution
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-sample-choice


Multinomial Distribution
========================

.. <description>

This node generates samples from a list of strings/tokens.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Choices (*inputs:choices*)", "``any``", "The choices to be sampled", "None"
    "Num Samples (*inputs:numSamples*)", "``int``", "Number of samples to generate", "1"
    "Seed (*inputs:seed*)", "``int``", "Random Number Generator seed. A value of less than 0 will indicate using the global seed.", "-1"
    "Weights (*inputs:weights*)", "``float[]``", "The weights with which to sample", "[]"
    "With Replacements (*inputs:withReplacements*)", "``bool``", "Whether to avoid duplicates in sampling.", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Num Samples (*outputs:numSamples*)", "``int``", "Number of samples to generate", "1"
    "Samples (*outputs:samples*)", "``any``", "Sampled results", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSampleChoice"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Multinomial Distribution"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSampleChoiceDatabase"
    "Python Module", "omni.replicator.core"

