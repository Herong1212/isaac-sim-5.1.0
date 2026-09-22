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

import doctest
import io
import os
import shutil
import unittest
import uuid
from pathlib import Path

import boto3
import carb
import numpy as np
import omni.kit
import omni.replicator.core as rep
import omni.replicator.core.functional as F
import omni.usd
from omni.replicator.core import backends
from omni.replicator.core.backends.disk import validate_out_dir

DEFAULT_REPLICATOR_PATH = "omni.replicator_out"


# Unit tests for the Backend output directory validation feature
class TestBackend(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        if os.getenv("ETM_ACTIVE"):
            self.skipTest("skip in ETM to keep tests lean")

        self.absolute_path = (Path.home() / "rep_test_absolute_path").resolve().as_posix()
        self.relative_path = "relative_path_test"
        self.default_replicator_path = (Path.home() / DEFAULT_REPLICATOR_PATH).as_posix()
        self.blob_data = (1234).to_bytes(2, "big")
        self.exr_data = np.ones((1024, 1024), dtype=np.float32)
        carb.settings.get_settings().set("/omni/replicator/backends/disk/root_dir", "")

    def test_docstrings(self):
        """Test module docstring examples"""
        modules = [
            rep.backends.base,
            rep.backends.disk,
            rep.backends.dispatcher,
            rep.functional,
            rep.backends.registry,
            rep.backends.s3,
            # rep.backends.sequential,    # Handled in sequential test file
            rep.backends.telemetry,
        ]
        for module in modules:
            failures, test_counts = doctest.testmod(module)
            if failures:
                self.fail(f"Encountered {failures} failures in {test_counts} tests for {module}.")
            else:
                print(f"{test_counts} tests passed for {module}.")

    async def tearDown(self):
        # Delete file created for absolute path write blob test
        if os.path.exists(self.absolute_path):
            shutil.rmtree(self.absolute_path)

        # Clear AWS env vars
        if "AWS_ACCESS_KEY_ID" in os.environ:
            os.environ.pop("AWS_ACCESS_KEY_ID")
        if "AWS_SECRET_ACCESS_KEY" in os.environ:
            os.environ.pop("AWS_SECRET_ACCESS_KEY")

        if "PassBackend" in rep.backends.BackendRegistry.get_registered_backends():
            rep.backends.unregister("PassBackend")

        # Delete file created for relative path write blob test
        if os.path.exists(os.path.join(self.default_replicator_path, self.relative_path)):
            shutil.rmtree(os.path.join(self.default_replicator_path, self.relative_path))
        await omni.usd.get_context().new_stage_async()

    async def test_backend_creation(self):
        # only test disk backend, we know there will be only 1 disk backend because we only provide output_dir
        backend_abs = backends.BackendDispatch(output_dir=self.absolute_path)
        for backend in backend_abs._backends:
            if backend.__class__.__name__ == "DiskBackend":
                disk_backend = backend
                break
        self.assertEquals(
            Path(disk_backend.output_dir).resolve().as_posix(), Path(self.absolute_path).resolve().as_posix()
        )

        backend_rel = backends.BackendDispatch(output_dir=self.relative_path)
        for backend in backend_rel._backends:
            if backend.get_name() == "DiskBackend":
                disk_backend = backend
                break
        self.assertEquals(
            Path(disk_backend.output_dir).as_posix(),
            Path(self.default_replicator_path).joinpath(self.relative_path).resolve().as_posix(),
        )

    async def test_write_blob_for_absolute_path(self):
        backend_abs = backends.BackendDispatch(output_dir=self.absolute_path)
        abs_test_data_path = "absolute_path_test_data.txt"
        backend_abs.schedule(backend_abs.write_blob, data=self.blob_data, path=abs_test_data_path)

        backend_abs.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(self.absolute_path, abs_test_data_path)))

        # Check disk data
        written_data = int.from_bytes(backend_abs.read_blob(abs_test_data_path), "big")
        self.assertEqual(written_data, 1234)

    async def test_write_blob_for_relative_path(self):
        backend_rel = backends.BackendDispatch(output_dir=self.relative_path)
        rel_test_data_path = "relative_path_test_data.txt"
        backend_rel.schedule(backend_rel.write_blob, data=self.blob_data, path=rel_test_data_path)

        backend_rel.wait_until_done()
        self.assertTrue(
            os.path.exists(os.path.join(self.default_replicator_path, self.relative_path, rel_test_data_path))
        )

        # Check disk data
        written_data = int.from_bytes(backend_rel.read_blob(rel_test_data_path), "big")
        self.assertEqual(written_data, 1234)

    async def test_write_blob_for_relative_path_custom_root(self):
        root = os.path.join(Path.home().as_posix(), "custom_root")
        carb.settings.get_settings().set("/omni/replicator/backends/disk/root_dir", root)

        backend_rel = backends.BackendDispatch(output_dir=self.relative_path)
        rel_test_data_path = "relative_path_test_data.txt"
        backend_rel.schedule(backend_rel.write_blob, data=self.blob_data, path=rel_test_data_path)
        backend_rel.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(root, self.relative_path, rel_test_data_path)))

        # Check disk data
        written_data = int.from_bytes(backend_rel.read_blob(rel_test_data_path), "big")
        self.assertEqual(written_data, 1234)

    async def test_absolute_path_validation(self):
        validated_path = validate_out_dir(self.absolute_path)
        self.assertEquals(Path(self.absolute_path).resolve().as_posix(), Path(validated_path).resolve().as_posix())

    async def test_relative_path_validation(self):
        validated_path = validate_out_dir(self.relative_path)

        # Default absolute path created by validate_out_dir given input relative path
        expected_path = Path(self.default_replicator_path).joinpath(self.relative_path).resolve().as_posix()
        self.assertEquals(expected_path, validated_path)

    async def test_s3_connection_failure(self):
        backend_s3_fail = backends.BackendDispatch(
            output_dir="_test_output", key_prefix="_testoutput", bucket="test-bucket-ecameracci"
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

        backend_s3_ok = backends.BackendDispatch(
            use_s3=True, output_dir="_testoutput", key_prefix="_testoutput", bucket="test-bucket-ecameracci"
        )

        # If the S3 backend is successfully created, it will be added to the list
        valid_backends = [backend.get_name() for backend in backend_s3_ok._backends]
        self.assertTrue("S3Backend" in valid_backends, f"Got {valid_backends}")

    @unittest.skipIf(
        "TESTENV_AWS_ID" not in os.environ.keys() or "TESTENV_AWS_KEY" not in os.environ.keys(),
        "TESTENV_AWS_ID or TESTENV_AWS_KEY env vars not set!",
    )
    async def test_s3_create_bucket(self):
        # Set the AWS access keys to test-env keys
        os.environ["AWS_ACCESS_KEY_ID"] = os.environ["TESTENV_AWS_ID"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ["TESTENV_AWS_KEY"]

        # Create a new bucket name
        test_bucket_name = f"replicator-test-s3-create-bucket-{str(uuid.uuid4())[:8]}"

        # Try and initialize backend with new bucket name
        try:
            backend_s3_ok = backends.BackendDispatch(
                use_s3=True, output_dir="_testoutput", key_prefix="_testoutput", bucket=test_bucket_name
            )
        except:
            self.fail("Creating a new bucket when initializing backend failed!")

        s3_client = boto3.client("s3")

        try:
            s3_client.get_bucket_acl(Bucket=test_bucket_name)
        except s3_client.exceptions.NoSuchBucket:
            self.fail("New bucket was not created!")

        # Cleanup
        s3_client.delete_bucket(Bucket=test_bucket_name)

    @unittest.skipIf(
        "TESTENV_AWS_ID" not in os.environ.keys() or "TESTENV_AWS_KEY" not in os.environ.keys(),
        "TESTENV_AWS_ID or TESTENV_AWS_KEY env vars not set!",
    )
    async def test_s3_write_to_test_bucket(self):
        """Test bucket is test-bucket-ecameracci"""
        # Set the AWS access keys to test-env keys
        os.environ["AWS_ACCESS_KEY_ID"] = os.environ["TESTENV_AWS_ID"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ["TESTENV_AWS_KEY"]

        test_backends = backends.BackendDispatch(
            use_s3=True, output_dir="_testoutput", key_prefix="_testoutput", bucket="test-bucket-ecameracci"
        )

        # If the S3 backend is successfully created, it will be added to the list
        valid_backends = [backend.get_name() for backend in test_backends._backends]
        self.assertTrue("S3Backend" in valid_backends, f"Got {valid_backends}")

        path = "s3_write_test.txt"

        # Write the data
        test_backends.schedule(test_backends.write_blob, data=self.blob_data, path=path)

        test_backends.wait_until_done()

        # Check first backend
        written_data = int.from_bytes(test_backends.read_blob(path), "big")
        self.assertEqual(written_data, 1234)

        # Check each backend
        for backend in test_backends._backends:
            written_data = int.from_bytes(backend.read_blob(path), "big")
            self.assertEqual(written_data, 1234, f"Failed to read blob with {backend.get_name()}")

        # Cleanup folder
        s3_client = boto3.client("s3")
        s3_contents = s3_client.list_objects(Bucket="test-bucket-ecameracci", Prefix="_testoutput")["Contents"]
        for file in s3_contents:
            s3_client.delete_object(Bucket="test-bucket-ecameracci", Key=file["Key"])
        s3_client.delete_object(Bucket="test-bucket-ecameracci", Key="_testoutput")

    async def test_write_exr(self):
        backend_abs = backends.BackendDispatch(output_dir=self.absolute_path)
        abs_test_data_path = "exr_data.exr"
        backend_abs.schedule(F.write_image, data=self.exr_data, path=abs_test_data_path)

        backend_abs.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(self.absolute_path, abs_test_data_path)))

        exr_data_read = F.io_functions.read_exr(abs_test_data_path, backend_instance=backend_abs)
        np.testing.assert_allclose(exr_data_read, self.exr_data)

    async def test_backend_get(self):
        backend_abs = backends.get("DiskBackend")
        backend_abs.initialize(output_dir=self.absolute_path)
        abs_test_data_path = "absolute_path_test_data.txt"
        backend_abs.schedule(backend_abs.write_blob, data=self.blob_data, path=abs_test_data_path)

        backend_abs.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(self.absolute_path, abs_test_data_path)))

        # Check disk data
        written_data = int.from_bytes(backend_abs.read_blob(abs_test_data_path), "big")
        self.assertEqual(written_data, 1234)

    async def test_group_backend(self):
        backend_abs1 = backends.get("DiskBackend", init_params={"output_dir": self.absolute_path})
        backend_abs2 = backends.get("DiskBackend", init_params={"output_dir": self.relative_path})

        backend_group = backends.get("BackendGroup")
        backend_group.initialize([backend_abs1, backend_abs2])

        data_path = "test_data.txt"
        backend_group.schedule(backend_group.write_blob, data=self.blob_data, path=data_path)

        # Test first backend
        backend_group.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(self.absolute_path, data_path)))
        written_data = int.from_bytes(backend_group.read_blob(data_path), "big")
        self.assertEqual(written_data, 1234)

        # Test second backend
        self.assertTrue(os.path.exists(os.path.join(self.default_replicator_path, self.relative_path, data_path)))
        written_data = int.from_bytes(backend_group.read_blob(data_path), "big")
        self.assertEqual(written_data, 1234)
