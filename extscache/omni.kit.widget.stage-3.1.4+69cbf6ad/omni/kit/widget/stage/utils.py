__all__ = ["handle_exception", "get_unicode_normalization_method", "UnicodeNormalizationMethod"]

import carb
import carb.settings
import traceback
import functools
from enum import StrEnum

SETTINGS_UNICODE_NORMALIZATION_METHOD = "/persistent/app/stage/unicodeNormalizationMethod"


def handle_exception(func):
    """
    Decorator to print exception in async functions
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


# OMPE-31959: Add setting to control the Unicode normalization method.
class UnicodeNormalizationMethod(StrEnum):
    DISABLED = "Disabled"
    NFC = "NFC"


def get_unicode_normalization_method() -> UnicodeNormalizationMethod:
    """
    Get the Unicode normalization method from the settings.
    """
    method = carb.settings.get_settings().get_as_string(SETTINGS_UNICODE_NORMALIZATION_METHOD)
    try:
        return UnicodeNormalizationMethod(method)
    except ValueError:
        carb.log_warn(f"Invalid Unicode normalization method: {method}, set to disabled.")
        return UnicodeNormalizationMethod.DISABLED
