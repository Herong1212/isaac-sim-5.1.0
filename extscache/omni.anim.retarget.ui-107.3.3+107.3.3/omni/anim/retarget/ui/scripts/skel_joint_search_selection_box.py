# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .search_widget import SearchWidget

import carb.input
import carb.settings
import omni.stageupdate
import omni.ui as ui
from omni.anim.retarget.core.scripts.utils import convert_to_simple_joints, get_selected_joint

import asyncio
from typing import List

INVALID_JOINT_NAME = "None"


class JointListItem(ui.AbstractItem):
    """Single item of the model"""
    def __init__(self, text):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
        # true when the item is visible
        self.filtered = True

    def prefilter(self, filter_name_text: str):
        if not filter_name_text:
            self.filtered = True
        else:
            self.filtered = filter_name_text in self.name_model.as_string.lower()

    def __repr__(self):
        return f'"{self.name_model.as_string}"'


class JointListModel(ui.AbstractItemModel):
    def __init__(self, bind_joint_fn, joints_list, selected_index):
        super().__init__()
        self._bind_joint_fn = bind_joint_fn
        self._children = []
        for joint in joints_list:
            self._children.append(JointListItem(joint))
        self._selected_index = selected_index

    def clean(self):
        self._bind_joint_fn = None
        self._children.clear()

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is not None:
            return []
        return [c for c in self._children if c.filtered]

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item, column_id):
        return item.name_model

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""
        for c in self._children:
            c.prefilter(filter_name_text.lower())
        self._item_changed(None)

    def execute(self, item):
        """ here we bind the material into the Scene"""
        if self._bind_joint_fn is not None:
            self._bind_joint_fn(item.name_mode.as_string)


class JointListDelegate(ui.AbstractItemDelegate):
    """
    Delegate is the representation layer. TreeView calls the methods
    of the delegate to create custom widgets for each item.
    """
    def __init__(self, flat=False):
        super().__init__()

    def clean(self):
        pass

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        pass

    def build_widget(self, model, item, column_id, level, expanded):
        value_model = model.get_item_value_model(item, column_id)
        joint_name = value_model.as_string
        ui.Label(joint_name, skip_draw_when_clipped=True, elided_text=True)


