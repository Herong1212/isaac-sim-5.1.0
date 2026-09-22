# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["LiveSessionInterface"]

import abc

import omni.client


def make_session_link(layer_uri: str, session_name: str):
    """Create a session link uri by breaking the layer_uri and recomposing with live_session_name query key / value"""
    url = omni.client.break_url(layer_uri)
    return omni.client.make_url(
        scheme=url.scheme,
        host=url.host,
        port=url.port,
        user=url.user,
        path=url.path,
        query=f"live_session_name={session_name}"
    )


class LiveSessionInterface(metaclass=abc.ABCMeta):
    """LiveSession Interface"""
    @classmethod
    def __subclasshook__(cls, subclass):
        return all(hasattr(subclass, n) for n in (
            'name', 'url', 'owner', 'channel_url', 'base_layer_identifier', 'get_last_modified_time', 'shared_link')
        )

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The name of the Live Session."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def url(self) -> str:
        """The physical url of the Live Session in the server."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def owner(self) -> str:
        """
        The owner name of the Live Session. It returns the static owner name of the session only.
        If it has multiple instances of the same user join the same session, only one of the owner
        has the real merge_permission.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def channel_url(self) -> str:
        """The physical channel_url of the Live Session in the server."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def base_layer_identifier(self) -> str:
        """The base layer identifier of the Live Session."""
        return NotImplementedError

    @abc.abstractmethod
    def get_last_modified_time(self) -> int:
        """
        Gets the last modified time of the Live Session. The modified time is
        fetched from the session config file. It can be used to sort the Live Session
        list in access order.
        """
        raise NotImplementedError

    @property
    def shared_link(self) -> str:
        """
        The session link to be shared. Shared link is different as
        url, so url points to the physical location of the Live Session
        that local user can get access to, while session link is the URL
        that you can share to others, and can be launched from Omniverse launcher
        and other apps could parse it and decide the action from it. The session
        name is passed as the query parameter to the base layer url, for example,
        omniverse://localhost/test/stage.usd?live_session_name=my_session.
        """
        raise NotImplementedError
