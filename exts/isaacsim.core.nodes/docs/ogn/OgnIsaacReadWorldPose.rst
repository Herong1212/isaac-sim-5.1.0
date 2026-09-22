.. _isaacsim_core_nodes_IsaacReadWorldPose_2:

.. _isaacsim_core_nodes_IsaacReadWorldPose:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Read World Pose
    :keywords: lang-en omnigraph node isaacCore nodes isaac-read-world-pose


Isaac Read World Pose
=====================

.. <description>

Isaac Sim node that reads world pose of an xform

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.core.nodes<ext_isaacsim_core_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim (*inputs:prim*)", "``target``", "Usd prim reference from which the fabric pose will be read", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Orientation (*outputs:orientation*)", "``quatd[4]``", "Orientation as a quaternion (IJKR)", "[0.0, 0.0, 0.0, 1.0]"
    "Scale (*outputs:scale*)", "``vectord[3]``", "Scale vector in meters", "[0.0, 0.0, 0.0]"
    "Translation (*outputs:translation*)", "``vectord[3]``", "Translation vector in meters", "[0.0, 0.0, 0.0]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.core.nodes.IsaacReadWorldPose"
    "Version", "2"
    "Extension", "isaacsim.core.nodes"
    "Icon", "ogn/icons/isaacsim.core.nodes.IsaacReadWorldPose.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Read World Pose"
    "Categories", "isaacCore"
    "Generated Class Name", "OgnIsaacReadWorldPoseDatabase"
    "Python Module", "isaacsim.core.nodes"

