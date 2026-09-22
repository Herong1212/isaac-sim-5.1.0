"""Material library MaterialUtils class. Provides upto date cache of known materials in stage."""
__all__ = ['UpdateState', 'MaterialUtils', 'initalize_material_utils', 'destroy_material_utils', 'add_cache_changed_fn', 'remove_cache_changed_fn', 'get_materials_from_stage', 'get_materials_from_stage_async', 'add_materials_from_stage_filter_func', 'remove_materials_from_stage_filter_func', 'get_prim_children_paths']

import asyncio
import carb
import omni.usd
import weakref
from enum import Enum
from pxr import Usd, Tf, Sdf, UsdShade
from omni.usd import PrimCaching


g_singleton = None

class UpdateState(Enum):
    """State of cache of known materials in stage, passed to update_func."""
    UPDATE = 1
    """Cache is updating & partial list of materials is passed."""
    UPDATE_COMPLETE = 2
    """Cache has finished updating & partial list of materials is passed.."""
    COMPLETE_LIST = 3
    """Cache has finished updating & complete list of materials is passed."""


class MaterialUtils:
    """Material library MaterialUtils class. Provides upto date cache of known materials in stage."""
    def __init__(self, usd_context_name: [str|None] = None):
        # TODO: Check g_singleton is None, and if not performance warning on extra UsdNotice handlers being installed 
        self._usd_material_cache = None
        self._on_prim_cache_changed = []
        self._prim_caching = PrimCaching(UsdShade.Material, on_changed=self._on_prim_cache_changed_func, usd_context_name=usd_context_name)
        self._stop_event = asyncio.Event()
        self._full_list_event = asyncio.Event()
        self._async_task_get_materials_from_stage = None
        self._materials_from_stage_filter_funcs = []

    @staticmethod
    def is_valid_material(prim, filter_funcs, ext_filter_func=None):
        """
        Is prim a valid material.

        Args:
            filter_funcs (list): List of additional functions to validate material prim.
            ext_filter_func (callable): Additional function to validate material prim.
        Returns:
            (bool): True if valid material otherwise False.
        """
        if (not prim.IsA(UsdShade.Material) or
            prim.GetMetadata("hide_in_stage_window") or
            prim.IsHidden() or
            prim.GetMetadata("ignore_material_updates")):
            return False
        try:
            for filter_fn in filter_funcs:
                if not filter_fn(prim):
                    return False
            if ext_filter_func:
                if not ext_filter_func(prim):
                    return False
        except Exception as exc:                                                            # pragma: no cover
            carb.log_error(f"is_valid_material error {filter_func}, {ext_filter_func} {exc}") # pragma: no cover
        return True

    def stop(self):
        """Stop traversing the stage"""
        if self._stop_event:
            self._stop_event.set()

    def add_cache_changed_fn(self, cache_changed_fn: callable):
        """
        Adds callback to material cache changed list.

        Args:
            cache_changed_fn (callable): Callback.
        """
        if cache_changed_fn:
            self._on_prim_cache_changed.append(cache_changed_fn)

    def remove_cache_changed_fn(self, cache_changed_fn: callable):
        """
        Remove callback to material cache changed list.

        Args:
            cache_changed_fn (callable): Callback.
        """
        if cache_changed_fn:
            self._on_prim_cache_changed.remove(cache_changed_fn)

    def destroy(self):
        """
        Destroy class and cleanup.
        """
        self.stop()
        self._materials_from_stage_filter_funcs = None
        self._usd_material_cache = None
        self._on_prim_cache_changed = None
        if self._prim_caching:
            self._prim_caching.destroy()
            self._prim_caching = None

    def _on_prim_cache_changed_func(self):
        for changed in self._on_prim_cache_changed:
            changed()

    def flush_material_cache(self):
        """Clear material cache."""
        self._usd_material_cache = None

    def get_materials_from_stage(self, ext_filter_func=None):
        """
        Get list of materials for stage. NOTE: This function can block on large stages.

        Args:
            ext_filter_func (callable): filter function to remove material names from list. Optional.
        Returns:
            (list): list of materials names
        """
        stage = self._prim_caching._stage
        if not stage or not stage():
            carb.log_warn(f"get_materials_from_stage error stage isn't initialized")
            return []
        stage = stage()
        material_list = self._usd_material_cache
        if material_list is None or self._prim_caching.get_cache_state() == False:
            material_list = set()
            # OM-25609 Make sure we detect abstract materials (inside of class prim hierarchies)
            for p in stage.Traverse(Usd.TraverseInstanceProxies(Usd.PrimIsActive and Usd.PrimIsDefined and Usd.PrimIsLoaded)):
                if MaterialUtils.is_valid_material(p, self._materials_from_stage_filter_funcs, ext_filter_func):
                    material_list.add(p.GetPath().pathString)
            self._usd_material_cache = material_list
            self._prim_caching.set_cache_state(True)
        return sorted(list(material_list))

    def get_materials_from_stage_async(self, update_func: callable, wait_frames: int, ext_filter_func: callable):
        """
        Get list of materials for stage asynchronously.

        Args:
            update_func (callable): function to call when new material names are available.
            wait_frames (int): number of frames to wait before starting to get materials list.
            ext_filter_func (callable): filter function to remove material names from list. Optional.
        """
        stage = self._prim_caching._stage
        if not stage or not stage():
            carb.log_warn(f"get_materials_from_stage error stage isn't initialized")
            return

        material_list = self._usd_material_cache
        if material_list is None or self._prim_caching.get_cache_state() == False:
            if self._async_task_get_materials_from_stage and not self._async_task_get_materials_from_stage.done():
                self._full_list_event.set()
            else:
                self._async_task_get_materials_from_stage = asyncio.ensure_future(self.__get_materials_from_stage_async(stage(), self._stop_event, self._full_list_event, update_func, wait_frames, ext_filter_func))
            return

        async def use_cached():
            for f in range(wait_frames):
                await omni.kit.app.get_app().next_update_async()
            await update_func(material_list, 100, UpdateState.COMPLETE_LIST)

        asyncio.ensure_future(use_cached())

    def add_materials_from_stage_filter_func(self, filter_fn: callable):
        """
        Add filter callback function to get_materials_from_stage_async() callback.

        Args:
            filter_fn (callable): Filter function.
        """
        if filter_fn:
            self._materials_from_stage_filter_funcs.append(filter_fn)

    def remove_materials_from_stage_filter_func(self, filter_fn: callable):
        """
        Remove filter callback function from get_materials_from_stage_async() callback.

        Args:
            filter_fn (callable): Filter function.
        """
        if filter_fn:
            self._materials_from_stage_filter_funcs.remove(filter_fn)

    async def __get_materials_from_stage_async(self, stage: Usd.Stage, stop_event: asyncio.Event, full_list_event: asyncio.Event, update_func: callable, wait_frames: int, ext_filter_func: callable):
        import time

        stop_event.clear()
        full_list_event.clear()

        # Wait n frame to let other tasks go
        for _ in range(wait_frames):
            await omni.kit.app.get_app().next_update_async()
        start_time = time.monotonic()

        # The widget will be updated not faster than xx times a second
        update_every = (1.0 / 60.0) * 10

        materials = set()
        material_list = set()

        prim_total = 0
        for p in stage.Traverse(
            Usd.TraverseInstanceProxies(Usd.PrimIsActive and Usd.PrimIsDefined and Usd.PrimIsLoaded)
        ):
            prim_total += 1

        prim_count = 0
        sent_update = False
        for p in stage.Traverse(
            Usd.TraverseInstanceProxies(Usd.PrimIsActive and Usd.PrimIsDefined and Usd.PrimIsLoaded)
        ):
            prim_count += 1
            if stop_event.is_set():
                return

            if MaterialUtils.is_valid_material(p, self._materials_from_stage_filter_funcs, ext_filter_func):
                materials.add(p.GetPath().pathString)

            elapsed_time = time.monotonic()

            # Loop some amount of time so fps will be about 60FPS
            if elapsed_time - start_time > update_every:
                if materials:
                    percent = int((prim_count / prim_total) * 100)
                    material_list.update(materials)

                    sent_update = True
                    if full_list_event.is_set():
                        await update_func(material_list, percent, UpdateState.UPDATE)
                        full_list_event.clear()
                    else:
                        await update_func(materials, percent, UpdateState.UPDATE)

                    materials = set()

                # Wait one frame to let other tasks go
                await omni.kit.app.get_app().next_update_async()
                start_time = time.monotonic()

        material_list.update(materials)
        self._usd_material_cache = material_list
        self._prim_caching.set_cache_state(True)
        self._async_task_get_materials_from_stage = None

        if sent_update:
            await update_func(materials, 100, UpdateState.UPDATE_COMPLETE)
        else:
            await update_func(material_list, 100, UpdateState.COMPLETE_LIST)
        full_list_event.clear()


