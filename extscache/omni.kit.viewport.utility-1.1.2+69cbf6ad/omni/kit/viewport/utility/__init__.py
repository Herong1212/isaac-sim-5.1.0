"""An utility module to access [active] Viewport information"""
# Copyright (c) 2022-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = [
    "frame_viewport_prims",
    "frame_viewport_selection",
    "get_viewport_from_window_name",
    "get_active_viewport",
    'get_active_viewport_window',
    "get_active_viewport_and_window",
    "get_viewport_window_camera_path",
    "get_viewport_window_camera_string",
    "get_active_viewport_camera_path",
    "get_active_viewport_camera_string",
    "get_num_viewports",
    "capture_viewport_to_file",
    "capture_viewport_to_buffer",
    "post_viewport_message",
    "toggle_global_visibility",
    "create_drop_helper",
    "disable_selection",
    "get_ground_plane_info",
]


import asyncio
import carb

from pxr import Gf, Sdf

from typing import Callable, List, Optional, Tuple, Union


_g_is_viewport_next = None


def _is_viewport_next(self):
    global _g_is_viewport_next
    if _g_is_viewport_next is None:
        vp_window_name = carb.settings.get_settings().get("/exts/omni.kit.viewport.window/startup/windowName")
        _g_is_viewport_next = vp_window_name and (vp_window_name == "Viewport")
    return _g_is_viewport_next


def _get_default_viewport_window_name(window_name: str = None):
    if window_name:
        return window_name
    return carb.settings.get_settings().get("/exts/omni.kit.viewport.window/startup/windowName") or "Viewport"


def get_viewport_from_window_name(window_name: str = None):
    """
    Retrieves the first viewport API instance from a specified window name.

    If a window name is not provided or is None, it defaults to the viewport window name
    defined in the settings ('/exts/omni.kit.viewport.window/startup/windowName') or 'Viewport'.

    Args:
        window_name (str, optional): The name of the window from which to retrieve the viewport API.

    Returns:
        Optional[ViewportAPI]: An instance of the viewport API or None if no viewport was found.
    """
    window_name = _get_default_viewport_window_name(window_name)
    try:
        from omni.kit.viewport.window import get_viewport_window_instances

        # Get every ViewportWindow, regardless of UsdContext it is attached to
        for window in get_viewport_window_instances(None):
            if window.title == window_name:
                return window.viewport_api
    except ImportError:
        pass

    return None


def get_active_viewport_and_window(usd_context_name: str = "", window_name: str = None, **kwargs):
    """
    Retrieves the active viewport and its window for a given USD context and window name.

    Args:
        usd_context_name (str, optional): The name of the USD context to query. If empty, the current USD context is used.
        window_name (str, optional): The name of the window to query. If none is provided, defaults to the viewport window name from settings.

    Returns:
        Tuple[Optional[ViewportAPI], Optional[Window]]: A tuple containing the active viewport API instance and the corresponding window instance, or (None, None) if not found.
    """
    if isinstance(window_name, bool) or kwargs.get("wrap_legacy", None) != None:
        carb.log_error("wrap_legacy is not a valid argument to get_active_viewport_and_window")

    default_window_name = _get_default_viewport_window_name(window_name)
    try:
        from omni.kit.viewport.window import get_viewport_window_instances, ViewportWindow

        # If no windowname provided, see if the ViewportWindow already knows what is active
        if window_name is None:
            active_window = ViewportWindow.active_window
            if active_window:
                # Have an active Window, need to make sure UsdContext name matches (or passed None to avoid the match)
                viewport_api = active_window.viewport_api
                if (usd_context_name is None) or (usd_context_name == viewport_api.usd_context_name):
                    return (viewport_api, active_window)

        active_window = None
        # Get all ViewportWindows attached the UsdContext with this name
        for window in get_viewport_window_instances(usd_context_name):
            # If matching by name, check that first ignoring whether focused or not (multiple Windows cannot have same name)
            window_title = window.title
            if window_name and window_name != window_title:
                continue

            # If this Window is focused, then return it
            if window.focused:
                active_window = window
                break
            # Save the first encountered Window as he fallback 'default' Window
            if window_title == default_window_name:
                active_window = window
            elif active_window is None:
                active_window = window
        if active_window:
            return (active_window.viewport_api, active_window)
    except ImportError:
        pass

    return (None, None)


