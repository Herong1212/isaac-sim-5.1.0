# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TypeModel"]

import omni.ui as ui


class TypeModel(ui.AbstractValueModel):
    def __init__(self, stage_item):
        super().__init__()
        self.__stage_item = stage_item

    def destroy(self):
        self.__stage_item = None

    def get_value_as_string(self) -> str:
        return self.__stage_item.type_name

    def set_value(self, value: str):
        pass
