import math
from typing import Tuple

import omni.kit.app
import omni.kit.commands
import omni.usd
import pxr.Gf
from omni import ui
from usdrt import Gf, Rt, Sdf, Usd, UsdGeom, Vt, hierarchy

# omni.kit.commands.execute("ChangeSetting", path="/app/useFabricSceneDelegate", value=True)
omni.kit.commands.execute("ToggleExtension", ext_id="omni.fabric.commands-1.1.2", enable=True)
# omni.kit.commands.execute("ToggleExtension", ext_id = "omni.kit.manipulator.prim-105.0.14", enable = False)
# omni.kit.commands.execute("ToggleExtension", ext_id = "omni.kit.manipulator.prim.bundle-105.0.9", enable = True)
# omni.kit.commands.execute("ToggleExtension", ext_id = "omni.kit.manipulator.prim.core-105.0.11", enable = True)
# omni.kit.commands.execute("ToggleExtension", ext_id = "omni.kit.manipulator.prim.usd-105.0.10", enable = True)
# omni.kit.commands.execute("ToggleExtension", ext_id = "omni.kit.manipulator.prim.fabric-105.0.11", enable = True)


class moveTst:
    def _quaternion_from_euler(self, eulers):
        # TODO: add rotation order when USDRT supports it
        axes = [pxr.Gf.Vec3d(1, 0, 0), pxr.Gf.Vec3d(0, 1, 0), pxr.Gf.Vec3d(0, 0, 1)]
        nrs = [pxr.Gf.Rotation(axis, eulers[i]) for i, axis in enumerate(axes)]
        nr = nrs[2] * nrs[1] * nrs[0]
        result = nr.GetQuat()
        return result

    def __init__(self):
        self._window = ui.Window("Test", width=300, height=480)
        with self._window.frame:
            # with ui.VStack():
            #     self.label = ui.Label("TEST")
            with ui.VStack():
                # with ui.HStack():
                ui.Button("Reload", clicked_fn=self.reload)
                ui.Button("Enable prim2 fabric", clicked_fn=self.enablePrim2Fabric)
                ui.Button("Enable prim2 USD", clicked_fn=self.enablePrim2USD)
                ui.Button("Enable prim", clicked_fn=self.enablePrim)
                ui.Button("Start", clicked_fn=self.start)
                ui.Button("Stop", clicked_fn=self.stop)
                # ui.Button("Create Fabric only prim", clicked_fn=self.createFabricPrim)
                ui.Button("Create multiple Fabric only prims", clicked_fn=self.createMultiFabricPrim)
                # ui.Button("Select Triangle as FABRIC", clicked_fn=self.selectFabricPrim)
                ui.Button("Select multiple fabric only prims", clicked_fn=self.selectMultipleFabricPrim)
                ui.Button("Select Triangle and Cube as ALL", clicked_fn=self.selectMixedPrims)
                ui.Button("Select Cube as USD", clicked_fn=self.selectUsdPrim)
                ui.Button("Select Cube as ALL", clicked_fn=self.selectMixedPrim)
                ui.Button("Select Cube and Cube_01 as ALL", clicked_fn=self.selectMixedPrims01)
                ui.Button("Unselect Mixed prims", clicked_fn=self.selectMixedNone)
                ui.Button("Get data for selected Fabric prim", clicked_fn=self.get_fabric_data_for_prim)
                ui.Button("update_fabric_from_usd", clicked_fn=self.update_fabric_from_usd)
                ui.Button("update_usd_from_fabric", clicked_fn=self.update_usd_from_fabric)
        # self.reload()

    def enablePrim2Fabric(self):
        omni.kit.commands.execute("ChangeSetting", path="/app/useFabricSceneDelegate", value=True)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim-105.0.14", enable=False)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim.core-105.0.13", enable=True)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim.usd-105.0.10", enable=True)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim.fabric-105.0.12", enable=True)

    def enablePrim2USD(self):
        omni.kit.commands.execute("ChangeSetting", path="/app/useFabricSceneDelegate", value=False)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim-105.0.14", enable=False)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim.core-105.0.13", enable=True)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim.usd-105.0.10", enable=True)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim.fabric-105.0.12", enable=False)

    def enablePrim(self):
        omni.kit.commands.execute("ChangeSetting", path="/app/useFabricSceneDelegate", value=False)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim.core-105.0.13", enable=False)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim.usd-105.0.10", enable=False)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim.fabric-105.0.12", enable=False)
        omni.kit.commands.execute("ToggleExtension", ext_id="omni.kit.manipulator.prim-105.0.14", enable=True)

    def reload(self):
        self._window.visible = True
        self.listener = None
        self.eulers = [0, 0, 0]
        self.context = omni.usd.get_context()
        self.stage_id = self.context.get_stage_id()
        self.stage = Usd.Stage.Attach(self.stage_id)
        self.stage_usd = self.context.get_stage()

    def selectFabricPrim(self):
        sel = self.context.get_selection()
        sel.set_selected_prim_paths(["/World/Triangle"], True, omni.usd.Selection.SourceType.FABRIC)

    def selectMultipleFabricPrim(self):
        paths = []
        n = 1024
        for i in range(0, n):
            paths.append("/World/Triangle_" + str(i))
        sel = self.context.get_selection()
        sel.set_selected_prim_paths(paths, True, omni.usd.Selection.SourceType.FABRIC)

    def selectMixedPrims(self):
        sel = self.context.get_selection()
        sel.set_selected_prim_paths(["/World/Triangle", "/World/Cube"], True, omni.usd.Selection.SourceType.ALL)

    def selectUsdPrim(self):
        sel = self.context.get_selection()
        sel.set_selected_prim_paths(["/World/Cube"], True, omni.usd.Selection.SourceType.USD)

    def selectMixedPrims01(self):
        sel = self.context.get_selection()
        sel.set_selected_prim_paths(["/World/Cube", "/World/Cube_01"], True, omni.usd.Selection.SourceType.ALL)

    def selectMixedPrim(self):
        sel = self.context.get_selection()
        sel.set_selected_prim_paths(["/World/Cube"], True, omni.usd.Selection.SourceType.ALL)

    def selectMixedNone(self):
        sel = self.context.get_selection()
        sel.set_selected_prim_paths([], True, omni.usd.Selection.SourceType.ALL)

    def start(self):
        print("start")
        self.prim = self.stage.GetPrimAtPath(Sdf.Path("/World/Cube"))
        self.rtxformable = Rt.Xformable(self.prim)
        if not self.rtxformable.HasWorldXform():
            self.rtxformable.SetWorldXformFromUsd()
        self.posAttr = self.rtxformable.GetWorldPositionAttr()
        self.rotAttr = self.rtxformable.GetWorldOrientationAttr()
        from carb.eventdispatcher import get_eventdispatcher

        self.listener = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self.on_tick,
            observer_name="omni.kit.manipulator.prim.fabric widgetTest",
        )

    def on_tick(self, _):
        # print(str(count))
        self.posAttr.Set(self.posAttr.Get() + Gf.Vec3d(0.2, 0, 0))
        self.eulers[0] += 1.0
        self.eulers[1] += 0.5
        self.eulers[2] += 0.25
        q = self._quaternion_from_euler((self.eulers[0], self.eulers[1], self.eulers[2]))
        qRt = Gf.Quatf(q.GetReal(), q.GetImaginary()[0], q.GetImaginary()[1], q.GetImaginary()[2])
        self.rotAttr.Set(qRt)

    def stop(self):
        print("stop")
        self.listener = None

    def createMultiFabricPrim(self):
        stage_id = self.stage.GetStageIdAsStageId()
        fabric_id = self.stage.GetFabricId()
        # hier = hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
        paths = []
        new_translations = []
        new_rotation_eulers = []
        new_rotation_orders = []
        new_scales = []
        n = 1024
        for i in range(0, n):
            w = int(math.sqrt(n))
            x = float((i % w) * 100.0)
            y = float((i // w) * 100.0)
            path = "/World/Triangle_" + str(i)
            prim = self.stage.DefinePrim(path, "Mesh")
            mesh = UsdGeom.Mesh(prim)

            points = mesh.CreatePointsAttr()
            points.Set(Vt.Vec3fArray([Gf.Vec3f(100.0, 0, 0), Gf.Vec3f(0, 100.0, 0), Gf.Vec3f(-100.0, 0, 0)]))
            face_vc = mesh.CreateFaceVertexCountsAttr()
            face_vc.Set(Vt.IntArray([3]))
            face_vi = mesh.CreateFaceVertexIndicesAttr()
            face_vi.Set(Vt.IntArray([0, 1, 2]))

            rtbound = Rt.Boundable(prim)
            world_ext = rtbound.CreateWorldExtentAttr()
            world_ext.Set(Gf.Range3d(Gf.Vec3d(-100.0, 0, -100.0), Gf.Vec3d(100.0, 100.0, 100.0)))

            if not prim.HasAttribute("omni:fabric:localMatrix"):
                local_matrix_attr = prim.CreateAttribute("omni:fabric:localMatrix", Sdf.ValueTypeNames.Matrix4d, False)
                local_matrix_attr.Set(Gf.Matrix4d(1))  # .SetTranslate(Gf.Vec3d(x,0,y)))

            if not prim.HasAttribute("omni:fabric:worldMatrix"):
                world_matrix_attr = prim.CreateAttribute("omni:fabric:worldMatrix", Sdf.ValueTypeNames.Matrix4d, False)
                world_matrix_attr.Set(Gf.Matrix4d(1))  # .SetTranslate(Gf.Vec3d(x,0,y)))

            # tr_mtx = Gf.Matrix4d(1).SetTranslate(Gf.Vec3d(x,0,y))
            # hier.set_world_xform(Sdf.Path(path), tr_mtx)
            # hier.set_local_xform(Sdf.Path(path), tr_mtx)
            # paths.append(path)
            # new_translations += [x, 0.0, y]
            # new_rotation_eulers += [0.0,0.0,0.0]
            # new_rotation_orders += [0,1,2]
            # new_scales += [1.0,1.0,1.0]
        # omni.kit.commands.create(
        # "TransformMultiPrimsSRTFabricCpp",
        # count = len(paths),
        # fabric_stage_id = stage_id,
        # no_undo = True,
        # paths = paths,
        # new_translations = new_translations,
        # new_rotation_eulers = new_rotation_eulers,
        # new_rotation_orders = new_rotation_orders,
        # new_scales = new_scales,
        # ).do()

    def createFabricPrim(self):
        prim = self.stage.DefinePrim("/World/Triangle", "Mesh")
        mesh = UsdGeom.Mesh(prim)

        points = mesh.CreatePointsAttr()
        points.Set(Vt.Vec3fArray([Gf.Vec3f(100.0, 0, 0), Gf.Vec3f(0, 100.0, 0), Gf.Vec3f(-100.0, 0, 0)]))
        face_vc = mesh.CreateFaceVertexCountsAttr()
        face_vc.Set(Vt.IntArray([3]))
        face_vi = mesh.CreateFaceVertexIndicesAttr()
        face_vi.Set(Vt.IntArray([0, 1, 2]))

        rtbound = Rt.Boundable(prim)
        world_ext = rtbound.CreateWorldExtentAttr()
        world_ext.Set(Gf.Range3d(Gf.Vec3d(-100.0, 0, -100.0), Gf.Vec3d(100.0, 100.0, 100.0)))

        if not prim.HasAttribute("omni:fabric:localMatrix"):
            local_matrix_attr = prim.CreateAttribute("omni:fabric:localMatrix", Sdf.ValueTypeNames.Matrix4d, False)
            local_matrix_attr.Set(Gf.Matrix4d(1))

        if not prim.HasAttribute("omni:fabric:worldMatrix"):
            world_matrix_attr = prim.CreateAttribute("omni:fabric:worldMatrix", Sdf.ValueTypeNames.Matrix4d, False)
            world_matrix_attr.Set(Gf.Matrix4d(1))

    def get_fabric_data_for_prim(self):
        # selection = self._usd_context.get_selection().get_selected_prim_paths(omni.usd.Selection.SourceType.USD)
        selection_fabric = self.context.get_selection().get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        # selection_all = self._usd_context.get_selection().get_selected_prim_paths(omni.usd.Selection.SourceType.ALL)
        for path in selection_fabric:
            # If a prim does not already exist in Fabric,
            # it will be fetched from USD by simply creating the
            # Usd.Prim object. At this time, only the attributes that have
            # authored opinions will be fetch into Fabric.
            prim = self.stage.GetPrimAtPath(Sdf.Path(path))
            if not prim:
                return f"Prim at path {path} is not in Fabric"

            # This diverges a bit from USD - only attributes
            # that exist in Fabric are returned by this API
            attrs = prim.GetAttributes()

            result = f"Fabric data for prim at path {path}\n\n\n"
            for attr in attrs:
                try:
                    data = attr.Get()
                    datastr = str(data)
                    if data is None:
                        datastr = "<no value>"
                except TypeError:
                    # Some data types not yet supported in Python
                    datastr = "<no Python conversion>"

                result += "{} ({}): {}\n".format(attr.GetName(), str(attr.GetTypeName().GetAsToken()), datastr)
            result += "Xformable: " + str(prim.IsA(UsdGeom.Xformable))
            print(result)

    def quaternion_from_euler(self, eulers, ro):
        axes = [Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1)]
        nrs = [Gf.Rotation(axes[i], eulers[i]) for i in [ro[0], ro[1], ro[2]]]
        nr = nrs[0] * nrs[1] * nrs[2]
        result = nr.GetQuat()
        return result

    def euler_from_quaternion(self, q, ro):
        axes = [Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1)]
        usd_axes = [axes[i] for i in [ro[0], ro[1], ro[2]]]
        rot = Gf.Rotation(q)
        eulers = rot.Decompose(*usd_axes)
        # round epsilons from decompose
        eulers = [round(angle + 1e-4, 3) for angle in eulers]
        return eulers

    def update_fabric_from_usd(self):
        selection = self.context.get_selection().get_selected_prim_paths()
        fabric_rot_orders = [2, 1, 0]
        # usd_rot_orders = [0, 1, 2]

        for path in selection:
            prim_pxr = self.stage_usd.GetPrimAtPath(pxr.Sdf.Path(path))
            prim_usdrt = self.stage.GetPrimAtPath(Sdf.Path(path))

            _, _, usd_rot_orders, _ = omni.usd.get_local_transform_SRT(prim_pxr)

            print(f"usd_rot_orders = {usd_rot_orders}")

            rtxformable = Rt.Xformable(prim_usdrt)
            if not rtxformable.HasWorldXform():
                rtxformable.SetWorldXformFromUsd()
            usd_eulers = prim_pxr.GetAttribute("xformOp:rotateXYZ").Get()
            usd_eulers = [usd_eulers[0], usd_eulers[1], usd_eulers[2]]
            q = self.quaternion_from_euler(usd_eulers, usd_rot_orders)
            print(f"q = {q}")
            rtxformable.GetWorldOrientationAttr().Set(q)
            # fabric_eulers = [ fabric_eulers[2], fabric_eulers[1], fabric_eulers[0] ]

    def update_usd_from_fabric(self):
        selection = self.context.get_selection().get_selected_prim_paths()
        fabric_rot_orders = [2, 1, 0]
        usd_rot_orders = [0, 1, 2]
        print("===========================")
        for path in selection:
            prim_pxr = self.stage_usd.GetPrimAtPath(pxr.Sdf.Path(path))
            prim_usdrt = self.stage.GetPrimAtPath(Sdf.Path(path))
            rtxformable = Rt.Xformable(prim_usdrt)
            if not rtxformable.HasWorldXform():
                rtxformable.SetWorldXformFromUsd()
            fabric_q = rtxformable.GetWorldOrientationAttr().Get()
            print(f"fabric_q = {fabric_q}")
            fabric_eulers = self.euler_from_quaternion(fabric_q, usd_rot_orders)
            # fabric_eulers = [fabric_eulers[2], fabric_eulers[1], fabric_eulers[0]]
            print(f"fabric_eulers = {fabric_eulers}")

            new_fabric_q = self.quaternion_from_euler(fabric_eulers, fabric_rot_orders)
            print(f"new_fabric_q = {new_fabric_q}")

            usd_eulers = self.euler_from_quaternion(fabric_q, fabric_rot_orders)
            usd_eulers = [usd_eulers[2], usd_eulers[1], usd_eulers[0]]
            print(f"usd_eulers = {usd_eulers}")


