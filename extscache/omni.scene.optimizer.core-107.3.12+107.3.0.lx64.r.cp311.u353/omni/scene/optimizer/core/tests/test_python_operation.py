__copyright__ = "Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import os

import omni.kit.test
from omni.scene.optimizer.core import ExecutionContext
from omni.scene.optimizer.core.bindings._omni_scene_optimizer_core import acquire_interface


class TestPythonOperation(omni.kit.test.AsyncTestCase):
    def test_load_plugins_from_path(self):
        # load the test plugins from data
        interface = acquire_interface()
        interface.load_plugins_from_path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/pythonPlugins"
        )
        operation_names = interface.get_operations()

        # has the valid plugin been registered?
        valid_op_name = "validPythonOperation"
        self.assertIn(valid_op_name, interface.get_operations())
        self.assertEqual(interface.get_operation_display_name(valid_op_name), "Valid Python Operation")
        self.assertEqual(
            interface.get_operation_description(valid_op_name), "This is a valid Python Operation for testing purposes."
        )
        self.assertEqual(interface.get_operation_author(valid_op_name), "Scene Optimizer Unit Test")
        version = interface.get_operation_version(valid_op_name)
        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.rev, 3)
        args = interface.get_operation_arguments(valid_op_name)
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0]["name"], "resultString")
        self.assertEqual(args[1]["name"], "enumArg")
        self.assertEqual(args[2]["name"], "minMaxArg")

        # import the python Operation before we execute it to see the value of the global result variable
        from so_py_op_valid import RESULT

        self.assertIsNone(RESULT)

        # run the operation
        self.assertTrue(interface.execute_operation(valid_op_name, ExecutionContext(), '{"resultString": "test123"}'))

        # has the global result been updated?
        from so_py_op_valid import RESULT

        self.assertEqual(RESULT, "test123")

        # now we just want to check that none of the test plugins with various errors have not been registered but that
        # we can still import the ones which are valid python - this means they were handled during the plugin load
        # process but failed to register
        self.assertNotIn("noInitFilePythonOperation", operation_names)
        self.assertNotIn("syntaxErrorPythonOperation", operation_names)

        # -----------------------
        from so_py_op_no_init_func import NoInitFuncPythonOperation

        self.assertNotIn("noInitFuncPythonOperation", operation_names)

        # -----------------------
        from so_py_op_init_func_error import InitFuncErrorPythonOperation

        self.assertNotIn("initFuncErrorPythonOperation", operation_names)

        # -----------------------
        from so_py_op_init_func_none import InitFuncNonePythonOperation

        self.assertNotIn("initFuncNonePythonOperation", operation_names)

        # -----------------------
        from so_py_op_name_error import NameErrorPythonOperation

        self.assertNotIn("nameErrorPythonOperation", operation_names)

        # -----------------------
        from so_py_op_display_name_error import DisplayNameErrorPythonOperation

        self.assertNotIn("displayNameErrorPythonOperation", operation_names)

        # -----------------------
        from so_py_op_description_error import DescriptionErrorPythonOperation

        self.assertNotIn("descriptionErrorPythonOperation", operation_names)

        # -----------------------
        from so_py_op_no_author import NoAuthorPythonOperation

        self.assertNotIn("noAuthorPythonOperation", operation_names)

        # -----------------------
        from so_py_op_no_version import NoVersionPythonOperation

        self.assertNotIn("noVersionPythonOperation", operation_names)

        # -----------------------
        from so_py_op_bad_version_1 import BadVersion1PythonOperation

        self.assertNotIn("badVersion1PythonOperation", operation_names)

        # -----------------------
        from so_py_op_bad_version_2 import BadVersion2PythonOperation

        self.assertNotIn("badVersion2PythonOperation", operation_names)

        # -----------------------
        from so_py_op_bad_version_3 import BadVersion3PythonOperation

        self.assertNotIn("badVersion3PythonOperation", operation_names)

        # -----------------------
        from so_py_op_visible_error import VisibleErrorPythonOperation

        self.assertNotIn("visibleErrorPythonOperation", operation_names)

        # -----------------------
        from so_py_op_args_error import ArgsErrorPythonOperation

        self.assertNotIn("argsErrorPythonOperation", operation_names)

        # -----------------------
        from so_py_op_bad_args_1 import BadArgs1PythonOperation

        self.assertNotIn("badArgs1PythonOperation", operation_names)

        # -----------------------
        from so_py_op_bad_args_2 import BadArgs2PythonOperation

        self.assertNotIn("badArgs2PythonOperation", operation_names)

        # check the plugin that raises an error during execute
        op_name = "executeErrorPythonOperation"
        self.assertIn(op_name, interface.get_operations())
        self.assertFalse(interface.execute_operation(op_name, ExecutionContext(), "{}")[0])

        # check the plugin that returns a non-bool from execute
        op_name = "badExecutePythonOperation"
        self.assertIn(op_name, interface.get_operations())
        self.assertFalse(interface.execute_operation(op_name, ExecutionContext(), "{}")[0])

        # test derigstering operations
        op_name = "validPythonOperation"
        interface.deregister_operation(op_name)
        self.assertNotIn(op_name, interface.get_operations())

        op_name = "executeErrorPythonOperation"
        interface.deregister_operation(op_name)
        self.assertNotIn(op_name, interface.get_operations())

        op_name = "badExecutePythonOperation"
        interface.deregister_operation(op_name)
        self.assertNotIn(op_name, interface.get_operations())

    def test_load_plugins_from_env_var(self):
        interface = acquire_interface()
        operation_names = interface.get_operations()

        # check plugins haven't been loaded yet
        self.assertNotIn("envVar1PythonOperation", operation_names)
        self.assertNotIn("envVar2PythonOperation", operation_names)

        # set environment variable
        plugins_root = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/pythonPlugins"
        delimiter = ":"
        if os.name == "nt":
            delimiter = ";"
        os.environ["SCENE_OPTIMIZER_PLUGIN_PATH"] = f"{plugins_root}/env_var_1{delimiter}{plugins_root}/env_var_2"

        interface.load_plugins()
        operation_names = interface.get_operations()

        # check plugins have been loaded
        self.assertIn("envVar1PythonOperation", operation_names)
        self.assertIn("envVar2PythonOperation", operation_names)
