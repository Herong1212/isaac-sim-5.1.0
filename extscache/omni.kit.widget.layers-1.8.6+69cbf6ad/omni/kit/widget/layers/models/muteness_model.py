import weakref
import omni.ui as ui
import omni.kit.usd.layers as layers


class MutenessModel(ui.AbstractValueModel):
    def __init__(self, usd_context, layer_item, local: bool):
        super().__init__()
        self.local = local
        self._layer_item = layer_item
        self._usd_context = usd_context
    
    def destroy(self):
        self._layer_item = None
        self._usd_context = None

    def get_value_as_bool(self):
        if self.local:
            return self._layer_item.locally_muted
        else:
            return self._layer_item.globally_muted

    def set_value(self, value):
        self._layer_item.muted = value
