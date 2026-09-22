import omni.kit.app

def is_material_graph_editor_available(featureCustomNode: bool = True) -> bool:
    """Check if the MDL Material Graph extensions is available

    Args:
        featureCustomNode: the material graph extension supports registration and deregistration of custom nodes.

    Returns:
        True if the extension and the selected feature(s) are available.
    """
    available: bool = False
    try:
        # check if the extension is enabled
        if omni.kit.app.get_app().get_extension_manager().get_enabled_extension_id("omni.kit.window.material_graph"):
            # load the module to be able to inspect it
            from omni.kit.window.material_graph.shader_registry import ShaderRegistry
            available = True
            # check the availablity of the features
            if featureCustomNode:
                available &= callable(getattr(ShaderRegistry().Get("mdl"), "register_node_by_asset_and_id", None))
    except Exception:
        available = False
    return available


class MaterialGraphEditor():
    registered_nodes: list[tuple[str, str]] = []

    def is_available(self) -> bool:
        """Check if the material graph extension is installed in the required version"""
        return is_material_graph_editor_available(featureCustomNode=True)

    def register_node(self, sourceAsset: str, subIdentifier: str, category: str = "") -> bool:
        """
        Add a node to the material graph node list.

        Note, that `reload_node_list` has to be called to update the node list shown in the editor.
        """

        # note, that the extension could be unloaded at any point in time
        if self.is_available():
            from omni.kit.window.material_graph.shader_registry import ShaderRegistry
            shader_graph_registry: ShaderRegistry = ShaderRegistry().Get("mdl")

            # add one of the modules materials (the rough and smooth ones will not show)
            if shader_graph_registry.register_node_by_asset_and_id(sourceAsset, subIdentifier, category):
                self.registered_nodes.append((sourceAsset, subIdentifier))
                return True
        return False

    def deregister_node(self, sourceAsset: str, subIdentifier: str) -> bool:
        """
        Remove a node from the material graph node list.

        Note, that `reload_node_list` has to be called to update the node list shown in the editor.
        """

        # note, that the extension could be unloaded at any point in time
        if self.is_available():
            from omni.kit.window.material_graph.shader_registry import ShaderRegistry
            shader_graph_registry: ShaderRegistry = ShaderRegistry().Get("mdl")

            # add one of the modules materials (the rough and smooth ones will not show)
            key: tuple[str, str] = (sourceAsset, subIdentifier)
            if shader_graph_registry.deregister_node_by_asset_and_id(sourceAsset, subIdentifier):
                if key in self.registered_nodes:
                    self.registered_nodes.remove(key)
                return True
        return False

    def deregister_nodes(self):
        """remove all nodes registered using this object."""
        # note, that the extension could be unloaded at any point in time
        if self.is_available():
            from omni.kit.window.material_graph.shader_registry import ShaderRegistry
            shader_graph_registry: ShaderRegistry = ShaderRegistry().Get("mdl")

            to_remove: list[tuple[str, str]] = self.registered_nodes.copy()
            for entry in to_remove:
                if shader_graph_registry.deregister_node_by_asset_and_id(entry[0], entry[1]):
                    self.registered_nodes.remove(entry)
        return len(self.registered_nodes) == 0

    async def reload_node_list(self):
        """Update the node list shown in the editor."""

        # note, that the extension could be unloaded at any point in time
        if self.is_available():
            from omni.kit.window.material_graph.shader_registry import ShaderRegistry
            await ShaderRegistry().Get("mdl").reload()  # reload required after adding/removing nodes
