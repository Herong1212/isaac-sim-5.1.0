import omni.kit.test
from omni.physics.core import (
    PhysicsStepContext,
    Simulation,
    get_physics_interface,
    get_physics_simulation_interface,
    k_invalid_simulation_id,
    ContactEventHeaderVector,
    ContactDataVector,
    FrictionAnchorsDataVector,
    ContactEventType,
    ContactEventHeader,
    ContactData,
    FrictionAnchor,
    ForceMode,
)


class MockSimulator:
    """Mock implementation of physics simulation functionality"""

    def __init__(self):
        self.attached_stage_id = 0
        self.change_tracking_paused = False
        self.time_steps_per_second = 60
        self.simulation_timestamp = 0
        self.simulation_step_count = 0
        self.sleeping_bodies = {}
        self.step_event_callbacks = []
        self.contact_event_callbacks = []
        self.simulation_id = 0

    def attach_stage(self, stage_id):
        self.attached_stage_id = stage_id
        return True

    def detach_stage(self):
        self.attached_stage_id = 0

    def get_attached_stage(self):
        return self.attached_stage_id

    def simulate(self, elapsed_time, current_time):
        self.simulation_timestamp += 1
        self.simulation_step_count += 1

        # Call step event callbacks
        context = PhysicsStepContext()
        context.scene_path = self.attached_stage_id
        context.simulation_id = self.simulation_id

        for callback in self.step_event_callbacks:
            callback(elapsed_time, context)

    def fetch_results(self):
        # Mock implementation - call contact event callbacks
        contact_event_headers = ContactEventHeaderVector()
        contact_data = ContactDataVector()
        friction_anchors = FrictionAnchorsDataVector()
        for callback in self.contact_event_callbacks:
            callback(contact_event_headers, contact_data, friction_anchors)
        pass

    def check_results(self):
        return True

    def flush_changes(self):
        pass

    def pause_change_tracking(self, pause):
        self.change_tracking_paused = pause

    def is_change_tracking_paused(self):
        return self.change_tracking_paused

    def subscribe_physics_contact_report_events(self, on_event):
        self.contact_event_callbacks.append(on_event)
        return len(self.contact_event_callbacks)

    def unsubscribe_physics_contact_report_events(self, subscription_id):
        if subscription_id > 0 and subscription_id <= len(self.contact_event_callbacks):
            self.contact_event_callbacks.pop(subscription_id - 1)

    def get_simulation_time_steps_per_second(self, stage_id, scene_path):
        return self.time_steps_per_second

    def get_simulation_timestamp(self):
        return self.simulation_timestamp

    def get_simulation_step_count(self):
        return self.simulation_step_count

    def add_force_at_pos(self, stage_id, path, force, pos, mode):
        pass

    def add_torque(self, stage_id, path, torque):
        pass

    def wake_up(self, stage_id, path):
        self.sleeping_bodies[path] = False

    def put_to_sleep(self, stage_id, path):
        self.sleeping_bodies[path] = True

    def is_sleeping(self, stage_id, path):
        return path in self.sleeping_bodies and self.sleeping_bodies[path]

    def subscribe_physics_on_step_events(self, pre_step, order, on_update):
        self.step_event_callbacks.append(on_update)
        return len(self.step_event_callbacks)

    def unsubscribe_physics_on_step_events(self, subscription_id):
        if subscription_id > 0 and subscription_id <= len(self.step_event_callbacks):
            self.step_event_callbacks.pop(subscription_id - 1)


