.. _omni_graph_TransformBundle_1:

.. _omni_graph_TransformBundle:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Transform Bundle
    :keywords: lang-en omnigraph node bundle graph transform-bundle


Transform Bundle
================

.. <description>

Applies a transform to an input bundle, storing the result in an output bundle

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input (*inputs:input*)", "``bundle``", "Input bundle containing the attributes to be transformed.", "None"
    "Transform (*inputs:transform*)", "``matrixd[4]``", "The transform to apply to the bundle", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Output (*outputs:output*)", "``bundle``", "Output bundle containing all of the transformed attributes", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.TransformBundle"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Transform Bundle"
    "Categories", "bundle"
    "Generated Class Name", "OgnTransformBundleDatabase"
    "Python Module", "omni.graph.nodes"

