.. _isaacsim_core_nodes_IsaacReadSimulationTimeAnnotator_1:

.. _isaacsim_core_nodes_IsaacReadSimulationTimeAnnotator:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Read Simulation Time Annotator
    :keywords: lang-en omnigraph node isaacCore nodes isaac-read-simulation-time-annotator


Isaac Read Simulation Time Annotator
====================================

.. <description>

Holds values related to simulation timestamps

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.core.nodes<ext_isaacsim_core_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Reference Time Denominator (*inputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "0"
    "Reference Time Numerator (*inputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "0"
    "Reset On Stop (*inputs:resetOnStop*)", "``bool``", "If True the simulation time will reset when stop is pressed, False means time increases monotonically", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "The output execution port", "None"
    "Simulation Time (*outputs:simulationTime*)", "``double``", "Current Simulation Time in Seconds", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.core.nodes.IsaacReadSimulationTimeAnnotator"
    "Version", "1"
    "Extension", "isaacsim.core.nodes"
    "Icon", "ogn/icons/isaacsim.core.nodes.IsaacReadSimulationTimeAnnotator.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Read Simulation Time Annotator"
    "Categories", "isaacCore"
    "Generated Class Name", "OgnIsaacReadSimulationTimeAnnotatorDatabase"
    "Python Module", "isaacsim.core.nodes"

