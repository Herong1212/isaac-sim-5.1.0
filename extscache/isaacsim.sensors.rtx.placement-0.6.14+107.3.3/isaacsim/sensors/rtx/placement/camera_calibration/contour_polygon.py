import copy
import heapq
import math
from enum import Enum, IntFlag

import carb


## data structure used to store the contour field
class simple_cf:
    def __init__(self, matrix):
        self.vertex_info = matrix
        self.direction_offset = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        self.rows = len(matrix)
        self.cols = len(matrix[0])

    # given a coordinate in the FOV matrix and a direction. Retrun whether it has connected neighbor
    def get_con(self, x, y, direction: int):
        target_x, target_y = self.get_connect_dir_x_y(x, y, direction)
        return target_x == -1 and target_y == -1

    # give a cooridnate in the FOV matrix, return current region index
    def get_region(self, x, y):
        if x >= 0 and y >= 0 and x < self.rows and y < self.cols:
            return self.vertex_info[x][y]
        return None

    # if two areas are connected in certain direction, then return the coordinate of the neighborhood area
    def get_connect_dir_x_y(self, x, y, direction: int):
        offset_x, offset_y = self.direction_offset[direction]
        target_x = x + offset_x
        target_y = y + offset_y
        # check whether neigborhood element have the same region id
        curr_region_id = self.vertex_info[x][y]
        if target_x >= 0 and target_x < self.rows and target_y >= 0 and target_y < self.cols:
            neighbor_region = self.vertex_info[target_x][target_y]
            if neighbor_region == curr_region_id:
                return target_x, target_y
        else:
            return -1, -1


# data structure to store the outline contour and holes contour of an FOV area
class region_cf:
    def __init__(self):
        self.outline = None
        self.holes = []


class FOVStatus(Enum):
    INACCESSIBLE = -1
    BOUNDARY = -2
    ACCESSIBLE = 0


class RegionStatus(Enum):
    BOUNDARY_REGION = 0
    UNMARKED_REGION = -1
    MARKED_REGION = 1


class DirectionFlags(IntFlag):
    LEFT = 1 << 0  # 0001
    UP = 1 << 1  # 0010
    RIGHT = 1 << 2  # 0100
    DOWN = 1 << 3  # 1000
    ALL = LEFT | UP | RIGHT | DOWN