def get_active_viewport_window(window_name: str = None, usd_context_name: str = "", **kwargs):
    """
    Retrieves the active viewport window, optionally for a specified USD context and window name.

    Args:
        window_name (str, optional): The name of the window to query. If none is provided, defaults to the viewport window name from settings.
        usd_context_name (str, optional): The name of the USD context to query. If empty, the current USD context is used.

    Returns:
        Optional[Window]: The active viewport window instance or None if not found.
    """
    return get_active_viewport_and_window(usd_context_name, window_name, **kwargs)[1]


def get_active_viewport(usd_context_name: str = ""):
    """
    Retrieves the active viewport API instance for a given USD context.

    If no USD context name is provided, the current USD context is used.

    Args:
        usd_context_name (str, optional): The name of the USD context to query. Defaults to an empty string,
            which indicates the current USD context.

    Returns:
        Optional[ViewportAPI]: The active viewport API instance, or None if not found.
    """
    return get_active_viewport_and_window(usd_context_name)[0]


def get_viewport_window_camera_path(window_name: str = None) -> Sdf.Path:
    """Retrieves the camera path for the viewport in the specified window.

    If the window name is not provided, the default viewport window is used.

    Args:
        window_name (str, optional): The name of the window from which to retrieve the camera path.

    Returns:
        Sdf.Path: The SDF path to the camera used by the viewport, or None if the viewport is not found.
    """
    viewport_api = get_viewport_from_window_name(window_name)
    return viewport_api.camera_path if viewport_api else None


def get_viewport_window_camera_string(window_name: str = None) -> str:
    """
    Retrieves the camera path string for the viewport in the specified window.

    If the window name is not provided, the default viewport window is used.

    Args:
        window_name (str, optional): The name of the window from which to retrieve the camera path string.

    Returns:
        str: The camera path string for the viewport, or None if the viewport is not found.
    """
    viewport_api = get_viewport_from_window_name(window_name)
    return viewport_api.camera_path.pathString if viewport_api else None


def get_active_viewport_camera_path(usd_context_name: str = "") -> Sdf.Path:
    """
    Retrieves the camera Sdf.Path for the active viewport within a specified USD context.

    Args:
        usd_context_name (str, optional): The name of the USD context to query.
            If empty, the current USD context is used. Defaults to an empty string.

    Returns:
        Sdf.Path: The SDF path to the camera used by the active viewport, or None if no active viewport is found.
    """
    viewport_api = get_active_viewport(usd_context_name)
    return viewport_api.camera_path if viewport_api else None


def get_active_viewport_camera_string(usd_context_name: str = "") -> str:
    """
    Retrieves the camera path string for the active viewport within a specified USD context.

    Args:
        usd_context_name (str, optional): The name of the USD context to query.
            If empty, the current USD context is used. Defaults to an empty string.

    Returns:
        str: The camera path string for the active viewport, or an empty string if no active viewport is found.
    """
    viewport_api = get_active_viewport(usd_context_name)
    return viewport_api.camera_path.pathString if viewport_api else None


def get_available_aovs_for_viewport(viewport_api):
    """This function is deprecated and does nothing.

    Args:
        viewport_api (ViewportAPI): The viewport API instance for which to retrieve the available AOVs.

    Returns:
        List[str]: A list of AOV names that are available for the given viewport. If AOVs are not implemented, returns an empty list.
    """
    carb.log_error("Available AOVs not implemented")
    return []


