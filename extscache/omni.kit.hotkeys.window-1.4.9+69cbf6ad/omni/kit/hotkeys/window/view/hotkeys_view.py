# pylint: disable=relative-beyond-top-level

__all__ = ["HotkeysView"]
import asyncio
from omni.kit.actions.window import ActionsView
import omni.ui as ui
import omni.kit.app
from ..model.hotkeys_model import HotkeysModel
from .hotkeys_delegate import HotkeysDelegate


class HotkeysView(ActionsView):
    def __init__(self, model: HotkeysModel, delegate: HotkeysDelegate):
        self.__delegate = delegate
        super().__init__(model, delegate)
        self.model.add_item_changed_fn(self.__model_changed)
        self.set_selection_changed_fn(self.__delegate.on_selection_changed)
        self.set_hover_changed_fn(self.__delegate.on_hover_changed)

    def __model_changed(self, model: HotkeysModel, item: ui.AbstractItem):
        if model.next_select_hotkey:
            # Select expect item
            async def __force_select_hotkey_async(select_hotkey):
                await omni.kit.app.get_app().next_update_async()
                for ext_item in self.model.get_item_children(None):
                    for hotkey_item in self.model.get_item_children(ext_item):
                        if hotkey_item.hotkey == select_hotkey:
                            self.set_expanded(ext_item, True, True)
                            self.selection = [hotkey_item]  # pylint: disable=attribute-defined-outside-init
                            return

            (saved_select_hotkey, model.next_select_hotkey) = (model.next_select_hotkey, None)
            asyncio.ensure_future(__force_select_hotkey_async(saved_select_hotkey))

        if model.search_done:
            # Auto expand on searching
            async def __force_expand_async():
                await omni.kit.app.get_app().next_update_async()
                self.set_expanded(None, True, True)
                model.search_done = False

            asyncio.ensure_future(__force_expand_async())
