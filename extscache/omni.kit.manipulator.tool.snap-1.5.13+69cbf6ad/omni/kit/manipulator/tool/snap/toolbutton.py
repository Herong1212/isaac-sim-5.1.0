# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pathlib import Path

import omni.kit.app
import omni.ui as ui
from omni.kit.manipulator.transform import TransformManipulator, SimpleToolButton, Operation

from .models import SettingModel


class SnapMenuDelegate(ui.MenuDelegate):
    """A UI menu delegate for the snap functionality in a manipulator tool.

    This delegate provides custom styling for the snap menu used in conjunction with
    transform manipulators such as translate, rotate, and scale operations."""

    def get_style(self):
        """Returns the style configuration for the snap menu.

        Returns:
            dict or style object: The style configuration for the snap menu."""
        from omni.kit.context_menu import style

        return style.MENU_STYLE


class SnapToolButton(SimpleToolButton):
    """A button for toggling snap functionality in transform manipulators.

    This class provides a UI component that allows users to enable or disable snapping when using translate, rotate, or scale manipulators. It interfaces with a SettingModel to persist the snapping state across sessions.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments, among which 'operation' (Operation) is mandatory and specifies the manipulator operation type (translate, rotate, scale).
    """

    def __init__(self, *args, **kwargs):
        """Initializes the snap tool button with the given operation.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments, among which 'operation' (Operation) is mandatory and specifies the manipulator operation type (translate, rotate, scale).
        """
        super().__init__(*args, **kwargs)

        operation = kwargs.get("operation")

        OP_TO_STR = {
            Operation.TRANSLATE: "translate",
            Operation.ROTATE: "rotate",
            Operation.SCALE: "scale",
        }

        self._model = SettingModel("/app/viewport/snapEnabled")
        ICON_FOLDER_PATH = Path(f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons")
        enabled_img_url = f"{ICON_FOLDER_PATH}/snap_enabled_color.svg"
        disabled_img_url = f"{ICON_FOLDER_PATH}/snap_dark.svg"

        self._build_widget(
            button_name="snap",
            enabled_img_url=enabled_img_url,
            disabled_img_url=disabled_img_url,
            model=self._model,
            menu_index=f"snap_{OP_TO_STR[operation]}",
            menu_extension_id="omni.kit.manipulator.tool.snap",
            tooltip="Snap",
        )

    def destroy(self):
        """Cleans up the resources used by the SnapToolButton instance. Destroys the associated model if it exists."""
        super().destroy()
        if self._model:
            self._model.destroy()
            self._model = None

    @classmethod
    def can_build(cls, manipulator: TransformManipulator, operation: Operation) -> bool:
        """Determines whether the snap tool button can be built for the given manipulator and operation.

        Args:
            manipulator (TransformManipulator): The manipulator to check for compatibility with the snap tool.
            operation (Operation): The operation type for which to check the possibility of building the snap tool.

        Returns:
            bool: True if the snap tool button can be built for the given manipulator and operation, otherwise False."""
        return operation == Operation.TRANSLATE or operation == Operation.ROTATE or operation == Operation.SCALE
