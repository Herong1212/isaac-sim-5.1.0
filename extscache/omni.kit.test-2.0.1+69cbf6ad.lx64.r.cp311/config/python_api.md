# Public API for module omni.kit.test:

## Classes

- class AsyncTestCase(unittest.TestCase)
  - fail_on_log_error: bool
  - async def run(self, result = None)
  - async def wait_n_updates(self, n_frames: int = 3)
  - async def retry_until_success(self, operation: Callable[[], Any], wait_frames: int = 2, max_retries: int = 50) -> Any
  - async def assertTrueWithRetry(self, operation: Callable[[], Any], wait_frames: int = 2, max_retries: int = 50)
  - async def assertEqualWithRetry(self, operation: Callable[[], Any], expected: Any, wait_frames: int = 2, max_retries: int = 50)
  - def assertEquals(self, *args, **kwargs)

- class AsyncTestCaseFailOnLogError(AsyncTestCase)
  - fail_on_log_error: bool

- class AsyncTestSuite(unittest.TestSuite)
  - async def run(self, result, debug = False)

- class BenchmarkTestCase(AsyncTestCase)
  - def __init__(self, tests = (), methodName = 'runTest')
  - def set_metric_sample(self, name: str, value: Union[int, float, bool], unit: Optional[str] = None)
  - def set_metric_sample_array(self, name: str, values: Union[List[int], List[float]], unit: Optional[str] = None)

- class ExtTest
  - def __init__(self, ext_id: str, ext_info: carb.dictionary.Item, test_config: Dict, test_id: str, is_parallel_run: bool, run_context: TestRunContext, test_app: TestApp, valid = True)
  - def get_cmd(self) -> str
  - def on_start(self)
  - def on_finish(self, test_result: bool)
  - def on_fail(self, fail_message)

- class ExtTestResult
  - def __init__(self)

- class TestPopulateAll(TestPopulator)
  - def __init__(self)
  - def get_tests(self, call_when_done: callable)

- class TestPopulateDisabled(TestPopulator)
  - def __init__(self)
  - def get_tests(self, call_when_done: callable)

- class TestPopulator(abc.ABC)
  - def __init__(self, name: str, description: str)
  - def destroy(self)
  - def get_tests(self, call_when_done: callable)

- class TestReturnCode
  - UNIT_TESTS_FAILED: int
  - UNIT_TEST_TIMEOUT: int
  - EXT_TESTS_FAILED: int

- class TestRunStatus(Enum)
  - UNKNOWN: int
  - RUNNING: int
  - PASSED: int
  - FAILED: int

## Functions

- def add_test_status_report_cb(callback: Callable[[str, TestRunStatus, Any], None])
- def add_test_case_to_tested_extension(test_case: AsyncTestCase, phony_submodule: str = '')
- def get_global_test_output_path()
- def get_setting(path, default = None)
- def get_test_output_path()
- def get_tests(tests_filter = '') -> List
- def get_tests_from_modules(modules, log = _LOG)
- def is_etm_run() -> bool
- def run_tests(tests = None, on_finish_fn = None, on_status_report_fn = None)

## Variables

- DEFAULT_POPULATOR_NAME: str
