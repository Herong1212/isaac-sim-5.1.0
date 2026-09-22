import omni
import omni.client
import omni.usd
import weakref
import os
import carb
import omni.kit.notification_manager as nm
import omni.client

from omni.kit.async_engine import run_coroutine
from .layer_settings import LayerSettings
from typing import List
from pxr import Sdf
from omni.kit.usd.layers import LayerUtils
from omni.kit.widget.prompt import PromptButtonInfo, PromptManager
from omni.kit.window.file_importer import get_file_importer
from omni.kit.window.file_exporter import get_file_exporter


def _show_confirm_layer_insert_prompt(layer_identifier, confirm_fn):
    PromptManager.post_simple_prompt(
        "Insert Layer",
        f"Do you want to insert {os.path.basename(layer_identifier)} into stage?",
        PromptButtonInfo("Yes", confirm_fn),
        PromptButtonInfo("No")
    )


def _show_outdated_layer_prompt(layer_identifier, confirm_fn, middle_fn, middle_2_fn, cancel_fn):
    if middle_2_fn:
        middle_2_button = PromptButtonInfo("Fetch Latest", middle_2_fn)
    else:
        middle_2_button = None

    PromptManager.post_simple_prompt(
        f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Merge Conflict',
        f"({os.path.basename(layer_identifier)}) has been updated on disk.",
        ok_button_info=PromptButtonInfo("Save", confirm_fn),
        cancel_button_info=PromptButtonInfo("Cancel", confirm_fn),
        middle_button_info=PromptButtonInfo("Save As", middle_fn),
        middle_2_button_info=middle_2_button,
        modal=True
    )


def _show_outdated_layers_prompt(outdated_layers, confirm_fn, middle_fn, cancel_fn):
    global _layers_are_outdated_prompt
    if not outdated_layers:
        if confirm_fn:
            confirm_fn()
        return

    if middle_fn:
        middle_button = PromptButtonInfo("Fetch Latest", middle_fn)
    else:
        middle_button = None

    message = os.path.basename(outdated_layers[0])
    for i in range(1, len(outdated_layers)):
        message += f", {os.path.basename(outdated_layers[i])}"

    PromptManager.post_simple_prompt(
        f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Merge Conflict',
        f"Layers ({message}) have been updated on disk.",
        ok_button_info=PromptButtonInfo("Save", confirm_fn),
        cancel_button_info=PromptButtonInfo("Cancel"),
        middle_button_info=middle_button,
        modal=True
    )


def _show_transfer_root_content_prompt(confirm_fn, cancel_fn):
    PromptManager.post_simple_prompt(
        "Transfer Content",
        "Root Layer is not empty. Transfer Root Layer contents to the new sublayer?",
        ok_button_info=PromptButtonInfo("Yes", confirm_fn),
        cancel_button_info=PromptButtonInfo("No", cancel_fn),
    )


def _show_save_file_picker(title: str, file_handler, default_location=None, default_filename=None):
    def on_export(filename: str, dirname: str, extension: str = '', selections: List[str] = []):
        if dirname and dirname[-1] != "/":
            dirname += "/"

        path = omni.client.make_absolute_url_if_possible(dirname, filename + extension)

        async def on_file_selected():
            result, _ = await omni.client.stat_async(path)
            overwrite = result == omni.client.Result.OK
            if overwrite:
                PromptManager.post_simple_prompt(
                    f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Overwrite',
                    f"File {os.path.basename(path)} already exists, do you want to overwrite it?",
                    ok_button_info=PromptButtonInfo("YES", lambda: file_handler([path], True)),
                    cancel_button_info=PromptButtonInfo("No")
                )
            else:
                file_handler([path], overwrite)

        run_coroutine(on_file_selected())

    file_picker = get_file_exporter()
    file_picker.show_window(
        title=title,
        export_button_label="Save",
        export_handler=on_export,
        file_extension_types=[
            (".usd", "USD File (*.usd)"),
            (".usda", "USDA File (*.usda)"),
            (".usdc", "USDC File (*.usdc)"),
            (".live", "Live File (*.live)"),
        ]
    )


