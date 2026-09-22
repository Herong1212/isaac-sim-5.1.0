.. _omni_graph_nodes_TranslateToLocation_2:

.. _omni_graph_nodes_TranslateToLocation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Translate To Location
    :keywords: lang-en omnigraph node sceneGraph threadsafe WriteOnly nodes translate-to-location


Translate To Location
=====================

.. <description>

Perform a smooth translation maneuver, translating a prim to a desired point given a speed and easing factor

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Execute In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Ease Exponent (*inputs:exponent*)", "``float``", "The blend exponent, which is the degree of the ease curve  (1 = linear, 2 = quadratic, 3 = cubic, etc). ", "2.0"
    "Prim (*inputs:prim*)", "``target``", "The prim to be translated", "None"
    "Prim Path (*inputs:primPath*)", "``path``", "The source prim to be transformed, used when 'usePath' is true", "None"
    "Speed (*inputs:speed*)", "``double``", "The peak speed of approach (Units / Second)", "1.0"
    "Stop (*inputs:stop*)", "``execution``", "Signal to the graph that this node is ready to stop the maneuver.", "None"
    "Target Location (*inputs:target*)", "``vectord[3]``", "The desired local position", "[0.0, 0.0, 0.0]"
    "Use Path (*inputs:usePath*)", "``bool``", "When true, the 'Prim Path' attribute is used, otherwise it will read the connection at the 'Prim' attribute", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Finished (*outputs:finished*)", "``execution``", "When the maneuver is completed, Signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.TranslateToLocation"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Translate To Location"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnTranslateToLocationDatabase"
    "Python Module", "omni.graph.nodes"

