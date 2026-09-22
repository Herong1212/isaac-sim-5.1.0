import omni.ui as ui


class DisplayLayerModel(ui.SimpleBoolModel):
    def __init__(self, layer) -> None:
        self._layer = layer
        super().__init__()

    def get_value_as_bool(self) -> bool:
        return self._layer.visible

    def set_value(self, visible: bool):
        if visible != self._layer.visible:
            self._layer.visible = visible
            self._value_changed()

    def begin_edit(self) -> None:
        pass

    def end_edit(self) -> None:
        pass
