# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.


class Facility:
    """
    Base class for all stateful type objects (pooling, etc.) that can be injected into services at runtime.

    When registered with the `ServiceAPIRouter`, they can be retrieved from service function handlers through dependency
    injection.
    """

    def stop(self):
        pass
