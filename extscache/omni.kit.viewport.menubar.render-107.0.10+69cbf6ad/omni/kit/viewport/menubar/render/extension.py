# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportRenderMenuBarExtension", "get_instance", "SingleRenderMenuItemBase", "SingleRenderMenuItem"]

from typing import Callable, Optional
import omni.ext
from .menu_item.single_render_menu_item import SingleRenderMenuItem, SingleRenderMenuItemBase
from .renderer_menu_container import RendererMenuContainer

_extension_instance = None


class ViewportRenderMenuBarExtension(omni.ext.IExt):
    """The main class that manages the render settings integration into the viewport menu bar"""

    def on_startup(self, ext_id):
        self._render_menu = RendererMenuContainer()  # noqa: PLW0201
        self.__auto_enable_renderers()

        global _extension_instance
        _extension_instance = self

    def register_menu_item_type(self, menu_item_type: Callable[..., "SingleRenderMenuItemBase"]):
        """
        Register a custom menu type for the default created renderer

        Args:
            menu_item_type: callable that will create the menu item
        """
        if self._render_menu:  # noqa: PLW0201
            self._render_menu.set_menu_item_type(menu_item_type)

    def on_shutdown(self):
        if self._render_menu:  # noqa: PLW0201
            self._render_menu.destroy()
        self._render_menu = None  # noqa: PLW0201

        global _extension_instance
        _extension_instance = None

    @staticmethod
    def __auto_enable_renderers():
        # Read the auto-managed renderer list now to enable any renderers that were enabled on startup
        # but do not exist yet in /renderer/enabled.
        #
        import carb
        import omni.kit.app  # noqa: PLW0621

        ext_manager = omni.kit.app.get_app().get_extension_manager()
        if not ext_manager:
            carb.log_error("No extension manager interface")
            return

        settings = carb.settings.get_settings()
        auto_manage_prefix = "/exts/omni.kit.viewport.menubar.render/autoManage"
        managed_hd_exts = settings.get(f"{auto_manage_prefix}/enabledList") or ""
        if not managed_hd_exts:
            return

        edited_enabled = False
        can_remove = settings.get(f"{auto_manage_prefix}/canRemove")
        rnd_enabled_src = settings.get("/renderer/enabled") or ""
        rnd_enabled_dst = [rnd.lstrip().rstrip() for rnd in rnd_enabled_src.split(",") if rnd]
        for rndr_ext in [ext.lstrip().rstrip() for ext in managed_hd_exts.split(",")]:
            if ext_manager.is_extension_enabled(f"omni.hydra.{rndr_ext}"):
                if rndr_ext not in rnd_enabled_dst:
                    rnd_enabled_dst.append(rndr_ext)
                    edited_enabled = True
            elif can_remove:
                while rndr_ext in rnd_enabled_dst:
                    rnd_enabled_dst.remove(rndr_ext)
                    edited_enabled = True

        if edited_enabled:
            rnd_enabled_dst = ",".join(rnd_enabled_dst)
            settings.set("/renderer/enabled", rnd_enabled_dst)
            carb.log_info(f"Changing '/renderer/enabled' to '{rnd_enabled_dst}' from '{rnd_enabled_src}'")


def get_instance() -> Optional[ViewportRenderMenuBarExtension]:
    """
    Retrieves the singleton instance of the viewport render menu bar extension.
    """
    return _extension_instance
