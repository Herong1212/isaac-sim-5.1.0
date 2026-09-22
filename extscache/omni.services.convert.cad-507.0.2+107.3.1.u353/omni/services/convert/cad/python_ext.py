# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

from .services.convert import ConverterRegistry, router
from .services.progress_facility import ProgressFacility

__all__ = ["ServiceConvertCADExtension", "ConverterRegistry"]


class ServiceConvertCADExtension(omni.ext.IExt):
    def on_startup(self):
        progress_facility = ProgressFacility()
        router.register_facility("progress", progress_facility)
        main.register_router(router, prefix="/convert/cad", tags=["cad"])

    def on_shutdown(self):
        main.deregister_router(router, prefix="/convert/cad")
