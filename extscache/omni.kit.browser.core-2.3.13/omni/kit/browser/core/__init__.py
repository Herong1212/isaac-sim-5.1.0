__all__ = ["AbstractBrowserModel", "CategoryItem", "CollectionItem", "DetailItem", "BrowserSearchBar", "BrowserWidget", "CategoryDelegate", "DetailDelegate", "OptionsMenu", "OptionMenuDescription", "TreeBrowserWidget", "TreeCategoryDelegate", "create_drop_helper"]

from typing import Callable

from .models import AbstractBrowserModel, CategoryItem, CollectionItem, DetailItem
from .widgets import (
    BrowserSearchBar,
    BrowserWidget,
    CategoryDelegate,
    DetailDelegate,
    OptionMenuDescription,
    OptionsMenu,
    TreeBrowserWidget,
    TreeCategoryDelegate,
)


def get_legacy_viewport_interface():
    try:
        import omni.kit.viewport_legacy

        return omni.kit.viewport_legacy.get_viewport_interface()
    except ImportError:
        pass

    try:
        import omni.kit.viewport

        return omni.kit.viewport.get_viewport_interface()
    except ImportError:
        pass
    except AttributeError:
        pass

    return None


def create_drop_helper(
    pickable: bool = False,
    add_outline: bool = True,
    on_drop_accepted_fn: Callable = None,
    on_drop_fn: Callable = None,
    on_pick_fn: Callable = None,
    protocal: str = None
):
    try:
        try:
            from omni.kit.viewport.window import create_drop_helper as create_viewport_drop_helper
        except ImportError:
            from omni.kit.viewport.window.dragdrop import create_drop_helper as create_viewport_drop_helper

        if protocal is not None:
            from omni.kit.viewport.window.dragdrop.scene_drop_delegate import SceneDropDelegate
            SceneDropDelegate.add_ignored_protocol(protocal)

        return create_viewport_drop_helper(
            pickable=pickable,
            add_outline=add_outline,
            on_drop_accepted_fn=on_drop_accepted_fn,
            on_drop_fn=on_drop_fn,
            on_pick_fn=on_pick_fn
        )

    except ImportError:
        viewport = get_legacy_viewport_interface()
        if viewport:
            return viewport.create_drop_helper(
                pickable=pickable,
                add_outline=add_outline,
                on_drop_accepted_fn=on_drop_accepted_fn,
                on_drop_fn=on_drop_fn,
                on_pick_fn=on_pick_fn
            )
    return None