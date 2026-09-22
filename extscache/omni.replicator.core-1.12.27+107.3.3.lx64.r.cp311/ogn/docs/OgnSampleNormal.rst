.. _omni_replicator_core_OgnSampleNormal_1:

.. _omni_replicator_core_OgnSampleNormal:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Normal Distribution
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-sample-normal


Normal Distribution
===================

.. <description>

This node generates samples from a normal distribution.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Mean (*inputs:mean*)", "``float[]``", "the mean of the normal distribution", "[]"
    "Num Samples (*inputs:numSamples*)", "``int``", "number of samples to generate", "1"
    "Output Type (*inputs:outputType*)", "``string``", "The helper attribute to resolve output's type", ""
    "Seed (*inputs:seed*)", "``int``", "Random Number Generator seed. A value of less than 0 will indicate using the global seed.", "-1"
    "Std (*inputs:std*)", "``float[]``", "the standard deviation of the normal distribution", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Num Samples (*outputs:numSamples*)", "``int``", "number of samples to generate", "1"
    "Samples (*outputs:samples*)", "``any``", "sampled results", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSampleNormal"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Normal Distribution"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSampleNormalDatabase"
    "Python Module", "omni.replicator.core"

