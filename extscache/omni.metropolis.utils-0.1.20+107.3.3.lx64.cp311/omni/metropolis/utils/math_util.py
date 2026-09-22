import sys
from typing import Iterable, List, Optional, Sequence, Tuple, Union
import numpy as np
import math
from pxr import Gf


# TODO METROPERF-822: Add use comments and consider reorganizing util functions to different util classes
class MathUtil:
    # TODO METROPERF-818: Refactor into an interpolate class with linear being a subclass
    @staticmethod
    def lerp(a, b, t):
        return a + (b - a) * t

    @staticmethod
    def is_colinear(a, b, c, tol=1e-6):
        """check if three points are colinear"""
        ab = b - a
        ac = c - a
        cross_product = np.cross(ab, ac)
        return np.linalg.norm(cross_product) < tol

    @staticmethod
    def is_coplanar(a, b, c, d, tol=1e-6):
        """check if four points are coplanar"""
        ab = b - a
        ac = c - a
        ad = d - a
        volume = np.dot(ad, np.cross(ab, ac))
        return abs(volume) < tol

    @staticmethod
    def is_a_valid_stochastic_matrix(matrix):
        matrix = np.array(matrix)
        tolerance = 1e-4
        # Check if all entries are non-negative
        if np.any(matrix < 0):
            return False

        # Check whether the sum of the row is equal to 1 with a small tolerance
        row_sums = np.sum(matrix, axis=1)
        if not np.all(np.abs(row_sums - 1) < tolerance):
            return False
        return True

    @staticmethod
    def get_rotation_angle_difference(angle_a, angle_b):
        angle_diff = abs(angle_a - angle_b)
        return min(angle_diff, 360 - angle_diff)

    # TODO METROPERF-818: Design a clustering class that operates on objects that need to be classified
    # and runs with respect to a function expressing similarity between a pair of objects.
    # The output is a clustering of the objects with respect to the similarity measure.
    # group points in certain number of group base on their scatter
    @staticmethod
    def simple_k_means(all_points, num_points_to_select, max_iterations=100, seed=None):
        rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()

        points_array = np.array(all_points)

        centroids = points_array[rng.choice(points_array.shape[0], num_points_to_select, replace=False)]

        for _ in range(max_iterations):
            distances = np.linalg.norm(points_array[:, np.newaxis, :] - centroids, axis=2)
            cluster_indices = np.argmin(distances, axis=1)
            new_centroids = np.array(
                [points_array[cluster_indices == i].mean(axis=0) for i in range(num_points_to_select)]
            )
            if np.allclose(centroids, new_centroids):
                break
            centroids = new_centroids

        return cluster_indices, centroids

    @staticmethod
    def find_closest_points(points, target_points):
        closest_points = []
        min_distances = []
        for target_point in target_points:
            # Calculate the Euclidean distance between the target point and each point in the array
            distances = [np.linalg.norm(np.array(target_point) - np.array(point)) for point in points]
            # Find the index of the point with the minimum distance
            closest_index = np.argmin(distances)
            # Append the closest point and its distance to the respective lists
            closest_points.append(points[closest_index])
            min_distances.append(distances[closest_index])
        return closest_points, min_distances

    @staticmethod
    def limit_float(value):
        """
        Limits the float value to the maximum and minimum values supported by Python.

        Args:
            value (float): The float value to be checked and limited.

        Returns:
            float: The value constrained within the supported range.
        """
        max_float = sys.float_info.max  # Maximum representable float
        min_float = -max_float  # Minimum representable float

        if value > max_float:
            return max_float
        elif value < min_float:
            return min_float
        else:
            return value

    @staticmethod
    def get_angle_between(vec1: Gf.Vec3d, vec2: Gf.Vec3d) -> float:
        """
        Calculate the angle between two vectors.
        The angle will be between -180 and 180 degrees.

        Args:
            vec1 (Gf.Vec3d): The first vector.
            vec2 (Gf.Vec3d): The second vector.

        Returns:
            float: The angle in degrees between the two vectors.
        """
        rotation = Gf.Rotation(Gf.Vec3d(vec1), Gf.Vec3d(vec2))
        angle = rotation.GetAngle()

        # angle is always between 0-180 so we need the following to decide the direction.
        if rotation.GetAxis()[2] < 0:
            return -angle
        else:
            return angle

    @staticmethod
    def get_euclidean_distance(
        point1: Union[Gf.Vec2d, Gf.Vec3d, Gf.Vec4d], point2: Union[Gf.Vec2d, Gf.Vec3d, Gf.Vec4d]
    ) -> float:
        """
        Compute the distance between two points. Supports both 2D and 3D points.

        Args:
            point1 (Union[Gf.Vec2d, Gf.Vec3d, Gf.Vec4d]): First point in 2D or 3D or 4D space
            point2 (Union[Gf.Vec2d, Gf.Vec3d, Gf.Vec4d]): Second point in 2D or 3D or 4D space

        Returns:
            float: The Euclidean distance between the points

        Note:
            Both points must be of the same dimension (either both 2D or both 3D or both 4D)
        """
        if not isinstance(point1, type(point2)):
            raise ValueError("point1 and point2 must be the same type")
        return (point1 - point2).GetLength()

    @staticmethod
    def get_quaternion_distance(q1: Gf.Quatd, q2: Gf.Quatd) -> float:
        """
        Compute the angular distance between two quaternions representing 3D rotations in degrees.

        Args:
            q1 (Gf.Quatd): First quaternion rotation
            q2 (Gf.Quatd): Second quaternion rotation

        Returns:
            float: The signed angular distance in degrees between the two rotations
        """
        # Normalize both quaternions to ensure they represent valid rotations
        q1 = q1.GetNormalized()
        q2 = q2.GetNormalized()

        # Calculate the dot product between quaternions
        # This is done component-wise: real part + imaginary x,y,z parts
        dot_product = (
            q1.GetReal() * q2.GetReal()  # Real component
            + q1.GetImaginary()[0] * q2.GetImaginary()[0]  # x component
            + q1.GetImaginary()[1] * q2.GetImaginary()[1]  # y component
            + q1.GetImaginary()[2] * q2.GetImaginary()[2]  # z component
        )

        # Calculate the quaternion difference (q1^-1 * q2)
        # This gives us a single quaternion representing the rotation from q1 to q2
        quat_diff = q1.GetInverse() * q2

        # Clamp the real component to [-1, 1] to avoid numerical issues
        dot_product = max(min(quat_diff.GetReal(), 1.0), -1.0)

        # Convert to angle using the quaternion angle formula
        # Note: The factor of 2 is because quaternions represent half-angles
        angle_radians = math.acos(2 * (dot_product) ** 2 - 1)

        # Get the sign of the rotation based on the rotation axis
        # and convert to degrees for the final result
        return MathUtil.get_quaternion_sign(quat_diff) * math.degrees(angle_radians)

    @staticmethod
    def get_quaternion_sign(quat: Gf.Quatd, rot_axis: Gf.Vec3d = Gf.Vec3d(0, 0, 1)) -> int:
        """
        Determine the sign of a quaternion rotation relative to a reference axis using the right hand rule.

        Args:
            quat (Gf.Quatd): The quaternion rotation to analyze
            rot_axis (Gf.Vec3d): Reference axis to determine rotation direction,
                                defaults to positive Z-axis (0, 0, 1)

        Returns:
            int: 1 for positive rotation, -1 for negative rotation around the reference axis
        """
        # Normalize the quaternion to ensure valid rotation representation
        quat = quat.GetNormalized()

        # Normalize the rotation axis to ensure unit length
        rot_axis = rot_axis.GetNormalized()

        # Extract the vector (imaginary) part of the quaternion
        quat_vec = quat.GetImaginary()

        # Extract the scalar (real) part of the quaternion
        quat_scale = quat.GetReal()

        # Calculate the projection of quaternion vector onto the reference axis
        # This tells us how aligned the rotation is with our reference axis
        projection = quat_vec * rot_axis

        # In quaternion mathematics, the sign of (projection * real) indicates rotation direction
        # negative product means positive (counterclockwise) rotation
        is_positive_rotation = projection * quat_scale > 0
        return 1 if is_positive_rotation else -1

    @staticmethod
    def rotate_and_normalize_vector(rotation: Gf.Rotation, vector: Gf.Vec3d) -> Gf.Vec3d:
        """
        Applies a rotation to a vector and normalizes the result.

        Args:
            rotation (Gf.Rotation): The rotation to apply.
            vector (Gf.Vec3d): The vector to be rotated and normalized.

        Returns:
            Gf.Vec3d: The resulting vector after rotation and normalization.
        """
        return rotation.TransformDir(vector).GetNormalized()


