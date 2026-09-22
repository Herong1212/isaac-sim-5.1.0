"""pybind11 omni.usd bindings"""
from __future__ import annotations
import omni.usd._usd
import typing
import carb._carb
import carb.events._events
import omni.timeline._timeline

__all__ = [
    "AudioManager",
    "EngineCreationFlags",
    "HydraEngineCreationConfig",
    "HydraEngineDesc",
    "HydraEngineInvalidUniqueId",
    "MOTION_RAYTRACING_ENABLED",
    "NONE",
    "OpaqueSharedHydraEngineContext",
    "PickingMode",
    "SKIP_ON_WORKER_PROCESS",
    "Selection",
    "StageEventType",
    "StageRenderingEventType",
    "StageState",
    "UsdContext",
    "UsdContextInitialLoadSet",
    "WRITABLE_USD_FILE_EXTS_STR",
    "add_hydra_engine",
    "attach_all_hydra_engines",
    "create_context",
    "create_hydra_engine",
    "create_hydra_engine_with_config",
    "destroy_context",
    "destroy_hydra_engine",
    "get_context",
    "get_context_from_stage_id",
    "make_valid_identifier",
    "merge_layers",
    "merge_prim_spec",
    "release_all_hydra_engines",
    "resolve_paths",
    "resolve_prim_path_references",
    "resolve_prim_paths_references",
    "shutdown_usd",
    "stage_event_type",
    "stage_rendering_event_type"
]


class AudioManager():
    """
    Audio manager. See :class:`omni.usd.audio` for wrapped python interfaces that manage audio play/capture.
    """
    pass
class EngineCreationFlags():
    """
            Specifies the flags for the hydra engine creation.
            

    Members:

      NONE

      MOTION_RAYTRACING_ENABLED

      SKIP_ON_WORKER_PROCESS
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    MOTION_RAYTRACING_ENABLED: omni.usd._usd.EngineCreationFlags # value = <EngineCreationFlags.MOTION_RAYTRACING_ENABLED: 1>
    NONE: omni.usd._usd.EngineCreationFlags # value = <EngineCreationFlags.NONE: 0>
    SKIP_ON_WORKER_PROCESS: omni.usd._usd.EngineCreationFlags # value = <EngineCreationFlags.SKIP_ON_WORKER_PROCESS: 2>
    __members__: dict # value = {'NONE': <EngineCreationFlags.NONE: 0>, 'MOTION_RAYTRACING_ENABLED': <EngineCreationFlags.MOTION_RAYTRACING_ENABLED: 1>, 'SKIP_ON_WORKER_PROCESS': <EngineCreationFlags.SKIP_ON_WORKER_PROCESS: 2>}
    pass
class HydraEngineCreationConfig():
    """
    HydraEngineCreationConfig structure.
    """
    def __init__(self) -> None: ...
    @property
    def creation_index(self) -> int:
        """
        :type: int
        """
    @creation_index.setter
    def creation_index(self, arg0: int) -> None:
        pass
    @property
    def device_mask(self) -> int:
        """
        :type: int
        """
    @device_mask.setter
    def device_mask(self, arg0: int) -> None:
        pass
    @property
    def flags(self) -> EngineCreationFlags:
        """
        :type: EngineCreationFlags
        """
    @flags.setter
    def flags(self, arg0: EngineCreationFlags) -> None:
        pass
    @property
    def tickrate_in_hz(self) -> int:
        """
        :type: int
        """
    @tickrate_in_hz.setter
    def tickrate_in_hz(self, arg0: int) -> None:
        pass
    pass
class HydraEngineDesc():
    """
    HydraEngineDesc structure.
    """
    def __init__(self) -> None: ...
    @property
    def config(self) -> HydraEngineCreationConfig:
        """
        :type: HydraEngineCreationConfig
        """
    @config.setter
    def config(self, arg0: HydraEngineCreationConfig) -> None:
        pass
    @property
    def engine_type_name(self) -> str:
        """
        :type: str
        """
    @engine_type_name.setter
    def engine_type_name(self, arg0: str) -> None:
        pass
    @property
    def thread_name(self) -> str:
        """
        :type: str
        """
    @thread_name.setter
    def thread_name(self, arg0: str) -> None:
        pass
    @property
    def uid(self) -> int:
        """
        :type: int
        """
    @uid.setter
    def uid(self, arg0: int) -> None:
        pass
    pass
class OpaqueSharedHydraEngineContext():
    pass
class PickingMode():
    """
    Members:

      NONE

      RESET_AND_SELECT

      MERGE_SELECTION

      INVERT_SELECTION

      TRACK
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    INVERT_SELECTION: omni.usd._usd.PickingMode # value = <PickingMode.INVERT_SELECTION: 3>
    MERGE_SELECTION: omni.usd._usd.PickingMode # value = <PickingMode.MERGE_SELECTION: 2>
    NONE: omni.usd._usd.PickingMode # value = <PickingMode.NONE: 0>
    RESET_AND_SELECT: omni.usd._usd.PickingMode # value = <PickingMode.RESET_AND_SELECT: 1>
    TRACK: omni.usd._usd.PickingMode # value = <PickingMode.TRACK: 5>
    __members__: dict # value = {'NONE': <PickingMode.NONE: 0>, 'RESET_AND_SELECT': <PickingMode.RESET_AND_SELECT: 1>, 'MERGE_SELECTION': <PickingMode.MERGE_SELECTION: 2>, 'INVERT_SELECTION': <PickingMode.INVERT_SELECTION: 3>, 'TRACK': <PickingMode.TRACK: 5>}
    pass
