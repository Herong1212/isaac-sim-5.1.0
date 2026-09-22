import carb

import omni.kit.test
from omni.physics.core import (
    Simulation,
    get_physics_interaction_interface,
    get_physics_interface,
    k_invalid_simulation_id,
)


class MockInteraction:
    """Mock implementation of physics interaction functionality"""

    def __init__(self):
        self.is_reset_on_stop_disabled = False
        self.raycast_count = 0
        self.last_raycast_input = False
        self.last_raycast_origin = carb.Float3(0.0, 0.0, 0.0)
        self.last_raycast_direction = carb.Float3(0.0, 0.0, 0.0)

    def disable_reset_on_stop(self, disable):
        self.is_reset_on_stop_disabled = disable

    def is_disabled_reset_on_stop(self):
        return self.is_reset_on_stop_disabled

    def handle_raycast(self, origin, direction, has_input):
        self.raycast_count += 1
        self.last_raycast_input = has_input
        if origin:
            self.last_raycast_origin = origin
        if direction:
            self.last_raycast_direction = direction
        return True


class TestSimulateInteraction(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Get the physics interface
        self.physics = get_physics_interface()
        self.assertIsNotNone(self.physics)

        # Get the physics interaction interface
        self.physics_interaction = get_physics_interaction_interface()
        self.assertIsNotNone(self.physics_interaction)

        # Create mock implementation
        self.mock_interaction = MockInteraction()

        # Create simulation with mock interaction functions
        self.simulation = Simulation()
        self.simulation.interaction_fns.disable_reset_on_stop = self.mock_interaction.disable_reset_on_stop
        self.simulation.interaction_fns.is_disabled_reset_on_stop = self.mock_interaction.is_disabled_reset_on_stop
        self.simulation.interaction_fns.handle_raycast = self.mock_interaction.handle_raycast

        # Register simulation with physics interface
        self.simulation_id = self.physics.register_simulation(self.simulation, "MockInteractionSim")
        self.assertNotEqual(self.simulation_id, k_invalid_simulation_id)

    async def tearDown(self):
        # Unregister simulation
        if self.simulation_id != k_invalid_simulation_id:
            self.physics.unregister_simulation(self.simulation_id)

    async def test_reset_on_stop_control(self):
        """Test reset on stop control functionality"""
        # Test initial state
        self.assertFalse(self.mock_interaction.is_reset_on_stop_disabled)
        self.assertFalse(self.physics_interaction.is_disabled_reset_on_stop())

        # Test disable
        self.physics_interaction.disable_reset_on_stop(True)
        self.assertTrue(self.mock_interaction.is_reset_on_stop_disabled)
        self.assertTrue(self.physics_interaction.is_disabled_reset_on_stop())

        # Test enable
        self.physics_interaction.disable_reset_on_stop(False)
        self.assertFalse(self.mock_interaction.is_reset_on_stop_disabled)
        self.assertFalse(self.physics_interaction.is_disabled_reset_on_stop())

        # Test multiple toggles
        for i in range(5):
            expected = (i % 2) == 0
            self.physics_interaction.disable_reset_on_stop(expected)
            self.assertEqual(self.mock_interaction.is_reset_on_stop_disabled, expected)
            self.assertEqual(self.physics_interaction.is_disabled_reset_on_stop(), expected)

    async def test_raycast_handling(self):
        """Test raycast handling functionality"""
        origin = carb.Float3(1.0, 2.0, 3.0)
        direction = carb.Float3(0.0, 1.0, 0.0)

        # Test raycast with input
        self.physics_interaction.handle_raycast(origin, direction, True)
        self.assertEqual(self.mock_interaction.raycast_count, 1)
        self.assertTrue(self.mock_interaction.last_raycast_input)

        # Test raycast without input
        self.physics_interaction.handle_raycast(origin, direction, False)
        self.assertEqual(self.mock_interaction.raycast_count, 2)
        self.assertFalse(self.mock_interaction.last_raycast_input)

        # Test multiple raycasts
        for i in range(5):
            test_origin = carb.Float3(float(i), float(i + 1), float(i + 2))
            test_dir = carb.Float3(float(i), float(i + 1), float(i + 2))

            self.physics_interaction.handle_raycast(test_origin, test_dir, True)
            self.assertEqual(self.mock_interaction.raycast_count, 3 + i)
            self.assertTrue(self.mock_interaction.last_raycast_input)

    async def test_null_pointer_handling(self):
        """Test handling of null pointers in raycast"""
        # Test raycast with null pointers
        self.physics_interaction.handle_raycast(None, None, True)
        self.assertEqual(self.mock_interaction.raycast_count, 1)
        self.assertTrue(self.mock_interaction.last_raycast_input)
