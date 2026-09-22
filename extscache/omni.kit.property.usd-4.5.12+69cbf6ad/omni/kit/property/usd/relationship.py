# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "filter_prims",
    "SelectionWatch",
    "RelationshipTargetPicker",
    "RelationshipArrayModel",
    "SdfRelationshipArraySingleEntryModel",
    "SdfRelationshipArrayItemModel",
    "RelationshipEditWidget",
]

import weakref
from functools import partial
from typing import Callable, List, Optional

import omni.kit.commands
import omni.ui as ui
from omni.kit.widget.stage import StageWidget
from pxr import Sdf, Usd


def filter_prims(stage, prim_list, type_list):
    """
    Filter the prims based on the type list.
    """
    if len(type_list) != 0:
        filtered_selection = []
        for item in prim_list:
            prim = stage.GetPrimAtPath(item.path)
            if prim:
                for _type in type_list:
                    if prim.IsA(_type):
                        filtered_selection.append(item)
                        break
        if filtered_selection != prim_list:
            return filtered_selection
    return prim_list


class SelectionWatch:
    """
    SelectionWatch is used to watch the selection of the stage.
    """

    def __init__(self, stage, on_selection_changed_fn, filter_type_list, filter_lambda, tree_view=None):
        self._stage = weakref.ref(stage)
        self._last_selected_prim_paths = None
        self._filter_type_list = filter_type_list
        self._filter_lambda = filter_lambda
        self._on_selection_changed_fn = on_selection_changed_fn
        self._targets_limit = 0
        if tree_view:
            self.set_tree_view(tree_view)

    def reset(self, targets_limit):
        """
        Reset the targets limit.

        Args:
            targets_limit (int): The targets limit.
        """
        self._targets_limit = targets_limit
        self.clear_selection()

    def set_tree_view(self, tree_view):
        """
        Set the tree view.

        Args:
            tree_view (TreeView): The tree view.
        """
        self._tree_view = tree_view
        self._tree_view.set_selection_changed_fn(self._on_widget_selection_changed)
        self._last_selected_prim_paths = None

    def clear_selection(self):
        """
        Clear the selection.
        """
        if not self._tree_view:
            return

        self._tree_view.model.update_dirty()
        self._tree_view.selection = []
        if self._on_selection_changed_fn:
            self._on_selection_changed_fn([])

    def _on_widget_selection_changed(self, selection):
        """
        On widget selection changed.

        Args:
            selection (List[Sdf.Path]): The selection.
        """
        stage = self._stage()
        if not stage:
            return

        prim_paths = [str(item.path) for item in selection if item]

        # Deselect instance proxy items if they were selected
        selection = [item for item in selection if item and not item.instance_proxy]

        # Although the stage view has filter, you can still select the ancestor of filtered prims, which might not match the type.
        selection = filter_prims(stage, selection, self._filter_type_list)

        # or the ancestor might not match the lambda filter
        if self._filter_lambda is not None:
            selection = [item for item in selection if self._filter_lambda(stage.GetPrimAtPath(item.path))]

        # Deselect if over the limit
        if self._targets_limit > 0 and len(selection) > self._targets_limit:
            selection = selection[: self._targets_limit]

        if self._tree_view.selection != selection:
            self._tree_view.selection = selection
            prim_paths = [str(item.path) for item in selection]

        if prim_paths == self._last_selected_prim_paths:
            return

        self._last_selected_prim_paths = prim_paths
        if self._on_selection_changed_fn:
            self._on_selection_changed_fn(self._last_selected_prim_paths)

    def enable_filtering_checking(self, enable: bool):
        """
        It is used to prevent selecting the prims that are filtered out but
        still displayed when such prims have filtered children. When `enable`
        is True, SelectionWatch should consider filtering when changing Kit's
        selection.
        """

    def set_filtering(self, filter_string: Optional[str]):
        """
        Set the filtering.

        Args:
            filter_string (Optional[str]): The filter string.
        """


