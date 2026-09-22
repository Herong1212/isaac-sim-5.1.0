from __future__ import annotations
import omni.hydratexture._hydra_texture
import typing
import carb._carb
import carb.events._events
import omni.gpu_foundation_factory._gpu_foundation_factory
import omni.usd._usd

__all__ = [
    "EVENT_TYPE_DRAWABLE_CHANGED",
    "EVENT_TYPE_HYDRA_ENGINE_CHANGED",
    "EVENT_TYPE_RENDER_SETTINGS_CHANGED",
    "IHydraTexture",
    "IHydraTextureFactory",
    "TextureGpuReference",
    "acquire_hydra_texture_factory_interface"
]


class IHydraTexture():
    def _get_drawable_ldr_resource(self, result_handle: int = 0) -> omni.gpu_foundation_factory._gpu_foundation_factory.RpResource: 
        """
        Get the drawable resource for the low-dynamic-range color buffer.
        """
    def _get_imgui_reference(self, result_handle: int = 0, aov_name: str = '') -> capsule: 
        """
        Deprecated function, DO NOT USE
        """
    def cancel_all_picking(self) -> None: 
        """
        Cancel any picking or query requests that are in flight or queued.
        """
    def get_aov_info(self, result_handle: int = 0, aov_name: str = None, include_texture: bool = False) -> typing.List[dict]: 
        """
        Get AOV data durring EVENT_TYPE_DRAWABLE_CHANGED as a list of dictionaries.

        Args:
            include_texture: (bool) Whether to include a dictionary for the AOVs texture, under the key 'texture' (defaults to False).
        Returns:
            A list of dictionaries [{'name': str, 'texture': dict}]
        """
    def get_async(self) -> bool: 
        """
        Returns whether rendering is performed on a separate thread.

        Returns:
            Whether rendering is performed on a separate thread as a bool.
        """
    def get_camera_path(self) -> str: 
        """
        Returns the path to the pxr.UsdGeom.Camera that will be used by the HydraEngine (Deprecated, use the "camera_path" property).
        Returns:
            The path to the pxr.UsdGeom.Camera this HydraTexture is rendering as a string.
        """
    def get_drawable_resource(self, result_handle: int = 0, aov_name: str = '') -> omni.gpu_foundation_factory._gpu_foundation_factory.RpResource: 
        """
        Deprecated function, DO NOT USE
        """
    def get_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Returns the event stream where events like drawable change are pumped.

        Returns:
            The event stream where events like drawable change are pumped.
        """
    def get_frame_info(self, result_handle: int = 0, include_aov_list: bool = False) -> dict: 
        """
        Get additional data durring EVENT_TYPE_DRAWABLE_CHANGED in dictionary form.

        Args:
            result_handle: The result_handle passed as a key in the carb.event.IEvent payload for the EVENT_TYPE_DRAWABLE_CHANGED callback.
            include_aov_list (bool) = False: Whether to include an 'aovs' entry in the dict for the aovs available from the render (defaults to False).

        Returns:
            A dictionary.
            {
            'view': [float] * 16,
            'projection': [float] * 16,
            'fps': float,
            'resolution': (uint, uint),
            'progression': uint,
            'frame_number': number,
            'swh_frame_number': Optional[number],
            'subframe_count': uint,
            'progression': uint,
            'aovs' : list
            }
        """
    def get_height(self) -> int: 
        """
        Returns the texture height (Deprecated, use the "height" property).

        Returns:
            The height of the HydraTexture as an int.
        """
    def get_hydra_engine(self) -> str: 
        """
        Returns HydraEngine that is used currently to render to the associated texture  (Deprecated, use the "hydra_engine" property).

        Returns:
            The HydraEngine this HydraTexture is rendering with as a string.
        """
    def get_name(self) -> str: 
        """
        Returns name of the HydraTexture.

        Returns:
            The name of the HydraTexture as a str.
        """
    def get_render_product_path(self) -> str: 
        """
        Returns the prim path for the render product
        """
    def get_settings_path(self) -> str: 
        """
        Returns path to the settings section where this HydraTexture tracks its state.

        Returns:
            The path to the settings section where this HydraTexture tracks its state as a string.
        """
    def get_updates_enabled(self) -> bool: 
        """
        Returns whether the HydraTexture is active and requesting renderers to be delivered.
        (Deprecated, use the "updates_enabled" property).

        Returns:
            Whether the HydraTexture is active and requesting renderers to be delivered as a bool.
        """
    def get_usd_context_name(self) -> str: 
        """
        Returns name of the omni.usd.UsdContext this HydraTexture is attached too.

        Returns:
            The name of the omni.usd.UsdContext as a str.
        """
    def get_width(self) -> int: 
        """
        Returns the texture width (Deprecated, use the "width" property).

        Returns:
            The width of the HydraTexture as an int.
        """
    def pick(self, x_left: int, y_top: int, x_right: int = 0, y_bottom: int = 0, mode: omni.usd._usd.PickingMode = PickingMode.TRACK, pick_name: str = '', y_down: bool = True) -> None: 
        """
        Pick a pixel in the HydraTexture.

        Args:
            x_left (uint): The left-most x coordinate to pick.
            y_top (uint): The top-most y coordinate to pick.
            x_right (uint): The right-most x coordinate to pick.
            y_bottom (uint): The bottom-most y coordinate to pick.
            mode (omni.usd.PickingMode) = omni.usd.PickingMode.TRACK: The mode to use when the pick completes (defaults to omni.usd.PickingMode.TRACK)
            pick_name (str) = "": A unique name for the pick to use to update/reschedule before a previous pick has completed.
            y_down (bool) = False: Whether to treat the pixel coordinate as y-down (defaults to False).
        """
    def query(self, x: int, y: int, callback: typing.Callable[[str, carb._carb.Double3, carb._carb.Uint2], None] = None, add_outline: bool = False, query_name: str = '', y_down: bool = True) -> None: 
        """
        Query a pixel in the HydraTexture.
        """
    def request_pick(self, p0: carb._carb.Uint2, p1: carb._carb.Uint2, mode: omni.usd._usd.PickingMode = PickingMode.TRACK, pick_name: str = '', y_down: bool = True) -> bool: 
        """
        Pick a pixel in the HydraTexture.

        Args:
            p0: (Sequence[uint, uint]): The top left pixel coordinate.
            p1: (Sequence[uint, uint]): The bottom-right pixel coordinate.
            mode: (omni.usd.PickingMode) The mode to use when the pick completes (defaults to omni.usd.PickingMode.TRACK)
            pick_name: (str) A unique name for the pick to use to update/reschedule before a previous pick has completed.
        """
    @typing.overload
    def request_query(self, pixel: carb._carb.Uint2, callback: typing.Callable[[str, carb._carb.Double3, carb._carb.Uint2], None] = None, query_name: str = '', add_outline: bool = False, y_down: bool = True) -> bool: 
        """
        Query a pixel in the HydraTexture.

        Args:
            pixel (Sequence[uint, uint]): The pixel coordinate for the query.
            callback (Callable): The object to invoke when the query has completed.
            query_name (str) = "": A unique name for the query to use to update/reschedule before a previous query has completed.
            add_outline (bool) = False: Whether to add an outline to any objects the query finds (defaults to False).
            y_down (bool) = False: Whether to treat the pixel coordinate as y-down (defaults to False).

        Query a pixel in the HydraTexture.

        Args:
            pixel (Sequence[uint, uint]): The pixel coordinate for the query.
            callback (Callable): The object to invoke when the query has completed.
            query_name (str): A unique name for the query to use to update/reschedule before a previous query has completed.
            view ([float] * 16) = None: The view matrix to use for the query.
            projection ([float] * 16) = None: The projection matrix to use for the query.
            add_outline (bool) = False: Whether to add an outline to any objects the query finds (defaults to False).
            y_down (bool) = False: Whether to treat the pixel coordinate as y-down (defaults to False).
        """
    @typing.overload
    def request_query(self, pixel: carb._carb.Uint2, callback: typing.Callable[[str, carb._carb.Double3, carb._carb.Uint2], None] = None, query_name: str = '', view: handle = None, projection: handle = None, add_outline: bool = False, y_down: bool = True) -> bool: ...
    def set_async(self, is_async: bool) -> None: 
        """
        Sets whether it is desirable to perform rendering on another thread.
        """
    def set_camera_path(self, usd_camera_path: str = '/OmniverseKit_Persp') -> None: 
        """
        Sets the USD camera prim path that will be used by the HydraEngine (Deprecated, use the "camera_path" property).

        Args:
            usd_camera_path (str): The full path to the pxr.UsdGeom.Camera to render with.
        """
    def set_height(self, height: int) -> None: 
        """
        Sets the texture height (Deprecated, use the "height" property).

        Args:
            height (uint): The height to render at.
        """
    def set_hydra_engine(self, hydra_engine_name: str = 'rtx') -> None: 
        """
        Sets the desired HydraEngine that should render to the associated texture (Deprecated, use the "hydra_engine" property).

        Args:
            hydra_engine_name (str): The name of the render-engine to render with.
        """
    def set_render_product_path(self, prim_path: str, keep_camera: bool = False, keep_resolution: bool = False) -> bool: 
        """
        Sets the prim path for the render product.

        Args:
            prim_path (str): The prim path to a valid UsdRenderProduct.
            keep_camera (bool) = False:  Keep the viewport's current camera.
            keep_resolution (bool) = False: Keep the viewport's current resolution.
        """
    def set_updates_enabled(self, updates_enabled: bool = True) -> None: 
        """
        Allows to pause/resume rendering updates. When updates are disabled, calls to render from the associated HydraEngine are not made.
        (Deprecated, use the "updates_enabled" property).

        Args:
            updates_enabled: (bool) Whether to enable or disable rendering for this HydraTexture.
        """
    def set_width(self, width: int) -> None: 
        """
        Sets the HydraTexture width (Deprecated, use the "width" property).

        Args:
            width (uint): The width to render at.
        """
    @property
    def camera_path(self) -> str:
        """
        Gets/sets the USD camera prim path that will be used by the HydraEngine.

        :type: str
        """
    @camera_path.setter
    def camera_path(self, arg1: str) -> None:
        """
        Gets/sets the USD camera prim path that will be used by the HydraEngine.
        """
    @property
    def height(self) -> int:
        """
        Gets/sets the texture height.

        :type: int
        """
    @height.setter
    def height(self, arg1: int) -> None:
        """
        Gets/sets the texture height.
        """
    @property
    def hydra_engine(self) -> str:
        """
        Gets/sets the desired HydraEngine that should render to the associated texture.

        :type: str
        """
    @hydra_engine.setter
    def hydra_engine(self, arg1: str) -> None:
        """
        Gets/sets the desired HydraEngine that should render to the associated texture.
        """
    @property
    def is_async(self) -> bool:
        """
        Gets/sets whether it is desirable to perform rendering on another thread.

        :type: bool
        """
    @is_async.setter
    def is_async(self, arg1: bool) -> None:
        """
        Gets/sets whether it is desirable to perform rendering on another thread.
        """
    @property
    def updates_enabled(self) -> bool:
        """
        Gets/sets viewport updates state. Allows to pause/resume viewport updates. When paused, calls to associated HydraEngine are not made.

        :type: bool
        """
    @updates_enabled.setter
    def updates_enabled(self, arg1: bool) -> None:
        """
        Gets/sets viewport updates state. Allows to pause/resume viewport updates. When paused, calls to associated HydraEngine are not made.
        """
    @property
    def width(self) -> int:
        """
        Gets/sets the texture width.

        :type: int
        """
    @width.setter
    def width(self, arg1: int) -> None:
        """
        Gets/sets the texture width.
        """
    pass
class IHydraTextureFactory():
    def create_hydra_texture(self, name: str, width: int, height: int, usd_context_name: str = '', usd_camera_path: str = '/OmniverseKit_Persp', hydra_engine_name: str = 'rtx', is_async: bool = True, is_async_low_latency: bool = False, hydra_tick_rate: int = 0, engine_creation_flags: int = 0, device_mask: int = 0, is_asyncLowLatency: bool = False, hydraTickRate: int = 0) -> IHydraTexture: 
        """
        Create a HydraTexture instance to receive rendering output.

        Args:
            name (string): A unique name for the HydraTexture being created.
            width (uint): The width of the returned HydraTexture should start rendering at.
            height (uint): The height of the HydraTexture should start rendering at.
            usd_context_name (str) = "": The name of the omni.usd.UsdContext the returned HydraTexture should attached.
            usd_camera_path (str) = "/OmniverseKit_Persp": The full-path to the pxr.UsdGeom.Camera the returned HydraTexture should render from.
            hydra_engine_name (str) = "rtx": The name of the render-engine the returned HydraTexture should render from.
            is_async (bool) = True: Whether the returned HydraTexture will be requesting renders asynchronously.
            is_async_low_latency (bool) = False: Private/Internal.
            hydra_tick_rate (int) = 0: Optionally provide a rate at which to run the rendering engine.
            engine_creation_flags (int): Private/Internal.
            device_mask (int) = 0: Private/Internal
        Returns:
            A HydraTexture instance.
        """
    def get_hydra_texture_from_handle(self, handle: int) -> IHydraTexture: ...
    def shutdown(self) -> bool: ...
    def startup(self) -> bool: ...
    pass
class TextureGpuReference():
    @property
    def gpu_index(self) -> int:
        """
        :type: int
        """
    pass
def acquire_hydra_texture_factory_interface(*args, **kwargs) -> typing.Any:
    pass
EVENT_TYPE_DRAWABLE_CHANGED = 11183105052706112355
EVENT_TYPE_HYDRA_ENGINE_CHANGED = 13015938697279081123
EVENT_TYPE_RENDER_SETTINGS_CHANGED = 5475677776228743414
