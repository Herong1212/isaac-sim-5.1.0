# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.stageupdate
import omni.ui as ui
from omni.anim.retarget.core.scripts.utils import convert_to_simple_joints

from pxr import Usd, UsdSkel, Tf, Sdf

import weakref
import usdrt


class MinimalItem(ui.AbstractItem):
    def __init__(self, text):
        super().__init__()
        self.model = ui.SimpleStringModel(text)

    def __del__(self):
        self.model = None


class PrimComboBox(ui.AbstractItemModel):
    def __init__(self, set_callback):
        super().__init__()
        self._set_callback_ref = weakref.WeakMethod(set_callback)
        self._stage_update = omni.stageupdate.get_stage_update_interface()
        self._current_index = ui.SimpleIntModel()
        self._items = []

    def __del__(self):
        self._items = None
        self._stage_update = None
        self._set_callback_ref = None
        self._current_index = None

    def get_item_children(self, item):
        return self._items

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._current_index
        return item.model

    def set_value(self, value):
        for i in range(len(self._items)):
            if self._items[i].model.as_string == value:
                self._current_index.as_int = i
                break

    def _current_index_changed(self, model):
        index = model.as_int
        self._item_changed(None)
        self._set_callback_ref()(
            index,
            self._items[index].model.as_string
        )

    def _add_unique_item(self, item):
        for iter in self._items:
            if iter.model.as_string == item.model.as_string:
                return
        self._items.append(item)


class StageInfo:
    def __init__(self):
        self._skeleton_set = set()
        self._widgets = []

        stage_update = omni.stageupdate.get_stage_update_interface()
        self.stage_subscription = stage_update.create_stage_update_node(
            "SkeletonsCombo", self._on_attach, self._on_detach, None, self._on_prim_created, None)
        self._usd_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, None)

    def on_shutdown(self):
        self._widgets = []
        self.stage_subscription = None
        self._usd_listener = None

    def __del__(self):
        self._widgets = []
        self.stage_subscription = None
        self._usd_listener = None

    def find_skeletons(self, prim):
        skeleton_paths = []
        for child in Usd.PrimRange(prim):
            if (UsdSkel.Skeleton(child)):
                skeleton_paths.append(child.GetPath())

        return skeleton_paths

    def _on_attach(self, stage_id, meters_per_unit):
        self._rebuild()

    def _on_detach(self):
        self._rebuild()

    def _on_prim_created(self, path):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(path)
        if prim.IsValid():
            skeleton_paths = self.find_skeletons(prim)
            for skel_path in skeleton_paths:
                self._skeleton_set.add(skel_path)
                for widget in self._widgets:
                    widget._on_prim_added(skel_path)

    def _on_prim_removed(self, path, stage):
        skeleton_set_copy = self._skeleton_set.copy()
        for skel_path in skeleton_set_copy:
            if skel_path.HasPrefix(path):
                self._skeleton_set.remove(skel_path)
                for widget in self._widgets:
                    widget._on_prim_removed(skel_path)

    def _on_objects_changed(self, notice, stage):
        if stage is None:
            return
        # see if it's being removed
        for p in notice.GetResyncedPaths():
            if p.IsAbsoluteRootOrPrimPath():
                prim = stage.GetPrimAtPath(p)
                if not prim:
                    self._on_prim_removed(p, stage)

    def _rebuild(self):
        self._skeleton_set.clear()

        # in the event of shutdown, this will cause spam
        context = omni.usd.get_context()
        if context:
            usdrtstage = usdrt.Usd.Stage.Attach(context.get_stage_id())
            skeleton_paths = usdrtstage.GetPrimsWithTypeName("Skeleton")

            for widget in self._widgets:
                widget.rebuild(skeleton_paths)

    def registerWidget(self, widget):
        if self._widgets.count(widget) == 0:
            self._widgets.append(widget)

    def unrigisterWidget(self, widget):
        while self._widgets.count(widget) > 0:
            self._widgets.remove(widget)


