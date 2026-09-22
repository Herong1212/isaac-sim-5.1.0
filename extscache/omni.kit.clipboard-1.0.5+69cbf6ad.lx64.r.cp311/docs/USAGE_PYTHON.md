```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Copy String to Clipboard

```python
from omni.kit.clipboard import copy

# Copy a string into the system clipboard
text_to_copy = "Hello, Clipboard!"
copy(text_to_copy)
```

## Paste String from Clipboard

```python
from omni.kit.clipboard import paste

# Paste a string from the system clipboard
pasted_text = paste()
print(f"Text pasted from clipboard: '{pasted_text}'")
```