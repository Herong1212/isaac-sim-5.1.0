# omni.kit.viewport.menubar.display
Display setting of a Menu-Bar in the viewport

To add custom display settings, try the following:

```python
import omni.ui as ui
import omni.kit.viewport.menubar.core
import omni.kit.viewport.menubar.display
from omni.kit.viewport.menubar.core import CategoryCollectionItem, CategoryCustomItem, CategoryStateItem, SelectableMenuItem

def _build_menu():
  with ui.Menu("Attachments", delegate=ViewportMenuDelegate()):
    ui.MenuItem("None")
    ui.MenuItem("Selected")
    ui.MenuItem("All")

inst = omni.kit.viewport.menubar.display.get_instance()
physics_item = CategoryCollectionItem(
  "Physics",
  [
    CategoryStateItem("Joints", ui.SimpleBoolModel(True)),
    CategoryCustomItem("Attachments", _build_menu)
  ]
)
inst.register_custom_category_item("Show By Type", physics_item)
```

Built in categories include `"Heads Up Display"`, `"Show By Type"` and `"Show By Purpose"`, but custom categories can
also be created. Optionally a custom section can also be specified which will add a labeled separator before the top
level categories in that section. Also, shown_changed_fn callback can now be registered in CategoryCollectionItem.

```python
category = "Draw Overlay"
section = "Selection Display"

def on_shown(s):
    print("on_shown: {s}")

overlay_item = CategoryCollectionItem(
  category,
  [
    CategoryCustomItem("Points", lambda: SelectableMenuItem("Points", model=ui.SimpleBoolModel())),
    CategoryCustomItem("Normals", lambda: SelectableMenuItem("Normals", model=ui.SimpleBoolModel()))
  ],
  shown_changed_fn=on_shown
)

inst.register_custom_category_item(category, overlay_item, section)
```
