.. _omni_graph_nodes_RandomBoolean_1:

.. _omni_graph_nodes_RandomBoolean:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Random Boolean
    :keywords: lang-en omnigraph node math:operator threadsafe nodes random-boolean


Random Boolean
==============

.. <description>

Generates a random boolean value.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Is noise function (*inputs:isNoise*)", "``bool``", "Turn this node into a noise generator function For a given seed, it will then always output the same number(s)", "False"
    "", "Metadata", "*hidden* = true", ""
    "", "Metadata", "*literalOnly* = 1", ""
    "Seed (*inputs:seed*)", "``uint64``", "The seed of the random generator.", "None"
    "Use seed (*inputs:useSeed*)", "``bool``", "Use the custom seed instead of a random one", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"
    "Random Boolean (*outputs:random*)", "``bool``", "The random boolean value that was generated", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Gen (*state:gen*)", "``matrixd[3]``", "Random number generator internal state (abusing matrix3d because it is large enough)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RandomBoolean"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Random Boolean"
    "Categories", "math:operator"
    "Generated Class Name", "OgnRandomBooleanDatabase"
    "Python Module", "omni.graph.nodes_core"