class RelationshipTargetPicker:
    """
    RelationshipTargetPicker is used to pick the target of the relationship.
    """

    def __init__(self, stage, filter_type_list, filter_lambda, additional_widget_kwargs):
        """
        Initialize the RelationshipTargetPicker.

        Args:
            stage (Usd.Stage): The stage.
            filter_type_list (List[str]): The filter type list.
            filter_lambda (Callable): The filter lambda.
            additional_widget_kwargs (dict): The additional widget kwargs.
        """
        self._weak_stage = weakref.ref(stage)
        self._filter_lambda = filter_lambda
        self._selected_paths = []
        self._filter_type_list = filter_type_list
        self._on_targets_selected = None
        self._additional_widget_kwargs = additional_widget_kwargs if additional_widget_kwargs else {}
        self._target_name = additional_widget_kwargs.get("target_name", "Target")
        self._target_plural_name = additional_widget_kwargs.get("target_plural_name", "Targets")
        self._use_modal = additional_widget_kwargs.get("modal_window", False)
        self._targets_limit = None

        def on_window_visibility_changed(visible):
            if not visible:
                self._stage_widget.open_stage(None)
            else:
                # Only attach the stage when picker is open. Otherwise the Tf notice listener in StageWidget kills perf
                self._stage_widget.open_stage(self._weak_stage())

        self._window = ui.Window(
            f"Select {self._target_plural_name}",
            width=400,
            height=400,
            visible=False,
            flags=ui.WINDOW_FLAGS_MODAL if self._use_modal else ui.WINDOW_FLAGS_NONE,
            visibility_changed_fn=on_window_visibility_changed,
        )
        with self._window.frame:
            with ui.VStack():
                with ui.Frame():
                    self._stage_widget = StageWidget(None, columns_enabled=["Type"])
                    self._selection_watch = SelectionWatch(
                        stage=stage,
                        on_selection_changed_fn=self._on_selection_changed,
                        filter_type_list=filter_type_list,
                        filter_lambda=filter_lambda,
                    )
                    self._stage_widget.set_selection_watch(self._selection_watch)

                with ui.VStack(
                    height=0, style={"Button.Label:disabled": {"color": 0xFF606060}}
                ):  # TODO consolidate all styles
                    self._label = ui.Label(f"Selected {self._target_name}:\n\tNone")
                    self._button = ui.Button(
                        "Select",
                        height=10,
                        clicked_fn=partial(RelationshipTargetPicker._on_select, weak_self=weakref.ref(self)),
                        enabled=False,
                        identifier="select_button",
                    )

    @staticmethod
    def _on_select(weak_self: callable):
        # pylint: disable=protected-access

        weak_self = weak_self()
        if not weak_self:
            return

        if weak_self._on_targets_selected:
            weak_self._on_targets_selected(weak_self._selected_paths)
        weak_self._window.visible = False

    def clean(self):
        """
        Clean the RelationshipTargetPicker.
        """
        self._window.set_visibility_changed_fn(None)
        self._window = None
        self._selection_watch = None
        self._stage_widget.open_stage(None)
        self._stage_widget.destroy()
        self._stage_widget = None
        self._filter_type_list = None
        self._filter_lambda = None
        self._on_targets_selected = None

    def show(self, targets_limit, on_targets_selected: Optional[Callable] = None):
        """
        Show the RelationshipTargetPicker.

        Args:
            targets_limit: The targets limit.
            on_targets_selected: The on targets selected callback.
        """
        self._targets_limit = targets_limit
        self._selection_watch.reset(targets_limit)
        self._on_targets_selected = on_targets_selected
        self._window.visible = True
        if self._filter_lambda is not None:
            self._stage_widget.filter_by_lambda({"relpicker_filter": self._filter_lambda}, True)
        if self._filter_type_list:
            self._stage_widget.filter_by_type(self._filter_type_list, True)
            self._stage_widget.update_filter_menu_state(self._filter_type_list)

    def _on_selection_changed(self, paths):
        """
        On selection changed.

        Args:
            paths: The paths.
        """
        self._selected_paths = paths
        if self._button:
            self._button.enabled = len(self._selected_paths) > 0
        if self._label:
            text = "\n\t".join(self._selected_paths)
            if len(self._selected_paths) > 1:
                label_text = f"Selected {self._target_plural_name}"
            else:
                label_text = f"Selected {self._target_name}"
            if self._targets_limit > 0:
                label_text += f" ({len(self._selected_paths)}/{self._targets_limit})"
            label_text += f":\n\t{text if text else 'None'}"
            self._label.text = label_text


