import asyncio
import time
from functools import wraps

# change this flag to true will print every test's cost time
PRINT_TEST_TIME = False  # pragma: no cover


def time_logger(cls):  # pragma: no cover
    original_init = cls.__init__

    @wraps(cls.__init__)
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._wrap_methods()

    def _wrap_methods(self):
        if hasattr(self, "setUp") and asyncio.iscoroutinefunction(self.setUp):
            original_setup = self.setUp

            @wraps(original_setup)
            async def setup_wrapper(*args, **kwargs):
                self._start_time = time.monotonic()
                return await original_setup(*args, **kwargs)

            self.setUp = setup_wrapper

        if hasattr(self, "tearDown") and asyncio.iscoroutinefunction(self.tearDown):
            original_teardown = self.tearDown

            @wraps(original_teardown)
            async def teardown_wrapper(*args, **kwargs):
                end_time = time.monotonic()
                elapsed_time = end_time - self._start_time
                if elapsed_time > 2:
                    print("=====================Long test time==========================")
                print(f"Test time: {elapsed_time:.4f} seconds")
                return await original_teardown(*args, **kwargs)

            self.tearDown = teardown_wrapper

    if PRINT_TEST_TIME:
        cls.__init__ = new_init
        cls._wrap_methods = _wrap_methods
    return cls
