import carb

_preface_printed = False


# --------------------------------------------------------------------------------------------------------------
class ExpectedError:
    """
    Helper class used to prefix any pending error messages with [Expected Error]
    stdoutFailPatterns.exclude (defined in extension.toml) will cause these errors
    to be ignored when running tests.

    Note that it will prepend only the first error.

    Usage:
        with ExpectedError():
            function_that_produced_error_output()

    """

    def __enter__(self):
        # This is a workaround for single test runs failing due to ExpectedError not properly
        # prefixing the error. This will make sure there is a single use of carb.log_warn before
        # attempting to prefix the error. It's likely carb.log_* is flushing on the first usage,
        # which prevents the first prefix from working
        global _preface_printed
        if not _preface_printed:
            carb.log_warn("Test(s) are running that expect errors and/or warnings")
            _preface_printed = True

        # Preflush any output, otherwise it may be appended to the next statement.
        print("", flush=True)

        # Output the prefix string without a newline so that the error to be ignored will appear on
        # the same line. We do NOT want to flush this because that could allow output from another thread
        # to appear between the prefix and the error message.
        print("[Ignore this error/warning] ", end="", flush=False)

    def __exit__(self, exit_type, value, traceback):
        # Print a newline, to avoid actual errors being ignored.
        print("", flush=True)
