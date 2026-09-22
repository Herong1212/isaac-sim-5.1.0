.. _isaacsim_core_nodes_IsaacReadSystemTime_1:

.. _isaacsim_core_nodes_IsaacReadSystemTime:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Read System Time
    :keywords: lang-en omnigraph node isaacCore nodes isaac-read-system-time


Isaac Read System Time
======================

.. <description>

Holds values related to system timestamps

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.core.nodes<ext_isaacsim_core_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Reference Time Denominator (*inputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "0"
    "Reference Time Numerator (*inputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "System Time (*outputs:systemTime*)", "``double``", "Current system time in seconds", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.core.nodes.IsaacReadSystemTime"
    "Version", "1"
    "Extension", "isaacsim.core.nodes"
    "Icon", "ogn/icons/isaacsim.core.nodes.IsaacReadSystemTime.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Read System Time"
    "Categories", "isaacCore"
    "Generated Class Name", "OgnIsaacReadSystemTimeDatabase"
    "Python Module", "isaacsim.core.nodes"

