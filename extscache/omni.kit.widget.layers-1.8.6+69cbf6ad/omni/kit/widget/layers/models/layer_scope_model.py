import omni.ui as ui


class LayerScopeModel(ui.AbstractValueModel):
    def __init__(self, layer_model):
        super().__init__()
        self._layer_model = layer_model
    
    def destroy(self):
        self._layer_model = None

    def get_value_as_bool(self):
        # False means local mode
        return self._layer_model.global_muteness_scope

    def set_value(self, value):
        self._layer_model.global_muteness_scope = value
