.. _omni_graph_nodes_BuildString_2:

.. _omni_graph_nodes_BuildString:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Append String
    :keywords: lang-en omnigraph node function threadsafe nodes build-string


Append String
=============

.. <description>

Creates a new token or string by concatenating the inputs. token[] inputs will be appended element-wise.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "A (*inputs:a*)", "``['string', 'token', 'token[]']``", "The string(s) to be appended to.  This input determines the output type.", "None"
    "B (*inputs:b*)", "``['string', 'token', 'token[]']``", "The string to be appended.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*outputs:value*)", "``['string', 'token', 'token[]']``", "The new string(s).", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.BuildString"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Append String"
    "Categories", "function"
    "Generated Class Name", "OgnBuildStringDatabase"
    "Python Module", "omni.graph.nodes"

