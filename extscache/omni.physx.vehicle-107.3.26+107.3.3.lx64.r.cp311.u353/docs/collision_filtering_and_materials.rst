
Collision Filtering & Materials
*******************************

Collision Filtering
===================

A key setup step to get vehicles running properly is to define which components should collide with each other
and which should not. The following collision groups are common for a simple setup:

* GroundQuery

    * (PhysxSchema.PhysxVehicleWheelAttachmentAPI)
* GroundSurface

    * (UsdPhysics.CollisionAPI)
* Chassis

    * (UsdPhysics.CollisionAPI)
* Wheel

    * (UsdPhysics.CollisionAPI)

.. note::

    The PhysX Vehicle SDK does not simulate the wheel as a separate rigid body, instead a geometrical query along
    the suspension direction detects impact with the ground. In the given example, the listed GroundQuery collision
    group represents this geometrical query. The GroundQuery collison group would be set on the wheel attachment
    prim (PhysxSchema.PhysxVehicleWheelAttachmentAPI, relationship "collisionGroup").

The following table marks the collisions that may usually be discarded with an "x".

+---------------+-------------+---------------+---------+-------+
|               | GroundQuery | GroundSurface | Chassis | Wheel |
+---------------+-------------+---------------+---------+-------+
| GroundQuery   |             |               |    x    |   x   |
+---------------+-------------+---------------+---------+-------+
| GroundSurface |             |       x       |         |   x   |
+---------------+-------------+---------------+---------+-------+
| Chassis       |      x      |               |         |   x   |
+---------------+-------------+---------------+---------+-------+
| Wheel         |      x      |       x       |    x    |       |
+---------------+-------------+---------------+---------+-------+

.. note::

    Collisions between Wheel and Chassis will be ignored automatically if the wheel and chassis collision geometries
    are placed under the same PhysxSchema.PhysxVehicleAPI root.

Materials
=========

Another important setup step involves setting physics materials for the ground surfaces a vehicle will drive on. Those
materials are used to define the friction values for tire vs. ground. To be recognized as a vehicle compatible material,
UsdPhysics.MaterialAPI has to be applied. Physics materials can be set on collision geometry through
UsdShade.MaterialBindingAPI. Once the materials are set up, tire friction tables (PhysxSchema.PhysxVehicleTireFrictionTable)
can be created to define the friction values of materials for a given tire.

Example:

=================  ==============
Material USD Path  Friction Value
=================  ==============
/TarmacMaterial    0.7
/GravelMaterial    0.6
...                ...
=================  ==============

The tire friction table can be linked to in the corresponding relationship in PhysxSchema.PhysxVehicleTire. Please have a
look at the basic setup samples for details.

.. note::

    If the vehicle tires touch an unknown material, the default friction value will be used which can be specified per
    tire friction table (1 is the default value).
