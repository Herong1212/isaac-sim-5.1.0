"""Tests that exercise the various types of deprecation"""

import re

import omni.graph.tools as ogt
import omni.kit

# ==============================================================================================================
# Deprecated constructs for testing
CLASS_DEPRECATED = "Use og.NewerClass"


@ogt.DeprecatedClass(CLASS_DEPRECATED)
class OlderClass:
    pass


FUNCTION_DEPRECATED = "Use og.newer_function()"


@ogt.deprecated_function(FUNCTION_DEPRECATED)
def older_function():
    pass


class NewNameForClass:
    pass


RENAME_MESSAGE = "OldNameForClass is now NewNameForClass"
OldNameForClass = ogt.RenamedClass(NewNameForClass, "OldNameForClass", RENAME_MESSAGE)
OLD_STRING = ogt.DeprecatedStringConstant("OLD_STRING", "GARBAGE", "Wipe your memory of it")
OLD_DICTIONARY = ogt.DeprecatedDictConstant("OLD_DICTIONARY", {}, "Wipe your memory of it")
OLD_OBJECT = ogt.deprecated_constant_object(older_function, "Wipe your memory of it")


# ==============================================================================================================
class TestDeprecation(omni.kit.test.AsyncTestCase):

    # --------------------------------------------------------------------------------------------------------------
    def setUp(self):
        """Messages have to be cleared before the test to avoid spurious success"""
        ogt.DeprecateMessage.clear_messages()
        self.__were_deprecations_errors = ogt.DeprecateMessage.deprecations_are_errors()
        ogt.DeprecateMessage.set_deprecations_are_errors(False)

    def tearDown(self):
        """Messages have to be cleared after the test to prevent contamination of the message logs"""
        ogt.DeprecateMessage.clear_messages()
        ogt.DeprecateMessage.set_deprecations_are_errors(self.__were_deprecations_errors)

    # --------------------------------------------------------------------------------------------------------------
    def __check_deprecation_messages(self, pattern: str, expected_count: int):
        """Returns True if the pattern appears in the deprecation messages the given number of times"""
        actual_count = sum(
            match is not None
            for match in [
                re.search(pattern, message) for message in ogt.DeprecateMessage._MESSAGES_LOGGED  # noqa: PLW0212
            ]
        )

        self.assertEqual(
            actual_count, expected_count, f"Expected {expected_count} messages matching {pattern} - got {actual_count}"
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_class_deprecation(self):
        """Test deprecation of a class"""
        with ogt.DeprecateMessage.NoLogging():
            _ = OlderClass()
        self.__check_deprecation_messages(CLASS_DEPRECATED, 1)

    # --------------------------------------------------------------------------------------------------------------
    async def test_function_deprecation(self):
        """Test deprecation of a single function"""
        with ogt.DeprecateMessage.NoLogging():
            older_function()
        expected = f"older_function() is deprecated: {FUNCTION_DEPRECATED}"
        self.assertTrue(
            expected in ogt.DeprecateMessage.messages_logged(),
            f"'{expected}' not found in {ogt.DeprecateMessage.messages_logged()}",
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_rename_deprecation(self):
        """Test deprecation of a class by giving it a new name"""
        with ogt.DeprecateMessage.NoLogging():
            _ = OldNameForClass()
        self.__check_deprecation_messages(RENAME_MESSAGE, 1)

    # --------------------------------------------------------------------------------------------------------------
    async def test_string_constant_deprecation(self):
        """Test deprecation of a string constant that is being removed"""
        # The deprecation message only happens on conversion to string as that's where it's most relevant.
        with ogt.DeprecateMessage.NoLogging():
            new_constant = str(OLD_STRING)
        expected = "OLD_STRING is deprecated: Wipe your memory of it"
        self.assertEqual(new_constant, "GARBAGE")
        self.assertTrue(
            expected in ogt.DeprecateMessage.messages_logged(),
            f"'{expected}' not found in {ogt.DeprecateMessage.messages_logged()}",
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_dict_constant_deprecation(self):
        """Test deprecation of a dictionary constant that is being removed"""
        expected = "OLD_DICTIONARY is deprecated: Wipe your memory of it"
        self.assertEqual(dict(OLD_DICTIONARY), {})
        self.assertTrue(
            expected in ogt.DeprecateMessage.messages_logged(),
            f"'{expected}' not found in {ogt.DeprecateMessage.messages_logged()}",
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_object_constant_deprecation(self):
        """Test deprecation of an object constant that is being removed"""
        expected = re.compile(".*older_function.*is deprecated. Wipe your memory of it")
        self.assertEqual(OLD_OBJECT.__name__, "older_function")
        found_message = False
        messages = ogt.DeprecateMessage.messages_logged()
        for message in messages:
            if expected.match(message):
                found_message = True
        self.assertTrue(found_message, f"'{expected}' not found in {messages}")

    # --------------------------------------------------------------------------------------------------------------
    async def test_deprecation_message(self):
        """Test issuing a deprecation message"""
        deprecation_message = "This is deprecated"
        with ogt.DeprecateMessage.NoLogging():
            ogt.DeprecateMessage.deprecated(deprecation_message)
        self.assertTrue(deprecation_message in ogt.DeprecateMessage.messages_logged())

    # --------------------------------------------------------------------------------------------------------------
    async def test_deprecated_import(self):
        """Test deprecation of a module import"""
        with ogt.DeprecateMessage.NoLogging():
            import omni.graph.tools.tests.deprecated_import as _do_not_export  # noqa: F401,PLW0621
        expected = "omni.graph.tools.tests.deprecated_import is deprecated: Do Not Import"
        self.assertTrue(
            expected in ogt.DeprecateMessage.messages_logged(),
            f"'{expected}' not found in {ogt.DeprecateMessage.messages_logged()}",
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_deprecation_error(self):
        """Test escalation of deprecations from warning to error"""
        old_setting = ogt.DeprecateMessage.deprecations_are_errors()
        try:
            ogt.DeprecateMessage.set_deprecations_are_errors(True)
            with self.assertRaises(ogt.DeprecationError, msg="Use of hard deprecated class not raising an error"):
                _ = OlderClass()
        finally:
            ogt.DeprecateMessage.set_deprecations_are_errors(old_setting)
