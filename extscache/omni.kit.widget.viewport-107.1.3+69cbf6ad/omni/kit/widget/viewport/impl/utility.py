# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["init_settings", "save_implicit_cameras"]

from typing import List, Optional, Sequence, Tuple
import carb

from pxr import Usd, UsdGeom, Sdf, Tf, Kind, Gf


def _report_error():
    import traceback
    carb.log_error(traceback.format_exc())


def _support_legacy_viewport():
    return True


@carb.profiler.profile
def _build_viewport_cameras(stage: Usd.Stage, isettings: carb.settings, usd_context_name: str, cam_prefix: str = None):
    if _support_legacy_viewport():
        isettings.set_default("/app/viewport/defaultCamPos/x", 500.0)
        isettings.set_default("/app/viewport/defaultCamPos/y", 500.0)
        isettings.set_default("/app/viewport/defaultCamPos/z", 500.0)
        isettings.set_default("/app/viewport/defaultCamTarget/x", 0.0)
        isettings.set_default("/app/viewport/defaultCamTarget/y", 0.0)
        isettings.set_default("/app/viewport/defaultCamTarget/z", 0.0)

        def_pos = (
            isettings.get("/app/viewport/defaultCamPos/x"),
            isettings.get("/app/viewport/defaultCamPos/y"),
            isettings.get("/app/viewport/defaultCamPos/z")
        )
    else:
        isettings.set_default("/app/viewport/defaultCameraPosition", (500.0, 500.0, 500.0))
        isettings.set_default("/app/viewport/defaultCameraTarget", (0.0, 0.0, 0.0))
        def_pos = tuple(isettings.get("/app/viewport/defaultCameraPosition"))

    up_axis = UsdGeom.GetStageUpAxis(stage).upper()
    if up_axis == UsdGeom.Tokens.z:
        up_correction = Gf.Matrix4d(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1)
    elif up_axis == UsdGeom.Tokens.x:
        up_correction = Gf.Matrix4d(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1)
    else:
        up_correction = Gf.Matrix4d(1)

    def resolve_translate(stage: Usd.Stage, md_name: str, translate: Sequence[float], meter_per_unit: bool):
        md_target = None
        md_position = stage.GetMetadataByDictKey("customLayerData", f"cameraSettings:{md_name}:position")

        if md_position and len(md_position) == 3:
            translate = md_position
            meter_per_unit = False
        else:
            # Otherwise, it may be a really old scene, with incorrect ortho=target
            md_target = stage.GetMetadataByDictKey("customLayerData", f"cameraSettings:{md_name}:target")
            if md_target and len(md_target) == 3:
                meter_per_unit = (UsdGeom.GetStageMetersPerUnit(stage) or 0.01) if meter_per_unit else (1.0)
                if md_name == "Front":
                    translate = (md_target[0], md_target[1], translate[2] / meter_per_unit)
                elif md_name == "Top":
                    translate = (md_target[0], translate[1] / meter_per_unit, md_target[2])
                else:
                    translate = (translate[0] / meter_per_unit, md_target[1], md_target[2])
                meter_per_unit = False

        if md_position or md_target:
            translate = up_correction.Transform(Gf.Vec3d(translate[0], translate[1], translate[2]))
        else:
            translate = Gf.Vec3d(translate[0], translate[1], translate[2])

        # Calculate ortho aperture based on length before any meter-per-unit scaling is applied
        aperture = translate.GetLength() * 10
        if meter_per_unit:
            meter_per_unit = UsdGeom.GetStageMetersPerUnit(stage) or 0.01
            translate = translate / meter_per_unit

        return translate, aperture

    def add_viewport_camera(cam_name, translate, rotate, ortho, md_name, counter):
        cam_path = f"{cam_prefix}{cam_name}{counter if counter else ''}"
        prim = stage.GetPrimAtPath(cam_path)
        existed = prim and prim.IsValid()
        horizontal_aperture = None
        if existed:
            # Test if it's a camera, but also might be a pure-over which Define should take.
            if not prim.IsA(UsdGeom.Camera) and prim.GetTypeName():
                carb.log_warn(f"Usd.Prim exists at '{cam_path}', but is not a UsdGeom.Camera")
                if counter < 10:
                    return add_viewport_camera(cam_name, translate, rotate, ortho, md_name, counter + 1)
                return (None, False)
            horiz_prop = prim.GetProperty("horizontalAperture")
            if horiz_prop and horiz_prop.IsValid():
                horizontal_aperture = horiz_prop.Get()

        md_name = md_name or cam_name
        camera = UsdGeom.Camera.Define(stage, cam_path)
        add_xform = (not existed) or (not camera.GetOrderedXformOps())
        target = Gf.Vec3d(0, 0, 0)
        center_of_interest = None
        ortho_translate = None
        attr_defaults_key = None
        if not existed:
            attr_defaults_key = "/persistent/app/primCreation/typedDefaults/camera"
            if ortho:
                attr_defaults_key = "/persistent/app/primCreation/typedDefaults/orthoCamera"
                camera.GetProjectionAttr().Set(value=UsdGeom.Tokens.orthographic)
                if horizontal_aperture is None:
                    # This attempts what Kit currently did/does
                    # Restore translation from position if valid
                    ortho_translate, aperture = resolve_translate(stage, md_name, translate, True)
                    # md_radius = stage.GetMetadataByDictKey("customLayerData", f"cameraSettings:{md_name}:radius")
                    # if md_radius:
                    camera.GetHorizontalApertureAttr().Set(aperture)
                    camera.GetVerticalApertureAttr().Set(aperture)
            else:
                camera.GetFocalLengthAttr().Set(18.147562)

        # Try and restore from stage-metadata from position and target (both in world-space)
        # But only restore from meta-data if the actual camera does not exist
        # (i.e. if it exists assume it was saved out for a reason)
        xf_tr = camera.GetPrim().GetProperty("xformOp:translate") if existed else None
        # Get the authored value (which could still be empty if the property is decalred but not defined)
        authored_translate = xf_tr.Get() if (xf_tr and xf_tr.IsValid()) else ortho_translate
        if authored_translate:
            translate = authored_translate
        else:
            translate, _ = resolve_translate(stage, md_name, translate, False)

        if not ortho:
            # Restore center-of-interest from "target" metadata setting or existing property
            coi_prop = camera.GetPrim().GetProperty("omni:kit:centerOfInterest") if existed else None
            if coi_prop and coi_prop.IsValid():
                target = coi_prop.Get()
            else:
                md_target = stage.GetMetadataByDictKey("customLayerData", f"cameraSettings:{md_name}:target")
                if md_target:
                    target = up_correction.Transform(Gf.Vec3d(md_target[0], md_target[1], md_target[2]))
        else:
            if horizontal_aperture is None:
                # Restore ortho aperture from "radius" metadata setting or existing property
                radius = stage.GetMetadataByDictKey("customLayerData", f"cameraSettings:{md_name}:radius")
                if radius is not None and float(radius) > 0:
                    camera.GetHorizontalApertureAttr().Set(float(radius) * 10)
                    camera.GetVerticalApertureAttr().Set(float(radius) * 10)

            # Make sure to keep ortho rotations orthogonal to ground plane
            if md_name == "Front":
                target = (translate[0], translate[1], 0)
            elif md_name == "Top":
                target = (translate[0], 0, translate[2])
            elif md_name == "Right":
                target = (0, translate[1], translate[2])

        # Restore XYZ rotation fro pre-exiting property or lookAt from center of interest
        rot_prop = camera.GetPrim().GetProperty("xformOp:rotateXYZ") if existed else None
        # Get the authored value (which could still be empty if the property is decalred but not defined)
        authored_rotate = rot_prop.Get() if rot_prop and rot_prop.IsValid() else None
        if authored_rotate is None:
            # Build the look-at matrix. Do this in Y-up and handle other stage-up axis' later
            up = Gf.Vec3d(0, 1, 0)
            decomp = (Gf.Vec3d(-1, 0, 0), Gf.Vec3d(0, -1, 0), Gf.Vec3d(0, 0, 1))
            look_at = Gf.Matrix4d().SetLookAt(translate, target, up)
            # Put target into camera space for center of interest
            center_of_interest = look_at.Transform(target)
            # Extract x-y-z rotation
            rotation = look_at.ExtractRotation().Decompose(decomp[0], decomp[1], decomp[2])
            if rotation:
                rotate = rotation
            else:
                carb.log_warn("LookAt decomposition failed for camera {md_name}")
        else:
            rotate = authored_rotate

        prim = camera.GetPrim()

        # Setup with any user-specified defaults
        if attr_defaults_key:
            if not ortho:
                isettings.set_default(f"{attr_defaults_key}/clippingRange", (1.0, 10000000.0))
            attr_keys = isettings.get_settings_dictionary(attr_defaults_key)
            for name, value in (attr_keys.get_dict() if attr_keys else {}).items():
                # Catch failures and issue an error, but continue on
                try:
                    attr = prim.GetAttribute(name)
                    if attr:
                        attr.Set(value)
                except Exception:  # noqa PLW0718
                    _report_error()

        if add_xform:
            def set_op_value(attr_name, add_op, vec3):
                try:
                    xf_op = add_op()
                except Tf.ErrorException:
                    xf_attr = camera.GetPrim().GetAttribute(f"xformOp:{attr_name}")
                    xf_op = UsdGeom.XformOp(xf_attr) if xf_attr and xf_attr.IsValid() else None
                    if not xf_op:
                        raise

                precision = xf_op.GetPrecision()
                if precision == UsdGeom.XformOp.PrecisionFloat:
                    xf_op.Set(Gf.Vec3f(vec3[0], vec3[1], vec3[2]))
                elif precision == UsdGeom.XformOp.PrecisionHalf:
                    xf_op.Set(Gf.Vec3h(vec3[0], vec3[1], vec3[2]))
                else:
                    xf_op.Set(Gf.Vec3d(vec3[0], vec3[1], vec3[2]))

            set_op_value("translate", camera.AddTranslateOp, translate)
            set_op_value("rotateXYZ", camera.AddRotateXYZOp, rotate)
            set_op_value("scale", camera.AddScaleOp, (1, 1, 1))

            if not center_of_interest:
                zlen = Gf.Vec3d(translate[0], translate[1], translate[2]).GetLength()
                center_of_interest = Gf.Vec3d(0, 0, -zlen)
            prim.CreateAttribute("omni:kit:centerOfInterest", Sdf.ValueTypeNames.Vector3d,
                                 True, Sdf.VariabilityUniform).Set(center_of_interest)

        Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)
        cam_md = {
            "hide_in_stage_window": True,
            "no_delete": True
        }
        prim.SetCustomDataByKey("omni:kit", cam_md)

        if _support_legacy_viewport():
            for k, v in cam_md.items():
                prim.SetMetadata(k, v)

        return (camera, add_xform)

    class ScopedEdit():
        def __init__(self, stage):
            self.__stage = stage
            edit_target = stage.GetEditTarget()
            edit_layer = edit_target.GetLayer()
            self.__edit_layer = stage.GetSessionLayer()
            self.__was_editable = self.__edit_layer.permissionToEdit
            if not self.__was_editable:
                self.__edit_layer.SetPermissionToEdit(True)
            if self.__edit_layer != edit_layer:
                stage.SetEditTarget(stage.GetEditTargetForLocalLayer(self.__edit_layer))
                self.__edit_target = edit_target
            else:
                self.__edit_target = None

        def destroy(self):
            if self.__edit_layer and not self.__was_editable:
                self.__edit_layer.SetPermissionToEdit(False)
                self.__edit_layer = None

            if self.__edit_target:
                self.__stage.SetEditTarget(self.__edit_target)
                self.__edit_target = None

    def build_cameras():
        def build_camera(cam_name, translate, rotate, ortho=True, md_name=None):
            try:
                return add_viewport_camera(cam_name, translate, rotate, ortho, md_name, 0)
            except Exception:  # noqa PLW0718
                _report_error()
            return None

        return [(cam.GetPath(), xf_added) for cam, xf_added in [
            build_camera("Persp", def_pos, (-35, 45, 0), False, "Perspective"),
            build_camera("Front", (0, 0, def_pos[2]), (0, 0, 0)),
            build_camera("Top", (0, def_pos[1], 0), (90, 0, -180)),
            build_camera("Right", (-def_pos[0], 0, 0), (0, -90, 0))
        ] if cam]

    result = []
    edit_scope = ScopedEdit(stage)
    try:
        result = build_cameras()
    except Exception:  # noqa PLW0718
        _report_error()
    finally:
        edit_scope.destroy()

    return result


