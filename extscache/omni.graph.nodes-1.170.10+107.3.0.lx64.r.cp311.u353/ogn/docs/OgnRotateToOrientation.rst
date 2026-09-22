.. _omni_graph_nodes_RotateToOrientation_2:

.. _omni_graph_nodes_RotateToOrientation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Rotate To Orientation
    :keywords: lang-en omnigraph node sceneGraph threadsafe WriteOnly nodes rotate-to-orientation


Rotate To Orientation
=====================

.. <description>

Perform a smooth rotation maneuver, rotating a prim to a desired orientation given a speed and easing factor

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
    "Exponent (*inputs:exponent*)", "``float``", "The blend exponent, which is the degree of the ease curve  (1 = linear, 2 = quadratic, 3 = cubic, etc). ", "2.0"
    "Prim (*inputs:prim*)", "``target``", "The prim to be rotated", "None"
    "Prim Path (*inputs:primPath*)", "``path``", "The source prim to be transformed, used when 'usePath' is true", "None"
    "Speed (*inputs:speed*)", "``double``", "The peak speed of approach (Units / Second)", "1.0"
    "Stop (*inputs:stop*)", "``execution``", "Signal to the graph that this node is ready to stop the maneuver.", "None"
    "Target Orientation (*inputs:target*)", "``vectord[3]``", "The desired orientation as euler angles (XYZ) in local space", "[0.0, 0.0, 0.0]"
    "Use Path (*inputs:usePath*)", "``bool``", "When true, the 'primPath' attribute is used, otherwise it will read the connection at the 'prim' attribute", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Finished (*outputs:finished*)", "``execution``", "When the maneuver is completed, signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RotateToOrientation"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Rotate To Orientation"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnRotateToOrientationDatabase"
    "Python Module", "omni.graph.nodes"

