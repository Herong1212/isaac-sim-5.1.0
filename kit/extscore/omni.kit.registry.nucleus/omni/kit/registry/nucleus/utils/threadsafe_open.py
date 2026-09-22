r"""
Support for safe file writing from multiple threads.

The build system is threaded, which introduces the possibility of multiple threads trying to access the
same generated OGN files at the same time (e.g. the Python test initialization file ogn/tests/__init__.py)

For that reason it is necessary to be able to atomically write to a file.

You use this in the same way you would use open().

.. code-block:: python

    with ThreadsafeOpen("myFile.txt", "w") as my_fd:
        my_fd.write("Hello World\n")
"""
import os
from io import TextIOWrapper
from warnings import warn

# ======================================================================
# Implement the right definitions of shared functions based on the OS
try:
    # Posix based file locking (Linux, Ubuntu, MacOS, etc.)
    import fcntl

    def lock_file(file_to_lock: TextIOWrapper):
        """Lock a file for exclusive access"""
        fcntl.lockf(file_to_lock, fcntl.LOCK_EX)

    def unlock_file(file_to_unlock: TextIOWrapper):
        """Unlock exclusive access to a file"""
        fcntl.lockf(file_to_unlock, fcntl.LOCK_UN)

except ModuleNotFoundError:

    # Windows file locking (triggered by failed import of fcntl)
    # Only the first byte is locked, but that is enough for our purposes.
    import msvcrt

    def lock_file(file_to_lock: TextIOWrapper):
        """Lock a file for exclusive access"""
        file_to_lock.seek(0)
        msvcrt.locking(file_to_lock.fileno(), msvcrt.LK_LOCK, 1)

    def unlock_file(file_to_unlock: TextIOWrapper):
        """Unlock exclusive access to a file"""
        file_to_unlock.seek(0)
        msvcrt.locking(file_to_unlock.fileno(), msvcrt.LK_UNLCK, 1)


# ======================================================================
class ThreadsafeOpen:
    """
    Class for ensuring that all file operations are atomic, treat
    initialization like a standard call to 'open' that happens to be atomic.
    This file opener *must* be used in a "with" block.
    """

    def __init__(self, path, *args, **kwargs):
        """
        Open the file with the given arguments. Then acquire a lock on that file object
        WARNING: Advisory locking
        """
        self.file = open(path, *args, **kwargs)  # noqa: SIM115,PLR1732,PLW1514
        self.writing_to_file = "r" not in args
        try:
            lock_file(self.file)
        except IOError as error:
            warn(f"Could not lock {path}, may be out of sync - {error}")

    def __enter__(self, *args, **kwargs):
        """Yield the locked file descriptor on entry"""
        return self.file

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        """Release the locked file descriptor and close the file on exit"""
        # Flush to make sure all buffered contents are written to file before unlocking.
        if self.writing_to_file:
            try:
                self.file.flush()
                os.fsync(self.file.fileno())
            except OSError as error:
                warn(f"Error in sync of {self.file.name} - {error}")

        try:
            unlock_file(self.file)
            self.file.close()
        except PermissionError as error:
            warn(f"Could not unlock {self.file.name} - {error}")

        # By default any exceptions are raised to the user.
        return exc_type is None
