# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
A UI alternative to omni.ui.StringField for navigating tree views with the keyboard. As the user
navigates the tree using TAB, Backspace, and Arrow keys, they are constantly provided branching 
options via auto-filtered tooltips.

Example:

.. code-block:: python

    path_field = PathField(
        apply_path_handler=self._apply_path_handler,
        branching_options_provider=self._branching_options_provider,
    )

"""
from .widget import PathField

__all__ = ['PathField']
