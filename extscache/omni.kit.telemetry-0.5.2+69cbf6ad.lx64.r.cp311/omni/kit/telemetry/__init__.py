"""
    Provides a helper interface to abstract and simplify some common telemetry related
    tasks.
"""

__all__ = ['ITelemetry', 'ITelemetry2', 'RunEnvironment', 'should_enable_sentry', 'start_sentry', 'remove_sentry_pii_data']

from ._itelemetry import *
from .impl import *
