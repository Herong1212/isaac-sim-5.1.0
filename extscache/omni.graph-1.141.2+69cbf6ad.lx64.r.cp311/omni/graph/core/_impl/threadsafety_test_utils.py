"""Utilities for Running Threadsafety Unit Tests from Python Generators for OG nodes"""

import omni.graph.core as og
import omni.kit.app


class ThreadsafetyTestUtils:
    """Utilities for Running Threadsafety Unit Tests from Python Generators for OG nodes"""

    # Max number of graph instances to spawn for thread-safety tests.
    MAX_GRAPH_INSTANCES = 24

    # Variables for specifying evaluation type with "yield" statements.
    EVALUATION_ALL_GRAPHS = (
        0  # yield EVALUATION_ALL_GRAPHS is equivalent to await og.Controller.evaluate() (and is the default behavior).
    )
    EVALUATION_WAIT_FRAME = (
        1  # yield EVALUATION_WAIT_FRAME is equivalent to await omni.kit.app.get_app().next_update_async()
    )

    # List of stateful values/objects/attributes we wish to share
    # across all threading test instances (e.g. a single prim in the
    # stage that we want to use for all graph instances in the threading
    # safety test).
    threading_cache = []

    # Internal, per-test-instance list of indices that demarcate each
    # test's index in the thread cache as they are being executed.
    thread_cache_indices = [0] * MAX_GRAPH_INSTANCES

    # Adds data to the threading cache if it hasn't already been added,
    # and returns said data to the callee.
    @classmethod
    def add_to_threading_cache(cls, test_instance_id: int, code):
        """Add some data that needs to be shared across test instances to a single, shared cache"""
        if cls.thread_cache_indices[test_instance_id] >= len(cls.threading_cache):
            cls.threading_cache.append(code)
        result = cls.threading_cache[cls.thread_cache_indices[test_instance_id]]
        cls.thread_cache_indices[test_instance_id] += 1
        return result

    # Evaluate a function once in a threaded test during the first test instance
    # execution. Useful for setting some test states upfront/at the start of the test
    # and avoiding unnecessary resets while the rest of the test instance generators
    # get iterated through.
    @classmethod
    def single_evaluation_first_test_instance(cls, test_instance_id: int, func, *args, **kwargs):
        """Method that evaluates a piece of code once during the first test instance"""
        if test_instance_id == 0:
            return func(*args, **kwargs)
        return None

    # Evaluate a function once in a threaded test during the last test instance
    # execution. Useful for releasing test resources at the very end of a test.
    @classmethod
    def single_evaluation_last_test_instance(cls, test_instance_id: int, func, *args, **kwargs):
        """Method that evaluates a piece of code once during the last test instance"""
        if test_instance_id == cls.MAX_GRAPH_INSTANCES - 1:
            return func(*args, **kwargs)
        return None

    # Decorator for making a serial test (i.e. creating a single
    # test graph instance) from a test generator.
    @classmethod
    def make_serial_test(cls, test_generator):
        """Make a serial test from a test generator"""
        # Clear all caches/internal data prior to test generation.
        cls.threading_cache.clear()
        cls.thread_cache_indices = [0] * cls.MAX_GRAPH_INSTANCES

        # Iterate through the test generator once, evaluate
        # based on user-specified yield outputs. Defaults
        # to evaluating any existing test graphs.
        async def wrapper(self):
            for gen_test_yield in test_generator(self):
                if gen_test_yield == cls.EVALUATION_WAIT_FRAME:
                    await omni.kit.app.get_app().next_update_async()
                else:
                    await og.Controller.evaluate()

        return wrapper

    # Decorator for making a multithreading test (i.e. creating multiple
    # duplicates of a single test generator, which will typically result in
    # multiple identical graphs being instanced, and attempting to execute
    # them concurrently via the Execution Framework) from a test generator.
    @classmethod
    def make_threading_test(cls, test_generator):
        """Make a thread-safety test from a test generator"""
        # Clear all caches/internal data prior to test generation.
        cls.threading_cache.clear()
        cls.thread_cache_indices = [0] * cls.MAX_GRAPH_INSTANCES

        async def wrapper(self):
            # Construct multiple identical test generator objects.
            gen_tests = []
            for i in range(0, cls.MAX_GRAPH_INSTANCES):
                gen_tests.append(test_generator(self, i))

            # Iterate through each test generator object, which
            # will (presumably) run the written unit test on different
            # test graph instances/setups. Whenever any "yield" statement
            # are reached the loop will wait until iteration has reached
            # that same point across all test generator objects before
            # evaluating concurrently (either by evaluating all graphs,
            # which is the default behavior, or by waiting a frame if the
            # test writer specified that course of action).
            with og.Settings.temporary(og.Settings.AUTO_INSTANCING_ENABLED, False):
                keep_iterating = True
                while keep_iterating:
                    eval_type = cls.EVALUATION_ALL_GRAPHS
                    for idx, gen_test in enumerate(gen_tests):
                        try:
                            gen_test_yield = next(gen_test)
                        except StopIteration:
                            # We only break the loop once the final test generator
                            # instance has reached its end.
                            if idx == cls.MAX_GRAPH_INSTANCES - 1:
                                keep_iterating = False
                                break
                        else:
                            if gen_test_yield == cls.EVALUATION_WAIT_FRAME:
                                eval_type = cls.EVALUATION_WAIT_FRAME
                    if eval_type == cls.EVALUATION_WAIT_FRAME:
                        await omni.kit.app.get_app().next_update_async()
                    else:
                        await og.Controller.evaluate()

        return wrapper
