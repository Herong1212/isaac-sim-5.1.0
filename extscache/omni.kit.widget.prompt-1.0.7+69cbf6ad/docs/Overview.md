```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The widget extension provides a simple dialog for prompt.  
Users have the ability to customize buttons on it.

```{image} ../../../../source/extensions/omni.kit.widget.prompt/data/preview.png
---
align: center
---
```

## Quickstart

```
    prompt = Prompt("title", "message to user", on_closed_fn=lambda: print("prompt close"))
    prompt.show()
```
## Customizing the Prompt

You can customize these parts of the Prompt.

*  title: Text appearing in the titlebar of the window.
*  text: Text of the question being posed to the user.
*  ok_button_text: Text for the first button.
*  cancel_button_text: Text for the last button.
*  middle_button_text: Text for the middle button.
*  middle_button_2_text: Text for the second middle button.
*  ok_button_fn: Function executed when the first button is pressed.
*  cancel_button_fn: Function executed when the last button is pressed.
*  middle_button_fn: Function executed when the middle button is pressed.
*  middle_2_button_fn: Function executed when the second middle button is pressed.
*  modal: True if the window is modal, shutting down other UI until an answer is received
*  on_closed_fn: Function executed when the window is closed without hitting a button.
*  shortcut_keys: If it can be confirmed or hidden with shortcut keys like Enter or ESC.
*  width: The specified width. 
*  height: The specified height.

## Example
```
from omni.kit.widget.prompt import Prompt

folder_exist_popup = None

def on_confirm():
    print("overwrite the file")

def on_cancel():
    folder_exist_popup.hide()
    folder_exist_popup = None

folder_exist_popup = Prompt(
    title="Overwrite",
    text="The file already exists, are you sure you want to overwrite it?",
    ok_button_text="Overwrite",
    cancel_button_text="Cancel",
    ok_button_fn=on_confirm,
    cancel_button_fn=on_cancel,
)

folder_exist_popup.show()

```



