import os
import shutil
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import carb.settings
from carb.eventdispatcher import get_eventdispatcher
import coverage
import omni.kit.app

from .teamcity import teamcity_publish_artifact
from .utils import get_global_test_output_path, get_setting

# For Coverage.py to be able to combine data it's required that combined reports have the same prefix in the filenames.
# From https://coverage.readthedocs.io/en/coverage-6.1.2/api_coverage.htm:
# "All coverage data files whose name starts with data_file (from the coverage() constructor) will be read,
# and combined together into the current measurements."
COV_OUTPUT_DATAFILE_PREFIX = "py_cov"
COV_OUTPUT_DATAFILE_EXTENSION = ".pycov"

CURRENT_PATH = Path(__file__).parent
HTML_LOCAL_PATH = CURRENT_PATH.parent.parent.parent.joinpath("html", "coverage")


class _PyCoverageCollectorSettings:
    def __init__(self):
        self.enabled = False
        self.output_dir = ""
        self.filter: Optional[list] = None
        self.omit: Optional[list] = None
        self.include_modules = False
        self.include_dependencies = False
        self.include_test_dependencies = False


@lru_cache()
def _get_coverage_output_dir() -> str:
    return os.path.join(get_global_test_output_path(), "pycov")


@lru_cache()
def _get_coverage_env_var() -> Optional[bool]:
    """Provide env var to globally enable/disable coverage, return true/false or None if not set"""
    env_var = os.getenv("OMNI_KIT_TEST_COVERAGE_ENABLED")
    if env_var:
        return True if env_var.lower() in ["true", "1"] else False
    return None


def _get_coverage_enabled() -> bool:
    """Return true if coverage is enabled, false otherwise"""
    env_var = _get_coverage_env_var()
    if env_var is None:
        return get_setting("/exts/omni.kit.test/pyCoverageEnabled", True)
    return env_var


def read_coverage_collector_settings() -> _PyCoverageCollectorSettings:
    result = _PyCoverageCollectorSettings()
    result.enabled = _get_coverage_enabled()
    result.output_dir = _get_coverage_output_dir()
    result.filter = get_setting("/exts/omni.kit.test/pyCoverageFilter", None)
    result.omit = get_setting("/exts/omni.kit.test/pyCoverageOmit", None)
    result.include_modules = get_setting("/exts/omni.kit.test/pyCoverageIncludeModules", False)
    result.include_dependencies = get_setting("/exts/omni.kit.test/pyCoverageIncludeDependencies", False)
    result.include_test_dependencies = get_setting("/exts/omni.kit.test/pyCoverageIncludeTestDependencies", False)
    return result


class _PyCoverageCollector:
    """Initializes code coverage collections and saves collected data at Python interpreter exit"""

    class PyCoverageSettings:
        def __init__(self):
            self.filter: Optional[list] = None
            self.omit: Optional[list] = None
            self.output_data_path_prefix: Optional[str] = None
            self.output_datafile_suffix: Optional[str] = None

    def __init__(self):
        self._coverage = None

    def _read_collector_settings(self) -> Optional[PyCoverageSettings]:
        """
        Reads coverage settings and returns non None PyCoverageSettings if Python coverage is required
        """
        app_name = str(get_setting("/app/name"))

        collector_settings = read_coverage_collector_settings()
        if not collector_settings.enabled:
            print(f"'{app_name}' has disabled Python coverage in settings")
            return None

        if collector_settings.output_dir is None:
            print(f"Output directory for Python coverage isn't set. Skipping Python coverage for '{app_name}'.")
            return None

        result = self.PyCoverageSettings()
        result.filter = collector_settings.filter
        result.omit = collector_settings.omit

        filename_timestamp = app_name + f"_{datetime.now():%Y-%m-%d_%H-%M-%S-%f}"

        # PyCoverage combines report files that have the same prefix so adding the same prefix to created reports
        result.output_data_path_prefix = os.path.normpath(
            os.path.join(collector_settings.output_dir, COV_OUTPUT_DATAFILE_PREFIX)
        )
        result.output_datafile_suffix = filename_timestamp + COV_OUTPUT_DATAFILE_EXTENSION

        return result

    def startup(self):
        # Reading settings to check if it's needed to start Python coverage
        # It's needed to be done as soon as possible to properly collect data
        self._settings = self._read_collector_settings()

        if self._settings is not None:
            self._coverage = coverage.Coverage(
                source=self._settings.filter,
                omit=self._settings.omit,
                data_file=self._settings.output_data_path_prefix,
                data_suffix=self._settings.output_datafile_suffix,
            )
            self._coverage.config.disable_warnings = [
                "module-not-measured",
                "module-not-imported",
                "no-data-collected",
                "couldnt-parse",
            ]
            self._coverage.start()

            # Register for app shutdown to finalize the coverage.
            # For fast shutdown, shutdown function of ext will not be called.
            # The following subscription will give a chance to collect coverage report.
            if carb.settings.get_settings().get("/app/fastShutdown"):
                self._shutdown_subs = (
                    get_eventdispatcher()
                    .observe_event(
                        event_name=omni.kit.app.GLOBAL_EVENT_POST_QUIT, on_event=self.shutdown, observer_name="omni.kit.test::coverage", order=1000
                    )
                )
            else:
                self._shutdown_subs = None

    def shutdown(self, _=None):
        if self._coverage is not None:
            self._coverage.stop()
            try:
                # Note: trying to save report in non-internal format in the "atexit" handler will result in error
                self._coverage.save()
            except coverage.misc.CoverageException as err:
                print(f"Couldn't save Coverage report in internal format: {err}")

        self._coverage = None
        self._settings = None
        self._shutdown_subs = None


