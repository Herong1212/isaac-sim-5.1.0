## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from .test_base import OmniUiTest
from omni.ui import color as cl
from omni.ui import style as st
from omni.ui import url
from pathlib import Path
import omni.kit.app
import omni.ui as ui

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.parent.parent.parent.joinpath("data")

STYLE = {
    "MyRect": {"background_color": 0xFFEDB51A},
    "MyRect::test": {"background_color": 0xFFD6D50D},
    "MyRect:disabled": {"background_color": 0xFFB6F70F},
    "Rectangle": {"background_color": 0xFFF73F0F},
    "Rectangle::test": {"background_color": 0xFFD66C0D},
    "Rectangle:disabled": {"background_color": 0xFFD99C38},
    "Window": {"background_color": 0xFF000000, "border_color": 0x0, "border_radius": 0},
}

STYLE_SHADE = {
    "MyRect": {"background_color": cl.shade(0xFFEDB51A, light=cl("#DB6737"))},
    "MyRect::test": {"background_color": cl.shade(0xFFD6D50D, light=cl("#F24E30"))},
    "MyRect:disabled": {"background_color": cl.shade(0xFFB6F70F, light=cl("#E8302E"))},
    "Rectangle": {"background_color": cl.shade(0xFFF73F0F, light=cl("#E8A838"))},
    "Rectangle::test": {"background_color": cl.shade(0xFFD66C0D, light=cl("#F2983A"))},
    "Rectangle:disabled": {"background_color": cl.shade(0xFFD99C38, light=cl("#DB7940"))},
    "Window": {"background_color": 0xFF000000, "border_color": 0x0, "border_radius": 0},
}


