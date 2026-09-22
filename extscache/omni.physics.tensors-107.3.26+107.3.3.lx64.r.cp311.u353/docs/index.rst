.. _ext_omni_physics_tensors:

Omni Physics Tensors
####################

Interface for interacting with physics simulations in a data-oriented way.

Overview
********
The goal of ``omni.physics.tensors`` is to provide a simple interface to a physics simulation through a set of abstract Python and C++ APIs that are easy to 
use and understand for users without deep knowledge about the underlying physics simulation. 
The idea is to implement these APIs for various physics engines so that users of the APIs can use the same APIs across different engines.

The main concepts of the interface are:

- Tensor: A tensor is a multi-dimensional array that can be used to represent various data in a physics simulation.

- Physics Views: A physics (Rigid Body, Articulation, Deformable Body, etc) view is a collection of the underlying entities. A view class provides a set of APIs to interact with these entities.

- Concrete Implementation: Currently ``omni.physx.tensors`` is the only official concrete implementation of the interface. 

.. note::
 This abstraction assumes that the physics entities being used are already initialized to their initial states.


High-level functionalities of various physics views
***************************************************

- :py:class:`SimulationView <omni.physics.tensors.impl.api.SimulationView>` is a view designed to manage creation of all other physics views (mentioned below) as well as handling of global simulation parameters such as gravity, simulation device, etc.

- :py:class:`ArticulationView <omni.physics.tensors.impl.api.ArticulationView>` is a view designed to allow interaction with a constrained system of rigid bodies (articulation). Example use cases of :py:class:`ArticulationView <omni.physics.tensors.impl.api.ArticulationView>` are to get/set the joint positions, velocities, apply joint forces, control joint controller parameters, etc. 

- :py:class:`RigidBodyView <omni.physics.tensors.impl.api.RigidBodyView>`: A view to interact with a collection of rigid bodies. Note that these rigid bodies can be part of articulations, but are viewed as individual entities at the API level. Example use cases of :py:class:`RigidBodyView <omni.physics.tensors.impl.api.RigidBodyView>` are to get/set the transforms/velocity of a collection of bodies, apply forces, set contact/material parameters, etc.

- :py:class:`RigidContactView <omni.physics.tensors.impl.api.RigidContactView>`: A view that provides information about contact forces between rigid bodies. Example use cases of :py:class:`RigidContactView <omni.physics.tensors.impl.api.RigidContactView>` are to get the net contact forces, or pair-wise contact forces between predefined pairs of bodies. More involved APIs allow for receiving more detailed contact information such as contact points, normals, etc.

- :py:class:`SdfShapeView <omni.physics.tensors.impl.api.SdfShapeView>`: A view to interact with signed distance fields. Example use cases of :py:class:`SdfShapeView <omni.physics.tensors.impl.api.SdfShapeView>` are to get the signed distance value at a point, get the gradient of the signed distance field, etc.

- :py:class:`SoftBodyView <omni.physics.tensors.impl.api.SoftBodyView>`: Deprecated. A view to interact with a collection of deformable bodies. Example use cases of :py:class:`SoftBodyView <omni.physics.tensors.impl.api.SoftBodyView>` are to get/set the node-wise position/velocity of mesh nodes, apply kinematic motion to a subset of nodes, and get measures of stress/strain such as Cauchy stress, deformation gradient, etc.

- :py:class:`DeformableBodyView <omni.physics.tensors.impl.api.DeformableBodyView>`: Beta feature supporting both collections of volume and surface deformables. Example use cases of :py:class:`DeformableBodyView <omni.physics.tensors.impl.api.DeformableBodyView>` are to get/set simulation mesh node positions, velocities or kinematic targets. The collision mesh as well as the element's rest shape can be retrieved from the view. Retrieval of stress/strain and gradient information is currently not supported, but could be derived on the application side.


You can find out more about all the APIs available for each physics view in the :ref:`API documentation<OmniPhysicsTensors Python API>`.

How to use the interface
************************

