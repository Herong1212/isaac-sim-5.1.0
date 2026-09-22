.. _omni_graph_nodes_CrossProduct_1:

.. _omni_graph_nodes_CrossProduct:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cross Product
    :keywords: lang-en omnigraph node math:operator threadsafe nodes cross-product


Cross Product
=============

.. <description>

Compute the cross product of two (arrays of) 3D vectors of the same size. The cross product of two 3D vectors is a vector perpendicular to both inputs. If arrays of vectors are provided, then the cross product will be taken on an element-by-element basis between the two arrays (e.g. if two arrays with three vectors each are provided, the result will be another array containing three vectors where the first output vector is the result of taking the cross product between the first vectors in each input array, the second output vector is the result of taking the cross product between the second vectors in each input array, etc.). The inputs "A" and "B" must either both be 3D vectors, or both be arrays of 3D vectors with the same number of elements.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "A (*inputs:a*)", "``['vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The first 3D vector (or array of 3D vectors) in the cross product.", "None"
    "B (*inputs:b*)", "``['vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The second 3D vector (or array of 3D vectors) in the cross product.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Product (*outputs:product*)", "``['vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The resulting cross product between vector(s) ""A"" and vector(s) ""B"", which corresponds to the set of vectors perpendicular to both vector(s) ""A"" and vector(s) ""B"".", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.CrossProduct"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Cross Product"
    "Categories", "math:operator"
    "Generated Class Name", "OgnCrossProductDatabase"
    "Python Module", "omni.graph.nodes_core"