class RelationshipArrayModel(ui.AbstractValueModel):
    """
    RelationshipArrayModel is the model for the relationship array.
    """

    def __init__(self, stage, property_paths, additional_widget_kwargs):
        """
        Initialize the RelationshipArrayModel.

        Args:
            stage: The stage.
            property_paths: The property paths.
            additional_widget_kwargs: The additional widget kwargs.
        """
        super().__init__()
        self.stage = stage
        self.metadata = {}
        self._additional_widget_kwargs = additional_widget_kwargs if additional_widget_kwargs else {}
        self.targets_limit = self._additional_widget_kwargs.get("targets_limit", 0)
        self.filter_type_list = self._additional_widget_kwargs.get("target_picker_filter_type_list", [])
        self.filter_lambda = self._additional_widget_kwargs.get("target_picker_filter_lambda", None)
        self.on_add_targets = self._additional_widget_kwargs.get("target_picker_on_add_targets", None)
        self.property_paths = property_paths
        self._id_name = f"{property_paths[-1]}_{property_paths[-1].name}".replace("/", "_")
        self._relationships = [
            stage.GetPrimAtPath(path.GetPrimPath()).GetRelationship(path.name) for path in property_paths
        ]
        self._button = None
        self._update_shared_targets()
        self._value_changed()
        self._on_remove_target = None
        self._enabled = True
        self._label = None
        self._frame = None

    def clean(self):
        """
        Clean the RelationshipArrayModel.
        """
        self._frame = None
        self._button = None
        self._label = None
        self.on_add_targets = None
        self._on_remove_target = None
        self._enabled = True

    def _update_shared_targets(self):
        """
        Update the shared targets.
        """
        self._shared_targets = None
        for relationship in self._relationships:
            targets = relationship.GetTargets()
            if self._shared_targets is None:
                self._shared_targets = targets
            elif self._shared_targets != targets:
                self._shared_targets = None
                break

    def is_ambiguous(self) -> bool:
        """
        Check if the targets are ambiguous.

        Returns:
            bool: True if the targets are ambiguous, False otherwise.
        """
        return self._shared_targets is None

    def get_relationship_paths(self) -> List[Sdf.Path]:
        """
        Get the relationship paths.

        Returns:
            List[Sdf.Path]: The relationship paths.
        """
        return [rel.GetPath() for rel in self._relationships]

    def get_targets(self) -> List[Sdf.Path]:
        """
        Get the targets.

        Returns:
            List[Sdf.Path]: The targets.
        """
        return self._shared_targets

    def get_property_paths(self):
        """
        Get the property paths.

        Returns:
            List[Sdf.Path]: The property paths.
        """
        return self.property_paths

    def set_targets(self, targets: List[Sdf.Path]):
        """
        Set the targets.

        Args:
            targets: The targets.
        """
        if self.targets_limit > 0 and len(targets) > self.targets_limit:
            targets = targets[: self.targets_limit]
        with omni.kit.undo.group():
            for relationship in self._relationships:
                if relationship:
                    omni.kit.commands.execute("SetRelationshipTargets", relationship=relationship, targets=targets)
        if self.on_add_targets:
            self.on_add_targets(targets)

    def set_value(self, targets: List[Sdf.Path]):
        """
        Set the value.

        Args:
            targets: The targets.
        """
        self.set_targets(targets)

    def get_value(self):
        """
        Get the value.

        Returns:
            List[Sdf.Path]: The value.
        """
        return self.get_targets()

    def _set_dirty(self, *args, **kwargs):
        """
        Set dirty.

        Args:
            *args: The args.
            **kwargs: The kwargs.
        """
        self._update_shared_targets()
        self._value_changed()

    def _on_usd_changed(self, *args, **kwargs):
        """
        On USD changed.

        Args:
            *args: The args.
            **kwargs: The kwargs.
        """
        self._set_dirty()


