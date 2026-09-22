
USD Representation
******************

The recommended USD hierarchy and setup for a vehicle is as follows:

.. code:: none

    Xform (vehicle)
    |   applied API schemas:
    |   * UsdPhysics.RigidBodyAPI
    |   * UsdPhysics.MassAPI
    |   * PhysxSchema.PhysxRigidBodyAPI
    |   * PhysxSchema.PhysxVehicleAPI
    |     -> relationship to
    |        PhysxSchema.PhysxVehicleDriveStandardAPI prim
    |        or
    |        PhysxSchema.PhysxVehicleDriveBasicAPI prim
    |     alternative:
    |        apply PhysxVehicleDriveStandardAPI or PhysxVehicleDriveBasicAPI directly
    |   * PhysxSchema.PhysxVehicleMultiWheelDifferentialAPI
    |     or
    |     PhysxSchema.PhysxVehicleTankDifferentialAPI
    |   * PhysxSchema.PhysxVehicleBrakesAPI (instances "brakes0" and "brakes1")
    |   * PhysxSchema.PhysxVehicleSteeringAPI
    |     or
    |     PhysxSchema.PhysxVehicleAckermannSteeringAPI
    |   * PhysxSchema.PhysxVehicleControllerAPI (see note further below)
    |     or
    |     PhysxSchema.PhysxVehicleTankControllerAPI
    |
    |--- Xform (wheel0)
    |    |   applied API schemas:
    |    |   * PhysxSchema.PhysxVehicleWheelAttachmentAPI
    |    |     -> relationships to
    |    |        PhysxSchema.PhysxVehicleWheelAPI prim,
    |    |        PhysxSchema.PhysxVehicleTireAPI prim,
    |    |        PhysxSchema.PhysxVehicleSuspensionAPI prim
    |    |     alternative:
    |    |        apply PhysxVehicleWheelAPI, PhysxVehicleTireAPI and PhysxVehicleSuspensionAPI directly
    |    |   * PhysxSchema.PhysxVehicleSuspensionComplianceAPI (optionally)
    |    |   [* PhysxSchema.PhysxVehicleWheelControllerAPI] (see note further below)
    |    |
    |    |--- Mesh (wheel collision geometry if desired)
    |    |        applied API schemas:
    |    |        * UsdPhysics.CollisionAPI
    |    |        * PhysxSchema.PhysxCollisionAPI
    |    |        * UsdPhysics.MeshCollisionAPI
    |    |
    |    |--- Xform (wheel render objects)
    |         |
    |         |--- Mesh
    |         |--- Mesh
    |         |--- ...
    |
    |--- Xform (wheel1)
    |    |
    |    ...
    |
    |--- Xform (wheel2)
    |    |
    |    ...
    |
    |--- Xform (wheel3)
    |    |
    |    ...
    |
    |--- Mesh (chassis collision geometry)
    |        applied API schemas:
    |        * UsdPhysics.CollisionAPI
    |        * PhysxSchema.PhysxCollisionAPI
    |        * UsdPhysics.MeshCollisionAPI
    |
    |--- Xform (chassis render objects)
         |
         |--- Mesh
         |--- Mesh
         |--- ...

.. note::

    If direct control over wheels is desired (for example because a custom drive is implemented),
    then PhysxVehicleMultiWheelDifferentialAPI/PhysxVehicleTankDifferentialAPI, PhysxVehicleBrakesAPI,
    PhysxVehicleSteeringAPI/PhysxVehicleAckermannSteeringAPI and
    PhysxVehicleControllerAPI/PhysxVehicleTankControllerAPI should be omitted and instead
    PhysxVehicleWheelControllerAPI should be applied to the wheel attachment prims.
    This enables setting drive torque, brake torque or steer angle on the wheels directly.

    The wheel collision geometry does not have to be a Mesh, a Cylinder or other type will work too.
    For some use cases it can be omitted as well.
    
    Prims positioned under the wheel attachment Xforms will be transformed during simulation to match
    the wheel motion (wheel steer and rotation).

This is just a rough skeleton. A lot of vehicle components are not listed here as they are linked to through
USD relationships and can be shared among vehicles. There are also some global vehicle settings that need to
be defined. Please have a look at the basic setup samples to get the full picture.
