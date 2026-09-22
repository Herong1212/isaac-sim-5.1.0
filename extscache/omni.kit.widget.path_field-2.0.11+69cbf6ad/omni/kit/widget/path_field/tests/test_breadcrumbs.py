## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test

from unittest.mock import Mock, patch
from ..widget import PathField


class TestBreadCrumbs(omni.kit.test.AsyncTestCase):
    """Testing PathField.set_path"""
    async def setUp(self):
        self.test_paths = {
            "omniverse://ov-test/NVIDIA/Samples": ["omniverse://", "ov-test", "NVIDIA", "Samples"],
            "my-computer://C:/Users/jack": ["my-computer://", "C:", "Users", "jack"],
            "my-computer:///home/jack": ["my-computer://", "", "home", "jack"],
            "C:/Users/jack": ["C:", "Users", "jack"],
            "/": [""],
            "/home/jack": ["", "home", "jack"],
        }

    async def tearDown(self):
        pass

    async def test_breadcrumbs_succeeds(self):
        """Testing PathField.set_path correctly initializes breacrumbs"""
        mock_path_handler = Mock()
        under_test = PathField(separator="/", prefix_separator="://", apply_path_handler=mock_path_handler)

        for path, expected in self.test_paths.items():
            under_test.set_path(path)
            expected_path = ""
            for breadcrumb, _ in under_test._breadcrumbs:
                expected_step = expected.pop(0)
                expected_path += expected_step
                # Confirm when breadcrumb clicked, it triggers callback with expected path
                breadcrumb.call_clicked_fn()
                mock_path_handler.assert_called_with(expected_path)
                expected_path += "/" if not expected_step.endswith("://") else ""
