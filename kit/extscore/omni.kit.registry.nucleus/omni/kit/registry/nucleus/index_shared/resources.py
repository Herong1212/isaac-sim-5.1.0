import os
import json
import tempfile
from contextlib import nullcontext

import carb
import omni.client
from omni.client import CopyBehavior

from ..iregistry_index import RegistryURLs

from ..utils.common import (
    info_exec_time,
    md5_file,
)
from ..utils.omni_client_utils import upload_file
from ..utils.omni_client_utils import omni_client_copy, omni_client_exists, upload_file


def _serialize_ext_dict(ext_id, ext_dict, tmp_dir):
    data_file = f"{tmp_dir}/{ext_id}.json"
    with open(data_file, "w") as f:
        f.write(json.dumps(ext_dict))
    return data_file


@info_exec_time()
def upload_resources(
    ext_id,
    ext_dict,
    urls: RegistryURLs,
    tmp_dir=None,
    preview_override_path: str = None,
    icon_override_path: str = None,
    skip_images: bool = False,
) -> bool:
    """Upload resources (images and metadata) for a given extension to the remote registry.

    Path to images are taken from the extension metadata, unless path override is provided.
    """

    package_dict = ext_dict.setdefault("package", {})

    # 1. Upload resources (images)
    for k, override_path in [("preview_image", preview_override_path), ("icon", icon_override_path)]:
        if skip_images:
            continue

        if override_path:
            path = override_path
        else:
            path = package_dict.get(k, "")
            if not path:
                continue

            path = os.path.join(ext_dict.get("path", ""), path)

        if not os.path.exists(path):
            continue

        # Hash each resource and upload on remote. Replace resource name with a relative location on remote:
        new_filename = md5_file(path) + os.path.splitext(path)[1]
        remote_path = urls.resources + "/" + new_filename

        remote_relative_path = omni.client.make_relative_url(urls.index_file, remote_path).replace("\\", "/")
        package_dict[k + "_remote"] = remote_relative_path

        if omni_client_exists(remote_path):
            continue

        result = omni_client_copy(
            path, remote_path, f"uploading resource: '{path}'", behavior=CopyBehavior.ERROR_IF_EXISTS
        )
        if result != omni.client.Result.OK:
            carb.log_error(f"Failed to cache a resource from '{path}' to '{remote_path}'. Result: {result}.")
            return False

    # 2. Upload metadata
    ext_name = package_dict.get("name", "")
    # put data in a subfolder with extension name to limit number of files per folder. Client/nucleus is
    # slow otherwise, it tries to list all of them on certain operations like copying a file.
    archive_data_remote = f"{urls.archives}/{ext_name}/{ext_id}.json"
    with tempfile.TemporaryDirectory() if tmp_dir is None else nullcontext(tmp_dir) as tmp_dir:
        archive_data_local = _serialize_ext_dict(ext_id, ext_dict, tmp_dir)
        if not upload_file(archive_data_local, archive_data_remote)[1]:
            return False

    return True
