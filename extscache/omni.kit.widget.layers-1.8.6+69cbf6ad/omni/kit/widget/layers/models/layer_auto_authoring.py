import omni.ui as ui
from ..layer_model_utils import LayerModelUtils


class LayerAutoAuthoringModel(ui.AbstractValueModel):
    def __init__(self, layer_model):
        super().__init__()
        self._layer_model = layer_model
    
    def destroy(self):
        self._layer_model = None

    def get_value_as_bool(self):
        # False means local mode
        return self._layer_model.auto_authoring_mode

    def set_value(self, value):
        LayerModelUtils.set_auto_authoring_mode(self._layer_model, value)
