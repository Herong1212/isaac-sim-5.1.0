.. _omni_genproc_core_Raycast_1:

.. _omni_genproc_core_Raycast:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Raycast
    :keywords: lang-en omnigraph node spatial core raycast


Raycast
=======

.. <description>

Perform intersection tests against a bundle of obstacle prims. The intersection test can be a raycast or a sweep operation,  and the source of the test can be a prim from a bundle or a point and direction. If 'Source Type' is 'Point and Direction' and 'Query Type' is 'Raycast', then a ray is created from the input point and direction  and cast against the meshes in the obstacles bundle.  If 'Source Type' is 'Point and Direction' and 'Query Type' is 'Sweep', then a sphere with 'radius' is swept out from the input point and direction  If 'Source Type' is 'Bundle Prim' and 'Query Type' is 'Raycast', then for each prim in the input bundle a ray is generated from the origin and z-axis  of the prim transformed into world space.  If 'Source Type' is 'Bundle Prim' and 'Query Type' is 'Sweep', then for each mesh prim in the input bundle a bounding sphere is fit to the prim's  points and that sphere is used for the sweep. 

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Closest Hit Only (*inputs:closestHitOnly*)", "``bool``", "If true, only the closest hit will be reported. Otherwise multiple ray intersections may be returned.  (Note that this value only matters for raycast queries. Sweep queries will never return more than one hit.)", "True"
    "Direction (*inputs:direction*)", "``float[3]``", "Direction of raycast.  When 'Point and Direction' is specified as the source type, this direction is used in world space.  When 'Bundle Prim' is the source type, this direction is considered to be in the prim's local space  (in other words, the prim's transform is applied to this direction before the raycast).", "[0, 0, 1]"
    "Obstacles Bundle (*inputs:obstacleBundle*)", "``bundle``", "Bundle containing intersection geometry for raycasting / sweeping", "None"
    "Point (*inputs:point*)", "``float[3]``", "Origin of raycast (when 'Point and Direction' is specified as the source type)", "[0, 0, 0]"
    "Prim in Bundle (*inputs:primBundle*)", "``bundle``", "Bundle containing prim data for use in raycast / sweep (when 'Bundle Prim' is specified as the source type)", "None"
    "Query Type (*inputs:queryType*)", "``int``", "0 = raycast, 1 = sweep", "0"
    "Radius (*inputs:radius*)", "``float``", "Radius of sphere used in sweep query (when 'Point and Direction' is specified as the source type)", "1.0"
    "Range (*inputs:range*)", "``float``", "If positive, this value specifies the maximum distance considered for intersection tests.  otherwise 'infinite' distance is used for intersection tests.", "0.0"
    "Source Type (*inputs:sourceType*)", "``int``", "0 = bundle prim, 1 = point and direction", "0"
    "Verbose (*inputs:verbose*)", "``bool``", "Print intersection information.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Distances (*outputs:distances*)", "``float[]``", "Distances to intersection points", "None"
    "Face Indices (*outputs:faceIndices*)", "``int[]``", "Face indices of intersection points", "None"
    "Normals (*outputs:normals*)", "``float[3][]``", "Surface normals of intersection points", "None"
    "Paths (*outputs:paths*)", "``token[]``", "Paths to prims hit by raycast / sweep", "None"
    "Points (*outputs:points*)", "``float[3][]``", "One or more (in the case of raycasting from multiple source prims or with closestHitOnly enabled) intersection points.", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Closest Hit Only (*state:prevClosestHitOnly*)", "``bool``", "Previous closestHitOnly value for recompute test", "None"
    "Prev Direction (*state:prevDirection*)", "``float[3]``", "Previous direction value for recompute test", "None"
    "Prev Point (*state:prevPoint*)", "``float[3]``", "Previous point value for recompute test", "None"
    "Prev Query Type (*state:prevQueryType*)", "``int``", "Previous queryType value for recompute test", "None"
    "Prev Radius (*state:prevRadius*)", "``float``", "Previous radius value for recompute test", "None"
    "Prev Range (*state:prevRange*)", "``float``", "Previous range value for recompute test", "None"
    "Prev Source Type (*state:prevSourceType*)", "``int``", "Previous sourceType value for recompute test", "None"
    "Prev Verbose (*state:prevVerbose*)", "``bool``", "Previous verbose value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.Raycast"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Raycast"
    "__tokens", "{""bboxMinCorner"": ""bboxMinCorner"", ""bboxMaxCorner"": ""bboxMaxCorner"", ""bboxTransform"": ""bboxTransform""}"
    "Categories", "spatial"
    "Generated Class Name", "OgnRaycastDatabase"
    "Python Module", "omni.genproc.core"

