class ContentHotkeys:
    """The Content Browser Hotkeys"""

    def __init__(self, ext_id: str, ext_inst, window_title: str):
        self._ext_id = ext_id
        self._ext_inst = ext_inst

        try:
            from omni.kit.actions.core import get_action_registry
            from omni.kit.hotkeys.core import get_hotkey_registry, HotkeyFilter

            self._action_registry = get_action_registry()
            self._hotkey_registry = get_hotkey_registry()
            self._hotkey_filter = HotkeyFilter(windows=[window_title])

            self._register_hotkeys()
        except ImportError:
            self._action_registry = None
            self._hotkey_registry = None

    def destroy(self):
        self._deregister_hotkeys()

    def _register_a_hotkey(self, action_id:str, display_name: str, hotkey_string: str, action_fn: callable):
        if self._action_registry:
            self._action_registry.register_action(self._ext_id, action_id, action_fn, display_name=display_name)
            if self._hotkey_registry:
                self._hotkey_registry.register_hotkey(self._ext_id, hotkey_string, self._ext_id, action_id, filter=self._hotkey_filter)

    def _register_hotkeys(self):
        self._register_a_hotkey("Copy", "Content->Copy Selected", "CTRL + C", self._copy)
        self._register_a_hotkey("Cut", "Content->Cut Selected", "CTRL + X", self._cut)
        self._register_a_hotkey("Paste", "Content->Paste", "CTRL + V", self._paste)
        self._register_a_hotkey("Delete", "Content->Delete Selected", "DEL", self._delete)
        self._register_a_hotkey("Rename", "Content->Rename Selected", "F2", self._rename)
        self._register_a_hotkey("Clear Clipboard", "Clear Clipboard", "ESCAPE", self._clear_clipboard)

    def _deregister_hotkeys(self):
        if self._hotkey_registry:
            self._hotkey_registry.deregister_all_hotkeys_for_extension(self._ext_id)
        if self._action_registry:
            self._action_registry.deregister_all_actions_for_extension(self._ext_id)

    def _copy(self):
        if self._ext_inst.api:
            self._ext_inst.api.copy_selected_items()

    def _cut(self):
        if self._ext_inst.api:
            self._ext_inst.api.cut_selected_items()

    def _paste(self):
        if self._ext_inst.api:
            self._ext_inst.api.paste_items()

    def _delete(self):
        if self._ext_inst.api:
            self._ext_inst.api.delete_selected_items()

    def _rename(self):
        if self._ext_inst.api:
            self._ext_inst.api.rename_selected_item()

    def _clear_clipboard(self):
        if self._ext_inst.api:
            self._ext_inst.api.clear_clipboard()
