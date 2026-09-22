# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['ViewportWidgetExtension']

import omni.ext


class ViewportWidgetExtension(omni.ext.IExt):

    def on_shutdown(self):
        from .widget import ViewportWidget
        from .impl.utility import _report_error
        for instance in ViewportWidget.get_instances():  # pragma: no cover
            try:
                instance.destroy()
            except Exception:
                _report_error()
                raise