class SdfRelationshipArraySingleEntryModel(ui.SimpleStringModel):
    """
    SdfRelationshipArraySingleEntryModel is the model for the single entry of the relationship array.
    """

    def __init__(self, stage: Usd.Stage, property_paths: List[Sdf.Path], index: int):
        """
        Initialize the SdfRelationshipArraySingleEntryModel.

        Args:
            stage: The stage.
            property_paths: The property paths.
            index: The index.
        """
        super().__init__()
        self._stage = stage
        self._paths = property_paths
        self.index = index

    def clean(self):
        """
        Clean the SdfRelationshipArraySingleEntryModel.
        """
        self._stage = None
        self._paths = None
        self.index = None

    def get_value_as_string(self):
        """
        Get the value as string.

        Returns:
            str: The value as string.
        """
        path = self._paths[0]
        relationships = self._stage.GetPrimAtPath(path.GetPrimPath()).GetRelationship(path.name)
        if relationships:
            targets = relationships.GetTargets()
            if self.index < len(targets):
                return str(targets[self.index])

        return ""

    def set_value_as_string(self, value):
        """
        Set the value as string.

        Args:
            value: The value.
        """
        path = self._paths[0]
        prim_path = path.GetPrimPath()
        relationships = self._stage.GetPrimAtPath(prim_path).GetRelationship(path.name)
        if relationships:
            targets = relationships.GetTargets()
            if self.index < len(targets):
                # If the given path is not a valid path the command will raise an exception
                if not Sdf.Path.IsValidPathString(value):
                    return
                new_path = Sdf.Path(value)
                # It's not allowed to have duplicate targets
                if new_path.MakeAbsolutePath(prim_path) in targets:
                    return
                targets[self.index] = new_path

                with omni.kit.undo.group():
                    omni.kit.commands.execute("SetRelationshipTargets", relationship=relationships, targets=targets)

    def get_value(self):
        """
        Get the value.

        Returns:
            str: The value.
        """
        return self.get_value_as_string()

    def set_value(self, value):
        """
        Set the value.

        Args:
            value: The value.
        """
        self.set_value_as_string(str(value))

    def _set_dirty(self, *args, **kwargs):
        """
        Set dirty.

        Args:
            *args: The args.
            **kwargs: The kwargs.
        """
        self._value_changed()

    def _on_usd_changed(self, *args, **kwargs):
        """
        On USD changed.

        Args:
            *args: The args.
            **kwargs: The kwargs.
        """
        self._set_dirty()


