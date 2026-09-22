# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import inspect
import omni.kit.test
import omni.kit.app
import omni.kit.actions.core

from ._kit_actions_core_tests import *

_last_args = None
_last_kwargs = None
_was_called = False
_action_tests = None
_print_execution_info = False


def setUpModule():
    global _action_tests
    _action_tests = acquire_action_tests()
    _action_tests.print_test_action_execution_info = _print_execution_info


def tearDownModule():
    global _action_tests
    release_action_tests(_action_tests)
    _action_tests = None


def test_callable_function(*args, **kwargs):
    global _last_args, _last_kwargs, _was_called, _print_execution_info
    _last_args = args
    _last_kwargs = kwargs
    _was_called = True
    if _print_execution_info:
        print(f"Executed test callable function with args: {args} and kwargs: {kwargs}")
    return list(_last_args)


def test_execute_callable_function_action_with_args(test_context, *args, **kwargs):
    global _last_args, _last_kwargs, _was_called
    _last_args = None
    _last_kwargs = None
    _was_called = False

    result = test_context.test_callable_function_action.execute(*args, **kwargs)

    test_context.assertTrue(_was_called)
    test_context.assertListEqual(result, list(args))
    test_context.assertListEqual(list(_last_args), list(args))
    test_context.assertDictEqual(_last_kwargs, kwargs)


class TestCallableClass:
    def __call__(self, *args, **kwargs):
        global _print_execution_info
        self.last_args = args
        self.last_kwargs = kwargs
        self.was_called = True
        if _print_execution_info:
            print(f"Executed test callable object with args: {args} and kwargs: {kwargs}")
        return list(self.last_args)


def test_execute_callable_object_action_with_args(test_context, *args, **kwargs):
    test_context.test_callable_object.last_args = None
    test_context.test_callable_object.last_kwargs = None
    test_context.test_callable_object.was_called = False

    result = test_context.test_callable_object_action.execute(*args, **kwargs)

    test_context.assertTrue(test_context.test_callable_object.was_called)
    test_context.assertListEqual(result, list(args))
    test_context.assertListEqual(list(test_context.test_callable_object.last_args), list(args))
    test_context.assertDictEqual(test_context.test_callable_object.last_kwargs, kwargs)


def test_execute_lambda_action_with_args(test_context, *args, **kwargs):
    result = test_context.test_lambda_action.execute(*args, **kwargs)
    test_context.assertTrue(result)


def test_execute_cpp_action_with_args(test_context, *args, **kwargs):
    test_context.test_cpp_action.reset_execution_count()
    test_context.assertEqual(test_context.test_cpp_action.execution_count, 0)

    result = test_context.test_cpp_action.execute(*args, **kwargs)
    test_context.assertTrue(result)
    test_context.assertEqual(test_context.test_cpp_action.execution_count, 1)
    test_context.assertTrue(test_context.test_cpp_action.was_executed_with_args(*args, **kwargs))

    test_context.test_cpp_action.reset_execution_count()
    test_context.assertEqual(test_context.test_cpp_action.execution_count, 0)


