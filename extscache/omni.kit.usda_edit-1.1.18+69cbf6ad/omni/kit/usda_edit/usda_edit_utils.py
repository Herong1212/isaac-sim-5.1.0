# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.kit.app


def Singleton(class_):
    """
    A singleton decorator.

    TODO: It's also available in omni.kit.widget.stage. We need a utility
    extension where we can put the utilities like this.
    """
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance

def is_extension_loaded(extansion_name: str) -> bool:
    """
    Returns True if the extension with the given name is loaded.
    """

    def is_ext(id: str, extension_name: str) -> bool:
        id_name = id.split("-")[0]
        return id_name == extension_name

    app = omni.kit.app.get_app_interface()
    ext_manager = app.get_extension_manager()
    extensions = ext_manager.get_extensions()

    loaded = next((ext for ext in extensions if is_ext(ext["id"], extansion_name) and ext["enabled"]), None)

    return not not loaded

def post_notification(message: str, info: bool = False, duration: int = 3):
    try:
        import omni.kit.notification_manager as nm

        if info:
            type = nm.NotificationStatus.INFO
        else:
            type = nm.NotificationStatus.WARNING

        return nm.post_notification(message, status=type, duration=duration)
    except Exception:
        pass

    return None