class Selection():
    """
    omni.usd.Selection manages all stage selections and provides APIs for querying/setting selections.
    """
    class SourceType():
        """
                Selection source stage.
                

        Members:

          USD : Selections from native USD stage.

          FABRIC : "Selections from Fabric.

          ALL : Selections from both native USD stage and Fabric.
        """
        def __eq__(self, other: object) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
        def __init__(self, value: int) -> None: ...
        def __int__(self) -> int: ...
        def __ne__(self, other: object) -> bool: ...
        def __repr__(self) -> str: ...
        def __setstate__(self, state: int) -> None: ...
        @property
        def name(self) -> str:
            """
            :type: str
            """
        @property
        def value(self) -> int:
            """
            :type: int
            """
        ALL: omni.usd._usd.Selection.SourceType # value = <SourceType.ALL: 3>
        FABRIC: omni.usd._usd.Selection.SourceType # value = <SourceType.FABRIC: 2>
        USD: omni.usd._usd.Selection.SourceType # value = <SourceType.USD: 1>
        __members__: dict # value = {'USD': <SourceType.USD: 1>, 'FABRIC': <SourceType.FABRIC: 2>, 'ALL': <SourceType.ALL: 3>}
        pass
    def clear_selected_prim_paths(self, source: Selection.SourceType = SourceType.USD) -> bool: 
        """
        Clears all selections.

        Args:
            source (omni.usd.Selection.SourceType): The source to be cleared. Selections are stored differently for Fabric. By default, it will check selections from native
                USD stage.
        """
    def get_selected_prim_paths(self, source: Selection.SourceType = SourceType.USD) -> typing.List[str]: 
        """
        Gets selected prim paths.

        Args:
            source (omni.usd.Selection.SourceType): The source to get selections. Selections are stored differently for Fabric. By default, it will check selections from native
                USD stage.

        Returns:
            List of selected prim paths.
        """
    def is_prim_path_selected(self, path: str, source: Selection.SourceType = SourceType.USD) -> bool: 
        """
        Checks if a prim is selected or not.

        Args:
            path (str): Prim path to be checked.
            source (omni.usd.Selection.SourceType): The source to be checked. Selections are stored differently for Fabric. By default, it will check selections from native
                USD stage.
        """
    def select_all_prims(self, type_names: object = None, type_kind_filtering: bool = False) -> None: 
        """
        Selects all prims with specific prim types.
        """
    def select_inverted_prims(self, type_kind_filtering: bool = False) -> None: 
        """
        Selects all prims without the current selections

        Args:
            type_kind_filtering (bool): Apply type and model-kind filtering to the paths.
        """
    def set_prim_path_selected(self, path: str, selected: bool = True, forcePrim: bool = True, clearSelected: bool = False, expandInStage: bool = True, source: Selection.SourceType = SourceType.USD) -> bool: 
        """
        Selects/Unselects single prim.

        Args:
            path (str): Prim path to be selected.
            selected (bool): Selected or unselected.
            forcePrim (bool): Force it to be Prim Mode. When this option is false, it depends on the selection mode to decide the prim to be selected.
            clearSelected (bool): Clears existing selections or not before selection.
            expandInStage (bool):  DEPRECATED.
            source (omni.usd.Selection.SourceType): The source to be set. Selections are stored differently for Fabric. By default, it will check selections from native
                USD stage.
        """
    def set_selected_prim_paths(self, paths: typing.List[str], expandInStage: bool = True, source: Selection.SourceType = SourceType.USD, type_kind_filtering: bool = False) -> bool: 
        """
        Sets selected prim paths.

        Args:
            paths (List[str]): The list of prim paths to be selected.
            expandInStage (bool): DEPRECATED.
            source (omni.usd.Selection.SourceType): The source to be set. Selections are stored differently for Fabric. By default, it will check selections from native
                USD stage
            type_kind_filtering (bool): Apply type and model-kind filtering to the paths.
        """
    pass
