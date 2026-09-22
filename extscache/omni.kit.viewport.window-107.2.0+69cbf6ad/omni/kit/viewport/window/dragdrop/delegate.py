# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['DragDropDelegate']

import weakref


class DragDropDelegate:
    # Use a list to track drag-drop order so that it's deterministic in the event of clashes or cancelation.
    __g_registered = []

    @classmethod
    def get_instances(cls):
        remove = []
        for wref in DragDropDelegate.__g_registered:
            obj = wref()
            if obj:
                yield obj
            else:
                remove.append(wref)
        for wref in remove:
            DragDropDelegate.__g_registered.remove(wref)

    def __init__(self):
        self.__g_registered.append(weakref.ref(self, lambda r: DragDropDelegate.__g_registered.remove(r)))

    def __del__(self):
        self.destroy()

    def destroy(self):
        for wref in DragDropDelegate.__g_registered:
            if wref() == self:
                DragDropDelegate.__g_registered.remove(wref)
                break

    @property
    def add_outline(self) -> bool:
        return False

    def accepted(self, drop_data: dict) -> bool:
        return False

    def update_drop_position(self, drop_data: dict) -> bool:
        return True

    def dropped(self, drop_data: dict) -> None:
        pass

    def cancel(self, drop_data: dict) -> None:
        pass
