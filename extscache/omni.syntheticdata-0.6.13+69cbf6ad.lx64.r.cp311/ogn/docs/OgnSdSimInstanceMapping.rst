.. _omni_syntheticdata_SdSimInstanceMapping_1:

.. _omni_syntheticdata_SdSimInstanceMapping:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Sim Instance Mapping
    :keywords: lang-en omnigraph node graph:simulation,internal syntheticdata sd-sim-instance-mapping


Sd Sim Instance Mapping
=======================

.. <description>

Synthetic Data node to update and cache the instance mapping data

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Need Transform (*inputs:needTransform*)", "``bool``", "If true compute the semantic entities world and object transforms", "True"
    "Semantic Filter Predicate (*inputs:semanticFilterPredicate*)", "``token``", "The semantic filter predicate : a disjunctive normal form of semantic type and label", "*:*"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Semantic Filter Predicate (*outputs:semanticFilterPredicate*)", "``token``", "The semantic filter predicate in normalized form", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdSimInstanceMapping"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:simulation,internal"
    "Generated Class Name", "OgnSdSimInstanceMappingDatabase"
    "Python Module", "omni.syntheticdata"

