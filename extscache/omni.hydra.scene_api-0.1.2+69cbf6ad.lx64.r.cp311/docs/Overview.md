```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

This extension provides a scene delegate that can load in the background, and also python APIs for adding and removing those scene delegates.

Here is an example of how to add and remove a delegate:

```python
from omni.hydra.scene_api import add_background_loading_hydra_scene_delegate, remove_hydra_scene_delegate

add_background_loading_hydra_scene_delegate('myuniquename', '/path/to/file.usd')
remove_hydra_scene_delegate('myuniquename')
```

Note that name needs to follow usd identifier rules, like a prim name.