# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb.settings

def reset_toolbar_settings():
    settings = carb.settings.get_settings()

    vals = {
        "/app/transform/operation": "move",
        "/persistent/app/viewport/pickingMode": "type:ALL",
        "/app/viewport/snapEnabled": False,
    }

    for key, val in vals.items():
        settings.set(key, val)
