import omni.ui as ui

import omni.kit.usd.layers as layers


class LiveSessionUserModel(ui.AbstractValueModel):
    def __init__(self, peer_user: layers.LiveSessionUser):
        super().__init__()
        self._peer_user = peer_user

    @property
    def peer_user(self):
        return self._peer_user

    @peer_user.setter
    def peer_user(self, value):
        self._peer_user = value

    def destroy(self):
        self._peer_user = None

    def get_value_as_string(self):
        if self._peer_user:
            return layers.get_short_user_name(self._peer_user.user_name)
        else:
            return ""

    def set_value(self, value):
        # Cannot change layer name
        pass
