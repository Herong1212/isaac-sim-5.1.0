from __future__ import annotations
import numpy as np
from ..utils import CameraGeneralUtil
from isaacsim.sensors.rtx.placement.camera_placement.camera_placement_manager import (
    CameraPlacementManager,
)
from typing import Optional, List, Tuple
from isaacsim.sensors.rtx.placement.camera_placement.camera_placement_helper import CameraPlacementHelper
import carb


class CameraClusterHelper:
    @classmethod
    def compute_camera_fov_center(cls, camera_path):
        """calculate a camera fov's center point"""
        camera_placement_manager = CameraPlacementManager.get_instance()
        covered_point_list, _, _ = camera_placement_manager.calculate_existing_camera_coverage(camera_path=camera_path)
        calculate_average_point = np.mean(covered_point_list, axis=0)

        x, y = calculate_average_point

        average_point = (int(x), int(y))
        return average_point

    @classmethod
    def get_camera_matrix(cls, camera_path):
        """get a matrix with camera covered element signed with 1"""
        camera_placement_manager = CameraPlacementManager.get_instance()
        x_size, y_size = camera_placement_manager.get_section_size()
        covered_point_list, _, _ = camera_placement_manager.calculate_existing_camera_coverage(camera_path=camera_path)
        camera_matrix = np.zeros((x_size, y_size), dtype=int)

        for element in covered_point_list:
            x, y = element
            camera_matrix[x][y] = 1

        return camera_matrix

    @classmethod
    def get_fov_polygon_area(cls, fov_matrix):
        """
        Calculate the area of a simple polygon given its vertices.

        Parameters:
        vertices (list or array-like): A list or array of (x, y) pairs.

        Returns:
        float: The area of the polygon.
        """

        x_size = len(fov_matrix)
        y_size = len(fov_matrix[0])

        counter = 0

        for x in range(x_size):
            for y in range(y_size):
                if fov_matrix[x][y] == 1:
                    counter = counter + 1

        return counter

    @classmethod
    def compute_intersection_volume(cls, matrix_1, matrix_2):
        """
        Calculate the area of a simple polygon given its vertices.

        Parameters:
        vertices (list or array-like): A list or array of (x, y) pairs.

        Returns:
        float: The area of the polygon.
        """

        x_size = len(matrix_1)
        y_size = len(matrix_1[0])

        counter = 0

        for x in range(x_size):
            for y in range(y_size):
                if matrix_1[x][y] == 1 and matrix_2[x][y] == matrix_1[x][y]:
                    counter = counter + 1

        return counter

    @classmethod
    def get_unioned_matrix(cls, matrix_list):
        """
        get the unioned_matrix within a list
        """
        camera_placement_manager = CameraPlacementManager.get_instance()
        x_size, y_size = camera_placement_manager.get_section_size()
        union_matrix = np.zeros((x_size, y_size), dtype=int)

        for matrix in matrix_list:

            for x in range(x_size):
                for y in range(y_size):
                    if matrix[x][y] == 1:
                        union_matrix[x][y] = 1

        return union_matrix

    # # Function to compute frustum overlaps
    @classmethod
    def compute_overlap(cls, matrix_1, matrix_2):
        """Compute intersection volume of frustums"""
        V_i = cls.get_fov_polygon_area(matrix_1)
        V_j = cls.get_fov_polygon_area(matrix_2)
        V_ij = cls.compute_intersection_volume(matrix_1, matrix_2)
        P_ij = (V_ij / ((V_i + V_j) / 2)) * 100
        return P_ij

    @classmethod
    def shortest_distance(cls, point_list, target_point):
        """
        Calculate the shortest distance between a target 2D point and a list of 2D points.

        Parameters:
        - point_list: list of tuples or numpy array of shape (n_points, 2)
        - target_point: tuple or numpy array of shape (2,)

        Returns:
        - min_distance: float, the shortest distance
        """
        # Convert inputs to numpy arrays for vectorized operations
        points = np.array(point_list)
        target = np.array(target_point)

        # Compute the Euclidean distances from the target to each point
        distances = np.linalg.norm(points - target, axis=1)

        # Find and return the minimal distance
        min_distance = np.min(distances)
        return min_distance

    @classmethod
    def longest_distance_sum(cls, point_list):
        """average distance within the points in a cluster"""
        max_distance_sum = 0
        for point in point_list:
            distance = cls.longest_distance(point_list=point_list, target_point=point)
            max_distance_sum = max_distance_sum + distance
        return max_distance_sum

    @classmethod
    def longest_distance(cls, point_list, target_point):
        """
        Calculate the shortest distance between a target 2D point and a list of 2D points.

        Parameters:
        - point_list: list of tuples or numpy array of shape (n_points, 2)
        - target_point: tuple or numpy array of shape (2,)

        Returns:
        - min_distance: float, the shortest distance
        """
        # Convert inputs to numpy arrays for vectorized operations
        points = np.array(point_list)
        target = np.array(target_point)

        # Compute the Euclidean distances from the target to each point
        distances = np.linalg.norm(points - target, axis=1)

        # Find and return the minimal distance
        min_distance = np.max(distances)
        return min_distance

    @classmethod
    def split_number(cls, N, K):
        """
        Splits the number N into K parts as evenly as possible.

        Parameters:
        - N (int): The number to be split.
        - K (int): The number of parts to split into.

        Returns:
        - parts (list): A list of integers representing the split parts.
        """
        if K <= 0:
            raise ValueError("K must be a positive integer.")
        if N < 0:
            raise ValueError("N must be a non-negative integer.")
        if K > N:
            # If K > N, the best we can do is to have N ones and K-N zeros
            parts = [1] * N + [0] * (K - N)
            return parts

        base = N // K
        remainder = N % K

        # Initialize all parts to the base value
        parts = [base] * K

        # Distribute the remainder by adding 1 to the first 'remainder' parts
        for i in range(remainder):
            parts[i] += 1

        return parts


