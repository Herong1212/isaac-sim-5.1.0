.. _omni_graph_nodes_BooleanNor_2:

.. _omni_graph_nodes_BooleanNor:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Boolean NOR
    :keywords: lang-en omnigraph node math:condition threadsafe nodes boolean-nor


Boolean NOR
===========

.. <description>

Boolean NOR on two or more inputs. If the inputs are arrays, NOR operations will be performed pair-wise. The input sizes must match. If only one input is an array, the other input(s) will be applied individually to each element in the array. Returns an array of booleans if either input is an array, otherwise returning a boolean.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "A (*inputs:a*)", "``['bool', 'bool[]']``", "Input A: bool or bool array.", "None"
    "B (*inputs:b*)", "``['bool', 'bool[]']``", "Input B: bool or bool array.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``['bool', 'bool[]']``", "The result of the boolean NOR - an array of booleans if either input is an array, otherwise a boolean.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.BooleanNor"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Boolean NOR"
    "Categories", "math:condition"
    "Generated Class Name", "OgnNorDatabase"
    "Python Module", "omni.graph.nodes"

