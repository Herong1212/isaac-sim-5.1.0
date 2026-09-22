

class LayerGlobals:
    _missing_layer_map = set([])

    @staticmethod
    def on_stage_attached(stage):
        pass

    @staticmethod
    def on_stage_detached():
        pass

    @staticmethod
    def is_layer_missing(layer_identifier: str) -> bool:
        return layer_identifier in LayerGlobals._missing_layer_map

    @staticmethod
    def add_missing_layer(layer_identifier: str):
        LayerGlobals._missing_layer_map.add(layer_identifier)
