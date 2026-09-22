from pathlib import Path

from omni.ui import color as cl

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("icons")

UI_STYLE = {
    "Menu.Item.Icon::UnlockedCamera": {"image_url": f"{ICON_PATH}/camera_viewport.svg"},
    "Menu.Item.Icon::UnlockedCameraWithoutHovered": {"image_url": f"{ICON_PATH}/camera_viewport.svg"},
    "Menu.Item.Icon::UnlockedCamera:hovered": {"image_url": f"{ICON_PATH}/lock_dark.svg"},
    "Menu.Item.Icon::LockedCamera": {"image_url": f"{ICON_PATH}/viewport_cameras_locked.svg"},
    "Menu.Item.Icon::LockedCameraWithoutHovered": {"image_url": f"{ICON_PATH}/viewport_cameras_locked.svg"},
    "Menu.Item.Icon::LockedCamera:hovered": {"image_url": f"{ICON_PATH}/unlock_dark.svg"},
    "Menu.Item.Icon::Expand": {"image_url": f"{ICON_PATH}/expand.svg", "color": cl.viewport_menubar_background},
    "Menu.Item.Icon::Expand:checked": {"image_url": f"{ICON_PATH}/contract.svg"},
    "Menu.Item.Icon::Lock": {"image_url": f"{ICON_PATH}/unlock_dark.svg", "color": cl.viewport_menubar_background},
    "Menu.Item.Icon::Lock:checked": {"image_url": f"{ICON_PATH}/lock_dark.svg"},
    "Menu.Item.Icon::Sample": {"image_url": f"{ICON_PATH}/focalSample_viewport.svg"},
    "Menu.Item.Icon::Sample:disabled": {"color": cl.viewport_menubar_medium},
    "Menu.Item.Icon::Add": {"image_url": f"{ICON_PATH}/add.svg", "color": cl.viewport_menubar_selection_border},
    "Menu.Item.Icon::Lens": {"image_url": f"{ICON_PATH}/lens.svg"},
    "Menu.Item.Icon::FocalDistance": {"image_url": f"{ICON_PATH}/focal_distance.svg"},
    "Menu.Item.Icon::FStop": {"image_url": f"{ICON_PATH}/Fstop.svg"},
    "Menu.Item.Button": {
        "background_color": 0,
        "margin": 0,
        "padding": 0,
    },
    "Menu.Item.Button.Image::OptionBox": {"image_url": f"{ICON_PATH}/settings_submenu.svg"},
    "Menu.Item.Button.Image::CameraLocked": {"image_url": f"{ICON_PATH}/lock_dark.svg"},
    "Menu.Item.Button.Image::CameraUnlocked": {"image_url": f"{ICON_PATH}/unlock_dark.svg"},
    "MenuBar.Item::transparent": {
        # "color": 0,
    },
}
