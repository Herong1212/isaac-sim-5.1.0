"""Utilities for managing OmniGraph Python node registration"""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path

import omni.graph.tools._internal as ogi

from ._registration.register_python_ogn import register_python_ogn


# ================================================================================
class PythonNodeRegistration:
    """Scoped object to register and deregister Python nodes as their extension is started up and shut down.
    This will be created and destroyed automatically by OmniGraph and does not need to be explicitly managed.
    Attributes:
        _ext_name: Name of the extension for which this object is handling registrations
        _deregistration_methods: Dictionary of NodeTypeName:DeregistrationFunction for each node type in the extension
    """

    def __init__(self, ext_name: str, module_name: str, ext_path: Path, autonode_config: dict[str, any] = None):
        """Save the information required to deregister the nodes when the module is shut down
        Args:
            ext_name: Name of the extension being registered
            module_name: Name of the Python module associated with the extension
            ext_path: Path to the extension's import module
            autonode_config: Extra configuration for AutoNode from the .toml file - None means no mention of it there
            or that calls here predate the addition of this parameter.
        Raises:
            ogi.OmniGraphExtensionError if no nodes were found
        """
        _ = ogi.LOG.disabled or ogi.LOG.info(
            "Registering nodes in %s imported as %s with AutoNode config %s",
            ext_path,
            module_name,
            autonode_config,
        )
        self._ext_name: str = ext_name
        self.__deregistration_methods: dict[str, callable] = {}
        if ext_path is not None:
            self.__deregistration_methods = register_python_ogn(ext_name, module_name, ext_path)
        else:
            _ = ogi.LOG.disabled or ogi.LOG.info("Failed to find module location")
        if not self.__deregistration_methods:
            raise ogi.OmniGraphExtensionError("No nodes in this module, do not remember it")

    def __del__(self):
        """In case the object is going away before deregister was explicitly called"""
        _ = ogi.LOG.disabled or ogi.LOG.info("Destroying registration record for %s", self._ext_name)
        if self.__deregistration_methods:
            self.deregister()

    def deregister(self):
        """Deregister all of the remembered nodes"""
        with suppress(AttributeError):
            _ = ogi.LOG.disabled or ogi.LOG.info("Deregistering Python node types in %s", self._ext_name)
            for node_type_name, deregistration_fn in self.__deregistration_methods.items():
                _ = ogi.LOG.disabled or ogi.LOG.info("    --> node type %s", node_type_name)
                deregistration_fn()
        self.__deregistration_methods = {}
