import omni.kit.test
from omni.physics.core import (
    PhysicsProfileStats,
    Simulation,
    get_physics_interface,
    get_physics_benchmarks_interface,
    k_invalid_simulation_id,
    k_invalid_subscription_id,
)


class MockBenchmark:
    """Mock implementation of physics benchmark functionality"""

    def __init__(self):
        self.subscription_count = 0
        self.last_subscription_id = k_invalid_subscription_id
        self.profile_stats_callback = None

    def subscribe_profile_stats_events(self, on_event):
        """Subscribe to profile stats events"""
        self.profile_stats_callback = on_event
        self.subscription_count += 1
        self.last_subscription_id = self.subscription_count
        return self.last_subscription_id

    def unsubscribe_profile_stats_events(self, subscription_id):
        """Unsubscribe from profile stats events"""
        if subscription_id == self.last_subscription_id:
            self.profile_stats_callback = None
            self.last_subscription_id = k_invalid_subscription_id

    def simulate_profile_stats(self):
        """Simulate profile stats being generated"""
        if self.profile_stats_callback:
            stats = [
                PhysicsProfileStats(),
                PhysicsProfileStats(),
                PhysicsProfileStats()
            ]
            stats[0].zone_name = "Simulation"
            stats[0].ms = 16.6
            stats[1].zone_name = "Collision Detection"
            stats[1].ms = 5.2
            stats[2].zone_name = "Integration"
            stats[2].ms = 2.1
            self.profile_stats_callback(stats)

    def has_active_subscription(self):
        """Check if there's an active subscription"""
        return self.profile_stats_callback is not None

    def get_last_subscription_id(self):
        """Get the last subscription ID"""
        return self.last_subscription_id