@carb.profiler.profile
def _run_viewport_auto_frame(stage: Usd.Stage, isettings: carb.settings, usd_context_name: str,
                             camera_path: Sdf.Path, camera_paths: Sequence[Sdf.Path],
                             bound_camera: Optional[Sdf.Path], resolution: Optional[Tuple[int]]):
    auto_frame_section = "/persistent/app/viewport/autoFrame"
    auto_frame = f"{isettings.get(auto_frame_section + '/mode')}".lower()
    if auto_frame == "first_open":
        # Use whether cameraSettings:boundCamera metadata exists as test whether this file has
        # ever been opened in Kit.
        auto_frame = not bool(bound_camera)
    elif auto_frame == "always":
        auto_frame = True
    else:
        auto_frame = False

    if not auto_frame:
        return

    if Sdf.Layer.IsAnonymousLayerIdentifier(stage.GetRootLayer().identifier):
        carb.log_info("Skipping auto-frame for anonymous layer")
        return

    single_camera = isettings.get(f"{auto_frame_section}/singleCamera")
    implicit_only = isettings.get(f"{auto_frame_section}/implicitOnly")
    if single_camera:
        if implicit_only and (camera_path not in camera_paths):
            camera_paths = [camera_paths[0]]
        else:
            camera_paths = [camera_path]
    elif not implicit_only and (camera_path not in camera_paths):
        camera_paths.append(camera_path)

    try:
        import omni.kit.commands
        for frame_camera in camera_paths:
            omni.kit.commands.create(
                "FramePrimsCommand",
                prim_to_move=frame_camera,
                usd_context_name=usd_context_name,
                aspect_ratio=resolution[0] / resolution[1],
            ).do()
    except ModuleNotFoundError:
        carb.log_warn("omni.kit.commands.FramePrimsCommand is not available for auto-frame")


