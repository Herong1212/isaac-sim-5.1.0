import omni.ui as ui
from ..layer_model_utils import LayerModelUtils


class SaveAllModel(ui.AbstractValueModel):
    def __init__(self, layer_model):
        super().__init__()
        self._layer_model = layer_model
    
    def destroy(self):
        self._layer_model = None

    def get_value_as_bool(self):
        return self._layer_model.has_dirty_layers()

    def set_value(self, value):
        if value:
            return

        LayerModelUtils.save_model(self._layer_model)
