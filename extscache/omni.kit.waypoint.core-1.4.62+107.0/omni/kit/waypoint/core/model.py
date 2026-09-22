from typing import Dict, List

from omni import ui
from omni.kit.browser.core import AbstractBrowserModel, CategoryItem, CollectionItem, DetailItem

from . import ViewportWaypoint, WaypointChangeCallbacks
from . import get_instance as get_waypoint_instance


class WaypointItem(DetailItem):
    """
    Represent a detail item for a waypoint in a stage.
    Args:
        waypoint (ViewportWaypoint): Waypoint object.
    """

    def __init__(self, waypoint: ViewportWaypoint):
        self.waypoint = waypoint

        thumbnail_data = waypoint.thumbnail_data
        if thumbnail_data:
            self.thumbnail_provider = ui.ByteImageProvider()
            byte_data, width, height = thumbnail_data
            self.thumbnail_provider.set_bytes_data(bytearray(byte_data), [width, height])
        else:  # pragma: no cover
            self.thumbnail_provider = None

        super().__init__(waypoint.name, waypoint.path, None)


class WaypointModel(AbstractBrowserModel):
    """
    Represent waypoints in opened stage.

    Args:
        on_waypoint_changed_fn: Callback when waypoint created/deleted/changed. Function signaure::

            def on_waypoint_changed_fn() -> None
    """

    def __init__(self, on_waypoint_changed_fn: callable = None):
        self._on_waypoint_changed_fn = on_waypoint_changed_fn
        self._waypoint_instance = get_waypoint_instance()
        self._waypoints: List[ViewportWaypoint] = []
        self._cached_detail_items: Dict[str, WaypointItem] = {}
        self._collection_item = CollectionItem("Stage", "stage")

        self._waypoint_callback = WaypointChangeCallbacks(
            self.on_waypoint_changed, self.on_waypoint_changed, self.on_waypoint_changed, self.on_waypoint_changed
        )
        self._waypoint_instance.register_callback(self._waypoint_callback)

        super().__init__()

    def destroy(self) -> None:
        self._waypoint_instance.deregister_callback(self._waypoint_callback)
        self._waypoint_instance = None

    def execute(self, item: WaypointItem) -> None:
        """
        Recall a waypoint
        """
        self._waypoint_instance.recall_waypoint(item.waypoint)

    def get_collection_items(self) -> List[CollectionItem]:
        return [self._collection_item]

    def get_category_items(self, item: CollectionItem) -> List[CategoryItem]:
        self._waypoints = self._waypoint_instance.get_waypoints()
        count = len(self._waypoints) if self._waypoints else 0
        return [CategoryItem("Stage", count)]

    def get_detail_items(self, item: CategoryItem) -> List[WaypointItem]:
        detail_items = []
        self._cached_detail_items = {}
        if self._waypoints:
            for waypoint in self._waypoints:
                self._cached_detail_items[waypoint] = WaypointItem(waypoint)
                detail_items.append(self._cached_detail_items[waypoint])
            detail_items.sort(key=lambda item: item.name)

        return detail_items

    def on_waypoint_changed(self, *_) -> None:
        self._item_changed(self._collection_item)
        if self._on_waypoint_changed_fn is not None:
            self._on_waypoint_changed_fn()
