from .icons import Icons


class Styles:
    CACHE_STATE_ITEM_STYLE = None
    LIVE_STATE_ITEM_STYLE = None

    @staticmethod
    def on_startup():
        # It needs to delay initialization of style as icons need to be initialized firstly.
        Styles.CACHE_STATE_ITEM_STYLE = {
            "Image::doc": {"image_url": Icons.get("docs"), "color": 0xB04B4BFF},
            "Label::offline": {"color": 0xB04B4BFF},
            "Rectangle::offline": {"border_radius": 2.0},
            "Rectangle::offline": {"background_color": 0xff808080},
            "Rectangle::offline:hovered": {"background_color": 0xFF9E9E9E},
        }

        Styles.LIVE_STATE_ITEM_STYLE = {
            "Label": {"color": 0xffffffff},
            "Image::lightning": {"image_url": Icons.get("lightning")},
            "Image::arrow_down": {"image_url": Icons.get("arrow_down"), "color": 0xffffffff},
            "Rectangle": {"border_radius": 2.0},
            "Rectangle:hovered": {"background_color": 0xFF9E9E9E},
            "Rectangle::offline": {"background_color": 0xff808080},
            "Rectangle::live": {"background_color": 0xff00b86b}
        }
