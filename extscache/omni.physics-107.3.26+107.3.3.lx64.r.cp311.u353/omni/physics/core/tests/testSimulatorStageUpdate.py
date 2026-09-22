import carb

import omni.kit.test
from omni.physics.core import (
    Simulation,
    get_physics_interface,
    get_physics_stage_update_interface,
    k_invalid_simulation_id,
)

from .expectedError import ExpectedError


class MockPhysicsStageUpdate:
    """Mock implementation of physics stage update functionality"""

    class TimelineState:
        STOPPED = 0
        PAUSED = 1
        PLAYING = 2

    def __init__(self):
        self.attached_stage_id = None
        self.is_physics_enabled = False
        self.is_paused = False
        self.update_count = 0
        self.raycast_hits = []
        self.last_raycast_origin = None
        self.last_raycast_direction = None
        self.force_load_called = False
        self.release_objects_called = False
        self.is_physics_loaded = False
        self.timeline_state = self.TimelineState.STOPPED
        self.reset_simulation_called = False

    def on_attach(self, stage_id):
        self.attached_stage_id = stage_id
        return True

    def on_detach(self):
        self.attached_stage_id = None
        self.is_physics_loaded = False
        self.timeline_state = self.TimelineState.STOPPED
        return True

    def on_update(self, time, delta_time, physics_enabled):
        self.is_physics_enabled = physics_enabled
        self.update_count += 1
        return True

    def on_resume(self, time):
        if self.attached_stage_id is not None:
            self.timeline_state = self.TimelineState.PLAYING
        self.is_paused = False
        return True

    def on_pause(self):
        if self.attached_stage_id is not None:
            self.timeline_state = self.TimelineState.PAUSED
        self.is_paused = True
        return True

    def on_reset(self):
        if self.attached_stage_id is not None:
            self.timeline_state = self.TimelineState.STOPPED
        self.update_count = 0
        self.is_paused = False
        return True

    def force_load_physics_from_usd(self):
        if self.attached_stage_id is not None:
            self.is_physics_loaded = True
        self.force_load_called = True
        return True

    def release_physics_objects(self):
        if self.attached_stage_id is not None:
            self.is_physics_loaded = False
        self.release_objects_called = True
        return True

    def reset_simulation(self):
        if self.attached_stage_id is not None:
            self.is_physics_loaded = False
            self.timeline_state = self.TimelineState.STOPPED
            self.reset_simulation_called = True
        return True

    def get_timeline_state(self):
        return self.timeline_state

    def was_reset_simulation_called(self):
        return self.reset_simulation_called

    def clear_reset_simulation_flag(self):
        self.reset_simulation_called = False

    def handle_raycast(self, origin, direction, has_input):
        self.last_raycast_origin = origin
        self.last_raycast_direction = direction
        if has_input:
            self.raycast_hits.append((origin, direction))
        return True


