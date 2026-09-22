```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

This extension provides a collection of utility functions and actions to manage USD files, including creating, opening, saving and closing.

 Here is an example of implementing menu click actions to open and save files easily with this extension.

```
with ui.Menu("File"):
      ui.MenuItem(
         "Load",
         triggered_fn=lambda: omni.kit.window.file.open()
      )
      ui.MenuItem(
         "Save",
         triggered_fn=lambda: omni.kit.window.file.save(dialog_options=DialogOptions.HIDE),
      )
```

For a detailed usage on how to use actions please refer to:
```{eval-rst}
.. raw:: html

   <a href="../../omni.kit.actions.core/latest/index.html">Actions Overview</a>
```