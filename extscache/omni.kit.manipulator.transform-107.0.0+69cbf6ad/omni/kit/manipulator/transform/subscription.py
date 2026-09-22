# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Callable


class Subscription:
    """A class representing a subscription to an event or notification.

    This class provides a method to unsubscribe and clean up resources when notifications or updates are no longer needed.

    Args:
        unsubscribe_fn (Callable): A callable to unsubscribe from the event or notification."""

    def __init__(self, unsubscribe_fn: Callable):
        """Initializes a new Subscription object with a callable to unsubscribe.

        Args:
            unsubscribe_fn (Callable): A callable that, when called, will unsubscribe this subscription and prevent any further notifications or updates.
        """
        self._unsubscribe_fn = unsubscribe_fn

    def __del__(self):
        """Handles the deletion of the Subscription object by calling unsubscribe to clean up resources."""
        self.unsubscribe()

    def unsubscribe(self):
        """Unsubscribes from the event or notification, preventing any further updates.
        If the subscription is already unsubscribed, this method does nothing."""
        if self._unsubscribe_fn:
            self._unsubscribe_fn()
            self._unsubscribe_fn = None
