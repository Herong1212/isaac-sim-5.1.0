# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import os
import shutil
import unittest
from pathlib import Path

import boto3
import carb
import numpy as np
import omni.kit
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core.backends import BackendDispatch
from omni.replicator.core.backends.disk import validate_out_dir

DEFAULT_REPLICATOR_PATH = "omni.replicator_out"


# Unit tests for the Backend output directory validation feature
class TestBackend(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        if os.getenv("ETM_ACTIVE"):
            self.skipTest("skip in ETM to keep tests lean")

        self.absolute_path = (Path.home() / "rep_test_absolute_path").as_posix()
        self.relative_path = "relative_path_test"
        self.default_replicator_path = (Path.home() / DEFAULT_REPLICATOR_PATH).as_posix()
        self.blob_data = (1234).to_bytes(2, "big")
        self.exr_data = np.ones((1024, 1024), dtype=np.float32)
        carb.settings.get_settings().set("/omni/replicator/backends/disk/root_dir", "")

    async def tearDown(self):
        # Delete file created for absolute path write blob test
        if os.path.exists(self.absolute_path):
            shutil.rmtree(self.absolute_path)

        # Clear AWS env vars
        if "AWS_ACCESS_KEY_ID" in os.environ:
            os.environ.pop("AWS_ACCESS_KEY_ID")
        if "AWS_SECRET_ACCESS_KEY" in os.environ:
            os.environ.pop("AWS_SECRET_ACCESS_KEY")

        # Delete file created for relative path write blob test
        if os.path.exists(os.path.join(self.default_replicator_path, self.relative_path)):
            shutil.rmtree(os.path.join(self.default_replicator_path, self.relative_path))
        await omni.usd.get_context().new_stage_async()

    async def test_backend_creation(self):
        backend_abs = BackendDispatch({"paths": {"out_dir": self.absolute_path}})
        self.assertEquals(
            Path(backend_abs.output_dir).resolve().as_posix(), Path(self.absolute_path).resolve().as_posix()
        )

        backend_rel = BackendDispatch({"paths": {"out_dir": self.relative_path}})
        self.assertEquals(
            Path(backend_rel.output_dir).resolve().as_posix(),
            Path(self.default_replicator_path).joinpath(self.relative_path).resolve().as_posix(),
        )

    async def test_write_blob_for_absolute_path(self):
        backend_abs = BackendDispatch({"paths": {"out_dir": self.absolute_path}})
        abs_test_data_path = "absolute_path_test_data.txt"
        backend_abs.write_blob(abs_test_data_path, self.blob_data)

        backend_abs.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(self.absolute_path, abs_test_data_path)))

    async def test_write_blob_for_relative_path(self):
        backend_rel = BackendDispatch({"paths": {"out_dir": self.relative_path}})
        rel_test_data_path = "relative_path_test_data.txt"
        backend_rel.write_blob(rel_test_data_path, self.blob_data)

        backend_rel.wait_until_done()
        self.assertTrue(
            os.path.exists(os.path.join(self.default_replicator_path, self.relative_path, rel_test_data_path))
        )

    async def test_write_blob_for_relative_path_custom_root(self):
        root = os.path.join(Path.home().as_posix(), "custom_root")
        carb.settings.get_settings().set("/omni/replicator/backends/disk/root_dir", root)

        backend_rel = BackendDispatch({"paths": {"out_dir": self.relative_path}})
        rel_test_data_path = "relative_path_test_data.txt"
        backend_rel.write_blob(rel_test_data_path, self.blob_data)
        backend_rel.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(root, self.relative_path, rel_test_data_path)))

    async def test_absolute_path_validation(self):
        validated_path = validate_out_dir(self.absolute_path)
        self.assertEquals(Path(self.absolute_path).resolve().as_posix(), Path(validated_path).resolve().as_posix())

    async def test_relative_path_validation(self):
        validated_path = validate_out_dir(self.relative_path)

        # Default absolute path created by validate_out_dir given input relative path
        expected_path = Path(self.default_replicator_path).joinpath(self.relative_path).resolve().as_posix()
        self.assertEquals(expected_path, validated_path)

    @unittest.skipIf(os.name == "nt", "S3 failing on Windows CI runners")
    async def test_s3_connection_failure(self):
        backend_s3_fail = BackendDispatch(
            config={"use_s3": True, "paths": {"out_dir": "_testoutput", "s3_bucket": "test-bucket-ecameracci"}},
            output_dir="_test_output",
        )
        disk_backends = [bk.get_name() for bk in backend_s3_fail._backends if bk.get_name() == "DiskBackend"]
        s3_backends = [bk.get_name() for bk in backend_s3_fail._backends if bk.get_name() == "S3Backend"]

        self.assertEqual(disk_backends, ["DiskBackend"])
        self.assertEqual(s3_backends, [])

    @unittest.skipIf(
        "TESTENV_AWS_ID" not in os.environ.keys() or "TESTENV_AWS_KEY" not in os.environ.keys(),
        "TESTENV_AWS_ID or TESTENV_AWS_KEY env vars not set!",
    )
    async def test_s3_connection_success(self):
        # Set the AWS access keys to test-env keys
        os.environ["AWS_ACCESS_KEY_ID"] = os.environ["TESTENV_AWS_ID"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ["TESTENV_AWS_KEY"]

        backend_s3_ok = BackendDispatch(
            {"use_s3": True, "paths": {"out_dir": "_testoutput", "s3_bucket": "test-bucket-ecameracci"}}
        )
        disk_backends = [bk.get_name() for bk in backend_s3_ok._backends if bk.get_name() == "DiskBackend"]
        s3_backends = [bk.get_name() for bk in backend_s3_ok._backends if bk.get_name() == "S3Backend"]

        # No disk backend should be created
        self.assertEqual(disk_backends, [])
        # If the S3 backend is successfully created, it will be added to the list
        self.assertEqual(s3_backends, ["S3Backend"])

    @unittest.skipIf(
        "TESTENV_AWS_ID" not in os.environ.keys() or "TESTENV_AWS_KEY" not in os.environ.keys(),
        "TESTENV_AWS_ID or TESTENV_AWS_KEY env vars not set!",
    )
    async def test_s3_write_to_test_bucket(self):
        """Test bucket is test-bucket-ecameracci"""
        # Set the AWS access keys to test-env keys
        os.environ["AWS_ACCESS_KEY_ID"] = os.environ["TESTENV_AWS_ID"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ["TESTENV_AWS_KEY"]

        backend_s3_write = BackendDispatch(
            {"use_s3": True, "paths": {"out_dir": "_testoutput", "s3_bucket": "test-bucket-ecameracci"}}
        )
        s3_backends = [bk.get_name() for bk in backend_s3_write._backends if bk.get_name() == "S3Backend"]

        # Confirm no disk backends are created
        disk_backends = [bk.get_name() for bk in backend_s3_write._backends if bk.get_name() == "DiskBackend"]
        self.assertEqual(len(disk_backends), 0, "Expected no disk backends, found at least 1")

        # If the S3 backend is successfully created, it will be added to the list
        self.assertFalse(s3_backends == [])

        # Write the data
        resp = backend_s3_write.write_blob("s3_write_test.txt", self.blob_data)

        # TODO Return whether writing was successful or not in dispatcher
        # For now, just write something and hope no errors are thrown.
        # Verified this writes to S3 when running the test locally.

        # Cleanup folder
        s3_client = boto3.client("s3")
        s3_contents = s3_client.list_objects(Bucket="test-bucket-ecameracci", Prefix="_testoutput")["Contents"]
        for file in s3_contents:
            s3_client.delete_object(Bucket="test-bucket-ecameracci", Key=file["Key"])
        s3_client.delete_object(Bucket="test-bucket-ecameracci", Key="_testoutput")

    async def test_write_exr(self):
        backend_abs = BackendDispatch({"paths": {"out_dir": self.absolute_path}})
        abs_test_data_path = "exr_data.exr"
        backend_abs.write_exr(abs_test_data_path, self.exr_data)

        backend_abs.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(self.absolute_path, abs_test_data_path)))
