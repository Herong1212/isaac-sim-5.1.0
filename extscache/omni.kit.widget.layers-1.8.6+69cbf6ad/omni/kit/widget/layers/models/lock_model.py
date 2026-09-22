import omni.ui as ui
from ..layer_model_utils import LayerModelUtils


class LockModel(ui.AbstractValueModel):
    def __init__(self, layer_item):
        super().__init__()
        self._layer_item = layer_item
    
    def destroy(self):
        self._layer_item = None

    def get_value_as_bool(self):
        return self._layer_item.locked

    def set_value(self, value):
        LayerModelUtils.lock_layer(self._layer_item, value)
