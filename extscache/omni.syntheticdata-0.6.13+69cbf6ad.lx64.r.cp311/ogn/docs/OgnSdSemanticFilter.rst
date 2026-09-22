.. _omni_syntheticdata_SdSemanticFilter_1:

.. _omni_syntheticdata_SdSemanticFilter:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Semantic Filter
    :keywords: lang-en omnigraph node graph:simulation syntheticdata sd-semantic-filter


Sd Semantic Filter
==================

.. <description>

Synthetic Data node to declare a semantic filter.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Dependency", "None"
    "Hierarchical Labels (*inputs:hierarchicalLabels*)", "``bool``", "If true the filter consider all labels in the semantic hierarchy above the prims", "False"
    "Matching Labels (*inputs:matchingLabels*)", "``bool``", "If true output only the labels matching the filter (if false keep all labels of the matching prims)", "True"
    "Name (*inputs:name*)", "``token``", "Filter unique identifier [if empty, use the normalized predicate as an identifier]", ""
    "Predicate (*inputs:predicate*)", "``token``", "The semantic filter specification : a disjunctive normal form of semantic type and label", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Name (*outputs:name*)", "``token``", "The semantic filter name identifier", ""
    "Predicate (*outputs:predicate*)", "``token``", "The semantic filter predicate in normalized form", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdSemanticFilter"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:simulation"
    "Generated Class Name", "OgnSdSemanticFilterDatabase"
    "Python Module", "omni.syntheticdata"

