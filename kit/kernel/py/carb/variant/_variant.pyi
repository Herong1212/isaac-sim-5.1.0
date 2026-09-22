from __future__ import annotations
import carb.variant._variant
import typing

__all__ = [
    "IVariant",
    "acquire_variant_interface"
]


class IVariant():
    pass
def acquire_variant_interface(plugin_name: str = None, library_path: str = None) -> IVariant:
    pass
