"""MaterialListItem, MaterialListModel & MaterialListDelegate classes, used by MaterialListBoxWidget."""
__all__ = ['MaterialListItem', 'MaterialListModel', 'MaterialListDelegate']

import asyncio
import copy
import weakref
import omni.ui as ui
import omni.kit.material.library
from .material_utils import UpdateState

from pxr import Sdf
from .thumbnail_loader import ThumbnailLoader

class Constant:
    """Constant class, used by MaterialListModel & MaterialListDelegate."""
    def __setattr__(self, name, value):
        raise Exception(f"Can't change Constant.{name}") # pragma: no cover

    SDF_PATH_INVALID = "$NONE$"

    # verify SDF_PATH_INVALID is invalid
    if Sdf.Path.IsValidPathString(SDF_PATH_INVALID):
        raise Exception(f"SDF_PATH_INVALID is Sdf.Path.IsValidPathString - FIXME") # pragma: no cover

class MaterialListItem(ui.AbstractItem):
    """Single item model class, used by MaterialListModel."""
    def __init__(self, text):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
        # True when the item is visible
        self.filtered = True

    def prefilter(self, filter_name_text: str):
        if not filter_name_text:
            self.filtered = True
        else:
            self.filtered = filter_name_text in self.name_model.as_string.lower()

    def __repr__(self):
        return f'"{self.name_model.as_string}"'


class MaterialListModel(ui.AbstractItemModel):
    """List model class, used by MaterialListBoxWidget."""
    _instance = None

    def __init__(self, placeholder_fn=None, update_list_model_fn=None, filter_fn=None, get_materials_async_fn=None):
        super().__init__()
        self._placeholder_fn = placeholder_fn
        self._update_list_model_fn = update_list_model_fn
        self._children = [MaterialListItem(Constant.SDF_PATH_INVALID)]

        # call a local instance of MaterialUtils, otherwise call the singleton
        if get_materials_async_fn:
            get_materials_async_fn(MaterialListModel.update_children, wait_frames=2, ext_filter_func=filter_fn)
        else:
            omni.kit.material.library.get_materials_from_stage_async(MaterialListModel.update_children, wait_frames=2, ext_filter_func=filter_fn)
        global _instance
        _instance = self

    def clean(self):
        self._placeholder_fn = None
        self._update_list_model_fn = None
        global _instance
        _instance = None

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is not None:
            return []
        return [c for c in self._children if c.filtered]

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 1

    def get_drag_mime_data(self, item):
        """Returns Multipurpose Internet Mail Extensions (MIME) data for be able to drop this item somewhere"""
        # As we don't do Drag and Drop to the operating system, we return the string.
        return item.name_model.as_string

    def get_item_value_model(self, item, column_id):
        return item.name_model

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""
        for c in self._children:
            c.prefilter(filter_name_text.lower())
        self._item_changed(None)

    def execute(self, item):
        """ here we bind the material into the Scene"""
        material_path = item.name_model.as_string
        paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        if not paths:
            omni.usd.get_context().get_selection().set_selected_prim_paths([material_path], True)
        else:
            context = omni.usd.get_context()
            stage = context.get_stage() if context else None
            if not stage:
                return False
            with omni.kit.undo.group():
                for path in paths:
                    prim = stage.GetPrimAtPath(path)
                    if path and omni.usd.is_prim_material_supported(prim):
                        omni.kit.commands.execute(
                            "BindMaterial",
                            prim_path=path,
                            material_path=material_path,
                            strength=None,
                        )

    @staticmethod
    async def update_children(new_list: list, percent: int, state: UpdateState):
        if not _instance._placeholder_fn:
            return
        # NOTE: this must append to self._children
        if state == UpdateState.UPDATE:
            _instance._placeholder_fn(f"Loading {percent}%")
        elif state == UpdateState.COMPLETE_LIST:
            _instance._placeholder_fn("Search")
            new_list = sorted(new_list)
        elif state == UpdateState.UPDATE_COMPLETE:
            _instance._placeholder_fn("Search")
        for c in new_list:
            _instance._children.append(MaterialListItem(c))
        _instance._item_changed(None)
        if _instance._update_list_model_fn:
            await _instance._update_list_model_fn(new_list, percent, state)


class MaterialListDelegate(ui.AbstractItemDelegate):
    """
    Delegate is the representation layer. TreeView calls the methods
    of the delegate to create custom widgets for each item. Used by MaterialListBoxWidget.
    """
    def __init__(self, flat=False):
        super().__init__()
        self._thumbnail_loader = ThumbnailLoader()
        self._icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"
        self._icon_size = 32

    def _get_prim(self, prim_path):
        if prim_path:
            context = omni.usd.get_context()
            stage = context.get_stage() if context else None
            if stage:
                return stage.GetPrimAtPath(prim_path)
        return None

    def clean(self):
        pass

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        pass

    def build_widget(self, model, item, column_id, level, expanded):
        def on_drag(thumbnail_image: ui.Image, name, path):
            thumbnail = thumbnail_image.source_url
            with ui.VStack(width=64, height=64):
                if thumbnail:
                    ui.Image(thumbnail, width=64, height=64)
                ui.Label(name)
            return path

        value_model = model.get_item_value_model(item, column_id)
        material_path = value_model.as_string
        if material_path == Constant.SDF_PATH_INVALID:
            material_path = "None"

        with ui.HStack():
            # thumbnail
            with ui.ZStack(width=0):
                thumbnail_image = ui.Image(f"{self._icon_path}/material@3x.png",
                                            width=self._icon_size,
                                            height=self._icon_size,
                                            skip_draw_when_clipped=True)

                material_prim = self._get_prim(material_path)
                if material_prim:
                    self._thumbnail_loader.load(material_prim, thumbnail_image)

            # material name
            label = ui.Label(material_path, skip_draw_when_clipped=True, elided_text=True)

            # setup dragging... NOTE: image filename may change
            material_name = Sdf.Path(material_path).name
            if len(material_name) > 10:
                material_name = ".." + material_name[-10:]
            thumbnail_image.set_drag_fn(lambda i=thumbnail_image: on_drag(i, material_name, value_model.as_string))