def add_aov_to_viewport(viewport_api, aov_name: Union[str, List[str]]):
    """Adds an Arbitrary Output Variable (AOV) to the specified viewport.

    Args:
        viewport_api: The viewport API instance to which the AOV will be added.
        aov_name (str): The name of the AOV to add.

    Returns:
        bool: True if the AOV was successfully added, False otherwise.

    Raises:
        RuntimeError: If the renderProduct or renderVar cannot be created or set.
    """
    from pxr import Usd, UsdRender
    from omni.usd import editor

    stage = viewport_api.stage
    render_product_path = viewport_api.render_product_path

    def write_kit_attributes(render_var_prim):
        editor.set_hide_in_stage_window(render_var_prim, True)
        editor.set_no_delete(render_var_prim, True)

    def write_usd_attributes(aov_names):
        if isinstance(aov_names, str):
            aov_names = [aov_names]

        render_prod_prim = stage.GetPrimAtPath(render_product_path)
        if not render_prod_prim:
            raise RuntimeError(f'Invalid renderProduct "{render_product_path}"')

        render_prod_var_rel = render_prod_prim.GetRelationship("orderedVars")
        if not render_prod_var_rel:
            render_prod_prim.CreateRelationship("orderedVars")
        if not render_prod_var_rel:
            raise RuntimeError(f'cannot set orderedVars relationship for renderProduct "{render_product_path}"')

        render_var_prims = []
        for aov_name in aov_names:
            render_var_prim_path = Sdf.Path(f"/Render/Vars/{aov_name}")
            render_var_prim = stage.GetPrimAtPath(render_var_prim_path)
            if not render_var_prim:
                render_var_prim = stage.DefinePrim(render_var_prim_path)
            if not render_var_prim:
                raise RuntimeError(f'Cannot create renderVar "{render_var_prim_path}"')

            render_var_prim.CreateAttribute("sourceName", Sdf.ValueTypeNames.String).Set(aov_name)
            render_prod_var_rel.AddTarget(render_var_prim_path)
            render_var_prims.append(render_var_prim)

        return render_var_prims

    # Write to proper layer (session vs current authoring layer) based on render-settings
    if not carb.settings.get_settings().get("/app/hydra/renderSettings/saveUsdAttributes"):
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            for render_var_prim in write_usd_attributes(aov_name):
                write_kit_attributes(render_var_prim)
    else:
        render_var_prims = write_usd_attributes(aov_name)
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            for render_var_prims in render_var_prims:
                write_kit_attributes(render_var_prim)

    return True


def post_viewport_message(viewport_api_or_window, message: str, message_id: str = None):
    """
    Posts a message as a toast notification to the viewport or viewport window.

    Args:
        viewport_api_or_window: The viewport API instance or viewport window to which the message will be posted.
        message (str): The content of the message to post.
        message_id (str, optional): A unique identifier for the message. Defaults to None.
    """
    if hasattr(viewport_api_or_window, "_post_toast_message"):
        viewport_api_or_window._post_toast_message(message, message_id)
        return

    try:
        from omni.kit.viewport.window import get_viewport_window_instances

        for window in get_viewport_window_instances(viewport_api_or_window.usd_context_name):
            if window.viewport_api.id == viewport_api_or_window.id:
                window._post_toast_message(message, message_id)
                return
    except (ImportError, AttributeError):
        pass


def capture_viewport_to_buffer(viewport_api, on_capture_fn: Callable, is_hdr: bool = False):
    """
    Captures the current viewport and sends the image to a callback function.

    Args:
        viewport_api (ViewportAPI): The viewport API instance to capture.
        on_capture_fn (Callable): The callback function that will receive the image.
        is_hdr (bool, optional): If True, captures the HDR buffer; otherwise, captures the LDR buffer. Defaults to False.

    Returns:
        A future-like object that can be awaited to ensure the capture completes.
    """

    from omni.kit.widget.viewport.capture import ByteCapture
    return viewport_api.schedule_capture(ByteCapture(on_capture_fn, aov_name="HdrColor" if is_hdr else "LdrColor"))