class SdfRelationshipArrayItemModel(ui.AbstractItemModel):
    """
    SdfRelationshipArrayItemModel is the model for the item of the relationship array.
    """

    class SdfRelationshipPathItem(ui.AbstractItem):
        """
        Single item of the model
        """

        def __init__(
            self,
            stage: Usd.Stage,
            property_paths: List[Sdf.Path],
            index: int,
            self_refresh: bool,
            metadata: dict,
            additional_widget_kwargs=None,
        ):
            """
            Initialize the SdfRelationshipPathItem.

            Args:
                stage: The stage.
                property_paths: The property paths.
                index: The index.
                self_refresh: Whether to refresh the item.
                metadata: The metadata.
                additional_widget_kwargs: The additional widget kwargs.
            """
            super().__init__()
            item_cls = (additional_widget_kwargs or {}).get(
                "relationship_array_single_value_model_cls", SdfRelationshipArraySingleEntryModel
            )
            self.sdf_relationship_path_model = item_cls(stage, property_paths, index)

        def destroy(self):
            """
            Destroy the SdfRelationshipPathItem.
            """
            self.sdf_relationship_path_model.clean()

        def is_ambiguous(self) -> bool:
            """
            Check if the targets are ambiguous.

            Returns:
                bool: True if the targets are ambiguous, False otherwise.
            """
            self._update_value()
            return self._ambiguous

    def __init__(
        self, stage: Usd.Stage, property_paths: List[Sdf.Path], metadata: dict, delegate, additional_widget_kwargs
    ):
        """
        Initialize the SdfRelationshipArrayItemModel.

        Args:
            stage: The stage.
            property_paths: The property paths.
            metadata: The metadata.
            delegate: The delegate.
            additional_widget_kwargs: The additional widget kwargs.
        """
        super().__init__()
        self.metadata = metadata
        self.property_paths = property_paths
        self._additional_widget_kwargs = additional_widget_kwargs if additional_widget_kwargs else {}
        self.targets_limit = self._additional_widget_kwargs.get("targets_limit", 0)
        self.filter_type_list = self._additional_widget_kwargs.get("target_picker_filter_type_list", [])
        self.filter_lambda = self._additional_widget_kwargs.get("target_picker_filter_lambda", None)
        self._button = None
        picker_cls = self._additional_widget_kwargs.get("target_picker_cls", RelationshipTargetPicker)
        self.picker = picker_cls(
            stage,
            self.filter_type_list,
            self.filter_lambda,
            self._additional_widget_kwargs,
        )
        self._enabled = self._additional_widget_kwargs.get("enabled", True)
        self._delegate = delegate  # keep a reference of the delegate so it's not destroyed
        self._value_model = RelationshipArrayModel(stage, property_paths, additional_widget_kwargs)
        value = self._value_model.get_value()
        self._entries = []

        self._repopulate_entries(value)

    def clean(self):
        """
        Clean the SdfRelationshipArrayItemModel.
        """
        self.picker.clean()
        self.picker = None

        self._delegate = None

        for entry in self._entries:
            entry.destroy()
        self._entries.clear()

        if self._value_model:
            self._value_model.clean()
            self._value_model = None

    @property
    def value_model(self):
        """
        Get the value model.

        Returns:
            RelationshipArrayModel: The value model.
        """
        return self._value_model

    def get_item_children(self, item):
        """
        Get the item children.

        Args:
            item: The item.
        """
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self._entries

    def get_item_value_model_count(self, item):
        """
        Get the item value model count.

        Args:
            item: The item.
        """
        return 1

    def get_item_value_model(self, item, column_id):
        """
        Get the item value model.

        Args:
            item: The item.
            column_id: The column id.
        """
        return (item.sdf_relationship_path_model, self._value_model)

    def get_drag_mime_data(self, item):
        """
        Get the drag mime data.

        Args:
            item: The item.
        """
        return str(item.sdf_relationship_path_model.index)

    def drop_accepted(self, target_item, source, drop_location=-1):
        """
        Check if the drop is accepted.

        Args:
            target_item: The target item.
            source: The source.
            drop_location: The drop location.
        """
        try:
            self._entries.index(source)
        except ValueError:
            # Not in the list. This is the source from another model.
            return False

        return not target_item and drop_location >= 0

    def drop(self, target_item, source, drop_location=-1):
        """
        Drop the item.

        Args:
            target_item: The target item.
            source: The source.
            drop_location: The drop location.
        """
        try:
            source_id = self._entries.index(source)
        except ValueError:
            # Not in the list. This is the source from another model.
            return

        if source_id == drop_location:
            # Nothing to do
            return

        value = list(self._value_model.get_value())
        moved_entry_value = value[source_id]
        del value[source_id]

        if drop_location > len(value):
            # Drop it to the end
            value.append(moved_entry_value)
        else:
            if source_id < drop_location:
                # Because when we removed source, the array became shorter
                drop_location = drop_location - 1

            value.insert(drop_location, moved_entry_value)
        self._value_model.set_value(value)

    def _repopulate_entries(self, value):
        """
        Repopulate the entries.

        Args:
            value: The value.
        """
        for entry in self._entries:
            entry.destroy()
        self._entries.clear()

        if value is not None:
            stage = self._value_model.stage
            metadata = self._value_model.metadata
            property_paths = self._value_model.get_property_paths()

            for i in range(len(value)):
                model = SdfRelationshipArrayItemModel.SdfRelationshipPathItem(
                    stage, property_paths, i, False, metadata, self._additional_widget_kwargs
                )
                self._entries.append(model)

        self._item_changed(None)

    def _on_usd_changed(self, *args, **kwargs):
        """
        On USD changed.

        Args:
            *args: The args.
            **kwargs: The kwargs.
        """
        # pylint: disable=protected-access

        # forward to all sub-models
        self._value_model._on_usd_changed(*args, **kwargs)
        for entry in self._entries:
            entry.sdf_relationship_path_model._on_usd_changed(*args, **kwargs)

    def _set_dirty(self, *args, **kwargs):
        """
        Set dirty.

        Args:
            *args: The args.
            **kwargs: The kwargs.
        """
        # pylint: disable=protected-access

        # forward to all sub-models
        self._value_model._set_dirty(*args, **kwargs)

        new_value = self._value_model.get_value()
        if new_value and len(new_value) != len(self._entries):
            self._repopulate_entries(new_value)
        else:
            for entry in self._entries:
                entry.sdf_relationship_path_model._set_dirty(*args, **kwargs)

    def get_value(self, *args, **kwargs):
        """
        Get the value.

        Args:
            *args: The args.
            **kwargs: The kwargs.
        """
        return self._value_model.get_value(*args, **kwargs)

    def set_value(self, *args, **kwargs):
        """
        Set the value.

        Args:
            *args: The args.
            **kwargs: The kwargs.
        """
        return self._value_model.set_value(*args, **kwargs)

    def get_attribute_paths(self) -> List[Sdf.Path]:
        """
        Get the attribute paths.

        Returns:
            List[Sdf.Path]: The attribute paths.
        """
        return self.get_property_paths()

    def get_property_paths(self) -> List[Sdf.Path]:
        """
        Get the property paths.

        Returns:
            List[Sdf.Path]: The property paths.
        """
        return self.property_paths

    def is_ambiguous(self) -> bool:
        """
        Check if the targets are ambiguous.

        Returns:
            bool: True if the targets are ambiguous, False otherwise.
        """
        # pylint: disable=protected-access

        model = self._value_model
        model._update_shared_targets()
        return model.is_ambiguous()


