import omni.kit.test
import omni.kit.app
import omni.anim.navigation

import carb
import carb.events
import carb.dictionary


class TestNavigation(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._iface = omni.anim.navigation.get_navigation_interface()