class PyCoverageReporterSettings:
    def __init__(self):
        self.source_dir = ""
        self.output_to_std = False
        self.output_to_json = False
        self.output_to_html = False
        self.combine_previous_data = False


def read_coverage_reporter_settings() -> Optional[PyCoverageReporterSettings]:
    coverage_enabled = _get_coverage_enabled()
    if not coverage_enabled:
        return None

    pyCoverageFormats = [s.lower() for s in get_setting("/exts/omni.kit.test/pyCoverageFormats", ["json"])]

    output_to_std = "stdout" in pyCoverageFormats
    output_to_json = "json" in pyCoverageFormats
    output_to_html = "html" in pyCoverageFormats
    # Check if no Python coverage report required
    if not output_to_std and not output_to_json:
        return None

    source_dir = _get_coverage_output_dir()
    if not os.path.exists(source_dir):
        return None

    result = PyCoverageReporterSettings()
    result.source_dir = source_dir
    result.output_to_std = output_to_std
    result.output_to_json = output_to_json
    result.output_to_html = output_to_html
    result.combine_previous_data = get_setting("/exts/omni.kit.test/pyCoverageCombinedReport", False)
    return result


def _report_single_coverage_result(
    cov,
    src_path: str,
    std_output: bool = True,
    json_output_file: Optional[str] = None,
    title: Optional[str] = None,
    html_output_path: Optional[str] = None,
):
    """
    Creates single report and returns path for created json file (or None if it wasn't created)
    """
    try:
        # Note: parameter 'keep' sets if read files will be removed afterwards
        # setting it to true as they might be used to regenerate overall coverage report
        cov.combine(data_paths=[src_path], keep=True)
        # Note: ignore errors is needed to ignore some of the errors when coverage fails to process
        # .../PythonExtension.cpp::shutdown() or some other file
        if std_output:
            print()
            print("=" * 60)
            title = title if title is not None else "Python coverage report"
            print(title)
            print()
            cov.report(ignore_errors=True)
            print("=" * 60)

        if json_output_file is not None:
            cov.json_report(outfile=json_output_file, ignore_errors=True)

        if html_output_path is not None:
            cov.html_report(directory=html_output_path, ignore_errors=True)

    except coverage.misc.CoverageException as err:
        print(f"Couldn't create coverage report for '{src_path}': {err}")


def _modify_html_report(output_path: str):
    # modify coverage html file to have a larger and clearer filter for extensions
    html = ""
    with open(os.path.join(output_path, "index.html"), "r") as file:
        html = file.read()

    with open(os.path.join(HTML_LOCAL_PATH, "modify.html"), "r") as file:
        # find_replace [0] is the line to find, [1] the line to replace and [2] the line to add
        find_replace = file.read().splitlines()
        html = html.replace(find_replace[0], find_replace[1] + "\n" + find_replace[2])

    with open(os.path.join(output_path, "index.html"), "w") as file:
        file.write(html)

    # overwrite coverage css/js files
    shutil.copyfile(os.path.join(HTML_LOCAL_PATH, "new_style.css"), os.path.join(output_path, "style.css"))
    shutil.copyfile(os.path.join(HTML_LOCAL_PATH, "new_script.js"), os.path.join(output_path, "coverage_html.js"))


