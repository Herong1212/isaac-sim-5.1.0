import omni.kit.test
import time
import asyncio
from unittest.mock import patch, MagicMock
from omni.kit.registry.nucleus.utils.omni_client_utils import retry_on_connection_error, retry_on_connection_error_async, get_retry_parameters
from omni.client import Result


class TestUtils(omni.kit.test.AsyncTestCase):
    async def test_retry_on_connection_error(self):
        # Test synchronous retry decorator
        call_count = 0

        @retry_on_connection_error
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Simulate connection errors for first 2 calls
                return Result.ERROR_CONNECTION
            return Result.OK

        # Test successful retry with mocked sleep and logging
        with patch('time.sleep') as mock_sleep, \
             patch('carb.log_error') as mock_log_error, \
             patch('carb.log_warn') as mock_log_warn, \
             patch('omni.kit.registry.nucleus.utils.omni_client_utils.get_retry_parameters') as mock_get_retry_params:
            # Set non-default values
            mock_get_retry_params.return_value = (12, 2.0, 30.0)  # max_retries, base_delay, max_delay
            result = test_func()
            self.assertEqual(result, Result.OK)
            self.assertEqual(call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)  # Should sleep twice before success
            self.assertEqual(mock_log_error.call_count, 0)  # No errors should be logged
            self.assertEqual(mock_log_warn.call_count, 2)  # warn logs for retries

        # Test max retries reached
        call_count = 0

        @retry_on_connection_error
        def failing_func():
            nonlocal call_count
            call_count += 1
            return Result.ERROR_CONNECTION

        with patch('time.sleep') as mock_sleep, \
             patch('carb.log_error') as mock_log_error, \
             patch('carb.log_warn') as mock_log_warn, \
             patch('omni.kit.registry.nucleus.utils.omni_client_utils.get_retry_parameters') as mock_get_retry_params:
            # Set non-default values
            mock_get_retry_params.return_value = (12, 2.0, 30.0)  # max_retries, base_delay, max_delay
            result = failing_func()
            self.assertEqual(result, Result.ERROR_CONNECTION)
            self.assertEqual(call_count, 12)  # MAX_RETRIES
            self.assertEqual(mock_sleep.call_count, 11)  # Should sleep 11 times before giving up
            self.assertEqual(mock_log_error.call_count, 0)  # No errors should be logged for max retries
            self.assertEqual(mock_log_warn.call_count, 11 + 1)  # warn logs for each retry + max retries

    async def test_retry_on_connection_error_async(self):
        # Test asynchronous retry decorator
        call_count = 0

        @retry_on_connection_error_async
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Simulate connection errors for first 2 calls
                return Result.ERROR_CONNECTION
            return Result.OK

        # Test successful retry with mocked sleep and logging
        with patch('asyncio.sleep') as mock_sleep, \
             patch('carb.log_error') as mock_log_error, \
             patch('carb.log_warn') as mock_log_warn, \
             patch('omni.kit.registry.nucleus.utils.omni_client_utils.get_retry_parameters') as mock_get_retry_params:
            # Set non-default values
            mock_get_retry_params.return_value = (12, 2.0, 30.0)  # max_retries, base_delay, max_delay
            result = await test_func()
            self.assertEqual(result, Result.OK)
            self.assertEqual(call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)  # Should sleep twice before success
            self.assertEqual(mock_log_error.call_count, 0)  # No errors should be logged
            self.assertEqual(mock_log_warn.call_count, 2)  # warn logs for retries

        # Test max retries reached
        call_count = 0

        @retry_on_connection_error_async
        async def failing_func():
            nonlocal call_count
            call_count += 1
            return Result.ERROR_CONNECTION

        with patch('asyncio.sleep') as mock_sleep, \
             patch('carb.log_error') as mock_log_error, \
             patch('carb.log_warn') as mock_log_warn, \
             patch('omni.kit.registry.nucleus.utils.omni_client_utils.get_retry_parameters') as mock_get_retry_params:
            # Set non-default values
            mock_get_retry_params.return_value = (12, 2.0, 30.0)  # max_retries, base_delay, max_delay
            result = await failing_func()
            self.assertEqual(result, Result.ERROR_CONNECTION)
            self.assertEqual(call_count, 12)  # MAX_RETRIES
            self.assertEqual(mock_sleep.call_count, 11)  # Should sleep 11 times before giving up
            self.assertEqual(mock_log_error.call_count, 0)  # No error should be logged for max retries
            self.assertEqual(mock_log_warn.call_count, 11 + 1)  # warn logs for each retry + max retries

        # Test with tuple result
        call_count = 0

        @retry_on_connection_error_async
        async def tuple_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return (Result.ERROR_CONNECTION, None)
            return (Result.OK, "data")

        with patch('asyncio.sleep') as mock_sleep, \
             patch('carb.log_error') as mock_log_error, \
             patch('carb.log_warn') as mock_log_warn, \
             patch('omni.kit.registry.nucleus.utils.omni_client_utils.get_retry_parameters') as mock_get_retry_params:
            # Set non-default values
            mock_get_retry_params.return_value = (12, 2.0, 30.0)  # max_retries, base_delay, max_delay
            result = await tuple_func()
            self.assertEqual(result, (Result.OK, "data"))
            self.assertEqual(call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)  # Should sleep twice before success
            self.assertEqual(mock_log_error.call_count, 0)  # No errors should be logged
            self.assertEqual(mock_log_warn.call_count, 2)  # warn logs for retries
