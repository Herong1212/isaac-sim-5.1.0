# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ColumnMenuItem", "ColumnMenuModel", "ColumnMenuDelegate"]

from .event import Event
from .event import EventSubscription
from .abstract_stage_column_delegate import AbstractStageColumnDelegate
from .stage_column_delegate_registry import StageColumnDelegateRegistry
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from .stage_icons import StageIcons as Icons

import omni.ui as ui
import weakref


class ColumnMenuItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, model, text, checked):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
        self.checked_model = ui.SimpleBoolModel(checked)
        self.checked_model.add_value_changed_fn(self._on_checked_changed)
        self.__weak_model = weakref.ref(model)

    def _on_checked_changed(self, model):
        model = self.__weak_model()
        if model:
            model._item_changed(self)
            model._on_column_checked_changed([i[0] for i in model.get_columns()])

    def __repr__(self):
        return f'"{self.name_model.as_string}"'


class ColumnMenuModel(ui.AbstractItemModel):
    """
    Represents the model for available columns.
    """

    def __init__(self, enabled: Optional[List[str]] = None, accepted: Optional[List[str]] = None, **kwargs):
        super().__init__()

        self._stage_column_registry = kwargs.get("stage_column_registry", StageColumnDelegateRegistry())

        self._column_delegate_sub = self._stage_column_registry.subscribe_delegate_changed(
            self._on_column_delegate_changed
        )

        self._accepted = accepted

        if enabled is None:
            self._children = []
        else:
            self._children = [
                ColumnMenuItem(self, name, True) for name in enabled if not self._accepted or name in self._accepted
            ]
        self._on_column_delegate_changed(enabled is None)

        self._on_column_checked_changed = Event()

        # Indicating item in dragging
        self.dragging = False

    def destroy(self):
        self._column_delegate_sub = None
        self._children = None

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self._children

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        It's the object that tracks the specific value.
        In our case we use ui.SimpleStringModel.
        """
        return item.name_model

    def get_drag_mime_data(self, item):
        """Returns Multipurpose Internet Mail Extensions (MIME) data for be able to drop this item somewhere"""
        # As we don't do Drag and Drop to the operating system, we return the string.
        self.dragging = True
        return item.name_model.as_string

    def drop_accepted(self, target_item, source, drop_location=-1):
        """Reimplemented from AbstractItemModel. Called to highlight target when drag and drop."""
        # If target_item is None, it's the drop to root. Since it's
        # list model, we support reorganization of root only and we
        # don't want to create tree.
        return not target_item and drop_location >= 0

    def drop(self, target_item, source, drop_location=-1):
        """Reimplemented from AbstractItemModel. Called when dropping something to the item."""
        try:
            source_id = self._children.index(source)
        except ValueError:
            try:
                current_names = [c.name_model.as_string for c in self._children]
                source_id = current_names.index(source)
                source = self._children[source_id]

            except ValueError:
                # Not in the list. This is the source from another model.
                return

        if source_id == drop_location:
            # Nothing to do
            return

        self._children.pop(source_id)

        if drop_location > len(self._children):
            # Drop it to the end
            self._children.append(source)
        else:
            if source_id < drop_location:
                # Becase when we removed source, the array became shorter
                drop_location = drop_location - 1

            self._children.insert(drop_location, source)

        self._item_changed(None)

    def get_columns(self) -> List[Tuple[str, bool]]:
        """
        Return all the columns in the format

           `[("Visibility", True), ("Type", False)]`

        The first item is the column name, and the second item is a flag that
        is True if the column is enabled.
        """
        current_names = [c.name_model.as_string for c in self._children]
        current_checked = [c.checked_model.as_bool for c in self._children]
        return list(zip(current_names, current_checked))

    def subscribe_delegate_changed(self, fn: Callable[[List[str]], None]) -> EventSubscription:
        """
        Return the object that will automatically unsubscribe when destroyed.
        """
        return EventSubscription(self._on_column_checked_changed, fn)

    def _on_column_delegate_changed(self, enabled=False):
        """Called by StageColumnDelegateRegistry"""
        current_names = [c.name_model.as_string for c in self._children]
        column_delegate_names = self._stage_column_registry.get_column_delegate_names()

        # Exclude "Name" as it's enabled always.
        if "Name" in column_delegate_names:
            column_delegate_names.remove("Name")

        # Filter columns. We only need the columns that is in self._accepted list.
        if self._accepted:
            column_delegate_names = [name for name in column_delegate_names if name in self._accepted]

        # Fetch current columns and delegates
        all_delegates = []
        all_names = []
        for name in current_names:
            if name in column_delegate_names:
                all_names.append(name)
                all_delegates.append(self._stage_column_registry.get_column_delegate(name))

        # For new delegate, insert by order
        for name in column_delegate_names:
            if name not in all_names:
                new_delegate = self._stage_column_registry.get_column_delegate(name)
                if new_delegate is None or not isinstance(new_delegate(), AbstractStageColumnDelegate):
                    all_delegates.append(new_delegate)
                    all_names.append(name)
                else:
                    for index, delegate in enumerate(all_delegates):
                        if delegate is None or delegate().order > new_delegate().order:
                            all_delegates.insert(index, new_delegate)
                            all_names.insert(index, name)
                            break
                    else:
                        all_delegates.append(new_delegate)
                        all_names.append(name)

        if current_names == all_names:
            # Nothing changed
            return

        # Create item for new columns and reuse the items for old columns
        new_children = []
        for name in all_names:
            if name in current_names:
                i = current_names.index(name)
                new_children.append(self._children[i])
            else:
                new_children.append(ColumnMenuItem(self, name, enabled))

        # Replace children
        self._children = new_children

        self._item_changed(None)


class ColumnMenuDelegate(ui.AbstractItemDelegate):
    """
    Delegate is the representation layer. TreeView calls the methods
    of the delegate to create custom widgets for each item.
    """

    def __init__(self):
        super().__init__()

    def destroy(self):
        pass

    def build_header(self, column_id):
        pass

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        pass

    def build_widget(self, model: ColumnMenuModel, item: ColumnMenuItem, column_id, level, expanded):
        """Create a widget per column per item"""
        self._container = ui.HStack(height=24, content_clipping=False, checked=item.checked_model.as_bool, style=self._get_styles())
        with self._container:
            ui.ImageWithProvider(width = 24, style_type_name_override="MenuItem.Icon")
            ui.Label(
                    item.name_model.as_string,
                    style_type_name_override="MenuItem.Label",
                )
            ui.Image(style_type_name_override="Menu.Drag", width=10)
            ui.Spacer(width=4)

        self._container.set_mouse_pressed_fn(lambda x, y, b, a, m=model: self._on_mouse_pressed(m))
        self._container.set_mouse_released_fn(lambda x, y, b, a, t=model, m=item.checked_model: self._on_mouse_released(m, t))
        self._container.set_mouse_hovered_fn(lambda h, c=self._container: self._on_mouse_hovered(h, c))
        return

    def _on_mouse_pressed(self, column_model: ColumnMenuModel) -> None:
        # Clear item dragging flag
        column_model.dragging = False

    def _on_mouse_released(self, item_model: ui.SimpleBoolModel, column_model: ColumnMenuModel) -> None:
        if column_model.dragging:
            return
        item_model.set_value(not item_model.as_bool)

    def _on_mouse_hovered(self, hovered: bool, container: ui.HStack) -> None:
        # Here to set selected instead of hovered status for icon.
        # Because there is margin in icon, there will be some blank at top/bottom as a result icon does not become hovered if mouse on these area.
        container.selected = hovered

    @staticmethod
    def _get_styles():
        return {
            "Menu.CheckBox": {"background_color": 0x0, "margin": 0},
            "Menu.Drag": {
                "image_url": Icons().get("drag"),
                "color": 0xFF505050,
                "alignment": ui.Alignment.CENTER,
                "margin": 0.5,
            },
        }