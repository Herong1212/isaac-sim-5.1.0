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

# Relevant references:
# Boto3 API for S3 - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html

import io
import os
import sys
import threading
from pathlib import Path

import carb

# import boto3 - boto3 is lazily imported to avoid impact on startup time (~100 ms)
from botocore.exceptions import ClientError, NoCredentialsError

from .base import BackendError, BaseBackend


class S3BackendError(BackendError):
    """Base exception for errors raised by the S3 backend registry"""

    def __init__(self, msg=None):
        if msg is None:
            msg = f"An S3 backend error was encountered: {msg}"
        super().__init__(msg)


class S3Backend(BaseBackend):
    """Writer backend for saving generated data to an S3 bucket.

    This backend requires that AWS credentials are set up in ~/.aws/credentials or the AWS_ACCESS_KEY_ID
    and AWS_SECRET_ACCESS_KEY environment variables be defined.
    See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    Args:
        key_prefix: Prefix path within S3 bucket. When calling ``write_blob`` or `read_blob`, ``key_prefix`` is joined to
            the ``path`` argument of either methods to produce the full ``Key`` denoting the file location in the bucket.
        bucket: S3 bucket name. Bucket must follow naming rules: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
        region: Optionally specify S3 Region name (eg. `us-east-2`)
        endpoint_url: Optionally specify S3 endpoint URL (eg. `s3.us-east-2.amazonaws.com`)
        overwrite: If ``True``, overwrite existing ``key_prefix`` path. If ``False``, a suffix in the format of
            `_000N` is added to the ``key_prefix`` name, where ``N`` is the next available number. Defaults to False.
    """

    def __init__(
        self, bucket: str, key_prefix: str, region: str = None, endpoint_url: str = None, overwrite: bool = False
    ):
        import boto3

        self.output_dir = key_prefix  # kept for backwards compatibility
        self.key_prefix = key_prefix
        self._bucket = bucket
        carb.log_info(f"S3 configured to save to the bucket named: {self._bucket}")

        self._region = region
        self._endpoint_url = endpoint_url

        # Create an S3 Client
        s3_session = boto3.Session()
        self._s3_client = s3_session.client(
            "s3",
            region_name=self._region,
            endpoint_url=self._endpoint_url,
        )

        try:
            # Basic query to see if client is set up properly
            response = self._s3_client.list_buckets()
        except NoCredentialsError:
            raise S3BackendError(
                "S3Backend: No credentials file in ~/.aws or AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
            )

        try:
            create_bucket(self._bucket, self._region, self._endpoint_url)
        except ClientError as e:
            raise S3BackendError(f"Unable to initialize S3Backend. Error creating bucket: {e}")

        suffix = 0
        while not overwrite and self._prefix_exists(self.key_prefix):
            suffix += 1
            self.key_prefix = f"{key_prefix}_{suffix:04}"

    def write_blob(self, path: str, data: bytes) -> None:
        """Upload a file to the S3 bucket

        Args:
            path: Filepath to upload
            data: Data to upload

        Returns:
            True if file was uploaded, else False
        """
        # Append the object path to the output path
        key = Path(self.key_prefix).joinpath(path).as_posix()

        # Upload the file
        try:
            data = io.BytesIO(data)
            self._s3_client.upload_fileobj(Fileobj=data, Bucket=self._bucket, Key=key)
        except ClientError as e:
            carb.log_error(e)
            return False

        return True

    def read_blob(self, path: str) -> bytes:
        """Read file data from S3 bucket

        Args:
            path: Path in bucket (S3 Key) to read data from.

        Returns:
            Buffer of data
        """
        key = Path(self.key_prefix).joinpath(path).as_posix()
        buf = io.BytesIO()
        try:
            self._s3_client.download_fileobj(Bucket=self._bucket, Key=key, Fileobj=buf)
        except ClientError as e:
            raise ValueError(f"No file found in bucket `{self._bucket}` at key `{key}`. {e}")

        return buf.getvalue()

    def _prefix_exists(self, key_prefix):
        response = self._s3_client.list_objects(Bucket=self._bucket, Prefix=key_prefix, MaxKeys=1)
        return "Contents" in response


def bucket_exists(bucket: str, region=None, endpoint_url=None):
    """Check that an S3 bucket exists

    Args:
        bucket: S3 bucket name
        region: Optionally specify S3 Region name (eg. `us-east-2`)
        endpoint_url: Optionally specify S3 endpoint URL (eg. `s3.us-east-2.amazonaws.com`)

    Returns:
        True if bucket exists, else False
    """
    import boto3

    # Retrieve the list of existing buckets
    s3_client = boto3.client("s3", region_name=region, endpoint_url=endpoint_url)

    try:
        s3_client.get_bucket_acl(Bucket=bucket)
        return True
    except s3_client.exceptions.NoSuchBucket:
        return False


def create_bucket(bucket: str, region: str = None, endpoint_url: str = None) -> None:
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1). If bucket already exists, no action is taken.

    Args:
        bucket: S3 bucket name
        region: Optionally specify S3 Region name (eg. `us-east-2`)
        endpoint_url: Optionally specify S3 endpoint URL (eg. `s3.us-east-2.amazonaws.com`)
    """
    import boto3

    if bucket_exists(bucket, region, endpoint_url):
        carb.log_info(f"S3Backend: Bucket ({bucket}) already exists.")
        return
    else:
        carb.log_info(f"S3Backend: Creating bucket ({bucket}).")

    # Create bucket
    if region is None:
        s3_client = boto3.client("s3", endpoint_url=endpoint_url)
        s3_client.create_bucket(Bucket=bucket)
    else:
        s3_client = boto3.client("s3", region_name=region, endpoint_url=endpoint_url)
        location = {"LocationConstraint": region}
        s3_client.create_bucket(Bucket=bucket, CreateBucketConfiguration=location)


def upload_file(
    file_name: str, bucket: str, region: str = None, endpoint_url: str = None, object_name: str = None
) -> bool:
    """Upload a file to an S3 bucket

    Args:
        file_name: File to upload
        bucket: S3 bucket name
        region: Optionally specify S3 Region name (eg. `us-east-2`)
        endpoint_url: Optionally specify S3 endpoint URL (eg. `s3.us-east-2.amazonaws.com`)
        object_name: Optionally specify a S3 object name. If not specified then file_name is used.

    Returns:
        True if file was uploaded, else False
    """
    import boto3

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client("s3", region_name=region, endpoint_url=endpoint_url)

    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        carb.log_error(e)
        return False

    return True
