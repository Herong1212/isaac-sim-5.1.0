# Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb.settings
import omni.kit.app


class OgnExitApplication:
    @staticmethod
    def compute(db) -> bool:
        carb.settings.get_settings().set("/app/fastShutdown", True)
        omni.kit.app.get_app().shutdown()
