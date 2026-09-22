import omni.kit.test
import os

# local testing only
from omni.mdl import pymdlsdk  # low-level MDL python binding that matches the native SDK
BindingModuleName: str = 'omni.mdl.pymdlsdk'
BindingModule = pymdlsdk

# the unittest base class, in case testing system already needs a specializing
UnittestFrameworkBase = omni.kit.test.AsyncTestCase


class SDK():
    neuray: pymdlsdk.INeuray = None
    transaction: pymdlsdk.ITransaction = None
    mdlFactory: pymdlsdk.IMdl_factory = None

    def load(self, addExampleSearchPath: bool = True, loadImagePlugins: bool = True, loadDistillerPlugin: bool = False):
        """Initialize the SDK and get some common interface for basic testing"""

        # load neuray
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        ov_neuraylib_handle = ov_neuraylib.getNeurayAPI()
        self.neuray = omni.mdl.pymdlsdk.attach_ineuray(ov_neuraylib_handle)
        if not self.neuray.is_valid_interface():
            raise Exception('Failed to load the MDL SDK.')  # pragma: no cover
        print(f"Acquired neuray instance of version: {self.neuray.get_version()}")

        # create a DB transaction
        with self.neuray.get_api_component(pymdlsdk.IDatabase) as database, \
             database.get_global_scope() as scope:
            self.transaction = scope.create_transaction()

        # fetch other components we need
        self.mdlFactory = self.neuray.get_api_component(pymdlsdk.IMdl_factory)

    def unload(self, commitTransaction: bool = True):
        """Release all components created in the 'load' function"""
        if commitTransaction:
            self.transaction.commit()
        self.transaction = None
        self.mdlFactory = None
        self.neuray = None
