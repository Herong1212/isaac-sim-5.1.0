import omni.kit.test
from omni.physics.core import Simulation, get_physics_interface, k_invalid_simulation_id

from .expectedError import ExpectedError


class TestSimulationRegistry(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Get the physics interface
        self.physics = get_physics_interface()
        self.assertIsNotNone(self.physics)

    async def test_create_new_simulation(self):
        """Test creating a new simulation"""
        simulation = Simulation()
        simulation_name = "TestSimulation"

        simulation_id = self.physics.register_simulation(simulation, simulation_name)
        self.assertNotEqual(simulation_id, k_invalid_simulation_id)

        # Test getting simulation name
        retrieved_name = self.physics.get_simulation_name(simulation_id)
        self.assertEqual(retrieved_name, simulation_name)

        self.physics.unregister_simulation(simulation_id)

    async def test_invalid_simulation_operations(self):
        """Test operations with invalid simulation IDs"""
        with ExpectedError():
            # Test getting simulation with invalid ID
            invalid_sim = self.physics.get_simulation(k_invalid_simulation_id)
            self.assertIsNone(invalid_sim)

        with ExpectedError():
            # Test getting name with invalid ID
            invalid_name = self.physics.get_simulation_name(k_invalid_simulation_id)
            self.assertEqual(invalid_name, "")

        with ExpectedError():
            # Test activation state with invalid ID
            self.assertFalse(self.physics.is_simulation_active(k_invalid_simulation_id))

        with ExpectedError():
            # Test unregistering invalid ID (should not crash)
            self.physics.unregister_simulation(k_invalid_simulation_id)

        with ExpectedError():
            # Test activating invalid ID (should not crash)
            self.physics.activate_simulation(k_invalid_simulation_id)

        with ExpectedError():
            # Test deactivating invalid ID (should not crash)
            self.physics.deactivate_simulation(k_invalid_simulation_id)

    async def test_register_and_unregister_simulation(self):
        """Test registering and unregistering a simulation"""
        simulation = Simulation()
        simulation_name = "TestSimulation"

        # Test registration
        simulation_id = self.physics.register_simulation(simulation, simulation_name)
        self.assertNotEqual(simulation_id, k_invalid_simulation_id)

        # Test getting simulation by ID
        retrieved_sim = self.physics.get_simulation(simulation_id)
        self.assertTrue(retrieved_sim is not None)

        # Test getting simulation name
        retrieved_name = self.physics.get_simulation_name(simulation_id)
        self.assertEqual(retrieved_name, simulation_name)

        # Test unregistration
        self.physics.unregister_simulation(simulation_id)
        with ExpectedError():
            retrieved_sim = self.physics.get_simulation(simulation_id)
            self.assertIsNone(retrieved_sim)

    async def test_multiple_simulations_management(self):
        """Test managing multiple simulations"""
        sim1 = Simulation()
        sim2 = Simulation()
        sim3 = Simulation()
        sim1_name = "Simulation1"
        sim2_name = "Simulation2"
        sim3_name = "Simulation3"

        # Register multiple simulations
        id1 = self.physics.register_simulation(sim1, sim1_name)
        id2 = self.physics.register_simulation(sim2, sim2_name)
        id3 = self.physics.register_simulation(sim3, sim3_name)

        self.assertNotEqual(id1, k_invalid_simulation_id)
        self.assertNotEqual(id2, k_invalid_simulation_id)
        self.assertNotEqual(id3, k_invalid_simulation_id)

        # Test get_num_simulations
        num_sims = self.physics.get_num_simulations()
        self.assertEqual(num_sims, 3)

        # Test get_simulation_ids
        sim_ids = self.physics.get_simulation_ids()
        self.assertEqual(len(sim_ids), num_sims)

        # Verify all IDs are present and names are correct
        found_id1 = False
        found_id2 = False
        found_id3 = False
        for sim_id in sim_ids:
            if sim_id == id1:
                found_id1 = True
                self.assertEqual(self.physics.get_simulation_name(sim_id), sim1_name)
            if sim_id == id2:
                found_id2 = True
                self.assertEqual(self.physics.get_simulation_name(sim_id), sim2_name)
            if sim_id == id3:
                found_id3 = True
                self.assertEqual(self.physics.get_simulation_name(sim_id), sim3_name)

        self.assertTrue(found_id1)
        self.assertTrue(found_id2)
        self.assertTrue(found_id3)

        # Cleanup
        self.physics.unregister_simulation(id1)
        self.physics.unregister_simulation(id2)
        self.physics.unregister_simulation(id3)

    async def test_simulation_activation(self):
        """Test simulation activation and deactivation"""
        simulation = Simulation()
        simulation_name = "TestSimulation"

        # Register simulation
        simulation_id = self.physics.register_simulation(simulation, simulation_name)
        self.assertNotEqual(simulation_id, k_invalid_simulation_id)

        # Test initial state (should be active by default)
        self.assertTrue(self.physics.is_simulation_active(simulation_id))

        # Test deactivation
        self.physics.deactivate_simulation(simulation_id)
        self.assertFalse(self.physics.is_simulation_active(simulation_id))

        # Test activation
        self.physics.activate_simulation(simulation_id)
        self.assertTrue(self.physics.is_simulation_active(simulation_id))

        # Cleanup
        self.physics.unregister_simulation(simulation_id)
