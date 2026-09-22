import os
import omni.client


class PathUtils:
    @staticmethod
    def is_omni_objects_enabled_path(path: str):
        return omni.client.is_omni_objects_enabled(path)

    @staticmethod
    def is_omni_path(path: str): # pragma: no cover
        # this is used in extension out of kit
        return omni.client.is_omni_objects_enabled(path)

    @staticmethod
    def is_omni_live(path: str):
        url = omni.client.break_url(path)
        if not url:
            return False

        _, ext = os.path.splitext(url.path)
        return ext == ".live"
