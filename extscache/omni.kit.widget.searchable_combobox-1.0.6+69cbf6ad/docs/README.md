# Searchable ComboBox widget


To use:

```
from omni.kit.widget.searchable_combobox import build_searchable_combo_widget

def on_combo_click_fn(model):
    component = model.get_value_as_string()
    print(f"{component} selected")

component_list = ['3d Reconstruction', 'AEC Experience', 'AI Framework', 'AI Toybox', 'AR Experience', 'ArtTech', 'Asset Converter Service', 'Asset Management', 'Physics Research', 'PhysX Third Party Integrations', 'Pinocchio', 'PLC', 'Point Clouds', 'Pose Tracker', 'QA Builds', 'QA Needs Repro', 'Repo Tools', 'Reshade', 'Resolvers', 'RTX', 'RTX Hydra', 'RTX MGPU', 'RTX Renderer', 'Sample Content', 'SDG', 'Sequencer', 'Server Installer', 'Showroom', 'Synthetic Data', 'USD', 'USD Delta Library', 'USD Hydra', 'Kit', 'USDRT', 'UX', 'UX / UI', 'Virtual Production', 'XR']
component_index = -1
self._component_combo = build_searchable_combo_widget(component_list, component_index, on_combo_click_fn, widget_height=18, default_value="Kit")
```

Get combo widget value:

```
component_name = self._component_combo.get_text()
```

Set combo widget value:

```
self._component_combo.set_text("Showroom")
```

Cleanup:

```
self._component_combo.destroy()
self._component_combo = None
```