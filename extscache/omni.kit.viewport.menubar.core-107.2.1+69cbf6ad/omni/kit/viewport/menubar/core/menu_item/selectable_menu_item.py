from typing import Callable, Optional

from omni import ui

from ..delegate.viewport_menu_delegate import ViewportMenuDelegate


__all__ = ["SelectableMenuItem"]


class SelectableMenuItem(ui.MenuItem):
    """A menu item can be selected."""

    def __init__(self, name: str,
                 model: Optional[ui.AbstractValueModel] = None,
                 delegate: Optional[ui.MenuDelegate] = None,
                 hide_on_click: bool = False,
                 toggle: bool = True,
                 triggered_fn: Callable = None,
                 trigger_will_set_model: bool = False,
                 **kwargs):
        """
        Constructor.

        keyword Args:
            model (Optional[ui.AbstractValueModel]): Model for selected state, defaults to none.
            delegate (Optional[ui.MenuDelegate]): Menu item delegate, defaults to None means using ViewportMenuDelegate.
            hide_on_click (bool): Hide menu when radio menu item clicked, defaults to False.
            toggle (bool): Whether this item can be toggled to (on/off) or always triggers on, defaults to True
            triggered_fn (callable): Callback when menu item clicked, defaults to None.
            trigger_will_set_model (bool): Update selected state model when menu item clicked, defaults to False.
            For other kwargs, please refer to ui.MenuItem
        """
        if model is None:
            model = ui.SimpleBoolModel()
        if delegate is None:
            delegate = ViewportMenuDelegate()

        self._triggered_fn = triggered_fn
        self.__trigger_will_set_model = trigger_will_set_model

        kwargs['triggered_fn'] = self._on_triggered
        if toggle:
            kwargs['selected'] = kwargs.get('selected', model.as_bool)
        else:
            kwargs['checkable'] = kwargs.get('checkable', True)
            kwargs['checked'] = kwargs.get('checked', model.as_bool)

        super().__init__(
            name,
            delegate=delegate,
            hide_on_click=hide_on_click,
            **kwargs
        )
        self._sub = model.subscribe_value_changed_fn(self._on_value_changed)
        self.model = model
        self.__toggle = toggle

    def __del__(self):
        self.destroy()

    def destroy(self) -> None:
        """Release resources"""
        self.set_triggered_fn(None)
        model, self.model, self._sub = self.model, None, None
        if model and hasattr(model, 'destroy'):
            model.destroy()
        super().destroy()

    def _on_triggered(self) -> None:
        if not self.__trigger_will_set_model:
            if self.__toggle:
                self.model.set_value(not self.model.as_bool)
            else:
                self.model.set_value(True)
        if self._triggered_fn:
            self._triggered_fn()

    def _on_value_changed(self, model: ui.AbstractValueModel) -> None:
        # When value changed, update selected status
        value = model.as_bool
        attr_name = 'selected' if self.__toggle else 'checked'
        if getattr(self.delegate, attr_name) != value:
            setattr(self.delegate, attr_name, value)
