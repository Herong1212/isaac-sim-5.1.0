# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["AutoAuthoring"]

from .._omni_kit_usd_layers import acquire_auto_authoring_interface, release_auto_authoring_interface, ILayersInstance


class AutoAuthoring:
    """
    (Experimental) USD supports switching edit targets so that all authoring will take place in that specified layer. When it's working
    with multiple sublayers, this kind of freedom may cause experience issues. The user has to be aware the changes made are
    not overridden in any stronger layer. We extend a new mode called Auto Authoring to improve it. In this mode, all
    changes will firstly go into a middle delegate layer and it will then distribute edits (per frame) into their
    corresponding layers where the edits have the strongest opinions. So it cannot switch edit targets freely,
    and users do not need to be aware of the existence of multi-sublayers and how USD will compose the changes.
    """

    def __init__(self, layers_instance: ILayersInstance, usd_context) -> None:
        self._layers_instance = layers_instance
        self._usd_context = usd_context
        self._auto_authoring_interface = acquire_auto_authoring_interface()

    @property
    def usd_context(self):
        return self._usd_context

    def _destroy(self):
        self._layers_instance = None
        release_auto_authoring_interface(self._auto_authoring_interface)

    def is_enabled(self) -> bool:
        """Checks if UsdContext is in Auto Authoring mode."""

        return self._auto_authoring_interface.is_enabled(self._layers_instance)

    def set_default_layer(self, layer_identifier: str):
        """Sets the default layer to receive the newly created opinions."""

        self._auto_authoring_interface.set_default_layer(self._layers_instance, layer_identifier)

    def get_default_layer(self) -> str:
        """Gets the default layer."""

        return self._auto_authoring_interface.get_default_layer(self._layers_instance)

    def is_auto_authoring_layer(self, layer_identifier: str) -> bool:
        """Checks if a layer is an auto authoring layer."""

        return self._auto_authoring_interface.is_auto_authoring_layer(self._layers_instance, layer_identifier)
