.. _omni_graph_examples_cpp_VersionedDeformer_2:

.. _omni_graph_examples_cpp_VersionedDeformer:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Versioned Deformer
    :keywords: lang-en omnigraph node examples threadsafe cpp versioned-deformer


Example Node: Versioned Deformer
================================

.. <description>

Test node to confirm version upgrading works. Performs a basic deformation on some points.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Points (*inputs:points*)", "``pointf[3][]``", "Set of points to be deformed", "[]"
    "Wavelength (*inputs:wavelength*)", "``float``", "Wavelength of sinusoidal deformer function", "50.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Points (*outputs:points*)", "``pointf[3][]``", "Set of deformed points", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.VersionedDeformer"
    "Version", "2"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Versioned Deformer"
    "Categories", "examples"
    "Generated Class Name", "OgnVersionedDeformerDatabase"
    "Python Module", "omni.graph.examples.cpp"

