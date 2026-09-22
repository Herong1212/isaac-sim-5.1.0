# Public API for module omni.kit.property.layer:

## Classes

- class ModifyLayerMetadataCommand(omni.kit.commands.Command)
  - def __init__(self, layer_identifier, parent_layer_identifier, meta_index, value)
  - def do(self)
  - def undo(self)

- class ModifyStageAxisCommand(omni.kit.commands.Command)
  - def __init__(self, stage, axis)
  - def do(self)
  - def undo(self)

- class LayerPropertyWidgets(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

## Functions

- def get_instance()