def capture_viewport_to_file(
    viewport_api, file_path: str = None, is_hdr: bool = False, render_product_path: str = None, format_desc: dict = None,
    frame_to_capture = None
):
    """Capture the provided viewport to a file.

    Args:
        viewport_api (ViewportAPI): The viewport API instance to capture.
        file_path (str, optional): The file path where the captured image will be saved. If not specified, a default path is used.
        is_hdr (bool, optional): If True, captures the HDR buffer; otherwise, captures the LDR buffer. Defaults to False.
        render_product_path (str, optional): Render product path to use for capturing. Defaults to None.
        format_desc (dict, optional): A dictionary describing the format in which to save the captured image. Defaults to None.
        frame_to_capture (int, optional): A specific SWH frame number to capture. Defaults to None.

    Returns:
        A future-like object that can be awaited to ensure the capture completes.
    """
    from omni.kit.widget.viewport.capture import MultiAOVFileCapture

    class HdrCaptureHelper(MultiAOVFileCapture):
        """A helper class for capturing high dynamic range (HDR) images from a viewport.

        This class manages the process of capturing images from a viewport and saving them in HDR format.
        It extends the MultiAOVFileCapture class to handle HDR image capture specifically.

        Args:
            file_path: str
                The file path where the captured image will be saved.
            is_hdr: bool
                Indicates whether to capture in HDR format.
            format_desc: dict, optional
                A dictionary describing the format in which to save the captured image."""

        def __init__(self, file_path: str, is_hdr: bool, format_desc: dict = None):
            """Initializes the HdrCaptureHelper instance. """
            super().__init__(["HdrColor" if is_hdr else "LdrColor"], [file_path],
                frame_to_capture=frame_to_capture, viewport=viewport_api)
            # Setup RenderProduct for Hdr

        def __del__(self):
            # Setdown RenderProduct for Hdr
            pass

        def capture_aov(self, file_path, aov):
            if render_product_path:
                self.save_product_to_file(file_path, render_product_path)
            else:
                self.save_aov_to_file(file_path, aov, format_desc=format_desc)

    return viewport_api.schedule_capture(HdrCaptureHelper(str(file_path), is_hdr))


def get_num_viewports(usd_context_name: str = None):
    """
    Returns the number of active viewports within an optional USD context.

    Args:
        usd_context_name (str, optional): The name of the USD context for which to count the viewports.
            If None, all viewports across all USD contexts are counted. Defaults to None.

    Returns:
        int: The number of active viewports.
    """
    try:
        from omni.kit.viewport.window import get_viewport_window_instances
        return sum(1 for _ in get_viewport_window_instances(usd_context_name))
    except ImportError:
        pass

    return 0


def create_viewport_window(
    name: str = None,
    usd_context_name: str = "",
    width: int = 1280,
    height: int = 720,
    position_x: int = 0,
    position_y: int = 0,
    camera_path: Sdf.Path = None,
    **kwargs,
):
    """Creates a new viewport window with the given parameters.

    Args:
        name (str, optional): The name of the new viewport window. If None, a default name is generated.
        usd_context_name (str, optional): The name of the USD context to associate with the new viewport window.
        width (int, optional): The width of the new viewport window in pixels.
        height (int, optional): The height of the new viewport window in pixels.
        position_x (int, optional): The x-coordinate of the new viewport window's position.
        position_y (int, optional): The y-coordinate of the new viewport window's position.
        camera_path (Sdf.Path, optional): The path to the camera to be used in the new viewport window.
        **kwargs: Arbitrary keyword arguments to be passed into create_viewport_window.

    Returns:
        The created viewport window or None if the creation fails.
    """
    try:
        from omni.kit.viewport.window import get_viewport_window_instances, ViewportWindow

        if name is None:
            name = f"Viewport {get_num_viewports()}"

        window = ViewportWindow(name, usd_context_name, width=width, height=height, **kwargs)

        if window:
            window.setPosition(position_x, position_y)
            if camera_path:
                window.viewport_api.camera_path = camera_path

        return window
    except ImportError:
        pass

    return None


class ViewportPrimReferencePoint:
    """An enumeration for specifying reference points on a USD prim's bounding box within a viewport."""

    BOUND_BOX_CENTER = 0
    """Reference point at the center of the bounding box."""
    BOUND_BOX_LEFT = 1
    """Reference point at the left-most edge of the bounding box."""
    BOUND_BOX_RIGHT = 2
    """Reference point at the right-most edge of the bounding box."""
    BOUND_BOX_TOP = 3
    """Reference point at the top-most edge of the bounding box."""
    BOUND_BOX_BOTTOM = 4
    """Reference point at the bottom-most edge of the bounding box."""