@carb.profiler.profile
def _init_viewport_cameras(stage: Usd.Stage, isettings: carb.settings, usd_context_name: str, first_init: bool, cam_prefix: Optional[str] = None):
    if cam_prefix is None:
        cam_prefix = "/OmniverseKit_"

    if first_init:
        # Build the implicit cameras
        result = _build_viewport_cameras(stage, isettings, usd_context_name, cam_prefix)
        cameras = [cam for cam, xf_added in result]

        # All camera's we're created in Y-up, if stage is not Y-up then they need to be rotated now
        y_tok = UsdGeom.Tokens.y
        if UsdGeom.GetStageUpAxis(stage).upper() != y_tok:
            # Exclude any up adjustment for cameras where xform-op was loaded from disk (not created).
            exclude_cameras = [exclude_cam for exclude_cam, xf_added in result if not xf_added]
            StageAxis(stage, y_tok).update(stage, Usd.TimeCode.Default(), usd_context_name, first_init,
                                           exclude_cameras=exclude_cameras)
    else:
        # The list of known implicit camera suffixes
        cameras = ["Persp", "Front", "Top", "Right"]
        # Query stage for the implicit camera prims
        cameras = [stage.GetPrimAtPath(f"{cam_prefix}{camera}") for camera in cameras]
        # Keep only the paths that are valid prims
        cameras = [camera.GetPath() for camera in cameras if camera.IsValid()]

    bound_camera = None
    try:
        bound_camera = stage.GetMetadataByDictKey("customLayerData", "cameraSettings:boundCamera")
        if bound_camera:
            bound_camera = Sdf.Path(bound_camera)
    except Exception:  # noqa PLW0718
        _report_error()

    return cameras, bound_camera


