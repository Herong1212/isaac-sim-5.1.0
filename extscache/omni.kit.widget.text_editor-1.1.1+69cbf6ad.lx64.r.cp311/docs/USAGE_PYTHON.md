# Usage Examples

## Create a Basic Text Editor

```python
import omni.ui as ui
from omni.kit.widget.text_editor import TextEditor

# Create a window
window = ui.Window("Text Editor Example", width=600, height=400)

# Add a TextEditor to the window with simple text content
with window.frame:
    text_editor = TextEditor(text="Hello, this is a simple text editor example.")
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.text_editor/data/docs_images/usage_preview.png
---
align: center
---
```

---

## Create Text Editor with Multiple Lines

```python
import omni.ui as ui
from omni.kit.widget.text_editor import TextEditor

# Create a window
window = ui.Window("Multi-line Text Editor", width=600, height=400)

# Create a list of text lines
lines = ["The quick brown fox jumps over the lazy dog."] * 5

# Add a TextEditor with multiple lines
with window.frame:
    text_editor = TextEditor(text_lines=lines)
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.text_editor/data/docs_images/create_text_editor_with_multiple_lines.png
---
align: center
---
```

---

## Enable Syntax Highlighting for Code

```python
import omni.ui as ui
from omni.kit.widget.text_editor import TextEditor

# Create a window
window = ui.Window("Python Code Editor", width=600, height=400)

# Python code sample
python_code = [
    "def fibonacci(n):",
    "    if n <= 1:",
    "        return n",
    "    else:",
    "        return fibonacci(n-1) + fibonacci(n-2)",
    "",
    "# Calculate the first 10 Fibonacci numbers",
    "for i in range(10):",
    "    print(fibonacci(i))"
]

# Add a TextEditor with Python syntax highlighting
with window.frame:
    text_editor = TextEditor(
        text_lines=python_code,
        syntax=TextEditor.Syntax.PYTHON  # Enable Python syntax highlighting
    )
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.text_editor/data/docs_images/enable_syntax_highlighting_for_code.png
---
align: center
---
```

---

## Detect Text Changes with Callback

```python
import omni.ui as ui
from omni.kit.widget.text_editor import TextEditor

# Create a window
window = ui.Window("Text Change Detection", width=600, height=400)

# Create layout with TextEditor and controls
with window.frame:
    with ui.VStack():
        # Create the text editor
        text_editor = TextEditor(text="Edit this text to see change detection in action.")
        
        # Status label to show text change state
        status_label = ui.Label("Text status: unchanged")
        
        # Function to handle text changes
        def on_text_changed(text_changed):
            if text_changed:
                status_label.text = "Text status: modified"
            else:
                status_label.text = "Text status: unchanged"
        
        # Register the callback for text changes
        text_editor.set_edited_fn(on_text_changed)
        
        # Button to programmatically set text (won't trigger the callback)
        def reset_text():
            text_editor.text = "Edit this text to see change detection in action."
            status_label.text = "Text status: reset programmatically"
            
        ui.Button("Reset Text", clicked_fn=reset_text)
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.text_editor/data/docs_images/detect_text_changes_with_callback.png
---
align: center
---
```