class TestSimulatorSimulation(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Get the physics interface
        self.physics = get_physics_interface()
        self.assertIsNotNone(self.physics)

        # Get the physics simulation interface
        self.physics_simulation = get_physics_simulation_interface()
        self.assertIsNotNone(self.physics_simulation)

        # Create mock simulator
        self.mock_simulator = MockSimulator()

        # Create simulation with mock functions
        self.simulation = Simulation()
        self.simulation.simulation_fns.attach_stage = (
            self.mock_simulator.attach_stage
        )
        self.simulation.simulation_fns.detach_stage = (
            self.mock_simulator.detach_stage
        )
        self.simulation.simulation_fns.get_attached_stage = (
            self.mock_simulator.get_attached_stage
        )
        self.simulation.simulation_fns.simulate = self.mock_simulator.simulate
        self.simulation.simulation_fns.fetch_results = self.mock_simulator.fetch_results
        self.simulation.simulation_fns.check_results = self.mock_simulator.check_results
        self.simulation.simulation_fns.flush_changes = self.mock_simulator.flush_changes
        self.simulation.simulation_fns.pause_change_tracking = self.mock_simulator.pause_change_tracking
        self.simulation.simulation_fns.is_change_tracking_paused = self.mock_simulator.is_change_tracking_paused
        self.simulation.simulation_fns.subscribe_physics_contact_report_events = (
            self.mock_simulator.subscribe_physics_contact_report_events
        )
        self.simulation.simulation_fns.unsubscribe_physics_contact_report_events = (
            self.mock_simulator.unsubscribe_physics_contact_report_events
        )
        self.simulation.simulation_fns.get_simulation_time_steps_per_second = (
            self.mock_simulator.get_simulation_time_steps_per_second
        )
        self.simulation.simulation_fns.get_simulation_timestamp = (
            self.mock_simulator.get_simulation_timestamp
        )
        self.simulation.simulation_fns.get_simulation_step_count = (
            self.mock_simulator.get_simulation_step_count
        )
        self.simulation.simulation_fns.add_force_at_pos = self.mock_simulator.add_force_at_pos
        self.simulation.simulation_fns.add_torque = self.mock_simulator.add_torque
        self.simulation.simulation_fns.wake_up = self.mock_simulator.wake_up
        self.simulation.simulation_fns.put_to_sleep = self.mock_simulator.put_to_sleep
        self.simulation.simulation_fns.is_sleeping = self.mock_simulator.is_sleeping
        self.simulation.simulation_fns.subscribe_physics_on_step_events = (
            self.mock_simulator.subscribe_physics_on_step_events
        )
        self.simulation.simulation_fns.unsubscribe_physics_on_step_events = (
            self.mock_simulator.unsubscribe_physics_on_step_events
        )

        # Register simulation with physics interface
        self.simulation_id = self.physics.register_simulation(self.simulation, "MockSimulator")
        self.assertNotEqual(self.simulation_id, k_invalid_simulation_id)
        self.mock_simulator.simulation_id = self.simulation_id

    async def tearDown(self):
        # Unregister simulation
        if self.simulation_id != k_invalid_simulation_id:
            self.physics.unregister_simulation(self.simulation_id)

    async def test_stage_attachment(self):
        """Test stage attachment functionality"""
        # Test initial state
        self.assertEqual(self.mock_simulator.attached_stage_id, 0)

        # Test attach
        self.assertTrue(self.physics_simulation.attach_stage(123))
        self.assertEqual(self.mock_simulator.attached_stage_id, 123)
        self.assertEqual(self.physics_simulation.get_attached_stage(), 123)

        # Test detach
        self.physics_simulation.detach_stage()
        self.assertEqual(self.mock_simulator.attached_stage_id, 0)
        self.assertEqual(self.physics_simulation.get_attached_stage(), 0)

    async def test_simulation_timing(self):
        """Test simulation timing functionality"""
        stage_id = 123
        scene_path = 0

        # Test initial state
        self.assertEqual(
            self.physics_simulation.get_simulation_time_steps_per_second(self.simulation_id, stage_id, scene_path), 60
        )
        self.assertEqual(self.physics_simulation.get_simulation_timestamp(self.simulation_id), 0)
        self.assertEqual(self.physics_simulation.get_simulation_step_count(self.simulation_id), 0)

        # Test single simulation step
        self.physics_simulation.simulate(1.0 / 60.0, 0.0)
        self.physics_simulation.fetch_results()

        self.assertEqual(self.physics_simulation.get_simulation_timestamp(self.simulation_id), 1)
        self.assertEqual(self.physics_simulation.get_simulation_step_count(self.simulation_id), 1)

        # Test multiple simulation steps
        for i in range(5):
            self.physics_simulation.simulate(1.0 / 60.0, (i + 1) * 1.0 / 60.0)
            self.physics_simulation.fetch_results()

        self.assertEqual(self.physics_simulation.get_simulation_timestamp(self.simulation_id), 6)
        self.assertEqual(self.physics_simulation.get_simulation_step_count(self.simulation_id), 6)

    async def test_sleep_wake_control(self):
        """Test sleep/wake control functionality"""
        stage_id = int(123)
        path = int(456)

        # Test initial state
        self.assertFalse(self.physics_simulation.is_sleeping(stage_id, path))

        # Test put to sleep
        self.physics_simulation.put_to_sleep(stage_id, path)
        self.assertTrue(self.physics_simulation.is_sleeping(stage_id, path))

        # Test wake up
        self.physics_simulation.wake_up(stage_id, path)
        self.assertFalse(self.physics_simulation.is_sleeping(stage_id, path))

    async def test_change_tracking(self):
        """Test change tracking functionality"""
        # Test initial state
        self.assertFalse(self.mock_simulator.change_tracking_paused)
        self.assertFalse(self.physics_simulation.is_change_tracking_paused())

        # Test pause
        self.physics_simulation.pause_change_tracking(True)

        self.assertTrue(self.mock_simulator.change_tracking_paused)
        self.assertTrue(self.physics_simulation.is_change_tracking_paused())

        # Test resume
        self.physics_simulation.pause_change_tracking(False)
        self.assertFalse(self.mock_simulator.change_tracking_paused)
        self.assertFalse(self.physics_simulation.is_change_tracking_paused())

    # TODO: Fix this test
    async def test_contact_callbacks(self):
        """Test contact callback functionality"""
        # Test variables to track callback execution
        contact_callback_called = False

        def on_contact_event(event_headers, contact_data, friction_anchors):
            nonlocal contact_callback_called
            print("on_contact_event")
            contact_callback_called = True

        # Subscribe to contact events
        subscription_id = (
            self.physics_simulation.subscribe_physics_contact_report_events(
                on_contact_event
            )
        )
        self.assertIsNotNone(subscription_id)

        # Simulate and fetch results to trigger callback
        self.physics_simulation.simulate(1.0 / 60.0, 0.0)
        self.physics_simulation.fetch_results()

        # Verify callback was called
        self.assertTrue(contact_callback_called)

        # Unsubscribe and verify callback is not called
        contact_callback_called = False
        subscription_id = None
        self.physics_simulation.simulate(1.0 / 60.0, 1.0 / 60.0)
        self.physics_simulation.fetch_results()
        self.assertFalse(contact_callback_called)

    async def test_step_callbacks(self):
        """Test step callback functionality"""
        # Test variables to track callback execution
        step_callback_called = False
        step_elapsed_time = None
        step_context = None

        def on_step_event(elapsed_time, context):
            nonlocal step_callback_called, step_elapsed_time, step_context
            step_callback_called = True
            step_elapsed_time = elapsed_time
            step_context = context

        # Subscribe to step events
        subscription_id = (
            self.physics_simulation.subscribe_physics_on_step_events(
                False, 0, on_step_event
            )
        )
        self.assertIsNotNone(subscription_id)

        # Simulate to trigger callback
        elapsed_time = 1.0 / 60.0
        self.physics_simulation.simulate(elapsed_time, 0.0)
        self.physics_simulation.fetch_results()

        # Verify callback was called with correct data
        self.assertTrue(step_callback_called)
        self.assertAlmostEqual(step_elapsed_time, elapsed_time)
        self.assertIsNotNone(step_context)
        self.assertEqual(
            step_context.scene_path, self.mock_simulator.attached_stage_id
        )
        self.assertEqual(
            step_context.simulation_id, self.mock_simulator.simulation_id
        )

        # Unsubscribe and verify callback is not called
        step_callback_called = False
        subscription_id = None
        self.physics_simulation.simulate(1.0 / 60.0, 1.0 / 60.0)
        self.assertFalse(step_callback_called)

    async def test_contact_event_type_enum(self):
        """Test ContactEventType enum values and functionality"""
        # Test enum values exist and have expected values
        self.assertEqual(
            ContactEventType.CONTACT_FOUND, ContactEventType.CONTACT_FOUND
        )
        self.assertEqual(
            ContactEventType.CONTACT_LOST, ContactEventType.CONTACT_LOST
        )
        self.assertEqual(
            ContactEventType.CONTACT_PERSIST, ContactEventType.CONTACT_PERSIST
        )

        # Test that values are distinct
        self.assertNotEqual(
            ContactEventType.CONTACT_FOUND, ContactEventType.CONTACT_LOST
        )
        self.assertNotEqual(
            ContactEventType.CONTACT_FOUND, ContactEventType.CONTACT_PERSIST
        )
        self.assertNotEqual(
            ContactEventType.CONTACT_LOST, ContactEventType.CONTACT_PERSIST
        )

    async def test_force_mode_enum(self):
        """Test ForceMode enum values and functionality"""
        # Test enum values exist and have expected values
        self.assertEqual(ForceMode.FORCE, ForceMode.FORCE)
        self.assertEqual(ForceMode.IMPULSE, ForceMode.IMPULSE)
        self.assertEqual(ForceMode.VELOCITY_CHANGE, ForceMode.VELOCITY_CHANGE)
        self.assertEqual(ForceMode.ACCELERATION, ForceMode.ACCELERATION)

        # Test that values are distinct
        self.assertNotEqual(ForceMode.FORCE, ForceMode.IMPULSE)
        self.assertNotEqual(ForceMode.FORCE, ForceMode.VELOCITY_CHANGE)
        self.assertNotEqual(ForceMode.FORCE, ForceMode.ACCELERATION)

    async def test_contact_event_header(self):
        """Test ContactEventHeader class creation and field access"""
        # Test default construction
        header = ContactEventHeader()

        # Test field assignment and access
        header.type = ContactEventType.CONTACT_FOUND
        header.stage_id = 123
        header.actor0 = 456
        header.actor1 = 789
        header.collider0 = 111
        header.collider1 = 222
        header.contact_data_offset = 10
        header.num_contact_data = 5
        header.friction_anchors_data_offset = 20
        header.num_friction_anchors_data = 3
        header.proto_index0 = 0xFFFFFFFF
        header.proto_index1 = 0xFFFFFFFF

        # Verify all fields were set correctly
        self.assertEqual(header.type, ContactEventType.CONTACT_FOUND)
        self.assertEqual(header.stage_id, 123)
        self.assertEqual(header.actor0, 456)
        self.assertEqual(header.actor1, 789)
        self.assertEqual(header.collider0, 111)
        self.assertEqual(header.collider1, 222)
        self.assertEqual(header.contact_data_offset, 10)
        self.assertEqual(header.num_contact_data, 5)
        self.assertEqual(header.friction_anchors_data_offset, 20)
        self.assertEqual(header.num_friction_anchors_data, 3)
        self.assertEqual(header.proto_index0, 0xFFFFFFFF)
        self.assertEqual(header.proto_index1, 0xFFFFFFFF)

    async def test_contact_data(self):
        """Test ContactData class creation and field access"""
        # Test default construction
        contact = ContactData()

        # Test field assignment and access
        position = [1.0, 2.0, 3.0]
        normal = [0.0, 1.0, 0.0]
        separation = -0.1
        impulse = [5.0, 6.0, 7.0]

        contact.position = position
        contact.normal = normal
        contact.separation = separation
        contact.impulse = impulse

        # Verify all fields were set correctly
        self.assertEqual(contact.position, position)
        self.assertEqual(contact.normal, normal)
        self.assertAlmostEqual(contact.separation, separation, delta=1e-5)
        self.assertEqual(contact.impulse, impulse)

    async def test_friction_anchor(self):
        """Test FrictionAnchor class creation and field access"""
        # Test default construction
        anchor = FrictionAnchor()

        # Test field assignment and access
        position = [10.0, 20.0, 30.0]
        impulse = [1.5, 2.5, 3.5]

        anchor.position = position
        anchor.impulse = impulse

        # Verify all fields were set correctly
        self.assertEqual(anchor.position, position)
        self.assertEqual(anchor.impulse, impulse)

    async def test_contact_vectors(self):
        """Test contact-related vector operations"""
        # Test ContactEventHeaderVector
        header_vector = ContactEventHeaderVector()
        self.assertEqual(len(header_vector), 0)

        # Add some headers
        header1 = ContactEventHeader()
        header1.type = ContactEventType.CONTACT_FOUND
        header1.stage_id = 100

        header2 = ContactEventHeader()
        header2.type = ContactEventType.CONTACT_LOST
        header2.stage_id = 200

        header_vector.append(header1)
        header_vector.append(header2)
        self.assertEqual(len(header_vector), 2)

        # Test accessing elements
        self.assertEqual(header_vector[0].type, ContactEventType.CONTACT_FOUND)
        self.assertEqual(header_vector[0].stage_id, 100)
        self.assertEqual(header_vector[1].type, ContactEventType.CONTACT_LOST)
        self.assertEqual(header_vector[1].stage_id, 200)

        # Test ContactDataVector
        contact_vector = ContactDataVector()
        self.assertEqual(len(contact_vector), 0)

        contact1 = ContactData()
        contact1.position = [1.0, 0.0, 0.0]
        contact1.separation = -0.05

        contact2 = ContactData()
        contact2.position = [0.0, 1.0, 0.0]
        contact2.separation = -0.1

        contact_vector.append(contact1)
        contact_vector.append(contact2)
        self.assertEqual(len(contact_vector), 2)

        # Test accessing elements
        self.assertEqual(contact_vector[0].position, [1.0, 0.0, 0.0])
        self.assertAlmostEqual(contact_vector[0].separation, -0.05, delta=1e-5)
        self.assertEqual(contact_vector[1].position, [0.0, 1.0, 0.0])
        self.assertAlmostEqual(contact_vector[1].separation, -0.1, delta=1e-5)

        # Test FrictionAnchorsDataVector
        friction_vector = FrictionAnchorsDataVector()
        self.assertEqual(len(friction_vector), 0)

        anchor1 = FrictionAnchor()
        anchor1.position = [2.0, 0.0, 0.0]
        anchor1.impulse = [1.0, 0.0, 0.0]

        anchor2 = FrictionAnchor()
        anchor2.position = [0.0, 2.0, 0.0]
        anchor2.impulse = [0.0, 1.0, 0.0]

        friction_vector.append(anchor1)
        friction_vector.append(anchor2)
        self.assertEqual(len(friction_vector), 2)

        # Test accessing elements
        self.assertEqual(friction_vector[0].position, [2.0, 0.0, 0.0])
        self.assertEqual(friction_vector[0].impulse, [1.0, 0.0, 0.0])
        self.assertEqual(friction_vector[1].position, [0.0, 2.0, 0.0])
        self.assertEqual(friction_vector[1].impulse, [0.0, 1.0, 0.0])

    async def test_enhanced_contact_callbacks(self):
        """Test enhanced contact callback functionality with new structures"""
        # Test variables to track callback execution and data
        contact_callback_called = False
        received_headers = None
        received_contact_data = None
        received_friction_anchors = None

        def on_contact_event(event_headers, contact_data, friction_anchors):
            nonlocal contact_callback_called, received_headers
            nonlocal received_contact_data, received_friction_anchors
            contact_callback_called = True
            received_headers = event_headers
            received_contact_data = contact_data
            received_friction_anchors = friction_anchors

        # Subscribe to contact events
        subscription_id = (
            self.physics_simulation.subscribe_physics_contact_report_events(
                on_contact_event
            )
        )
        self.assertIsNotNone(subscription_id)

        # Simulate and fetch results to trigger callback
        self.physics_simulation.simulate(1.0 / 60.0, 0.0)
        self.physics_simulation.fetch_results()

        # Verify callback was called with proper data types
        self.assertTrue(contact_callback_called)
        self.assertIsInstance(received_headers, ContactEventHeaderVector)
        self.assertIsInstance(received_contact_data, ContactDataVector)
        self.assertIsInstance(
            received_friction_anchors, FrictionAnchorsDataVector
        )

        # Unsubscribe and verify callback is not called
        contact_callback_called = False
        subscription_id = None
        self.physics_simulation.simulate(1.0 / 60.0, 1.0 / 60.0)
        self.physics_simulation.fetch_results()
        self.assertFalse(contact_callback_called)