class SelectionSettings:
    _g_inited = False

    @staticmethod
    def init(isettings):
        if SelectionSettings._g_inited:
            return
        SelectionSettings._g_inited = True

        # TODO: Check against existing
        default_color = [1.0, 0.6, 0.0, 1.0]
        isettings.set_default("/app/viewport/outline/enabled", True)
        isettings.set_default("/persistent/app/viewport/outline/width", 2)
        isettings.set_default("/persistent/app/viewport/outline/intersection/color", default_color)

        # Fill default ouline colors with different rgb mix
        colors = []
        r_end, g_end, b_end, b_start = 8, 8, 8, 4
        for r in range(r_end):
            for g in range(g_end):
                for b in range(b_start, b_end):
                    colors += [float(r) / float(r_end - 1),
                               float(g) / float(g_end - 1),
                               float(b) / float(b_end - 1),
                               1.0]

        # Override last one with orange default color
        colors = colors[:len(colors) - 4] + default_color
        isettings.set_default("/persistent/app/viewport/outline/color", colors)

        # Replace last element with 0.0 alpha?
        colors = colors[:len(colors) - 1] + [0.0]
        isettings.set_default("/persistent/app/viewport/outline/shadeColor", colors)


@carb.profiler.profile
def init_settings():
    isettings = carb.settings.acquire_settings_interface()
    if not isettings:
        carb.log_warn("Carb settings not available.")
        return None

    SelectionSettings.init(isettings)
    return isettings


