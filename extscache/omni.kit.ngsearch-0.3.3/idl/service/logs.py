import inspect
import logging
from typing import List


def access_log(kwargs: List[str] = None, returns: List[str] = None):
    if kwargs is None:
        kwargs = []

    logger = logging.getLogger("idl.service")

    def log_decorator(func):
        def log_input(instance, func_kwargs):
            logged_kwargs = {key: value for key, value in func_kwargs.items() if key in kwargs}
            logger.debug(f"> {instance.__class__.__name__}.{func.__name__}: {logged_kwargs}")

        def log_output(instance, result):
            logged_result = {key: value for key, value in result.items() if returns is None or key in returns}
            logger.debug(f"< {instance.__class__.__name__}.{func.__name__}: {logged_result}")

        async def awaitable(self, *func_args, **func_kwargs):
            log_input(self, func_kwargs)
            result = await func(self, *func_args, **func_kwargs)
            log_output(self, result)
            return result

        async def async_gen(self, *func_args, **func_kwargs):
            log_input(self, func_kwargs)
            async for result in func(self, *func_args, **func_kwargs):
                log_output(self, result)
                yield result

        if inspect.isasyncgenfunction(func):
            return async_gen
        else:
            return awaitable

    return log_decorator
