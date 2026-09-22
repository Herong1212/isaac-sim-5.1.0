import asyncio
import math
import unittest

import omni.kit.test
import omni.kit.app
import carb.settings
from carb.eventdispatcher import get_eventdispatcher
from concurrent.futures import Future

async def _async_factorial(x):
    if x == 0 or x == 1:
        return 1
    return x * await _async_factorial(x - 1)


class TestAsyncEngine(omni.kit.test.AsyncTestCase):
    async def test_async_engine_one_update(self):
        # Wait for few updates
        app = omni.kit.app.get_app()
        update_number = app.get_update_number()
        await app.next_update_async()
        self.assertEqual(app.get_update_number(), update_number + 1)
        await app.next_update_async()
        await app.next_update_async()
        self.assertEqual(app.get_update_number(), update_number + 3)

    async def test_async_engine(self):
        app = omni.kit.app.get_app()
        update_number = app.get_update_number()

        # Here we run a bunch of async tasks each of them contains nested async calls.
        # Default `spinLoopOncePerUpdate` setting set to False so that it guarantees complete progress during one update.
        input = [1, 2, 3, 4, 5, 6, 7, 8]

        res = await asyncio.gather(*[_async_factorial(x) for x in input])
        await app.next_update_async()

        # Only one update passed and result is correct
        self.assertEqual(app.get_update_number(), update_number + 1)
        self.assertEqual(res, [math.factorial(x) for x in input])

    async def test_asyncio_run(self):
        # Add an event subscription
        app = omni.kit.app.get_app()

        fut = Future()
        # Async function
        async def fn():
            await asyncio.sleep(0.5)
            fut.set_result(True)

        # Update subscription function that calls asyncio.run().
        def testFn(*args):
            asyncio.run(fn())

        # Register our subscription
        sub = get_eventdispatcher().observe_event(event_name=omni.kit.app.GLOBAL_EVENT_UPDATE, on_event=testFn)

        # This will cause the update to fire off
        await app.next_update_async()
        self.assertTrue(fut.done())
        self.assertTrue(fut.result())
        sub.reset()

    async def test_run_until_complete(self):
        # Add an event subscription
        app = omni.kit.app.get_app()

        fut = Future()
        # Async function
        async def fn():
            await asyncio.sleep(0.5)
            fut.set_result(True)
            return "Test Return Value"

        # Update subscription function that calls run_until_complete
        def testFn(*args):
            self.assertEqual(asyncio.get_event_loop().run_until_complete(fn()), "Test Return Value")

        # Register our subscription
        sub = get_eventdispatcher().observe_event(event_name=omni.kit.app.GLOBAL_EVENT_UPDATE, on_event=testFn)

        # This will cause the update to fire off
        await app.next_update_async()
        self.assertTrue(fut.done())
        self.assertTrue(fut.result())
        sub.reset()

    async def test_run_forever(self):
        # Add an event subscription
        app = omni.kit.app.get_app()

        fut = Future()
        def testFn(*args):
            loop = asyncio.get_event_loop()
            # Tick twice the "proper" way
            loop.stop()
            loop.run_forever()

            loop.stop()
            loop.run_forever()

            fut.set_result(True)

        # Register a subscription
        sub = get_eventdispatcher().observe_event(event_name=omni.kit.app.GLOBAL_EVENT_UPDATE, on_event=testFn)

        # Cause the update to fire off
        await app.next_update_async()
        self.assertTrue(fut.done())
        self.assertTrue(fut.result())
        sub.reset()

    async def test_is_patched(self):
        self.assertTrue(hasattr(asyncio.get_running_loop(), "run_once"))
        self.assertTrue(hasattr(asyncio.get_running_loop(), "stop_if_running"))
        self.assertTrue(hasattr(asyncio.get_running_loop(), "_run_forever_setup"))
        self.assertTrue(hasattr(asyncio.get_running_loop(), "_run_forever_cleanup"))

        keep_loop_running = carb.settings.get_settings().get("/exts/omni.kit.async_engine/keep_loop_running") or False
        self.assertEqual(hasattr(asyncio.get_running_loop(), "_has_work"), keep_loop_running)

    async def test_nested_asyncio_run_with_exceptions(self):

        # Add an event subscription.
        app = omni.kit.app.get_app()

        class NestedAsyncioRunWithException(Exception):
            """
            A custom exception type for this test, which allows us to filter out the (expected) failure messages that
            occur from running this test via the `stdoutFailPatterns.exclude` filter in this extension's config file,
            since simply wrapping the failure code inside a try-except block isn't enough to get it to pass.
            """
            pass

        fut = Future()
        # Define a coroutine that conditionally raises an exception when evaluated.
        async def inner_conditionally_raise_exception(raise_exception: bool):
            await asyncio.sleep(0.5)
            if raise_exception:
                raise NestedAsyncioRunWithException()
            fut.set_result(True)

        # Update subscription function that calls asyncio.run() and raises an exception.
        def raise_exception(*args):
            asyncio.run(inner_conditionally_raise_exception(raise_exception=True))
        sub = get_eventdispatcher().observe_event(event_name=omni.kit.app.GLOBAL_EVENT_UPDATE, on_event=raise_exception)

        # Step to the next frame. The future should not get set due to the raised exception, but the async engine event
        # loop should still be intact.
        #
        # Note that for testing purposes, we need to reroute the thrown exception to the test call stack in order to
        # reason about it without causing the entire test to fail; unfortunately there does not seem to be a way to
        # allow this test to conditionally fail without potentially filtering out other invalid error states (e.g., via
        # stdoutFailPatterns) or throwing the exception from the async_engine without any tracebacks (to reduce the
        # amount of filtering that would be required for catching failure patterns, which also didn't seem like a great
        # trade-off).
        asyncio._raise_exception = False
        await app.next_update_async()
        self.assertFalse(fut.done())
        self.assertFalse(asyncio._raise_exception)
        self.assertTrue(isinstance(asyncio._prev_exception, NestedAsyncioRunWithException))
        self.assertFalse(asyncio._ov_loop.is_closed())

        # We should still be able to execute other coroutines on the main event loop.
        asyncio._raise_exception = True
        update_number = app.get_update_number()
        def do_not_raise_exception(*args):
            asyncio.run(inner_conditionally_raise_exception(raise_exception=False))
        sub = get_eventdispatcher().observe_event(event_name=omni.kit.app.GLOBAL_EVENT_UPDATE, on_event=do_not_raise_exception)
        res = await asyncio.ensure_future(_async_factorial(5))
        await app.next_update_async()
        self.assertEqual(app.get_update_number(), update_number + 1)
        self.assertTrue(fut.done())
        self.assertTrue(fut.result())
        self.assertEqual(res, math.factorial(5))
        self.assertTrue(asyncio._raise_exception)
        self.assertTrue(isinstance(asyncio._prev_exception, NestedAsyncioRunWithException))  # Should not have changed.

        sub.reset()

    @unittest.skipIf(not carb.settings.get_settings().get(f"/tests/selectorTest"), "Only for selector test")
    async def test_is_selector(self):
        self.assertTrue(isinstance(asyncio.get_running_loop(), asyncio.SelectorEventLoop))
