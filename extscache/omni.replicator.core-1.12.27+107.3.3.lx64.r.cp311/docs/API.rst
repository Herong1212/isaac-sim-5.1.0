PYTHON API
###########

Core Functions
===============

.. automodule:: omni.replicator.core
    :platform: Windows-x86_64, Linux-x86_64
    :members: new_layer, set_global_seed, get_global_seed, open_stage


Create
======

``create`` methods are helpers to put objects onto the USD stage.

.. module:: omni.replicator.core.create
    :platform: Windows-x86_64, Linux-x86_64

    .. autofunction:: render_product
    .. autofunction:: register


Lights
------
    .. autofunction:: light

Misc
----
    .. autofunction:: group

Cameras
--------
    .. autofunction:: camera
    .. autofunction:: stereo_camera

Materials
-----------
    .. autofunction:: material_omnipbr
    .. autofunction:: projection_material
    .. autofunction:: mdl_from_json

Shapes
-------
    .. autofunction:: cone
    .. autofunction:: cube
    .. autofunction:: cylinder
    .. autofunction:: disk
    .. autofunction:: plane
    .. autofunction:: sphere
    .. autofunction:: torus
    .. autofunction:: xform

USD
----
    .. autofunction:: from_dir
    .. autofunction:: from_usd


Get
===

``get`` methods are helpers to get objects from the USD stage, either by path or by semantic label.

``get.prims`` is very broad with its regex matching on the USD stage, so individual helper methods are provided
to narrow the search field to differnt USD types (mesh, light, etc.)

.. automodule:: omni.replicator.core.get
    :platform: Windows-x86_64, Linux-x86_64

    .. autofunction:: camera
    .. autofunction:: curve
    .. autofunction:: geomsubset
    .. autofunction:: graph
    .. autofunction:: light
    .. autofunction:: listener
    .. autofunction:: material
    .. autofunction:: mesh
    .. autofunction:: physics
    .. autofunction:: prim_at_path
    .. autofunction:: prims
    .. autofunction:: renderproduct
    .. autofunction:: rendervar
    .. autofunction:: scope
    .. autofunction:: shader
    .. autofunction:: shape
    .. autofunction:: skelanimation
    .. autofunction:: skeleton
    .. autofunction:: sound
    .. autofunction:: xform
    .. autofunction:: register

Distribution
============

``distribution`` methods are helpers set a range of values to simulate complex behavior.

.. automodule:: omni.replicator.core.distribution
    :platform: Windows-x86_64, Linux-x86_64

    .. autofunction:: choice
    .. autofunction:: combine
    .. autofunction:: log_uniform
    .. autofunction:: normal
    .. autofunction:: sequence
    .. autofunction:: uniform
    .. autofunction:: register


Modify
======

``modify`` methods are helpers to get change objects on the USD stage.

.. automodule:: omni.replicator.core.modify
    :platform: Windows-x86_64, Linux-x86_64
    :show-inheritance:

    .. autofunction:: animation
    .. autofunction:: attribute
    .. autofunction:: material
    .. autofunction:: pose
    .. autofunction:: pose_camera_relative
    .. autofunction:: pose_orbit
    .. autofunction:: projection_material
    .. autofunction:: semantics
    .. autofunction:: variant
    .. autofunction:: visibility
    .. autofunction:: register

Time
-----
    .. autofunction:: time
    .. autofunction:: timeline


Randomizer
==========

.. automodule:: omni.replicator.core.randomizer
    :platform: Windows-x86_64, Linux-x86_64
    :show-inheritance:

    .. autofunction:: color
    .. autofunction:: instantiate
    .. autofunction:: materials
    .. autofunction:: rotation
    .. autofunction:: scatter_2d
    .. autofunction:: scatter_3d
    .. autofunction:: texture
    .. autofunction:: register

Physics
=======

.. automodule:: omni.replicator.core.physics
    :platform: Windows-x86_64, Linux-x86_64
    :show-inheritance:

    .. autofunction:: collider
    .. autofunction:: drive_properties
    .. autofunction:: mass
    .. autofunction:: physics_material
    .. autofunction:: rigid_body


Annotators
==========

.. module:: omni.replicator.core.annotators
    :platform: Windows-x86_64, Linux-x86_64
    :no-index:

    .. autofunction:: get
    .. autofunction:: get_augmentation
    .. autofunction:: get_registered_annotators
    .. autofunction:: register
    .. autofunction:: register_augmentation
    .. autofunction:: unregister_augmentation

.. autoclass:: Annotator
    :members:

.. autoclass:: AnnotatorRegistry
    :members:

Default Annotators
-------------------
.. include:: annotators_details.rst

Annotator Exceptions
-----------------------
.. autoexception:: AnnotatorError
    :show-inheritance:

.. autoexception:: AnnotatorRegistryError
    :show-inheritance:

.. autoexception:: AugmentationError
    :show-inheritance:

Annotator Utils
-------------------
.. automodule:: omni.replicator.core.utils.annotator_utils
    :platform: Windows-x86_64, Linux-x86_64
    :members:

Augmentations
===============
.. automodule:: omni.replicator.core.annotators
    :platform: Windows-x86_64, Linux-x86_64

    .. autofunction:: augment
    .. autofunction:: augment_compose

    .. autoclass:: Augmentation
        :members:

Default Augmentations
---------------------
.. include:: augmentations_docs.rst

Writers
==========

``Writers`` are how to get data from Omniverse Replicator out to disk.

.. automodule:: omni.replicator.core.writers
    :platform: Windows-x86_64, Linux-x86_64
    :members: get, register_node_writer, register_writer, unregister_writer

.. autoclass:: WriterRegistry
    :members:

Writer Base Class
-----------------
.. autoclass:: Writer
    :members:
    :no-undoc-members:

Default Writers
-----------------
.. module:: omni.replicator.core.writers_default

BasicWriter
^^^^^^^^^^^^
.. autoclass:: BasicWriter

FPSWriter
^^^^^^^^^^
.. autoclass:: FPSWriter

KittiWriter
^^^^^^^^^^^^
.. autoclass:: KittiWriter

COCOWriter
^^^^^^^^^^^^
.. autoclass:: CocoWriter

Writer Utils
---------------
.. automodule:: omni.replicator.core.writers_default.tools
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :show-inheritance:
    :noindex:

Triggers
========

.. automodule:: omni.replicator.core.trigger
    :platform: Windows-x86_64, Linux-x86_64
    :show-inheritance:

    .. autofunction:: on_frame
    .. autofunction:: on_key_press
    .. autofunction:: on_time
    .. autofunction:: on_custom_event
    .. autofunction:: on_condition
    .. autofunction:: register


Orchestrator
============

.. automodule:: omni.replicator.core.orchestrator
    :platform: Windows-x86_64, Linux-x86_64

Simulation Control
--------------------
    .. autofunction:: pause
    .. autofunction:: preview
    .. autofunction:: resume
    .. autofunction:: run
    .. autofunction:: run_until_complete
    .. autofunction:: step
    .. autofunction:: stop
    .. autofunction:: wait_until_complete

Simulation Control (async)
----------------------------
    .. autofunction:: preview_async
    .. autofunction:: run_async
    .. autofunction:: run_until_complete_async
    .. autofunction:: step_async
    .. autofunction:: wait_until_complete_async

Orchestrator info
-------------------
    .. autofunction:: get_is_paused
    .. autofunction:: get_is_started
    .. autofunction:: get_is_stopped
    .. autofunction:: get_sim_times_to_write
    .. autofunction:: get_status

Other
--------
    .. autofunction:: register_status_callback
    .. autofunction:: set_capture_on_play
    .. autofunction:: set_minimum_next_rt_subframes
    .. autofunction:: set_next_rt_subframes

    .. autoexception:: OrchestratorError

Functional
==========
.. automodule:: omni.replicator.core.functional
    :platform: Windows-x86_64, Linux-x86_64

Create
------
.. automodule:: omni.replicator.core.functional.create
    :members:

Create Batch
------------
.. automodule:: omni.replicator.core.functional.create_batch
    :members:

I/O
---
.. automodule:: omni.replicator.core.functional.io_functions
    :members:

Modify
------
.. automodule:: omni.replicator.core.functional.modify
    :members:

Physics
-------
.. automodule:: omni.replicator.core.functional.physics
    :members:

Randomizer
----------
.. automodule:: omni.replicator.core.functional.randomizer
    :members:

Backends
========

Backend Registry
----------------

.. automodule:: omni.replicator.core.backends.registry
    :members: get, register, unregister

.. autoclass:: omni.replicator.core.backends.BackendRegistry
    :members:


IO Queue
----------------

.. automodule:: omni.replicator.core.backends.io_queue
    :members:

.. automodule:: omni.replicator.core.backends.sequential
    :members:

Default Backends
----------------

.. autoclass:: omni.replicator.core.backends.BaseBackend
    :members:

.. autoclass:: omni.replicator.core.backends.DiskBackend
    :members:

.. autoclass:: omni.replicator.core.backends.S3Backend
    :members:

.. autoclass:: omni.replicator.core.backends.BackendGroup
    :members:


Replicator Utils
=================

.. module:: omni.replicator.core.utils
    :platform: Windows-x86_64, Linux-x86_64

    .. autofunction:: compute_aabb
    .. autofunction:: create_node
    .. autofunction:: find_prims
    .. autofunction:: get_files_group
    .. autofunction:: get_graph
    .. autofunction:: get_node_targets
    .. autofunction:: get_non_xform_prims
    .. autofunction:: get_prim_variant_values
    .. autofunction:: get_prims_from_paths
    .. autofunction:: get_replicator_graph_exists
    .. autofunction:: get_usd_files
    .. autofunction:: read_prim_transform
    .. autofunction:: send_og_event
    .. autofunction:: set_target_prims

Settings
========

.. automodule:: omni.replicator.core.settings
    :platform: Windows-x86_64, Linux-x86_64
    :show-inheritance:

    .. autofunction:: carb_settings
    .. autofunction:: set_render_pathtraced
    .. autofunction:: set_render_rtx_realtime
    .. autofunction:: set_stage_meters_per_unit
    .. autofunction:: set_stage_up_axis