class StageEventType():
    """
            Stage Event Type. Stage events are sent through event stream of the UsdContext.
            

    Members:

      SAVING : Starting to save stage.

      SAVED : Stage saved successfully.

      SAVE_FAILED : Stage save failed.

      OPENING : Starting to open stage.

      OPENED : Stage open finished.

      OPEN_FAILED : Stage open failed.

      CLOSING : Starting to close stage.

      CLOSED : Stage closed successfully.

      SELECTION_CHANGED : Stage selections changed.

      ASSETS_LOADED : Assets (textures or materials) loaded successfully.

      ASSETS_LOAD_ABORTED : Assets (textures or materials) load aborted .

      GIZMO_TRACKING_CHANGED : DEPRECATED.

      MDL_PARAM_LOADED : Some MDL materials finish its params loading by material watcher.

      SETTINGS_LOADED : Render settings loaded.

      SETTINGS_SAVING : Starting to save render settings.

      OMNIGRAPH_START_PLAY : OmniGraph is starting to play.

      OMNIGRAPH_STOP_PLAY : OmniGraph is stopped to play.

      SIMULATION_START_PLAY : Physx Simulation starts playing.

      SIMULATION_STOP_PLAY : Physx Simulation stopped.

      ANIMATION_START_PLAY : Timeline starts playing.

      ANIMATION_STOP_PLAY : Timeline stopped.

      DIRTY_STATE_CHANGED : Stage dirtiness state is changed. It's sent when stage adds the first unsaved change, or after stage finishes it saving.

      ASSETS_LOADING : Assets are in progress of loading (textures or materials).

      ACTIVE_LIGHT_COUNTS_CHANGED : Count of active lights is changed.

      HIERARCHY_CHANGED : Some prims are resynced in the stage.

      HYDRA_GEOSTREAMING_STARTED

      HYDRA_GEOSTREAMING_STOPPED

      HYDRA_GEOSTREAMING_STOPPED_NOT_ENOUGH_MEM

      HYDRA_GEOSTREAMING_STOPPED_AT_LIMIT

      COUNT
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ACTIVE_LIGHT_COUNTS_CHANGED: omni.usd._usd.StageEventType # value = <StageEventType.ACTIVE_LIGHT_COUNTS_CHANGED: 22>
    ANIMATION_START_PLAY: omni.usd._usd.StageEventType # value = <StageEventType.ANIMATION_START_PLAY: 18>
    ANIMATION_STOP_PLAY: omni.usd._usd.StageEventType # value = <StageEventType.ANIMATION_STOP_PLAY: 19>
    ASSETS_LOADED: omni.usd._usd.StageEventType # value = <StageEventType.ASSETS_LOADED: 8>
    ASSETS_LOADING: omni.usd._usd.StageEventType # value = <StageEventType.ASSETS_LOADING: 21>
    ASSETS_LOAD_ABORTED: omni.usd._usd.StageEventType # value = <StageEventType.ASSETS_LOAD_ABORTED: 9>
    CLOSED: omni.usd._usd.StageEventType # value = <StageEventType.CLOSED: 6>
    CLOSING: omni.usd._usd.StageEventType # value = <StageEventType.CLOSING: 5>
    COUNT: omni.usd._usd.StageEventType # value = <StageEventType.COUNT: 29>
    DIRTY_STATE_CHANGED: omni.usd._usd.StageEventType # value = <StageEventType.DIRTY_STATE_CHANGED: 20>
    GIZMO_TRACKING_CHANGED: omni.usd._usd.StageEventType # value = <StageEventType.GIZMO_TRACKING_CHANGED: 10>
    HIERARCHY_CHANGED: omni.usd._usd.StageEventType # value = <StageEventType.HIERARCHY_CHANGED: 23>
    HYDRA_GEOSTREAMING_STARTED: omni.usd._usd.StageEventType # value = <StageEventType.HYDRA_GEOSTREAMING_STARTED: 24>
    HYDRA_GEOSTREAMING_STOPPED: omni.usd._usd.StageEventType # value = <StageEventType.HYDRA_GEOSTREAMING_STOPPED: 25>
    HYDRA_GEOSTREAMING_STOPPED_AT_LIMIT: omni.usd._usd.StageEventType # value = <StageEventType.HYDRA_GEOSTREAMING_STOPPED_AT_LIMIT: 27>
    HYDRA_GEOSTREAMING_STOPPED_NOT_ENOUGH_MEM: omni.usd._usd.StageEventType # value = <StageEventType.HYDRA_GEOSTREAMING_STOPPED_NOT_ENOUGH_MEM: 26>
    MDL_PARAM_LOADED: omni.usd._usd.StageEventType # value = <StageEventType.MDL_PARAM_LOADED: 11>
    OMNIGRAPH_START_PLAY: omni.usd._usd.StageEventType # value = <StageEventType.OMNIGRAPH_START_PLAY: 14>
    OMNIGRAPH_STOP_PLAY: omni.usd._usd.StageEventType # value = <StageEventType.OMNIGRAPH_STOP_PLAY: 15>
    OPENED: omni.usd._usd.StageEventType # value = <StageEventType.OPENED: 3>
    OPENING: omni.usd._usd.StageEventType # value = <StageEventType.OPENING: 2>
    OPEN_FAILED: omni.usd._usd.StageEventType # value = <StageEventType.OPEN_FAILED: 4>
    SAVED: omni.usd._usd.StageEventType # value = <StageEventType.SAVED: 0>
    SAVE_FAILED: omni.usd._usd.StageEventType # value = <StageEventType.SAVE_FAILED: 1>
    SAVING: omni.usd._usd.StageEventType # value = <StageEventType.SAVING: 28>
    SELECTION_CHANGED: omni.usd._usd.StageEventType # value = <StageEventType.SELECTION_CHANGED: 7>
    SETTINGS_LOADED: omni.usd._usd.StageEventType # value = <StageEventType.SETTINGS_LOADED: 12>
    SETTINGS_SAVING: omni.usd._usd.StageEventType # value = <StageEventType.SETTINGS_SAVING: 13>
    SIMULATION_START_PLAY: omni.usd._usd.StageEventType # value = <StageEventType.SIMULATION_START_PLAY: 16>
    SIMULATION_STOP_PLAY: omni.usd._usd.StageEventType # value = <StageEventType.SIMULATION_STOP_PLAY: 17>
    __members__: dict # value = {'SAVING': <StageEventType.SAVING: 28>, 'SAVED': <StageEventType.SAVED: 0>, 'SAVE_FAILED': <StageEventType.SAVE_FAILED: 1>, 'OPENING': <StageEventType.OPENING: 2>, 'OPENED': <StageEventType.OPENED: 3>, 'OPEN_FAILED': <StageEventType.OPEN_FAILED: 4>, 'CLOSING': <StageEventType.CLOSING: 5>, 'CLOSED': <StageEventType.CLOSED: 6>, 'SELECTION_CHANGED': <StageEventType.SELECTION_CHANGED: 7>, 'ASSETS_LOADED': <StageEventType.ASSETS_LOADED: 8>, 'ASSETS_LOAD_ABORTED': <StageEventType.ASSETS_LOAD_ABORTED: 9>, 'GIZMO_TRACKING_CHANGED': <StageEventType.GIZMO_TRACKING_CHANGED: 10>, 'MDL_PARAM_LOADED': <StageEventType.MDL_PARAM_LOADED: 11>, 'SETTINGS_LOADED': <StageEventType.SETTINGS_LOADED: 12>, 'SETTINGS_SAVING': <StageEventType.SETTINGS_SAVING: 13>, 'OMNIGRAPH_START_PLAY': <StageEventType.OMNIGRAPH_START_PLAY: 14>, 'OMNIGRAPH_STOP_PLAY': <StageEventType.OMNIGRAPH_STOP_PLAY: 15>, 'SIMULATION_START_PLAY': <StageEventType.SIMULATION_START_PLAY: 16>, 'SIMULATION_STOP_PLAY': <StageEventType.SIMULATION_STOP_PLAY: 17>, 'ANIMATION_START_PLAY': <StageEventType.ANIMATION_START_PLAY: 18>, 'ANIMATION_STOP_PLAY': <StageEventType.ANIMATION_STOP_PLAY: 19>, 'DIRTY_STATE_CHANGED': <StageEventType.DIRTY_STATE_CHANGED: 20>, 'ASSETS_LOADING': <StageEventType.ASSETS_LOADING: 21>, 'ACTIVE_LIGHT_COUNTS_CHANGED': <StageEventType.ACTIVE_LIGHT_COUNTS_CHANGED: 22>, 'HIERARCHY_CHANGED': <StageEventType.HIERARCHY_CHANGED: 23>, 'HYDRA_GEOSTREAMING_STARTED': <StageEventType.HYDRA_GEOSTREAMING_STARTED: 24>, 'HYDRA_GEOSTREAMING_STOPPED': <StageEventType.HYDRA_GEOSTREAMING_STOPPED: 25>, 'HYDRA_GEOSTREAMING_STOPPED_NOT_ENOUGH_MEM': <StageEventType.HYDRA_GEOSTREAMING_STOPPED_NOT_ENOUGH_MEM: 26>, 'HYDRA_GEOSTREAMING_STOPPED_AT_LIMIT': <StageEventType.HYDRA_GEOSTREAMING_STOPPED_AT_LIMIT: 27>, 'COUNT': <StageEventType.COUNT: 29>}
    pass
class StageRenderingEventType():
    """
            Rendering Events.
            

    Members:

      NEW_FRAME

      HYDRA_ENGINE_FRAMES_COMPLETE

      HYDRA_ENGINE_FRAMES_ADDED

      RENDERER_RECORDING_COMPLETE

      COUNT
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    COUNT: omni.usd._usd.StageRenderingEventType # value = <StageRenderingEventType.COUNT: 4>
    HYDRA_ENGINE_FRAMES_ADDED: omni.usd._usd.StageRenderingEventType # value = <StageRenderingEventType.HYDRA_ENGINE_FRAMES_ADDED: 2>
    HYDRA_ENGINE_FRAMES_COMPLETE: omni.usd._usd.StageRenderingEventType # value = <StageRenderingEventType.HYDRA_ENGINE_FRAMES_COMPLETE: 1>
    NEW_FRAME: omni.usd._usd.StageRenderingEventType # value = <StageRenderingEventType.NEW_FRAME: 0>
    RENDERER_RECORDING_COMPLETE: omni.usd._usd.StageRenderingEventType # value = <StageRenderingEventType.RENDERER_RECORDING_COMPLETE: 3>
    __members__: dict # value = {'NEW_FRAME': <StageRenderingEventType.NEW_FRAME: 0>, 'HYDRA_ENGINE_FRAMES_COMPLETE': <StageRenderingEventType.HYDRA_ENGINE_FRAMES_COMPLETE: 1>, 'HYDRA_ENGINE_FRAMES_ADDED': <StageRenderingEventType.HYDRA_ENGINE_FRAMES_ADDED: 2>, 'RENDERER_RECORDING_COMPLETE': <StageRenderingEventType.RENDERER_RECORDING_COMPLETE: 3>, 'COUNT': <StageRenderingEventType.COUNT: 4>}
    pass
