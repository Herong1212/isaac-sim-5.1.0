"""Asynchronous tasks engine for Omniverse Kit.

It runs :mod:`asyncio` ``EventLoop`` every update for one iteration (all scheduled tasks).
"""

import asyncio
import platform
import logging
import threading
import sys
from asyncio import events
from collections.abc import Coroutine

import omni.kit.app
import omni.ext

import carb.settings
import carb.eventdispatcher
from ..main_event_loop_wrapper import MainEventLoopWrapper
from contextlib import suppress

logger = logging.getLogger(__name__)

# Creates an asyncio.Task object or concurrent.futures.Future (different from asyncio.Future) object
# out of a submitted coroutine (depending on whether or not the function was called from the
# main thread), the latter of which gets scheduled to run on the main event loop (which
# ticks on the main thread), and returns said asyncio.Task or concurrent.futures.Future object. This
# method is useful, in part, because the Execution Framework (EF) can orchestrate extensions
# registered to the USD stage update to evaluate on separate worker threads, and if there exists
# any Python code in said extensions operating on non-main threads that attempt to create tasks
# out of coroutines (e.g. via asyncio.ensure_future()), those methods will actually fail
# if there aren't any default event loops set in the thread (basically what happens is
# if ensure_future() isn't passed a specific loop object along with a coroutine object, it'll try
# to obtain the default one set for the current thread via get_running_loop(). But, if no
# such loops exist AND the method is being used in a non-main thread, rather than creating
# a new event loop object against which coroutines are to be scheduled, it'll simply raise
# an exception error. So, one can utilize this method instead so that all coroutine submissions
# in threads without already-set event loops get passed on to the main event loop that was
# spawned by the async engine).
def run_coroutine(coroutine: Coroutine):
    """Submit a coroutine object to the main event loop; return either a Task object
    if the function was called from the main thread, or a concurrent.futures.Future to access
    the result if the function was called from any other non-main thread.

    Args:
        coroutine (:obj:`coroutine`): The coroutine to schedule for execution.

    Returns:
        Union[:obj:`asyncio.Task`, :obj:`concurrent.futures.Future`]: An asyncio.Task if called from the main thread, otherwise a concurrent.futures.Future.

    Raises:
        TypeError: If the provided coroutine is not an actual coroutine object."""
    if not asyncio.iscoroutine(coroutine):
        raise TypeError("run_coroutine only accepts coroutine object.")
    if threading.current_thread() is threading.main_thread():
        return MainEventLoopWrapper.g_main_event_loop.create_task(coroutine)  # This returns an asyncio.Task object!
    else:
        return asyncio.run_coroutine_threadsafe(coroutine, MainEventLoopWrapper.g_main_event_loop)  # This returns a concurrent.futures.Future object!


