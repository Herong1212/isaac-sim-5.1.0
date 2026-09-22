import omni.ui as ui
from ..layer_model_utils import LayerModelUtils


class SaveModel(ui.AbstractValueModel):
    def __init__(self, layer_item):
        super().__init__()
        self._layer_item = layer_item
    
    def destroy(self):
        self._layer_item = None

    def get_value_as_bool(self):
        return self._layer_item.dirty or (self._layer_item.is_live_session_layer and self._layer_item.has_content)

    def set_value(self, value):
        if (
            value
            or not self._layer_item.dirty
            or self._layer_item.missing
            or not self._layer_item.editable
            or self._layer_item.is_live_session_layer
        ):
            return

        LayerModelUtils.save_layer(self._layer_item)
