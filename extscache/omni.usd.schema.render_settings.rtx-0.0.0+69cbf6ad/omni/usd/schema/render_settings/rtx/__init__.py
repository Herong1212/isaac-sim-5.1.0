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

Plug.Registry().RegisterPlugins(str(Path(__file__).parent.parent.parent.parent.parent.parent.joinpath("usd_plugins").resolve()))
