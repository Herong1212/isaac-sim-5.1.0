.. include:: ../../../../../dev_guide/_links.rst

.. _ext_omni_physx_cct:

Omni PhysX Character Controller
###############################

The omni.physxcct extension adds support for a capsule-based kinematic character controller i.e. a way for a user controlled character to move through a scene using a collide-and-slide collision algorithm. Character controller is represented by the |PhysxCharacterControllerAPI| .

For a wide array of CCT usage see the "Python" or "Action Graph" demos in the Demos/Character Controller category (CharacterControllerDemo.py, CharacterControllerActionGraph.py). 

Setup and Controls
******************

.. code::

    from omni.physxcct.scripts import utils

    # set up a base capsule 
    utils.spawn_capsule(stage, cct_path, position)

    # start first-person CCT control with gravity
    utils.activate_cct(stage, cct_path, "/OmniverseKit_Persp", True)

    # activate default controls (keyboard/mouse or gamepad)
    control_state = utils.setup_controls(cct_path, speed)

Manual Setup
************

.. code::

    from omni.physxcct import get_physx_cct_interface
    from pxr import UsdGeom, PhysxSchema

    # set up a base capsule
    capsule_geom = UsdGeom.Capsule.Define(stage, capsule_path)
    capsule_geom.CreateHeightAttr(50.0)
    capsule_geom.CreateRadiusAttr(25.0)
    capsule_geom.CreateAxisAttr(UsdGeom.GetStageUpAxis(stage))

    # apply CCT API
    capsule_prim = stage.GetPrimAtPath(capsule_path)
    cct = PhysxSchema.PhysxCharacterControllerAPI.Apply(capsule_prim)

    # start first-person CCT control with gravity
    physx_cct = get_physx_cct_interface()
    physx_cct.enable_first_person(self._path_cct, True)
    physx_cct.enable_gravity(self._path_cct)
    physx_cct.set_current_camera("/OmniverseKit_Persp")

Manual Controls
***************

.. code::

    # multiply speed constant with current frametime
    speed = 10 * dt

    # add up directions and normalize to account for possible diagonal movement
    x = control_up + control_down * -1
    y = control_left + control_right * -1
    move = Gf.Vec3f(x * speed, y * speed, 0).GetNormalized()

    # set move to usd
    get_physx_cct_interface().set_move(state.cct_path, (move[0], move[1], move[2]))

Note that the CharacterControllerAPI:MoveTarget attribute is by default considered a local space vector of either the CCT Capsule prim or the CCT first person camera prim (when in first person mode). To consider it as a world space vector call (`use_worldspace_move(True) <#omni.physxcct.bindings._physxCct.IPhysxCct.use_worldspace_move>`__).

Python API
**********

.. automodule:: omni.physxcct.scripts.utils
    :platform: Windows-x86_64, Linux-x86_64
    :members: CharacterController, spawn_capsule, ControlFlag, ControlState

.. include::
    python_bindings.rst


OmniGraph Nodes
***************

.. toctree::
    :maxdepth: 1
    :glob:

    ../../../../../_build/ogn/docs/omni.physx.cct/*