@carb.profiler.profile
def save_implicit_cameras(stage: Usd.Stage, time: Usd.TimeCode = None, camera_path: str = None):
    try:
        if time is None:
            time = Usd.TimeCode.Default()

        def save_camera_settings(cam_path: str, setting_key: str):
            prim = stage.GetPrimAtPath(cam_path)
            camera = UsdGeom.Camera(prim) if prim else None
            if camera is None:
                return

            cam_key = f"cameraSettings:{setting_key}"
            world_xform = camera.ComputeLocalToWorldTransform(time)
            stage.SetMetadataByDictKey("customLayerData", f"{cam_key}:position", world_xform.Transform(Gf.Vec3d(0, 0, 0)))

            target = prim.GetProperty("omni:kit:centerOfInterest")
            target = target.Get() if target else None
            if target:
                if camera.GetProjectionAttr().Get(time) == UsdGeom.Tokens.perspective:
                    stage.SetMetadataByDictKey("customLayerData", f"{cam_key}:target", world_xform.Transform(target))
                else:
                    horiz_ap = camera.GetHorizontalApertureAttr()
                    if horiz_ap and horiz_ap.IsValid():
                        stage.SetMetadataByDictKey("customLayerData", f"{cam_key}:radius", horiz_ap.Get() / 10)

        with Usd.EditContext(stage, stage.GetRootLayer()):
            if camera_path:
                stage.SetMetadataByDictKey("customLayerData", "cameraSettings:boundCamera", camera_path)
            save_camera_settings("/OmniverseKit_Persp", "Perspective")
            save_camera_settings("/OmniverseKit_Front", "Front")
            save_camera_settings("/OmniverseKit_Right", "Right")
            save_camera_settings("/OmniverseKit_Top", "Top")
    except Exception:  # noqa PLW0718
        _report_error()


