.. _omni_graph_nodes_GetPrimLocalToWorldTransform_2:

.. _omni_graph_nodes_GetPrimLocalToWorldTransform:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Prim Local to World Transform
    :keywords: lang-en omnigraph node sceneGraph threadsafe ReadOnly nodes get-prim-local-to-world-transform


Get Prim Local to World Transform
=================================

.. <description>

Given a path to a prim on the current USD stage, returns the transformation matrix. that transforms a vector from the local frame to the global frame 

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim (*inputs:prim*)", "``target``", "The prim used as the local coordinate system when 'Use Path' is false", "None"
    "Prim Path (*inputs:primPath*)", "``token``", "The path of the prim used as the local coordinate system when 'Use Path' is true", ""
    "Use Path (*inputs:usePath*)", "``bool``", "When true, the 'Prim Path' attribute is used as the path to the prim being read otherwise it will read the connection at the 'Prim' attribute", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Local Transform (*outputs:localToWorldTransform*)", "``matrixd[4]``", "The local to world transformation matrix for 'Prim'", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetPrimLocalToWorldTransform"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Prim Local to World Transform"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetPrimLocalToWorldTransformDatabase"
    "Python Module", "omni.graph.nodes"