class StageState():
    """
            Stage states. The current stage state of the UsdContext.
            

    Members:

      CLOSED : Stage closed.

      CLOSING : Stage closing.

      OPENING : Stage opening.

      OPENED : Stage opened.
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    CLOSED: omni.usd._usd.StageState # value = <StageState.CLOSED: 0>
    CLOSING: omni.usd._usd.StageState # value = <StageState.CLOSING: 3>
    OPENED: omni.usd._usd.StageState # value = <StageState.OPENED: 2>
    OPENING: omni.usd._usd.StageState # value = <StageState.OPENING: 1>
    __members__: dict # value = {'CLOSED': <StageState.CLOSED: 0>, 'CLOSING': <StageState.CLOSING: 3>, 'OPENING': <StageState.OPENING: 1>, 'OPENED': <StageState.OPENED: 2>}
    pass
class UsdContext():
    """
    UsdContext is the container for a :cpp:class:`PXR_NS::UsdStage` that manages the lifecycle of a UsdStage instance.
    Because of historical reasons, UsdContext also undertakes extra responsibilities, including managing Hydra Engines selections, and etc.
    """
    def attach_stage_with_callback(self, stage_id: int, on_finish_fn: typing.Callable[[bool, str], None] = None) -> bool: 
        """
        Attaches an existing stage asynchronously.

        Args:
            stage_id (long int): The stage id that can be queried with pxr.UsdUtils.StageCache.Get().Find.
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
        """
    def can_close_stage(self) -> bool: 
        """
        Whether the current stage can be closed or not.
        """
    def can_open_stage(self) -> bool: 
        """
        Whether a new stage can be opened or not.
        """
    def can_save_stage(self) -> bool: 
        """
        Whether the current stage can be saved or not.
        """
    def close_stage(self, on_finish_fn: typing.Callable[[bool, str], None] = None) -> bool: 
        """
        Closes the current stage synchronously.

        Args:
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.

        Returns:
            Successful or not.
        """
    def close_stage_with_callback(self, on_finish_fn: typing.Callable[[bool, str], None]) -> bool: 
        """
        Closes the current stage asynchronously.

        Args:
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
        """
    def compute_path_world_bounding_box(self, arg0: str) -> typing.Tuple[carb._carb.Double3, carb._carb.Double3]: 
        """
        Compute world bound box for specified prim. Unlike using USD API directly, it speeds up bound box computation with cache or Fabric when it's enabled.
        """
    def compute_path_world_transform(self, arg0: str) -> typing.Annotated[typing.List[float], pybind11_stubgen.typing_ext.FixedSize(16)]: 
        """
        Compute world transform for specified prim. Unlike using USD API directly, it speeds up transform computation with cache.
        """
    def disable_save_to_recent_files(self) -> None: 
        """
        Disable save to recent files for opened stage url.
        """
    def enable_save_to_recent_files(self) -> None: 
        """
        Enable save to rencet files for opened stage url.
        """
    def export_as_stage(self, url: str, on_finish_fn: typing.Callable[[bool, str], None] = None) -> bool: 
        """
        Export stage with all prims flattened synchronously, and it will include contents from session layer also.

        Args:
            url (str): New location to save the exported stage.
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.

        Returns:
            Successful or not.
        """
    def export_as_stage_with_callback(self, url: str, on_finish_fn: typing.Callable[[bool, str], None]) -> bool: 
        """
        Export stage with all prims flattened asynchronously, and it will include contents from session layer also.

        Args:
            url (str): New location to save the exported stage.
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
        """
    def get_attached_hydra_engine_description(self, arg0: int) -> HydraEngineDesc: 
        """
        Gets attached hydra engine description based on unique id.
        """
    def get_attached_hydra_engine_names(self) -> typing.List[str]: 
        """
        Gets the attached hydra engine names to the UsdContext.
        """
    def get_attached_hydra_engine_uids(self) -> typing.List[int]: 
        """
        Gets all attached hydra engines unique ids.
        """
    def get_geometry_instance_path(self, arg0: int) -> str: 
        """
        Gets the geometry instance path with instance id.
        """
    def get_name(self) -> str: 
        """
        Gets the name of the context.
        """
    def get_rendering_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Gets the rendering event stream. See :class:`.StageRenderingEventType` for more details.
        """
    @staticmethod
    def get_selection(*args, **kwargs) -> typing.Any: 
        """
        Gets the selection interface. See :class:`.Selection` for more details.
        """
    def get_stage_audio_manager(self) -> AudioManager: 
        """
        Internal. Gets audio manager handle. See :class:`omni.usd.audio` for wrapped python interfaces that manage audio play/capture.
        """
    def get_stage_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Gets the stage event stream. See :class:`.StageEventType` for more details.
        """
    def get_stage_id(self) -> int: 
        """
        Gets the UsdStage Id that can be queried with Usd.StageCache.
        """
    def get_stage_loading_status(self) -> typing.Tuple[str, int, int]: 
        """
        Gets the stage loading status.

        Returns:
            (str, int, int): A tuple that the first element tells the current loading message, the second element tells how many files are loaded already, and the third one tells the total files to be loaded.
        """
    def get_stage_state(self) -> StageState: 
        """
        Gets the current stage state. See :class:`.StageState` for more details.
        """
    def get_stage_streaming_status(self) -> bool: 
        """
        Gets the status of all stage streaming systems.
        Returns:
            bool: whether any of the streaming systems is busy.
        """
    def get_stage_url(self) -> str: 
        """
        Gets the Stage url. The URL can be used as layer identifier to query layer handle from USD Layer Registry.
        """
    def get_timeline(self) -> omni.timeline._timeline.Timeline: 
        """
        Gets the timeline interface. See :mod:`omni.timeline` for more details.
        """
    def get_timeline_name(self) -> str: 
        """
        Gets current timeline used in this context.
        """
    def has_pending_edit(self) -> bool: 
        """
        Whether it has unsaved edits or not.
        """
    def is_new_stage(self) -> bool: 
        """
        Whether the current stage (root layer) is anonymous or not.
        """
    def is_omni_stage(self) -> bool: 
        """
        Whether the URL of the current stage (root layer) is prefixed with 'omniverse:'.
        """
    def is_writable(self) -> bool: 
        """
        Whether the current stage is writable or not
        """
    def load_render_settings_from_stage(self, arg0: int) -> None: 
        """
        Loads render settings from stage.
        """
    def manual_update(self, dt: float) -> bool: 
        """
        Explicitly update the UsdContext state.  This shoud only be run when auto-update is disabled (which is rare).

        Args:
            dt (float): The time that has elapsed since the last update call
        """
    def open_stage(self, url: str, on_finish_fn: typing.Callable[[bool, str], None] = None, load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool: 
        """
        Opens a stage synchronously.

        Args:
            url (str): The stage URL that can be resolved.
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
            load_set (omni.usd.UsdContextInitialLoadSet): Whether it should open stage with payloads loaded or not. By default, it loads all payloads.

        Returns:
            Successful or not.
        """
    def open_stage_with_callback(self, url: str, on_finish_fn: typing.Callable[[bool, str], None], load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool: 
        """
        Opens a stage asynchronously.

        Args:
            url (str): The stage URL that can be resolved.
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
            load_set (omni.usd.UsdContextInitialLoadSet): Whether it should open stage with payloads loaded or not. By default, it loads all payloads.
        """
    def open_stage_with_session_layer(self, url: str, session_layer_url: str, on_finish_fn: typing.Callable[[bool, str], None], load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool: 
        """
        Opens a stage asynchronously with specified session layer.

        Args:
            url (str): The stage URL that can be resolved.
            session_layer_url (str): The specified session layer URL.
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
            load_set (omni.usd.UsdContextInitialLoadSet): Whether it should open stage with payloads loaded or not. By default, it loads all payloads.
        """
    def register_selection_group(self) -> int: 
        """
        Registers a selection group. Prims can be assigned to selection group with customized outline colors than the default. It supports 255 selection groups at most.
        """
    def remove_all_hydra_engines(self) -> None: 
        """
        Detach all attached hydra engines from the UsdContext.
        """
    def reopen_stage(self, on_finish_fn: typing.Callable[[bool, str], None] = None, load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool: 
        """
        Re-opens the current stage synchronously.

        Args:
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
            load_set (omni.usd.UsdContextInitialLoadSet): Whether it should open stage with payloads loaded or not. By default, it loads all payloads.

        Returns:
            Successful or not.
        """
    def reopen_stage_with_callback(self, on_finish_fn: typing.Callable[[bool, str], None], load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool: 
        """
        Re-opens the current stage asynchronously.

        Args:
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
            load_set (omni.usd.UsdContextInitialLoadSet): Whether it should open stage with payloads loaded or not. By default, it loads all payloads.
        """
    def reset_renderer_accumulation(self) -> None: 
        """
        Resets all accumulation state inside renderers so that rendering n frames after this point is deterministic independent of prior frame-history.
        """
    def save_as_stage(self, url: str, on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None] = None) -> bool: 
        """
        Saves the current stage to another location synchronously.

        Args:
            url (str): New location to save the current stage.
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
        Returns:
            Successful or not.
        """
    def save_as_stage_with_callback(self, url: str, on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None]) -> bool: 
        """
        Saves the current stage to another location asynchronously.

        Args:
            url (str): New location to save the current stage.
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
        """
    def save_layers(self, new_root_layer_path: str, layer_identifiers: typing.List[str], on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None] = None) -> bool: 
        """
        Saves specified layers (only ones in the local layer stack) synchronously.

        Args:
            new_root_layer_path (str): New location for root layer if it's to save-as the current stage. If it's empty, it will save specified layers only.
            layer_identifiers (List[str]): List of layer identifiers to be saved.
            on_finish_fn (Callable[[bool, str, List[str]], None]): Finish callback that the first param is to tell if the operation is successful, the second one tells the error message if it's faled and
                the third param is the list of layer identifiers that are saved successfully.
        Returns:
            Successful or not.
        """
    def save_layers_with_callback(self, new_root_layer_path: str, layer_identifiers: typing.List[str], on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None]) -> bool: 
        """
        Saves specified layers (only ones in the local layer stack) asynchronously.

        Args:
            new_root_layer_path (str): New location for root layer if it's to save-as the current stage. If it's empty, it will save specified layers only.
            layer_identifiers (List[str]): List of layer identifiers to be saved.
            on_finish_fn (Callable[[bool, str, List[str]], None]): Finish callback that the first param is to tell if the operation is successful, the second one tells the error message if it's faled and
                the third param is the list of layer identifiers that are saved successfully.
        """
    def save_render_settings_to_current_stage(self) -> None: 
        """
        Saves render settings into the current stage. Render settings will be serialized into the custom layer data of root layer.
        """
    def save_stage(self, on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None] = None) -> bool: 
        """
        Saves the current stage (only layers in the local layer stack) synchronously.

        Args:
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.

        Returns:
            Successful or not.
        """
    def save_stage_with_callback(self, on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None]) -> bool: 
        """
        Saves the current stage asynchronously.

        Args:
            on_finish_fn (Callable[[bool, str], None]): Finish callback that the first param is to tell if the operation is successful, and the second one tells the error message if it's faled.
        """
    def set_pending_edit(self, arg0: bool) -> None: 
        """
        Set or clear the stage dirtiness state manually no matter if it has pending edits to save.
        """
    def set_pickable(self, arg0: str, arg1: bool) -> None: 
        """
        Sets the pickable state for a prim.
        """
    def set_selection_group(self, groupId: int, path: str) -> None: 
        """
        Assigns the prim to specified selection group.
        """
    def set_selection_group_outline_color(self, groupId: int, color: carb._carb.Float4) -> None: 
        """
        Sets the outline color of the selection group.
        """
    def set_selection_group_shade_color(self, groupId: int, color: carb._carb.Float4) -> None: 
        """
        Sets the shade color of the selection group.
        """
    def set_timeline(self, name: str = '') -> None: 
        """
        Sets the timeline for this context.
        """
    def stage_event_name(self, event: StageEventType) -> str: 
        """
        Returns the Stage Event name for a given StageEventType.
        """
    def stage_event_type(self, event: str) -> StageEventType: 
        """
        Returns the StageEventType from a Stage Event name.
        """
    def stage_rendering_event_name(self, event: StageRenderingEventType, immediate: bool = False) -> str: 
        """
        Returns the Stage Rendering Event name for a given StageRenderingEventType.
        """
    def stage_rendering_event_type(self, event: str) -> StageRenderingEventType: 
        """
        Returns the StageRenderingEventType from a Stage Event name.
        """
    def try_cancel_save(self) -> None: 
        """
        Try to cancel the saving process. It only take effects when it's called immediately after receiving event StageEventType::eSaving or StageEventType::eSettingsSaving.
        """
    def updated_hydra_engine_device_mask(self, arg0: int, arg1: int) -> bool: 
        """
        Update device mask for specific hydra engine on unique id.
        """
    pass
class UsdContextInitialLoadSet():
    """
            Specifies the initial set of prims to load when opening a UsdStage.
            

    Members:

      LOAD_ALL : Load all payloads

      LOAD_NONE : Unload all payloads
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    LOAD_ALL: omni.usd._usd.UsdContextInitialLoadSet # value = <UsdContextInitialLoadSet.LOAD_ALL: 0>
    LOAD_NONE: omni.usd._usd.UsdContextInitialLoadSet # value = <UsdContextInitialLoadSet.LOAD_NONE: 1>
    __members__: dict # value = {'LOAD_ALL': <UsdContextInitialLoadSet.LOAD_ALL: 0>, 'LOAD_NONE': <UsdContextInitialLoadSet.LOAD_NONE: 1>}
    pass
