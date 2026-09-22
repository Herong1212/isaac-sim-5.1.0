import carb

import omni.kit.test
from omni.physics.core import (
    OverlapHit,
    RaycastHit,
    Simulation,
    SweepHit,
    get_physics_interface,
    get_physics_scene_query_interface,
    k_invalid_simulation_id,
)


class MockSceneQuery:
    """Mock implementation of physics scene query functionality"""

    def __init__(self):
        self.raycast_count = 0
        self.sweep_count = 0
        self.overlap_count = 0
        self.last_raycast_origin = carb.Float3(0.0, 0.0, 0.0)
        self.last_raycast_direction = carb.Float3(0.0, 0.0, 0.0)
        self.last_raycast_distance = 0.0
        self.last_raycast_both_sides = False
        self.last_sweep_origin = carb.Float3(0.0, 0.0, 0.0)
        self.last_sweep_direction = carb.Float3(0.0, 0.0, 0.0)
        self.last_sweep_distance = 0.0
        self.last_sweep_both_sides = False
        self.last_overlap_position = carb.Float3(0.0, 0.0, 0.0)
        self.last_overlap_radius = 0.0
        self.report_fn_calls = 0
        self.last_hit = None

    def raycast_closest(self, origin, unit_dir, distance, hit, both_sides):
        self.raycast_count += 1
        self.last_raycast_origin = origin
        self.last_raycast_direction = unit_dir
        self.last_raycast_distance = distance
        self.last_raycast_both_sides = both_sides
        return True

    def raycast_any(self, origin, unit_dir, distance, both_sides):
        self.raycast_count += 1
        self.last_raycast_origin = origin
        self.last_raycast_direction = unit_dir
        self.last_raycast_distance = distance
        self.last_raycast_both_sides = both_sides
        return True

    def raycast_all(self, origin, unit_dir, distance, report_fn, both_sides):
        self.raycast_count += 1
        self.last_raycast_origin = origin
        self.last_raycast_direction = unit_dir
        self.last_raycast_distance = distance
        self.last_raycast_both_sides = both_sides

        # Create a mock hit for testing
        hit = RaycastHit()
        hit.position = carb.Float3(1.0, 2.0, 3.0)
        hit.normal = carb.Float3(0.0, 1.0, 0.0)
        hit.distance = 5.0
        self.last_hit = hit

        # Call report function
        if report_fn:
            self.report_fn_calls += 1
            report_fn(hit)
        return True

    def sweep_sphere_closest(self, radius, origin, unit_dir, distance, hit, both_sides):
        self.sweep_count += 1
        self.last_sweep_origin = origin
        self.last_sweep_direction = unit_dir
        self.last_sweep_distance = distance
        self.last_sweep_both_sides = both_sides
        return True

    def sweep_sphere_any(self, radius, origin, unit_dir, distance, both_sides):
        self.sweep_count += 1
        self.last_sweep_origin = origin
        self.last_sweep_direction = unit_dir
        self.last_sweep_distance = distance
        self.last_sweep_both_sides = both_sides
        return True

    def sweep_sphere_all(self, radius, origin, unit_dir, distance, report_fn, both_sides):
        self.sweep_count += 1
        self.last_sweep_origin = origin
        self.last_sweep_direction = unit_dir
        self.last_sweep_distance = distance
        self.last_sweep_both_sides = both_sides

        # Create a mock hit for testing
        hit = SweepHit()
        hit.position = carb.Float3(1.0, 2.0, 3.0)
        hit.normal = carb.Float3(0.0, 1.0, 0.0)
        hit.distance = 5.0
        self.last_hit = hit

        # Call report function
        if report_fn:
            self.report_fn_calls += 1
            report_fn(hit)
        return True

    def overlap_sphere(self, radius, pos, report_fn):
        self.overlap_count += 1
        self.last_overlap_position = pos
        self.last_overlap_radius = radius

        # Create a mock hit for testing
        hit = OverlapHit()
        self.last_hit = hit

        # Call report function
        if report_fn:
            self.report_fn_calls += 1
            report_fn(hit)
        return 1

    def overlap_sphere_any(self, radius, pos):
        self.overlap_count += 1
        self.last_overlap_position = pos
        self.last_overlap_radius = radius
        return True


