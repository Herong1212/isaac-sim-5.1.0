.. _omni_graph_nodes_Distance3D_1:

.. _omni_graph_nodes_Distance3D:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Distance3D
    :keywords: lang-en omnigraph node math:operator threadsafe nodes distance3-d


Distance3D
==========

.. <description>

Computes the distance between two 3D points A and B, which is the length of the vector with start and end points A and B. If one input is an array and the other is a single point, the scalar will be broadcast to the size of the array (i.e. the output will be an array of the distances between each point in the input array and the second singular point).

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "A (*inputs:a*)", "``['pointd[3]', 'pointd[3][]', 'pointf[3]', 'pointf[3][]', 'pointh[3]', 'pointh[3][]']``", "The first 3D vector (or array of 3D vectors) specifying the point position(s) with which the distance computation will be performed.", "None"
    "B (*inputs:b*)", "``['pointd[3]', 'pointd[3][]', 'pointf[3]', 'pointf[3][]', 'pointh[3]', 'pointh[3][]']``", "The second 3D vector (or array of 3D vectors) specifying the point position(s) with which the distance computation will be performed.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Distance (*outputs:distance*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]']``", "The distance between the points specified by vector(s) ""A"" and vector(s) ""B"".", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Distance3D"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Distance3D"
    "Categories", "math:operator"
    "Generated Class Name", "OgnDistance3DDatabase"
    "Python Module", "omni.graph.nodes_core"

