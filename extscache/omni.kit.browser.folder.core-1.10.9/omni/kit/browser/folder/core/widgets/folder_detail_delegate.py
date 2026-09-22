__all__ = ["FolderDetailDelegate"]
from pathlib import Path
from typing import Optional

from omni.kit.browser.core import DetailDelegate
from ..models import FolderBrowserModel, FileDetailItem


class FolderDetailDelegate(DetailDelegate):
    """
    Delegate to show folder item in detail view.
    Keyword args:
        model (FolderBrowserModel): Folder browser model. Default None.
    """

    def __init__(self, model: FolderBrowserModel = None):
        super().__init__(model=model)

        self.hide_label: bool = False

    def destroy(self) -> None:
        super().destroy()

    def get_tooltip(self, item: FileDetailItem) -> str:
        return item.url

    def get_label(self, item: FileDetailItem) -> Optional[str]:
        return None if self.hide_label else Path(item.name).stem

    def get_label_height(self) -> int:
        # return 0 if self.hide_label else two lines for small thumbnail size and one line for large thumbnail size
        if self.hide_label:
            return 0
        elif self.thumbnail_size <= 192:
            return 40
        else:
            return 20
