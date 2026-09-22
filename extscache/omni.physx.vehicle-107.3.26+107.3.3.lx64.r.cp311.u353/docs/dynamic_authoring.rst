
Dynamic Vehicle Authoring
-------------------------

Vehicles can be created and destroyed while the simulation is running. This is called Dynamic Vehicle Authoring. This feature can be used to warp vehicles from one end of a street to the other in order to create the illusion of an endless stream of city traffic, for example. 

Presently, there are a few restrictions with how this is done:

1. All of the vehicle primitives (prims) must be created within a single simulation time step when creating a vehicle. Many of these prims reference other prims and the vehicle creation process will fail if the referenced prims are missing.

2. A Physics Scene must be created before the simulation is started and it must have the PhysxVehicleContextAPI API schema applied.

3. To destroy a vehicle, all of the vehicle prims must be deleted within a single simulation time step.

