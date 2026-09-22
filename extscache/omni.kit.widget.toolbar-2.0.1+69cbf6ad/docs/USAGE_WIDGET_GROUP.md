# WidgetGroup Usage Example

[WidgetGroup](omni.kit.widget.toolbar/omni.kit.widget.toolbar.WidgetGroup) is the base class you can override and put custom omni.ui widgets on the toolbar. [SimpleToolButton](omni.kit.widget.toolbar/omni.kit.widget.toolbar.SimpleToolButton) included in this extension is an example of how you can inherit and extent [WidgetGroup](omni.kit.widget.toolbar/omni.kit.widget.toolbar.WidgetGroup).

Here we provide another example showing how to create a custom by inheriting and overriding [WidgetGroup](omni.kit.widget.toolbar/omni.kit.widget.toolbar.WidgetGroup) class and its methods.

```python
from omni.kit.widget.toolbar import Hotkey, WidgetGroup

class DemoToolButtonGroup(WidgetGroup):
    """
    Example of how to create two ToolButton in one WidgetGroup
    """

    def __init__(self, icon_path):
        super().__init__()
        self._icon_path = icon_path

    def clean(self):
        self._sub1 = None
        self._sub2 = None
        self._hotkey.clean()
        self._hotkey = None
        super().clean()

    def get_style(self):
        style = {
            "Button.Image::test1": {"image_url": f"{self._icon_path}/plus.svg"},
            "Button.Image::test1:checked": {"image_url": f"{self._icon_path}/minus.svg"},
            "Button.Image::test2": {"image_url": f"{self._icon_path}/minus.svg"},
            "Button.Image::test2:checked": {"image_url": f"{self._icon_path}/plus.svg"},
        }
        return style

    def create(self, default_size):
        def on_value_changed(index, model):
            if model.get_value_as_bool():
                self._acquire_toolbar_context()
            else:
                self._release_toolbar_context()
            test_message_queue.append(f"Group button {index} clicked")

        button1 = ui.ToolButton(
            name="test1",
            width=default_size,
            height=default_size,
        )
        self._sub1 = button1.model.subscribe_value_changed_fn(lambda model, index=1: on_value_changed(index, model))

        button2 = ui.ToolButton(
            name="test2",
            width=default_size,
            height=default_size,
        )
        self._sub2 = button2.model.subscribe_value_changed_fn(lambda model, index=2: on_value_changed(index, model))

        self._hotkey = Hotkey(
            "toolbar::test2",
            Key.K,
            lambda: button2.model.set_value(not button2.model.get_value_as_bool()),
            lambda: self._is_in_context(),
        )

        # return a dictionary of name -> widget if you want to expose it to other widget_group
        return {"test1": button1, "test2": button2}
```

For examples of how to put this [WidgetGroup](omni.kit.widget.toolbar/omni.kit.widget.toolbar.WidgetGroup) onto a [Toolbar](omni.kit.widget.toolbar/omni.kit.widget.toolbar.Toolbar), check out [](USAGE_TOOLBAR).