class FOV:
    @staticmethod
    def mark_boundary(matrix):
        if not matrix:
            return []

        rows, cols = len(matrix), len(matrix[0])
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]

        for i in range(rows):
            for j in range(cols):
                if matrix[i][j] == FOVStatus.INACCESSIBLE.value:
                    continue
                is_boundary = False
                for dx, dy in neighbors:
                    x, y = i + dx, j + dy
                    if x < 0 or x >= rows or y < 0 or y >= cols or matrix[x][y] == FOVStatus.INACCESSIBLE.value:
                        is_boundary = True
                        break
                if is_boundary:
                    matrix[i][j] = FOVStatus.BOUNDARY.value

        return matrix

    # mark seperate region with different numbers
    @staticmethod
    def mark_regions(matrix):
        if not matrix:
            return []

        rows, cols = len(matrix), len(matrix[0])
        region_matrix = [[RegionStatus.UNMARKED_REGION.value] * cols for _ in range(rows)]
        region_id = RegionStatus.MARKED_REGION.value

        def is_valid(x, y):
            return 0 <= x < rows and 0 <= y < cols

        stack = []

        for row in range(rows):
            for col in range(cols):
                # if the position is an unmarked accessible position
                if (
                    matrix[row][col] == FOVStatus.ACCESSIBLE.value
                    and region_matrix[row][col] == RegionStatus.UNMARKED_REGION.value
                ):
                    stack.append((row, col))

                    while stack:
                        x, y = stack.pop()
                        if (
                            not is_valid(x, y)
                            or matrix[x][y] != FOVStatus.ACCESSIBLE.value
                            or region_matrix[x][y] != RegionStatus.UNMARKED_REGION.value
                        ):
                            continue
                        region_matrix[x][y] = region_id

                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            nx, ny = x + dx, y + dy
                            if (
                                is_valid(nx, ny)
                                and matrix[nx][ny] == FOVStatus.ACCESSIBLE.value
                                and region_matrix[nx][ny] == RegionStatus.UNMARKED_REGION.value
                            ):
                                stack.append((nx, ny))

                    region_id += 1

        # mark all the boundary of the region
        for row in range(rows):
            for col in range(cols):
                if matrix[row][col] == FOVStatus.BOUNDARY.value:
                    region_matrix[row][col] = RegionStatus.BOUNDARY_REGION.value

        return region_matrix

    @staticmethod
    def calculate_flags(matrix):
        if matrix is None:
            return None

        rows = len(matrix)
        cols = len(matrix[0])
        flags_matrix = [[0 for _ in range(cols)] for _ in range(rows)]

        for x in range(rows):
            for y in range(cols):
                flags = DirectionFlags(0)

                # Skip boundary or inaccessible regions
                if (
                    matrix[x][y] == RegionStatus.BOUNDARY_REGION.value
                    or matrix[x][y] == RegionStatus.UNMARKED_REGION.value
                ):
                    flags_matrix[x][y] = flags
                    continue

                # Check neighbors in each direction and set the flag accordingly
                if y > 0 and matrix[x][y - 1] == matrix[x][y]:
                    flags |= DirectionFlags.LEFT

                if x > 0 and matrix[x - 1][y] == matrix[x][y]:
                    flags |= DirectionFlags.UP

                if y < cols - 1 and matrix[x][y + 1] == matrix[x][y]:
                    flags |= DirectionFlags.RIGHT

                if x < rows - 1 and matrix[x + 1][y] == matrix[x][y]:
                    flags |= DirectionFlags.DOWN

                # Invert flags to find the absence of connections
                flags ^= DirectionFlags.ALL
                flags_matrix[x][y] = flags

        return flags_matrix

    def get_valid_edge(x, y, dir):
        """select edge base on certain rule to avoid repeat selection"""
        if dir == 0:
            x = x - 1
        if dir == 1:
            x = x - 1
            y = y + 1
        if dir == 2:
            y = y + 1
        return x, y

    def walk_contour(x, y, flags, cf):
        """generate contour vertex list and region index"""
        start_x = x
        start_y = y
        curr_x = x
        curr_y = y
        points = []
        region = cf.get_region(x, y)
        if region == -2:
            return None, None

        dir = 0
        while (flags[x][y] & (1 << dir)) == 0:
            dir = dir + 1
        start_dir = dir
        curr_iter = 0
        while curr_iter < 40000:
            if flags[curr_x][curr_y] & (1 << dir):
                px, py = FOV.get_valid_edge(curr_x, curr_y, dir)
                # if the neigbor vertex on current direction is a boundary, we add it to the list
                points.append([px, py])
                # mark curr direction as visited
                flags[curr_x][curr_y] &= ~(1 << dir)
                # if the accessed point is a boundary, then we change the direction contour_clockwise
                dir = (dir + 1) & 0x3

            else:
                nx, ny = cf.get_connect_dir_x_y(curr_x, curr_y, dir)
                if nx == -1 or ny == -1:
                    return region, points
                curr_x = nx
                curr_y = ny
                # if the accessed point is a boundary, then we change the direction clockwise
                dir = (dir + 3) & 0x3

            if curr_x == start_x and curr_y == start_y and dir == start_dir:
                break

            curr_iter = curr_iter + 1

        return region, points

    def polygon_area(vertices):
        """
        Calculate the area from contour dot list
        """
        if len(vertices) < 3:
            return 0.0

        # if the area value large than 0, then this contour is a the outline of certain region
        # else this contour is a hole in the region
        area = 0.0
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
            area += x1 * y2 - x2 * y1

        area /= 2.0

        return -area

    def build_contour_group(hit_matrix, signed_matrix, contour_index=0, size_threshold=0):
        """from the ray hit matrix, extract contour information for FOV outline and holes"""
        # signe vertex that near inaccessible area to -2
        signed_boundary_matrix = FOV.mark_boundary(signed_matrix)

        # mark the FOV matrix:
        # index = -1 : not accessible area or not visible area
        # index = 0 : boundary of every region
        # index > 0 : accessible/visible region
        signed_region_matrix = FOV.mark_regions(signed_boundary_matrix)
        # use flag to sign each element's relationship with boundary
        flag_matrix = FOV.calculate_flags(signed_region_matrix)
        contour_field = simple_cf(signed_region_matrix)
        # get the row and col value of the flagged FOV matrix
        rows = len(flag_matrix)
        cols = len(flag_matrix[0])

        region_dict = {}
        wasted_region_list = []

        for i in range(0, rows):
            for j in range(0, cols):
                if flag_matrix[i][j] == 0 or flag_matrix[i][j] == 0xF:
                    flag_matrix[i][j] = 0
                    continue
                r, contours = FOV.walk_contour(i, j, flag_matrix, contour_field)
                # makes sure the region id and contour vertex list are not empty
                if r is not None and (str(r) not in wasted_region_list) and contours is not None:
                    # calculate polygon area for each contour
                    polygon_area = FOV.polygon_area(contours)

                    # if it is a region that we have not yet encounter before
                    # create a region_cf structure to store its outline and hole vertex
                    if str(r) not in region_dict.keys():
                        region_dict[str(r)] = region_cf()
                    # if the region's area larger than 0, it is an outline contour
                    if polygon_area > 0:
                        outline = copy.deepcopy(contours)
                        start_point = outline[0]
                        outline.append(start_point)
                        contour_vertex = [hit_matrix[point[0]][point[1]] for point in outline]
                        # simplify the contour
                        contour_vertex_simplified = FOV.douglas_peucker(contour_vertex, contour_index)
                        # check whether the simplified ourline vertex still meet region size threshold
                        if (
                            len(contour_vertex_simplified) >= 3
                            and abs(FOV.polygon_area([[coord[0], coord[1]] for coord in contour_vertex_simplified]))
                            > size_threshold
                        ):
                            # if so, add the outline vertex to the dictionary
                            region_dict[str(r)].outline = contour_vertex_simplified
                        else:
                            wasted_region_list.append(str(r))

                    # else the contour is a hole in certain area
                    else:
                        hole = copy.deepcopy(contours)
                        hole_start_point = hole[0]
                        hole.append(hole_start_point)
                        hole_vertex = [hit_matrix[point[0]][point[1]] for point in hole]
                        # simplify hole contour
                        hole_vertex_simplified = FOV.douglas_peucker(hole_vertex, contour_index)
                        # check whether the simplified hole vertex still meet region size threshold
                        if (
                            len(hole_vertex_simplified) >= 3
                            and abs(FOV.polygon_area([[coord[0], coord[1]] for coord in hole_vertex_simplified]))
                            > size_threshold
                        ):
                            # if so, add the outline vertex to the dictionary
                            region_dict[str(r)].holes.append(hole_vertex_simplified)
        return region_dict

    def distance_point_to_segment(point, segment_start, segment_end):
        """return the distance between a point and a segment"""
        # Unpack the coordinates of the start and end points of the segment
        start_x, start_y, _ = segment_start
        end_x, end_y, _ = segment_end

        # Unpack the coordinates of the point
        point_x, point_y, _ = point

        # Compute vector from start point to the given point (vector_point_to_start_x, vector_point_to_start_y)
        vector_point_to_start_x = point_x - start_x
        vector_point_to_start_y = point_y - start_y

        # Compute vector of the segment (vector_segment_x, vector_segment_y)
        vector_segment_x = end_x - start_x
        vector_segment_y = end_y - start_y

        # Dot product of the two vectors (vector_point_to_start and vector_segment)
        dot_product = vector_point_to_start_x * vector_segment_x + vector_point_to_start_y * vector_segment_y

        # Compute the squared length of the segment
        segment_length_squared = vector_segment_x * vector_segment_x + vector_segment_y * vector_segment_y

        # If the segment length is zero (start and end points are the same),
        # return the distance between the point and the start (or end) point
        if segment_length_squared == 0:
            return math.sqrt((point_x - start_x) ** 2 + (point_y - start_y) ** 2)

        # Calculate the projection parameter (t) which determines the position
        # of the point on the line relative to the segment.
        t = dot_product / segment_length_squared

        # If the projection falls before the start of the segment, return the distance
        # from the point to the start of the segment
        if t < 0:
            return math.sqrt((point_x - start_x) ** 2 + (point_y - start_y) ** 2)

        # If the projection falls after the end of the segment, return the distance
        # from the point to the end of the segment
        elif t > 1:
            return math.sqrt((point_x - end_x) ** 2 + (point_y - end_y) ** 2)

        # Otherwise, the projection falls on the segment, so calculate the nearest point
        # on the segment and return the distance from the point to that nearest point
        else:
            nearest_x = start_x + t * vector_segment_x
            nearest_y = start_y + t * vector_segment_y
            return math.sqrt((point_x - nearest_x) ** 2 + (point_y - nearest_y) ** 2)

    def douglas_peucker(contour_points: list, tolerance: float):
        """simpily the contour via the tolerance index set by user"""
        # If the contour has 2 or fewer points, it cannot be simplified further.
        if len(contour_points) <= 2:
            return contour_points

        # Initialize variables to track the maximum distance and the index of the point farthest from the line.
        max_perpendicular_distance = 0
        farthest_point_index = 0

        # Loop through each point (excluding the first and last) to find the point farthest from the line segment.
        for i in range(1, len(contour_points) - 1):
            # Calculate the perpendicular distance of the point from the line segment formed by the first and last points.
            distance = FOV.distance_point_to_segment(
                point=contour_points[i], segment_start=contour_points[0], segment_end=contour_points[-1]
            )

            # If the current point's distance is greater than the maximum distance, update the variables.
            if distance > max_perpendicular_distance:
                max_perpendicular_distance = distance
                farthest_point_index = i

        # If the maximum distance exceeds the tolerance, recursively simplify both segments divided by the farthest point.
        if max_perpendicular_distance > tolerance:
            # Recursively simplify the points from the start to the farthest point.
            first_segment = FOV.douglas_peucker(contour_points[: farthest_point_index + 1], tolerance)

            # Recursively simplify the points from the farthest point to the end.
            second_segment = FOV.douglas_peucker(contour_points[farthest_point_index:], tolerance)

            # Combine the two simplified segments, excluding the duplicate point at the junction.
            return first_segment[:-1] + second_segment
        else:
            # If the maximum distance is within the tolerance, only keep the endpoints.
            return [contour_points[0], contour_points[-1]]