class SelectionWatchOld:  # pragma: no cover
    """
    DEPRECATED
    """

    def __init__(self, stage, on_selection_changed_fn, filter_type_list, filter_lambda, tree_view=None):
        """
        Initialize the SelectionWatchOld.

        Args:
            stage: The stage.
            on_selection_changed_fn: The on selection changed function.
            filter_type_list: The filter type list.
            filter_lambda: The filter lambda.
            tree_view: The tree view.
        """
        self._stage = weakref.ref(stage)
        self._last_selected_prim_paths = None
        self._filter_type_list = filter_type_list
        self._filter_lambda = filter_lambda
        self._on_selection_changed_fn = on_selection_changed_fn
        self._targets_limit = 0
        if tree_view:
            self.set_tree_view(tree_view)

    def reset(self, targets_limit):
        """
        Reset the targets limit.

        Args:
            targets_limit: The targets limit.
        """
        self._targets_limit = targets_limit
        self.clear_selection()

    def set_tree_view(self, tree_view):
        """
        Set the tree view.

        Args:
            tree_view: The tree view.
        """
        self._tree_view = tree_view
        self._tree_view.set_selection_changed_fn(self._on_widget_selection_changed)
        self._last_selected_prim_paths = None

    def clear_selection(self):
        """
        Clear the selection.
        """
        if not self._tree_view:
            return

        self._tree_view.model.update_dirty()
        self._tree_view.selection = []
        if self._on_selection_changed_fn:
            self._on_selection_changed_fn([])

    def _on_widget_selection_changed(self, selection):
        """
        On widget selection changed.

        Args:
            selection: The selection.
        """
        stage = self._stage()
        if not stage:
            return

        prim_paths = [str(item.path) for item in selection if item]

        # Deselect instance proxy items if they were selected
        selection = [item for item in selection if item and not item.instance_proxy]

        # Although the stage view has filter, you can still select the ancestor of filtered prims, which might not match the type.
        if len(self._filter_type_list) != 0:
            filtered_selection = []
            for item in selection:
                prim = stage.GetPrimAtPath(item.path)
                if prim:
                    for _type in self._filter_type_list:
                        if prim.IsA(_type):
                            filtered_selection.append(item)
                            break
            if filtered_selection != selection:
                selection = filtered_selection

        # or the ancestor might not match the lambda filter
        if self._filter_lambda is not None:
            selection = [item for item in selection if self._filter_lambda(stage.GetPrimAtPath(item.path))]

        # Deselect if over the limit
        if self._targets_limit > 0 and len(selection) > self._targets_limit:
            selection = selection[: self._targets_limit]

        if self._tree_view.selection != selection:
            self._tree_view.selection = selection
            prim_paths = [str(item.path) for item in selection]

        if prim_paths == self._last_selected_prim_paths:
            return

        self._last_selected_prim_paths = prim_paths
        if self._on_selection_changed_fn:
            self._on_selection_changed_fn(self._last_selected_prim_paths)

    def enable_filtering_checking(self, enable: bool):
        """
        It is used to prevent selecting the prims that are filtered out but
        still displayed when such prims have filtered children. When `enable`
        is True, SelectionWatch should consider filtering when changing Kit's
        selection.
        """

    def set_filtering(self, filter_string: Optional[str]):
        """
        Set the filtering.

        Args:
            filter_string: The filter string.
        """


