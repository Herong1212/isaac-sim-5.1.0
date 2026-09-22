"""Support for the population of a test list from various configurable sources"""
from __future__ import annotations
import abc
import unittest

from .ext_utils import find_disabled_tests
from .unittests import get_tests


__all__ = [
    "DEFAULT_POPULATOR_NAME",
    "TestPopulator",
    "TestPopulateAll",
    "TestPopulateDisabled",
]


# The name of the default populator, implemented with TestPopulateAll
DEFAULT_POPULATOR_NAME = "All Tests"


# ==============================================================================================================
class TestPopulator(abc.ABC):
    """Base class for the objects used to populate the initial list of tests, before filtering."""
    def __init__(self, name: str, description: str):
        """Set up the populator with the important information it needs for getting tests from some location
        Args:
            name: Name of the populator, which can be used for a menu
            description: Verbose description of the populator, which can be used for the tooltip of the menu item
        """
        self.name: str = name
        self.description: str = description
        self.tests: list[unittest.TestCase] = []  # Remembers the tests it retrieves for later use

    # --------------------------------------------------------------------------------------------------------------
    def destroy(self):
        """Opportunity to clean up any allocated resources"""
        pass

    # --------------------------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def get_tests(self, call_when_done: callable):
        """Populate the internal list of raw tests and then call the provided function when it has been done.
        The callable takes one optional boolean 'canceled' that is only True if the test retrieval was not done.
        """


# ==============================================================================================================
class TestPopulateAll(TestPopulator):
    """Implementation of the TestPopulator that returns a list of all tests known to Kit"""
    def __init__(self):
        super().__init__(
            DEFAULT_POPULATOR_NAME,
            "Use all of the tests in currently enabled extensions that pass the filters",
        )

    def get_tests(self, call_when_done: callable):
        self.tests = get_tests()
        call_when_done()


# ==============================================================================================================
class TestPopulateDisabled(TestPopulator):
    """Implementation of the TestPopulator that returns a list of all tests disabled by their extension.toml file"""
    def __init__(self):
        super().__init__(
            "Disabled Tests",
            "Use all tests from enabled extensions whose extension.toml flags them as disabled",
        )

    def get_tests(self, call_when_done: callable):
        self.tests = find_disabled_tests()
        call_when_done()
