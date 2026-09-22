# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
A set of simple popup dialogs with optional input fields and two buttons, OK and Cancel.

Example:

.. code-block:: python

    dialog = InputDialog(
        width=450,
        pre_label="prefix",
        post_label="postfix",
        ok_handler=on_okay,
        cancel_handler=on_cancel,
    )

"""
__all__ = [
    'MessageDialog', 'MessageWidget',
    'InputDialog', 'InputWidget', 
    'FormDialog', 'FormWidget',
    'OptionsDialog', 'OptionsWidget',
    'OptionsMenu', 'OptionsMenuWidget',
    'PopupDialog'
]

from .message_dialog import MessageDialog, MessageWidget
from .input_dialog import InputDialog, InputWidget
from .form_dialog import FormDialog, FormWidget
from .options_dialog import OptionsDialog, OptionsWidget
from .options_menu import OptionsMenu, OptionsMenuWidget
from .dialog import PopupDialog
