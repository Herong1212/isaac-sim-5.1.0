Fabric Transforms with Fabric Scene Delegate and IFabricHierarchy
=================================================================

#####
About
#####

The Fabric Scene Delegate is the next-generation Omniverse
scene delegate for Hydra. It leverages the power and performance of 
Fabric for a faster, more flexible, streamlined rendering pipeline.

Fabric Scene Delegate uses Fabric as its data source for all
rendering operations. Starting in Kit 106, Fabric Scene Delegate also
leverages the new Connectivity API in Fabric to store and query information
about the scenegraph transform hierarchy via the new IFabricHierarchy interface.
This adds the following functionality to Fabric Scene Delegate:

* all Boundable prims in Fabric now participate in the transform
  hierarchy - changes to the local transform of a Fabric prim will affect
  the world transform of all descendants of that prim in Fabric
* prims authored exclusively in Fabric now participate in the transform
  hierarchy for the scene - previously, participating in the transform
  hierarchy (to the extent that OmniHydra supported it) required a corresponding prim
  on the USD stage

This document reviews the IFabricHierarchy interface and how the transform
hierarchy is maintained in Fabric.


############################
Fabric Transforms Previously
############################

Earlier iterations of the Omniverse rendering pipeline supported limited
Fabric-based transforms in the Hydra scene delegate. These required Fabric
prims to express their world transform on Fabric prims using these attributes:
* ``_worldPosition``
* ``_worldOrientation``
* ``_worldScale``

You can read more about this here: :doc:`Working with OmniHydra Transforms <omnihydra_xforms>`

Prims with these transform attributes authored in Fabric no longer participate
in any transform hierarchy. This often causes unexpected behavior when
manipulating transforms on ancestors or descendants of these prims.

OmniHydra also supports a ``_localMatrix`` attribute, which if it exists
in Fabric is substituted in the world transform calculation for a given
prim in place of the backing USD prim's computed local-to-parent transform.
However, this requires a valid backing USD hierarchy, and is superseded by
the existence of any of the ``_world*`` attributes.

Earlier versions of Fabric Scene Delegate also leveraged the
``_world*`` attributes to drive rendered prim transforms. These attribute values
could be updated directly in Fabric, and transform attribute changes to the
underlying USD stage are reflected in Fabric by the Fabric population
interface USD notice handler. Like with OmniHydra, these values in Fabric
represent an absolute world-space transform for the prim, and any changes
to these values in Fabric does not represent a hierarchical transform change.
There is no transform change that can be made in Fabric that will affect 
transform descendants of that prim in a Fabric Scene Delegate powered render.

In summary, support for hierarchical transform changes in Fabric has
been somewhat incomplete. IFabricHierarchy was created to add complete,
Fabric-native transform hierarchy support with Fabric Scene Delegate.

#################################################################
Fabric Transforms with Fabric Scene Delegate and IFabricHierarchy
#################################################################

Kit 106 adds a new interface for use with Fabric Scene Delegate
called IFabricHierarchy. This interface is not supported with OmniHydra.

New transform attributes
------------------------

When Fabric is populated from the USD Stage while Fabric Scene Delegate
is enabled, every Boundable prim has two new attributes created in Fabric:

* ``omni:fabric:localMatrix`` - the local-to-parent transform of
  the prim, as a ``GfMatrix4d``
* ``omni:fabric:worldMatrix`` - the local-to-world transform of
  the prim, as a ``GfMatrix4d``

``omni:fabric:localMatrix`` is the editable local transform of any
prim in Fabric. ``omni:fabric:worldMatrix`` is the computed, cached,
read-only (:ref:`*<ReadOnlyException>`) world transform of any prim in Fabric.
Changes to the
value of the ``omni:fabric:localMatrix`` attribute will cause the
``omni:fabric:worldMatrix`` attribute of that prim and all of its 
descendants to be recomputed before the next rendered frame.
Fabric Scene Delegate uses the ``omni:fabric:worldMatrix`` attribute
to set prim transform values in the Hydra rendering pipeline.

.. _ReadOnlyException:

(*) All attributes in Fabric are writeable, but as a computed value, 
``omni:fabric:worldMatrix`` is intended as a read-only attribute
outside of updates from the IFabricHierarchy implementation.

The IFabricHierarchy interface
------------------------------

IFabricHierarchy is a new interface defined in 
`includes/usdrt/hierarchy/IFabricHierarchy.h`

:cpp:struct:`usdrt::hierarchy::IFabricHierarchy`

IFabricHierarchy has a few simple APIs:

* ``getFabricHierarchy(fabricId, stageId)`` - Get the Fabric Hierarchy
  instance for a given FabricId and StageId
* ``getLocalXform(path)`` - Get the local-to-parent transform of a
  given prim - this just returns the value of the ``omni:fabric:localMatrix``
  attribute in Fabric.
* ``getWorldXform(path)`` - Get the local-to-world transform of a
  given prim - note that this value will be computed, so the value returned
  will always be correct. To query the cached value, ``omni:fabric:worldMatrix``
  can be read from Fabric directly.
