import omni.ui as ui


class LayerNameModel(ui.AbstractValueModel):
    def __init__(self, layer_item):
        super().__init__()
        self._layer_item = layer_item
    
    def destroy(self):
        self._layer_item = None

    def get_value_as_string(self):
        if not self._layer_item.model.normal_mode and self._layer_item.edit_layer_in_auto_authoring_mode:
            return self._layer_item.name + " (Default Layer)"
        elif self._layer_item.model.normal_mode and self._layer_item.is_edit_target:
            return self._layer_item.name + " (Authoring Layer)"
        else:
            return self._layer_item.name

    def set_value(self, value):
        # Cannot change layer name
        pass
