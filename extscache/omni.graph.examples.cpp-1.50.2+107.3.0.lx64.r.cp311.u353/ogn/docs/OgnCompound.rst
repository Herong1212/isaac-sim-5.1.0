.. _omni_graph_examples_cpp_Compound_1:

.. _omni_graph_examples_cpp_Compound:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Compound
    :keywords: lang-en omnigraph node examples threadsafe cpp compound


Example Node: Compound
======================

.. <description>

Encapsulation of one more other nodes into a single node entity. The compound node doesn't have any functionality of its own, it is merely a wrapper for a set of nodes that perform a complex task. It presents a more limited set of input and output attributes than the union of the contained nodes to make it seem as though a single node is performing a higher level function. For example a compound node could present inputs a, b, and c, and outputs root1 and root2 at the compound boundary, wiring up simple math nodes square, squareRoot, add, subtract, times, and divided_by in a simple way that calculates quadratic roots. (root1 = divide(add(b, square_root(subtract(square(b), times(4, times(a, c))))))) (root2 = divide(subtract(b, square_root(subtract(square(b), times(4, times(a, c)))))))

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.Compound"
    "Version", "1"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Compound"
    "Categories", "examples"
    "Generated Class Name", "OgnCompoundDatabase"
    "Python Module", "omni.graph.examples.cpp"

