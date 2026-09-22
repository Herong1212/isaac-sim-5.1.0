import json

import carb
from functools import lru_cache
from .common import info_exec_time


POST_TIMEOUT = 60 # seconds


@lru_cache()
def import_requests():
    """Import requests only when needed, e.g. when publishing an extensions.

    To avoid polluting the global namespace and startup slowdowns.
    """
    import sys
    import carb.tokens

    path = carb.tokens.get_tokens_interface().resolve("${omni.kit.registry.nucleus}/pip_requests")
    sys.path.append(path)
    import requests

    carb.log_info("Imported requests version: {}".format(requests.__version__))
    return requests


@info_exec_time()
def post_publish_extension_request(url: str, ext_id: str, ext_dict: dict, archive_path: str) -> bool:
    requests = import_requests()
    url += "/registry/publish"
    payload = {"package_id": ext_id, "metadata": json.dumps(ext_dict)}

    carb.log_info(f"Publishing extension {ext_id} to {url}")
    if archive_path:
        with open(archive_path, "rb") as f:
            files = {"archive": f}
            resp = requests.post(url, data=payload, files=files, timeout=POST_TIMEOUT)
    else:
        resp = requests.post(url, data=payload, timeout=POST_TIMEOUT)
    if not resp.ok:
        carb.log_error(f"publish request failed: status code: {resp.status_code}, content: {resp.content}")
    return resp.ok


@info_exec_time()
def post_unpublish_extension_request(url: str, ext_id: str) -> bool:
    requests = import_requests()
    url += "/registry/unpublish"
    payload = {"package_id": ext_id}
    carb.log_info(f"Unpublishing extension {ext_id} to {url}")
    resp = requests.post(url, data=payload, timeout=POST_TIMEOUT)
    if not resp.ok:
        carb.log_error(f"unpublish request failed: status code: {resp.status_code}, content: {resp.content}")
    return resp.ok
