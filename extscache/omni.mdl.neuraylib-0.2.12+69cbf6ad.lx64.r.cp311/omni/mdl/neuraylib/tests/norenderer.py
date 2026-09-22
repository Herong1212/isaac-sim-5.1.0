from omni.kit.test.async_unittest import AsyncTestCase

import omni.mdl.neuraylib   # interface the OV material backend
import omni.mdl.pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.pymdl       # high-level wrapper

from pxr import Ar

# Note, this test is explicitly running without rtx.hydra or any extensions that require to startup neuray
class NoRendererTest(AsyncTestCase):

    # make sure neuray is loaded to enable MDL resource resolution in USD
    # otherwise, we would need call `omni.mdl.neuraylib.get_neuraylib()` and attach the neuray instance to the binding
    async def test_assure_running(self):

        # neuray is not loaded, so the USD AR doesn't know about MDL search paths
        resolved_path: str = str(Ar.GetResolver().Resolve('nvidia/core_definitions.mdl'))
        print(f"resolved_path before: {resolved_path}")
        self.assertEqual(resolved_path, "")

        # this starts neuray
        omni.mdl.neuraylib.ensure_running()

        # and now, USD AR should know about MDL search paths
        resolved_path = str(Ar.GetResolver().Resolve('nvidia/core_definitions.mdl'))
        print(f"resolved_path after: {resolved_path}")
        self.assertNotEqual(resolved_path, "")