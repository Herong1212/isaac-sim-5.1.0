.. _omni_graph_nodes_Modulo_1:

.. _omni_graph_nodes_Modulo:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Modulo
    :keywords: lang-en omnigraph node math:operator threadsafe nodes modulo


Modulo
======

.. <description>

Computes the modulo of integer inputs ("A" % "B"), which is the remainder of "A" / "B". If "B" is zero, then the final result is zero. Note that truncated division is utilized to determine the remainder behind-the-hood, i.e. "Result" = "A" - "B" * trunc("A" / "B"), where the trunc operation simply says to round the resultant of "A" / "B" towards zero (i.e. down if positive, and up if negative). As a consequence of this, if "A" > 0 and "B" < 0, then "Result" > 0, but if "A" < 0 and "B" > 0, then "Result" < 0.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "A (*inputs:a*)", "``['int', 'int64', 'uchar', 'uint', 'uint64']``", "The dividend of the (""A"" % ""B"") operation, i.e. ""A"".", "None"
    "B (*inputs:b*)", "``['int', 'int64', 'uchar', 'uint', 'uint64']``", "The divisor of the (""A"" % ""B"") operation, i.e. ""B"". If ""B"" is zero, then the final result will be zero.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``['int', 'int64', 'uchar', 'uint', 'uint64']``", "Modulo (""A"" % ""B""), i.e. the remainder of the division operation ""A"" / ""B"".", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Modulo"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Modulo"
    "Categories", "math:operator"
    "Generated Class Name", "OgnModuloDatabase"
    "Python Module", "omni.graph.nodes"

