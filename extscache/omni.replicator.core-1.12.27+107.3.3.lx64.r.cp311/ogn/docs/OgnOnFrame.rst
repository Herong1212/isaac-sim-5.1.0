.. _omni_replicator_core_OgnOnFrame_2:

.. _omni_replicator_core_OgnOnFrame:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: On Frame
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-on-frame


On Frame
========

.. <description>

Triggers when there is a new frame available for the given viewport. Note that the graph will run asynchronously to the new frame event

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Interval (*inputs:interval*)", "``uint``", "Frame interval between executions", "1"
    "Max Execs (*inputs:maxExecs*)", "``uint``", "Number of frames triggered before stopping. If 0, continue indefinitely.", "0"
    "Render Product (*inputs:renderProduct*)", "``token``", "Name of the render product, or empty for the default render product", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Rt Subframes (*inputs:rtSubframes*)", "``uint64``", "Determines how many subframes to render in RealTime render mode on each trigger to reduce artifacts caused by sudden scene changes.", "1"
    "Run (*inputs:run*)", "``bool``", "Run", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Counts (*outputs:execCounts*)", "``int``", "The number of times the trigger has executed.", "None"
    "Exec Out (*outputs:execOut*)", "``execution``", "Output Execution", "None"
    "Frame Number (*outputs:frameNumber*)", "``int``", "Deprecated, unused", "None"
    "Reference Time Denominator (*outputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "None"
    "Reference Time Numerator (*outputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnOnFrame"
    "Version", "2"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "On Frame"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnOnFrameDatabase"
    "Python Module", "omni.replicator.core"