def initalize_material_utils():
    """Initialize material_utils. This should only be called from omni.kit.material.library on_startup."""
    global g_singleton
    if g_singleton == None:
        g_singleton = MaterialUtils()


def destroy_material_utils():
    """Destroy material_utils. This should only be called from omni.kit.material.library on_shutdown."""
    global g_singleton
    if g_singleton:
        g_singleton.destroy()
        g_singleton = None


def add_cache_changed_fn(cache_changed_fn: callable):
    """
    Adds callback to material cache changed list.

    Args:
        cache_changed_fn (callable): Callback.
    """
    if g_singleton:
        g_singleton.add_cache_changed_fn(cache_changed_fn)


def remove_cache_changed_fn(cache_changed_fn: callable):
    """
    Remove callback to material cache changed list.

    Args:
        cache_changed_fn (callable): Callback.
    """
    if g_singleton:
        g_singleton.remove_cache_changed_fn(cache_changed_fn)


def get_materials_from_stage(none_string: str):
    """
    Get list of materials for stage. NOTE: This function can block on large stages.

    Args:
        none_string (str): name of "None" material to be added to list
    Returns:
        (list): list of materials names
    """
    if g_singleton:
        material_list = g_singleton.get_materials_from_stage()
        if none_string:
            return [none_string] + material_list
        return material_list
    return []


