## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from pathlib import Path

import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.window.extensions
import omni.ui as ui
from omni.kit.test_suite.helpers import get_test_data_path, wait_stage_loading
from omni.kit.window.extensions.markdown_renderer import MarkdownText
from omni.ui.tests.compare_utils import CompareMetric
from omni.ui.tests.test_base import OmniUiTest


class TestMarkdown(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_markdown(self):
        width = 800
        height = 1920
        window = await self.create_test_window(width=width, height=height)
        markdown_index = 1
        text_editor_tag = (
            "te"
            if omni.kit.app.get_app().get_extension_manager().is_extension_enabled("omni.kit.widget.text_editor")
            else "lab"
        )

        ext_info = {"path": get_test_data_path(__name__, "markdown")}
        ext_item = None

        readme_str = "test...\n"
        with open(get_test_data_path(__name__, f"markdown/test{markdown_index}.md"), "r", encoding="utf-8") as f:
            readme_str = f.read()

        with window.frame:
            sframe = ui.ScrollingFrame(
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            )
            with sframe:
                with ui.ZStack():
                    ui.Rectangle(style_type_name_override="ExtensionDescription.ContentBackground")
                    with ui.VStack(height=0):
                        MarkdownText(readme_str, ext_info, ext_item)

            await ui_test.human_delay(10)

            for page, y in enumerate(range(0, 100000, int(height))):
                sframe.scroll_y = y

                # allow time for images to load
                await wait_stage_loading()

                await self.capture_and_compare(
                    threshold=None,
                    golden_img_dir=Path(get_test_data_path(__name__, "golden_img")),
                    golden_img_name=f"test_markdown_{text_editor_tag}_{markdown_index}_page_{page+1}.png",
                    use_log=True,
                    cmp_metric=CompareMetric.MEAN_ERROR,
                    test_name="omni.kit.window.extensions.tests.test_markdown.TestMarkdown.test_markdown",
                    hide_menu_bar=True,
                )

                page += 1
                if sframe.scroll_y < y:
                    break

        await self.finalize_test_no_image()
