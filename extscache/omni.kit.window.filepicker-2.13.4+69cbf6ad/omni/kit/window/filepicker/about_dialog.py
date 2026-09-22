# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["AboutDialog"]
from typing import Callable
from omni.kit.window.popup_dialog import PopupDialog
import omni.ui as ui

from .style import get_style, ICON_PATH


class AboutDialog(PopupDialog):
    """Dialog to show the omniverse server info."""

    def __init__(
            self,
            server_info,
        ):
        """
        Initialize an AboutDialog.

        Args:
            server_info ([FileBrowserItem]): server's information.
            title (str): Title of the dialog. Default "Confirm File Deletion".
            width (int): Dialog width. Default `500`.
            ok_handler (Callable): Function to execute upon clicking the "Yes" button. Function signature:
                void ok_handler(dialog: :obj:`PopupDialog`)
        """
        super().__init__(
            width=400,
            title="About",
            ok_handler=lambda self: self.hide(),
            ok_label="Close",
            modal=True,
        )
        self._server_info = server_info
        self._build_ui()

    def _build_ui(self) -> None:
        with self._window.frame:
            with ui.ZStack(style=get_style(),spacing=6):
                ui.Rectangle(style_type_name_override="Background")
                with ui.VStack(style_type_name_override="Dialog", spacing=6):
                    ui.Spacer(height=25)
                    with ui.HStack(style_type_name_override="Dialog", spacing=6, height=60):
                        ui.Spacer(width=15)
                        ui.Image(
                            f"{ICON_PATH}/omniverse_logo_64.png",
                            width=50,
                            height=50,
                            alignment=ui.Alignment.CENTER
                            )
                        ui.Spacer(width=5)
                        with ui.VStack(style_type_name_override="Dialog"):
                            ui.Spacer(height=10)
                            ui.Label("Nucleus", style={"font_size": 20})
                            ui.Label(self._server_info.version)
                            ui.Spacer(height=5)
                    with ui.HStack(style_type_name_override="Dialog"):
                         ui.Spacer(width=15)
                         with ui.VStack(style_type_name_override="Dialog"):
                            ui.Label("Services", style={"font_size": 20})
                            self._build_info_item(True, "Discovery")
                            # OM-94622: what it this auth for? seems token is not correct
                            self._build_info_item(True, "Auth 1.4.5+tag-" + self._server_info.auth_token[:8])
                            has_tagging = False
                            try:
                                # TODO: how to check the tagging is exist? how to get it's version?
                                import omni.tagging_client
                                has_tagging = True
                            except ImportError:
                                pass
                            self._build_info_item(has_tagging, "Tagging")
                            # there always has search service in content browser
                            self._build_info_item(True, "NGSearch")
                            self._build_info_item(True, "Search")
                            ui.Label("Features", style={"font_size": 20})
                            self._build_info_item(True, "Versioning")
                            self._build_info_item(self._server_info.checkpoints_enabled, "Atomic checkpoints")
                            self._build_info_item(self._server_info.omniojects_enabled, "Omni-objects V2")
                    self._build_ok_cancel_buttons(disable_cancel_button=True)

    def _build_info_item(self, supported: bool, info: str):
        with ui.HStack(style_type_name_override="Dialog", spacing=6):
            ui.Spacer(width=5)
            if supported:
                ui.Image(
                "resources/icons/Ok_64.png",
                width=20,
                height=20,
                alignment=ui.Alignment.CENTER
                )
            else:
                ui.Image(
                "resources/icons/Cancel_64.png",
                width=20,
                height=20,
                alignment=ui.Alignment.CENTER
                )
            ui.Label(info)
            ui.Spacer()

    def destroy(self) -> None:
        """Destructor."""
        self._window = None
