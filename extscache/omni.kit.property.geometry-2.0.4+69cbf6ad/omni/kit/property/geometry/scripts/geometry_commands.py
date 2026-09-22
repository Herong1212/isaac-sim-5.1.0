from typing import Any, List, Optional

import carb
import omni.kit.commands
from pxr import Sdf, UsdGeom


class PrimVarCommand(omni.kit.commands.Command):
    """Set undoable primvar command.

    Args:
        prim_path (list): List of paths of prims.
        prim_name (str): Primvar name.
        prim_type (str): Primvar variable type (E.g. Sdf.ValueTypeNames.Bool).
        value (any): New primvar value. If primvar does not exist, it will be created.
        usd_context_name (Optional[str]): USD context name.
    """

    def __init__(
        self,
        prim_path: List[str],
        prim_name: str,
        prim_type: str,
        value: Any,
        usd_context_name: Optional[str] = "",
    ):
        """Initializes a PrimVarCommand instance for updating primvar values. Sets up internal state for execution."""
        self._prim_path = prim_path
        self._prim_name = prim_name
        self._prim_type = prim_type
        self._value = value
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._undo_values = {}

    def do(self):
        """Performs the update of primvar values on the specified prim paths and stores the original values for undo."""
        stage = self._usd_context.get_stage()
        for path in self._prim_path:
            if path:
                primvars_api = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath(path))
                value = primvars_api.GetPrimvar(self._prim_name)
                if value:
                    if value.GetTypeName() != self._prim_type:  # pragma: no cover
                        carb.log_error(
                            f"PrimVarCommand: cannot set value as {path}.{self._prim_name} is type {value.GetTypeName()} and expected type is {self._prim_type}"
                        )
                    else:
                        self._undo_values[str(path)] = value.Get()
                        value.Set(self._value)
                else:
                    self._undo_values[str(path)] = None
                    primvars_api.CreatePrimvar(self._prim_name, self._prim_type).Set(self._value)

    def undo(self):
        """Reverts the primvar values to their original state by using the stored undo information."""
        stage = self._usd_context.get_stage()
        for path, orig_value in self._undo_values.items():
            primvars_api = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath(path))
            value = primvars_api.GetPrimvar(self._prim_name)
            if orig_value:
                value.Set(orig_value)
            else:
                primvars_api.RemovePrimvar(self._prim_name)

        self._undo_values = {}


class TogglePrimVarCommand(omni.kit.commands.Command):
    """Toggle primvar undoable Command.

    Args:
        prim_path (list): List of paths of prims.
        prim_name (str): Primvar name.
        usd_context_name (str): USD context name.
    """

    def __init__(
        self,
        prim_path: List[str],
        prim_name: str,
        usd_context_name: Optional[str] = "",
    ):
        """Initializes the TogglePrimVarCommand which toggles a boolean primvar for the specified prims."""
        self._prim_path = prim_path
        self._prim_name = prim_name
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._undo_values = {}

    def do(self):
        """Executes the TogglePrimVarCommand, toggling the boolean primvar value for each prim."""
        stage = self._usd_context.get_stage()
        for path in self._prim_path:
            if path:
                primvars_api = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath(path))
                value = primvars_api.GetPrimvar(self._prim_name)
                if value:
                    if value.GetTypeName() != Sdf.ValueTypeNames.Bool:  # pragma: no cover
                        carb.log_error(
                            f"TogglePrimVarCommand: cannot set value as {value.GetTypeName()} isn't a {self._prim_type}"
                        )
                    else:
                        self._undo_values[str(path)] = value.Get()
                        value.Set(not value.Get())
                else:
                    self._undo_values[path] = None
                    primvars_api.CreatePrimvar(self._prim_name, Sdf.ValueTypeNames.Bool).Set(True)

    def undo(self):
        """Reverts the changes made by the TogglePrimVarCommand, restoring the original primvar values."""
        stage = self._usd_context.get_stage()
        for path, orig_value in self._undo_values.items():
            primvars_api = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath(path))
            value = primvars_api.GetPrimvar(self._prim_name)
            if orig_value:
                value.Set(orig_value)
            else:
                primvars_api.RemovePrimvar(self._prim_name)

        self._undo_values = {}


class ToggleInstanceableCommand(omni.kit.commands.Command):
    """Toggle instanceable undoable **Command**.

    Args:
        prim_path (list): List of paths of prims.
        usd_context_name (str, optional): USD context name. Defaults to ""
    """

    def __init__(
        self,
        prim_path: List[str],
        usd_context_name: Optional[str] = "",
    ):
        """Initializes a new ToggleInstanceableCommand. This command sets up the internal state to toggle the instanceable property for each prim in the provided prim_path."""
        self._prim_path = prim_path
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._undo_values = {}

    def do(self):
        """Executes the command by toggling the instanceable property of each prim specified in prim_path."""
        stage = self._usd_context.get_stage()
        for path in self._prim_path:
            if path:
                prim = stage.GetPrimAtPath(path)
                value = prim.IsInstanceable()
                self._undo_values[str(path)] = value
                prim.SetInstanceable(not value)

    def undo(self):
        """Reverses the command by restoring the original instanceable state for each prim in prim_path."""
        stage = self._usd_context.get_stage()
        for path, value in self._undo_values.items():
            prim = stage.GetPrimAtPath(path)
            prim.SetInstanceable(value)

        self._undo_values = {}
