"""This module provides the LightPropertyExtension class for adding a custom light properties widget to the Omniverse Kit."""

import omni.ext
import omni.kit.app
from pxr import Usd, UsdLux


class LightPropertyExtension(omni.ext.IExt):
    """A class that extends the Omniverse Kit by registering a custom widget for light properties.

    This class is an extension for the Omniverse Kit, designed to enhance the user interface by adding a custom widget that allows for easy manipulation of light properties in a 3D scene. It leverages USD and UsdLux for defining and managing these properties. Upon startup, the class registers the widget and sets up a path for test data. On shutdown, it ensures the widget is properly unregistered.

    It is important to note that the visibility of this widget is contingent on the presence of the property window within the Omniverse Kit. The widget is specifically tailored for light primitives and includes a comprehensive set of light attributes for various light types supported by UsdLux. The class also handles version-specific features of USD, ensuring compatibility across different versions of the software.
    """

    def __init__(self):
        """Initializes the LightPropertyExtension."""
        self._registered = False
        super().__init__()

    def on_startup(self, ext_id):
        """This method is called when the extension is started.

        Args:
            ext_id (str): The ID of the extension being started."""
        self._register_widget()

    def on_shutdown(self):
        """Cleans up resources and unregisters widgets before the extension shuts down."""
        if self._registered:
            self._unregister_widget()

    def _register_widget(self):
        import omni.kit.window.property as p

        from .prim_light_widget import LightSchemaAttributesWidget

        w = p.get_window()
        if w:

            # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
            w.register_widget(
                "prim",
                "light",
                LightSchemaAttributesWidget(
                    "Light",
                    # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
                    UsdLux.LightAPI if hasattr(UsdLux, "LightAPI") else UsdLux.Light,
                    [
                        UsdLux.CylinderLight,
                        UsdLux.DiskLight,
                        UsdLux.DistantLight,
                        UsdLux.DomeLight,
                        UsdLux.GeometryLight,
                        UsdLux.RectLight,
                        UsdLux.SphereLight,
                        UsdLux.ShapingAPI,
                        UsdLux.ShadowAPI,
                        UsdLux.LightFilter,
                        # https://github.com/PixarAnimationStudios/USD/commit/9eda37ec9e1692dd290efd9a26526e0d2c21bb03
                        UsdLux.PortalLight if hasattr(UsdLux, "PortalLight") else UsdLux.LightPortal,
                        UsdLux.ListAPI,
                    ],
                    [
                        "color",
                        "enableColorTemperature",
                        "colorTemperature",
                        "intensity",
                        "exposure",
                        "normalize",
                        "angle",
                        "radius",
                        "height",
                        "width",
                        "radius",
                        "length",
                        "texture:file",
                        "texture:format",
                        "diffuse",
                        "specular",
                        "shaping:focus",
                        "shaping:focusTint",
                        "shaping:cone:angle",
                        "shaping:cone:softness",
                        "shaping:ies:file",
                        "shaping:ies:angleScale",
                        "shaping:ies:normalize",
                        "collection:shadowLink:expansionRule",
                        "collection:shadowLink:excludes",
                        "collection:shadowLink:includes",
                        "collection:lightLink:expansionRule",
                        "collection:lightLink:excludes",
                        "collection:lightLink:includes",
                        "light:enableCaustics",
                        "visibleInPrimaryRay",
                        "disableFogInteraction",
                        "isProjector",
                    ]  # https://github.com/PixarAnimationStudios/USD/commit/c8cd344af6be342911e50d2350c228ed329be6b2
                    # USD v22.08 adds this to LightAPI as an API schema override of CollectionAPI
                    + (["collection:lightLink:includeRoot"] if Usd.GetVersion() >= (0, 22, 8) else []),
                    [
                        "collection:lightLink",
                        "collection:lightLink:membershipExpression",
                        "collection:shadowLink",
                        "collection:shadowLink:membershipExpression",
                    ],
                    [
                        "CylinderLight",
                        "DiskLight",
                        "DistantLight",
                        "DomeLight",
                        "GeometryLight",
                        "RectLight",
                        "SphereLight",
                        "ShapingAPI",
                        "ShadowAPI",
                        "LightFilter",
                        "PortalLight" if hasattr(UsdLux, "PortalLight") else "LightPortal",
                        "ListAPI",
                    ],
                ),
            )
            self._registered = True

    def _unregister_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        if w:
            w.unregister_widget("prim", "light")
            self._registered = False
