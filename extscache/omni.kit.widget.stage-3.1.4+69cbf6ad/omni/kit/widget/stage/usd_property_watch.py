# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from .stage_helper import UsdStageHelper
from pxr import Sdf
from pxr import Tf
from pxr import Trace
from pxr import Usd
from typing import Any
from typing import Dict
from typing import List
from typing import Optional, Union
from typing import Type
import asyncio
import carb
import functools
import omni.kit.app
from omni.kit.async_engine import run_coroutine
import omni.kit.commands
import omni.ui as ui
import traceback
import concurrent.futures


def handle_exception(func):  # pragma: no cover
    """
    Decorator to print exception in async functions
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


class UsdPropertyWatchModel(ui.AbstractValueModel, UsdStageHelper):  # pragma: no cover
    """
    DEPRECATED: A helper model of UsdPropertyWatch that behaves like a model that watches
    a USD property. It doesn't work properly if UsdPropertyWatch does not
    create it.
    """

    def __init__(self, stage: Usd.Stage, path: Sdf.Path):
        """
        ## Arguments:
            `stage`: USD Stage
            `path`: The full path to the watched property
        """
        ui.AbstractValueModel.__init__(self)
        UsdStageHelper.__init__(self, stage)

        if stage:
            prop = stage.GetObjectAtPath(path)
        else:
            prop = None

        if prop:
            self._path = path
            self._type = prop.GetTypeName().type
        else:
            self._path = None
            self._type = None

    def destroy(self):
        """Called before destroying"""
        pass

    def _get_prop(self):
        """Get the property this model holds"""
        if not self._path:
            return

        stage = self._get_stage()
        if not stage:
            return

        return stage.GetObjectAtPath(self._path)

    def on_usd_changed(self):
        """Called by the stage model when the visibility is changed"""
        self._value_changed()

    def get_value_as_bool(self) -> Optional[bool]:
        """Reimplemented get bool"""
        prop = self._get_prop()
        if not prop:
            return

        return not not prop.Get()

    def get_value_as_float(self) -> Optional[float]:
        """Reimplemented get bool"""
        prop = self._get_prop()
        if not prop:
            return

        return float(prop.Get())

    def get_value_as_int(self) -> Optional[int]:
        """Reimplemented get bool"""
        prop = self._get_prop()
        if not prop:
            return

        return int(prop.Get())

    def get_value_as_string(self) -> Optional[str]:
        """Reimplemented get bool"""
        prop = self._get_prop()
        if not prop:
            return

        return str(prop.Get())

    def set_value(self, value: Any):
        """Reimplemented set bool"""
        prop = self._get_prop()
        if not prop:
            return

        omni.kit.commands.execute("ChangeProperty", prop_path=self._path, value=value)


class UsdPropertyWatch(UsdStageHelper):  # pragma: no cover
    """
    DEPRECATED: The purpose of this class is to keep a large number of models.
    `Usd.Notice.ObjectsChanged` is pretty slow, and to remain fast, we need
    to register as few `Tf.Notice` as possible. Thus, we can't put the
    `Tf.Notice` logic to the model. Instead, this class creates and
    coordinates the models.
    """

    def __init__(
        self,
        stage: Usd.Stage,
        property_name: str,
        model_type: Type[UsdPropertyWatchModel] = UsdPropertyWatchModel,
    ):
        """
        ## Arguments:
            `stage`: USD Stage
            `property_name`: The name of the property to watch
            `model_type`: The name of the property to watch
        """
        UsdStageHelper.__init__(self, stage)

        self.__prim_changed_task_or_future: Union[asyncio.Task, concurrent.futures.Future, None] = None
        self.__dirty_property_paths: List[Sdf.Path] = []
        self.__watch_property: str = property_name
        self.__model_type: Type[UsdPropertyWatchModel] = model_type
        self.__stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, stage)
        self.__models: Dict[str, UsdPropertyWatchModel] = {}

    def destroy(self):
        """Called before destroying"""
        self.__stage_listener = None

        for _, model in self.__models.items():
            model.destroy()
        self.__models = {}

        if self.__prim_changed_task_or_future is not None:
            self.__prim_changed_task_or_future.cancel()
            self.__prim_changed_task_or_future = None

    @Trace.TraceFunction
    def _on_objects_changed(self, notice, sender):
        """Called by Tf.Notice"""
        # We only watch the property self.__watch_property
        prims_resynced = [
            p for p in notice.GetChangedInfoOnlyPaths() if p.IsPropertyPath() and p.name == self.__watch_property
        ]

        if prims_resynced:
            # It's important to return as soon as possible, because
            # Usd.Notice.ObjectsChanged can be called thousands times a frame.
            # We collect the paths change and will work with them the next
            # frame at once.
            self.__dirty_property_paths += prims_resynced

            if self.__prim_changed_task_or_future is None or self.__prim_changed_task_or_future.done():
                self.__prim_changed_task_or_future = run_coroutine(self.__delayed_prim_changed())

        # TODO: Do something when the watched object is removed

    @handle_exception
    @Trace.TraceFunction
    async def __delayed_prim_changed(self):
        """Called in the next frame when the object is changed"""
        await omni.kit.app.get_app().next_update_async()

        # Pump the changes to the model.
        self.update_dirty()

        self.__prim_changed_task_or_future = None

    def update_dirty(self):
        """
        Create/remove dirty items that was collected from TfNotice. Can be
        called any time to pump changes.
        """
        dirty_property_paths = set(self.__dirty_property_paths)
        self.__dirty_property_paths = []

        dirty_prim_paths = [p.GetParentPath() for p in dirty_property_paths]

        for path in dirty_prim_paths:
            model = self.__models.get(path, None)
            if model is None:
                continue
            model.on_usd_changed()

    def _create_model(self, path: Sdf.Path):
        """Creates a new model and puts in to the cache"""
        model = self.__model_type(self._get_stage(), path.AppendProperty(self.__watch_property))

        self.__models[path] = model
        return model

    def get_model(self, path):
        model = self.__models.get(path, None)
        if model is None:
            model = self._create_model(path)
        return model
