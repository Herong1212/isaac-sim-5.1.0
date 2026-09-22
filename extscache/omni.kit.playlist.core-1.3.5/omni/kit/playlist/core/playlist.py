import getpass
import os
import time
from typing import Optional, Union

import carb
import omni.client
import omni.usd
from omni import ui
from omni.kit.widgets.custom import SimpleListItem, SimpleListModel
from pxr import Sdf, Tf, Usd, UsdGeom

from .constant import PLAYLISTS_ROOT, PlayMode
from .playlist_card import PlaylistCard, enum_playlist_cards

STAGE_ITEM_CLASS = "omni.kit.widget.stage.stage_model.StageItem"
WAYPOINT_DRAG_PAYLOAD_PREFIX = "waypoint::"


class Column:
    NAME = 1
    TYPE = 2
    ID = 0
    COUNT = 3


class CardItem(SimpleListItem):
    """Single item of playlist card"""

    def __init__(self, card: PlaylistCard, index):
        super().__init__([f"{index+1}##int", card.name, card.type])
        self._sub_id = None

        self.data = card

    @property
    def name_model(self):
        return ui.SimpleStringModel(self.data.name)

    @property
    def type_model(self):
        return self.get_value_model(Column.TYPE)

    @property
    def index_model(self):
        return self.get_value_model(Column.ID)

    def active(self) -> None:
        self.data.active()

    def _get_values(self, card: PlaylistCard, index):
        return [f"{index}##int", card.name, card.type]

    def change_index(self, differ):
        # print(f"{self.name_model.as_string}: index change from {self.index_model.as_int} to {self.index_model.as_int + differ}")
        self.index_model.set_value(self.index_model.as_int + differ)

    def set_index(self, index):
        # print(f"{self.name_model.as_string}: index set from {self.index_model.as_int} to {index+1}")
        self.index_model.set_value(index + 1)

    def subscribe_index_changed_fn(self, fn):
        self._sub_id = self.index_model.subscribe_value_changed_fn(fn)

    def get_value_model(self, index=0):
        if index == Column.NAME:
            return self.name_model
        else:
            return super().get_value_model(index)

    def __repr__(self):
        return f'"{self.index_model.as_string}: {self.name_model.as_string} {self.type_model.as_string}"'


