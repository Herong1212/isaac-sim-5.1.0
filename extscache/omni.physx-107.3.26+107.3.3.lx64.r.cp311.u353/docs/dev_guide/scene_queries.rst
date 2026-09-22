.. include:: ../../../../../../dev_guide/_links.rst

.. _scene_queries:

Scene Queries
=============

Scene queries allow you to gather information about the current scene state by using the same computations and data as what is used for simulating collisions. They only work *after* simulation has begun, because all data (including collider data) is not fully initialized until after that point.

Typically, they function by determining which colliders in the scene intersect or overlap with the provided input shape. They come in three overall variants: 

* :ref:`scene_query_overlap`
* :ref:`scene_query_raycast`
* :ref:`scene_query_sweep`
 
Each variant then exists in a number of subvariants that return a single result or multiple results.

.. _scene_query_overlap:

Overlap
-------
Overlap scene queries indicate which colliders overlap with the input geometry. There are unique function variants for box, sphere, shape (|UsdGPrim|_), and mesh (|UsdMesh|_).

Each of these come in subvariants that exclusively report whether any collider overlaps with the input geometry and with subvariants that provide detailed information on each detected overlap. For the latter, this is handled by passing an input callback function, in which you can process the information for each individually detected overlap (supplied as an :py:class:`OverlapHit <omni.physx.bindings._physx.OverlapHit>` object). With the callback function, you can also control whether to continue or stop the query at the specific overlap by setting the function return value. Note that the overlaps are returned in a random, unspecified order.

Example code:

.. code::

    from omni.physx import get_physx_scene_query_interface

    body_prim_found = False
    body_prim_path = "/World/BodyPrim"

    def report_overlap(overlapHit):
        if overlapHit.rigid_body == prim_path:
            global body_prim_found
            body_prim_found = True
            # Now that we have found our prim, return False to abort further search.
            return False
        return True

    origin = carb.Float3(0.0, 0.0, 50.0)
    extent = carb.Float3(100.0, 100.0, 100.0)
    rotation = carb.Float4(0.0, 0.0, 0.0, 1.0)

    get_physx_scene_query_interface().overlap_box(extent, origin, rotation, report_overlap, False)
    if body_prim_found:
        print("Prim overlapped box!")

.. _scene_query_raycast:

Raycast
-------
Raycast scene queries allow you to detect any colliders that intersect with the input ray. In addition to providing the same information as the Overlap queries, it also provides detailed data on the exact points of intersection, as part of the :py:class:`RaycastHit <omni.physx.bindings._physx.RaycastHit>` structure.

Example code:

.. code::

    from omni.physx import get_physx_scene_query_interface

    body_prim_found = False
    body_prim_path = "/World/BodyPrim"
    hit_position = carb.Float3(0.0, 0.0, 0.0)

    def report_raycast(raycastHit):
        if raycastHit.rigid_body == body_prim_path:
            global body_prim_found
            body_prim_found = True
            global hit_position
            hit_position = raycastHit.position
            # Now that we have found our prim, return False to abort further search.
            return False
        return True

    origin = carb.Float3(0.0, 1000.0, 0.0)
    direction = carb.Float3(0.0, -1.0, 0.0)
    distance = 1000.0
    rotation = carb.Float4(0.0, 0.0, 0.0, 1.0)

    get_physx_scene_query_interface().raycast_all(origin, direction, distance, report_raycast)
    if body_prim_found:
        print(f"Body prim was hit by ray at {hit_position}!")

Note that the raycast results are not necessarily returned in a sorted order. If you do need hits ordered according to the impact distance, you must post-process and sort the results in the client code. That being said, raycasting also features a subvariant that only returns information about the closest intersection in the form of a dictionary. Here is an example of using this variant:

.. code::

    from omni.physx import get_physx_scene_query_interface

    origin = carb.Float3(0.0, 1000.0, 0.0)
    direction = carb.Float3(0.0, -1.0, 0.0)
    distance = 1000.0
    rotation = carb.Float4(0.0, 0.0, 0.0, 1.0)

    hit_info = get_physx_scene_query_interface().raycast_closest(origin, direction, distance)
    if hit_info['hit']:
        print(f"{hit_info['rigidBody']} was hit by ray at {hit_info['position']}!")

The returned dictionary includes the following data (notice the minor variations from :py:class:`RaycastHit <omni.physx.bindings._physx.RaycastHit>` objects):

* ``hit`` - True if a hit was found, otherwise False.
* ``collision`` - Path string to the collider that was hit.
* ``rigidBody`` - Path string to the rigid body that was hit.
* ``protoIndex`` - ProtoIndex, filled for pointInstancers; otherwise, 0xFFFFFFFF.
* ``distance`` - Hit location distance.
* ``faceIndex`` - Hit location face index.
* ``material`` - Path string to the collider material that was hit.
* ``normal`` - Hit location normal.
* ``position`` - Hit location position.

.. _scene_query_sweep:

Sweep
-----
Sweep is almost identical to raycast, except that rather than just doing an intersection check against a line, it checks against the input geometry. The sweep scene query will then return intersection information corresponding to if you moved (or swept) the geometry along the direction you input.

There are variants for the following types of geometry:

* Sphere
* Cube
* Mesh
* Shape

Example code for sweeping a sphere shape:

.. code::

    from omni.physx import get_physx_scene_query_interface

    body_prim_found = False
    body_prim_path = "/World/BodyPrim"
    hit_position = carb.Float3(0.0, 0.0, 0.0)

    def report_sweep(sweepHit):
        if sweepHit.rigid_body == body_prim_path:
            global body_prim_found
            body_prim_found = True
            global hit_position
            hit_position = sweepHit.position
            # Now that we have found our prim, return False to abort further search.
            return False
        return True

    radius = 100.0
    origin = carb.Float3(0.0, 1000.0, 0.0)
    direction = carb.Float3(0.0, -1.0, 0.0)
    distance = 1000.0
    rotation = carb.Float4(0.0, 0.0, 0.0, 1.0)

    get_physx_scene_query_interface().sweep_sphere_all(radius, origin, direction, distance, report_sweep)
    if body_prim_found:
        print(f"Body was hit by sweep at {hit_position}!")

The return values of the sweep scene queries are identical to those of the corresponding :ref:`scene_query_raycast` queries, but returned in a :py:class:`SweepHit <omni.physx.bindings._physx.SweepHit>` structure.