def get_ui_position_for_prim(
    viewport_window,
    prim_path: str,
    alignment: ViewportPrimReferencePoint = ViewportPrimReferencePoint.BOUND_BOX_CENTER,
    **kwargs
):
    """
    Calculates the UI position of a given USD primitive in the viewport window.

    Args:
        viewport_window: The viewport window instance or its name as a string.
        prim_path (str): The USD path to the primitive whose UI position is to be calculated.
        alignment (ViewportPrimReferencePoint, optional): The reference point on the primitive's bounding box to align with.
            Defaults to ViewportPrimReferencePoint.BOUND_BOX_CENTER.

    Returns:
        Tuple[Tuple[float, float], bool]: A tuple containing the (x, y) UI position of the primitive and a boolean indicating success.
    """
    if isinstance(viewport_window, str):
        window_name = str(viewport_window)
        viewport_window = get_active_viewport_window(window_name=window_name)
        if viewport_window is None:
            carb.log_error('No ViewportWindow found with name "{window_name}"')
            return (0, 0), False

    # XXX: omni.ui constants needed
    import omni.ui

    dpi = omni.ui.Workspace.get_dpi_scale()
    if dpi <= 0.0:
        dpi = 1

    # XXX: kit default dock splitter size (4)
    dock_splitter_size = 4 * dpi
    tab_bar_height = 0
    if viewport_window.dock_tab_bar_visible or not (viewport_window.flags & omni.ui.WINDOW_FLAGS_NO_TITLE_BAR):
        tab_bar_height = 22 * dpi

    # Force legacy Viewport code path if requested
    if kwargs.get("force_legacy_api", None) != None:
        carb.log_error("force_legacy_api is no longer supported on get_ui_position_for_prim")

    from pxr import UsdGeom, Gf

    viewport_api = viewport_window.viewport_api
    usd_context = viewport_window.viewport_api.usd_context
    stage = usd_context.get_stage()
    usd_prim = stage.GetPrimAtPath(prim_path) if stage else False
    if usd_prim:
        xformable_prim = UsdGeom.Xformable(usd_prim)
    else:
        xformable_prim = None
    if (not stage) or (not xformable_prim):
        return (0, 0), False

    # Get bounding box from prim
    aabb_min, aabb_max = usd_context.compute_path_world_bounding_box(str(prim_path))
    gf_range = Gf.Range3d(
        Gf.Vec3d(aabb_min[0], aabb_min[1], aabb_min[2]), Gf.Vec3d(aabb_max[0], aabb_max[1], aabb_max[2])
    )
    if gf_range.IsEmpty():
        # May be empty (UsdGeom.Xform for example), so build a scene-scaled constant box
        world_units = UsdGeom.GetStageMetersPerUnit(stage)
        if Gf.IsClose(world_units, 0.0, 1e-6):
            world_units = 0.01

        # XXX: compute_path_world_transform is identity in this case
        if False:
            world_xform = Gf.Matrix4d(*usd_context.compute_path_world_transform(str(prim_path)))
        else:
            import omni.timeline

            time = omni.timeline.get_timeline_interface().get_current_time() * stage.GetTimeCodesPerSecond()
            world_xform = xformable_prim.ComputeLocalToWorldTransform(time)

        ref_position = world_xform.ExtractTranslation()
        extent = Gf.Vec3d(0.2 / world_units)  # 20cm by default
        gf_range.SetMin(ref_position - extent)
        gf_range.SetMax(ref_position + extent)

    # Computes the extent in clipping pos
    mvp = viewport_api.world_to_ndc
    min_x, min_y, min_z = 2.0, 2.0, 2.0
    max_x, max_y, max_z = -2.0, -2.0, -2.0
    for i in range(8):
        corner = gf_range.GetCorner(i)
        pos = mvp.Transform(corner)
        min_x = min(min_x, pos[0])
        min_y = min(min_y, pos[1])
        min_z = min(min_z, pos[2])
        max_x = max(max_x, pos[0])
        max_y = max(max_y, pos[1])
        max_z = max(max_z, pos[2])

    min_point = Gf.Vec3d(min_x, min_y, min_z)
    max_point = Gf.Vec3d(max_x, max_y, max_z)
    mid_point = (min_point + max_point) / 2

    # Map to reference point in screen space
    if alignment == ViewportPrimReferencePoint.BOUND_BOX_LEFT:
        ndc_pos = mid_point - Gf.Vec3d((max_x - min_x) / 2, 0, 0)
    elif alignment == ViewportPrimReferencePoint.BOUND_BOX_RIGHT:
        ndc_pos = mid_point + Gf.Vec3d((max_x - min_x) / 2, 0, 0)
    elif alignment == ViewportPrimReferencePoint.BOUND_BOX_TOP:
        ndc_pos = mid_point + Gf.Vec3d(0, (max_y - min_y) / 2, 0)
    elif alignment == ViewportPrimReferencePoint.BOUND_BOX_BOTTOM:
        ndc_pos = mid_point - Gf.Vec3d(0, (max_y - min_y) / 2, 0)
    else:
        ndc_pos = mid_point

    # Make sure its not clipped
    if (ndc_pos[2] < 0) or (ndc_pos[0] < -1) or (ndc_pos[0] > 1) or (ndc_pos[1] < -1) or (ndc_pos[1] > 1):
        return (0, 0), False

    """
    XXX: Simpler world calculation
    world_pos = gf_range.GetMidpoint()

    dir_sel = (0, 1)
    up_axis = UsdGeom.GetStageUpAxis(stage)
    if up_axis == UsdGeom.Tokens.z:
        dir_sel = (0, 2)
    if up_axis == UsdGeom.Tokens.x:
        dir_sel = (2, 1)

    if alignment == ViewportPrimReferencePoint.BOUND_BOX_LEFT:
        world_pos[dir_sel[0]] = gf_range.GetMin()[dir_sel[0]]
    elif alignment == ViewportPrimReferencePoint.BOUND_BOX_RIGHT:
        world_pos[dir_sel[0]] = gf_range.GetMax()[dir_sel[0]]
    elif alignment == ViewportPrimReferencePoint.BOUND_BOX_TOP:
        world_pos[dir_sel[1]] = gf_range.GetMax()[dir_sel[1]]
    elif alignment == ViewportPrimReferencePoint.BOUND_BOX_BOTTOM:
        world_pos[dir_sel[1]] = gf_range.GetMin()[dir_sel[1]]

    ndc_pos = viewport_api.world_to_ndc.Transform(world_pos)
    """

    x = (ndc_pos[0] + 1.0) / 2.0  # x to [0, 1]
    y = 1 - (ndc_pos[1] + 1.0) / 2.0  # y to [0, 1] and reverse its direction.

    frame = viewport_window.frame
    prim_window_pos_x = dpi * (frame.screen_position_x + x * frame.computed_width) - dock_splitter_size
    prim_window_pos_y = (
        dpi * (frame.screen_position_y + y * frame.computed_height) - tab_bar_height - dock_splitter_size
    )

    return (prim_window_pos_x, prim_window_pos_y), True


