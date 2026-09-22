import omni.ui as ui


class LayerLiveUpdateModel(ui.AbstractValueModel):
    def __init__(self, usd_context, layer_item):
        super().__init__()
        self._usd_context = usd_context
        self._layer_item = layer_item
    
    def destroy(self):
        self._usd_context = None
        self._layer_item = None

    def get_value_as_bool(self):
        return self._layer_item.is_in_live_session

    def set_value(self, value):
        pass
        
