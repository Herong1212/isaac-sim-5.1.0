import os
import sys
import time
import pathlib

from functools import lru_cache

_quote = {"'": "|'", "|": "||", "\n": "|n", "\r": "|r", "[": "|[", "]": "|]"}


def escape_value(value):
    return "".join(_quote.get(x, x) for x in value)


@lru_cache()
def is_running_in_teamcity():
    return bool(os.getenv("TEAMCITY_VERSION"))


@lru_cache()
def get_teamcity_build_url() -> str:
    teamcity_url = os.getenv("TEAMCITY_BUILD_URL")
    if teamcity_url and not teamcity_url.startswith("http"):
        teamcity_url = "https://" + teamcity_url
    return teamcity_url or ""


# TeamCity Service messages documentation
# https://www.jetbrains.com/help/teamcity/service-messages.html


def teamcity_publish_artifact(artifact_path: str, stream=sys.stdout):
    if not is_running_in_teamcity():
        return

    tc_message = f"##teamcity[publishArtifacts '{escape_value(artifact_path)}']\n"
    stream.write(tc_message)
    stream.flush()


def teamcity_log_fail(teamCityName, msg, stream=sys.stdout):
    if not is_running_in_teamcity():
        return

    tc_message = f"##teamcity[testFailed name='{teamCityName}' message='{teamCityName} failed. Reason {msg}. Check artifacts for logs']\n"
    stream.write(tc_message)
    stream.flush()


def teamcity_test_retry_support(enabled: bool, stream=sys.stdout):
    """
    With this option enabled, the successful run of a test will mute its previous failure,
    which means that TeamCity will mute a test if it fails and then succeeds within the same build.
    Such tests will not affect the build status.
    """
    if not is_running_in_teamcity():
        return

    retry_support = str(bool(enabled)).lower()
    tc_message = f"##teamcity[testRetrySupport enabled='{retry_support}']\n"
    stream.write(tc_message)
    stream.flush()


def teamcity_show_image(label: str, image_path: str, stream=sys.stdout):
    if not is_running_in_teamcity():
        return

    tc_message = f"##teamcity[testMetadata type='image' name='{label}' value='{image_path}']\n"
    stream.write(tc_message)
    stream.flush()


def teamcity_publish_image_artifact(src_path: str, dest_path: str, inline_image_label: str = None, stream=sys.stdout):
    if not is_running_in_teamcity():
        return

    tc_message = f"##teamcity[publishArtifacts '{src_path} => {dest_path}']\n"
    stream.write(tc_message)
    if inline_image_label:
        result_path = str(pathlib.PurePath(dest_path).joinpath(os.path.basename(src_path)).as_posix())
        teamcity_show_image(inline_image_label, result_path)
    stream.flush()


def teamcity_message(message_name, stream=sys.stdout, **properties):
    if not is_running_in_teamcity():
        return

    current_time = time.time()
    (current_time_int, current_time_fraction) = divmod(current_time, 1)
    current_time_struct = time.localtime(current_time_int)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.", current_time_struct) + "%03d" % (int(current_time_fraction * 1000))
    message = "##teamcity[%s timestamp='%s'" % (message_name, timestamp)

    for k in sorted(properties.keys()):
        value = properties[k]
        if value is None:
            continue
        message += f" {k}='{escape_value(str(value))}'"

    message += "]\n"

    # Python may buffer it for a long time, flushing helps to see real-time result
    stream.write(message)
    stream.flush()


# Based on metadata message for TC:
# https://www.jetbrains.com/help/teamcity/reporting-test-metadata.html#Reporting+Additional+Test+Data
def teamcity_metadata_message(metadata_value, stream=sys.stdout, metadata_name="", metadata_testname=""):
    teamcity_message(
        "testMetadata",
        stream=stream,
        testName=metadata_testname,
        name=metadata_name,
        value=metadata_value,
    )


def teamcity_status(text, status: str = "success", stream=sys.stdout):
    teamcity_message("buildStatus", stream=stream, text=text, status=status)
