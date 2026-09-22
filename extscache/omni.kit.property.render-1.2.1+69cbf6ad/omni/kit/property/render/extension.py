# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ext


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class RenderPropertiesExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self.__wg_registered = False

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        self.__wg_registered = False
        # Register custom UI for Property widget
        self.__register_widgets()

    def on_shutdown(self):
        self.__unregister_widgets()

    def __register_widgets(self):
        import omni.kit.window.property as p
        from omni.kit.property.usd.usd_property_widget import MultiSchemaPropertiesWidget
        from pxr import UsdRender

        from .product_schema import ProductSchemaAttributesWidget

        w = p.get_window()
        if w:
            self.__wg_registered = True
            w.register_widget(
                "prim",
                "rendersettings_base",
                MultiSchemaPropertiesWidget(
                    "Render Settings", UsdRender.Settings, [UsdRender.SettingsBase], group_api_schemas=True
                ),
            )
            w.register_widget(
                "prim",
                "renderproduct_base",
                ProductSchemaAttributesWidget(
                    "Render Product",
                    UsdRender.Product,
                    [UsdRender.SettingsBase],
                    include_list=["camera", "orderedVars"],
                    exclude_list=[
                        "aspectRatioConformPolicy",
                        "dataWindowNDC",
                        "instantaneousShutter",
                        "pixelAspectRatio",
                        "productName",
                        "productType",
                    ],
                    group_api_schemas=True,
                ),
            )
            w.register_widget(
                "prim",
                "rendervar_base",
                MultiSchemaPropertiesWidget("Render Var", UsdRender.Var, [UsdRender.Var], group_api_schemas=True),
            )

    def __unregister_widgets(self):
        if self.__wg_registered:
            import omni.kit.window.property as p

            w = p.get_window()
            if w:
                w.unregister_widget("prim", "rendersettings_base")
                w.unregister_widget("prim", "renderproduct_base")
                w.unregister_widget("prim", "rendervar_base")
                self.__wg_registered = False