class JointListBoxWidget():
    def __init__(self, joints_list, index: int, on_click_fn: callable, theme: str, icon_path: str):
        self._height = 32
        self._joints_list = joints_list
        self._index = index
        self._on_click_fn = on_click_fn
        self._theme = theme
        self.__parent = None
        self._window = None
        self.__frame = None
        self._search_widget = SearchWidget(theme=theme, icon_path=icon_path, modified_fn=self._search_updated)
        self._search_size = 22

        if theme == "NvidiaDark":
            BACKGROUND_COLOR = 0xFF555555
            FIELD_TEXT_COLOR = 0xFFD5D5D5
            FIELD_BORDER_COLOR = 0
            FIELD_HOVER_COLOR = 0xFF333333
        else:
            BACKGROUND_COLOR = 0xFF545454
            FIELD_TEXT_COLOR = 0xFFD5D5D5
            FIELD_BORDER_COLOR = 0
            FIELD_HOVER_COLOR = 0xFFACACAF

        self._window_style = {
            "Window": {
                "background_color": BACKGROUND_COLOR,
                "border_radius": 6,
                "border_width": 1,
                "border_color": FIELD_BORDER_COLOR
            },
            "ScrollingFrame":
            {
                "background_color": BACKGROUND_COLOR
            },
            "Field": {
                "background_color": BACKGROUND_COLOR,
                "color": FIELD_TEXT_COLOR,
                "border_color": FIELD_BORDER_COLOR,
                "border_radius": 1,
                "border_width": 0.5,
                "font_size": 16.0,
            },
            "Field:hovered": {"background_color": FIELD_HOVER_COLOR},
            "Field:pressed": {"background_color": FIELD_HOVER_COLOR},
            "Field::text_field": {
                "border_width": 0,
                "font_size": 14.0
            },
            # search treeview
            "TreeView.Item::search_treeview": {
                "margin": 4
            },
        }

    def set_parent(self, parent):
        self.__parent = parent

    def clean(self):
        if self._name_value_model:
            self._name_value_model.clean()
        if self._name_value_delegate:
            self._name_value_delegate.clean()
        del self._name_value_model
        del self._name_value_delegate

    def _search_updated(self, string):
        self._search_widget.update(string)
        self._name_value_model.filter_by_text(string)
        self._tree_view.scroll_here_y(0.0)

    def __on_key_pressed(self, key, mod, pressed):
        """Called when the user presses a key"""
        if not pressed:
            return
        if key == int(carb.input.KeyboardInput.ESCAPE):
            self._window.visible = False
        elif mod == 0 and key == int(carb.input.KeyboardInput.ENTER):
            self._execute(self._tree_view)
        elif mod == 0 and key == int(carb.input.KeyboardInput.DOWN):
            self._select_next(self._tree_view, self._name_value_model, after=True)
        elif mod == 0 and key == int(carb.input.KeyboardInput.UP):
            self._select_next(self._tree_view, self._name_value_model, after=False)

    def _select_next(self, treeview: ui.TreeView, model: ui.AbstractItemModel, after=True):
        full_list = model.get_item_children(None)
        selection = treeview.selection
        if not selection:
            treeview.selection = [full_list[0]]
        else:
            index = full_list.index(selection[0])
            index += 1 if after else -1
            if index < 0 or index >= len(full_list):
                return
            treeview.selection = [full_list[index]]

    def _select_index(self, treeview: ui.TreeView, model: ui.AbstractItemModel, index: int):
        full_list = model.get_item_children(None)
        if index >= 0 and index < len(full_list):
            treeview.selection = [full_list[index]]

    def _get_treeview_height(self):
        item_count = len(self._name_value_model.get_item_children(None))
        treeview_height = ((min(10, item_count) * self._height + 1.5) + 4)
        treeview_height_min = ((3 * self._height + 1.5) + 4)
        appwindow = omni.appwindow.get_default_app_window()
        window_height = appwindow.get_height()
        window_height = (window_height / ui.Workspace.get_dpi_scale()) - 8
        if self._window.position_y + treeview_height > window_height:
            adj = ((self._window.position_y + treeview_height) - window_height) + self._search_size
            treeview_height -= adj
            if treeview_height < treeview_height_min:
                treeview_height = treeview_height_min
        return treeview_height

    def _execute(self, treeview):
        selection = treeview.selection
        if selection:
            self._on_click_fn(selection[0].name_model.as_string)
            self._window.visible = False

    def build_ui(self):
        if self._window and self._window.visible:
            return
        # create and show the window
        self._window = ui.Window(
            "JointPopupWindow",
            flags=ui.WINDOW_FLAGS_POPUP | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE,
            auto_resize=True,
            padding_x=0,
            padding_y=0
        )
        self._window.frame.set_style(self._window_style)
        self._window.set_key_pressed_fn(self.__on_key_pressed)

        def tree_view_clicked(treeview):
            async def get_selection_async():
                await omni.kit.app.get_app().next_update_async()
                selection = treeview.selection
                self._on_click_fn(selection[0].name_model.as_string)
                self._window.visible = False
            asyncio.ensure_future(get_selection_async())

        self._window.position_x = self.__parent.screen_position_x
        self._window.position_y = self.__parent.screen_position_y + 20

        with self._window.frame:
            with ui.VStack(width=0, height=0):
                self._search_widget.build_ui(self.__parent.computed_content_width + 40, self._search_size)
                self._name_value_model = JointListModel(self._on_click_fn, self._joints_list, self._index)
                self._name_value_delegate = JointListDelegate()
                self._scrolling_frame = ui.ScrollingFrame(
                    height=self._get_treeview_height(),
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                )
                with self._scrolling_frame:
                    self._tree_view = ui.TreeView(
                        self._name_value_model,
                        delegate=self._name_value_delegate,
                        root_visible=False,
                        header_visible=False,
                        name="search_treeview",
                    )
                    self._select_index(self._tree_view, self._name_value_model, self._index)
                    self._tree_view.set_mouse_released_fn(lambda x, y, b, c: tree_view_clicked(self._tree_view))

    def destroy(self):
        self.__parent = None
        self.__frame = None
        self._window = None
        self._scrolling_frame = None