def frame_viewport_prims(viewport_api=None, prims: List[str] = None):
    """Frames the view of the viewport to include the specified prims.

    Args:
        viewport_api (ViewportAPI, optional): The viewport API instance to operate on.
            If not provided, the active viewport is used.
        prims (List[str], optional): A list of USD prim paths to frame in the viewport.
            If not provided or empty, no action is taken.

    Returns:
        bool: True if the operation was successful, False otherwise."""
    if not prims:
        return False
    return __frame_viewport_objects(viewport_api, prims=prims)


def frame_viewport_selection(viewport_api=None, **kwargs):
    """Frames the camera in the viewport to include the current selection.

    This function adjusts the camera in the viewport to frame the currently
    selected objects. If no objects are selected, it adjusts the camera to show
    the entire scene.

    Args:
        viewport_api (ViewportAPI, optional): The viewport API instance to operate on.
            If not provided, the active viewport is used.

    Returns:
        bool: True if the operation was successful, False otherwise."""
    if kwargs.get("force_legacy_api", None) != None:
        carb.log_error("force_legacy_api is no longer supported on frame_viewport_selection")

    return __frame_viewport_objects(viewport_api, prims=None)


def __frame_viewport_objects(viewport_api=None, prims: Optional[List[str]] = None):
    if not viewport_api:
        viewport_api = get_active_viewport()
    if not viewport_api:
        return False


    # This is new CODE
    if prims is None:
        # Get current selection
        prims = viewport_api.usd_context.get_selection().get_selected_prim_paths()
        # Pass None to underlying command to signal "frame all" if selection is empty
        prims = prims if prims else None

    stage = viewport_api.stage
    cam_path = viewport_api.camera_path
    if not stage or not cam_path:
        return False
    cam_prim = stage.GetPrimAtPath(cam_path)
    if not cam_prim:
        return False

    import omni.kit.undo
    import omni.kit.commands
    from pxr import UsdGeom

    look_through = None
    # Loop over all targets (should really be only one) and see if we can get a valid UsdGeom.Imageable
    for target in cam_prim.GetRelationship("omni:kit:viewport:lookThrough:target").GetForwardedTargets():
        target_prim = stage.GetPrimAtPath(target)
        if not target_prim:
            continue
        if UsdGeom.Imageable(target_prim):
            look_through = target_prim
            break

    try:
        omni.kit.undo.begin_group()
        resolution = viewport_api.resolution
        omni.kit.commands.execute(
            "FramePrimsCommand",
            prim_to_move=cam_path if not look_through else look_through.GetPath(),
            prims_to_frame=prims,
            time_code=viewport_api.time,
            usd_context_name=viewport_api.usd_context_name,
            aspect_ratio=resolution[0] / resolution[1],
        )
    finally:
        omni.kit.undo.end_group()

    return True


