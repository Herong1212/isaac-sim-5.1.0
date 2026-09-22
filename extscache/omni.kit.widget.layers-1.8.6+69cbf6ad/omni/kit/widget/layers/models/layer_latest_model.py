import omni.ui as ui
from ..layer_model_utils import LayerModelUtils


class LayerLatestModel(ui.AbstractValueModel):
    def __init__(self, usd_context, layer_item):
        super().__init__()
        self._usd_context = usd_context
        self._layer_item = layer_item

    def destroy(self):
        self._usd_context = None
        self._layer_item = None

    def get_value_as_bool(self):
        return not self._layer_item.latest

    def set_value(self, _):
        if not self._layer_item.latest:
            LayerModelUtils.reload_layer(self._layer_item)