test = moveTst()


# from typing import Tuple
# import usdrt.Gf
# import usdrt.Usd
# import usdrt.Sdf
# import usdrt.UsdGeom
# from pxr import Sdf

# def quaternion_from_euler(eulers: Tuple[float, ...], ro: usdrt.Gf.Vec3i):
#     axes = [usdrt.Gf.Vec3d(1, 0, 0), usdrt.Gf.Vec3d(0, 1, 0), usdrt.Gf.Vec3d(0, 0, 1)]
#     nrs = [usdrt.Gf.Rotation(axes[i], eulers[i]) for i in [ro[0], ro[1], ro[2]] ]
#     nr = nrs[0] * nrs[1] * nrs[2]
#     result = nr.GetQuat()
#     return result

# def euler_from_quaternion(q: usdrt.Gf.Quatd, ro: usdrt.Gf.Vec3i):
#     axes = [usdrt.Gf.Vec3d(1, 0, 0), usdrt.Gf.Vec3d(0, 1, 0), usdrt.Gf.Vec3d(0, 0, 1)]
#     usd_axes = [ axes[i] for i in [ro[0], ro[1], ro[2]] ]
#     rot = usdrt.Gf.Rotation(q)
#     eulers = rot.Decompose(*usd_axes)
#     # round epsilons from decompose
#     eulers = [round(angle + 1e-4, 3) for angle in eulers]
#     return eulers

