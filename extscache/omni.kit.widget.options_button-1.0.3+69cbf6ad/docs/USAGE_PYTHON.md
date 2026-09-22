# Usage Examples

## OptionsButton with OptionItems

```python
import omni.ui as ui
from omni.kit.widget.options_menu import OptionItem
from omni.kit.widget.options_button import OptionsButton

# Create a window to hold the OptionsButton
window = ui.Window("OptionsButton Example", width=300, height=200)

# Define OptionItems to display in the menu
option_items = [
    OptionItem("First Option"),
    OptionItem("Second Option"),
    OptionItem("Third Option"),
    OptionItem("More Options"),
]

# Create an OptionsButton with the defined OptionItems
with window.frame:
    options_button = OptionsButton(option_items)

# Access the OptionsModel associated with the OptionsButton
options_model = options_button.model

# Access the ui.Button used as the OptionsButton
options_ui_button = options_button.button

# Later in the code, when the OptionsButton is no longer needed, destroy it
options_button.destroy()
```
