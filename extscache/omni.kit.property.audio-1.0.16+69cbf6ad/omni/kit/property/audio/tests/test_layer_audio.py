# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path

import omni.kit.app
import omni.kit.commands
import omni.kit.test
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows
from omni.ui.tests.test_base import OmniUiTest


class TestLayerAudioWidget(OmniUiTest):  # pragma: no cover
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Layer")

        self._usd_path = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests"
        )

        usd_context = omni.usd.get_context()
        test_file_path = self._usd_path.joinpath("audio_test.usda").absolute()
        usd_context.open_stage(str(test_file_path))

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_layer_sound_ui(self):
        layer_window = ui_test.find("Layer")
        if not layer_window:
            return
        await ui_test.find("Layer").focus()
        await ui_test.find("Layer//Frame/**/TreeView[*]").find(
            "**/Label[*].text=='Root Layer (Authoring Layer)'"
        ).click()
        await ui_test.human_delay(50)
