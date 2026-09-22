
.. _Physics Debug Window:

Physics Debug Window
====================

Use the **Window > Simulation > Debug** window to access physics debugging tools like manual stepping, visualizations or additional logging.

Simulation Control
#######################

You can run, stop, and *Step*. Stepping the simulation goes through one time step at a time, so you can inspect problems that happen.

Simulation Overrides
#######################

You can manually perform updates from USD or release simulation objects, and override the CPU/GPU and solver settings of the PhysicsScene. You also have the options to disable sleeping and enable synchronous CUDA kernel launches. Enabling synchronous CUDA kernel launches is especially useful when submitting bug reports because it shows the exact point of failure, if the crash happens during CUDA kernel execution.

Mass Information
#######################

You can query the mass information for the selected prims and their sub-hierarchies.

Simulation Debug Visualization
##############################

You can enable and configure a low-level visualizer that renders directly based on the PhysX engine's state, which is useful, if for some reason the simulation is not in sync with USD. When you check the **Enabled** box, the different elements to visualize are presented. 

.. note:: Data is only visualized *when the simulation is running*. 
    
The *Scale* field can be used to adjust the length of some lines and arrows.

Some data, like contact points, are generated at the start of an update and bodies are moved at the end of the update. Shapes are also drawn using their state at the start of an update so that they line up with contact points. For this reason the visualization display may appear to lag one frame behind the graphics rendering.

Deformable Debug Visualization
##################################

Configure the options for :ref:`deformable bodies<deformableDebugViz>`.

Particles Debug Visualization
##################################

You can configure the particle radius by selecting the desired offset parameter and the particle positions based on the particle position type. For particle cloth, there is the option to render the mesh wireframe instead of the particles.

Collision Mesh Debug Visualization
##################################

In addition to the wireframe debug visualization available in the :ref:`viewport show/hide menu<viewport_overlays>`, you can visualize the collision-mesh approximations using solid render meshes. You may also inspect a convex decomposition using the explode-view distance.

Vehicle Debug Visualization
##################################

This is an option to enable the suspension debug visualization.

OmniPVD
#######

Enable and configure PVD data logging by the `PhysX PVD logger <https://developer.nvidia.com/physx-visual-debugger>`_, which can be helpful to inspect the PhysX simulation objects created from USD data.

Legacy PVD
##########

This is provided for backwards compatibility.

Physics Schema Removal
#######################

Remove the ``physics`` or ``physx`` schemas from prims.

.. _physics_debug_window_logging_channels:

Logging Channels
#######################

Selecting a checkbox will log additional messages related to the subject.
