# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
The :obj:`PathField` widget supes up tree navigation via keyboard entry. This widget extends that
experience further by queuing up the user's navigation history. As in any modern day browser, the
user can then directly jump to any previously visited path.

Example:

.. code-block:: python

    browser_bar = BrowserBar(
        visited_history_size=20,
        branching_options_provider=branching_options_provider,
        apply_path_handler=apply_path_handler,
    )

"""
__all__ = ["BrowserBar"]
from .widget import BrowserBar
