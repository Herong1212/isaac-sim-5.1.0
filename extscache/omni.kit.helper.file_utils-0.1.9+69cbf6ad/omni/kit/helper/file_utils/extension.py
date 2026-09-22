# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
import omni.ext
import omni.client
import carb.settings
from dataclasses import dataclass, asdict

from typing import List, Tuple, Optional
from datetime import datetime
from urllib import parse
from carb import eventdispatcher, log_warn
from collections import OrderedDict
from omni.kit.helper.file_utils import asset_types
from . import FILE_OPENED_GLOBAL_EVENT, FILE_SAVED_GLOBAL_EVENT, FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT

g_singleton = None


@dataclass
class FileEventModel:
    """A data model representing a file event within the application.

    This class holds information about a file-related event, such as opening or saving a file.

    Args:
        url: str
            The URL of the file associated with the event.
        asset_type: Optional[str]
            The type of asset involved in the event (e.g., image, model).
        is_folder: Optional[bool]
            Flag indicating whether the URL points to a folder.
        event_type: Optional[int]
            Numerical ID representing the type of event (e.g., opened, saved).
        tag: Optional[str]
            An optional tag providing additional context for the event.
        datetime: Optional[datetime]
            Timestamp of when the event occurred."""

    url: str
    """The URL of the file associated with the event."""
    asset_type: Optional[str] = None
    """The type of asset involved in the event (e.g., image, model)."""
    is_folder: Optional[bool] = False
    """Flag indicating whether the URL points to a folder."""
    event_type: Optional[int] = None
    """Numerical ID representing the type of event (e.g. opened, saved)."""
    event_name: Optional[str] = None
    """String name representing the type of event (e.g. opened, saved)."""
    tag: Optional[str] = None
    """An optional tag providing additional context for the event."""
    datetime: Optional[datetime] = None
    """ Timestamp of when the event occurred."""

    def dict(self):
        """
        Returns a dictionary representation of FileEventModel object.

        Returns:
            dict: A dictionary containing the object's attributes as key-value pairs.
        """
        return asdict(self)


class FileEventHistoryExtension(omni.ext.IExt):
    """A class for managing the history of file events within an application.

    This class subscribes to file events, maintains a queue of these events up to a specified maximum size, and provides methods for querying and manipulating this event history. It is designed to integrate with an application's event system, capturing information about file operations such as opening and saving files.

    Args:
        max_queue_size (int): The maximum number of events to retain in the queue."""

    FILE_EVENT_QUEUE_SETTING = "/persistent/app/omniverse/fileEventHistory"

    def __init__(self, max_queue_size: int = 100):
        super().__init__()
        self._event_subs = []
        self._event_queue = None
        self._max_queue_size = max_queue_size

        # set up singleton
        global g_singleton
        g_singleton = self

    def on_startup(self, ext_id: str):
        # Listen for file open and file save events
        from carb.eventdispatcher import get_eventdispatcher

        self._event_subs = [
            get_eventdispatcher().observe_event(event_name=FILE_OPENED_GLOBAL_EVENT, on_event=self._on_file_event),
            get_eventdispatcher().observe_event(event_name=FILE_SAVED_GLOBAL_EVENT, on_event=self._on_file_event),
        ]

    @property
    def event_queue(self):
        if self._event_queue is None:
            self._event_queue = self._load_queue_from_settings()
        return self._event_queue

    def _load_queue_from_settings(self) -> OrderedDict:
        queue = OrderedDict()
        settings = carb.settings.get_settings()
        for uri in settings.get(self.FILE_EVENT_QUEUE_SETTING) or []:
            url, file_event = self._deserialize_uri(uri)
            if url and file_event:
                queue[url] = file_event
                queue.move_to_end(url, last=True)
        self._adjust_queue_size(queue)
        return queue

    def _save_queue_to_settings(self, queue: OrderedDict):
        uris = []
        for url, file_event in queue.items():
            uri = self._serialize_uri(file_event)
            if not uri in uris:
                uris.append(uri)
        settings = carb.settings.get_settings()
        if settings:
            settings.set_string_array(self.FILE_EVENT_QUEUE_SETTING, uris)

    def _serialize_uri(self, file_event: FileEventModel) -> str:
        url_parts = omni.client.break_url(file_event.url)
        params = {"is_folder": file_event.is_folder, "event_type": file_event.event_type, "tag": file_event.tag or ""}
        uri = omni.client.make_url(
            scheme=url_parts.scheme or "file", host=url_parts.host, path=url_parts.path, query=parse.urlencode(params)
        )
        return uri

    def _deserialize_uri(self, uri: str) -> Tuple[str, FileEventModel]:
        url_parts = omni.client.break_url(uri)
        url = omni.client.make_url(scheme=url_parts.scheme, host=url_parts.host, path=url_parts.path)
        file_event = None
        try:
            params = parse.parse_qs(url_parts.query, strict_parsing=False, keep_blank_values=False)
            file_event = FileEventModel(
                url=url,
                asset_type=asset_types.get_asset_type(url),
                is_folder=params.get("is_folder", ["False"])[0] == "True",
                event_type=int(params.get("event_type", ["0"])[0]),
                tag=params.get("tag", [None])[0],
                datetime=datetime.utcnow(),
            )
        except Exception as e:
            log_warn(f"Failed to deserialize file event uri: {str(e)}")

        return url, file_event

    def _adjust_queue_size(self, queue: OrderedDict):
        while len(queue) > self._max_queue_size:
            # Delete items from the tail end
            queue.popitem(last=True)

    def _on_file_event(self, event: eventdispatcher.Event):
        from carb.events import type_from_string
        event_queue = self.event_queue
        try:
            # Ensure payload fits expected data model
            url = event["url"]
            file_event = FileEventModel(
                url=url,
                asset_type=asset_types.get_asset_type(url),
                is_folder=event["is_folder"],
                event_name=event.event_name,
                event_type=type_from_string(event.event_name),
                tag=event["tag"],
                datetime=datetime.utcnow(),
            )
        except Exception as e:
            log_warn(f"Failed to deserialize file event uri: {str(e)}")
            return

        # Insert at head of queue
        event_queue[url] = file_event
        event_queue.move_to_end(url, last=False)
        self._adjust_queue_size(event_queue)
        self._save_queue_to_settings(event_queue)
        omni.kit.app.queue_event(FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT)

    def get_latest_urls_from_event_queue(
        self, num_latest: int = 1, asset_type: str = None, event_type: int = 0, event_name: str = None, tag: str = None
    ) -> List[str]:
        urls = []
        for url, file_event in self.event_queue.items():
            if asset_type and file_event.asset_type != asset_type:
                continue
            elif event_name and file_event.event_name != event_name:
                continue
            elif event_type and file_event.event_type != event_type:
                continue
            elif tag and file_event.tag != tag:
                continue
            urls.append(url)
            if len(urls) >= num_latest:
                break
        return urls

    def clear_event_queue(self):
        queue = self.event_queue
        queue.clear()
        self._save_queue_to_settings(queue)
        omni.kit.app.queue_event(FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT)

    def on_shutdown(self):
        self._save_queue_to_settings(self.event_queue)
        self._event_queue = None
        self._event_subs.clear()

        global g_singleton
        g_singleton = None


def get_instance():
    return g_singleton