def toggle_global_visibility():
    """
    .. deprecated:: 1.0.15
        use omni.kit.viewport.actions.toggle_global_visibility instead.

    Toggles the global visibility of all viewport layers.

    This function is used to toggle the visibility of all the viewport layers, such as the grid, axis, and
    stage lights. It can be useful when you want to declutter the viewport or focus on specific elements.
    """
    # Forward to omni.kit.viewport.actions and propogate an errors so caller should update code
    carb.log_warn(
        "omni.kit.viewport.utility.toggle_global_visibility is deprecated, use omni.kit.viewport.actions.toggle_global_visibility"
    )
    import omni.kit.actions.core
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.get_action("omni.kit.viewport.actions", "toggle_global_visibility").execute()


async def next_viewport_frame_async(viewport, n_frames: int = 0):
    """
    Waits until frames have been delivered to the Viewport.

    Args:
        viewport: the Viewport to wait for a frame on.
        n_frames: the number of rendered frames to wait for.
    """
    await viewport.usd_context.next_frame_async(viewport, n_frames)


def create_drop_helper(*args, **kwargs):
    """
    Creates a helper object to handle drag-and-drop operations in a viewport.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Any: The drop helper object that can be used to manage drag-and-drop events.
    """
    try:
        from omni.kit.viewport.window.dragdrop.legacy import create_drop_helper

        return create_drop_helper(*args, **kwargs)
    except (ImportError, ModuleNotFoundError):
        pass
    return None


class _DisableViewportWindowLayer:
    def __init__(self, viewport_or_window, layers_and_categories):
        self.__layers = []

        # Find the omni.ui.Window for this Viewport to disable selection manipulator
        viewport_window = None
        from omni.kit.viewport.window import ViewportWindow, get_viewport_window_instances

        if not isinstance(viewport_or_window, ViewportWindow):
            viewport_id = viewport_or_window.id
            for window_instance in get_viewport_window_instances(viewport_or_window.usd_context_name):
                viewport_window_viewport = window_instance.viewport_api
                if viewport_window_viewport.id == viewport_id:
                    viewport_window = window_instance
                    break
        else:
            viewport_window = viewport_or_window

        if viewport_window:
            for layer, category in layers_and_categories:
                found_layer = viewport_window._find_viewport_layer(layer, category)
                if found_layer:
                    self.__layers.append((found_layer, found_layer.visible))
                    found_layer.visible = False

    def __del__(self):
        for layer, visible in self.__layers:
            layer.visible = visible
        self.__layers = tuple()


