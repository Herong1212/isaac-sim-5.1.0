# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["EventSubscription", "Event"]

class Event(list):
    """
    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.
    """

    def __call__(self, *args, **kwargs):
        """Called when the instance is “called” as a function"""
        # Call all the saved functions
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        """
        Called by the repr() built-in function to compute the “official”
        string representation of an object.
        """
        return f"Event({list.__repr__(self)})"


class EventSubscription:
    """
    Event subscription.

    Event has callback while this object exists.
    """

    def __init__(self, event, fn):
        """
        Save the function, the event, and add the function to the event.
        """
        self._fn = fn
        self._event = event
        event.append(self._fn)

    def destroy(self):
        if self._fn in self._event:
            self._event.remove(self._fn)

    def __del__(self):
        """Called by GC."""
        self.destroy()
