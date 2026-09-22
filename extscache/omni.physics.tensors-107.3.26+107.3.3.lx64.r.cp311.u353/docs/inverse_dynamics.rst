.. _OmniPhysicsTensors Inverse Dynamics:

Inverse dynamics
****************

The tensor API provides multiple functionalities to help users integrate inverse dynamics to their workflow.
In the following, several typical use cases will be described.

Application of a joint-space trajectory
=======================================

A common use case is to estimate the forces/torques required to apply to a robot in order to follow a given joint-space trajectory.
In other words, a method to convert the root link and joint accelerations into forces/torques applied to the root link and joints given the root link and joint positions and velocities.

This can be performed by using the equation of motion:

.. math::
   \tau = M(q) \ddot{q} + C(q, \dot{q}) * \dot{q} + G(q),

where :math:`q` is the root link and joint positions, :math:`{\tau}` the forces/torques applied to the root link and joints, :math:`M(q)` the mass matrix, :math:`C(q, \dot{q}) * \dot{q}` the Coriolis and centrifugal forces, and :math:`G(q)` the gravity forces.

The different terms of the equation of motion can be obtained using the following functions:

* The mass matrix :math:`M(q)` with the function :py:func:`get_generalized_mass_matrices <omni.physics.tensors.impl.api.ArticulationView.get_generalized_mass_matrices>`.
* The Coriolis and centrifugal compensation forces :math:`C(q, \dot{q}) * \dot{q}` with the function :py:func:`get_coriolis_and_centrifugal_compensation_forces <omni.physics.tensors.impl.api.ArticulationView.get_coriolis_and_centrifugal_compensation_forces>`.
* The gravity compensation forces :math:`G(q)` with the function :py:func:`get_gravity_compensation_forces <omni.physics.tensors.impl.api.ArticulationView.get_gravity_compensation_forces>`.

Using these properties, one can convert the desired root link and joint accelerations :math:`\ddot{q}` to the required forces/torques :math:`{\tau}`.

.. note::
  The inverse dynamics calculation does not include the effects of damping, joint friction, and contact.

A usage example is provided below based on a simple gripper with a floating base.
The inverse dynamics calculation is performed in the `_apply_inverse_dynamics` function.
The original file is located at `omni/extensions/ux/source/omni.physx.demos/python/scenes/InverseDynamicsTensorAPIDemo.py`.

.. literalinclude:: ../../../../ux/source/omni.physx.demos/python/scenes/InverseDynamicsTensorAPIDemo.py
  :language: python
  :linenos:

To run the demo:

#. Enables the demos from the menu ``Window > Physics > Demo Scenes``.

#. In the ``Physics Demo Scenes`` tab, the demo is under the ``Complex Showcases`` category and is named ``Gripper inverse dynamics``.

Link velocities to joint velocities
===================================

In some cases, it may be useful to convert link velocities/accelerations to joint velocities/accelerations, or vice versa.
This can be performed by using the Jacobian matrix, which maps the joint space velocities of the robot to world-space link velocities.

The Jacobian matrix of an articulation can be obtained using the function :py:func:`get_jacobians <omni.physics.tensors.impl.api.ArticulationView.get_jacobians>`.

.. note::
  The Jacobian matrix does not include the effects of damping, joint friction, and contact.

A minimal usage example is provided below for a fixed-base articulation::

    import asyncio
    import numpy as np
    import omni.physics.tensors as tensors

    async def jacobian_use_case():
        # Wait for a frame to ensure the physics simulation is initialized
        await omni.kit.app.get_app_interface().next_update_async()

        # Create the simulation view
        sim_view = tensors.create_simulation_view("warp")

        # Create the articulation view
        articulation_view = sim_view.create_articulation_view("/World/envs/env_0/franka")

        # Get the Jacobian for all articulations in the view
        jacobians = articulation_view.get_jacobians()
        jacobians_np = jacobians.numpy().reshape(articulation_view.count, (articulation_view.max_links - 1) * 6, articulation_view.max_dofs)

        # Set arbitrary joint velocities for the sake of the example
        joint_velocity = np.zeros([articulation_view.count, articulation_view.max_dofs])
        for i in range(articulation_view.count):
            for j in range(articulation_view.max_dofs):
                joint_velocity[i, j] = 0.1 * i - 0.5 * j

        # Calculate expected link velocities
        expected_link_velocity = np.zeros([articulation_view.count, (articulation_view.max_links - 1) * 6])
        for i in range(articulation_view.count):
            expected_link_velocity[i, :] = np.dot(jacobians_np[i, :, :], joint_velocity[i, :])

    # Run the simulation
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    asyncio.ensure_future(jacobian_use_case())