class RelationshipTargetPickerOld:  # pragma: no cover
    """
    DEPRECATED
    """

    def __init__(
        self, stage, relationship_widget, filter_type_list, filter_lambda, on_add_targets: Optional[Callable] = None
    ):
        # pylint: disable=protected-access

        self._weak_stage = weakref.ref(stage)
        self._relationship_widget = relationship_widget
        self._filter_lambda = filter_lambda
        self._selected_paths = []
        self._filter_type_list = filter_type_list
        self._on_add_targets = on_add_targets
        self._targets_limit = None

        def on_window_visibility_changed(visible):
            if not visible:
                self._stage_widget.open_stage(None)
            else:
                # Only attach the stage when picker is open. Otherwise the Tf notice listener in StageWidget kills perf
                self._stage_widget.open_stage(self._weak_stage())

        self._window = ui.Window(
            "Select Target(s)",
            width=400,
            height=400,
            visible=False,
            flags=0,
            visibility_changed_fn=on_window_visibility_changed,
        )
        with self._window.frame:
            with ui.VStack():
                with ui.Frame():
                    self._stage_widget = StageWidget(None, columns_enabled=["Type"])
                    self._selection_watch = SelectionWatchOld(
                        stage=stage,
                        on_selection_changed_fn=self._on_selection_changed,
                        filter_type_list=filter_type_list,
                        filter_lambda=filter_lambda,
                    )
                    self._stage_widget.set_selection_watch(self._selection_watch)

                def on_select(weak_self):
                    weak_self = weak_self()
                    if not weakref:
                        return

                    pending_add = []
                    for relationship in weak_self._relationship_widget._relationships:
                        if relationship:
                            existing_targets = relationship.GetTargets()
                            for selected_path in weak_self._selected_paths:
                                selected_path = Sdf.Path(selected_path)
                                if selected_path not in existing_targets:
                                    pending_add.append((relationship, selected_path))

                    if pending_add:
                        omni.kit.undo.begin_group()
                        for add in pending_add:
                            omni.kit.commands.execute("AddRelationshipTarget", relationship=add[0], target=add[1])
                        omni.kit.undo.end_group()
                        if self._on_add_targets:
                            self._on_add_targets(pending_add)

                    weak_self._window.visible = False

                with ui.VStack(
                    height=0, style={"Button.Label:disabled": {"color": 0xFF606060}}
                ):  # TODO consolidate all styles
                    self._label = ui.Label("Selected Path(s):\n\tNone")
                    self._button = ui.Button(
                        "Add",
                        height=10,
                        clicked_fn=partial(on_select, weak_self=weakref.ref(self)),
                        enabled=False,
                        identifier="add_button",
                    )

    def clean(self):
        """
        Clean the RelationshipTargetPickerOld.
        """
        self._window.set_visibility_changed_fn(None)
        self._window = None
        self._selection_watch = None
        self._stage_widget.open_stage(None)
        self._stage_widget.destroy()
        self._stage_widget = None
        self._filter_type_list = None
        self._filter_lambda = None
        self._on_add_targets = None

    def show(self, targets_limit):
        """
        Show the RelationshipTargetPickerOld.

        Args:
            targets_limit: The targets limit.
        """
        self._targets_limit = targets_limit
        self._selection_watch.reset(targets_limit)
        self._window.visible = True
        if self._filter_lambda is not None:
            self._stage_widget.filter_by_lambda({"relpicker_filter": self._filter_lambda}, True)
        if self._filter_type_list:
            self._stage_widget.filter_by_type(self._filter_type_list, True)
            self._stage_widget.update_filter_menu_state(self._filter_type_list)

    def _on_selection_changed(self, paths):
        """
        On selection changed.

        Args:
            paths: The paths.
        """
        self._selected_paths = paths
        if self._button:
            self._button.enabled = len(self._selected_paths) > 0
        if self._label:
            text = "\n\t".join(self._selected_paths)
            label_text = "Selected Path(s)"
            if self._targets_limit > 0:
                label_text += f" ({len(self._selected_paths)}/{self._targets_limit})"
            label_text += f":\n\t{text if text else 'None'}"
            self._label.text = label_text