def _show_save_error_prompt(layer_identifier):
    PromptManager.post_simple_prompt(
        f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Save Failed',
        f"Failed to save layer {os.path.basename(layer_identifier)}."
    )


def _show_remove_dirty_layer_prompt(layer_identifier, dirty, confirm_fn, multiple=False):
    layer_name = os.path.basename(layer_identifier)
    if dirty:
        if multiple:
            message = "Several layers have unsaved changes. Do you want to remove them from stage?"
        else:
            message = f"Layer {layer_name} has unsaved changes. Do you want to remove this layer from stage?"
    else:
        if multiple:
            message = "Several layers are not empty. Do you want to remove them from stage?"
        else:
            message = f"Layer {layer_name} content is not empty. Do you want to remove this layer from stage?"

    PromptManager.post_simple_prompt(
        f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Removing Layer',
        message,
        ok_button_info=PromptButtonInfo("Yes", confirm_fn),
        cancel_button_info=PromptButtonInfo("No")
    )


def _show_reload_dirty_layer_prompt(layer_identifier, confirm_fn):
    layer_name = os.path.basename(layer_identifier)
    PromptManager.post_simple_prompt(
        f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Reload Layer',
        f"Layer {layer_name} has unsaved changes. Do you want to reload this layer?",
        ok_button_info=PromptButtonInfo("Yes", confirm_fn),
        cancel_button_info=PromptButtonInfo("No")
    )


def _show_file_insert_picker(title: str, file_handler, default_location=None, default_filename=None):
    filter_string = ", ".join(omni.usd.readable_usd_dotted_file_exts())
    filter_options = [
        (filter_string, omni.usd.readable_usd_files_desc()),
        ("*.*", "All Files (*.*)"),
    ]

    def on_import(filename, dirname, selections):
        if dirname and dirname[-1] != "/":
            dirname += "/"

        async def on_file_selected(filename, dirname, selections):
            all_paths = []
            if not selections:
                path = omni.client.make_absolute_url_if_possible(dirname, filename)
                selections = [path]

            for selection in selections:
                path = omni.client.make_absolute_url_if_possible(dirname, selection)
                all_paths.append(path)

            if file_handler:
                file_handler(all_paths)

        run_coroutine(on_file_selected(filename, dirname, selections))

    file_picker = get_file_importer()
    file_picker.show_window(
        title=title,
        import_button_label="Open",
        import_handler=on_import,
        file_extension_types=filter_options,
        allow_multi_files_selection=True
    )


def _show_move_prim_spec_warning_prompt(layer_identifier, confirm_fn):
    layer_name = os.path.basename(layer_identifier)
    PromptManager.post_simple_prompt(
        f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Merge Prim Spec',
        f"Do you want to merge this prim spec to layer {layer_name}?",
        ok_button_info=PromptButtonInfo("Yes", confirm_fn),
        cancel_button_info=PromptButtonInfo("No")
    )


