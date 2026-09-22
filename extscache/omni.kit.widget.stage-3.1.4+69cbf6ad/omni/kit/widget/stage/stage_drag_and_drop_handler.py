__all__ = ["StageDragAndDropHandler", "AssetType"]

import os
import carb
import re
import omni.kit.commands
import omni.kit.notification_manager as nm
import carb.events
import omni.kit.app
import asyncio

from .drag_and_drop_registry import DragAndDropRegistry
from .stage_item import StageItem
from .stage_settings import StageSettings
from .utils import handle_exception
from pxr import Sdf, Tf, UsdGeom
from pathlib import Path
from omni.kit.async_engine import run_coroutine
from omni.usd import make_valid_identifier


ASSET_DRAG_GLOBAL_EVENT: str = "omni.kit.widget.stage.DRAG_ASSET"
ASSET_DRAG_EVENT: int = carb.events.type_from_string(ASSET_DRAG_GLOBAL_EVENT)
omni.kit.app.register_event_alias(ASSET_DRAG_EVENT, ASSET_DRAG_GLOBAL_EVENT)

KEEP_TRANSFORM_FOR_REPARENTING = "/persistent/app/stage/movePrimInPlace"
STAGE_DRAGDROP_IMPORT = "/persistent/app/stage/dragDropImport"


class AssetType:
    """A singleton that determines the type of asset using regex"""

    def __init__(self):
        self._re_mdl = re.compile(r"^.*\.mdl(\?.*)?(@.*)?$", re.IGNORECASE)
        self._re_audio = re.compile(r"^.*\.(wav|wave|ogg|oga|flac|fla|mp3|m4a|spx|opus)(\?.*)?$", re.IGNORECASE)
        self._re_material_in_mdl = re.compile(r"export\s+material\s+([^\s]+)\s*\(")
        self._read_material_tasks_or_futures = []

    def destroy(self):
        for task in self._read_material_tasks_or_futures:
            if not task.done():
                task.cancel()

        self._read_material_tasks_or_futures.clear()

    def is_usd(self, asset):
        return omni.usd.is_usd_readable_filetype(asset)

    def is_mdl(self, asset):
        return self._re_mdl.match(asset)

    def is_audio(self, asset):
        return self._re_audio.match(asset)

    def add_future(self, obj):
        """Add a future-like object to the global list, so it's not destroyed"""
        # Destroy the objects that are done or canceled
        self._read_material_tasks_or_futures = [
            task_or_future for task_or_future in self._read_material_tasks_or_futures if not task_or_future.done() and not task_or_future.cancelled()
        ]
        self._read_material_tasks_or_futures.append(run_coroutine(obj))

    async def get_first_material_name(self, mdl_file):
        """Parse the MDL asset and return the name of the first shader"""
        subid_list = await omni.kit.material.library.get_subidentifier_from_mdl(mdl_file, show_alert=True)
        if subid_list:
            return str(subid_list[0])
        return None