class PyCoverageReporterResult:
    def __init__(self):
        self.html_path: Optional[str] = None
        self.json_path: Optional[str] = None


def report_coverage_results(reporter_settings: Optional[PyCoverageReporterSettings] = None) -> PyCoverageReporterResult:
    """
    Processes previously collected coverage data according to settings in the 'reporter_settings'
    """

    result = PyCoverageReporterResult()

    if reporter_settings is None:
        return result

    if (
        not reporter_settings.output_to_std
        and not reporter_settings.output_to_json
        and not reporter_settings.output_to_html
    ):
        print("No output report options selected for the coverage results. No result report generated.")
        return result

    # use global configuration file
    config_file = str(CURRENT_PATH.joinpath(".coveragerc"))

    # A helper file required by coverage for combining already existing reports
    cov_internal_file = os.path.join(reporter_settings.source_dir, COV_OUTPUT_DATAFILE_PREFIX)
    cov = coverage.Coverage(source=None, data_file=cov_internal_file, config_file=config_file)
    cov.config.disable_warnings = ["module-not-measured", "module-not-imported", "no-data-collected", "couldnt-parse"]

    if reporter_settings.combine_previous_data:
        result.json_path = (
            os.path.join(reporter_settings.source_dir, "combined_py_coverage" + COV_OUTPUT_DATAFILE_EXTENSION + ".json")
            if reporter_settings.output_to_json
            else None
        )
        result.html_path = (
            os.path.join(reporter_settings.source_dir, "combined_py_coverage_html")
            if reporter_settings.output_to_html
            else None
        )
        _report_single_coverage_result(
            cov,
            reporter_settings.source_dir,
            reporter_settings.output_to_std,
            result.json_path,
            html_output_path=result.html_path,
        )

        if result.html_path and os.path.exists(result.html_path):
            # slightly modify the html report for our needs
            _modify_html_report(result.html_path)

            # add folder to zip file, while be used on TeamCity
            shutil.make_archive(os.path.join(reporter_settings.source_dir, "coverage"), "zip", result.html_path)

        if result.json_path and not os.path.exists(result.json_path):
            result.json_path = None
    else:
        internal_reports = [
            file for file in os.listdir(reporter_settings.source_dir) if file.endswith(COV_OUTPUT_DATAFILE_EXTENSION)
        ]
        for cur_file in internal_reports:
            cov.erase()

            processed_filename = (
                cur_file[len(COV_OUTPUT_DATAFILE_PREFIX) + 1 :]
                if cur_file.startswith(COV_OUTPUT_DATAFILE_PREFIX)
                else cur_file
            )

            json_path = None
            if reporter_settings.output_to_json:
                json_path = os.path.join(reporter_settings.source_dir, processed_filename + ".json")

            title = None
            if reporter_settings.output_to_std:
                title, _ = os.path.splitext(processed_filename)
                title = f"Python coverage report for '{title}'"
            _report_single_coverage_result(
                cov,
                os.path.join(reporter_settings.source_dir, cur_file),
                reporter_settings.output_to_std,
                json_path,
                title,
            )
    # Cleanup of intermediate data
    cov.erase()

    return result


def generate_coverage_report() -> PyCoverageReporterResult:
    # processing coverage data
    result = PyCoverageReporterResult()
    coverage_collector_settings = read_coverage_collector_settings()

    # automatically enable coverage if we detect a pycov directory present when generating a report
    if os.path.exists(coverage_collector_settings.output_dir) and _get_coverage_env_var() != False:
        carb.settings.get_settings().set("/exts/omni.kit.test/pyCoverageEnabled", True)
        coverage_collector_settings.enabled = True

    if coverage_collector_settings.enabled:
        coverage_reporter_settings = read_coverage_reporter_settings()
        result = report_coverage_results(coverage_reporter_settings)
        teamcity_publish_artifact(os.path.join(coverage_collector_settings.output_dir, "*.zip"))

    return result