class TestSimulatorSceneQuery(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Get the physics interface
        self.physics = get_physics_interface()
        self.assertIsNotNone(self.physics)

        # Get the physics scene query interface
        self.physics_scene_query = get_physics_scene_query_interface()
        self.assertIsNotNone(self.physics_scene_query)

        # Create mock implementation
        self.mock_scene_query = MockSceneQuery()

        # Create simulation with mock scene query functions
        self.simulation = Simulation()
        self.simulation.scene_query_fns.raycast_closest = self.mock_scene_query.raycast_closest
        self.simulation.scene_query_fns.raycast_any = self.mock_scene_query.raycast_any
        self.simulation.scene_query_fns.raycast_all = self.mock_scene_query.raycast_all
        self.simulation.scene_query_fns.sweep_sphere_closest = self.mock_scene_query.sweep_sphere_closest
        self.simulation.scene_query_fns.sweep_sphere_any = self.mock_scene_query.sweep_sphere_any
        self.simulation.scene_query_fns.sweep_sphere_all = self.mock_scene_query.sweep_sphere_all
        self.simulation.scene_query_fns.overlap_sphere = self.mock_scene_query.overlap_sphere
        self.simulation.scene_query_fns.overlap_sphere_any = self.mock_scene_query.overlap_sphere_any

        # Register simulation with physics interface
        self.simulation_id = self.physics.register_simulation(self.simulation, "MockSceneQuerySim")
        self.assertNotEqual(self.simulation_id, k_invalid_simulation_id)

    async def tearDown(self):
        # Unregister simulation
        if self.simulation_id != k_invalid_simulation_id:
            self.physics.unregister_simulation(self.simulation_id)

    async def test_raycast_queries(self):
        """Test raycast query functionality"""
        origin = carb.Float3(1.0, 2.0, 3.0)
        direction = carb.Float3(0.0, 1.0, 0.0)
        distance = 10.0
        both_sides = True

        # Test raycast closest
        result, hit = self.physics_scene_query.raycast_closest(origin, direction, distance, both_sides)
        self.assertTrue(result)
        self.assertEqual(self.mock_scene_query.raycast_count, 1)
        self.assertEqual(self.mock_scene_query.last_raycast_origin, origin)
        self.assertEqual(self.mock_scene_query.last_raycast_direction, direction)
        self.assertEqual(self.mock_scene_query.last_raycast_distance, distance)
        self.assertEqual(self.mock_scene_query.last_raycast_both_sides, both_sides)

        # Test raycast any
        result = self.physics_scene_query.raycast_any(origin, direction, distance, both_sides)
        self.assertTrue(result)
        self.assertEqual(self.mock_scene_query.raycast_count, 2)

        # Test raycast all
        hit_received = False

        def report_fn(hit):
            nonlocal hit_received
            hit_received = True
            self.assertIsInstance(hit, RaycastHit)
            self.assertEqual(hit.position, carb.Float3(1.0, 2.0, 3.0))
            self.assertEqual(hit.normal, carb.Float3(0.0, 1.0, 0.0))
            self.assertEqual(hit.distance, 5.0)
            return True

        self.physics_scene_query.raycast_all(origin, direction, distance, report_fn, both_sides)
        self.assertEqual(self.mock_scene_query.raycast_count, 3)
        self.assertEqual(self.mock_scene_query.report_fn_calls, 1)
        self.assertTrue(hit_received)

    async def test_sweep_queries(self):
        """Test sweep query functionality"""
        radius = 1.0
        origin = carb.Float3(1.0, 2.0, 3.0)
        direction = carb.Float3(0.0, 1.0, 0.0)
        distance = 10.0
        both_sides = True

        # Test sweep sphere closest
        result, hit = self.physics_scene_query.sweep_sphere_closest(radius, origin, direction, distance, both_sides)
        self.assertTrue(result)
        self.assertEqual(self.mock_scene_query.sweep_count, 1)
        self.assertEqual(self.mock_scene_query.last_sweep_origin, origin)
        self.assertEqual(self.mock_scene_query.last_sweep_direction, direction)
        self.assertEqual(self.mock_scene_query.last_sweep_distance, distance)
        self.assertEqual(self.mock_scene_query.last_sweep_both_sides, both_sides)

        # Test sweep sphere any
        result = self.physics_scene_query.sweep_sphere_any(radius, origin, direction, distance, both_sides)
        self.assertTrue(result)
        self.assertEqual(self.mock_scene_query.sweep_count, 2)

        # Test sweep sphere all
        hit_received = False

        def report_fn(hit):
            nonlocal hit_received
            hit_received = True
            self.assertIsInstance(hit, SweepHit)
            self.assertEqual(hit.position, carb.Float3(1.0, 2.0, 3.0))
            self.assertEqual(hit.normal, carb.Float3(0.0, 1.0, 0.0))
            self.assertEqual(hit.distance, 5.0)
            return True

        self.physics_scene_query.sweep_sphere_all(radius, origin, direction, distance, report_fn, both_sides)
        self.assertEqual(self.mock_scene_query.sweep_count, 3)
        self.assertEqual(self.mock_scene_query.report_fn_calls, 1)
        self.assertTrue(hit_received)

    async def test_overlap_queries(self):
        """Test overlap query functionality"""
        radius = 1.0
        position = carb.Float3(1.0, 2.0, 3.0)

        # Test overlap sphere
        hit_received = False

        def report_fn(hit):
            nonlocal hit_received
            hit_received = True
            self.assertIsInstance(hit, OverlapHit)
            return True

        result = self.physics_scene_query.overlap_sphere(radius, position, report_fn)
        self.assertEqual(result, 1)
        self.assertEqual(self.mock_scene_query.overlap_count, 1)
        self.assertEqual(self.mock_scene_query.last_overlap_position, position)
        self.assertEqual(self.mock_scene_query.last_overlap_radius, radius)
        self.assertEqual(self.mock_scene_query.report_fn_calls, 1)
        self.assertTrue(hit_received)

        # Test overlap sphere any
        result = self.physics_scene_query.overlap_sphere_any(radius, position)
        self.assertTrue(result)
        self.assertEqual(self.mock_scene_query.overlap_count, 2)
