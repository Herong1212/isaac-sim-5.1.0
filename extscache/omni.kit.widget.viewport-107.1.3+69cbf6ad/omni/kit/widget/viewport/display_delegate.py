# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['ViewportDisplayDelegate']

import omni.ui as ui


class ViewportDisplayDelegate:
    def __init__(self, viewport_api):
        self.__zstack = None
        self.__image_provider = None
        self.__image = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.__zstack:
            self.__zstack.clear()
            self.__zstack.destroy()
            self.__zstack = None
        if self.__image:
            self.__image.destroy()
            self.__image = None
        if self.__image_provider:
            self.__image_provider = None

    @property
    def image_provider(self):
        return self.__image_provider

    @image_provider.setter
    def image_provider(self, image_provider: ui.ImageProvider):
        if not isinstance(image_provider, ui.ImageProvider):
            raise RuntimeError('ViewportDisplayDelegate.image_provider must be an omni.ui.ImageProvider')

        # Clear any existing ui.ImageWithProvider
        # XXX: ui.ImageWithProvider should have a method to swap this out
        if self.__image:
            self.__image.destroy()
            self.__image = None

        self.__image_provider = image_provider
        self.__image = ui.ImageWithProvider(self.__image_provider,
                                            style_type_name_override='ViewportImage',
                                            name='Color')

    def create(self, ui_frame, prev_delegate, *args, **kwargs):
        # Save the previous ImageProvider early to keep it alive
        image_provider = prev_delegate.image_provider if prev_delegate else None
        self.destroy()
        with ui_frame:
            self.__zstack = ui.ZStack()
            with self.__zstack:
                if not image_provider:
                    image_provider = ui.ImageProvider(name='ViewportImageProvider')
                self.image_provider = image_provider

        return self.__zstack

    def update(self, viewport_api, texture, view, projection, presentation_key=0, metadata=None):
        self.__image_provider.set_image_data(texture, presentation_key=presentation_key, metadata=metadata)
        return self.size

    @property
    def size(self):
        return (int(self.__image.computed_width), int(self.__image.computed_height))


class OverlayViewportDisplayDelegate(ViewportDisplayDelegate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__overlay_image = None
        self.__overlay_provider = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.__overlay_image:
            self.__overlay_image.destroy()
            self.__overlay_image = None
        if self.__overlay_provider:
            self.__overlay_provider = None
        super().destroy()

    def create(self, ui_frame, prev_delegate, *args, **kwargs):
        # Grab the last image and put to push as the last element in the parent ui.Stack
        prev_provider = prev_delegate.image_provider if prev_delegate else None
        # Build the default ui for the Viewports display, but don't pass along any previous delegate/image
        ui_stack = super().create(ui_frame, None, *args, **kwargs)
        if ui_stack and prev_provider:
            # Clear any presentation-key embedded in the ImageProvider so it stays locked to the current content/image.
            # Check for None before assignment, as set_image_data will error on None
            # Then take the return value back into rsrc just to clear any ref-count.
            rsrc = prev_provider.get_managed_resource()
            if rsrc is not None:
                rsrc = prev_provider.set_image_data(rsrc)
            with ui_stack:
                self.__overlay_provider = prev_provider
                self.__overlay_image = ui.ImageWithProvider(self.__overlay_provider,
                                                            style_type_name_override='ViewportImageOverlay',
                                                            name='Overlay')
        return ui_stack

    def set_overlay_alpha(self, overlay_alpha: float):
        self.__overlay_image.set_style({
            'ViewportImageOverlay': {
                'color': ui.color(1.0, 1.0, 1.0, overlay_alpha)
            }
        })
