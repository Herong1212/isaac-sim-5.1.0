import asyncio
import concurrent.futures
import tempfile
import weakref
import time
import os
import unittest

import omni.kit.test
import omni.kit.app
import omni.client
import omni.client.utils as clientutils

class TestClient(omni.kit.test.AsyncTestCase):
    async def test_client_utils(self):
        self.assertEqual(
            clientutils.make_file_url_if_possible("anon:000001F0B86967D0:World3.usd"),
            "anon:000001F0B86967D0:World3.usd"
        )
        self.assertEqual(
            clientutils.make_file_url_if_possible("omniverse:/test/test.usd"),
            "omniverse:/test/test.usd"
        )
        self.assertEqual(
            clientutils.make_file_url_if_possible("./test.usd"),
            "./test.usd"
        )

        if os.name == "nt":
            self.assertEqual(
                clientutils.make_file_url_if_possible("c:/test.usd"),
                "file:/C:/test.usd"
            )
            self.assertEqual(
                clientutils.make_file_url_if_possible("file:/c:/test.usd"),
                "file:/c:/test.usd"
            )
            # Windows will treat path prefixed with "/" as relative path
            self.assertEqual(
                clientutils.make_file_url_if_possible("/test/test.usd"),
                "/test/test.usd"
            )

            self.assertEqual(
                clientutils.make_relative_url_if_possible("c:/b.usd", "c:/a.usd"),
                "./a.usd"
            )
            self.assertEqual(
                clientutils.make_relative_url_if_possible("omniverse:/test/b.usd", "c:/a.usd"),
                "C:/a.usd"
            )
            self.assertEqual(
                clientutils.make_relative_url_if_possible("anon:000001F0B86967D0:World3.usd", "c:/a.usd"),
                "C:/a.usd"
            )
            self.assertEqual(
                clientutils.make_relative_url_if_possible("c:/b.usd", "./test/a.usd"),
                "./test/a.usd"
            )
            # Windows will treat path prefixed with "/" as relative path
            self.assertEqual(
                clientutils.make_relative_url_if_possible("c:/b.usd", "/test/a.usd"),
                "/test/a.usd"
            )
            self.assertEqual(
                clientutils.make_relative_url_if_possible("c:/b.usd", "anon:xxxx:a.usd"),
                "anon:xxxx:a.usd"
            )

            self.assertEqual(
                clientutils.make_absolute_url_if_possible("c:/b.usd", "c:/a.usd"),
                "C:/a.usd"
            )
            self.assertEqual(
                clientutils.make_absolute_url_if_possible("omniverse:/test/b.usd", "c:/a.usd"),
                "C:/a.usd"
            )
            self.assertEqual(
                clientutils.make_absolute_url_if_possible("anon:000001F0B86967D0:World3.usd", "c:/a.usd"),
                "C:/a.usd"
            )
            self.assertEqual(
                clientutils.make_absolute_url_if_possible("c:/b.usd", "./test/a.usd"),
                "C:/test/a.usd"
            )
            self.assertEqual(
                clientutils.make_absolute_url_if_possible("c:/b.usd", "/test/a.usd"),
                "C:/test/a.usd"
            )
            self.assertEqual(
                clientutils.make_absolute_url_if_possible("c:/b.usd", "anon:xxxx:a.usd"),
                "anon:xxxx:a.usd"
            )
            self.assertTrue(clientutils.equal_urls("c:/test", "c:/test"))
            self.assertFalse(clientutils.equal_urls("c:/test/", "c:/test"))
            self.assertTrue(clientutils.equal_urls("file:/c:/test", "c:/test"))
            self.assertFalse(clientutils.equal_urls("file:/c:/test", "anon:/test"))

            # For UNC path, keep it untouched for now.
            self.assertEqual(clientutils.normalize_url("file://server/share/test"), "file://server/share/test")
            self.assertEqual(clientutils.normalize_url("//server/share/test"), "//SERVER/SHARE/test")
            self.assertEqual(clientutils.normalize_url("\\\\server\\share\\test"), "//SERVER/SHARE/test")

            # For local filesystem paths, ensure scheme is removed.
            self.assertEqual(clientutils.normalize_url("file:/c:/test"), clientutils.normalize_url("c:/test"))
            self.assertEqual(clientutils.normalize_url("file:/C:/test"), clientutils.normalize_url("c:/test"))
            self.assertEqual(clientutils.normalize_url("C:/test"), clientutils.normalize_url("c:/test"))
            self.assertEqual(clientutils.normalize_url("C:\\test"), clientutils.normalize_url("c:/test"))
            self.assertEqual(clientutils.normalize_url("c:/test"), clientutils.normalize_url("c:/test"))
            self.assertEqual(clientutils.normalize_url("file:/C:/test"), clientutils.normalize_url("file:/c:/test"))
            self.assertNotEqual(clientutils.normalize_url("anon:/C:/test"), clientutils.normalize_url("file:/c:/test"))

            self.assertTrue(clientutils.is_local_url("C:/temp/foo.usd"))
            self.assertTrue(clientutils.is_local_url("z:/temp/foo.usd"))
        else:
            self.assertTrue(clientutils.is_local_url("/home/user/data/foo.usd"))
            self.assertEqual(
                clientutils.make_file_url_if_possible("/test/test.usd"),
                "file:/test/test.usd"
            )
            self.assertEqual(
                clientutils.make_file_url_if_possible("file:/test/test.usd"),
                "file:/test/test.usd"
            )
            self.assertEqual(
                clientutils.make_relative_url_if_possible("/test/b.usd", "/test/a.usd"),
                "./a.usd"
            )
            self.assertEqual(
                clientutils.make_relative_url_if_possible("omniverse:/test/b.usd", "/test/a.usd"),
                "/test/a.usd"
            )
            self.assertEqual(
                clientutils.make_relative_url_if_possible("anon:000001F0B86967D0:World3.usd", "/test/a.usd"),
                "/test/a.usd"
            )
            self.assertEqual(
                clientutils.make_relative_url_if_possible("/test/b.usd", "./test/a.usd"),
                "./test/a.usd"
            )
            self.assertEqual(
                clientutils.make_absolute_url_if_possible("/test/b.usd", "/test/a.usd"),
                "/test/a.usd"
            )
            self.assertEqual(
                clientutils.make_absolute_url_if_possible("omniverse:/test/b.usd", "/test/a.usd"),
                "/test/a.usd"
            )
            self.assertEqual(
                clientutils.make_absolute_url_if_possible("anon:000001F0B86967D0:World3.usd", "/test/a.usd"),
                "/test/a.usd"
            )
            self.assertEqual(
                clientutils.make_absolute_url_if_possible("/test/b.usd", "./test/a.usd"),
                "/test/test/a.usd"
            )
            self.assertTrue(clientutils.equal_urls("/test", "/test"))
            self.assertFalse(clientutils.equal_urls("/test/", "/test"))
            self.assertTrue(clientutils.equal_urls("file:/test", "/test"))
            self.assertFalse(clientutils.equal_urls("file:/test", "anon:/test"))

            self.assertEqual(clientutils.normalize_url("file:/test"), clientutils.normalize_url("/test"))
            self.assertEqual(clientutils.normalize_url("/test"), clientutils.normalize_url("/test"))
            self.assertNotEqual(clientutils.normalize_url("anon:/test"), clientutils.normalize_url("file:/test"))

        self.assertTrue(clientutils.equal_urls("", ""))
        self.assertTrue(clientutils.equal_urls("./test", "./test"))
        self.assertTrue(clientutils.equal_urls("https://server/test.usd?a=1", "https://server/test.usd"))
        self.assertFalse(clientutils.equal_urls(
            "https://server/test.usd?a=1", "https://server/test.usd", ignore_query_string=False)
        )
        self.assertTrue(clientutils.equal_urls(
            "https://test@server/test.usd", "https://server/test.usd")
        )
        self.assertFalse(clientutils.equal_urls(
            "https://test@server/test.usd", "https://server/test.usd", ignore_user=False)
        )
        self.assertTrue(clientutils.equal_urls(
            "https://server:8891/test.usd", "https://server/test.usd")
        )
        self.assertFalse(clientutils.equal_urls(
            "https://server:8891/test.usd", "https://server/test.usd", ignore_port=False)
        )
        self.assertTrue(clientutils.equal_urls(
            "https://test@server:8891/test.usd?a=1", "https://server/test.usd")
        )
        self.assertTrue(clientutils.is_valid_url("https://test@server:8891/test.usd?a=1"))
        self.assertFalse(clientutils.is_valid_url("www.example.com"))
        self.assertTrue(clientutils.is_tagging_enabled("omniverse://test/test.usd"))
        self.assertTrue(clientutils.is_omni_objects_enabled("omniverse://test/test.usd"))
        self.assertFalse(clientutils.is_tagging_enabled("test/test.usd"))
        self.assertFalse(clientutils.is_omni_objects_enabled("test/test.usd"))