class SkeletonSelection(PrimComboBox):
    def __init__(
            self,
            set_callback,
            instruction_message,
            stageInfo,
            custom_add_callback=None,
            custom_set_callback=None
    ):
        self._instruction_message = instruction_message
        self._stage_info = weakref.ref(stageInfo)
        self._stage_info().registerWidget(self)
        super().__init__(set_callback)
        self._custom_add_callback = custom_add_callback
        self._custom_set_callback = custom_set_callback
        self._custom_item_count = 0
        self._current_index.add_value_changed_fn(self._current_index_changed)

    def __del__(self):
        self._stage_info().unrigisterWidget(self)
        self._stage_info = None
        super().__del__()

    @staticmethod
    def _list_children(prim):
        """ To list all nested children

        Args

        prim : Usd Prim
        """
        def get_all_descendents(prim, output=[]):
            prim_children = prim.GetChildren()
            if prim_children:
                for child in prim_children:
                    output.append(child)
                    get_all_descendents(child, output)
            return output

        output = []
        if prim:
            return get_all_descendents(prim, output)
        return output

    def _current_index_changed(self, model):
        index = model.as_int
        self._item_changed(None)
        skel_prim_string = self._items[index].model.as_string

        if index > 0 and index <= self._custom_item_count:
            # this allows users to pick the right skeleton for the case
            skel_prim_string = self._custom_set_callback(index, skel_prim_string)
            if skel_prim_string is None:
                return
        self._set_callback_ref()(index, skel_prim_string)

    def _on_prim_added(self, path):
        self._add_unique_item(MinimalItem(path.pathString))
        self._item_changed(None)

    def _on_prim_removed(self, path):
        skeleton_paths = [item.model.as_string for item in self._items]
        # when deleting skeleton, sometimes it's parent, not itself
        # and we don't get notification for children
        for skel_path in skeleton_paths:
            if Sdf.Path(skel_path) == path:
                index = [item.model.as_string for item in self._items].index(skel_path)
                if self._current_index.as_int == index:
                    self._current_index.as_int = 0
                del self._items[index]
                self._item_changed(None)

    def rebuild(self, skeleton_paths):  # skeleton_paths need to have no repeat elements.
        self._items.clear()
        self._items = [MinimalItem(self._instruction_message)]
        self._current_index.as_int = 0
        if self._custom_add_callback:
            custom_items = self._custom_add_callback()
            self._custom_item_count = len(custom_items)
            self._items += custom_items

        for path in skeleton_paths:
            self._items.append(MinimalItem(path.GetString()))
        self._item_changed(None)

    def select_skeleton(self, skeleton_path):
        selected = 0
        for i, item in enumerate(self._items):
            if (item.model.as_string == skeleton_path.pathString):
                selected = i
                break

        if self._current_index.as_int is not selected:
            self._current_index.as_int = selected
            self._item_changed(None)


class SkelJointSelection(PrimComboBox):
    """
    Doesn't support listening to notifications when stage changes
    that happens outside of this combo """
    def __init__(self, set_callback):
        super().__init__(set_callback)
        self._skeleton = None
        self._tag_name = ""
        self._joint = ""
        self.refresh()
        self._current_index.add_value_changed_fn(self._current_index_changed)

    def _current_index_changed(self, model):
        index = model.as_int
        self._item_changed(None)
        self._set_callback_ref()(self._tag_name, self._items[index].model.as_string)

    def __del__(self):
        self._stage_subscription = None
        super().__del__()

    def set_tag_name(self, tag_name):
        self._tag_name = tag_name

    def set_skeleton(self, skeleton):
        self._skeleton = skeleton

    def set_selection(self, tag_name, joint):
        self._tag_name = tag_name
        self._joint = joint
        self.refresh()

    def refresh(self):
        self._items.clear()
        self._items = [MinimalItem("Pick an end joint of this chain")]
        selected = 0
        if self._skeleton is not None:
            joint_attr = self._skeleton.GetJointsAttr()
            joints = convert_to_simple_joints(joint_attr.Get())
            for i, joint in enumerate(joints):
                if joint == self._joint:
                    selected = i + 1
                self._add_unique_item(MinimalItem(joint))
        else:
            self._add_unique_item(MinimalItem("None"))

        self._current_index.as_int = selected
        self._item_changed(None)


class AxisSelection(ui.AbstractItemModel):
    def __init__(self, set_callback):
        super().__init__()
        self._set_callback_ref = weakref.WeakMethod(set_callback)
        self._current_index = ui.SimpleIntModel()
        self._items = [MinimalItem("X"), MinimalItem("Y"), MinimalItem("Z"), MinimalItem("-X"), MinimalItem("-Y"), MinimalItem("-Z")]
        self._usd_names = ["X", "Y", "Z", "MINUS X", "MINUS Y", "MINUS Z"]
        self._current_index.add_value_changed_fn(self._current_index_changed)

    def __del__(self):
        self._items = None
        self._set_callback_ref = None
        self._current_index = None

    def get_item_children(self, item):
        return self._items

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._current_index
        return item.model

    def value(self):
        return self._current_index.get_value_as_int()

    def set_value(self, value):
        for i in range(len(self._items)):
            if self._usd_names[i] == value:
                self._current_index.as_int = i
                self._item_changed(None)
                break

    def _current_index_changed(self, model):
        index = model.as_int
        self._item_changed(None)
        self._set_callback_ref()(index, self._usd_names[index])