def add_hydra_engine(name: str, context: UsdContext) -> int:
    """
    Deprecated function. Do no use it - use create_hydra_engine instead
    """
def attach_all_hydra_engines(context: UsdContext) -> None:
    pass
def create_context(name: str = '') -> UsdContext:
    """
    Creates a new UsdContext.
    """
def create_hydra_engine(name: str, context: UsdContext) -> int:
    """
    Return created engine unique id value, will return HydraEngineInvalidUniqueId if creation failed.
    """
def create_hydra_engine_with_config(name: str, context: UsdContext, configuration: HydraEngineCreationConfig) -> int:
    """
    Return created engine unique id value, will return HydraEngineInvalidUniqueId if creation failed.
    """
def destroy_context(name: str = '') -> bool:
    """
    Destroys specified UsdContext.
    """
def destroy_hydra_engine(uid: int) -> bool:
    pass
def get_context(name: str = '') -> UsdContext:
    """
    Gets UsdContext instance.
    """
def get_context_from_stage_id(stage_id: int) -> UsdContext:
    """
    Finds UsdContext instance with specified stage id.
    """
def make_valid_identifier(*args, **kwargs) -> typing.Any:
    """
    Make a valid identifier from the provided string.
    """
def merge_layers(dst_layer_identifier: str, src_layer_identifier: str, dst_is_stronger_than_src: bool = True, src_layer_offset: float = 0.0, src_layer_scale: float = 1.0) -> bool:
    """
    Merge source layer into target layer according to the strength order.
    """
