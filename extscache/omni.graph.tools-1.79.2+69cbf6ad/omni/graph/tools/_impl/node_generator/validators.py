"""Set of functions that perform validity checks on different values.
Everything is internal for now, used when pedantic checking is turned on in the node generator.
"""


# ==============================================================================================================
class ValidationError:
    """Manage an error in validation, providing logging and string conversions."""

    def __init__(self, validation_message: str, *args):
        self._message = validation_message
        self._log_args = args

    def __str__(self) -> str:
        return self._message % tuple(self._log_args)

    def log(self, logger):
        logger.info(self._message, *self._log_args)


# ==============================================================================================================
def validate_description(description: str | list[str]) -> list[ValidationError]:
    """Check to see if the description is up to stricter standards.
    It must be greater than 10 characters and phrased as a sentence.
    Args:
        description: String or list of strings that were specified in the file as a description of some kind
    Returns:
        List of errors found in validating the description. Empty list if None.
    """

    def __validate_line(description: str) -> bool:
        """Validates the merged description line, after splitting by newlines"""
        errors = []
        description_lines = description.split("\n")
        for line in description_lines:
            if not line.endswith("."):
                errors.append(ValidationError("Description line does not end with a period - '%s'", line))
            if line.find("  ") >= 0:
                errors.append(ValidationError("Description line contains double spaces - '%s'", line))
        return errors

    if isinstance(description, list):
        return __validate_line(" ".join(description))

    return __validate_line(description)