* ``setLocalXform(path, matrix)`` - Update the ``omni:fabric:localMatrix``
  attribute value in Fabric with the new matrix value.
* ``setWorldXform(path, matrix)`` - Compute a new local-to-parent transform
  value such that the resulting computed local-to-world transform matches
  the given transform matrix, and set that value on ``omni:fabric:localMatrix``.
* ``updateWorldXforms()`` - Using Fabric change tracking, update all
  ``omni:fabric:worldMatrix`` values for any prim whose 
  ``omni:fabric:localMatrix`` value has changed, as well as all
  transform hierarchy descendants of those prims, since
  the last time ``updateWorldXforms()`` was called.

These APIs assume a few things about the data stored in Fabric.

* All Boundable prims have an ``omni:fabric:localMatrix`` and ``omni:fabric:worldMatrix``
  attribute authored. This is enforced for prims that originate from USD by the Fabric
  population interface that ships with Fabric Scene Delegate. For prims that are 
  created and only exist in Fabric, these attributes may need to be created
  directly or by using the RtXformable API:
  * :cpp:func:`usdrt::RtXformable::CreateFabricHierarchyLocalMatrixAttr`
  * :cpp:func:`usdrt::RtXformable::CreateFabricHierarchyWorldMatrixAttr`
* All prims in Fabric have been registered with the Fabric Connectivity API.
  This happens automatically for prims originating from USD and prims created
  with :cpp:func:`usdrt::UsdStage::DefinePrim`. The Connectivity API enables
  Fabric to establish a transform hierarchy for prims that only exist in Fabric.
* ``omni:fabric:localMatrix`` always represents the correct and most recent
  local transform for the prim. This is enforced for changes on the USD
  stage by the Fabric Scene Delegate USD Notice handler - any transform
  change on any prim in USD is immediately reflected as an update in Fabric
  on the ``omni:fabric:localMatrix`` attribute for the corresponding Fabric prim.

With IFabricHierarchy, the ``omni:fabric:worldMatrix`` attribute represents a cached
value of the world transform of the prim. That value is only updated when
``updateWorldXforms()`` is called on the interface - this allows changes to
``omni:fabric:localMatrix`` to happen quickly and at scale without the cost of
recomputing potentially thousands of ``omni:fabric:worldMatrix`` values that might
otherwise be incurred in order to reflect changes inherited through the transform
hierarchy every time a single prim transform is modified. Because of this, it is
possible that the value for any ``omni:fabric:worldMatrix`` attribute is stale
or out of date unless ``updateWorldXforms()`` has been called recently. Within
the Kit application, ``updateWorldXforms()`` is called immediately prior to
rendering every frame, so that Fabric Scene Delegate and the RTX renderer
pull the latest and correct world transform values directly from Fabric.

In order to discover the world transform of any prim at any time,
regardless of when ``updateWorldXforms()`` was last called,
``getWorldXform()`` will calculate the correct value using the
``omni:fabric:localMatrix`` values of the prim and its ancestors.

While ``updateWorldXforms()`` is always called just before rendering,
this method may be called any time that it is desirable to have the
``omni:fabric:worldMatrix`` attribute values in Fabric reflect
hierarchical transform changes from modifications to
``omni:fabric:localMatrix`` since the last time
``updateWorldXforms()`` was called, such as at the start of a simulation
step. If there have been no changes since the last call to
``updateWorldXforms()``, this call does nothing.

#############
Code Examples
#############

Getting and changing the local transform of a prim
--------------------------------------------------

The local transform of a prim can be modified by directly
changing the ``omni:fabric:localMatrix`` attribute in Fabric,
using USDRT APIs to change the value, or using the IFabricHierarchy interface.

Using UsdPrim and UsdAttribute APIs in USDRT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from usdrt import Gf, Sdf, Usd

    stage = Usd.Stage.Open(scene_path)
    prim = stage.GetPrimAtPath(prim_path)

    attr = prim.GetAttribute("omni:fabric:localMatrix")
    current_xform = attr.Get()

    new_xform = Gf.Matrix4d(1)
    new_xform.SetTranslateOnly((10, -15, 200))
    attr.Set(new_xform)


Using RtXformable API in USDRT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from usdrt import Gf, Sdf, Usd, Rt

    stage = Usd.Stage.Open(scene_path)
    prim = stage.GetPrimAtPath(prim_path)

    xformable = Rt.Xformable(prim)
    attr = xformable.GetFabricHierarchyLocalMatrixAttr()
    current_xform = attr.Get()

    new_xform = Gf.Matrix4d(1)
    new_xform.SetTranslateOnly((10, -15, 200))
    attr.Set(new_xform)


