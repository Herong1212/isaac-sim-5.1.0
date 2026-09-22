# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the BundlePropertyWidgets class for registering and managing custom property widgets in the Omniverse Kit application."""


import omni.kit.app
import omni.usd

from .geom_scheme_delegate import GeomPrimSchemeDelegate
from .material_scheme_delegate import MaterialPrimSchemeDelegate, ShaderPrimSchemeDelegate
from .path_scheme_delegate import PathPrimSchemeDelegate


class BundlePropertyWidgets(omni.ext.IExt):
    """A class for registering and managing property widgets in an application.

    This class is designed to interface with the application's property window, registering various schemes and their corresponding delegates to handle different types of property widgets. It manages the lifecycle of these widgets by providing methods for their registration on startup and unregistration on shutdown. The class ensures that property widgets for geometry, materials, paths, shaders, physics, and animation graphs are made available within the application's user interface, allowing users to interact with different aspects of a scene or object properties.
    """

    def __init__(self):
        """Initializes the bundle property widgets."""
        self._registered = False
        super().__init__()

    def on_startup(self, ext_id):
        """Called when the extension is started up.

        Args:
            ext_id (str): The ID of the extension being started."""
        self._register_widget()

    def on_shutdown(self):
        """Called when the extension is shutting down."""
        self._unregister_widget()

    def _register_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        w.register_scheme_delegate("prim", "xformable_prim", GeomPrimSchemeDelegate())
        w.register_scheme_delegate("prim", "path_prim", PathPrimSchemeDelegate())
        w.register_scheme_delegate("prim", "material_prim", MaterialPrimSchemeDelegate())
        w.register_scheme_delegate("prim", "shade_prim", ShaderPrimSchemeDelegate())
        physics_widgets = [
            "physics_components",
            "physics_prim",
            "joint_prim",
            "vehicle_prim",
            "physics_material",
            "custom_properties",
        ]
        anim_graph_widgets = ["anim_graph", "anim_graph_node"]
        w.set_scheme_delegate_layout(
            "prim",
            [
                "path_prim",
                "basis_curves_prim",
                "point_instancer_prim",
                "material_prim",
                "xformable_prim",
                "shade_prim",
                "audio_settings",
            ]
            + physics_widgets
            + anim_graph_widgets,
        )

    def _unregister_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        w.reset_scheme_delegate_layout("prim")
        w.unregister_scheme_delegate("prim", "xformable_prim")
        w.unregister_scheme_delegate("prim", "path_prim")
        w.unregister_scheme_delegate("prim", "material_prim")
        w.unregister_scheme_delegate("prim", "shade_prim")
