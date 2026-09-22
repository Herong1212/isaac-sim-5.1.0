.. _omni_graph_nodes_RandomUnitVector_1:

.. _omni_graph_nodes_RandomUnitVector:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Random Unit Vector
    :keywords: lang-en omnigraph node math:operator threadsafe nodes random-unit-vector


Random Unit Vector
==================

.. <description>

Generates a random vector with uniform distribution on the unit sphere.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Is noise function (*inputs:isNoise*)", "``bool``", "Turn this node into a noise generator function. For a given seed, it will always output the same number(s).", "False"
    "", "Metadata", "*hidden* = true", ""
    "", "Metadata", "*literalOnly* = 1", ""
    "Seed (*inputs:seed*)", "``uint64``", "The input seed value for the random unit vector generator.", "None"
    "Use seed (*inputs:useSeed*)", "``bool``", "Use the custom seed instead of a random one.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"
    "Random Unit Vector (*outputs:random*)", "``vectorf[3]``", "The random unit vector that was generated.", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Gen (*state:gen*)", "``matrixd[3]``", "Random number generator internal state. Not an actual matrix, the structure was chosen because it was large enough to hold the internal data required for the computation.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RandomUnitVector"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Random Unit Vector"
    "Categories", "math:operator"
    "Generated Class Name", "OgnRandomUnitVectorDatabase"
    "Python Module", "omni.graph.nodes"

