from pathlib import Path

import carb
import carb.tokens
import omni.ext
from pxr import Plug


def register_sequencer_plugins() -> bool:
    tokenizer = carb.tokens.get_tokens_interface()
    ext_root = Path(tokenizer.resolve("${omni.usd.schema.sequence}"))
    sequence_schema_path = ext_root / "_usd_sequence_schema" / "plugins" / "sequenceSchema" / "resources"

    if not sequence_schema_path.exists():
        carb.log_error(f"Sequence Schema path does not exist: {sequence_schema_path}")
        return False

    Plug.Registry().RegisterPlugins(str(sequence_schema_path))
    return True


class SequenceSchemaExt(omni.ext.IExt):
    _SINGLETON = None

    def __init__(self) -> None:
        super().__init__()
        self._plugins_registered = False

    def on_startup(self, ext_id: str):
        SequenceSchemaExt._SINGLETON = self
        self._plugins_registered = register_sequencer_plugins()

    @property
    def plugins_registered(self):
        return self._plugins_registered


def get_instance() -> SequenceSchemaExt:
    return SequenceSchemaExt._SINGLETON