def get_materials_from_stage_async(update_func: callable, wait_frames: int=1, ext_filter_func: callable=None):
    """
    Get list of materials for stage asynchronously.

    Args:
        update_func (callable): function to call when new material names are available.
        wait_frames (int): number of frames to wait before starting to get materials list.
        ext_filter_func (callable): filter function to remove material names from list. Optional.
    """
    if g_singleton:
        return g_singleton.get_materials_from_stage_async(update_func, wait_frames, ext_filter_func)
    return None


def add_materials_from_stage_filter_func(filter_fn: callable):
    """
    Add filter callback function to get_materials_from_stage_async() callback.

    Args:
        filter_fn (callable): Filter function.
    """
    if g_singleton:
        g_singleton.add_materials_from_stage_filter_func(filter_fn)


def remove_materials_from_stage_filter_func(filter_fn: callable):
    """
    Remove filter callback function from get_materials_from_stage_async() callback.

    Args:
        filter_fn (callable): Filter function.
    """
    if g_singleton:
        g_singleton.remove_materials_from_stage_filter_func(filter_fn)


def get_prim_children_paths(prim_path: Sdf.Path):
    """
    Get all child prims from prim_path.

    Args:
        prim_path (str): prim path.
    Returns:
        (list): list of child prims
    """
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    children = prim.GetFilteredChildren(Usd.PrimAllPrimsPredicate)

    children_all = []
    for child in children:
        if child.GetFilteredChildren(Usd.PrimAllPrimsPredicate):
            children_all = children_all + get_prim_children_paths(child.GetPath().pathString)
        children_all.append(child.GetPath().pathString)

    return children_all
