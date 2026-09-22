# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import omni.ext
from omni.services.core import main
from omni.services.facilities.monitoring.metrics import facilities as _metrics_facilities

from .services import convert

__all__ = ["ServiceConvertAssetExtension"]


class ServiceConvertAssetExtension(omni.ext.IExt):

    def on_startup(self):
        metrics = _metrics_facilities.MetricsFacility("asset_convert")
        convert.router.register_facility("metrics", metrics)

        main.register_router(convert.router, prefix="/convert/asset", tags=["convert"])

    def on_shutdown(self):
        main.deregister_router(convert.router, prefix="/convert/asset")
