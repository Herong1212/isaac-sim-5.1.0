# Option Menu

To use:

```
from omni.kit.widget.options_menu import OptionsMenu, OptionItem

model = OptionsModel(
    "Filter",
    [
        OptionItem("audio", text="Audio"),
        OptionItem("materials", text="Materials"),
        OptionItem("scripts", text="Scripts"),
        OptionItem("textures", text="Textures"),
        OptionItem("usd", text="USD"),
    ]
)

menu = OptionsMenu(model)
menu.show()
```