class TestStyle(OmniUiTest):
    """Testing ui.Rectangle"""

    async def test_default(self):
        """Testing using of st.default"""
        buffer = st.default

        window = await self.create_test_window()
        with window.frame:
            with ui.HStack():
                ui.Rectangle()
                ui.Rectangle(name="test")
                ui.Rectangle(enabled=False)
                ui.Rectangle(style_type_name_override="MyRect")
                ui.Rectangle(style_type_name_override="MyRect", name="test")
                ui.Rectangle(style_type_name_override="MyRect", enabled=False)

        st.default = STYLE

        await self.finalize_test()

        st.default = buffer

    async def test_window(self):
        """Testing using of window style"""
        window = await self.create_test_window()
        with window.frame:
            with ui.HStack():
                ui.Rectangle()
                ui.Rectangle(name="test")
                ui.Rectangle(enabled=False)
                ui.Rectangle(style_type_name_override="MyRect")
                ui.Rectangle(style_type_name_override="MyRect", name="test")
                ui.Rectangle(style_type_name_override="MyRect", enabled=False)

        window.frame.style = STYLE

        await self.finalize_test()

    async def test_stack(self):
        """Testing using of stack style"""
        window = await self.create_test_window()
        with window.frame:
            with ui.HStack(style=STYLE):
                ui.Rectangle()
                ui.Rectangle(name="test")
                ui.Rectangle(enabled=False)
                ui.Rectangle(style_type_name_override="MyRect")
                ui.Rectangle(style_type_name_override="MyRect", name="test")
                ui.Rectangle(style_type_name_override="MyRect", enabled=False)

        await self.finalize_test()

    async def test_leaf(self):
        """Testing using of leaf children style"""
        window = await self.create_test_window()
        with window.frame:
            with ui.HStack():
                ui.Rectangle(style=STYLE)
                ui.Rectangle(name="test", style=STYLE)
                ui.Rectangle(enabled=False, style=STYLE)
                ui.Rectangle(style_type_name_override="MyRect", style=STYLE)
                ui.Rectangle(style_type_name_override="MyRect", name="test", style=STYLE)
                ui.Rectangle(style_type_name_override="MyRect", enabled=False, style=STYLE)

        await self.finalize_test()

    async def test_shade(self):
        """Testing default shade"""
        window = await self.create_test_window()
        ui.set_shade()
        with window.frame:
            with ui.HStack():
                ui.Rectangle()
                ui.Rectangle(name="test")
                ui.Rectangle(enabled=False)
                ui.Rectangle(style_type_name_override="MyRect")
                ui.Rectangle(style_type_name_override="MyRect", name="test")
                ui.Rectangle(style_type_name_override="MyRect", enabled=False)

        window.frame.style = STYLE_SHADE

        await self.finalize_test()

    async def test_named_shade(self):
        """Testing named shade"""
        window = await self.create_test_window()
        ui.set_shade()
        with window.frame:
            with ui.HStack():
                ui.Rectangle()
                ui.Rectangle(name="test")
                ui.Rectangle(enabled=False)
                ui.Rectangle(style_type_name_override="MyRect")
                ui.Rectangle(style_type_name_override="MyRect", name="test")
                ui.Rectangle(style_type_name_override="MyRect", enabled=False)

        window.frame.style = STYLE_SHADE
        ui.set_shade("light")

        await self.finalize_test()

        # Return it back to default
        ui.set_shade()

    async def test_named_colors(self):
        """Testing named shade"""
        window = await self.create_test_window()
        ui.set_shade()
        cl.test = cl("#74B9AF")
        cl.common = cl("#F24E30")
        with window.frame:
            with ui.HStack():
                ui.Rectangle(style={"background_color": "DarkSlateGrey"})
                ui.Rectangle(style={"background_color": "DarkCyan"})
                ui.Rectangle(style={"background_color": "test"})
                ui.Rectangle(style={"background_color": cl.shade(cl.test, light=cl.common, name="shade_name")})
                ui.Rectangle(style={"background_color": cl.shade_name})

        window.frame.style = STYLE_SHADE
        ui.set_shade("light")
        # Checking read-only colors
        cl.DarkCyan = cl("#000000")
        # Checking changing of colors by name
        cl.common = cl("#9FDBCB")

        await self.finalize_test()

        # Return it back to default
        ui.set_shade()

    async def test_named_shade_append(self):
        """Testing named shade"""
        window = await self.create_test_window()
        ui.set_shade()

        cl.test_named_shade = cl.shade(cl("#000000"), red=cl("#FF0000"), blue=cl("#0000FF"))

        # Append blue to the existing shade. Two shades should be the same.
        cl.test_named_shade_append = cl.shade(cl("#000000"), red=cl("#FF0000"))
        cl.test_named_shade_append.add_shade(blue=cl("#0000FF"))

        with window.frame:
            with ui.HStack():
                ui.Rectangle(style={"background_color": cl.test_named_shade})
                ui.Rectangle(style={"background_color": cl.test_named_shade_append})

        ui.set_shade("blue")

        await self.finalize_test()

        # Return it back to default
        ui.set_shade()

    async def test_named_urls(self):
        """Testing named shade"""
        loaded = [0]

        def track_progress(progress):
            if progress == 1.0:
                loaded[0] += 1

        window = await self.create_test_window()
        ui.set_shade()

        # Wrong colors
        url.test_red = f"{DATA_PATH}/tests/blue.png"
        url.test_green = f"{DATA_PATH}/tests/red.png"
        url.test_blue = f"{DATA_PATH}/tests/green.png"

        with window.frame:
            with ui.VStack():
                with ui.HStack():
                    ui.Image(style={"image_url": url.test_red}, progress_changed_fn=track_progress)
                    ui.Image(style={"image_url": "test_green"}, progress_changed_fn=track_progress)
                    ui.Image(style={"image_url": url.test_blue}, progress_changed_fn=track_progress)
                with ui.HStack():
                    ui.Image(
                        style={"image_url": url.shade(f"{DATA_PATH}/tests/red.png")}, progress_changed_fn=track_progress
                    )
                    ui.Image(
                        style={
                            "image_url": url.shade(
                                f"{DATA_PATH}/tests/blue.png", test_url=f"{DATA_PATH}/tests/green.png"
                            )
                        },
                        progress_changed_fn=track_progress,
                    )
                    ui.Image(
                        style={
                            "image_url": url.shade(
                                f"{DATA_PATH}/tests/blue.png", test_url_light=f"{DATA_PATH}/tests/green.png"
                            )
                        },
                        progress_changed_fn=track_progress,
                    )

        # Correct colors
        url.test_red = f"{DATA_PATH}/tests/red.png"
        url.test_green = f"{DATA_PATH}/tests/green.png"
        url.test_blue = f"{DATA_PATH}/tests/blue.png"

        # Change shade
        ui.set_shade("test_url")

        while loaded[0] < 6:
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

        # Return it back to default
        ui.set_shade()