The above example may be used in the script editor as follows:

#. First, open the asset ``omni/data/usd/tests/Physics/FrankaCabinetOneEnv.usd``.

#. Open the script editor from the menu ``Window > Script Editor``.

#. Paste the following snippet in the script editor and run it.

Centroidal momentum
===================

The tensor API provides utilities to predict the evolution of the centroidal momentum :math:`h_G` using the velocity :math:`\dot{q}` and acceleration :math:`\ddot{q}` of the combined root link and joint degrees-of-freedom of a floating-base articulation.

This can be done using the centroidal momentum matrix :math:`A_G` and the corresponding bias force :math:`\dot{A}_G \dot{q}`:

.. math::
    h_G = A_G \dot{q}

and

.. math::
    \dot{h}_G = A_G \ddot{q} + \dot{A}_G \dot{q}.

The centroidal momentum matrix and the corresponding bias force of an articulation can be obtained using the function :py:func:`get_articulation_centroidal_momentum <omni.physics.tensors.impl.api.ArticulationView.get_articulation_centroidal_momentum>`.

.. note::
  The centroidal momentum matrix does not include the effects of damping, joint friction, and contact.
  Moreover, the functionality is only implemented for floating-base articulations.

A minimal usage example is provided below::

    import asyncio
    import numpy as np
    import omni.physics.tensors as tensors

    async def centroidal_momentum_use_case():
        # Wait for a frame to ensure the physics simulation is initialized
        await omni.kit.app.get_app_interface().next_update_async()

        # Create the simulation view
        sim_view = tensors.create_simulation_view("warp")

        # Create the articulation view
        articulation_view = sim_view.create_articulation_view("/World/envs/env_0/Humanoid")

        # Get the centroidal momentum matrix and bias force for all articulations in the view
        temp_buffer = articulation_view.get_articulation_centroidal_momentum()
        temp_buffer_np = temp_buffer.numpy().reshape(articulation_view.count, 6, articulation_view.max_dofs + 7)

        # Extract the centroidal momentum matrix and the bias force from the results
        centroidal_momentum_matrices_np = temp_buffer[:, :, :-1]
        bias_forces_np = temp_buffer[:, :, -1:]

        # Set arbitrary joint and root velocities for the sake of the example
        root_velocity = np.zeros([articulation_view.count, 6])
        joint_velocity = np.zeros([articulation_view.count, articulation_view.max_dofs])
        for i in range(articulation_view.count):
            root_velocity[i, :] = np.array([0.0, 0.1 * i, -0.1, 0.0, 0.4 * i, 0.0])
            for j in range(articulation_view.max_dofs):
                joint_velocity[i, j] = 0.1 * i - 0.5 * j

        # Calculate expected centroidal momentum
        expected_centroidal_momentum = np.zeros([articulation_view.count, 6])
        for i in range(articulation_view.count):
            expected_centroidal_momentum[i, :] = np.dot(centroidal_momentum_matrices_np[i, :, 6:], joint_velocity[i, :])
            expected_centroidal_momentum[i, :] += np.dot(centroidal_momentum_matrices_np[i, :, :6], root_velocity[i, :])

    # Run the simulation
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    asyncio.ensure_future(centroidal_momentum_use_case())

The above example may be used in the script editor as follows:

#. First, open the asset ``omni/data/usd/tests/Physics/HumanoidOneEnv.usd``.

#. Open the script editor from the menu ``Window > Script Editor``.

#. Paste the following snippet in the script editor and run it