class StageAxis:
    """Utility class to update implcit cameras when the Usd.Stage up-axis changes"""
    def __init__(self, stage: Usd.Stage, up_axis: str = None):
        self.__up_axis = (up_axis if up_axis else UsdGeom.GetStageUpAxis(stage)).upper()

    @staticmethod
    def __get_adjustment_matrix(current_up, previous_up):
        if current_up == previous_up:
            return Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        # Y => Z or X
        if previous_up == UsdGeom.Tokens.y:
            if current_up == UsdGeom.Tokens.z:
                return Gf.Matrix4d(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1)
            return Gf.Matrix4d(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1)
        # Z => Y or X
        if previous_up == UsdGeom.Tokens.z:
            if current_up == UsdGeom.Tokens.y:
                return Gf.Matrix4d(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1)
            return Gf.Matrix4d(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1)
        # X => Y or Z
        if current_up == UsdGeom.Tokens.y:
            return Gf.Matrix4d(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1)
        return Gf.Matrix4d(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1)

    @carb.profiler.profile
    def update(self, stage: Usd.Stage, time_code: Usd.TimeCode, usd_context_name: str, first_instance: bool,
               exclude_cameras: Optional[List[str]] = None):
        up_axis = UsdGeom.GetStageUpAxis(stage).upper()
        if up_axis == self.__up_axis:
            return False

        adjustment = self.__get_adjustment_matrix(up_axis, self.__up_axis)
        self.__up_axis = up_axis

        # Only the first instance needs to handle implicit camera scene changes
        if not first_instance:
            return True

        def adjust_session_camera(cam_path: Sdf.Path, adjustment: Gf.Matrix4d, time_code: Usd.TimeCode):
            cam_prim = stage.GetPrimAtPath(cam_path)
            xformable = UsdGeom.Xformable(cam_prim) if cam_prim else None
            if not xformable:
                return

            cur_xform = xformable.GetLocalTransformation(time_code)
            new_transform_matrix = cur_xform * adjustment

            try:
                import omni.kit.commands
                omni.kit.commands.create(
                    "TransformPrimCommand",
                    path=cam_path,
                    new_transform_matrix=new_transform_matrix,
                    old_transform_matrix=cur_xform,
                    time_code=time_code,
                    usd_context_name=usd_context_name
                ).do()
            except ModuleNotFoundError:
                carb.log_warn("omni.kit.commands.TransformPrimCommand is not available using UsdGeom.XformCommonAPI")

                timesampled = False
                for op in ("translate", "rotateXYZ", "scale"):
                    xf_attr = cam_prim.GetAttribute(f"xformOp:{op}")
                    timesampled = xf_attr.IsValid() and xf_attr.GetNumTimeSamples() > 1
                    if timesampled:
                        break
                if not timesampled:
                    time_code = Usd.TimeCode.Default()

                rotation = new_transform_matrix.ExtractRotation()
                rotation = rotation.Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
                rotation = Gf.Vec3f(rotation[2], rotation[1], rotation[0])

                with Usd.EditContext(stage, stage.GetSessionLayer()):
                    xfcommon_api = UsdGeom.XformCommonAPI(xformable)
                    xfcommon_api.SetXformVectors(translation=new_transform_matrix.ExtractTranslation(),
                                                 rotation=Gf.Vec3f(rotation),
                                                 scale=Gf.Vec3f(1, 1, 1),
                                                 pivot=Gf.Vec3f(0, 0, 0),
                                                 rotationOrder=UsdGeom.XformCommonAPI.RotationOrderXYZ,
                                                 time=time_code)

        for cam_path in ["/OmniverseKit_Persp", "/OmniverseKit_Front", "/OmniverseKit_Right", "/OmniverseKit_Top"]:
            if exclude_cameras and cam_path in exclude_cameras:
                continue
            adjust_session_camera(cam_path, adjustment, time_code)

        return True
