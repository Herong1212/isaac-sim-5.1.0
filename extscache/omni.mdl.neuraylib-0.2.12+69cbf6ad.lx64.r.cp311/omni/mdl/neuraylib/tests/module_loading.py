from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading

from .utils import *
from pathlib import Path
import omni.mdl.neuraylib as neuraylib   # interface the OV material backend
import omni.mdl.pymdlsdk as pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.pymdl       # high-level wrapper

class ModuleLoadingTest(AsyncTestCase):
    ov_neuraylib = None
    neuray: pymdlsdk.INeuray = None
    ext_mdl_dir_uri: str = None

    # Before running each test
    async def setUp(self):
        self.ov_neuraylib: neuraylib.NeurayLib = neuraylib.get_neuraylib()
        self.neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(self.ov_neuraylib.getNeurayAPI())

        ext_id = omni.kit.app.get_app().get_extension_manager().get_extension_id_by_module(__name__)
        ext_dir = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id))
        self.ext_mdl_dir_uri = make_uri_with_scheme(str(ext_dir.joinpath('data', 'tests', 'mdl')))

    # After running each test
    async def tearDown(self):
        self.neuray = None
        self.ov_neuraylib = None

    # ----------------------------------------------------------------------------------------------
    # Test Cases
    # ----------------------------------------------------------------------------------------------

    # load a broken module that has errors after the imports have been processed.
    # this will cause the (valid) imports to be loaded in the DB while the requested module failed.
    async def test_wrong_syntax(self):
        self.assertIsNotNone(self.neuray)

        module_uri: str = self.ext_mdl_dir_uri + "/loading_tests/WrongSyntaxTest.mdl"
        print("\nloading 'WrongSyntaxTest.mdl'")
        ov_module = self.ov_neuraylib.createMdlModule(module_uri)
        self.assertFalse(ov_module.valid())  # invalid
        print(f"    dbScopeName: {ov_module.dbScopeName}")  # defined even if invalid
        print(f"    dbName: {ov_module.dbName}")  # defined even if invalid
        print(f"    qualifiedName: {ov_module.qualifiedName}")  # defined even if invalid

        # open a new transaction after createMdlModule, otherwise we would not see the loaded modules
        ovTransactionReadHandle = self.ov_neuraylib.createReadingTransaction(ov_module.dbScopeName)
        trans: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ovTransactionReadHandle)
        m: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, ov_module.dbName)
        self.assertFalse(m.is_valid_interface()) # this module failed to load and should not be in the DB

        import_db_name: str = ov_module.dbName + "_validImport"

        # direct access to the module in the DB
        m2: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, import_db_name)
        self.assertTrue(m2.is_valid_interface()) # this import is done before the syntax error was found, so it is in DB

        # access through neuraylib is not possible yet because it's not tracked
        # this happens only after direct request or when the module appeared in the depencency graph which in turn
        # is only available when loaded succeeded.
        ov_module2 = self.ov_neuraylib.createMdlModuleFromDbName(import_db_name, ov_module.dbScopeName)
        self.assertIsNone(ov_module2)

        # directly requesting the imported module will return the same module (that we access directly above)
        # Note, we could only access it directly because we know that this file was imported
        print("\nloading 'WrongSyntaxTest_validImport.mdl'")
        ov_module3 = self.ov_neuraylib.createMdlModule(module_uri[:-4] + "_validImport.mdl")
        self.assertTrue(ov_module3.valid())
        print(f"    dbScopeName: {ov_module3.dbScopeName}")
        print(f"    dbName: {ov_module3.dbName}")
        print(f"    qualifiedName: {ov_module3.qualifiedName}")

        self.ov_neuraylib.destroyMdlModule(ov_module)
        self.ov_neuraylib.destroyMdlModule(ov_module3)

        # request a standard module after it has been loaded (by the imported module above)
        print("\nloading 'math.mdl'")
        ov_math_module = self.ov_neuraylib.createMdlModule("math.mdl")
        self.assertTrue(ov_math_module.valid())
        print(f"    dbScopeName: {ov_math_module.dbScopeName}")
        print(f"    dbName: {ov_math_module.dbName}")
        print(f"    qualifiedName: {ov_math_module.qualifiedName}")
        self.ov_neuraylib.destroyMdlModule(ov_math_module)

        # request the base module which shoud not have been loaded yet
        print("\nloading 'base.mdl'")
        m_base: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, "mdl::base.mdl")
        self.assertFalse(m_base.is_valid_interface()) # in this test setup, base should not have been loaded
        ov_base_module = self.ov_neuraylib.createMdlModule("base.mdl")
        self.assertTrue(ov_base_module.valid())
        print(f"    dbScopeName: {ov_base_module.dbScopeName}")
        print(f"    dbName: {ov_base_module.dbName}")
        print(f"    qualifiedName: {ov_base_module.qualifiedName}")
        self.ov_neuraylib.destroyMdlModule(ov_base_module)

    async def test_create_destroy_create(self):
        self.assertIsNotNone(self.neuray)

        module_uri: str = self.ext_mdl_dir_uri + "/loading_tests/CreateDestroyCreate.mdl"
        ov_module = self.ov_neuraylib.createMdlModule(module_uri)
        self.assertTrue(ov_module.valid())  # valid

        # access the module in the DB
        trans: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(self.ov_neuraylib.createReadingTransaction(ov_module.dbScopeName))
        m: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, ov_module.dbName)
        self.assertTrue(m.is_valid_interface())  # valid
        m = None
        trans = None

        # access OV module by DB name
        ov_module2 = self.ov_neuraylib.createMdlModuleFromDbName(ov_module.dbName, ov_module.dbScopeName)
        self.assertTrue(ov_module2.valid())  # valid

        # free the OV modules
        storedDbScopeName: str = ov_module.dbScopeName
        storedDbName: str = ov_module.dbName
        self.ov_neuraylib.destroyMdlModule(ov_module)
        self.ov_neuraylib.destroyMdlModule(ov_module2)

        # no access anymore because all ov modules have been destroyed
        ov_module3 = self.ov_neuraylib.createMdlModuleFromDbName(storedDbName, storedDbScopeName)
        self.assertIsNone(ov_module3)  # invalid

        # the module stays in the DB. This is a limitation at this point and might change in the future
        trans: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(self.ov_neuraylib.createReadingTransaction(storedDbScopeName))
        m: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, storedDbName)
        self.assertTrue(m.is_valid_interface())  # still valid
        m = None
        trans = None

        # requesting the same module again results in a reference to the same neuray DB module
        ov_module4 = self.ov_neuraylib.createMdlModule(module_uri)
        self.assertTrue(ov_module4.valid())  # valid again
        self.assertEqual(ov_module4.dbScopeName, storedDbScopeName)
        self.assertEqual(ov_module4.dbName, storedDbName)

        # also accessing though the DB name is possible again
        ov_module5 = self.ov_neuraylib.createMdlModuleFromDbName(storedDbName, storedDbScopeName)
        self.assertTrue(ov_module5.valid())  # valid again

        # the module is also (still) accessible in the DB
        trans: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(self.ov_neuraylib.createReadingTransaction(storedDbScopeName))
        m: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, storedDbName)
        self.assertTrue(m.is_valid_interface())  # still valid
        m = None
        trans = None

        # cleanup
        self.ov_neuraylib.destroyMdlModule(ov_module4)
        self.ov_neuraylib.destroyMdlModule(ov_module5)

    def _create_module_in_tmp_scope(self, module_name):
        scope_name = neuraylib.create_temporary_db_scope(resolveResources=False)
        self.assertNotEqual(scope_name, "")

        module = self.ov_neuraylib.createMdlModule(module_name, scope_name)
        self.assertTrue(module.valid())

        self.ov_neuraylib.destroyMdlModule(module)
        self.assertTrue(neuraylib.destroy_temporary_db_scope(scope_name))

    async def test_create_standard_modules(self):
        standard_modules = ["anno.mdl", "debug.mdl", "df.mdl", "limits.mdl", "math.mdl", "scene.mdl", "state.mdl", "std.mdl", "tex.mdl"]

        for module_name in standard_modules:
            self._create_module_in_tmp_scope(module_name)

    async def test_create_builtin_module(self):
        self._create_module_in_tmp_scope("mdl-builtin.mdl")

    async def test_create_base_module(self):
        self._create_module_in_tmp_scope("base.mdl")