# print("================")

# context = omni.usd.get_context()
# stage = context.get_stage()
# stage_id = context.get_stage_id()
# stage_usdrt = usdrt.Usd.Stage.Attach(stage_id)


# selection = context.get_selection().get_selected_prim_paths()

# for path in selection:
#     prim = stage.GetPrimAtPath(Sdf.Path(path))
#     prim_usdrt = stage_usdrt.GetPrimAtPath(usdrt.Sdf.Path(path))

#     rtxformable = usdrt.Rt.Xformable(prim_usdrt)
#     if not rtxformable.HasWorldXform():
#         rtxformable.SetWorldXformFromUsd()

#     axes = [usdrt.Gf.Vec3d(1, 0, 0), usdrt.Gf.Vec3d(0, 1, 0), usdrt.Gf.Vec3d(0, 0, 1)]
#     fabric_q = rtxformable.GetWorldOrientationAttr().Get()
#     print(f"fabric_q = {fabric_q}")
#     fabric_rot_orders = [2, 1, 0]
#     usd_rot_orders = [0, 1, 2]
#     fabric_eulers = euler_from_quaternion(fabric_q, fabric_rot_orders)
#     fabric_eulers = [ fabric_eulers[2], fabric_eulers[1], fabric_eulers[0] ]
#     print(f"fabric_eulers= {fabric_eulers}")


#     fabric_q_calc = quaternion_from_euler(fabric_eulers, usd_rot_orders)
#     print(f"fabric_q_calc = {fabric_q_calc}")
#     fabric_eulers_calc = euler_from_quaternion(fabric_q_calc, fabric_rot_orders)
#     print(f"fabric_eulers_calc = {fabric_eulers_calc}")

# # #    usd_rot_orders = [0, 1, 2]
# # #    usd_eulers = euler_from_quaternion(fabric_q,usd_rot_orders)
# # #    attrValue = prim.GetAttribute("xformOp:rotateXYZ").Get()
# # #    print(f"usd attrib = {attrValue}")
# # #
# # #    print("usd")
# # #    print(usd_eulers)
