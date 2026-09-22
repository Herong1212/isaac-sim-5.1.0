import omni.usd
from omni.kit.viewport.utility import get_active_viewport_window
from omni.ui import scene as sc

from pxr import Gf, Sdf, UsdGeom, Usd


class BBoxDrawerHelper:
    def __init__(self, scene_frame_name: str):
        self.canvas = None
        self.scene_view = None

        self.viewport_window = get_active_viewport_window()
        if not self.viewport_window:
            # TODO : use carb.log_error
            print("couldn't get viewport_window")
            return

        with self.viewport_window.get_frame(scene_frame_name):
            self.scene_view = sc.SceneView()
            with self.scene_view.scene:
                self.canvas = sc.Transform()

        self.viewport_window.viewport_api.add_scene_view(self.scene_view)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.scene_view:
            # Empty the SceneView of any elements it may have
            self.scene_view.scene.clear()
            # Be a good citizen, and un-register the SceneView from Viewport updates
            if self.viewport_window:
                self.viewport_window.viewport_api.remove_scene_view(self.scene_view)
        self._viewport_window = None
        self._scene_view = None

    def demo_draw_box(self):
        if not self.canvas:
            return

        with self.canvas:
            sc.Line([0, 0, 0], [10, 0, 0], thickness=1.0)
            sc.Line([10, 0, 0], [10, 10, 0], thickness=1.0)
            sc.Line([10, 10, 0], [0, 10, 0], thickness=1.0)
            sc.Line([0, 10, 0], [0, 0, 0], thickness=1.0)

    def draw_3D_line(self, begin: Gf.Vec3d, end: Gf.Vec3d, **kwargs):  # noqa: C901, N802
        with self.canvas:
            sc.Line([begin[0], begin[1], begin[2]], [end[0], end[1], end[2]], **kwargs)

    def draw_AABB_box(self, box_min: Gf.Vec3d, box_max: Gf.Vec3d, **kwargs):  # noqa: C901, N802
        vertices = [
            box_min,  # 0
            Gf.Vec3d(box_min[0], box_min[1], box_max[2]),  # 1
            Gf.Vec3d(box_min[0], box_max[1], box_min[2]),  # 2
            Gf.Vec3d(box_max[0], box_min[1], box_min[2]),  # 3
            Gf.Vec3d(box_max[0], box_max[1], box_min[2]),  # 4
            Gf.Vec3d(box_max[0], box_min[1], box_max[2]),  # 5
            Gf.Vec3d(box_min[0], box_max[1], box_max[2]),  # 6
            box_max,
        ]  # 7

        edges = [
            # x
            [0, 3],
            [1, 5],
            [2, 4],
            [6, 7],
            # y
            [0, 2],
            [1, 6],
            [3, 4],
            [5, 7],
            # z
            [0, 1],
            [2, 6],
            [3, 5],
            [4, 7],
        ]

        for edge in edges:
            p = vertices[edge[0]]
            q = vertices[edge[1]]

            size_factor = 0.33
            self.draw_3D_line(p, Gf.Lerp(size_factor, p, q), **kwargs)
            self.draw_3D_line(q, Gf.Lerp(size_factor, q, p), **kwargs)

    def clear_canvas(self):
        if not self.canvas:
            return
        self.canvas.clear()

    def draw_AABB_box_around_prim(self, prim_path: Sdf.Path, **kwargs):  # noqa: C901, N802
        ctx = omni.usd.get_context()

        purposes = [UsdGeom.Tokens.default_]
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
        prim = ctx.get_stage().GetPrimAtPath(prim_path)
        bound = bbox_cache.ComputeWorldBound(prim)
        box_range = bound.ComputeAlignedBox()
        bbox_max = box_range.GetMax()
        bbox_min = box_range.GetMin()

        self.draw_AABB_box(bbox_min, bbox_max, **kwargs)
