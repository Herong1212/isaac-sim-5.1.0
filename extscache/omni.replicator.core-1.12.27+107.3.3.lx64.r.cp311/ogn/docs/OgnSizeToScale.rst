.. _omni_replicator_core_OgnSizeToScale_1:

.. _omni_replicator_core_OgnSizeToScale:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Size to Scale
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-size-to-scale


Size to Scale
=============

.. <description>

Generate scales to make each prim fit a cube of specified size.

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
    "Maintain Aspect Ratio (*inputs:maintainAspectRatio*)", "``bool``", "Scale each axis by the same value to maintain aspect ratio", "True"
    "Num Samples (*inputs:numSamples*)", "``int``", "number of samples", "0"
    "Prims (*inputs:prims*)", "``target``", "Prim(s) to convert the scale to.", "None"
    "Size (*inputs:size*)", "``double[3][]``", "Desired size of the input prims.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"
    "Num Samples (*outputs:numSamples*)", "``int``", "number of samples", "None"
    "Samples (*outputs:samples*)", "``double[3][]``", "scale values of each prim in the world space", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSizeToScale"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Size to Scale"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSizeToScaleDatabase"
    "Python Module", "omni.replicator.core"