First enable the ``omni.physics.tensors`` and ``omni.physx.tensors`` extensions as follows:

#. Navigate to ``window > extensions``.
#. In the search bar, enter ``tensors``.
#. Locate the ``omni.physx.tensors`` extension and select it.
#. Select the ``Enabled`` toggle to enable the extension.
#. Select the ``Check Mark`` next to `AUTOLOAD` to load all of the required extensions automatically on application start, if desired.
#. Close the Extensions Panel.

This should enable both the ``omni.physics.tensors`` and ``omni.physx.tensors`` extensions. ``omni.physics.tensors`` is enabled too since it is a dependency of ``omni.physx.tensors``.


Hello World Example
-------------------
Open one of the sample USD assets. In this example we will use the Franka Panda robot asset located at  
``omni/extensions/runtime/source/omni.physics.tensors.tests/data/usd/franka.usda``.
Once the stage is open with the asset interacting with it is as simple as creating a simulation view and using that to create an articulation view. For isntance, the robot joint limits and current positions can be obtained from the ArticulationView's :py:func:`get_dof_limits <omni.physics.tensors.impl.api.ArticulationView.get_dof_limits>` and :py:func:`get_dof_positions <omni.physics.tensors.impl.api.ArticulationView.get_dof_positions>` APIs as follows.

.. code-block:: python

 import omni.physics.tensors as tensors
 # A simulation view is an entry point that manages all the physics view.
 # A simulation view can be created with numpy/torch/warp, but note that numpy doesn't have GPU support.
 simulation_view = tensors.create_simulation_view("warp")

 # Create an articulation view to interact with a constrained system of rigid bodies.
 articulation_view = simulation_view.create_articulation_view("/panda*")
 # in this example there is only one robot on the scene so the following regular expression will match the single robot.
 # Try right-clicking on the ``panda`` robot stage window and duplicate it. 
 # Creating the view will grab both robots now.

 dof_limits = articulation_view.get_dof_limits()
 print("DOF Limits: ", dof_limits)
    
 dof_positions = articulation_view.get_dof_positions()
 print("DOF Position: ", dof_positions)
    
The above example is how a standalone Python script works with the physics.tensors. You may use the above script with minor changes in the script editor workflow as follows:

#. First, open the asset ``omni/extensions/runtime/source/omni.physics.tensors.tests/data/usd/franka.usda``.

#. Open the script editor from the menu ``Window > Script Editor``.

#. Paste the following snippet in the script editor and run it.


.. code-block:: python   

 import asyncio
 import omni.physics.tensors as tensors

 async def articulation_abstraction():
 # wait a frame to ensure the physics simulation is initialized
 await omni.kit.app.get_app_interface().next_update_async()
 simulation_view = tensors.create_simulation_view("warp")
 articulation_view = simulation_view.create_articulation_view("/panda*")

 dof_limits = articulation_view.get_dof_limits()
 print("DOF Limits: ", dof_limits)
        
 dof_positions = articulation_view.get_dof_positions()
 print("DOF Position: ", dof_positions)

 timeline = omni.timeline.get_timeline_interface()
 timeline.play()
 asyncio.ensure_future(articulation_abstraction())


If everything is set up correctly, you should see the DOF limits and positions printed in the console.


How to run more examples
------------------------

#. Enable the ``omni.physics.tensors.tests`` extension from the extensions window as described above.

#. On the bottom panel close to ``Console`` and ``Content`` there should appear a tab labeled ``Physics Test Runner``. Click on it.

#. You will see a collection of tests that can be run. Click on one of them that seems most relevant to what you are trying to do.

#. Click on ``Run Selected`` to run the test.

#. Open the test script from ``omni/extensions/runtime/source/omni.physics.tensors.tests/python/scripts/tests.py``

#. Search for the name of the test. You will see that the function is a wrapper to a test class. 

#. Search for the test class to find out how the test is implemented.

#. Try to write your own test class and wrappers.

.. toctree::
    :maxdepth: 1
    :hidden:

    inverse_dynamics
    api/python
