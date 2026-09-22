## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from functools import partial
from .test_base import OmniUiTest
import omni.ui as ui
import omni.kit.app


class TestContainer(OmniUiTest):
    """Testing ui.Container"""

    async def test_context_manager(self):
        """Testing general properties of ui.Container"""
        window = await self.create_test_window()

        with window.frame as win_frame:
            with ui.VStack() as v_stack:
                with ui.Frame(width=0, height=0) as sub_frame:
                    ui.Label("Label in Frame")
        assert isinstance(win_frame, ui.Frame)
        assert isinstance(v_stack, ui.VStack)
        assert isinstance(sub_frame, ui.Frame)
        await self.finalize_test_no_image()

    async def test_add_child(self):
        window = await self.create_test_window()
        v_stack = ui.VStack()
        window.frame.add_child(v_stack)
        assert v_stack in ui.Inspector.get_children(window.frame)
        await self.finalize_test_no_image()

    async def test_clear(self):
        window = await self.create_test_window()
        with window.frame as win_frame:
            with ui.VStack() as v_stack:
                with ui.Frame(width=0, height=0) as sub_frame:
                    ui.Label("Label in Frame")
        v_stack.clear()
        assert len(ui.Inspector.get_children(v_stack)) == 0
        await self.finalize_test_no_image()