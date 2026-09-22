.. _ext_omni_physx_commands:

Omni PhysX Commands
###################################

Physics commands are providing undo/redo capability for a list of utilities from omni.physx.utils and omni.physx.physicsUtils \
or are directly applying or removing APIs from the physics USD schemas in defined sets which we call 'Components' \ 
(`see our API documentation <../../../${repo_docs_api_path}/omni_physics_api.html>`__).


For a general overview of the command system `see Kit Commands documentation <https://docs.omniverse.nvidia.com/kit/docs/omni.kit.commands/latest/>`_.


Utility Commands
********************************

.. automodule:: omni.physxcommands
    :platform: Windows-x86_64, Linux-x86_64
    :members: AddPhysicsSceneCommand, AddRigidBodyMaterialCommand, AddDeformableBodyMaterialCommand, AddDeformableSurfaceMaterialCommand, AddPBDMaterialCommand, AddCollisionGroupCommand, AddPairFilterCommand, RemovePairFilterCommand, AddGroundPlaneCommand, SetRigidBodyCommand, SetStaticColliderCommand, RemoveRigidBodyCommand, RemoveStaticColliderCommand, CreateJointCommand, CreateJointsCommand
    :noindex:


Helper Commands
********************************

.. automodule:: omni.physxcommands
    :platform: Windows-x86_64, Linux-x86_64
    :members: PhysicsCommand, ApplyAPISchemaCommand, UnapplyAPISchemaCommand, RemoveAttributeCommand, RemoveRelationshipCommand, ChangeAttributeCommand
    :noindex:
    

Component Commands
********************************

.. automodule:: omni.physxcommands
    :platform: Windows-x86_64, Linux-x86_64
    :members: AddPhysicsComponentCommand, RemovePhysicsComponentCommand
    :noindex:


For a list of low-level component commands called through AddPhysicsComponentCommand and RemovePhysicsComponentCommand see below:

.. automodule:: omni.physxcommands
    :platform: Windows-x86_64, Linux-x86_64
    :members: AddDistancePhysicsJointComponentCommand, RemoveDistancePhysicsJointComponentCommand, AddFixedPhysicsJointComponentCommand, RemoveFixedPhysicsJointComponentCommand, AddRevolutePhysicsJointComponentCommand, RemoveRevolutePhysicsJointComponentCommand, AddPrismaticPhysicsJointComponentCommand, RemovePrismaticPhysicsJointComponentCommand, AddSphericalPhysicsJointComponentCommand, RemoveSphericalPhysicsJointComponentCommand, AddD6PhysicsJointComponentCommand, RemoveD6PhysicsJointComponentCommand, 
    :noindex:
