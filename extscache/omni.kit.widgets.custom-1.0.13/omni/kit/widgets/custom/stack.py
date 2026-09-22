from omni import ui


# A ZStack that will block mouse events to deeper
class OpaqueZStack(ui.ZStack):
    def __init__(self, **kwargs):
        kwargs["opaque_for_mouse_events"] = True
        if "mouse_pressed_fn" not in kwargs:
            kwargs["mouse_pressed_fn"] = lambda *_: self._dummy()

        super().__init__(**kwargs)

    def _dummy(self):
        pass