Using IFabricHierarchy Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from usdrt import Gf, Sdf, Usd, hierarchy

    stage = Usd.Stage.Open(scene_path)

    stage_id = stage.GetStageIdAsStageId()
    fabric_id = stage.GetFabricId()
    
    hier = hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
    
    current_xform = hier.get_local_xform(prim_path)

    new_xform = Gf.Matrix4d(1)
    new_xform.SetTranslateOnly((10, -15, 200))
    hier.set_local_xform(prim_path, new_xform)


Getting the last computed world transform value
-----------------------------------------------

The last computed world transform value for a prim can be retrieved
directly from Fabric using Fabric or USDRT APIs.

Using UsdPrim and UsdAttribute APIs in USDRT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from usdrt import Gf, Sdf, Usd

    stage = Usd.Stage.Open(scene_path)
    prim = stage.GetPrimAtPath(prim_path)

    attr = prim.GetAttribute("omni:fabric:worldMatrix")
    cached_world_xform = attr.Get()


Using RtXformable API in USDRT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from usdrt import Gf, Sdf, Usd, Rt

    stage = Usd.Stage.Open(scene_path)
    prim = stage.GetPrimAtPath(prim_path)

    xformable = Rt.Xformable(prim)
    attr = xformable.GetFabricHierarchyWorldMatrixAttr()
    cached_world_xform = attr.Get()

Getting the computed world transform of a prim
----------------------------------------------

The IFabricHierarchy interface can compute the correct world transform
of any prim, regardless of when the last call to ``updateWorldXforms()`` was made.

.. code:: python

    from usdrt import Gf, Sdf, Usd, hierarchy

    stage = Usd.Stage.Open(scene_path)

    stage_id = stage.GetStageIdAsStageId()
    fabric_id = stage.GetFabricId()
    
    hier = hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
    
    current_world_xform = hier.get_world_xform(prim_path)


Set a computed local transform from a world transform value
-----------------------------------------------------------

The IFabricHierarchy interface can compute a local transform
for a prim using the transforms of the ancestors of that prim,
such that the new value transforms the prim to the desired
transform in world space.

.. code:: python

    from usdrt import Gf, Sdf, Usd, hierarchy

    stage = Usd.Stage.Open(scene_path)

    stage_id = stage.GetStageIdAsStageId()
    fabric_id = stage.GetFabricId()
    
    hier = hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)

    result = hier.get_world_xform(path)
    expected = Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 90, 0, 0, 1)
    self.assertEqual(result, expected)

    hier.set_world_xform(path, Gf.Matrix4d(1))
    hier.update_world_xforms()

    local_result = hier.get_local_xform(path)
    local_expected = Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -90, 0, 0, 1)
    self.assertEqual(local_result, local_expected)


######################
Timesampled Transforms
######################

Fabric does not have native support for USD timesamples - the StageReaderWriter
is a snapshot of composed data on the stage at a single point in time.

Fabric Scene Delegate builds on top of Fabric by adding limited
timesample support. Fabric Scene Delegate's population utilities will listen
for changes to the timeline in Kit, and populate timesampled attributes into
Fabric at the time selected in the playback timeline, overwriting any previously
existing value in Fabric. This is the case for timesampled transforms as well.

IFabricHierarchy will update calculate and update ``omni:fabric:worldMatrix``
for transform hierarchy descendants of any prims
with timesampled transforms whose values are updated by Fabric Scene
Delegate population when ``updateWorldXforms()`` is called.


############################
Backward Compatibility Layer
############################

In order to support existing OmniHydra applications, a degree of
backwards compatibility has been added to help developers bridge
the gap to the new interface and transform attributes.

If these attributes exist and have been modified since
the last call to ``updateWorldXforms()``...

* ``_worldPosition``
* ``_worldOrientation``
* ``_worldScale``

...then their values will be used to calculate and set the
corresponding ``omni:fabric:localMatrix`` value for the prim at
the beginning of the next ``updateWorldXforms()`` call.

Similarly, if a ``_localMatrix`` attribute exists and was modified
since the last call to ``updateWorldXforms()``, then its value will be
copied directly to ``omni:fabric:localMatrix`` for the prim.

This fallback behavior adds calculation overhead and will be
more expensive than writing ``omni:fabric:localMatrix`` directly.
It is recommended that developers update to the new interface for
the best performance with transforms in Fabric.

#################################################
Behavior when writing ``omni:fabric:worldMatrix``
#################################################

While ``omni:fabric:worldMatrix`` is not intended to be modified
outside the IFabricHierarchy implementation, Fabric does not
provide attribute permissions or other concepts, so it is
possible to write the ``omni:fabric:worldMatrix`` value at any time
using USDRT or Fabric APIs. In the event that this happens, it will
be inferred that this is a new target world transform for the prim,
and IFabricHierarchy will compute a new ``omni:fabric:localMatrix``
value at the start of the next ``updateWorldXforms()`` call. In
addition to being expensive to compute, it is also potentially
incorrect in the event that several of these attributes were
modified in a hierarchically dependent way - there is no way to
unravel an intended order of operations for calculating the new
``omni:fabric:localMatrix`` attributes.