class TestActions(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        global _action_tests

        # Cache the action tests and action registry interfaces.
        self.extension_id = "omni.kit.actions.core_tests"
        self.action_tests = _action_tests
        self.action_registry = omni.kit.actions.core.get_action_registry()

        # Register a test action that invokes a Python function.
        self.test_callable_function_action = self.action_registry.register_action(
            self.extension_id,
            "test_callable_function",
            test_callable_function,
            display_name="Test Callable Function Action",
            description="An action which invokes a callable Python function.",
            tag="TestTag",
        )

        # Register a test action that invokes a Python object.
        self.test_callable_object = TestCallableClass()
        self.test_callable_object_action = self.action_registry.register_action(
            self.extension_id,
            "test_callable_object",
            self.test_callable_object,
            display_name="Test Callable Object Action",
            description="An action which invokes a callable Python object.",
        )

        # Create and register a test action that invokes a C++ lambda.
        self.test_lambda_action = self.action_tests.create_test_lambda_action(
            self.extension_id, "test_lambda_action", "Test Lambda Action", "A lambda action which was created in C++."
        )
        self.action_registry.register_action(self.test_lambda_action)

        # Create a test action in C++.
        self.test_cpp_action = self.action_tests.create_test_cpp_action(
            self.extension_id, "test_cpp_action", "Test Cpp Action", "An action which was created in C++."
        )
        self.action_registry.register_action(self.test_cpp_action)

    async def tearDown(self):
        # Deregister all the test actions.
        self.action_registry.deregister_action(self.test_cpp_action)
        self.action_registry.deregister_action(self.test_lambda_action)
        self.action_registry.deregister_action(self.extension_id, "test_callable_object")
        self.action_registry.deregister_action(self.extension_id, "test_callable_function")

        # Destroy all the test actions.
        self.test_cpp_action = None
        self.test_lambda_action = None
        self.test_callable_object = None
        self.test_callable_object_action = None
        self.test_callable_function_action = None

        # Clear the action tests and action registry interfaces.
        self.action_registry = None
        self.action_tests = None
        self.extension_id = None

    async def test_find_registered_action(self):
        action = self.action_registry.get_action(self.extension_id, "test_callable_function")
        self.assertIsNotNone(action)

        action = self.action_registry.get_action(self.extension_id, "test_callable_object")
        self.assertIsNotNone(action)

        action = self.action_registry.get_action(self.extension_id, "test_lambda_action")
        self.assertIsNotNone(action)

        action = self.action_registry.get_action(self.extension_id, "test_cpp_action")
        self.assertIsNotNone(action)

    async def test_find_unregistered_action(self):
        action = self.action_registry.get_action(self.extension_id, "some_unregistered_action")
        self.assertIsNone(action)

    async def test_access_action_fields(self):
        action = self.action_registry.get_action(self.extension_id, "test_callable_function")
        self.assertEqual(action.id, "test_callable_function")
        self.assertEqual(action.extension_id, self.extension_id)
        self.assertEqual(action.display_name, "Test Callable Function Action")
        self.assertEqual(action.description, "An action which invokes a callable Python function.")
        self.assertEqual(action.icon_url, "")
        self.assertEqual(action.tag, "TestTag")

    async def test_get_all_actions(self):
        # If any of the asserts below fail, the 'actions' list object doesn't seem to get cleaned up properly,
        # resulting in a crash instead of a failed test. To protect against this we'll cache all the things we
        # need to assert are valid and clear the 'actions' list object before performing any of the asserts.
        actions = self.action_registry.get_all_actions()
        found_registered_action_0 = (
            not (next((action for action in actions if action.id == "test_callable_function"), None)) is None
        )
        found_registered_action_1 = (
            not (next((action for action in actions if action.id == "test_callable_object"), None)) is None
        )
        found_registered_action_2 = (
            not (next((action for action in actions if action.id == "test_lambda_action"), None)) is None
        )
        found_registered_action_3 = (
            not (next((action for action in actions if action.id == "test_cpp_action"), None)) is None
        )
        found_unregistered_action = (
            not (next((action for action in actions if action.id == "some_unregistered_action"), None)) is None
        )
        actions_length = len(actions)
        actions.clear()

        self.assertTrue(found_registered_action_0)
        self.assertTrue(found_registered_action_1)
        self.assertTrue(found_registered_action_2)
        self.assertTrue(found_registered_action_3)
        self.assertFalse(found_unregistered_action)

        # Ideally we would assert that the number of actions found is what we expect,
        # but the kit app itself registers some actions and we don't want to have to
        # keep updating this test to account for those, so we won't assert for this.
        # self.assertEqual(actions_length, 4)

    async def test_get_all_actions_registered_by_extension(self):
        # If any of the asserts below fail, the 'actions' list object doesn't seem to get cleaned up properly,
        # resulting in a crash instead of a failed test. To protect against this we'll cache all the things we
        # need to assert are valid and clear the 'actions' list object before performing any of the asserts.
        self.action_registry.register_action("some_other_extension_id", "test_action_registered_by_another_extension", test_callable_function)
        actions = self.action_registry.get_all_actions_for_extension(self.extension_id)
        found_registered_action_0 = (
            not (next((action for action in actions if action.id == "test_callable_function"), None)) is None
        )
        found_registered_action_1 = (
            not (next((action for action in actions if action.id == "test_callable_object"), None)) is None
        )
        found_registered_action_2 = (
            not (next((action for action in actions if action.id == "test_lambda_action"), None)) is None
        )
        found_registered_action_3 = (
            not (next((action for action in actions if action.id == "test_cpp_action"), None)) is None
        )
        found_unregistered_action = (
            not (next((action for action in actions if action.id == "some_unregistered_action"), None)) is None
        )
        found_action_registered_by_another_extension = (
            not (next((action for action in actions if action.id == "test_action_registered_by_another_extension"), None)) is None
        )
        actions.clear()

        self.assertTrue(found_registered_action_0)
        self.assertTrue(found_registered_action_1)
        self.assertTrue(found_registered_action_2)
        self.assertTrue(found_registered_action_3)
        self.assertFalse(found_unregistered_action)
        self.assertFalse(found_action_registered_by_another_extension)

        actions = self.action_registry.get_all_actions_for_extension("some_other_extension_id")
        found_registered_action_0 = (
            not (next((action for action in actions if action.id == "test_callable_function"), None)) is None
        )
        found_registered_action_1 = (
            not (next((action for action in actions if action.id == "test_callable_object"), None)) is None
        )
        found_registered_action_2 = (
            not (next((action for action in actions if action.id == "test_lambda_action"), None)) is None
        )
        found_registered_action_3 = (
            not (next((action for action in actions if action.id == "test_cpp_action"), None)) is None
        )
        found_unregistered_action = (
            not (next((action for action in actions if action.id == "some_unregistered_action"), None)) is None
        )
        found_action_registered_by_another_extension = (
            not (next((action for action in actions if action.id == "test_action_registered_by_another_extension"), None)) is None
        )
        actions.clear()

        self.assertFalse(found_registered_action_0)
        self.assertFalse(found_registered_action_1)
        self.assertFalse(found_registered_action_2)
        self.assertFalse(found_registered_action_3)
        self.assertFalse(found_unregistered_action)
        self.assertTrue(found_action_registered_by_another_extension)

        self.action_registry.deregister_action("some_other_extension_id", "test_action_registered_by_another_extension")

    async def test_create_actions_on_registeration(self):
        self.action_registry.register_action(self.extension_id, "test_python_action_created_on_registration", test_callable_function)
        action = self.action_registry.get_action(self.extension_id, "test_python_action_created_on_registration")
        self.assertIsNotNone(action)

        self.action_tests.create_test_action_on_registrartion(self.extension_id, "test_cpp_action_created_on_registration")
        action = self.action_registry.get_action(self.extension_id, "test_cpp_action_created_on_registration")
        self.assertIsNotNone(action)

        self.action_registry.deregister_action(self.extension_id, "test_cpp_action_created_on_registration")
        action = self.action_registry.get_action(self.extension_id, "test_cpp_action_created_on_registration")
        self.assertIsNone(action)

        self.action_registry.deregister_action(self.extension_id, "test_python_action_created_on_registration")
        action = self.action_registry.get_action(self.extension_id, "test_python_action_created_on_registration")
        self.assertIsNone(action)

    async def test_get_parameters(self):
        def test_function():
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertDictEqual(test_action.parameters, dict(inspect.signature(test_function).parameters))

        def test_function(arg0):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertDictEqual(test_action.parameters, dict(inspect.signature(test_function).parameters))

        def test_function(arg0, arg1):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertDictEqual(test_action.parameters, dict(inspect.signature(test_function).parameters))

        def test_function(arg0, arg1, arg2):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertDictEqual(test_action.parameters, dict(inspect.signature(test_function).parameters))

        def test_function(*args, **kwargs):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertDictEqual(test_action.parameters, dict(inspect.signature(test_function).parameters))

        def test_function(arg0, *args, **kwargs):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertDictEqual(test_action.parameters, dict(inspect.signature(test_function).parameters))

    async def test_requires_parameters(self):
        def test_function():
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertFalse(test_action.requires_parameters)

        def test_function(arg0):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertTrue(test_action.requires_parameters)

        def test_function(arg0=False):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertFalse(test_action.requires_parameters)

        def test_function(arg0, arg1=False):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertTrue(test_action.requires_parameters)

        def test_function(arg0=True, arg1=False):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertFalse(test_action.requires_parameters)

        def test_function(arg0="Nine", arg1=-9, arg2=False):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertFalse(test_action.requires_parameters)

        def test_function(*args, **kwargs):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertFalse(test_action.requires_parameters)

        def test_function(arg0, *args, **kwargs):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertTrue(test_action.requires_parameters)

        def test_function(arg0="Nine", *args, **kwargs):
            self.assertFalse(True) # Should never be called
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        self.assertFalse(test_action.requires_parameters)

    async def test_execute_callable_function_action(self):
        global _last_args, _last_kwargs, _was_called
        _last_args = None
        _last_kwargs = None
        _was_called = False

        result = self.test_callable_function_action.execute()

        self.assertTrue(_was_called)
        self.assertFalse(result)
        self.assertFalse(_last_args)
        self.assertFalse(_last_kwargs)

    async def test_execute_callable_object_action(self):
        self.test_callable_object.last_args = None
        self.test_callable_object.last_kwargs = None
        self.test_callable_object.was_called = False

        result = self.test_callable_object_action.execute()

        self.assertTrue(self.test_callable_object.was_called)
        self.assertFalse(result)
        self.assertFalse(self.test_callable_object.last_args)
        self.assertFalse(self.test_callable_object.last_kwargs)

    async def test_execute_lambda_action(self):
        result = self.test_lambda_action.execute()
        self.assertTrue(result)

    async def test_execute_cpp_action(self):
        self.test_cpp_action.reset_execution_count()
        self.assertEqual(self.test_cpp_action.execution_count, 0)

        result = self.test_cpp_action.execute()
        self.assertTrue(result)
        self.assertEqual(self.test_cpp_action.execution_count, 1)

        result = self.test_cpp_action.execute()
        self.assertTrue(result)
        self.assertEqual(self.test_cpp_action.execution_count, 2)

        result = self.test_cpp_action.execute()
        self.assertTrue(result)
        self.assertEqual(self.test_cpp_action.execution_count, 3)

        self.test_cpp_action.reset_execution_count()
        self.assertEqual(self.test_cpp_action.execution_count, 0)

    async def test_execute_action_using_id(self):
        global _last_args, _last_kwargs, _was_called
        _last_args = None
        _last_kwargs = None
        _was_called = False

        result = omni.kit.actions.core.execute_action(self.extension_id, "test_callable_function")

        self.assertTrue(_was_called)
        self.assertFalse(result)
        self.assertFalse(_last_args)
        self.assertFalse(_last_kwargs)

        self.test_callable_object.last_args = None
        self.test_callable_object.last_kwargs = None
        self.test_callable_object.was_called = False

        result = omni.kit.actions.core.execute_action(self.extension_id, "test_callable_object", True, 9, "Nine")

        self.assertTrue(self.test_callable_object.was_called)
        self.assertListEqual(result, [True, 9, "Nine"])
        self.assertListEqual(list(self.test_callable_object.last_args), [True, 9, "Nine"])
        self.assertFalse(self.test_callable_object.last_kwargs)

    async def test_find_and_execute_python_action_from_cpp(self):
        self.test_callable_object.last_args = None
        self.test_callable_object.last_kwargs = None
        self.test_callable_object.was_called = False

        result = self.action_tests.find_and_execute_test_action_from_cpp(self.extension_id, "test_callable_object")

        self.assertTrue(self.test_callable_object.was_called)
        self.assertFalse(result)
        self.assertFalse(self.test_callable_object.last_args)
        self.assertFalse(self.test_callable_object.last_kwargs)

    async def test_find_and_execute_cpp_action_from_cpp(self):
        self.test_cpp_action.reset_execution_count()
        self.assertEqual(self.test_cpp_action.execution_count, 0)

        result = self.action_tests.find_and_execute_test_action_from_cpp(self.extension_id, "test_cpp_action")

        self.assertTrue(result)
        self.assertEqual(self.test_cpp_action.execution_count, 1)

        self.test_cpp_action.reset_execution_count()
        self.assertEqual(self.test_cpp_action.execution_count, 0)

    async def test_find_and_execute_cpp_action_from_python(self):
        self.test_cpp_action.reset_execution_count()
        self.assertEqual(self.test_cpp_action.execution_count, 0)

        action = self.action_registry.get_action(self.extension_id, "test_cpp_action")
        self.assertIsNotNone(action)

        result = action.execute()

        self.assertTrue(result)
        self.assertEqual(self.test_cpp_action.execution_count, 1)

        self.test_cpp_action.reset_execution_count()
        self.assertEqual(self.test_cpp_action.execution_count, 0)

    async def test_execute_action_with_return_value(self):
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", lambda x: x * x)
        result = test_action.execute(9)
        self.assertEqual(result, 81)

        result = self.action_tests.execute_square_value_action_from_cpp(8)
        self.assertEqual(result, 64)

    async def test_invalidate_python_action(self):
        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", lambda x: x * x)
        result = test_action.execute(9)
        self.assertEqual(result, 81)

        test_action.invalidate()
        result = test_action.execute(9)
        self.assertIsNone(result)

    async def test_invalidate_lambda_action(self):
        test_action = self.action_tests.create_test_lambda_action(self.extension_id, "test_action", "", "")
        result = test_action.execute()
        self.assertTrue(result)

        test_action.invalidate()
        result = test_action.execute()
        self.assertIsNone(result)

    async def test_execute_actions_with_bool(self):
        test_execute_callable_function_action_with_args(self, True)
        test_execute_callable_object_action_with_args(self, True)
        test_execute_lambda_action_with_args(self, True)
        test_execute_cpp_action_with_args(self, True)

        def test_function(arg):
            self.assertTrue(arg)

        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        test_action.execute(True)
        self.action_tests.execute_test_action_from_cpp_with_bool(test_action, True)

    async def test_execute_actions_with_int(self):
        test_execute_callable_function_action_with_args(self, 9)
        test_execute_callable_object_action_with_args(self, 9)
        test_execute_lambda_action_with_args(self, 9)
        test_execute_cpp_action_with_args(self, 9)

        def test_function(arg):
            self.assertEqual(arg, 9)

        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        test_action.execute(9)
        self.action_tests.execute_test_action_from_cpp_with_int(test_action, 9)

    async def test_execute_actions_with_string(self):
        test_execute_callable_function_action_with_args(self, "Nine")
        test_execute_callable_object_action_with_args(self, "Nine")
        test_execute_lambda_action_with_args(self, "Nine")
        test_execute_cpp_action_with_args(self, "Nine")

        def test_function(arg):
            self.assertEqual(arg, "Nine")

        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        test_action.execute("Nine")
        self.action_tests.execute_test_action_from_cpp_with_string(test_action, "Nine")

    async def test_execute_actions_with_multiple_args(self):
        test_execute_callable_function_action_with_args(self, "Nine", 9, True)
        test_execute_callable_object_action_with_args(self, "Nine", 9, True)
        test_execute_lambda_action_with_args(self, "Nine", 9, True)
        test_execute_cpp_action_with_args(self, "Nine", 9, True)

        def test_function(arg0, arg1, arg2):
            self.assertEqual(arg0, "Nine")
            self.assertEqual(arg1, 9)
            self.assertTrue(arg2)

        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        test_action.execute("Nine", 9, True)
        self.action_tests.execute_test_action_from_cpp_with_multiple_args(test_action, "Nine", 9, True)

    async def test_execute_actions_with_nested_args(self):
        test_nested_args = (False, 99, "Ninety-Nine")
        test_execute_callable_function_action_with_args(self, "Nine", test_nested_args, 9, True)
        test_execute_callable_object_action_with_args(self, "Nine", test_nested_args, 9, True)
        test_execute_lambda_action_with_args(self, "Nine", test_nested_args, 9, True)
        test_execute_cpp_action_with_args(self, "Nine", test_nested_args, 9, True)

        def test_function(arg0, arg1, arg2, arg3):
            self.assertEqual(arg0, "Nine")
            self.assertListEqual(list(arg1), list(test_nested_args))
            self.assertEqual(arg2, 9)
            self.assertTrue(arg3)

        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        test_action.execute("Nine", test_nested_args, 9, True)

    async def test_execute_actions_with_keyword_args(self):
        test_execute_callable_function_action_with_args(self, kwarg0="Nine", kwarg1=9, kwarg2=True)
        test_execute_callable_object_action_with_args(self, kwarg0="Nine", kwarg1=9, kwarg2=True)
        test_execute_lambda_action_with_args(self, kwarg0="Nine", kwarg1=9, kwarg2=True)
        test_execute_cpp_action_with_args(self, kwarg0="Nine", kwarg1=9, kwarg2=True)

        def test_function(kwarg0="", kwarg1=0, kwarg2=False):
            self.assertEqual(kwarg0, "Nine")
            self.assertEqual(kwarg1, 9)
            self.assertTrue(kwarg2)

        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        test_action.execute(kwarg0="Nine", kwarg1=9, kwarg2=True)
        test_action.execute(kwarg2=True, kwarg1=9, kwarg0="Nine")
        self.action_tests.execute_test_action_from_cpp_with_variable_args(
            test_action, kwarg0="Nine", kwarg1=9, kwarg2=True
        )

    async def test_execute_actions_with_mixed_args(self):
        test_execute_callable_function_action_with_args(
            self, "Nine", 9, True, kwarg0=False, kwarg1=99, kwarg2="Ninety-Nine"
        )
        test_execute_callable_object_action_with_args(
            self, "Nine", 9, True, kwarg0=False, kwarg1=99, kwarg2="Ninety-Nine"
        )
        test_execute_lambda_action_with_args(self, "Nine", 9, True, kwarg0=False, kwarg1=99, kwarg2="Ninety-Nine")
        test_execute_cpp_action_with_args(self, "Nine", 9, True, kwarg0=False, kwarg1=99, kwarg2="Ninety-Nine")

        def test_function(arg0, arg1, arg2, kwarg0=True, kwarg1=0, kwarg2=""):
            self.assertEqual(arg0, "Nine")
            self.assertEqual(arg1, 9)
            self.assertTrue(arg2)
            self.assertFalse(kwarg0)
            self.assertEqual(kwarg1, 99)
            self.assertEqual(kwarg2, "Ninety-Nine")

        test_action = omni.kit.actions.core.Action(self.extension_id, "test_action", test_function)
        test_action.execute("Nine", 9, True, kwarg0=False, kwarg1=99, kwarg2="Ninety-Nine")
        test_action.execute("Nine", 9, True, kwarg2="Ninety-Nine", kwarg1=99, kwarg0=False)
        self.action_tests.execute_test_action_from_cpp_with_variable_args(
            test_action, "Nine", 9, True, kwarg0=False, kwarg1=99, kwarg2="Ninety-Nine"
        )
