import omni.ui as ui
from typing import List
from pxr import Sdf

external_drag_drop = None


def setup_external_drag_drop(window_name :str, stage_widget):
    global external_drag_drop
    destroy_external_drag_drop()
    try:
        from omni.kit.window.drop_support import ExternalDragDrop
        external_drag_drop = ExternalDragDrop(window_name=window_name,
                                              drag_drop_fn=lambda e, p, m=stage_widget.get_model(): _on_ext_drag_drop(e, p, m))
    except ImportError:
        pass


def destroy_external_drag_drop():
    global external_drag_drop
    if external_drag_drop:
        external_drag_drop.destroy()
        external_drag_drop = None


def _on_ext_drag_drop(edd, payload: List[str], model: ui.AbstractItemModel):
    import omni.usd

    default_prim_path = Sdf.Path("/")
    stage = omni.usd.get_context().get_stage()
    if stage.HasDefaultPrim():
        default_prim_path = stage.GetDefaultPrim().GetPath()
    target_item = model.find(default_prim_path)

    for file_path in edd.expand_payload(payload):
        model.drop(target_item, file_path.replace("\\", "/"))