class _AsyncEngineDriver(omni.ext.IExt):
    """
    Singleton class to connect python asyncio with app update pump. EventLoop runs iteration every IApp update.
    """

    def _patch_event_loop(self, loop_until_done):
        """Monkey-patch the event loop either to keep it always running or just to add a simple run_once function"""
        self._loop._loop_until_done = loop_until_done
        self._loop._is_proactor = hasattr(asyncio, "ProactorEventLoop") and isinstance(self._loop, getattr(asyncio, "ProactorEventLoop"))

        cls = self._loop.__class__

        if not hasattr(cls, "_run_forever_setup"): # Python 3.13, see https://github.com/python/cpython/pull/110773
            assert not hasattr(cls, "_run_forever_cleanup")
            def _run_forever_setup(self):
                if not hasattr(self, "_is_proactor"):
                    self._is_proactor = hasattr(asyncio, "ProactorEventLoop") and isinstance(self, getattr(asyncio, "ProactorEventLoop"))
                # ProactorEventLoop
                if self._is_proactor:
                    assert self._self_reading_future is None
                    self.call_soon(self._loop_self_reading)

                # BaseEventLoop
                self._check_closed()
                self._check_running()
                self._set_coroutine_origin_tracking(self._debug)

                self._old_agen_hooks = sys.get_asyncgen_hooks()
                self._thread_id = threading.get_ident()
                sys.set_asyncgen_hooks(
                    firstiter=self._asyncgen_firstiter_hook,
                    finalizer=self._asyncgen_finalizer_hook
                )
                events._set_running_loop(self)
            cls._run_forever_setup = _run_forever_setup

            def _run_forever_cleanup(self):
                # BaseEventLoop
                self._stopping = False
                self._thread_id = None
                events._set_running_loop(None)
                self._set_coroutine_origin_tracking(False)
                if self._old_agen_hooks is not None:
                    sys.set_asyncgen_hooks(*self._old_agen_hooks)
                    self._old_agen_hooks = None

                # ProactorEventLoop
                if self._is_proactor:
                    if self._self_reading_future is not None:
                        ov = self._self_reading_future._ov
                        self._self_reading_future.cancel()

                        if ov is not None and not ov.pending: # gh-116773 fix
                            self._proactor._unregister(ov)
                        self._self_reading_future = None
            cls._run_forever_cleanup = _run_forever_cleanup

            # This may have been patched already by nest_asyncio or something else.
            if cls.run_forever == asyncio.BaseEventLoop.run_forever:
                def run_forever(self):
                    """Run until stop() is called."""
                    try:
                        self._run_forever_setup()
                        while True:
                            self._run_once()
                            if self._stopping:
                                break
                    finally:
                        self._run_forever_cleanup()
                cls.run_forever = run_forever

        asyncio._orig_run = asyncio.run
        asyncio._ov_loop = self._loop

        # If set to true, exceptions thrown by the patched OV event loop will instead be rerouted to a separate
        # internal parameter instead of simply bubbling up the call stack. Can be useful for capturing async-engine-
        # related errors in different threads/stacks.
        asyncio._raise_exception = True

        # The latest exception that was thrown during event loop execution. Will only be set if `_raise_exception` is
        # set to `False`.
        asyncio._prev_exception = None

        def run(main, *, debug=False):
            asyncio._ov_loop.stop_if_running()
            try:
                retval = asyncio._orig_run(main, debug=debug)
            except Exception as e:
                # If the loop was closed due to an exception being raised, create a new one. One situation where this
                # can happen is if `asyncio.run` is invoked within kit's Python runtime on a coroutine that then raises
                # an exception. This is because `asyncio.run` will re-use whatever event loop already exists on the
                # thread it's being executed on (in this case the `_ov_loop` on the `MainThread`), and close said event
                # loop in the case of an exception (in Python 3.10 this happens more directly: https://github.com/python/cpython/blob/880adf6c318d73d6cf967e4d957d286aad5c5ecf/Lib/asyncio/runners.py#L52,
                # while in Python 3.11+ a separate `Runner` context will shutdown and close the event loop once the
                # scope is exited, which will occur if an exception is raised in the coroutine that's evaluated by
                # the nested `asyncio.run` invocation: https://github.com/python/cpython/blob/3.11/Lib/asyncio/runners.py#L63).
                # So, to handle such situations, we'll simply create a new event loop to replace the closed one,
                # otherwise all async Python coroutines in Kit that wish to run via the main async engine will fail to
                # execute to the lack of an event loop on the main thread.
                if asyncio._ov_loop.is_closed():
                    asyncio._ov_loop = asyncio.new_event_loop()
                events.set_event_loop(asyncio._ov_loop)
                if asyncio._raise_exception:
                    raise e
                else:
                    asyncio._prev_exception = e
                    return
            events.set_event_loop(asyncio._ov_loop)
            return retval
        asyncio.run = run

        if self._keep_loop_running:
            def stop_if_running(self):
                """Runs the loop epilogue code if the loop is running, otherwise does nothing. Preserves stop() state."""
                # We need to preserve the _stopping flag in case someone does stop() / run_forever() to run once.
                stopping = self._stopping
                if self.is_running():
                    self.stop()
                    self._run_forever_cleanup()
                self._stopping = stopping
            cls.stop_if_running = stop_if_running

            cls.super_run_forever = cls.run_forever
            def run_forever(self):
                self.stop_if_running()
                self.super_run_forever()
            cls.run_forever = run_forever

            cls.super_run_until_complete = cls.run_until_complete
            def run_until_complete(self, future):
                self.stop_if_running()
                return self.super_run_until_complete(future)
            cls.run_until_complete = run_until_complete

            def _has_work(self):
                """Returns True if the loop has work that can be done, otherwise returns False."""
                return self._ready or (self._scheduled and self._scheduled[0]._when <= self.time())
            cls._has_work = _has_work

            def run_once(self):
                """Similar to stop()/run_forever() to 'tick' the event loop once. However, this is much more efficient.

                Note: If not is_running(), the loop will be started by calling this function. But the loop will never be
                stopped when this function returns, even if stop() was called prior to this function.

                If the loop-until-done flag is True, this function will step the event loop until there is no work
                remaining. The event loop is always run once even if it appears that no work is queued.
                """
                if not hasattr(self, "_loop_until_done"):
                    self._loop_until_done = not carb.settings.get_settings().get("/exts/omni.kit.async_engine/spinLoopOncePerUpdate")

                # If there's nothing to do, _run_once() will block forever in select() as if run_forever() was called.
                # Give it some nothing to do.
                if not self._has_work():
                    self.call_soon(lambda *args: None)

                while True:
                    # Restart the loop if it's not already running
                    if not self.is_running():
                        self._run_forever_setup()
                    elif not events._get_running_loop():
                        # Register as the running loop for this thread
                        events._set_running_loop(self)
                    else:
                        assert events._get_running_loop() is self

                    # Run at least once
                    self._run_once()

                    # Nothing stops our loop except us
                    self._stopping = False

                    # By default we loop until there is no work to do, but if configured to not loop until done we exit.
                    # TODO: Is there a need for more complex logic here to avoid blocking for too long?
                    if not self._loop_until_done or not self._has_work():
                        events._set_running_loop(None)
                        break
            cls.run_once = run_once

        else:
            def stop_if_running(self):
                pass
            cls.stop_if_running = stop_if_running

            def run_once(self):
                if not hasattr(self, "_loop_until_done"):
                    self._loop_until_done = not carb.settings.get_settings().get("/exts/omni.kit.async_engine/spinLoopOncePerUpdate")
                while True:
                    self.stop()
                    self.run_forever()

                    # The proactor loop always has the self_reading_future event, so <= 1
                    if not self._loop_until_done or (len(self._ready) <= 1 if self._is_proactor else not self._ready):
                        break
            cls.run_once = run_once

    def on_startup(self):
        """ Init settings and path event loop on extension startup"""

        settings = carb.settings.get_settings()
        os_name = "windows" if platform.system().lower() == "windows" else "unix"
        self._shutting_down = False
        settings.set_default("/exts/omni.kit.async_engine/keep_loop_running", True)
        self._keep_loop_running = settings.get("/exts/omni.kit.async_engine/keep_loop_running")
        self._loop = None
        policy_key = f"/exts/omni.kit.async_engine/event_loop_policy_{os_name}"
        policy_type = settings.get(policy_key) or "os_default"
        policy_class = getattr(asyncio, policy_type, type(asyncio.get_event_loop_policy()))
        asyncio.set_event_loop_policy(policy_class())
        carb.log_info(f"policy: {asyncio.get_event_loop_policy()} from {policy_key} = \"{policy_type}\"")

        loop_key = f"/exts/omni.kit.async_engine/event_loop_{os_name}"
        loop_type = settings.get(loop_key) or "os_default"
        loop_class = getattr(asyncio, loop_type, asyncio.get_event_loop_policy()._loop_factory)
        try:
            self._loop = asyncio.get_running_loop()
            carb.log_info(f"There is already a running loop {self._loop}, not creating a new loop")
            self._keep_loop_running = False
        except:
            self._loop = loop_class()
            asyncio.set_event_loop(self._loop)
            carb.log_info(f"loop:   {self._loop} from {loop_key} = \"{loop_type}\"")

        once_per_update = settings.get("/exts/omni.kit.async_engine/spinLoopOncePerUpdate")
        self._patch_event_loop(loop_until_done=not once_per_update)

        settings.set_default("/exts/omni.kit.async_engine/updateSubscriptionOrder",
            omni.kit.app.UPDATE_ORDER_PYTHON_EXEC_END_UPDATE)

        update_subscription_order = settings.get("/exts/omni.kit.async_engine/updateSubscriptionOrder")

        self._update_end_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            order=update_subscription_order,
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            observer_name="[ext: omni.async_engine] AsyncEngineDriver::EndUpdate",
            on_event=lambda _: self._loop.run_once()
        )

        MainEventLoopWrapper.g_main_event_loop = self._loop

        if self._keep_loop_running:
            self._loop._run_forever_setup()

    def on_shutdown(self):
        """Clean event loop and all running async task on extension shutdown"""
        self._update_begin_sub = None
        self._update_end_sub = None

        self._post_update_sub = None

        logger.debug("Beginning shutdown")
        self._loop.stop_if_running() # Make sure the loop is stopped

        # Set the exception handler so we can log any exceptions that happen during shutdown
        phase = "set exception handler"
        logger.debug(f"Starting {phase}")
        def exception_handler(_, exc):
            logger.warning(f"Asyncio exception on shutdown during phase [{phase}]: {exc}")

        self._loop.set_exception_handler(exception_handler)

        # OM-86854: We need to cancel all tasks here, otherwise we'll get an exception like:
        # {'message': 'Task was destroyed but it is pending!', 'task': <Task pending name='Task-33' coro=<CacheStateMenu._on_update.<locals>._ping_cache() running at c:/src/kit/kit/_build/windows-x86_64/release/exts/omni.kit.widget.cache_indicator/omni/kit/widget/cache_indicator/cache_state_menu.py:158>>}
        phase = "cancel all tasks"
        logger.debug(f"Starting {phase}")
        all_tasks = asyncio.all_tasks(self._loop)
        for task in all_tasks:
            logger.debug(f"Cancelling {task}")
            task.cancel()

        # First cancel all the tasks above and then run until complete. This fixes a stall on shutdown when a task is
        # waiting on a pending job that also needed to be cancelled.
        phase = "run cancelled tasks until complete"
        logger.debug(f"Starting {phase}")
        for task in all_tasks:
            logger.debug(f"Run until complete: {task}")
            with suppress(asyncio.CancelledError):
                self._loop.run_until_complete(task)

        # Stop the event loop
        phase = "stop"
        logger.debug(f"Starting {phase}")
        self._loop.stop()

        # Wait for task completion (should basically be done)
        if not self._loop.is_closed():
            phase = "wait for all tasks to complete"
            logger.debug(f"Starting {phase}")
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())

        # Close the event loop
        phase = "close"
        logger.debug(f"Starting {phase}")
        self._loop.close()

        # OM-86854: Resolving {exc} after this point can cause a crash, so be sure to remove our handler
        phase = "after close"
        logger.debug(f"Starting {phase}")
        self._loop.set_exception_handler(None)
        self._loop.engine = None

        logger.debug("Shutdown complete")
