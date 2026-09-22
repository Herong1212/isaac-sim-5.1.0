import omni.kit.test

import omni.mdl.neuraylib   # interface the OV material backend
import omni.mdl.pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.pymdl       # high-level wrapper


class TestBasic(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    async def test_load_bindings(self):

        # we don't have the neuray instance here, but we should not crash in case we pass None
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        ov_neuraylib_handle = ov_neuraylib.getNeurayAPI()
        neuray: omni.mdl.pymdlsdk.INeuray = omni.mdl.pymdlsdk.attach_ineuray(ov_neuraylib_handle)
        self.assertIsNotNone(neuray)
        neuray = None
        ov_neuraylib = None
