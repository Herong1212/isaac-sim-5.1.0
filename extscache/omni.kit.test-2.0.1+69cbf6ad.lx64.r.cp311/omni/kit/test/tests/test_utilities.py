
import omni.kit.test


class TestUtilities(omni.kit.test.AsyncTestCase):
    async def test_assert_true_with_retry(self):
        n = 0
        def counter():
            nonlocal n
            n += 1
            return n // 10

        await self.assertTrueWithRetry(counter, 1, 10)

    async def test_assert_equal_with_retry(self):
        n = 0
        def counter():
            nonlocal n
            n += 1
            return n

        await self.assertEqualWithRetry(counter, 10, 1, 10)