class PlaylistModel(SimpleListModel):
    """
    Represents camera lists.

    Args:
        name (str): Name of this playlist

    Keyword Args:
        on_changed_fn (Callable[[PlaylistModel], None): Callback when this playlist changed. Default None.
        system (bool): If this a system playlist. True means could not be changed. Default False.
        transition_type (PlayMode): Play mode. Could be PlayMode.TRANSITION_CUT or PlayMode.TRANSITION_SMOOTH. Default PlayMode.TRANSITION_CUT.
        transition_time (float): Transition time in seconds when playing a item. Default 5.
        item_time (float): Time in seconds to stay at this item during playing. Default 5
        on_dropped_fn (Callable[[int], None]): Callback when dropped to a new location. Default None.
        path (Optional[str]): Prim path to save playlist. Default None
        auto_active (bool): Auto active item if item is selected. Default True
    """

    def __init__(
        self,
        name: str,
        on_changed_fn: callable = None,
        system=False,
        transition_type=PlayMode.TRANSITION_CUT,
        transition_time=5,
        item_time=5,
        on_dropped_fn: callable = None,
        path: Optional[str] = None,
        auto_active: bool = True,
    ):
        super().__init__(columns_count=1, enable_drag_drop=True)

        self._name = name
        self.path = path
        if not path and name:
            self.path = f"{PLAYLISTS_ROOT}/{Tf.MakeValidIdentifier(name)}"

        self._on_changed_fn = on_changed_fn
        self._on_dropped_fn = on_dropped_fn
        self._system = system
        self.auto_active = auto_active

        # Play options
        self._transition_type = transition_type
        self.transition_time_model = ui.SimpleFloatModel(transition_time)
        self.item_time_model = ui.SimpleFloatModel(item_time)

        # Default attributes
        username = self._get_created_by()
        self._attributes = [["Author", username], ["Data_Added", time.strftime("%m-%d-%Y", time.localtime())]]

        # Playing index
        self.index_model = ui.SimpleIntModel(-1)
        self.__sub_index = self.index_model.subscribe_value_changed_fn(self.__on_index_changed)
        # Playing flag
        self.playing_model = ui.SimpleBoolModel(False)

    @property
    def name(self):
        """Name of this playlist"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def transition_type(self) -> PlayMode:
        """Playlist transition type"""
        return self._transition_type

    @transition_type.setter
    def transition_type(self, value: PlayMode):
        if value != self._transition_type:
            self._transition_type = value
            self.save()

    @property
    def transition_time(self) -> float:
        """Item transition time"""
        return self.transition_time_model.as_float

    @transition_time.setter
    def transition_time(self, value: float) -> None:
        if value != self.transition_time_model.as_float:
            self.transition_time_model.set_value(value)
            self.save()

    @property
    def item_time(self) -> float:
        """Item time to stay during playing"""
        return self.item_time_model.as_float

    @item_time.setter
    def item_time(self, value: float) -> None:
        if value != self.item_time_model.as_float:
            self.item_time_model.set_value(value)
            self.save()

    @property
    def attributes(self):
        """Playlist attributes"""
        return self._attributes

    @attributes.setter
    def attributes(self, value):
        self._attributes = value

    @property
    def system(self):
        """If a system playlist"""
        return self._system

    @property
    def auto_save(self):
        """Auto save playlist"""
        return not self._system

    @property
    def can_change(self):
        """If playlist could be changed"""
        return not self._system

    @property
    def selection(self) -> Optional[CardItem]:
        """Selected playlist card"""
        index = self.index_model.as_int
        if index >= 0 and index < len(self.items):
            return self.items[index]
        else:
            return None

    @selection.setter
    def selection(self, item: Optional[CardItem]) -> None:
        if item is None:
            self.index_model.set_value(-1)
        elif item in self.items:
            index = self.items.index(item)
            if index != self.index_model.as_int:
                self.index_model.set_value(index)

    def set_dropped_fn(self, on_dropped_fn: callable):
        self._on_dropped_fn = on_dropped_fn

    def check_update(self):
        return

    def save(self) -> None:
        if self._on_changed_fn is not None:
            self._on_changed_fn(self)

    def insert_item(self, item: Union[CardItem, PlaylistCard], index=-1, notify=True):
        """Insert new camera"""
        if index == -1:
            index = len(self._children)

        if isinstance(item, PlaylistCard):
            # item is playlist card
            item = CardItem(item, index)
        else:
            # Update item index
            item.set_index(index)
        super().insert_item(item, index)

        # change item index after inserted location
        for item in self._children[index + 1 :]:
            item.change_index(1)

        if notify:
            self._item_changed(None)
            if self._on_changed_fn is not None:
                self._on_changed_fn(self)

        return index

    def remove_item(self, item: Union[int, CardItem]):
        if isinstance(item, int):
            index = item
        else:
            index = self._children.index(item)
        self.remove_index(index)

    def remove_index(self, index: int):
        super().remove_index(index)

        for item in self._children[index:]:
            item.change_index(-1)

        self._item_changed(None)
        if self._on_changed_fn is not None:
            self._on_changed_fn(self)

    @property
    def previous_index(self) -> int:
        """Index of previous item"""
        if self.index_model.as_int < 0:
            # None selected, set to last
            index = len(self._children) - 1
        else:
            index = self.index_model.as_int - 1
        if index < 0:
            if len(self._children) > 0:
                # Loop to last
                index = len(self._children) - 1
            else:
                return -1

        return index

    def previous(self) -> int:
        """Select previous item"""
        index = self.previous_index
        if index >= 0:
            self.index_model.set_value(index)

        return index

    @property
    def next_index(self) -> int:
        """Index of next item"""
        if self.index_model.as_int < 0:
            # None selected, set to first
            index = 0
        else:
            index = self.index_model.as_int + 1
        if index >= len(self._children):
            if len(self._children) == 0:
                carb.log_warn("No items in playlist")
                return -1
            else:
                # Loop to first
                index = 0
        return index

    def next(self) -> int:
        """Select next"""
        index = self.next_index
        if index >= 0:
            self.index_model.set_value(index)

        return index

    """Enable drag and drop"""

    def get_drag_mime_data(self, item):
        """Returns Multipurpose Internet Mail Extensions (MIME) data for be able to drop this item somewhere"""
        # As we don't do Drag and Drop to the operating system, we return the string.
        return item.name_model.as_string

    def drop_accepted(self, target_item, source, drop_location=-1):
        """Reimplemented from AbstractItemModel. Called to highlight target when drag and drop."""
        if isinstance(source, CardItem):
            print(f"drop card item: {target_item}, {drop_location}")
            return super().drop_accepted(target_item, source, drop_location)
        elif isinstance(source, omni.kit.widget.stage.stage_model.StageItem):
            # Drop from stage item
            return self._drop_accepted_prim_path(str(source))
        elif isinstance(source, str):
            # Prim path from waypoint manager and markup tool
            return self._drop_accepted_prim_path(source)
        else:
            return False

    def drop(self, target_item, source, drop_location=-1):
        """Reimplemented from AbstractItemModel. Called when dropping something to the item."""
        if isinstance(source, CardItem):
            super().drop(target_item, source, drop_location)
        elif isinstance(source, omni.kit.widget.stage.stage_model.StageItem):
            # Drop from stage item
            self._drop_prim_path(target_item, str(source), drop_location)
        elif isinstance(source, str):
            # Prim path from waypoint manager and markup tool
            self._drop_prim_path(target_item, source, drop_location)

    def _drop_prim_path(self, target_item, source, drop_location=-1):
        stage = omni.usd.get_context().get_stage()
        if not stage:
            return
        if not source:
            return

        # Comes from waypoint manager
        if source.startswith(WAYPOINT_DRAG_PAYLOAD_PREFIX):
            source = source[len(WAYPOINT_DRAG_PAYLOAD_PREFIX) :]

        prim = stage.GetPrimAtPath(source)
        if not prim:
            return

        card = PlaylistCard.create(camera_prim=prim)
        if card:
            self.insert_item(card, index=drop_location)
            if self._on_dropped_fn is not None:
                self._on_dropped_fn(drop_location)

    def _drop_accepted_prim_path(self, path):
        stage = omni.usd.get_context().get_stage()
        if stage and path:
            # Comes from waypoint manager
            if path.startswith(WAYPOINT_DRAG_PAYLOAD_PREFIX):
                path = path[len(WAYPOINT_DRAG_PAYLOAD_PREFIX) :]

            prim = stage.GetPrimAtPath(str(path))
            if prim:
                if prim.IsA(UsdGeom.Camera):
                    return True
                card = PlaylistCard.create(camera_prim=prim)
                if card:
                    return True
                return False
        else:
            return False

    def __on_index_changed(self, model: ui.SimpleIntModel) -> None:
        index = model.as_int
        if self.auto_active and index >= 0 and index < len(self.items):
            item = self.items[index]
            item.data.active()
            carb.log_info(f"[Playlist] Switch camera to: {item.data.path}")

    # OM-79712 - Grabbing the user name, either from the current file, or `getpass.getuser()`
    def _get_created_by(self):
        user_name = ""
        stage: Usd.Stage
        if stage := omni.usd.get_context().get_stage():
            path = stage.GetEditTarget().GetLayer().identifier
            res, inf = omni.client.get_server_info(path)
            if res == omni.client.Result.OK:
                user_name = inf.username
        if not user_name:
            return getpass.getuser()
        return user_name


class SystemPlaylistModel(PlaylistModel):
    def __init__(self, name, camera_type):
        self._camera_type = camera_type
        super().__init__(name, system=True)

        # overwrite attributes
        self._attributes = [["Author", "System"], ["Data_Added", time.strftime("%m-%d-%Y", time.localtime())]]

    @property
    def camera_type(self):
        return self._camera_type

    def check_update(self):
        cameras = []
        for card in enum_playlist_cards():
            if card.type != self._camera_type:
                continue
            cameras.append(card)

        def sort_by_name(camera):
            return camera.name

        cameras.sort(key=sort_by_name)

        self.clear()
        for camera in cameras:
            self.insert_item(camera)
