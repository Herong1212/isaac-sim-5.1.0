# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["StageMdlConverterExtension"]

from pxr import Sdf
import omni.ext
import omni.usd
import omni.kit.context_menu
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.window.popup_dialog import MessageDialog
import os
import omni.ui as ui
import asyncio
import carb
from omni.kit.helper.file_utils import get_last_url_opened

class AskForOverrideDialog(MessageDialog):
    WINDOW_FLAGS = ui.WINDOW_FLAGS_NO_RESIZE
    WINDOW_FLAGS |= ui.WINDOW_FLAGS_POPUP
    WINDOW_FLAGS |= ui.WINDOW_FLAGS_NO_SCROLLBAR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self._style = self._style.copy()
        # self._style["Background"]["background_color"] = ui.color("#00000000")
        # self._style["Background"]["border_color"] = ui.color("#00000000")

class WarningDialog(MessageDialog):
    WINDOW_FLAGS = ui.WINDOW_FLAGS_NO_RESIZE
    WINDOW_FLAGS |= ui.WINDOW_FLAGS_POPUP
    WINDOW_FLAGS |= ui.WINDOW_FLAGS_NO_SCROLLBAR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SimplifyDialog(MessageDialog):
    WINDOW_FLAGS = ui.WINDOW_FLAGS_NO_RESIZE
    WINDOW_FLAGS |= ui.WINDOW_FLAGS_POPUP
    WINDOW_FLAGS |= ui.WINDOW_FLAGS_NO_SCROLLBAR
    WINDOW_FLAGS |= ui.WINDOW_FLAGS_MODAL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StageMdlConverterExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        app = omni.kit.app.get_app_interface()
        ext_manager = app.get_extension_manager()

        self._stage_menu = ext_manager.subscribe_to_extension_enable(
            on_enable_fn=lambda _: self._register_stage_menu(),
            on_disable_fn=lambda _: self._unregister_stage_menu(),
            ext_name="omni.kit.widget.stage",
            hook_name="omni.kit.stage.mdl_converter",
        )
        self._pick_export_path_dialog = None
        self._override_dialog = None
        self._warning_dialog = None
        self._simplify_dialog = None
        self._selected_prim = None
        self._current_dir = None
        if get_last_url_opened():
            self._current_dir = os.path.dirname(get_last_url_opened())
        else:
            self._current_dir = '/'
        self._current_export_path = None

    def on_shutdown(self):
        self._unregister_stage_menu()
        self._stage_menu = None
        self._stage_context_menu_export = None
        self._stage_context_menu_expand = None

    @staticmethod
    def __on_filter_mdl_files(item: FileBrowserItem) -> bool:
        """Used by pick folder dialog to hide all the files"""
        if item and not item.is_folder:
            _, ext = os.path.splitext(item.path)
            return (ext in [".mdl"])
        return True

    def __run_export(self):
        """Do the actual export after we have a filename to export to"""
        carb.log_info(f"Picked output filename: {self._current_export_path}")
        asyncio.ensure_future(omni.mdl.usd_converter.usd_to_mdl(self._current_export_path, self._selected_prim))

    def __on_ok_override(self, popup):
        """Called when the the user confirmed to override"""
        carb.log_info(f"Confirmed to override selected filename: {self._current_export_path}")
        popup.hide()
        self.__run_export()

    def __on_cancel_override(self, popup):
        """Called when the the user rejected to override"""
        carb.log_info(f"Rejected to override selected filename: {self._current_export_path}")
        popup.hide()
        self._pick_export_path_dialog.refresh_current_directory()
        self._pick_export_path_dialog.show(path=self._current_export_path)

    def __on_ok_warning(self, popup):
        """Called when the the user closes warning dialog"""
        popup.hide()

    def __on_simplify_yes(self, popup):
        """Called when the the user closes warning dialog"""
        popup.hide()
        omni.mdl.usd_converter.build_shader_node_for_material(self._selected_prim, merge_identical_subgraphs_after_expand = True)

    def __on_simplify_no(self, popup):
        """Called when the the user closes warning dialog"""
        popup.hide()
        omni.mdl.usd_converter.build_shader_node_for_material(self._selected_prim)

    def __on_apply_filename(self, filename: str, dir: str):
        """Called when the user press "Export" in the pick filename dialog"""

        # don't accept as long as no filename is selected
        if not filename or not dir:
            return

        # add the file extension if missing
        if len(filename) < 5 or filename[-4:] != '.mdl':
            filename = filename + '.mdl'

        self._current_dir = dir

        # add a trailing slash for the client library
        if(dir[-1] != os.sep):
            dir = dir + os.sep
        self._current_export_path = omni.client.combine_urls(dir, filename)

        self._pick_export_path_dialog.hide()

        # ask for override or run export directly
        if os.path.exists(self._current_export_path):
            carb.log_info(f"WARNING: selected filename already exists: {self._current_export_path}")

            if self._override_dialog != None:
                self._override_dialog.destroy()

            self._override_dialog = AskForOverrideDialog(
                title = "Confirm override...",
                message = "The selected file already exists. Do you want to replace it?",
                ok_label = "Yes",
                cancel_label = "No",
                ok_handler = self.__on_ok_override,
                cancel_handler = self.__on_cancel_override
            )
            # self._override_dialog.build_ui()
            self._override_dialog.show()
        else:
            self.__run_export()

    def _register_stage_menu(self):
        """Called when "omni.kit.widget.stage" is loaded"""

        def on_export(objects: dict):
            """Called from the context menu"""

            # keep the selected prim
            prims = objects.get("prim_list", None)
            if not prims or len(prims) > 1:
                return
            if len(prims) == 1:
                theprim = prims[0]
                stage = theprim.GetStage()
                (status, message) = omni.mdl.usd_converter.is_shader_resolved(stage, theprim)
                if not status:
                    carb.log_warn(message)
                    if self._warning_dialog != None:
                        self._warning_dialog.destroy()
                    self._warning_dialog = WarningDialog(
                        title = "Convert Material to MDL",
                        message = "WARNING: " + message,
                        disable_cancel_button=True,
                        ok_handler = self.__on_ok_warning,
                    )
                    self._warning_dialog.show()
                    return
                if not omni.mdl.usd_converter.is_material_bound_to_prim(stage, theprim):
                    # Material not bound, display warning dialog and do not proceed
                    carb.log_warn(f"Material is not bound to any prim, can not convert")
                    if self._warning_dialog != None:
                        self._warning_dialog.destroy()
                    self._warning_dialog = WarningDialog(
                        title = "Convert Material to MDL",
                        message = "WARNING: Material is not bound to any prim, can not convert",
                        disable_cancel_button=True,
                        ok_handler = self.__on_ok_warning,
                    )
                    self._warning_dialog.show()
                    return

            self._selected_prim = prims[0]

            """Open Pick Folder dialog to add compounds"""
            if self._pick_export_path_dialog is None:
                self._pick_export_path_dialog = FilePickerDialog(
                    "Convert Material to MDL and Export As...",
                    allow_multi_selection=False,
                    apply_button_label="Export",
                    cancel_button_label="Cancel",
                    click_apply_handler=self.__on_apply_filename,
                    item_filter_options=["MDL Files (*.mdl)"],
                    item_filter_fn=self.__on_filter_mdl_files,
                    # OM-61553: Use the selected material prim name as the default filename
                    current_filename=self._selected_prim.GetName(),
                    current_directory=self._current_dir
                )

            if self._pick_export_path_dialog is not None:
                self._pick_export_path_dialog.refresh_current_directory()
                self._pick_export_path_dialog.set_filename(self._selected_prim.GetName())
                self._pick_export_path_dialog.show(path=self._current_export_path)

        def on_expand(objects: dict):
            """Called from the context menu"""

            # keep the selected prim
            prims = objects.get("prim_list", None)
            if not prims or len(prims) > 1:
                return
            if len(prims) == 1:
                theprim = prims[0]
                stage = theprim.GetStage()
                (status, message) = omni.mdl.usd_converter.is_shader_resolved(stage, theprim)
                if not status:
                    carb.log_warn(message)
                    if self._warning_dialog != None:
                        self._warning_dialog.destroy()
                    self._warning_dialog = WarningDialog(
                        title = "Expand Material",
                        message = "WARNING: " + message,
                        disable_cancel_button=True,
                        ok_handler = self.__on_ok_warning,
                    )
                    self._warning_dialog.show()
                    return
                if not omni.mdl.usd_converter.is_material_bound_to_prim(stage, theprim):
                    # Material not bound, display warning dialog and do not proceed
                    carb.log_warn(f"Material is not bound to any prim, can not convert")
                    if self._warning_dialog != None:
                        self._warning_dialog.destroy()
                    self._warning_dialog = WarningDialog(
                        title = "Expand Material",
                        message = "WARNING: Material is not bound to any prim, can not expand",
                        disable_cancel_button=True,
                        ok_handler = self.__on_ok_warning,
                    )
                    self._warning_dialog.show()
                    return

            self._selected_prim = prims[0]

            # Display the simplify checkbox UI
            if self._simplify_dialog != None:
                self._simplify_dialog.destroy()
            self._simplify_dialog = SimplifyDialog(
                title = "Expand Material",
                message = "Do you want to merging identical sub-graphs after expand?",
                ok_label = "Yes",
                cancel_label = "No",
                ok_handler = self.__on_simplify_yes,
                cancel_handler = self.__on_simplify_no,
            )
            self._simplify_dialog.show()

        # Add context menu to omni.kit.widget.stage
        context_menu = omni.kit.context_menu.get_instance()
        if context_menu:
            menu = {
                "name": "Export to MDL",
                "glyph": "menu_save.svg",
                "show_fn": [context_menu.is_material, context_menu.is_one_prim_selected],
                "onclick_fn": on_export,
                "appear_after": "Save Selected",
            }
            menu_expand = {
                "name": "Expand Graph",
                "glyph": "menu_save.svg",
                "show_fn": [context_menu.is_material, context_menu.is_one_prim_selected],
                "onclick_fn": on_expand,
                "appear_after": "Export to MDL",
            }
            self._stage_context_menu_export = omni.kit.context_menu.add_menu(menu, "MENU", "omni.kit.widget.stage")
            self._stage_context_menu_expand = omni.kit.context_menu.add_menu(menu_expand, "MENU", "omni.kit.widget.stage")

    def _unregister_stage_menu(self):
        """Called when "omni.kit.widget.stage" is unloaded"""
        if self._pick_export_path_dialog:
            self._pick_export_path_dialog.destroy()
            self._pick_export_path_dialog = None

        if self._override_dialog:
            self._override_dialog.destroy()
            self._override_dialog = None

        if self._warning_dialog:
            self._warning_dialog.destroy()
            self._warning_dialog = None

        if self._simplify_dialog:
            self._simplify_dialog.destroy()
            self._simplify_dialog = None

        self._stage_context_menu_export = None
        self._stage_context_menu_expand = None
