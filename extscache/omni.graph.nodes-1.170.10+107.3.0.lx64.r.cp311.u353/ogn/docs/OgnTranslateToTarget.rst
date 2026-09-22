.. _omni_graph_nodes_TranslateToTarget_2:

.. _omni_graph_nodes_TranslateToTarget:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Translate To Target
    :keywords: lang-en omnigraph node sceneGraph threadsafe WriteOnly nodes translate-to-target


Translate To Target
===================

.. <description>

This node smoothly translates a prim object to a target prim object given a speed and easing factor.  At the end of the maneuver, the source prim will have the same translation as the target prim

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
    "Source Prim (*inputs:sourcePrim*)", "``target``", "The source prim to be transformed", "None"
    "Source Prim Path (*inputs:sourcePrimPath*)", "``path``", "The source prim to be transformed, used when 'useSourcePath' is true", "None"
    "Speed (*inputs:speed*)", "``double``", "The peak speed of approach (Units / Second)", "1.0"
    "Stop (*inputs:stop*)", "``execution``", "Signal to the graph that this node is ready to stop the maneuver.", "None"
    "Target Prim (*inputs:targetPrim*)", "``target``", "The destination prim. The target's translation will be matched by the sourcePrim", "None"
    "Target Prim Path (*inputs:targetPrimPath*)", "``path``", "The destination prim. The target's translation will be matched by the sourcePrim, used when 'useTargetPath' is true", "None"
    "Use Source Path (*inputs:useSourcePath*)", "``bool``", "When true, the 'sourcePrimPath' attribute is used, otherwise it will read the connection at the 'sourcePrim' attribute", "False"
    "Use Target Path (*inputs:useTargetPath*)", "``bool``", "When true, the 'targetPrimPath' attribute is used, otherwise it will read the connection at the 'targetPrim' attribute", "False"


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

    "Unique ID", "omni.graph.nodes.TranslateToTarget"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Translate To Target"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnTranslateToTargetDatabase"
    "Python Module", "omni.graph.nodes"