class TestSimulateStageUpdate(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Get the physics interface
        self.physics = get_physics_interface()
        self.assertIsNotNone(self.physics)

        # Get the physics stage update interface
        self.physics_stage_update = get_physics_stage_update_interface()
        self.assertIsNotNone(self.physics_stage_update)

        # Create mock implementation
        self.mock_stage_update = MockPhysicsStageUpdate()

        # Create simulation with mock stage update functions
        self.simulation = Simulation()
        self.simulation.stage_update_fns.on_attach = self.mock_stage_update.on_attach
        self.simulation.stage_update_fns.on_detach = self.mock_stage_update.on_detach
        self.simulation.stage_update_fns.on_update = self.mock_stage_update.on_update
        self.simulation.stage_update_fns.on_resume = self.mock_stage_update.on_resume
        self.simulation.stage_update_fns.on_pause = self.mock_stage_update.on_pause
        self.simulation.stage_update_fns.on_reset = self.mock_stage_update.on_reset
        self.simulation.stage_update_fns.force_load_physics_from_usd = (
            self.mock_stage_update.force_load_physics_from_usd
        )
        self.simulation.stage_update_fns.release_physics_objects = self.mock_stage_update.release_physics_objects
        self.simulation.stage_update_fns.handle_raycast = self.mock_stage_update.handle_raycast
        self.simulation.stage_update_fns.reset_simulation = self.mock_stage_update.reset_simulation

        # Register simulation with physics interface
        self.simulation_id = self.physics.register_simulation(self.simulation, "MockStageUpdateSim")
        self.assertNotEqual(self.simulation_id, k_invalid_simulation_id)

    async def tearDown(self):
        # Unregister simulation
        if self.simulation_id != k_invalid_simulation_id:
            self.physics.unregister_simulation(self.simulation_id)

    async def test_stage_attachment(self):
        """Test stage attachment and detachment functionality"""
        # Test attaching a stage
        stage_id = 123
        self.physics_stage_update.on_attach(stage_id)
        self.assertEqual(self.mock_stage_update.attached_stage_id, stage_id)

        # Test detaching the stage
        self.physics_stage_update.on_detach()
        self.assertIsNone(self.mock_stage_update.attached_stage_id)

    async def test_stage_update(self):
        """Test stage update functionality with physics enabled and disabled"""
        stage_id = 123
        self.physics_stage_update.on_attach(stage_id)

        # Test update with physics enabled
        self.physics_stage_update.on_update(1.0, 0.016, True)
        self.assertTrue(self.mock_stage_update.is_physics_enabled)
        self.assertEqual(self.mock_stage_update.update_count, 1)

        # Test update with physics disabled
        self.physics_stage_update.on_update(1.0, 0.016, False)
        self.assertFalse(self.mock_stage_update.is_physics_enabled)

        self.physics_stage_update.on_detach()

    async def test_timeline_control(self):
        """Test timeline control functionality (resume, pause, reset)"""
        stage_id = 123
        self.physics_stage_update.on_attach(stage_id)

        # Test resume
        self.physics_stage_update.on_resume(1.0)
        self.assertFalse(self.mock_stage_update.is_paused)

        # Test pause
        self.physics_stage_update.on_pause()
        self.assertTrue(self.mock_stage_update.is_paused)

        # Test reset
        self.physics_stage_update.on_reset()
        self.assertEqual(self.mock_stage_update.update_count, 0)
        self.assertFalse(self.mock_stage_update.is_paused)

        self.physics_stage_update.on_detach()

    async def test_physics_loading(self):
        """Test physics loading and unloading functionality"""
        stage_id = 123
        self.physics_stage_update.on_attach(stage_id)

        # Test force loading physics
        self.physics_stage_update.force_load_physics_from_usd()
        self.assertTrue(self.mock_stage_update.force_load_called, "force_load_physics_from_usd should be called")
        self.assertTrue(self.mock_stage_update.is_physics_loaded, "Physics should be loaded")

        # Test releasing physics objects
        self.physics_stage_update.release_physics_objects()
        self.assertTrue(self.mock_stage_update.release_objects_called, "release_physics_objects should be called")
        self.assertFalse(self.mock_stage_update.is_physics_loaded, "Physics should be released")

        self.physics_stage_update.on_detach()

    async def test_raycast_handling(self):
        """Test raycast handling functionality"""
        stage_id = 123
        self.physics_stage_update.on_attach(stage_id)

        # Test raycast with input
        origin = carb.Float3(0.0, 0.0, 0.0)
        direction = carb.Float3(0.0, 0.0, 1.0)
        self.physics_stage_update.handle_raycast(origin, direction, True)
        self.assertEqual(len(self.mock_stage_update.raycast_hits), 1)

        # Test raycast without input
        self.physics_stage_update.handle_raycast(origin, direction, False)
        self.assertEqual(len(self.mock_stage_update.raycast_hits), 1)  # Should not add new hit

        self.physics_stage_update.on_detach()

    async def test_reset_simulation(self):
        """Test reset simulation functionality"""
        stage_id = 123
        self.physics_stage_update.on_attach(stage_id)
        self.assertEqual(self.mock_stage_update.attached_stage_id, stage_id)
        self.assertFalse(self.mock_stage_update.was_reset_simulation_called())

        # Load physics first
        self.physics_stage_update.force_load_physics_from_usd()
        self.assertTrue(self.mock_stage_update.is_physics_loaded)

        # Set timeline to playing
        self.physics_stage_update.on_resume(1.0)
        self.assertEqual(self.mock_stage_update.get_timeline_state(), MockPhysicsStageUpdate.TimelineState.PLAYING)

        # Test resetSimulation
        self.physics_stage_update.reset_simulation()

        # Verify simulation was reset
        self.assertTrue(self.mock_stage_update.was_reset_simulation_called())
        self.assertFalse(self.mock_stage_update.is_physics_loaded)  # Physics should be released
        self.assertEqual(self.mock_stage_update.get_timeline_state(), MockPhysicsStageUpdate.TimelineState.STOPPED)  # Timeline should be stopped
        self.assertEqual(self.mock_stage_update.attached_stage_id, stage_id)  # Stage should remain attached

        # Test that we can clear the flag and call again
        self.mock_stage_update.clear_reset_simulation_flag()
        self.assertFalse(self.mock_stage_update.was_reset_simulation_called())

        self.physics_stage_update.reset_simulation()
        self.assertTrue(self.mock_stage_update.was_reset_simulation_called())

        self.physics_stage_update.on_detach()