class StageDragAndDropHandler:

    def __init__(self, stage_model):
        self.__stage_model = stage_model
        self.__asset_type = AssetType()
        self.__reordering_prim = False
        self.__children_reorder_supported = False
        self.__drop_list = []
        self.__apply_task = None

    @property
    def children_reorder_supported(self):
        return self.__children_reorder_supported

    @children_reorder_supported.setter
    def children_reorder_supported(self, enabled):
        self.__children_reorder_supported = enabled

    @property
    def is_reordering_prim(self):
        return self.__reordering_prim

    @handle_exception
    async def __apply_mdl(self, mdl_name, target_path):
        """Import and apply MDL asset to the specified prim"""
        if mdl_name.startswith("material::"):
            mdl_name = mdl_name[10:]
        mtl_name = None
        encoded_subid = False
        # does the mdl name have the sub identifier encoded in it?
        if "@" in mdl_name:
            split = mdl_name.rfind("@")
            if split > 0 and mdl_name[split+1:].isidentifier():
                mtl_name = mdl_name[split+1:]
                mdl_name = mdl_name[:split]
                encoded_subid = True
        if not mtl_name:
            mtl_name = await self.__asset_type.get_first_material_name(mdl_name)
        if not mtl_name:
            carb.log_warn(f"[Stage Widget] the MDL Asset '{mdl_name}' doesn't have any material")
            return

        try:
            import omni.usd
            import omni.kit.material.library

            stage = self.__stage_model.stage
            subids = await omni.kit.material.library.get_subidentifier_from_mdl(mdl_name)
            if not encoded_subid and len(subids) > 1:
                # empty drops have target_path as /World - Fix
                root_path = Sdf.Path.absoluteRootPath.pathString
                if stage.HasDefaultPrim():
                    root_path = stage.GetDefaultPrim().GetPath().pathString

                omni.kit.material.library.custom_material_dialog(
                    mdl_path=mdl_name, bind_prim_paths=[target_path] if target_path != root_path else None
                )
                return
        except Exception as exc:
            carb.log_error(f"error {exc}")
            import traceback, sys
            traceback.print_exc(file=sys.stdout)
        except Exception:
            carb.log_warn(f"Failed to use omni.kit.material.library custom_material_dialog")

        # Create material with one sub-id
        with omni.kit.undo.group():
            # Create material. Despite the name, it only can bind to selection.
            mtl_created_list = []
            omni.kit.commands.execute(
                "CreateAndBindMdlMaterialFromLibrary",
                mdl_name=mdl_name,
                mtl_name=mtl_name,
                mtl_created_list=mtl_created_list,
                select_new_prim=False,
            )

            # Bind created material to the target prim
            # Special case: don't bind it to /World and to /World/Looks
            if target_path and target_path not in ["/World", "/World/Looks"]:
                omni.kit.commands.execute(
                    "BindMaterial", prim_path=target_path, material_path=mtl_created_list[0], strength=None
                )

    def drop_accepted(self, target_item, source, drop_location=-1):
        """Reimplemented from AbstractItemModel. Called to highlight target when drag and drop."""

        # Don't support drag and drop if the stage is not attached to any usd context.
        stage_model = self.__stage_model
        if not stage_model.usd_context:
            return False

        if source == target_item:
            return False

        # Skips it if reordering prims are not supported.
        if not self.__children_reorder_supported and drop_location != -1:
            return False

        if DragAndDropRegistry().drop_accepted(source):
            return True

        if isinstance(source, StageItem):
            # Drag and drop from inside the StageView
            if not target_item:
                target_item = stage_model.root

            if source.stage and source.stage == target_item.stage:
                # It cannot move from parent into child.
                # It stops if target_item already includes the source item.
                target_parent = target_item.path.GetParentPath() or target_item.path
                source_parent = source.path.GetParentPath() or source.path
                if (
                    target_item.path.HasPrefix(source.path) or
                    (source in target_item.children and drop_location == -1) or
                    (target_parent != source_parent and drop_location != -1)
                ):
                    return False
                else:
                    return True
            else:
                return not Sdf.Layer.IsAnonymousLayerIdentifier(source.root_identifier)

        if isinstance(source, str):
            def is_valid_url(source):
                for url in source.splitlines():
                    if url.startswith(("file:/", "material::")):
                        continue

                    if omni.client.is_valid_url(url):
                        continue

                    # must be a local filepath, use lstat to verify as it will throw an error in not valid
                    try:
                        os.lstat(url)
                    except OSError as exc:
                        return False

                return True

            # Drag and drop from the content browser. Verify its url as other DnD models also use strings
            return is_valid_url(source)

        try:
            from omni.kit.widget.filebrowser import FileSystemItem
            from omni.kit.widget.filebrowser import NucleusItem

            if isinstance(source, FileSystemItem) or isinstance(source, NucleusItem):
                # Drag and drop from the TreeView of Content Browser
                return True
        except Exception:
            pass

        try:
            from omni.kit.widget.versioning.checkpoints_model import CheckpointItem

            if isinstance(source, CheckpointItem):
                return True
        except Exception:
            pass

        return False

    def __drop_location_to_prim_index(self, prim_path, drop_location, new_item=False):
        """
        Gets the real prim index inside the children list of parent as drop location
        only shows the UI location while some of the children are possibly
        hidden in the stage window.
        """

        parent = prim_path.GetParentPath() or Sdf.Path.absoluteRootPath
        parent_item = self.__stage_model.find(parent)
        total_children = len(parent_item.children)
        # For new item, it needs to exclude current new item as the drop location is
        # got before this item is created.
        if new_item:
            total_children -= 1

        if drop_location >= total_children:
            drop_item_name = parent_item.children[-1].path.name
        else:
            drop_item_name = parent_item.children[drop_location].path.name

        parent_prim = parent_item.prim
        children_names = parent_prim.GetAllChildrenNames()
        if drop_item_name not in children_names:
            return None

        index = children_names.index(drop_item_name)
        if drop_location >= total_children:
            index += 1

        return index

    def __reorder_prim_to_drop_location(self, prim_path, drop_location, new_item):
        if not self.__children_reorder_supported:
            return

        stage_model = self.__stage_model
        stage = stage_model.stage
        if prim_path and stage.GetPrimAtPath(prim_path) and drop_location != -1:
            index = self.__drop_location_to_prim_index(prim_path, drop_location, new_item)
            if index is None:
                carb.log_error(f"Failed to re-order prim {prim_path} as it cannot be found in its parent.")
                return

            try:
                self.__reordering_prim = True
                success, _ = omni.kit.commands.execute(
                    "ReorderPrim", stage=stage, prim_path=prim_path, move_to_location=index
                )
            finally:
                self.__reordering_prim = False

            if success:
                parent_item = stage_model.find(prim_path.GetParentPath())
                if parent_item == stage_model.root:
                    parent_item = None
                stage_model._item_changed(parent_item)

    def drop(self, target_item, source, drop_location=-1):
        """
        Reimplemented from AbstractItemModel. Called when dropping something to the item.

        When drop_location is -1, it means to drop the source item on top of the target item.
        When drop_location is not -1, it means to drop the source item between items.
        """

        stage_model = self.__stage_model
        stage = stage_model.stage
        if not stage_model.root or not stage:
            return


        handled = DragAndDropRegistry().handle_drop_payload(source, target_item)
        if handled:
            return

        # Check type without importing if we have NucleusItem or FileSystemItem, we imported them in drop_accepted.
        if type(source).__name__ in ["NucleusItem", "FileSystemItem"]:
            # Drag and drop from the TreeView of Content Browser
            source = source._path

        # Check type without importing if we have CheckpointItem, we imported them in drop_accepted.
        if type(source).__name__ == "CheckpointItem":
            # Drag and drop from the TreeView of Content Browser
            source = source.get_full_url()

        self.__drop_list.append((target_item, source, drop_location))
        if not self.__apply_task or self.__apply_task.done():
            self.__apply_task = asyncio.ensure_future(self.__apply_drop_task(target_item._ui_widget if target_item and hasattr(target_item, "_ui_widget") else None))

    async def __apply_drop_task(self, target_widget):
        async def ask_user(move_pending_prims):
            import omni.ui as ui
            from omni.ui import color as cl
            from omni.ui import constant as fl

            async def set_parent_to(keep_transform, move_pending_prims):
                omni.kit.commands.execute(
                    "MovePrims",
                    paths_to_move=move_pending_prims,
                    keep_world_transform=keep_transform,
                    destructive=False
                )

            menu_style = {
                "Menu.Item": {
                    "color": cl.shade(cl("#D6D6D6")),
                    "margin_width": fl.shade(5),
                    "margin_height": fl.shade(3),
                },
                "MenuItem": {
                    "background_selected_color": cl.shade(cl("#34C7FF3B")),
                    "secondary_padding": 1,
                    "secondary_selected_color": cl.shade(cl("#34C7FF")),
                },
            }

            class ParentMenuDelegate(ui.MenuDelegate):
                def build_title(self, item: ui.Widget):
                    with ui.VStack():
                        with ui.ZStack():
                            ui.Rectangle(style={"background_color": 0xFF2A2825, "border_radius": 4.0})
                            with ui.HStack(height=32):
                                ui.Spacer(width=8)
                                with ui.HStack():
                                    ui.Label(
                                        item.text,
                                        style={"Label": {"color": 0xFFCCCCCC}, "Label:checked": {"color": 0xFFCCCCCC}},
                                        width=0,
                                    )

            self._set_parent_menu_delegate = ParentMenuDelegate()
            self._set_parent_menu = ui.Menu("Set Parent To", delegate=self._set_parent_menu_delegate, menu_compatibility=False, style=menu_style)
            with self._set_parent_menu:
                ui.MenuItem("Keep Prim Transform", delegate=self._set_parent_menu_delegate, menu_compatibility=False, triggered_fn=lambda: asyncio.ensure_future(set_parent_to(0, move_pending_prims)))
                ui.MenuItem("Inherit Parent Transform", delegate=self._set_parent_menu_delegate, menu_compatibility=False, triggered_fn=lambda: asyncio.ensure_future(set_parent_to(1, move_pending_prims)))
            self._set_parent_menu.show()

        move_pending_prims = {}
        while self.__drop_list:
            target_item, source, drop_location = self.__drop_list.pop(0)
            move_path_dict = await self.__apply_drop(target_item, source, drop_location)
            if move_path_dict:
                move_pending_prims.update(move_path_dict)
        if len(move_pending_prims):
            settings = carb.settings.get_settings()
            keep_transform = settings.get(KEEP_TRANSFORM_FOR_REPARENTING)
            if keep_transform is None:
                keep_transform = 1
            match keep_transform:
                case 0 | 1:
                    omni.kit.commands.execute(
                        "MovePrims",
                        paths_to_move=move_pending_prims,
                        keep_world_transform=keep_transform,
                        destructive=False
                    )
                case 2:
                    asyncio.ensure_future(ask_user(move_pending_prims))

    async def __apply_drop(self, target_item, source, drop_location):
        stage_model = self.__stage_model
        stage = stage_model.stage
        if not stage_model.root or not stage:
            return
        with omni.kit.undo.group():
            import_method = carb.settings.get_settings().get(STAGE_DRAGDROP_IMPORT) or "payload"
            new_prim_path = None
            new_item_added = False
            if isinstance(source, StageItem):
                if not target_item:
                    target_item = stage_model.root

                if source.root_identifier == target_item.root_identifier:
                    # Drop the source item as a child item of target.
                    if drop_location == -1:
                        new_path = target_item.path.AppendChild(source.path.name)
                        return {str(source.path): str(new_path)}
                    else:
                        # It's to drag and drop to re-order the children.
                        new_prim_path = source.path
                else:
                    # Drag and drop from external stage
                    new_item_added = True
                    if import_method.lower() == "reference":
                        _, new_prim_path = omni.kit.commands.execute(
                            "CreateReference",
                            path_to=target_item.path.AppendChild(source.path.name),
                            asset_path=source.root_identifier,
                            prim_path=source.path,
                            usd_context=stage_model.usd_context
                        )
                    else:
                        _, new_prim_path = omni.kit.commands.execute(
                            "CreatePayload",
                            path_to=target_item.path.AppendChild(source.path.name),
                            asset_path=source.root_identifier,
                            prim_path=source.path,
                            usd_context=stage_model.usd_context
                        )

            elif isinstance(source, str):
                defaultedToDefaultPrim = False
                omni.kit.app.queue_event(ASSET_DRAG_GLOBAL_EVENT, {"url": source})
                for i in range(4):
                    await omni.kit.app.get_app().next_update_async()
                # Don't drop it to default prim when it's to drop with location.
                if not target_item and stage.HasDefaultPrim() and drop_location == -1:
                    default_prim = stage.GetDefaultPrim()
                    default_prim_path = default_prim.GetPath()
                    if (
                        not default_prim.IsA(UsdGeom.Gprim)
                        and not omni.usd.is_ancestor_prim_type(stage, default_prim_path, UsdGeom.Gprim)
                    ):
                        target_item = stage_model.find(default_prim_path)
                        defaultedToDefaultPrim = True

                if not target_item:
                    target_item = stage_model.root
                    defaultedToDefaultPrim = True

                # Drag and drop from the content browser
                for source_url in source.splitlines():
                    if source_url.endswith(".sbsar"):
                        new_item_added = True
                        if "AddSbsarReferenceAndBind" in omni.kit.commands.get_commands():
                            # mimic viewport drag & drop behaviour and not assign material to
                            # /World if we defaulted to it in the code above
                            targetPrimPath = target_item.path if not defaultedToDefaultPrim else None
                            success, sbar_mat_prim = omni.kit.commands.execute(
                                "AddSbsarReferenceAndBind", sbsar_path=source_url, target_prim_path=targetPrimPath
                            )
                            if success and sbar_mat_prim:
                                omni.usd.get_context().get_selection().set_selected_prim_paths([sbar_mat_prim], True)
                                new_prim_path = sbar_mat_prim.GetPath()
                        else:
                            nm.post_notification(
                                "To drag&drop sbsar files please enable the omni.kit.property.sbsar extension first.",
                                status=nm.NotificationStatus.WARNING
                            )
                    elif source_url.startswith("flow::"):
                        # mimic viewport drag & drop behaviour
                        (name, preset_url) = source_url[len("flow::"):].split("::")
                        omni.kit.commands.execute(
                            "FlowCreatePresetsCommand",
                            preset_name=name,
                            url=preset_url,
                            paths=[str(target_item.path)],
                            layer=-1)
                    elif omni.usd.is_usd_readable_filetype(source_url):
                        new_item_added = True
                        stem = Path(source_url).stem
                        # It drops as child.
                        if drop_location == -1:
                            path = target_item.path.AppendChild(make_valid_identifier(stem))
                        else:
                            # It drops between items.
                            path = target_item.path.GetParentPath()
                            if not path:
                                path = Sdf.Path.absoluteRootPath
                            path = path.AppendChild(make_valid_identifier(stem))

                        if import_method == "reference":
                            success, new_prim_path = omni.kit.commands.execute(
                                "CreateReference", path_to=path, asset_path=source_url, usd_context=stage_model.usd_context
                            )
                        else:
                            success, new_prim_path = omni.kit.commands.execute(
                                "CreatePayload", path_to=path, asset_path=source_url, usd_context=stage_model.usd_context
                            )

                    elif self.__asset_type.is_mdl(source_url):
                        self.__asset_type.add_future(self.__apply_mdl(source_url, target_item.path))
                    elif self.__asset_type.is_audio(source_url):
                        new_item_added = True
                        stem = Path(source_url).stem
                        path = target_item.path.AppendChild(make_valid_identifier(stem))
                        _, new_prim_path = omni.kit.commands.execute(
                            "CreateAudioPrimFromAssetPath",
                            path_to=path,
                            asset_path=source_url,
                            usd_context=stage_model.usd_context
                        )

            if new_prim_path:
                self.__reorder_prim_to_drop_location(new_prim_path, drop_location, new_item_added)