def merge_prim_spec(dst_layer_identifier: str, src_layer_identifier: str, prim_spec_path: str, dst_is_stronger_than_src: bool = True, target_prim_path: str = '') -> None:
    """
    Merge prim specs between layers.
    """
def release_all_hydra_engines(context: UsdContext = None) -> None:
    pass
def resolve_paths(src_layer_identifier: str, dst_layer_identifier: str, store_relative_path: bool = True, relative_to_src_layer: bool = False, copy_sublayer_offsets: bool = False) -> None:
    """
    Resolve external paths in dst layer against base layer specified by src_layer_identifier.
    """
def resolve_prim_path_references(layer: str, old_prim_path: str, new_prim_path: str) -> None:
    """
    Resolve all prim path reference to use new path.
    This is mainly used to remapping prim path reference after structure change of original prim.

    Args:
        layer (Sdf.Layer): Layer to resolve.
        old_prim_path (str): Old prim path.
        new_prim_path (str): New prim path that all old prim path references will be replaced to.
    """
def resolve_prim_paths_references(layer: str, old_prim_paths: typing.List[str], new_prim_paths: typing.List[str]) -> None:
    """
    Resolve all prim paths reference to use new path.
    This is mainly used to remapping prim path reference after structure change of original prim.

    Args:
        layer (Sdf.Layer): Layer to resolve.
        old_prim_paths (List[str]): Old prim paths.
            new_prim_paths (list[str]): New prim paths that all old prim paths references will be replaced to.
    """
def shutdown_usd() -> None:
    """
    Internal.
    """
def stage_event_type(event: str) -> StageEventType:
    """
    Converts a stage event name to a StageEventType
    """
def stage_rendering_event_type(event: str) -> StageRenderingEventType:
    """
    Converts a stage event name to a StageRenderingEventType
    """
HydraEngineInvalidUniqueId = 4294967295
MOTION_RAYTRACING_ENABLED: omni.usd._usd.EngineCreationFlags # value = <EngineCreationFlags.MOTION_RAYTRACING_ENABLED: 1>
NONE: omni.usd._usd.EngineCreationFlags # value = <EngineCreationFlags.NONE: 0>
SKIP_ON_WORKER_PROCESS: omni.usd._usd.EngineCreationFlags # value = <EngineCreationFlags.SKIP_ON_WORKER_PROCESS: 2>
WRITABLE_USD_FILE_EXTS_STR = 'usd|usda|usdc|live'
