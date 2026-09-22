## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ["MaterialLibraryTestHelper"]
import os
import asyncio
import omni.kit.app

from omni.kit import ui_test
from omni.kit.test_suite.helpers import wait_for_window, wait_stage_loading
from omni.kit.window.file_importer.test_helper import FileImporterTestHelper
from . import MaterialLibraryExtension


class MaterialLibraryTestHelper:
    class DialogError(Exception):
        def __init__(self, message):
            self.message = message

        def __str__(self):
            return self.message


    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass
    
    async def add_material(self, mdl_path: str, mtl_name: str = None, bind_selected_prims: bool = True):
        MaterialLibraryExtension._on_create_custom_mdl_material(mtl_created_list=None, bind_selected_prims=bind_selected_prims)
        await self.handle_add_material_dialog(mdl_path, mtl_name)

    async def handle_assign_material_dialog(self, index, strength_index=0):
        from pxr import Sdf

        # handle assign dialog
        prims = omni.usd.get_context().get_selection().get_selected_prim_paths()
        if len(prims) == 1:
            shape = Sdf.Path(prims[0]).name
            window_name = f"Bind material to {shape}###context_menu_bind"
        else:
            window_name = f"Bind material to {len(prims)} selected models###context_menu_bind"

        await wait_for_window(window_name)

        # open listbox
        widget = ui_test.find(f"{window_name}//Frame/**/Button[*].identifier=='combo_open_button'")
        await ui_test.emulate_mouse_move_and_click(widget.center, human_delay_speed=4)
        # select material item on listbox
        await wait_for_window("MaterialPropertyPopupWindow")
        widget = ui_test.find(f"MaterialPropertyPopupWindow//Frame/**/TreeView[*]")
        # FIXME - can't use widget.click as open combobox has no readable size and clicks goto stage window
        item_name = widget.model.get_item_children(None)[index].name_model.as_string if index else "None"
        await ui_test.find(f"MaterialPropertyPopupWindow//Frame/**/Label[*].text=='{item_name}'").click(human_delay_speed=4)

        # select strength item on listbox
        widget = ui_test.find(f"{window_name}//Frame/**/ComboBox[*]")
        if widget:
            widget.model.set_value(strength_index)

        # click ok
        widget = ui_test.find(f"{window_name}//Frame/**/Button[*].identifier=='assign_material_ok_button'")
        await ui_test.emulate_mouse_move_and_click(widget.center, human_delay_speed=4)

        # wait for materials to load
        await ui_test.human_delay()
        await wait_stage_loading()

    async def handle_create_material_dialog(self, mdl_path: str, mtl_name: str):
        subid_list = []
        def have_subids(id_list):
            nonlocal subid_list
            subid_list = id_list
        await omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=mdl_path, on_complete_fn=have_subids)
        if len(subid_list)> 1:
            # material has subid and dialog is shown
            await wait_for_window("Create Material")
            create_widget = ui_test.find("Create Material//Frame/**/Button[*].identifier=='create_material_ok_button'")
            subid_widget = ui_test.find("Create Material//Frame/**/ComboBox[*].identifier=='create_material_subid_combo'")
            if not subid_widget:
                raise MaterialLibraryTestHelper.DialogError("create material dialog not open")

            subid_list = subid_widget.model.get_item_list()
            subid_index = 0
            for index, subid in enumerate(subid_list):
                if subid.name == mtl_name:
                    subid_index = index
            subid_widget.model.set_current_index(subid_index)
            await ui_test.human_delay()
            create_widget.widget.call_clicked_fn()
            await ui_test.human_delay(4)
            await wait_stage_loading()

    async def handle_add_material_dialog(self, mdl_path: str, mtl_name: str = None):
        await wait_for_window("Select MDL")

        async with FileImporterTestHelper() as file_import_helper:
            # Wait for file importer dialog to be ready
            await ui_test.human_delay(10)
            await file_import_helper.click_apply_async(filename_url=mdl_path)
            await ui_test.human_delay()

        await self.handle_create_material_dialog(mdl_path, mtl_name)

    async def add_mtlx_material(self, mtlx_path: str, bind_selected_prims: bool=True):
        MaterialLibraryExtension._on_create_custom_mtlx_material(mtl_created_list=None, bind_selected_prims=bind_selected_prims)
        await self.handle_add_mtlx_material_dialog(mtlx_path)

    async def handle_add_mtlx_material_dialog(self, mtlx_path: str):
        await wait_for_window("Select MTLX")

        async with FileImporterTestHelper() as file_import_helper:
            # Wait for file importer dialog to be ready
            await ui_test.human_delay(10)
            await file_import_helper.click_apply_async(filename_url=mtlx_path)
            await ui_test.human_delay()
