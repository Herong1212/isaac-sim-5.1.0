.. _omni_graph_nodes_ToTarget_1:

.. _omni_graph_nodes_ToTarget:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: To Target
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes to-target


To Target
=========

.. <description>

Creates a target object using the input value as references in the scenegraph.
Target objects in OmniGraph are represented by USD Relationships. See https://openusd.org/release/glossary.html#usdglossary-relationship for more information.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``['path', 'string', 'token', 'token[]']``", "The value or values to add as scenegraph references in the output target object. If the input is an empty string, no references are added to the target object. If the input is not a valid scenegraph path, an empty path is added to the target object. If the input is a token[], each element is added to the target object as an scenegraph reference.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Target (*outputs:converted*)", "``target``", "A target output containing the input value as scenegraph references.", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*state:value*)", "``['path', 'string', 'token', 'token[]']``", "A cached value of the input used to determine if the output target needs to be updated.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ToTarget"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "To Target"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnToTargetDatabase"
    "Python Module", "omni.graph.nodes"

