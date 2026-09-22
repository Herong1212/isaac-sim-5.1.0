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

path = str(
    Path(carb.tokens.get_tokens_interface().resolve("${omni.usd.schema.omni_lens_distortion}"))
         .joinpath("usd_plugins").resolve()
)
Plug.Registry().RegisterPlugins(path)