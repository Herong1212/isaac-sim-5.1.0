.. include:: ../../../../../../dev_guide/_links.rst

.. _contact_reports:

Contact Reports
============================

Contact reports can be received in Python code by adding a |PhysxContactReportAPI| to the body or articulation Prim.

Subscribing to the contact event report, contacts are sent through a callback function in two arrays.

The contact report first array contains contact headers, which can be of type:

* ``ContactEventType.CONTACT_FOUND``
* ``ContactEventType.CONTACT_PERSISTS``
* ``ContactEventType.CONTACT_LOST``

These events send the additional dictionary with contact information:

* actor0 - Usd path to rigid body actor 0 decoded into two ints. ``PhysicsSchemaTools.encodeSdfPath`` will return SdfPath.
* actor1 - Usd path to rigid body actor 1 decoded into two ints. ``PhysicsSchemaTools.encodeSdfPath`` will return SdfPath.
* collider0 - Usd path to collider 0 decoded into two ints. ``PhysicsSchemaTools.encodeSdfPath`` will return SdfPath.
* collider1 - Usd path to collider 1 decoded into two ints. ``PhysicsSchemaTools.encodeSdfPath`` will return SdfPath.
* stage_id - Stage that the report is coming from.
* contact_data_offset - Offset to the contact data array.
* num_contact_data - Number of contacts in the contact data array for this header.

The actual contact data are in the second array. Contact data contains this information:

* position - Contact position.
* normal - Contact normal.
* impulse - Contact impulse.
* separation - Separation value for collisions.
* face_index0 - Face index of the collider0 (filled only if available 0xFFFFFFFF otherwise).
* face_index1 - Face index of the collider1 (filled only if available 0xFFFFFFFF otherwise).
* material0 - Material of collider0.
* material1 - Material of collider1.

The following code will not execute and is just kept here as a guidance. Instead of copy pasting the snippet code, review the Physics Demo Sample - contactReportDemo.

.. code::

    from omni.physx.scripts.physicsUtils import *
    from pxr import Usd, UsdGeom, Sdf, Gf, Tf, Vt, UsdPhysics, PhysxSchema
    from omni.physx._physx import SimulationEvent
    from omni.physx import get_physx_interface


    # acquire the physx interface
    self._physx = _physx.acquire_physx_interface()

    # subscribe to physics contact report event, this callback is issued after each simulation step
    self._contact_report_sub = get_physx_simulation_interface().subscribe_contact_report_events(self._on_contact_report_event)

    # Spheres
    spherePath = "/sphere"

    radius = 30.0
    position = Gf.Vec3f(0.0, 0.0, 800.0)
    orientation = Gf.Quatf(1.0)
    color = Gf.Vec3f(71.0 / 255.0, 165.0 / 255.0, 1.0)
    density = 1000.0
    linvel = Gf.Vec3f(0.0)

    add_rigid_sphere(stage, spherePath, radius, position, orientation, color, density, linvel, Gf.Vec3f(0.0))

    # apply contact report
    spherePrim = stage.GetPrimAtPath(spherePath)
    contactReportAPI = PhysxSchema.PhysxContactReportAPI.Apply(spherePrim)
    contactReportAPI.CreatePhysxContactReportThresholdAttr().Set(200000)

    def _on_contact_report_event(self, contact_headers, contact_data):
        for contact_header in contact_headers:
            print("Got contact header type: " + str(contact_header.type))
            print("Actor0: " + str(PhysicsSchemaTools.intToSdfPath(contact_header.actor0)))
            print("Actor1: " + str(PhysicsSchemaTools.intToSdfPath(contact_header.actor1)))
            print("Collider0: " + str(PhysicsSchemaTools.intToSdfPath(contact_header.collider0)))
            print("Collider1: " + str(PhysicsSchemaTools.intToSdfPath(contact_header.collider1)))
            print("StageId: " + str(contact_header.stage_id))
            print("Number of contacts: " + str(contact_header.num_contact_data))
            
            contact_data_offset = contact_header.contact_data_offset
            num_contact_data = contact_header.num_contact_data
            
            for index in range(contact_data_offset, contact_data_offset + num_contact_data, 1):
                print("Contact:")
                print("Contact position: " + str(contact_data[index].position))
                print("Contact normal: " + str(contact_data[index].normal))
                print("Contact impulse: " + str(contact_data[index].impulse))
                print("Contact separation: " + str(contact_data[index].separation))
                print("Contact faceIndex0: " + str(contact_data[index].face_index0))
                print("Contact faceIndex1: " + str(contact_data[index].face_index1))
                print("Contact material0: " + str(PhysicsSchemaTools.intToSdfPath(contact_data[index].material0)))
                print("Contact material1: " + str(PhysicsSchemaTools.intToSdfPath(contact_data[index].material1)))

