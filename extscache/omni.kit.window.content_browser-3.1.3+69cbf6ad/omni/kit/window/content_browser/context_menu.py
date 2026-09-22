# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb.settings
from omni.kit.window.filepicker import UdimContextMenu, CollectionContextMenu, BookmarkContextMenu, ConnectionContextMenu, LocalContextMenu
from omni.kit.window.filepicker import ContextMenu as FilePickerContextMenu
from .file_ops import *
from .style import ICON_COMMON_PATH
from omni.kit.widget.filebrowser import save_items_to_clipboard, get_clipboard_items


class ContextMenu(FilePickerContextMenu):
    """
    Creates popup menu for the hovered FileBrowserItem.  In addition to the set of default actions below,
    users can add more via the add_menu_item API.

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        try:
            import omni.usd
            omni_usd_supported = True
        except Exception:
            omni_usd_supported = False

        if omni_usd_supported:
            self.add_menu_item(
                "Open",
                f"{ICON_COMMON_PATH}/icoOpen.svg",
                lambda menu, url: open_file(url),
                lambda url: get_file_open_handler(url) != None,
                index=0,
            )
            self.add_menu_item(
                "Open With Payloads Disabled",
                f"{ICON_COMMON_PATH}/icoOpenPayloadsDisabled.svg",
                lambda menu, url: open_file(url, load_all=False),
                lambda url: get_file_open_handler(url) != None,
                index=1,
            )
            self.add_menu_item(
                "Open With New Edit Layer",
                f"{ICON_COMMON_PATH}/icoOpenWithNewEditLayer.svg",
                lambda menu, url: open_stage_with_new_edit_layer(url),
                lambda url: omni.usd.is_usd_writable_filetype(url),
                index=2,
            )

        self.add_menu_item(
            "Copy",
            f"{ICON_COMMON_PATH}/icoCopyPrim.svg",
            lambda menu, _: save_items_to_clipboard(self._context["selected"]),
            # OM-94626: can't copy when select nothing
            lambda url: len(self._context["selected"]) >= 1,
            index=-2,
        )
        self.add_menu_item(
            "Cut",
            f"{ICON_COMMON_PATH}/icoCutPrim.svg",
            lambda menu, _: cut_items(self._context["selected"], self._view),
            lambda url: self._context["item"].writeable and len(self._context["selected"]) >= 1,
        )
        self.add_menu_item(
            "Paste",
            f"{ICON_COMMON_PATH}/icoPastePrim.svg",
            lambda menu, url: paste_items(self._context["item"], get_clipboard_items(), view=self._view),
            lambda url: self._context["item"].is_folder and self._context["item"].writeable and\
                len(self._context["selected"]) <= 1 and len(get_clipboard_items()) > 0,
            index=-2,
        )
        self.add_menu_item(
            "Download",
            f"{ICON_COMMON_PATH}/icoDownload.svg",
            lambda menu, _: download_items(self._context["selected"]),
            # OM-94626: can't download when select nothing
            lambda url: len(self._context["selected"]) >= 1 and \
               carb.settings.get_settings().get_as_bool("exts/omni.kit.window.content_browser/show_download_menuitem"),
            index=3,
            separator_name="_placeholder_"
        )
