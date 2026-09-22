# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path
from pxr import Plug
import carb

Plug.Registry().RegisterPlugins(str(
    Path(carb.tokens.get_tokens_interface().resolve("${omni.usd.schema.omni_sensors}"))
         .joinpath("usd_plugins").resolve()
))
