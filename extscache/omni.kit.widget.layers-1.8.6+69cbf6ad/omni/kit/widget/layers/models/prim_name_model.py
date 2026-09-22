import omni
import weakref
import omni.ui as ui


class PrimNameModel(ui.AbstractValueModel):
    def __init__(self, prim_item):
        super().__init__()
        self._prim_item = prim_item
    
    def destroy(self):
        self._prim_item = None   

    def get_value_as_string(self):
        return self._prim_item.name

    def set_value(self, value):
        # Cannot change layer name
        pass
