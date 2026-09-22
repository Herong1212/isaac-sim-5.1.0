import numpy as np
from typing import List, Dict, Optional, Tuple


class GeomtryUtil:
    """util functions related to geometry calculation"""

    def is_point_in_convex_polygon(point, vertices):
        """
        Determines if a point is inside a convex polygon using the cross product method.

        Parameters:
        - point (list): The point to check, represented as [x, y].
        - vertices (list of lists): The vertices of the polygon in order, each represented as [x, y].

        Returns:
        - bool: True if the point is inside the convex polygon, False otherwise.

        Raises:
        - ValueError: If inputs are not lists, have incorrect dimensions,
                    or if the polygon has fewer than three vertices.
        """
        if len(point) < 2:
            raise ValueError("Point must have at least two numerical values.")

        if len(vertices) < 3:
            raise ValueError("Vertices must be a list of at least three points.")

        for idx, vertex in enumerate(vertices):
            if len(vertex) < 2:
                raise ValueError(f"Vertex at index {idx} must have at least two numerical values [x, y].")

        def cross_product(P, Q, R):
            """Calculate the 2D cross product of vectors PQ and PR."""
            return (Q[0] - P[0]) * (R[1] - P[1]) - (Q[1] - P[1]) * (R[0] - P[0])

        num_vertices = len(vertices)
        sign = None

        for i in range(num_vertices):
            P = vertices[i]
            Q = vertices[(i + 1) % num_vertices]
            cross = cross_product(P, Q, point)

            if cross != 0:
                current_sign = cross > 0
                if sign is None:
                    sign = current_sign
                elif sign != current_sign:
                    return False  # Point is outside the convex polygon

        return True if sign is not None else False  # All points are colinear

    def fibonacci_sphere_directions(pitch_range=(-90, 90), yaw_range=(0, 360), num_points: float = 200):
        """
        Generates a specified number of direction unit vectors on a sphere using the Fibonacci Sphere algorithm
        within specified pitch and yaw ranges.

        Parameters:
            num_points (int): Number of direction vectors to generate within the specified ranges.
            pitch_range (tuple): (min_pitch, max_pitch) in degrees.
            yaw_range (tuple): (min_yaw, max_yaw) in degrees.

        Returns:
            np.ndarray: Array of shape (num_points, 3) containing unit vectors.
        """
        # Validate input ranges
        min_pitch, max_pitch = pitch_range
        min_yaw, max_yaw = yaw_range

        if not (-90 <= min_pitch <= 90 and -90 <= max_pitch <= 90):
            raise ValueError("Pitch angles must be between -90 and 90 degrees.")
        if not (0 <= min_yaw <= 360 and 0 <= max_yaw <= 360):
            raise ValueError("Yaw angles must be between 0 and 360 degrees.")

        # Convert pitch and yaw ranges from degrees to radians
        min_pitch_rad = np.radians(min_pitch)
        max_pitch_rad = np.radians(max_pitch)
        min_yaw_rad = np.radians(min_yaw)
        max_yaw_rad = np.radians(max_yaw)

        # Calculate theta (polar angle) range based on pitch
        # Pitch is elevation from the equator: pitch = 90 - theta (in degrees)
        # Therefore, theta = 90 - pitch
        theta_min = np.pi / 2 - max_pitch_rad  # Corresponds to max_pitch
        theta_max = np.pi / 2 - min_pitch_rad  # Corresponds to min_pitch

        # Handle yaw range, considering wrap-around
        yaw_diff = max_yaw_rad - min_yaw_rad
        if yaw_diff <= 0:
            yaw_diff += 2 * np.pi  # Ensure positive difference

        # Generate indices for Fibonacci distribution
        indices = np.arange(0, num_points, dtype=float) + 0.5

        # Golden angle in radians
        golden_angle = np.pi * (3 - np.sqrt(5))  # Approximately 2.39996323 radians

        # Distribute phi using the golden angle
        phi = indices * golden_angle
        phi = phi % (2 * np.pi)  # Wrap phi to [0, 2pi]

        # Distribute z uniformly between z_min and z_max for uniform theta distribution
        z_min = np.cos(theta_max)
        z_max = np.cos(theta_min)
        z = z_min + (z_max - z_min) * indices / num_points  # Linear distribution in z
        theta = np.arccos(z)  # Polar angle

        # Scale phi to fit within the specified yaw range
        if yaw_diff >= 2 * np.pi:
            scaled_phi = phi
        else:
            scaled_phi = min_yaw_rad + (phi / (2 * np.pi)) * yaw_diff
            scaled_phi = scaled_phi % (2 * np.pi)  # Ensure phi is within [0, 2pi]

        # Convert spherical coordinates to Cartesian coordinates
        x = np.sin(theta) * np.cos(scaled_phi)
        y = np.sin(theta) * np.sin(scaled_phi)
        z = np.cos(theta)

        vectors = np.vstack((x, y, z)).T

        return vectors

    def compute_bounding_box(
        polygon_vertices: List[List[float]], dimension: Optional[int] = None
    ) -> List[Tuple[float, float]]:
        """
        Computes the bounding box of a polygon defined by a list of n-dimensional vertices.

        The bounding box is represented as a list of tuples, where each tuple contains the minimum
        and maximum value for a corresponding dimension. Optionally considers only the first `dimension` dimensions.

        Parameters:
            polygon_vertices (List[List[float]]):
                A non-empty list of vertices, where each vertex is a list of numerical coordinates.
                Each vertex must have the same number of dimensions (e.g., all 2D, all 3D).
            dimension (Optional[int]):
                If provided, only the first `dimension` dimensions are considered.

        Returns:
            List[Tuple[float, float]]:
                A list of tuples. Each tuple contains the minimum and maximum value for a dimension.
                For example, [(x_min, x_max), (y_min, y_max), ...].

        Raises:
            ValueError:
                - If `polygon_vertices` is empty.
                - If any vertex does not have at least two coordinates.
                - If vertices have inconsistent dimensions.
                - If any coordinate is non-numerical.
                - If the specified `dimension` exceeds the dimensionality of the vertices.
        """
        if not isinstance(polygon_vertices, list) or not polygon_vertices:
            raise ValueError("Input must be a non-empty list of vertices.")

        # Convert to NumPy array for efficient computation
        try:
            vertices_array = np.array(polygon_vertices, dtype=float)
        except (ValueError, TypeError) as e:
            raise ValueError(f"All coordinates must be numerical values. {e}")

        if vertices_array.ndim != 2:
            raise ValueError("Each vertex must be a one-dimensional list of coordinates.")

        num_points, num_dimensions = vertices_array.shape

        if num_dimensions < 2:
            raise ValueError("Each vertex must have at least two coordinates (x and y).")

        # Adjust the number of dimensions to consider
        if dimension is None:
            dimension = num_dimensions
        elif dimension > num_dimensions:
            raise ValueError(f"Specified dimension {dimension} exceeds vertex dimensionality {num_dimensions}.")

        # Restrict to the first `dimension` dimensions
        vertices_array = vertices_array[:, :dimension]

        # Compute min and max for each dimension
        mins = np.min(vertices_array, axis=0)
        maxs = np.max(vertices_array, axis=0)

        # Construct the list of tuples
        bounding_box = [(mins[dim], maxs[dim]) for dim in range(dimension)]

        return bounding_box
