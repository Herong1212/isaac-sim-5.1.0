import omni.usd
import omni.ui as ui
from typing import List
from pxr import Sdf

external_drag_drop = None


def setup_external_drag_drop(window_name :str, model: ui.AbstractItemModel):
    global external_drag_drop
    destroy_external_drag_drop()
    try:
        from omni.kit.window.drop_support import ExternalDragDrop
        external_drag_drop = ExternalDragDrop(window_name=window_name,
                                              drag_drop_fn=lambda e, p, m=model: _on_ext_drag_drop(e, p, m))
    except ModuleNotFoundError:
        pass


def destroy_external_drag_drop():
    global external_drag_drop
    if external_drag_drop:
        external_drag_drop.destroy()
        external_drag_drop = None


def _on_ext_drag_drop(edd, payload: List[str], model: ui.AbstractItemModel):
    target_item = model._root_layer
    for file_path in edd.expand_payload(payload):
        model.drop(target_item, file_path.replace("\\", "/"))