def disable_selection(viewport_or_window, disable_click: bool = True):
    """Disables selection for a given viewport.

    Disable selection rect and possible the single click selection on a Viewport or ViewportWindow.
    Returns an object that resets selection when it goes out of scope.

    Args:
        viewport_or_window: The viewport API instance or viewport window to which the selection disabling will be applied.
        disable_click (bool, optional): If set to True, disables single click selection. Defaults to True.

    Returns:
        object: An object that, upon deletion, will reset the selection capability to its original state.
    """
    disable_items = [("Selection", "manipulator")]
    if disable_click:
        disable_items.append(("ObjectClick", "manipulator"))

    return _DisableViewportWindowLayer(viewport_or_window, disable_items)


def disable_context_menu(viewport_or_window=None):
    """Disable context menu on a Viewport or ViewportWindow.
    Returns an object that resets context menu visibility when it goes out of scope.

    Args:
        viewport_or_window (ViewportAPI or ViewportWindow, optional): The viewport API instance or viewport window to which the context menu disabling will be applied.

    Returns:
        object: An object that, upon deletion, will reset the context menu capability to its original state.
    """
    if viewport_or_window is None:
        class _DisableAllContextMenus:
            def __init__(self):
                # When setting is initially unset, then context menu is enabled
                self.__settings = carb.settings.get_settings()
                enabled = self.__settings.get("/exts/omni.kit.window.viewport/showContextMenu")
                self.__settings.set("/exts/omni.kit.window.viewport/showContextMenu", False)
                self.__restore = enabled if (enabled is not None) else True

            def __del__(self):
                self.__settings.set("/exts/omni.kit.window.viewport/showContextMenu", self.__restore)

        return _DisableAllContextMenus()

    return _DisableViewportWindowLayer(viewport_or_window, [("ContextMenu", "manipulator")])


def get_ground_plane_info(viewport, ortho_special: bool = True) -> Tuple[Gf.Vec3d, List[str]]:
    """
    Retrieves the ground plane information including its normal and the planes it occupies.

    Args:
        viewport (ViewportAPI): The viewport API instance for which to get the ground plane information.
        ortho_special (bool, optional): If True, uses an alternate ground plane for orthographic cameras
            that are looking down a single axis. Defaults to True.

    Returns:
        Tuple[Gf.Vec3d, List[str]]: A tuple containing the ground plane normal vector and a list of
            plane axes it occupies (e.g., ['x', 'z']).
    """

    stage = viewport.stage
    cam_path = viewport.camera_path

    from pxr import UsdGeom

    up_axis = UsdGeom.GetStageUpAxis(stage) if stage else UsdGeom.Tokens.y
    if up_axis == UsdGeom.Tokens.y:
        normal = Gf.Vec3d.YAxis()
        planes = ["x", "z"]
    elif up_axis == UsdGeom.Tokens.z:
        normal = Gf.Vec3d.ZAxis()
        planes = ["x", "y"]
    else:
        normal = Gf.Vec3d.XAxis()
        planes = ["y", "z"]

    if ortho_special:
        cam_prim = stage.GetPrimAtPath(cam_path) if stage else None
        if cam_prim:
            usd_camera = UsdGeom.Camera(cam_prim)
            if usd_camera and usd_camera.GetProjectionAttr().Get(viewport.time) == UsdGeom.Tokens.orthographic:
                orthoEpsilon = 0.0001
                viewNormal = viewport.transform.TransformDir(Gf.Vec3d(0, 0, -1))
                if Gf.IsClose(abs(viewNormal[1]), 1.0, orthoEpsilon):
                    normal = Gf.Vec3d.YAxis()
                    planes = ["x", "z"]
                elif Gf.IsClose(abs(viewNormal[2]), 1.0, orthoEpsilon):
                    normal = Gf.Vec3d.ZAxis()
                    planes = ["x", "y"]
                elif Gf.IsClose(abs(viewNormal[0]), 1.0, orthoEpsilon):
                    normal = Gf.Vec3d.XAxis()
                    planes = ["y", "z"]

    return normal, planes