class SkelJointSelectionBox():
    def __init__(self, icon_path):
        self._icon_path = icon_path
        self._theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        self._search_widget = SearchWidget(theme=self._theme, icon_path=icon_path)
        self._listbox_widget = None

    def build_ui(self, skeleton, joints_list, selected_index, bind_joint_fn, show_extras: bool = True) -> None:
        if (len(joints_list) > 0):
            with ui.HStack(spacing=5):
                self._build_joint_popup(skeleton, joints_list, selected_index, bind_joint_fn)

    def _build_joint_popup(self, skeleton, joints_list: List[str], selected_index: int, bind_joint_fn: callable, show_extras: bool = False):
        def update_joint(model, b):
            string = model.get_value_as_string()
            self._search_widget.set_text(string)
            bind_joint_fn(string)

        name_field, listbox_button, goto_button = self._search_widget.build_ui_popup(
            search_size=18,
            popup_text=joints_list[selected_index],
            index=selected_index,
            update_fn=update_joint,
            widget_flags=SearchWidget.WidgetFlags.SHOW_OPEN_BUTTON
        )
        name_field.set_mouse_pressed_fn(lambda x, y, b, m, f=name_field: self._show_joint_popup(f, joints_list, selected_index, bind_joint_fn))

        listbox_button.set_mouse_pressed_fn(lambda x, y, b, m, f=name_field: self._show_joint_popup(f, joints_list, selected_index, bind_joint_fn))
        listbox_button.enabled = show_extras

        if show_extras:
            ui.Spacer(width=4)
            goto_button = ui.Button(
                "Assign",
                width=20,
                height=20,
                fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                name="assign"
            )
            goto_button.set_mouse_pressed_fn(lambda x, y, b, m, f=name_field: self._assign_currently_selected_joint(skeleton, f, bind_joint_fn))

    def _assign_currently_selected_joint(self, skeleton, name_field, bind_joint_fn):
        simple_joint = get_selected_joint(skeleton)
        if simple_joint is not None:
            self._search_widget.set_text(simple_joint)
            bind_joint_fn(simple_joint)

    def _show_joint_popup(self, name_field: ui.StringField, joints_list, selected_index: int, bind_joint_fn: callable):
        if self._listbox_widget:
            self._listbox_widget.clean()
            del self._listbox_widget
            self._listbox_widget = None

        def _joint_selected(joint_name, bind_joint_fn):
            self._search_widget.set_text(joint_name)
            bind_joint_fn(joint_name)

        self._listbox_widget = JointListBoxWidget(
            joints_list,
            selected_index,
            lambda joint_name: _joint_selected(joint_name, bind_joint_fn),
            theme=self._theme,
            icon_path=self._icon_path
        )
        self._listbox_widget.set_parent(name_field)
        self._listbox_widget.build_ui()


class SkelJointSelectionSearchable():

    def __init__(self, set_callback, skeleton, tag_name, joint, icon_path):
        self._selection_box = SkelJointSelectionBox(icon_path)
        self._set_callback = set_callback
        self._skeleton = skeleton
        self._tag_name = tag_name
        self._joint = joint
        self._build_ui()

    def __del__(self):
        del self._selection_box

    def set_selection(self, tag_name, joint):
        if (self._tag_name != tag_name or self._joint != joint):
            self._tag_name = tag_name
            self._joint = joint

    def set_tag_name(self, tag_name):
        self._tag_name = tag_name

    def _selection_changed(self, joint_name):
        if (self._joint != joint_name):
            self._joint = joint_name
            # this is odd if the joint name is None, it will break
            if self._joint == "None":
                self._set_callback(self._tag_name, "")
            else:
                self._set_callback(self._tag_name, self._joint)

    def _build_ui(self):
        if (self._skeleton):
            joints_list = [INVALID_JOINT_NAME]

            joint_attr = self._skeleton.GetJointsAttr()
            joints = convert_to_simple_joints(joint_attr.Get())
            selected_index = 0
            for i, joint in enumerate(joints):
                joints_list.append(joint)
                if joint == self._joint:
                    selected_index = i + 1
            self._selection_box.build_ui(self._skeleton, joints_list, selected_index, self._selection_changed)