class LayerModelUtils:

    @staticmethod
    def _prompt_content_transfer_and_create_layer(weakref_layer_item, file_path, position):
        layer_item = weakref_layer_item()
        if not layer_item:
            return

        # Skips it if this file is already in sublayer list
        for sublayer in layer_item.sublayers:
            if sublayer.identifier == file_path:
                return

        def create_layer_callback(weakref_item, file_path, transfer_content):
            layer_item = weakref_item()
            if not layer_item:
                return
            omni.kit.commands.execute(
                "CreateSublayer",
                layer_identifier=layer_item.identifier,
                sublayer_position=position,
                new_layer_path=file_path,
                transfer_root_content=transfer_content,
                create_or_insert=True,
                layer_name="",
            )

        root_layer_item = layer_item.model.root_layer_item
        if len(root_layer_item.sublayers) == 0:
            _show_transfer_root_content_prompt(
                lambda: create_layer_callback(weakref_layer_item, file_path, True),
                lambda: create_layer_callback(weakref_layer_item, file_path, False),
            )
        else:
            create_layer_callback(weakref_layer_item, file_path, False)

    @staticmethod
    def can_set_as_edit_target(layer_item):
        model = layer_item.model
        if model.root_layer_item.is_in_live_session and not layer_item.is_live_session_layer:
            return False

        if not model.root_layer_item.is_in_live_session and layer_item.is_in_live_session:
            return False

        return True

    @staticmethod
    def can_edit_sublayer(layer_item):
        if layer_item.is_live_session_layer or layer_item.is_in_live_session:
            return False

        return True

    @staticmethod
    def _found_existing_sublayer(layer_item, layer_identifier):
        for sublayer in layer_item.sublayers:
            if os.path.normpath(sublayer.identifier) == os.path.normpath(layer_identifier):
                return True

        return False

    @staticmethod
    def create_sublayer(layer_item, position: int, create_anonymous=False):
        if not LayerModelUtils.can_edit_sublayer(layer_item):
            nm.post_notification("Cannot create sublayers in live-syncing mode.")
            return False

        if create_anonymous:
            # Create anonymous layer for session layer only
            omni.kit.commands.execute(
                "CreateSublayer",
                layer_identifier=layer_item.identifier,
                sublayer_position=position,
                new_layer_path="",
                transfer_root_content=False,
                create_or_insert=True,
                layer_name="",
            )
        else:
            model = layer_item.model
            weakref_item = weakref.ref(layer_item)

            def create_sublayer_fn(file_paths: List[str], overwrite_existing: bool):
                LayerModelUtils._prompt_content_transfer_and_create_layer(weakref_item, file_paths[-1], position)

            if (
                not Sdf.Layer.IsAnonymousLayerIdentifier(model.root_layer_item.identifier)
                and LayerSettings().file_dialog_show_root_layer_location
            ):
                save_location = os.path.dirname(model.root_layer_item.identifier)
            else:
                save_location = None
            _show_save_file_picker("Create Sublayer", create_sublayer_fn, save_location)

    @staticmethod
    def remove_prim_spec_items(prim_item_list):
        layer_paths = {}
        for prim_item in prim_item_list:
            prim_path = prim_item.path
            layer_item = prim_item.layer_item
            if layer_item.identifier in layer_paths:
                layer_paths[layer_item.identifier].append(prim_path)
            else:
                layer_paths[layer_item.identifier] = [prim_path]

        with omni.kit.undo.group():
            for layer_identifier, paths in layer_paths.items():
                if not paths:
                    continue

                # Prune paths
                paths = sorted(paths)
                base_path = paths[0]
                prune_paths = [base_path]
                for path in paths:
                    if not path.HasPrefix(base_path):
                        base_path = path
                        prune_paths.append(path)

                omni.kit.commands.execute(
                    "RemovePrimSpec", layer_identifier=layer_identifier,
                    prim_spec_path=prune_paths
                )

    @staticmethod
    def insert_sublayer(layer_item, position: int):
        if not LayerModelUtils.can_edit_sublayer(layer_item):
            nm.post_notification("Cannot insert sublayers in live-syncing mode.")
            return False

        weakref_item = weakref.ref(layer_item)

        def insert_sublayer_fn(file_paths: List[str]):
            # overwrite_existing param does not apply in "Open" dialog
            layer_item = weakref_item()
            if not layer_item:
                return

            for file_path in file_paths:
                parent_item = layer_item
                while parent_item and parent_item.identifier != file_path:
                    parent_item = parent_item.parent

                if not parent_item:
                    found = LayerModelUtils._found_existing_sublayer(layer_item, file_path)
                    if found:
                        nm.post_notification(
                            f"Duplicate sublayer {file_path} found in the parent.",
                            status=nm.NotificationStatus.WARNING,
                            duration=4
                        )
                    else:
                        omni.kit.commands.execute(
                            "CreateSublayer",
                            layer_identifier=layer_item.identifier,
                            sublayer_position=position,
                            new_layer_path=file_path,
                            transfer_root_content=False,
                            create_or_insert=False,
                            layer_name="",
                        )
                else:
                    nm.post_notification(
                        f"Skip the insert as duplicate parent {file_path} found.",
                        status=nm.NotificationStatus.WARNING,
                        duration=4
                    )

        model = layer_item.model
        if (
            not Sdf.Layer.IsAnonymousLayerIdentifier(model.root_layer_item.identifier)
            and LayerSettings().file_dialog_show_root_layer_location
        ):
            insert_location = os.path.dirname(model.root_layer_item.identifier)
        else:
            insert_location = None

        _show_file_insert_picker("Insert Sublayer", insert_sublayer_fn, insert_location)

    @staticmethod
    def save_layer(layer_item):
        if not layer_item.dirty:
            return
        layer_identifier = layer_item.identifier

        def on_save_done(result, error, saved_layers):
            if not result:
                _show_save_error_prompt(layer_identifier)

        def on_save_as_done(result, error, saved_layers):
            if not result:
                _show_save_error_prompt(layer_identifier)
            else:
                layer_item.reload()

        if not layer_item.latest:

            def confirm_fn():
                layer_item.save(on_save_done)

            def middle_button_fn():
                LayerModelUtils.save_layer_as(layer_item, False, True, on_save_as_done, True)

            _show_outdated_layer_prompt(layer_item.identifier, confirm_fn, middle_button_fn, None, None)
        else:
            layer_item.save(on_save_done)

    @staticmethod
    def _create_layer(layer_identifier: str):
        layer = Sdf.Layer.FindOrOpen(layer_identifier)
        if layer:
            layer.Clear()
        else:
            layer = Sdf.Layer.CreateNew(layer_identifier)

        return layer

    @staticmethod
    def save_layer_as(layer_item, replace=False, insert_before=False, on_save_done=None, confirm_before_insert=False):
        """Save layer as new layer.

        Args:
            layer_item (LayerItem): Layer item to be saved.
            replace (bool): After save, if it needs to replace the item to be saved.
            insert_before (bool): After save, if it needs to be inserted before this item.
            `replace` and `insert_before` cannot be true at the same time.
            confirm_before_insert (bool): Before insert, it needs to confirm or not.
        """

        if not layer_item.layer:
            return

        if not layer_item.parent or not layer_item.parent.layer:
            replace = False

        # Uses weakref to avoid filepicker hold it's strong reference
        weakref_item = weakref.ref(layer_item)

        def on_file_selected(file_paths: List[str], overwrite_existing: bool):
            layer_item = weakref_item()
            if not layer_item or not layer_item.layer:
                return

            layer = layer_item.layer

            file_path = file_paths[-1]
            new_layer = LayerModelUtils._create_layer(file_path)
            if not new_layer:
                carb.log_error(f"Save layer failed. Failed to create layer {file_path}")
                return

            new_layer.TransferContent(layer)
            if not new_layer.Save():
                if on_save_done:
                    on_save_done(False, f"Save layer {layer.identifier} failed.", [])

            elif replace:
                parent = layer_item.parent
                position = LayerUtils.get_sublayer_position_in_parent(parent.identifier, layer_item.identifier)
                omni.kit.commands.execute(
                    "ReplaceSublayer",
                    layer_identifier=parent.identifier,
                    sublayer_position=position,
                    new_layer_path=new_layer.identifier,
                )
                LayerUtils.resolve_paths(layer, new_layer)

                # If edit target changes to one that's not in layer stack or session layer.
                usd_context = layer_item.usd_context
                stage = usd_context.get_stage()
                edit_target = stage.GetEditTarget()
                edit_target_identifier = LayerUtils.get_edit_target(stage)
                if (
                    edit_target_identifier == stage.GetSessionLayer().identifier
                    or edit_target.GetLayer() not in stage.GetLayerStack()
                ):
                    LayerUtils.set_edit_target(stage, stage.GetRootLayer().identifier)
            elif insert_before:

                def insert_layer():
                    parent = layer_item.parent
                    usd_context = layer_item.usd_context
                    stage = usd_context.get_stage()
                    if not parent:
                        parent_identifier = stage.GetRootLayer().identifier
                        position = 0
                    else:
                        parent_identifier = parent.identifier
                        position = LayerUtils.get_sublayer_position_in_parent(parent_identifier, layer_item.identifier)

                    omni.kit.commands.execute(
                        "CreateSublayer",
                        layer_identifier=parent_identifier,
                        sublayer_position=position,
                        new_layer_path=new_layer.identifier,
                        transfer_root_content=False,
                        create_or_insert=False,
                    )

                    LayerUtils.resolve_paths(layer, new_layer)
                    edit_target_identifier = LayerUtils.get_edit_target(stage)
                    if edit_target_identifier == layer.identifier:
                        LayerUtils.set_edit_target(stage, new_layer.identifier)

                if confirm_before_insert:
                    _show_confirm_layer_insert_prompt(new_layer.identifier, insert_layer)
                else:
                    insert_layer()

            if on_save_done:
                on_save_done(True, "", [new_layer.identifier])

            comment = ""
            if overwrite_existing:
                if layer.anonymous:
                    comment = "Replaced with new file"
                else:
                    comment = f"Replaced with {layer.identifier}"

            LayerUtils.create_checkpoint(new_layer.identifier, comment)

        if (
            not layer_item.anonymous
            and LayerSettings().file_dialog_show_root_layer_location
        ):
            save_location = os.path.dirname(layer_item.identifier)
        else:
            save_location = None

        save_name = os.path.splitext(layer_item.layer.GetDisplayName())[0]
        _show_save_file_picker("Save Layer As", on_file_selected, save_location, save_name)

    @staticmethod
    def remove_layer(layer_item):
        if not LayerModelUtils.can_edit_sublayer(layer_item):
            nm.post_notification("Cannot remove sublayers in live-syncing mode.")
            return False

        if not layer_item.parent or not layer_item.parent.layer:
            return

        if not LayerModelUtils.can_edit_sublayer(layer_item.parent):
            nm.post_notification("Cannot remove sublayers in live-syncing mode.")
            return False

        layer_identifier = layer_item.identifier
        parent_layer = layer_item.parent.layer
        position = LayerUtils.get_sublayer_position_in_parent(parent_layer.identifier, layer_identifier)
        is_empty_layer = not layer_item.layer or len(layer_item.layer.pseudoRoot.nameChildren) == 0

        def remove_layer_command(layer_identifier, position):
            omni.kit.commands.execute(
                "RemoveSublayer", layer_identifier=layer_identifier, sublayer_position=position
            )

        if not is_empty_layer or layer_item.dirty:
            _show_remove_dirty_layer_prompt(
                layer_item.identifier,
                layer_item.dirty,
                lambda: remove_layer_command(parent_layer.identifier, position),
            )
        else:
            remove_layer_command(parent_layer.identifier, position)

    @staticmethod
    def remove_layers(layer_items):
        if not layer_items:
            return False

        can_edit_sublayers = True
        for layer_item in layer_items:
            if not LayerModelUtils.can_edit_sublayer(layer_item):
                can_edit_sublayers = False
                break

        if not can_edit_sublayers:
            nm.post_notification("Cannot remove sublayers in live-syncing mode.")
            return False

        has_dirty_layer = False
        has_non_empty_layer = False
        for layer_item in layer_items:
            if not layer_item.layer:
                continue

            if layer_item.dirty:
                has_dirty_layer = True
                break

            if len(layer_item.layer.pseudoRoot.nameChildren) != 0:
                has_non_empty_layer = True
                break

        def remove_layers(layer_items):
            with omni.kit.undo.group():
                for layer_item in layer_items:
                    parent = layer_item.parent
                    if not parent or not parent.layer:
                        continue

                    position = LayerUtils.get_sublayer_position_in_parent(parent.identifier, layer_item.identifier)
                    omni.kit.commands.execute(
                        "RemoveSublayer", layer_identifier=parent.identifier, sublayer_position=position
                    )

        if has_non_empty_layer or has_dirty_layer:
            _show_remove_dirty_layer_prompt(
                "",
                has_dirty_layer,
                lambda: remove_layers(layer_items),
                multiple=True
            )
        else:
            remove_layers(layer_items)

    @staticmethod
    def reload_layer(layer_item):
        if layer_item.dirty:
            _show_reload_dirty_layer_prompt(layer_item.identifier, lambda: layer_item.reload())
        else:
            layer_item.reload()

    @staticmethod
    def flatten_all_layers(layer_model):
        if not layer_model:
            return

        if layer_model.is_in_live_session:
            nm.post_notification("Cannot flatten sublayers in live-syncing mode.")
            return False

        if LayerSettings().show_merge_or_flatten_warning:
            PromptManager.post_simple_prompt(
                "Flatten All Layers",
                "Flatten all layers will remove all sublayers except root layer. Do you want to flatten them?",
                ok_button_info=PromptButtonInfo("Yes", lambda: layer_model.flatten_all_layers()),
                cancel_button_info=PromptButtonInfo("No")
            )
        else:
            layer_model.flatten_all_layers()

    @staticmethod
    def merge_layer_down(layer_item):
        if not LayerModelUtils.can_edit_sublayer(layer_item):
            nm.post_notification("Cannot merge sublayers in live-syncing mode.")
            return False

        def _merge_internal():
            if not layer_item.parent:
                return

            if layer_item.locked:
                return

            position_in_parent = LayerUtils.get_sublayer_position_in_parent(
                layer_item.parent.identifier, layer_item.identifier
            )

            if position_in_parent < len(layer_item.parent.sublayers) - 1:
                layer_item_down = layer_item.parent.sublayers[position_in_parent + 1]
                omni.kit.commands.execute(
                    "MergeLayers",
                    dst_parent_layer_identifier=layer_item.parent.identifier,
                    dst_layer_identifier=layer_item_down.identifier,
                    src_parent_layer_identifier=layer_item.parent.identifier,
                    src_layer_identifier=layer_item.identifier,
                    dst_stronger_than_src=False,
                )

        if LayerSettings().show_merge_or_flatten_warning:
            layer_name = os.path.basename(layer_item.identifier)
            PromptManager.post_simple_prompt(
                "Merge Layer Down",
                f"Layer ({layer_name}) will be removed after merging down. Do you want to merge this layer?",
                ok_button_info=PromptButtonInfo("Yes", _merge_internal),
                cancel_button_info=PromptButtonInfo("No")
            )
        else:
            _merge_internal()

    @staticmethod
    def can_move_prim_spec_to_layer(target_layer, prim_spec):
        if prim_spec.layer_item == target_layer:
            return False

        if (
            not target_layer.editable
            or target_layer.locked
            or target_layer.missing
            or target_layer.muted_or_parent_muted
        ):
            return False

        return True

    @staticmethod
    def can_create_layer_to_location(target_layer, drop_location):
        # Checks to see if layer is moved to the location between live and base layer.
        target_parent = target_layer.parent
        as_sublayer = drop_location == -1
        if not LayerModelUtils.can_edit_sublayer(target_layer) and as_sublayer:
            return False

        if not as_sublayer and target_parent:
            total_prim_specs = len(target_parent.prim_specs)
            sublayer_location = drop_location - total_prim_specs
            if sublayer_location < 0:
                return False

            if sublayer_location > 0 and sublayer_location < len(target_parent.sublayers):
                sublayer = target_parent.sublayers[sublayer_location]
                up_sublayer = target_parent.sublayers[sublayer_location - 1]
                if (
                    not LayerModelUtils.can_edit_sublayer(sublayer) and
                    not LayerModelUtils.can_edit_sublayer(up_sublayer)
                ):
                    return False

        return True

    @staticmethod
    def can_move_layer(target_layer, source_layer, drop_location):
        """Checks if it's possible to move source layer to position of target layer."""
        as_sublayer = drop_location == -1
        if (
            not LayerModelUtils.can_edit_sublayer(source_layer) or
            (not LayerModelUtils.can_edit_sublayer(target_layer) and as_sublayer)
        ):
            return False

        if (
            target_layer == source_layer or
            target_layer.base_layer == source_layer or
            target_layer.live_session_layer == source_layer or
            source_layer.base_layer == target_layer or
            source_layer.live_session_layer == target_layer
        ):
            return False

        # Checks to see if layer is moved to the location between live and base layer.
        if not LayerModelUtils.can_create_layer_to_location(target_layer, drop_location):
            return False

        if source_layer.reserved:
            return False

        if not target_layer.reserved and not as_sublayer:
            target_parent = target_layer.parent
        else:
            target_parent = target_layer

        if (
            source_layer.muted_or_parent_muted
            or target_parent.muted_or_parent_muted
            or not target_parent.editable
            or target_parent.locked
            or not target_parent.layer
            or not LayerModelUtils.can_edit_sublayer(target_parent)
        ):
            return False

        return True

    @staticmethod
    def move_prim_spec(model, target_item, prim_item):
        target_layer_identifier = target_item.identifier
        source_layer_identifier = prim_item.layer_item.identifier
        dst_stronger_than_src = LayerModelUtils.is_stronger_than(model, target_item, prim_item.layer_item)
        prim_spec_path = prim_item.path

        def _move_prim_spec():
            omni.kit.commands.execute(
                "MovePrimSpecsToLayer",
                dst_layer_identifier=target_layer_identifier,
                src_layer_identifier=source_layer_identifier,
                prim_spec_path=str(prim_spec_path),
                dst_stronger_than_src=dst_stronger_than_src,
            )

        if LayerUtils.has_prim_spec(target_layer_identifier, prim_spec_path):
            _show_move_prim_spec_warning_prompt(target_layer_identifier, _move_prim_spec)
        else:
            _move_prim_spec()

    @staticmethod
    def move_layer(target_layer, source_layer, drop_location):
        """Moving from source layer to sublayer position of target layer."""
        if not LayerModelUtils.can_move_layer(target_layer, source_layer, drop_location):
            return False

        source_parent_layer_identifier = source_layer.parent.identifier
        source_layer_position = LayerUtils.get_sublayer_position_in_parent(
            source_parent_layer_identifier, source_layer.identifier
        )

        target_parent_layer_identifier = target_layer.identifier
        if drop_location == -1:
            target_layer_position = 0
        else:
            target_layer_position = drop_location

        parent = target_layer.parent
        while parent and parent != source_layer:
            parent = parent.parent

        # If it's to move from up to down.
        if (
            source_parent_layer_identifier == target_parent_layer_identifier and
            source_layer_position < target_layer_position
        ):
            target_layer_position -= 1

        # If source layer is ancestor of target.
        if parent:
            remove_source = False
        else:
            remove_source = True

        omni.kit.commands.execute(
            "MoveSublayer",
            from_parent_layer_identifier=source_parent_layer_identifier,
            from_sublayer_position=source_layer_position,
            to_parent_layer_identifier=target_parent_layer_identifier,
            to_sublayer_position=target_layer_position,
            remove_source=remove_source,
        )

    @staticmethod
    def _traverse(layer_item, target_layer, source_layer):
        parent = layer_item.parent
        while parent and parent.identifier != layer_item.identifier:
            parent = parent.parent

        # Stop traverse since circular reference found
        if parent:
            return -1

        if layer_item == target_layer:
            return 0
        elif layer_item == source_layer:
            return 1

        for sublayer in layer_item.sublayers:
            ret = LayerModelUtils._traverse(sublayer, target_layer, source_layer)
            if ret == 0 or ret == 1:
                return ret

        return -1

    @staticmethod
    def is_stronger_than(model, target_layer, source_layer):
        """Checks if target_layer is stronger than source_layer"""
        target_from_session_layer = target_layer.from_session_layer
        source_from_session_layer = source_layer.from_session_layer
        if target_from_session_layer and not source_from_session_layer:
            return True
        elif not target_from_session_layer and source_from_session_layer:
            return False
        else:
            result = LayerModelUtils._traverse(model.root_layer_item, target_layer, source_layer)
            return result == 0

    @staticmethod
    def save_model(model):
        """Saves all dirty layers of this model"""
        dirty_layers = model.get_all_dirty_layer_identifiers()
        if not dirty_layers:
            return

        def save_dirty_layers():
            model.save_layers(dirty_layers)

        if model.has_outdated_layers():
            _show_outdated_layers_prompt(dirty_layers, save_dirty_layers, None, None)
        else:
            save_dirty_layers()

    @staticmethod
    def lock_layer(layer_item, locked):
        with omni.kit.undo.group():
            queue = [layer_item]
            while queue:
                item = queue.pop()
                if (
                    not item.missing and
                    not item.read_only_on_disk and
                    not item.anonymous and
                    not item.reserved
                ):
                    item.locked = locked
                queue.extend(item.sublayers)

    @staticmethod
    def set_auto_authoring_mode(layer_model, enabled):
        layer_model.auto_authoring_mode = enabled
