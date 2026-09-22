from enum import Enum
from typing import Callable, Any


class TestRunStatus(Enum):
    UNKNOWN = 0
    RUNNING = 1
    PASSED = 2
    FAILED = 3


_callbacks = []


def add_test_status_report_cb(callback: Callable[[str, TestRunStatus, Any], None]):
    """Add callback to be called when tests start, fail, pass."""
    global _callbacks
    _callbacks.append(callback)


def remove_test_status_report_cb(callback: Callable[[str, TestRunStatus, Any], None]):
    """Remove callback to be called when tests start, fail, pass."""
    global _callbacks
    _callbacks.remove(callback)


def _test_status_report(test_id: str, status: TestRunStatus, **kwargs):
    for cb in _callbacks:
        cb(test_id, status, **kwargs)
