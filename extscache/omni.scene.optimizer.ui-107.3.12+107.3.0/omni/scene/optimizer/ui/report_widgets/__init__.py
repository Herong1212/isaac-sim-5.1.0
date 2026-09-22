__copyright__ = "Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


# Add imports here so that report.py can find them when attempting to
# dynamically instantiate based on the operation name.
from .coinciding import CoincidingWidget
from .generic import GenericWidget
from .merge import MergeWidget
from .stats import StatsWidget
