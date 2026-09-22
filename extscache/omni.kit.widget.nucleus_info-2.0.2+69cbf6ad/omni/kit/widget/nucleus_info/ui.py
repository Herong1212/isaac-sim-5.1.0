# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Callable
from collections import namedtuple
from omni.kit.window.popup_dialog import PopupDialog
import omni.ui as ui


class NucleusAboutDialog(PopupDialog):
    """Dialog to show the omniverse server info."""
    FieldDef = namedtuple("AboutDialogFieldDef", "name version")
    _services_names = ["Discovery", "Auth", "Tagging", "NGSearch", "Search"]
    def __init__(
            self,
            nucleus_info,
            nucleus_services,
        ):
        """
        Args:
            nucleus_info ([ServerInfo]): nucleus server's information.
            nucleus_services ([ServicesData]): nucleus server's services
        Note:
        AboutDialog.FieldDef: 
            A namedtuple of (name, version) for describing the service's info,
        """
        super().__init__(
            width=400,
            title="About",
            ok_handler=lambda self: self.hide(),
            ok_label="Close",
            modal=True,
        )
        self._nucleus_info = nucleus_info
        self._nucleus_services = self._parse_services(nucleus_services)
        self._build_ui()

    def _parse_services(self, nucleus_services):
        parse_res = set()
        if nucleus_services:
            for service in nucleus_services:
                parse_res.add(
                    NucleusAboutDialog.FieldDef(
                        service.service_interface.name, 
                        service.meta.get('version','unknown')
                        )
                    )
        return parse_res

    def _build_ui(self) -> None:
        with self._window.frame:
            with ui.ZStack(spacing=6):
                ui.Rectangle(style_type_name_override="Background")
                with ui.VStack(style_type_name_override="Dialog", spacing=6):
                    ui.Spacer(height=25)
                    with ui.HStack(style_type_name_override="Dialog", spacing=6, height=60):
                        ui.Spacer(width=15)
                        ui.Image(
                            "resources/glyphs/omniverse_logo.svg",
                            width=50,
                            height=50,
                            alignment=ui.Alignment.CENTER
                            )
                        ui.Spacer(width=5)
                        with ui.VStack(style_type_name_override="Dialog"):
                            ui.Spacer(height=10)
                            ui.Label("Nucleus", style={"font_size": 20})
                            ui.Label(self._nucleus_info.version)
                            ui.Spacer(height=5)
                    with ui.HStack(style_type_name_override="Dialog"):
                         ui.Spacer(width=15)
                         with ui.VStack(style_type_name_override="Dialog"):
                            ui.Label("Services", style={"font_size": 20})
                            for service_name in NucleusAboutDialog._services_names:
                                self._build_service_item(service_name)
                            ui.Label("Features", style={"font_size": 20})
                            self._build_info_item(True, "Versioning")
                            self._build_info_item(self._nucleus_info.checkpoints_enabled, "Atomic checkpoints")
                            self._build_info_item(self._nucleus_info.omniojects_enabled, "Omni-objects V2")
                    self._build_ok_cancel_buttons(disable_cancel_button=True)

    def _build_service_item(self, service_name: str):
        supported = False
        version = "unknown"
        for service in self._nucleus_services:
            if service.name.startswith(service_name):
                supported = True
                version = service.version
                break
        self._build_info_item(supported, service_name + " " + version)

    def _build_info_item(self, supported: bool, info: str):
        with ui.HStack(style_type_name_override="Dialog", spacing=6):
            ui.Spacer(width=5)
            image_url = "resources/icons/Ok_64.png" if supported else "resources/icons/Cancel_64.png"
            ui.Image(image_url, width=20, height=20, alignment=ui.Alignment.CENTER)
            ui.Label(info)
            ui.Spacer()

    def destroy(self) -> None:
        """Destructor."""
        self._window = None
