.. _ext_omni_physx:

Omni PhysX
#########################

Overview
************************************

The omni.physx extension provides a connection between USD physics content and the NVIDIA PhysX simulation engine. Physics content in USD is defined through two USD schemas: UsdPhysics which implements the standard USD physics extension schema, and PhysXSchema, which extends it with PhysX specific features.

The omni.physx plugin is responsible for parsing the USD stage, running the PhysX simulation, and writing the results back to the USD stage.

API Documentation
************************************
.. toctree::
    :maxdepth: 1
    
    api/python
