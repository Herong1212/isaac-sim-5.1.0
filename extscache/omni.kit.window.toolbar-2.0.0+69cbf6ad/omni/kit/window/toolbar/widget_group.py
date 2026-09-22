# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.kit.app
omni.kit.app.log_deprecation(
    '"import omni.kit.window.toolbar.widget_group" is deprecated. '
    'Please use "import omni.kit.widget.toolbar.widget_group"'
)

try:  # pragma: no cover
    import inspect
    for stackframe in inspect.stack():
        if stackframe.code_context is None:
            continue
        code = stackframe.code_context[0]
        if code and code.startswith(("import", "from")):
            # name of importing file
            omni.kit.app.log_deprecation(f"Imported from {stackframe.filename}")
            break
except:  # pragma: no cover
    pass

from omni.kit.widget.toolbar.widget_group import *  # backward compatible
