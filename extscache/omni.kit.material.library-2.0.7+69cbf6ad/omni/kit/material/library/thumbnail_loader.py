"""Material thumbnail loader class."""
__all__ = ["ThumbnailLoader"]

import asyncio
import copy
import omni.ui as ui
import omni.kit.material.library
from pxr import Usd


class ThumbnailLoader():
    """Material thumbnail loader class."""
    def __init__(self):
        self._thumbnail_tasks = []

    def purge(self): # pragma: no cover
        for task in copy.copy(self._thumbnail_tasks):
            if task.done():
                self._thumbnail_tasks.remove(task)

    async def set_material_thumbnail_url(self, thumbnail_image: ui.Image, thumbnail_url: str):
        if not thumbnail_url:
            return
        (result, entry) = await omni.client.stat_async(thumbnail_url)
        if result == omni.client.Result.OK:
            thumbnail_image.source_url = thumbnail_url
            self.purge()

    def load(self, material_prim: Usd.Prim, thumbnail_image: ui.Image):
        thumbnail_filename = omni.kit.material.library.get_material_filename_from_prim(material_prim)
        self._thumbnail_tasks.append(
            asyncio.ensure_future(
                self.set_material_thumbnail_url(thumbnail_image, thumbnail_filename)
            )
        )