class RelationshipEditWidget:  # pragma: no cover
    """
    DEPRECATED!

    Existing extensions depend on this class but the UI has been updated. Please update your extensions.
    """

    def __init__(self, stage, attr_name, prim_paths, additional_widget_kwargs=None):
        self._id_name = f"{prim_paths[-1]}_{attr_name}".replace("/", "_")
        self._relationships = [stage.GetPrimAtPath(path).GetRelationship(attr_name) for path in prim_paths]
        self._additional_widget_kwargs = additional_widget_kwargs if additional_widget_kwargs else {}
        self._targets_limit = self._additional_widget_kwargs.get("targets_limit", 0)
        self._button = None
        self._target_picker = RelationshipTargetPickerOld(
            stage,
            self,
            self._additional_widget_kwargs.get("target_picker_filter_type_list", []),
            self._additional_widget_kwargs.get("target_picker_filter_lambda", None),
            self._additional_widget_kwargs.get("target_picker_on_add_targets", None),
        )
        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)
        self._on_remove_target = self._additional_widget_kwargs.get("on_remove_target", None)
        self._enabled = self._additional_widget_kwargs.get("enabled", True)
        self._shared_targets = None
        self._label = None

    def clean(self):
        """
        Clean the RelationshipEditWidget.
        """
        self._target_picker.clean()
        self._target_picker = None
        self._frame = None
        self._button = None
        self._label = None
        self._on_remove_target = None
        self._enabled = True

    def is_ambiguous(self) -> bool:
        """
        Check if the targets are ambiguous.

        Returns:
            bool: True if the targets are ambiguous, False otherwise.
        """
        return self._shared_targets is None

    def get_all_comp_ambiguous(self) -> List[bool]:
        """
        Get all components ambiguous.

        Returns:
            List[bool]: The all components ambiguous.
        """
        return []

    def get_relationship_paths(self) -> List[Sdf.Path]:
        """
        Get the relationship paths.

        Returns:
            List[Sdf.Path]: The relationship paths.
        """
        return [rel.GetPath() for rel in self._relationships]

    def get_property_paths(self) -> List[Sdf.Path]:
        """
        Get the property paths.

        Returns:
            List[Sdf.Path]: The property paths.
        """
        return self.get_relationship_paths()

    def get_targets(self) -> List[Sdf.Path]:
        """
        Get the targets.

        Returns:
            List[Sdf.Path]: The targets.
        """
        return self._shared_targets

    def set_targets(self, targets: List[Sdf.Path]):
        """
        Set the targets.

        Args:
            targets: The targets.
        """
        with omni.kit.undo.group():
            for relationship in self._relationships:
                if relationship:
                    omni.kit.commands.execute("SetRelationshipTargets", relationship=relationship, targets=targets)

    def set_value(self, targets: List[Sdf.Path]):
        """
        Set the value.

        Args:
            targets: The targets.
        """
        self.set_targets(targets)

    def _build(self):
        """
        Build the RelationshipEditWidget.
        """
        # pylint: disable=protected-access
        self._shared_targets = None

        for relationship in self._relationships:
            targets = relationship.GetTargets()
            if self._shared_targets is None:
                self._shared_targets = targets
            elif self._shared_targets != targets:
                self._shared_targets = None
                break

        with ui.VStack(spacing=2):
            if self._shared_targets is not None:
                for target in self._shared_targets:
                    with ui.HStack(spacing=2):
                        ui.StringField(name="models", read_only=True).model.set_value(target.pathString)

                        def on_remove_target(weak_self, target):
                            weak_self = weak_self()
                            if weak_self:
                                with omni.kit.undo.group():
                                    for relationship in weak_self._relationships:
                                        if relationship:
                                            omni.kit.commands.execute(
                                                "RemoveRelationshipTarget", relationship=relationship, target=target
                                            )
                                if self._on_remove_target:
                                    self._on_remove_target(target)

                        ui.Button(
                            "-",
                            enabled=self._enabled,
                            width=ui.Pixel(14),
                            clicked_fn=partial(on_remove_target, weak_self=weakref.ref(self), target=target),
                            identifier=f"remove_relationship{target.pathString.replace('/', '_')}",
                        )

                def on_add_target(weak_self):
                    weak_self = weak_self()
                    if weak_self:
                        weak_self._target_picker.show(weak_self._targets_limit - len(weak_self._shared_targets))

                within_target_limit = self._targets_limit == 0 or len(self._shared_targets) < self._targets_limit
                button = ui.Button(
                    "Add Target(s)",
                    width=ui.Pixel(30),
                    clicked_fn=partial(on_add_target, weak_self=weakref.ref(self)),
                    enabled=within_target_limit and self._enabled,
                    identifier=f"add_relationship{self._id_name}",
                )
                if not within_target_limit:
                    button.set_tooltip(
                        f"Targets limit of {self._targets_limit} has been reached. To add more target(s), remove current one(s) first."
                    )
            else:
                ui.StringField(name="models", read_only=True).model.set_value("Mixed")

    def _set_dirty(self):
        """
        Set dirty.
        """
        self._frame.rebuild()
