from typing import List

from .usda_write import UsdaFile, UsdaVisibility


class UsdaNavMeshOptions:

    @classmethod
    def default_contents_options(cls):
        instance = cls()
        instance.navmesh_polygons = True
        instance.navmesh_lines = True
        instance.paths = True
        instance.paths_start_markers = True
        instance.paths_finish_markers = True
        return instance

    @classmethod
    def default_visibility_options(cls):
        instance = cls()
        instance.navmesh_polygons = True
        instance.navmesh_lines = True
        instance.paths = True
        instance.paths_start_markers = True
        instance.paths_finish_markers = True
        return instance


class UsdaNavMeshConfig:

    @classmethod
    def default_config(
        cls,
        agent_max_radius: float,
        agent_min_height: float,
        contents_options=UsdaNavMeshOptions.default_contents_options(),
        visibility_options=UsdaNavMeshOptions.default_visibility_options()
    ):
        cls.contents_options = contents_options
        cls.visibility_options = visibility_options
        cls.agent_max_radius = agent_max_radius
        cls.agent_min_height = agent_min_height
        cls.navmesh_line_thickness = agent_max_radius * 0.1
        cls.navmesh_line_color = 0xFF000000
        cls.navmesh_polygon_height_bias = 0
        cls.path_line_color = 0xFF00FF00
        cls.path_start_marker_width = agent_max_radius * 0.1
        cls.path_start_marker_height = agent_min_height
        cls.path_start_marker_color = 0xFF00FF00
        cls.path_finish_marker_width = agent_max_radius * 0.1
        cls.path_finish_marker_height = agent_min_height
        cls.path_finish_marker_color = 0xFFFFFF00
        cls.path_line_thickness = agent_max_radius * 0.1
        cfg = UsdaFile.default_config()
        cfg['nav'] = cls
        return cfg


def usda_navmesh_write_lines(
    usda: UsdaFile,
    navmesh,
    id_prefix: str,
    color: int = None,
    thickness: float = None,
    vis: UsdaVisibility = None
):
    assert len(id_prefix) > 0
    nav_cfg = usda.cfg['nav']
    if not nav_cfg.contents_options.navmesh_lines:
        return
    draw_line_verts = navmesh.get_draw_lines()
    assert (len(draw_line_verts) % 2) == 0
    usda.write_line_list(
        id_prefix,
        draw_line_verts,
        color if color is not None else nav_cfg.navmesh_line_color,
        thickness if thickness is not None else nav_cfg.navmesh_line_thickness,
        vis if vis is not None else UsdaVisibility.from_bool(nav_cfg.visibility_options.navmesh_lines)
    )


def usda_navmesh_write_polygons(
    usda: UsdaFile,
    navmesh,
    id_prefix: str,
    area_colors: List[int],
    area_names: List[str],
    vis: UsdaVisibility = None
):
    area_count = navmesh.get_area_count()
    assert len(area_colors) >= area_count
    assert len(area_names) >= area_count
    nav_cfg = usda.cfg['nav']
    if not nav_cfg.contents_options.navmesh_polygons:
        return

    for a in range(0, area_count):
        color = area_colors[a]
        draw_triangle_verts = navmesh.get_draw_triangles(a)
        if len(draw_triangle_verts) > 0:
            assert (len(draw_triangle_verts) % 3) == 0
            usda.write_mesh_polygons_tri_list(
                f'{id_prefix}Area_{a:02d}_{area_names[a]}',
                draw_triangle_verts,
                color,
                nav_cfg.navmesh_polygon_height_bias,
                vis if vis is not None else UsdaVisibility.from_bool(nav_cfg.visibility_options.navmesh_polygons)
            )


def usda_navmesh_write_start_marker(
    usda: UsdaFile,
    id_prefix: str,
    position,
    width: float = None,
    height: float = None,
    color: int = None,
    vis: UsdaVisibility = None
):
    nav_cfg = usda.cfg['nav']
    if not nav_cfg.contents_options.paths_start_markers:
        return

    usda.write_box(
        f'Start_{id_prefix}',
        position,
        width if width is not None else nav_cfg.path_start_marker_width,
        height if height is not None else nav_cfg.path_start_marker_height,
        color if color is not None else nav_cfg.path_start_marker_color,
        vis if vis is not None else UsdaVisibility.from_bool(nav_cfg.visibility_options.paths_start_markers)
    )


def usda_navmesh_write_finish_marker(
    usda: UsdaFile,
    id_prefix: str,
    position,
    width: float = None,
    height: float = None,
    color: int = None,
    vis: UsdaVisibility = None
):
    nav_cfg = usda.cfg['nav']
    if not nav_cfg.contents_options.paths_finish_markers:
        return

    usda.write_box(
        f'Finish_{id_prefix}',
        position,
        width if width is not None else nav_cfg.path_finish_marker_width,
        height if height is not None else nav_cfg.path_finish_marker_height,
        color if color is not None else nav_cfg.path_finish_marker_color,
        vis if vis is not None else UsdaVisibility.from_bool(nav_cfg.visibility_options.paths_finish_markers)
    )


def usda_navmesh_write_path(
    usda: UsdaFile,
    navmesh_path,
    id_prefix: str,
    color: int = None,
    thickness: float = None,
    vis: UsdaVisibility = None
):
    assert len(id_prefix) > 0
    assert navmesh_path
    points = navmesh_path.get_points()
    assert len(points) > 1
    nav_cfg = usda.cfg['nav']
    if not nav_cfg.contents_options.paths:
        return
    usda_navmesh_write_start_marker(usda, id_prefix, points[0], vis=vis)
    usda_navmesh_write_finish_marker(usda, id_prefix, points[-1], vis=vis)
    usda.write_line_strip(
        id_prefix,
        points,
        color if color is not None else nav_cfg.path_line_color,
        thickness if thickness is not None else nav_cfg.path_line_thickness,
        vis if vis is not None else UsdaVisibility.from_bool(nav_cfg.visibility_options.paths)
    )