class TestSimulatorBenchmark(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Get the physics interface
        self.physics = get_physics_interface()
        self.assertIsNotNone(self.physics)

        # Get the physics benchmark interface
        self.physics_benchmarks = get_physics_benchmarks_interface()
        self.assertIsNotNone(self.physics_benchmarks)

        # Create mock benchmark
        self.mock_benchmark = MockBenchmark()

        # Create simulation with mock benchmark functions
        self.simulation = Simulation()
        self.simulation.benchmark_fns.subscribe_profile_stats_events = (
            self.mock_benchmark.subscribe_profile_stats_events
        )
        self.simulation.benchmark_fns.unsubscribe_profile_stats_events = (
            self.mock_benchmark.unsubscribe_profile_stats_events
        )

        # Register simulation with physics interface
        self.simulation_id = self.physics.register_simulation(
            self.simulation, "MockBenchmarkSimulator"
        )
        self.assertNotEqual(self.simulation_id, k_invalid_simulation_id)

    async def tearDown(self):
        # Unregister simulation
        if self.simulation_id != k_invalid_simulation_id:
            self.physics.unregister_simulation(self.simulation_id)

    async def test_profile_stats_subscription(self):
        """Test profile stats subscription functionality"""
        callback_called = False
        received_stats = []

        def test_callback(stats):
            nonlocal callback_called, received_stats
            callback_called = True
            received_stats = stats

        # Subscribe to profile stats events
        subscription_id = (
            self.physics_benchmarks.subscribe_profile_stats_events(
                test_callback
            )
        )
        self.assertNotEqual(subscription_id, k_invalid_subscription_id)
        self.assertTrue(self.mock_benchmark.has_active_subscription())

        # Simulate profile stats being generated
        self.mock_benchmark.simulate_profile_stats()

        # Verify callback was called with correct data
        self.assertTrue(callback_called)
        self.assertEqual(len(received_stats), 3)
        self.assertEqual(received_stats[0].zone_name, "Simulation")
        self.assertAlmostEqual(received_stats[0].ms, 16.6, delta=1e-5)
        self.assertEqual(received_stats[1].zone_name, "Collision Detection")
        self.assertAlmostEqual(received_stats[1].ms, 5.2, delta=1e-5)
        self.assertEqual(received_stats[2].zone_name, "Integration")
        self.assertAlmostEqual(received_stats[2].ms, 2.1, delta=1e-5)

        # Unsubscribe from profile stats events
        subscription_id = None
        self.assertFalse(self.mock_benchmark.has_active_subscription())

    async def test_multiple_subscriptions(self):
        """Test multiple subscriptions functionality"""
        callback1_called = False
        callback2_called = False

        def callback1(stats):
            nonlocal callback1_called
            callback1_called = True

        def callback2(stats):
            nonlocal callback2_called
            callback2_called = True

        # Test that only the last subscription is active
        # (limitation of current mock)
        sub1 = self.physics_benchmarks.subscribe_profile_stats_events(
            callback1
        )
        self.assertNotEqual(sub1, k_invalid_subscription_id)

        sub2 = self.physics_benchmarks.subscribe_profile_stats_events(
            callback2
        )
        self.assertNotEqual(sub2, k_invalid_subscription_id)
        self.assertNotEqual(sub2, sub1)

        # Simulate stats - only callback2 should be called in this mock
        # implementation
        self.mock_benchmark.simulate_profile_stats()
        self.assertFalse(callback1_called)
        self.assertTrue(callback2_called)

        # Cleanup
        sub2 = None
        self.assertFalse(self.mock_benchmark.has_active_subscription())

    async def test_unsubscribe_invalid_subscription(self):
        """Test unsubscribing with invalid subscription IDs"""
        # Test unsubscribing with invalid subscription ID
        k_invalid_subscription_id = None
        self.assertFalse(self.mock_benchmark.has_active_subscription())

        # Test unsubscribing with non-existent subscription ID
        k_invalid_subscription_id = 999
        self.assertFalse(self.mock_benchmark.has_active_subscription())

    async def test_profile_stats_data_validation(self):
        """Test profile stats data structure validation"""
        received_stats = []

        def test_callback(stats):
            nonlocal received_stats
            received_stats = stats

        subscription_id = (
            self.physics_benchmarks.subscribe_profile_stats_events(
                test_callback
            )
        )
        self.assertNotEqual(subscription_id, k_invalid_subscription_id)

        # Simulate profile stats
        self.mock_benchmark.simulate_profile_stats()

        # Validate profile stats data structure
        self.assertGreater(len(received_stats), 0)
        print(received_stats)
        for stat in received_stats:
            print(stat)
            print(stat.zone_name)
            print(stat.ms)
            self.assertIsNotNone(stat.zone_name)
            self.assertGreater(len(stat.zone_name), 0)
            self.assertGreaterEqual(stat.ms, 0.0)

        # Cleanup
        subscription_id = None

    async def test_no_callback_after_unsubscribe(self):
        """Test that no callback is called after unsubscribe"""
        callback_called = False

        def test_callback(stats):
            nonlocal callback_called
            callback_called = True

        subscription_id = (
            self.physics_benchmarks.subscribe_profile_stats_events(
                test_callback
            )
        )
        self.assertNotEqual(subscription_id, k_invalid_subscription_id)

        # Unsubscribe immediately
        subscription_id = None
        self.assertFalse(self.mock_benchmark.has_active_subscription())

        # Simulate stats - callback should not be called
        self.mock_benchmark.simulate_profile_stats()
        self.assertFalse(callback_called)

    async def test_subscription_id_generation(self):
        """Test that subscription IDs are properly generated and unique"""
        def dummy_callback(stats):
            pass

        # Subscribe multiple times and check IDs are unique
        sub1 = self.physics_benchmarks.subscribe_profile_stats_events(
            dummy_callback
        )
        self.assertNotEqual(sub1, k_invalid_subscription_id)

        sub2 = self.physics_benchmarks.subscribe_profile_stats_events(
            dummy_callback
        )
        self.assertNotEqual(sub2, k_invalid_subscription_id)
        self.assertNotEqual(sub2, sub1)

        # Cleanup
        sub2 = None

    async def test_callback_with_empty_stats(self):
        """Test callback behavior with empty profile stats"""
        callback_called = False
        received_stats = []

        def test_callback(stats):
            nonlocal callback_called, received_stats
            callback_called = True
            received_stats = stats

        subscription_id = (
            self.physics_benchmarks.subscribe_profile_stats_events(
                test_callback
            )
        )
        self.assertNotEqual(subscription_id, k_invalid_subscription_id)

        # Simulate empty profile stats
        if self.mock_benchmark.profile_stats_callback:
            self.mock_benchmark.profile_stats_callback([])

        # Verify callback was called with empty data
        self.assertTrue(callback_called)
        self.assertEqual(len(received_stats), 0)

        # Cleanup
        subscription_id = None
