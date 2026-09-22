.. _omni_graph_BundleToUSDA_1:

.. _omni_graph_BundleToUSDA:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Bundle to USDA Text
    :keywords: lang-en omnigraph node bundle threadsafe graph bundle-to-u-s-d-a


Bundle to USDA Text
===================

.. <description>

Outputs a represention of the content of a bundle as usda text

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*inputs:bundle*)", "``bundle``", "The bundle to convert to usda text.", "None"
    "Output Ancestors (*inputs:outputAncestors*)", "``bool``", "If usePath is true and this is also true, ancestor ""primPath"" entries will be output.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Output Values (*inputs:outputValues*)", "``bool``", "If true, the values of attributes will be output, else values will be omitted.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Use Prim Path (*inputs:usePrimPath*)", "``bool``", "Use the attribute named ""primPath"" for the usda prim path.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Use Prim Type (*inputs:usePrimType*)", "``bool``", "Use the attribute named ""primType"" for the usda prim type name.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Use Primvar Metadata (*inputs:usePrimvarMetadata*)", "``bool``", "Identify attributes representing metadata like the interpolation type for primvars, and include them as usda metadata in the output text.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Text (*outputs:text*)", "``token``", "Output usda text representing the bundle contents.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.BundleToUSDA"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Bundle to USDA Text"
    "Categories", "bundle"
    "Generated Class Name", "OgnBundleToUSDADatabase"
    "Python Module", "omni.graph.nodes"