class CameraFovInfo:
    def __init__(self, camera_fov_matrix=None, center_point=None, category=None):
        self.camera_fov_matrix = camera_fov_matrix
        self.center_point = center_point
        self.category = category

    def set_center_point(self, target_point):
        self.center_point = target_point

    def set_camera_fov_matrix(self, camera_matrix):
        self.camera_fov_matrix = camera_matrix

    def set_categroy(self, target_category):
        self.category = target_category

    def get_center_point(self):
        return self.center_point

    def get_camera_fov_matrix(self):
        return self.camera_fov_matrix

    def get_categroy(self):
        return self.category


class CameraClusterManager:

    __instance: CameraClusterManager = None

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError("Only one instance of CameraClusterManager is allowed")
        self._camera_info_dict: dict[str, CameraFovInfo] = {}
        self.clusters: dict[int, list[str]] = {}
        CameraClusterManager.__instance = self

    def destroy(self):
        CameraClusterManager.__instance = None

    def __del__(self):
        self.destroy()

    @classmethod
    def get_instance(cls) -> CameraClusterManager:
        if cls.__instance is None:
            CameraClusterManager()
        return cls.__instance

    def all_categoried(self):
        for key, item in self._camera_info_dict.items():
            if item.get_categroy() is None:
                return False

        return True

    def get_camera_num(self):
        return len(self._camera_info_dict.keys())

    def get_uncategoried_camera(self):
        """get camera without category"""
        result = []
        for key, item in self._camera_info_dict.items():
            if item.get_categroy() is None:
                result.append(key)

        return result

    def categorize_camera(self, camera_path, category):
        """set camera's category"""
        camera_info = self._camera_info_dict[camera_path]
        camera_info.set_categroy(category)

    def get_camera_matrix(self, camera_path):
        """get camera's fov matrix"""
        camera_info = self._camera_info_dict[camera_path]
        return camera_info.get_camera_fov_matrix()

    def get_camera_center_point(self, camera_path):
        """get camera's fov center point"""
        camera_info = self._camera_info_dict[camera_path]
        return camera_info.get_center_point()

    def initialize_camera_info(self):
        """initialize all camera info"""
        # each camera's info contains cateogry, fov matrix, and fov center.
        camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
        camera_prim_path_list = [str(camera_prim.GetPrimPath()) for camera_prim in camera_prim_list]
        for camera_path in camera_prim_path_list:
            self._camera_info_dict[camera_path] = CameraFovInfo()
            center_point = CameraClusterHelper.compute_camera_fov_center(camera_path)
            camera_matrix = CameraClusterHelper.get_camera_matrix(camera_path)
            camera_info = self._camera_info_dict[camera_path]
            camera_info.set_center_point(center_point)
            camera_info.set_camera_fov_matrix(camera_matrix)

    def get_union_matrix(self, camera_path_list):
        """get the unioned fov matrix"""
        matrix_list = []
        for camera_path in camera_path_list:
            matrix_list.append(self.get_camera_matrix(camera_path))

        union_matrix = CameraClusterHelper.get_unioned_matrix(matrix_list)
        return union_matrix

    def get_max_overlap_camera(self, target_camera_path_list: list):
        """get camera with the maximum fov overlap"""
        # try to fetch all camera without categroy
        max_overlap = 0

        camera_list = self.get_uncategoried_camera()
        max_overlap_camera = camera_list[0]
        union_matrix = self.get_union_matrix(target_camera_path_list)
        for camera_path in camera_list:
            camera_matrix = self.get_camera_matrix(camera_path)

            overlap = CameraClusterHelper.compute_overlap(union_matrix, camera_matrix)
            if overlap > max_overlap:
                max_overlap = overlap
                max_overlap_camera = camera_path

        return max_overlap, max_overlap_camera

    def get_min_overlap_camera(self, target_camera_path_list: list):
        """get camera with the maximum fov overlap"""
        # try to fetch all camera without categroy
        min_overlap = 10000

        camera_list = self.get_uncategoried_camera()
        min_overlap_camera = camera_list[0]
        union_matrix = self.get_union_matrix(target_camera_path_list)
        for camera_path in camera_list:
            camera_matrix = self.get_camera_matrix(camera_path)

            overlap = CameraClusterHelper.compute_overlap(union_matrix, camera_matrix)
            if overlap < min_overlap:
                min_overlap = overlap
                min_overlap_camera = camera_path

        return min_overlap, min_overlap_camera

    def get_closest_center_camera(self, target_camera_path_list: list):
        min_distance = 100000
        camera_list = self.get_uncategoried_camera()
        camera_center_list = []
        candidate = camera_list[0]
        for camera_path in target_camera_path_list:
            camera_center = self.get_camera_center_point(camera_path)
            camera_center_list.append(camera_center)

        for camera_path in camera_list:
            camera_center = self.get_camera_center_point(camera_path)
            distance = CameraClusterHelper.shortest_distance(target_point=camera_center, point_list=camera_center_list)
            if distance < min_distance:
                min_distance = distance
                candidate = camera_path

        return candidate

    def get_furthest_center_camera(self, target_camera_path_list: list):
        max_distance = -1
        camera_list = self.get_uncategoried_camera()
        camera_center_list = []
        candidate = camera_list[0]
        for camera_path in target_camera_path_list:
            camera_center = self.get_camera_center_point(camera_path)
            camera_center_list.append(camera_center)

        for camera_path in camera_list:
            camera_center = self.get_camera_center_point(camera_path)
            distance = CameraClusterHelper.shortest_distance(target_point=camera_center, point_list=camera_center_list)
            if distance > max_distance:
                max_distance = distance
                candidate = camera_path

        return candidate

    def pick_closest_camera(self, target_camera_path_list):
        """pick the closet camera toward the target camera group"""
        # try to fetch the camera that has the largest overlap
        max_overlap, candidate = self.get_max_overlap_camera(target_camera_path_list)
        if max_overlap > 0:
            return candidate

        candidate = self.get_closest_center_camera(target_camera_path_list=target_camera_path_list)

        return candidate

    def pick_furthest_camera(self, target_camera_path_list):
        """pick the furthest camera toward the target camera group"""
        # try to fetch the camera that has the largest overlap
        min_overlap, candidate = self.get_min_overlap_camera(target_camera_path_list)
        if min_overlap == 0:
            return candidate

        candidate = self.get_furthest_center_camera(target_camera_path_list=target_camera_path_list)
        return candidate

    def generate_index_mask(self):

        camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
        camera_prim_path_list = list([str(camera_prim.GetPrimPath()) for camera_prim in camera_prim_list])
        index_mask = [0] * len(camera_prim_path_list)
        for key, camera_list in self.clusters.items():
            for camera_path in camera_list:
                index = camera_prim_path_list.index(camera_path)
                index_mask[index] = key

        return index_mask

    def get_cluster_num(self):
        return len(self.clusters.keys())

    def evaluate_point_scatter(self, camera_list):
        """calculate the point cluster"""
        point_list = [self.get_camera_center_point(camera_path) for camera_path in camera_list]
        value = CameraClusterHelper.longest_distance_sum(point_list) / len(point_list)
        return value

    def refine_cluster_step(self):
        """switch the cluster's element in pair, so that the compactness store is less"""
        group_counter = self.get_cluster_num()

        for i in range(group_counter):
            for j in range(i + 1, group_counter):
                target_group_one = self.clusters[i]
                target_group_two = self.clusters[j]
                # evaluate two target group's point scatter
                distance_one = self.evaluate_point_scatter(target_group_one)
                distance_two = self.evaluate_point_scatter(target_group_two)
                # aiming at reduce/average the distance within the cluster, therefore using max value instead of sum
                distance_sum = max(distance_one, distance_two)
                max_improvement = 0
                best_switch = None

                for x in range(len(target_group_one)):
                    for y in range(len(target_group_two)):
                        # switch one arbitrary element between two cluster
                        delta_target_group_one = target_group_one[:x] + target_group_one[x + 1 :]
                        delta_target_group_one.append(target_group_two[y])
                        delta_target_group_two = target_group_two[:y] + target_group_two[y + 1 :]
                        delta_target_group_two.append(target_group_one[x])
                        # reevaluate  the cluster
                        delta_distance_one = self.evaluate_point_scatter(delta_target_group_one)
                        delta_distance_two = self.evaluate_point_scatter(delta_target_group_two)
                        # calculate the improvement
                        improvment = distance_sum - max(delta_distance_one, delta_distance_two)
                        # record the best switch
                        if improvment > max_improvement:
                            max_improvement = improvment
                            best_switch = (x, y)

                if best_switch is not None:
                    # switching elements between two cluste
                    x, y = best_switch
                    refined_group_one = target_group_one[:x] + target_group_one[x + 1 :]
                    refined_group_one.append(target_group_two[y])
                    refined_group_two = target_group_two[:y] + target_group_two[y + 1 :]
                    refined_group_two.append(target_group_one[x])

                    self.clusters[i] = refined_group_one
                    self.clusters[j] = refined_group_two

    def refine_cluster(self, max_iteration=100):
        """original cluster is generated via pure greedy algo. Improve the cluster via k means"""
        for i in range(max_iteration):
            self.refine_cluster_step()

    def init_cluster_camera_in_stage(self, n_clusters: int = 3, start_point_index=0, target_scope: Optional[List[Tuple[float, float]]] = None):
        camera_placement_manager = CameraPlacementManager.get_instance()
        if not CameraPlacementHelper.validate_scope(target_scope):
            target_scope = None
        camera_placement_manager.initialize_section_status(section_scope=target_scope)
        # clear the cluster data
        self.clusters.clear()
        self.clusters = {}
        # get all camera's path under the camera root prim
        camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
        camera_prim_path_list = list([str(camera_prim.GetPrimPath()) for camera_prim in camera_prim_list])

        self.initialize_camera_info()
        # get total camera num
        camera_num = self.get_camera_num()
        cluster_length_list = CameraClusterHelper.split_number(camera_num, n_clusters)
        cluster_index = 0
        clusters: dict[int, list] = {}
        for i in range(len(cluster_length_list)):
            clusters[i] = []

        first_camera = camera_prim_path_list[start_point_index]
        clusters[cluster_index].append(first_camera)
        self.categorize_camera(camera_path=first_camera, category=cluster_index)

        while not self.all_categoried():

            # Iteratively add the nearest point to the cluster
            while len(clusters[cluster_index]) < cluster_length_list[cluster_index] and not self.all_categoried():
                # Calculate distances from cluster to all unclustered points
                cluster_points = clusters[cluster_index]
                camera_path = self.pick_closest_camera(cluster_points)
                cluster_points.append(camera_path)
                self.categorize_camera(camera_path=camera_path, category=cluster_index)

            if not self.all_categoried():

                cluster_points = clusters[cluster_index]
                temp_path = self.pick_furthest_camera(cluster_points)
                cluster_index = cluster_index + 1
                clusters[cluster_index].append(temp_path)
                self.categorize_camera(camera_path=temp_path, category=cluster_index)
            # find out the next point in the stage to set in the list

        self.clusters = clusters

        return

    def cluster_camera_in_stage(self, n_clusters: int = 3, start_point_index=0, max_iteration=200, target_scope: Optional[List[Tuple[float, float]]] = None):
        # initalize the cluster with the greed algo
        self.init_cluster_camera_in_stage(n_clusters=n_clusters, start_point_index=start_point_index, target_scope=target_scope)
        # refine the cluster by switch two element (camera) between the cluster.
        self.refine_cluster(max_iteration=max_iteration)
        mask = self.generate_index_mask()
        return mask
