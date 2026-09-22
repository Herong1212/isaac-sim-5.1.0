__all__ = ["ReorderPrimCommand", "ChangePrimDisplayNameCommand"]

import carb
import omni.kit.commands
import omni.usd

from pxr import Usd, Sdf


class ChangePrimDisplayNameCommand(omni.kit.commands.Command):
    """
    Command to change the display name of a prim.
    """

    def __init__(self, stage: Usd.Stage, prim_path: Sdf.Path, new_display_name: str):
        """
        Constructor.

        Args:
            stage (Usd.Stage): USD stage.
            prim_path (Sdf.Path): Prim path.
            new_display_name (str): New display name to be set.
        """

        self.__stage = stage
        self.__prim_path = prim_path
        self.__old_display_name = None
        self.__new_display_name = new_display_name or ""

    def do(self):
        """Renames the prim display name with the new display name, or no operation performed if the prim doesn't exist."""
        prim = self.__stage.GetPrimAtPath(self.__prim_path)
        if not prim:
            return

        self.__old_display_name = omni.usd.editor.get_display_name(prim)
        omni.usd.editor.set_display_name(prim, self.__new_display_name)

    def undo(self):
        """Undo the rename for display name of the prim."""
        prim = self.__stage.GetPrimAtPath(self.__prim_path)
        if not prim:
            return

        if self.__old_display_name is not None:
            omni.usd.editor.set_display_name(prim, self.__old_display_name)


class ReorderPrimCommand(omni.kit.commands.Command):
    """
    Command to reorder prim under its parent.
    This command uses the support from USD to override the reorder property, and it will always be authored into the
    root layer without considering the edit target.
    """

    def __init__(self, stage: Usd.Stage, prim_path: Sdf.Path, move_to_location: int):
        """
        Constructor.

        Args:
            stage (Usd.Stage): USD stage.
            prim_path (Sdf.Path): Prim to reorder.
            move_to_location (int): Move to the location in its parent. If it's -1, it means to move
                the prim to the bottom.
        """
        self.__stage = stage
        self.__prim_path = Sdf.Path(prim_path)
        self.__move_to_location = move_to_location
        self.__old_location = -1
        self.__success = False

    def __move_to(self, location):
        if self.__prim_path == Sdf.Path.emptyPath or self.__prim_path == Sdf.Path.absoluteRootPath:
            carb.log_warn("Failed to reorder prim as empty path or absolute root path is not supported.")
            return False

        prim = self.__stage.GetPrimAtPath(self.__prim_path)
        if not prim:
            carb.log_error(f"Failed to reorder prim {self.__prim_path} as prim is not found in the stage.")
            return False

        parent_path = self.__prim_path.GetParentPath()
        parent_prim = self.__stage.GetPrimAtPath(parent_path)
        if not parent_prim:
            return

        all_children = parent_prim.GetAllChildrenNames()
        total_children = len(all_children)
        name = self.__prim_path.name
        if name in all_children:
            index = all_children.index(name)
            self.__old_location = index
            all_children.remove(name)
        else:
            index = -1

        if index == location:
            return

        if location < 0 or location > total_children:
            location = -1
        elif location > index and index != -1:
            # If it's to move from up to down.
            location -= 1

        all_children.insert(location, name)
        # Use Sdf API so it can be batched.
        parent_prim_spec = Sdf.CreatePrimInLayer(self.__stage.GetRootLayer(), parent_path)
        parent_prim_spec.nameChildrenOrder = all_children

        self.__success = True

        return True

    def do(self):
        """Moves the prim to the specified location."""
        with Usd.EditContext(self.__stage, self.__stage.GetRootLayer()):
            return self.__move_to(self.__move_to_location)

    def undo(self):
        """Restores the prim to its previous location."""
        if self.__success:
            with Usd.EditContext(self.__stage, self.__stage.GetRootLayer()):
                self.__move_to(self.__old_location)
                self.__success = False
