# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines the MaterialPropertyExtension which extends the OmniKit Editor by managing custom UI widgets for editing USD shade attributes and materials."""

__all__ = ["MaterialPropertyExtension"]

import omni.ext


class MaterialPropertyExtension(omni.ext.IExt):
    """A class that extends the OmniKit Editor by registering and managing custom widgets related to material properties.

    This extension is responsible for adding custom UI elements to the Properties Window within the OmniKit environment, specifically tailored for editing USD shade attributes and materials. It ensures the proper registration and unregistration of these widgets during the extension's startup and shutdown lifecycle events.
    """

    def __init__(self):
        """Initializes the extension and sets up necessary properties."""
        super().__init__()
        self._registered = False

    def on_startup(self, ext_id):
        """Called when the extension is started.

        Args:
            ext_id (str): The ID of the extension being started."""
        self._register_widgets(ext_id)

    def on_shutdown(self):  # pragma: no cover
        """Called when the extension is being shut down."""
        if self._registered:
            self._unregister_widgets()

    def _register_widgets(self, ext_id):
        import omni.kit.window.property as window_property

        from .widgets import (
            MaterialBindingWidget,
            UsdShadeAttributeWidget,
            UsdShadeMaterialWidget,
            UsdShadeNodeGraphWidget,
            UsdShadeShaderWidget,
            UsdUIBackdropWidget,
        )

        window = window_property.get_window()
        if window:
            extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)

            # Setup the default extension path for any file-resolution it needs to do
            #
            assert bool(extension_path)
            MaterialBindingWidget.EXTENSION_PATH = extension_path

            # Register custom attribute widget to modify display of UsdShade Raw Properties.
            window.register_widget(
                "prim",
                "attribute",
                UsdShadeAttributeWidget(title="Raw USD Properties", collapsed=True, enable_adapter=True),
                False,
            )

            window.register_widget("prim", "backdrop", UsdUIBackdropWidget())

            window.register_widget("prim", "material", UsdShadeMaterialWidget())

            window.register_widget(
                "prim", "material_binding", MaterialBindingWidget(extension_path=extension_path, add_context_menu=True)
            )

            window.register_widget("prim", "nodegraph", UsdShadeNodeGraphWidget())

            window.register_widget("prim", "shader", UsdShadeShaderWidget())

            self._registered = True

    def _unregister_widgets(self):  # pragma: no cover
        import omni.kit.window.property as window_property
        from omni.kit.property.usd.usd_property_widget import RawUsdPropertiesWidget

        if self._registered:
            window = window_property.get_window()

            if window:
                # Restore original attribute widget on close.
                window.register_widget(
                    "prim",
                    "attribute",
                    RawUsdPropertiesWidget(title="Raw USD Properties", collapsed=True, enable_adapter=True),
                    False,
                )

                window.unregister_widget("prim", "backdrop")
                window.unregister_widget("prim", "material")
                window.unregister_widget("prim", "material_binding")
                window.unregister_widget("prim", "nodegraph")
                window.unregister_widget("prim", "shader")

            self._registered = False
