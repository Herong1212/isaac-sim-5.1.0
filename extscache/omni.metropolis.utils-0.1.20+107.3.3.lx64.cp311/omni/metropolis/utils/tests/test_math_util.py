import omni.kit.test
from pxr import Gf
import math
from omni.metropolis.utils.math_util import MathUtil, MathNumpyUtil
import numpy as np


class TestMathUtil(omni.kit.test.AsyncTestCase):
    """Test suite for MathUtil class."""

    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_get_angle_between(self):
        """Test get_angle_between function with various vector pairs."""
        # Test parallel vectors (0 degrees)
        vec1 = Gf.Vec3d(1, 0, 0)
        vec2 = Gf.Vec3d(1, 0, 0)
        self.assertAlmostEqual(MathUtil.get_angle_between(vec1, vec2), 0.0)

        # Test perpendicular vectors (90 degrees)
        vec2 = Gf.Vec3d(0, 1, 0)
        self.assertAlmostEqual(MathUtil.get_angle_between(vec1, vec2), 90.0)

        # Test opposite vectors (180 degrees)
        vec2 = Gf.Vec3d(-1, 0, 0)
        self.assertAlmostEqual(MathUtil.get_angle_between(vec1, vec2), 180.0)

        # Test 45 degree angle
        vec2 = Gf.Vec3d(1, 1, 0).GetNormalized()
        self.assertAlmostEqual(MathUtil.get_angle_between(vec1, vec2), 45.0)

    async def test_get_euclidean_distance(self):
        """Test get_euclidean_distance function with different point types."""
        # Test 2D points
        point1_2d = Gf.Vec2d(0, 0)
        point2_2d = Gf.Vec2d(3, 4)
        self.assertAlmostEqual(MathUtil.get_euclidean_distance(point1_2d, point2_2d), 5.0)

        # Test 3D points
        point1_3d = Gf.Vec3d(0, 0, 0)
        point2_3d = Gf.Vec3d(1, 1, 1)
        self.assertAlmostEqual(MathUtil.get_euclidean_distance(point1_3d, point2_3d), math.sqrt(3))

        # Test 4D points
        point1_4d = Gf.Vec4d(0, 0, 0, 0)
        point2_4d = Gf.Vec4d(1, 1, 1, 1)
        self.assertAlmostEqual(MathUtil.get_euclidean_distance(point1_4d, point2_4d), math.sqrt(4))

        # Test mismatched dimensions
        with self.assertRaises(ValueError):
            MathUtil.get_euclidean_distance(point1_2d, point1_3d)

    async def test_get_quaternion_distance(self):
        """Test get_quaternion_distance function."""
        # Test identical rotations (0 degrees)
        q1 = Gf.Quatd(1.0, 0.0, 0.0, 0.0)  # Identity quaternion
        q2 = Gf.Quatd(1.0, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(MathUtil.get_quaternion_distance(q1, q2), 0.0)

        # Test 90-degree rotation around Z-axis
        q2 = Gf.Quatd(math.cos(math.pi / 4), 0.0, 0.0, math.sin(math.pi / 4))
        self.assertAlmostEqual(MathUtil.get_quaternion_distance(q1, q2), 90.0)

        # Test 180-degree rotation around Z-axis
        q2 = Gf.Quatd(0.0, 0.0, 0.0, 1.0)
        self.assertAlmostEqual(abs(MathUtil.get_quaternion_distance(q1, q2)), 180.0)

    async def test_get_quaternion_sign(self):
        """Test get_quaternion_sign function."""
        # Test positive rotation around Z-axis (45 degrees)
        rotation = Gf.Rotation(Gf.Vec3d(0, 0, 1), 90)
        quat = rotation.GetQuat()
        self.assertEqual(MathUtil.get_quaternion_sign(quat), 1)

        # Test negative rotation around Z-axis (-90 degrees)
        rotation = Gf.Rotation(Gf.Vec3d(0, 0, 1), -90)
        quat = rotation.GetQuat()
        self.assertEqual(MathUtil.get_quaternion_sign(quat), -1)

        # Test with custom rotation axis (Y-axis, 60 degrees)
        custom_axis = Gf.Vec3d(0, 1, 0)
        rotation = Gf.Rotation(custom_axis, 60)
        quat = rotation.GetQuat()
        self.assertEqual(MathUtil.get_quaternion_sign(quat, custom_axis), 1)

    async def test_rotate_and_normalize_vector(self):
        """Test rotate_and_normalize_vector function."""
        # Test with identity rotation
        vector = Gf.Vec3d(0, 1, 0)  # Forward is along Y-axis
        rotation = Gf.Rotation(Gf.Vec3d(0, 0, 1), 0)  # Identity rotation
        result = MathUtil.rotate_and_normalize_vector(rotation, vector)
        self.assertLess((result - vector).GetLength() ,  1e-6)

        # Test with 90-degree rotation around Z-axis
        rotation = Gf.Rotation(Gf.Vec3d(0, 0, 1), 90)
        result = MathUtil.rotate_and_normalize_vector(rotation, vector)
        expected = Gf.Vec3d(-1, 0, 0)
        self.assertLess((result - expected).GetLength() ,  1e-6)

        # Test with arbitrary axis and angle
        rotation = Gf.Rotation(Gf.Vec3d(1, 1, 1).GetNormalized(), 45)
        result = MathUtil.rotate_and_normalize_vector(rotation, vector)
        expected = Gf.Vec3d(-0.310617, 0.804738, 0.505879)
        self.assertLess((result - expected).GetLength() ,  1e-6)

    async def test_compute_stationary_distribution_ergodic(self):
        """Ergodic chain should converge to unique stationary distribution."""
        # Simple 2-state chain
        P = np.array([[0.9, 0.1],
                      [0.2, 0.8]], dtype=float)
        pi = MathNumpyUtil.compute_stationary_distribution(P)
        # Validate πP ≈ π and sum ≈ 1
        self.assertLess(np.linalg.norm(pi @ P - pi, ord=1), 1e-10)
        self.assertAlmostEqual(float(pi.sum()), 1.0, places=12)
        # Closed-form solution: π = [2/3, 1/3]
        self.assertAlmostEqual(pi[0], 2/3, places=3)
        self.assertAlmostEqual(pi[1], 1/3, places=3)

    async def test_compute_stationary_distribution_absorbing(self):
        """Absorbing chain should put all mass on absorbing state(s)."""
        # State 1 is absorbing
        P = np.array([[0.5, 0.5],
                      [0.0, 1.0]], dtype=float)
        pi = MathNumpyUtil.compute_stationary_distribution(P)
        self.assertLess(np.linalg.norm(pi @ P - pi, ord=1), 1e-10)
        self.assertAlmostEqual(float(pi.sum()), 1.0, places=12)
        # Any stationary distribution must have all mass on absorbing state
        self.assertAlmostEqual(pi[0] + pi[1], 1.0, places=12)
        self.assertAlmostEqual(pi[1], 1.0, places=6)

    async def test_compute_stationary_distribution_invalid_inputs(self):
        """Invalid matrices should raise ValueError."""
        with self.assertRaises(ValueError):
            MathNumpyUtil.compute_stationary_distribution([[1.0, 0.0, 0.0], [0.5, 0.5, 0.0]])  # non-square
        with self.assertRaises(ValueError):
            MathNumpyUtil.compute_stationary_distribution([[-0.1, 1.1], [0.0, 1.0]])  # negative
        with self.assertRaises(ValueError):
            MathNumpyUtil.compute_stationary_distribution([[0.5, 0.6], [0.4, 0.7]])  # rows not summing to 1
