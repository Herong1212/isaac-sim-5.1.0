import abc
import weakref
from typing import TYPE_CHECKING, Callable

import omni.ui as ui
from omni.kit.viewport.menubar.core import ViewportMenuDelegate

if TYPE_CHECKING:
    from omni.kit.widget.viewport.api import ViewportAPI

    from ..hd_renderer_list import HdEngineRenderer, HdRenderer


class SingleRenderMenuItemBase(ui.MenuItem):
    """
    A base menu item represent a single renderer
    """

    def __init__(
        self,
        display_name: str,
        engine_name: str,
        hd_engine_renderer: "HdEngineRenderer",
        hd_renderer: "HdRenderer",
        viewport_api: "ViewportAPI",
        enabled: bool,
        checked: bool,
        hide_on_click: bool,
        triggered_fn: Callable,
        hotkey_text: str = "",
        show_hotkey_placeholder: bool = False,
    ):
        """
        A base class for creating custom single renderer menu items.

        Args:
            display_name (str): Menu's text
            engine_name (str): Renderer engine name
            hd_engine_renderer (HdEngineRenderer): Renderer engine
            hd_renderer (HdRenderer): Renderer
            viewport_api (ViewportAPI): Viewport API
            enabled (bool): If menu item enabled
            checked (bool): If menu item checked
            hide_on_click (bool): If hide menu item when clicked
            triggered_fn (Callable): Callback when men item clicked

        Keyword Args:
            hotkey_text (str): Hotkey text. By default "" means no hotkey text displayed
            show_hotkey_placeholder (bool): If show placeholder for hotkey in menu item. Default False

        """
        self.__viewport_api = viewport_api
        self.__engine_name = engine_name
        self.__hd_engine_renderer = hd_engine_renderer
        self.__hd_renderer = hd_renderer
        self.__options_button = None

        def _build_menuitem_widgets(_self=weakref.ref(self)):
            if (self := _self()) is None:
                return
            return self._build_menuitem_widgets()

        super().__init__(
            display_name,
            enabled=enabled,
            checkable=True,
            checked=checked,
            delegate=ViewportMenuDelegate(
                force_checked=False,
                build_custom_widgets=lambda delegate, item: _build_menuitem_widgets(),
                show_hotkey_placeholder=show_hotkey_placeholder,
            ),
            hide_on_click=hide_on_click,
            triggered_fn=triggered_fn,
            hotkey_text=hotkey_text,
        )

    def destroy(self):
        """
        Remove custom ui widgets.
        """
        self.__options_button = None
        super().destroy()

    @property
    def hd_renderer(self) -> "HdRenderer":
        """
        Renderer binding to this menu item.
        """
        return self.__hd_renderer

    @property
    def hd_engine_renderer(self) -> "HdEngineRenderer":
        """
        Renderer engine binding to this menu item.
        """
        return self.__hd_engine_renderer

    @property
    def engine_name(self) -> str:
        """
        Render engine name binding to this menu item.
        """
        return self.__engine_name

    @property
    def viewport_api(self) -> "ViewportAPI":
        """
        Viewport API binding to this menu item.
        """
        return self.__viewport_api

    def _build_menuitem_widgets(self):
        ui.Spacer(width=10)
        self.__option_container = ui.VStack(content_clipping=self.checked, width=16)

        def _option_clicked(_self=weakref.ref(self)):
            if (self := _self()) is None:
                return
            self._option_clicked()

        with self.__option_container:
            # Button to show renderer settings
            self.__options_button = ui.Button(
                style_type_name_override="Menu.Item.Button",
                name="OptionBox",
                width=16,
                height=16,
                image_width=16,
                image_height=16,
                visible=self.checked,
                clicked_fn=_option_clicked,
            )

    @abc.abstractmethod
    def _option_clicked(self):
        """
        Function to implement when the option is clicked. Used by RTX Remix

        :meta public:
        """
        return

    def set_checked(self, checked: bool) -> None:
        """
        Set menu state to be checked
        """
        self.checked = checked  # noqa: PLW0201
        self.delegate.checked = checked

        # Only show options button when it is current renderer
        self.__options_button.visible = checked
        self.__option_container.content_clipping = checked


class SingleRenderMenuItem(SingleRenderMenuItemBase):
    """
    A default implementation for a single renderer menu item, with an option to open render settings
    """

    def _option_clicked(self):
        """
        Open the render settings window when clicking the option icon on the right of this menu item.
        """
        try:
            from omni.rtx.window.settings import RendererSettingsFactory

            rs_instance = RendererSettingsFactory.render_settings_extension_instance
            if rs_instance:
                rs_instance.show_render_settings(self.engine_name, self.hd_renderer.pluginID, True)
        except ImportError:
            pass