class MathNumpyUtil:
    """return result would be numpy array"""

    @staticmethod
    def calculate_centroid(
        points: Union[Iterable[Sequence[Union[int, float]]], Sequence[Sequence[Union[int, float]]]]
    ) -> Tuple[float, ...]:
        """
        Calculate the centroid (center point) of a list of n-dimensional points using NumPy.

        Parameters:
            points (Iterable[Sequence[Union[int, float]]]):
                A non-empty iterable of points, where each point is an iterable (list or tuple)
                of numerical coordinates.

        Returns:
            tuple: The centroid point as a tuple of coordinates.

        Raises:
            ValueError: If the input is not a non-empty iterable of points,
                        if points have inconsistent dimensions,
                        or if any coordinate is non-numerical.
        """
        if not isinstance(points, Iterable) or not points:
            raise ValueError("Input must be a non-empty iterable of points.")

        # Convert to NumPy array and ensure it's 2D
        try:
            array = np.array(points, dtype=float)
        except (ValueError, TypeError) as e:
            raise ValueError("All coordinates must be numerical.") from e

        if array.ndim != 2:
            raise ValueError("Each point must have the same number of dimensions.")

        # Calculate the centroid using NumPy's mean function along axis 0
        return np.mean(array, axis=0)

    @staticmethod
    def normalize_vector(v: Union[Iterable[Union[int, float]], np.ndarray]) -> Tuple[float, ...]:
        """
        Normalize a vector to have a magnitude of 1.

        Parameters:
            v (Iterable[Union[int, float]] or np.ndarray):
                The input vector, which can be a list, tuple, or NumPy array of numerical coordinates.

        Returns:
            tuple: The normalized unit vector as a tuple of floats.

        Raises:
            ValueError: If the input vector has zero magnitude or if input is invalid.
            TypeError: If the input contains non-numerical values.
        """
        if not isinstance(v, (Iterable, np.ndarray)):
            raise TypeError("Input must be an iterable (list, tuple) or a NumPy array of numerical values.")

        try:
            vector = np.array(v, dtype=float)
        except (ValueError, TypeError) as e:
            raise ValueError("All elements of the vector must be numerical.") from e

        if vector.ndim != 1:
            raise ValueError("Input vector must be one-dimensional.")

        norm = np.linalg.norm(vector)
        if norm == 0:
            raise ValueError("Cannot normalize a zero vector.")

        return vector / norm

    @staticmethod
    def is_point_within_scope_nd(
        target_point: Sequence[float], scope: List[Tuple[float, float]], dimension: Optional[int] = None
    ) -> bool:
        """
        Determines whether a given N-dimensional point lies within a specified multi-dimensional scope
        using NumPy for efficiency. Optionally considers only the first `dimension` dimensions.

        Parameters:
            target_point (Sequence[float]): The coordinates of the point to check.
            scope (List[Tuple[float, float]]): A list where each tuple defines (min, max) for a dimension.
            dimension (Optional[int]): If provided, considers only the first `dimension` dimensions.

        Returns:
            bool: True if the point is within the scope across the specified dimensions, False otherwise.

        Raises:
            ValueError: If the specified `dimension` exceeds the actual dimensions of `target_point` or `scope`.
        """
        target = np.array(target_point, dtype=float)
        scope_arr = np.array(scope, dtype=float).reshape(-1, 2)  # Ensure it's a 2D array

        if dimension is None:
            dimension = target.shape[0]

        if dimension > target.shape[0] or dimension > scope_arr.shape[0]:
            raise ValueError(
                f"Dimension {dimension} exceeds the number of dimensions in target_point "
                f"({target.shape[0]}) or scope ({scope_arr.shape[0]})."
            )

        target = target[:dimension]
        scope_arr = scope_arr[:dimension]

        min_vals = scope_arr[:, 0]
        max_vals = scope_arr[:, 1]

        within = np.logical_and(target >= min_vals, target <= max_vals)
        return np.all(within)

    @staticmethod
    def intersect_with_plane(
        start_point: np.ndarray, vector: np.ndarray, plane_height: float = 0
    ) -> Tuple[float, Optional[np.ndarray]]:
        """
        Calculate the intersection of a ray with a ground plane (z = plane_height).

        Args:
            point (np.ndarray): A 3D point on the ray, represented as a numpy array of shape (3,).
            vector (np.ndarray): The direction vector of the ray, represented as a numpy array of shape (3,).
            plane_height (float): The height of the ground plane along the z-axis (default is 0).

        Returns:
            Tuple[float, Optional[np.ndarray]]:
                - t (float): The scalar value such that the intersection point is `point + t * vector`.
                - ground_point (Optional[np.ndarray]): The 3D coordinates of the intersection point if it exists,
                otherwise `None` if the ray does not intersect the ground plane in the positive direction.
        """
        # Avoid division by zero if the vector's z-component is zero
        if vector[2] == 0:
            return float("inf"), None  # No intersection with the plane

        # Calculate t, the parameter for the ray equation
        t = (plane_height - start_point[2]) / vector[2]

        # If t is negative, the intersection is "behind" the ray's origin
        if t < 0:
            return t, None

        # Calculate the ground point using the ray equation
        ground_point = start_point + t * vector
        return t, ground_point

    @staticmethod
    def split_range_with_step(min_value: float, max_value: float, step_size: float) -> List[float]:
        """
        Generates a list of values using NumPy's arange, ensuring max is included.

        Parameters:
            min_value (float): The starting value .
            max_value (float): The maximum value to include.
            step (float): The increment between each value.

        Returns:
            List[float]: A list of values from min_value to max_value.

        Raises:
            ValueError: If step is not positive or if min_value is greater than max_value.
        """
        if step_size <= 0:
            raise ValueError("Step must be a positive number.")
        if min_value > max_value:
            raise ValueError("min_value cannot be greater than max_value.")

        # Use numpy's arange to generate values
        distance_values = list(np.arange(min_value, max_value, step_size))

        # Ensure max_distance is included
        if not distance_values or distance_values[-1] < max_value:
            distance_values.append(max_value)

        return distance_values

    @staticmethod
    def compute_stationary_distribution(
        transition_matrix: Union[np.ndarray, List[List[float]]],
        tol: float = 1e-12,
        max_iters: int = 10000,
        initial_distribution: Optional[Union[np.ndarray, List[float]]] = None,
    ) -> np.ndarray:
        """
        Compute the stationary distribution for a finite Markov chain with a row-stochastic
        transition matrix using power iteration, with a robust eigenvector fallback.

        Args:
            transition_matrix: Row-stochastic matrix P where P[i, j] = Pr(state i -> state j).
            tol: Convergence tolerance for L1 difference between successive distributions.
            max_iters: Maximum number of power-iteration steps before falling back to eigen solve.
            initial_distribution: Optional initial probability vector; defaults to uniform.

        Returns:
            np.ndarray: Stationary distribution vector π such that π = π P, π sums to 1.

        Raises:
            ValueError: If the input matrix is not square, has negative entries, or rows do not sum to 1.
        """
        P = np.array(transition_matrix, dtype=float)
        if P.ndim != 2 or P.shape[0] != P.shape[1]:
            raise ValueError("transition_matrix must be a square 2D array")
        if np.any(P < -1e-12):
            raise ValueError("transition_matrix must have non-negative entries")
        # Validate row-stochastic property within a small tolerance
        row_sums = P.sum(axis=1)
        if not np.allclose(row_sums, 1.0, atol=1e-8):
            raise ValueError("transition_matrix rows must sum to 1 within tolerance")

        n = P.shape[0]
        if initial_distribution is None:
            dist = np.ones(n, dtype=float) / n
        else:
            dist = np.array(initial_distribution, dtype=float).reshape(-1)
            if dist.shape[0] != n:
                raise ValueError("initial_distribution size must match transition_matrix size")
            if np.any(dist < 0):
                raise ValueError("initial_distribution must be non-negative")
            s = dist.sum()
            if s <= 0:
                raise ValueError("initial_distribution must have positive sum")
            dist = dist / s

        # Power iteration
        converged = False
        for _ in range(max_iters):
            new_dist = dist @ P
            if np.linalg.norm(new_dist - dist, ord=1) < tol:
                dist = new_dist
                converged = True
                break
            dist = new_dist

        if not converged:
            # Fallback: left eigenvector of P corresponding to eigenvalue 1
            try:
                w, v = np.linalg.eig(P.T)
                idx = int(np.argmin(np.abs(w - 1)))
                vec = np.real(v[:, idx])
                # Ensure non-negative and normalize
                vec = np.maximum(vec, 0)
                if vec.sum() == 0:
                    vec = np.abs(vec)
                if vec.sum() > 0:
                    dist = vec / vec.sum()
            except Exception:
                # Keep last iterate if eig fails
                pass

        # Final normalization for numerical safety
        s = dist.sum()
        if s > 0:
            dist = dist / s
        return dist
