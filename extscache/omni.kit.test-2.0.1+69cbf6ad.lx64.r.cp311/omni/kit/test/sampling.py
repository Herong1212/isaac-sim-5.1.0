import datetime
import logging
import random
from statistics import mean

from .nvdf import get_app_info, query_nvdf
from .utils import clamp, get_setting, is_running_on_ci

logger = logging.getLogger(__name__)


class SamplingFactor:
    LOWER_BOUND = 0.0
    UPPER_BOUND = 1.0
    MID_POINT = 0.5


class Sampling:
    """Basic Tests Sampling support"""

    AGG_TEST_IDS = "test_ids"
    AGG_LAST_PASSED = "last_passed"
    LAST_PASSED_COUNT = 3
    TEST_IDS_COUNT = 1000
    DAYS = 4

    def __init__(self, app_info: dict):
        self.tests_sample = []
        self.tests_run_count = []
        self.query_result = False
        self.app_info = app_info

    def run_query(self, extension_name: str, unittests: list, running_on_ci: bool):
        # when running locally skip the nvdf query
        if running_on_ci:
            try:
                self.query_result = self._query_nvdf(extension_name, unittests)
            except Exception as e:
                logger.warning(f"Exception while doing nvdf query: {e}")
        else:
            self.query_result = True

        # populate test list if empty, can happen both locally and on CI
        if self.query_result and not self.tests_sample:
            self.tests_sample = unittests
            self.tests_run_count = [SamplingFactor.MID_POINT] * len(self.tests_sample)

    def get_tests_to_skip(self, sampling_factor: float) -> list:
        if not self.query_result:
            return []

        weights = self._calculate_weights()
        samples_count = len(self.tests_sample)

        # Grab (1.0 - sampling factor) to get the list of tests to skip
        sampling_factor = SamplingFactor.UPPER_BOUND - sampling_factor
        sampling_count = clamp(int(sampling_factor * float(samples_count)), 0, samples_count)

        # use sampling seed if available
        seed = int(get_setting("/exts/omni.kit.test/testExtSamplingSeed", default=-1))
        if seed >= 0:
            random.seed(seed)
        sampled_tests = self._random_choices_no_replace(
            population=self.tests_sample,
            weights=weights,
            k=sampling_count,
        )
        return sampled_tests

    def _query_nvdf(self, extension_name: str, unittests: list) -> bool:  # pragma: no cover
        query = self._es_query(extension_name, days=self.DAYS, hours=0)
        r = query_nvdf(query)

        for aggs in r.get("aggregations", {}).get(self.AGG_TEST_IDS, {}).get("buckets", {}):
            key = aggs.get("key")
            if key not in unittests:
                continue

            hits = aggs.get(self.AGG_LAST_PASSED, {}).get("hits", {}).get("hits", [])
            if not hits:
                continue

            all_failed = False
            for hit in hits:
                passed = hit["_source"]["test"]["b_passed"]
                all_failed = all_failed or not passed

            # consecutive failed tests cannot be skipped
            if all_failed:
                continue

            self.tests_sample.append(key)
            self.tests_run_count.append(aggs.get("doc_count", 0))
        return True

    def _random_choices_no_replace(self, population, weights, k) -> list:
        """Similar to numpy.random.Generator.choice() with replace=False"""
        weights = list(weights)
        positions = range(len(population))
        indices = []
        while True:
            needed = k - len(indices)
            if not needed:
                break
            for i in random.choices(positions, weights, k=needed):
                if weights[i]:
                    weights[i] = SamplingFactor.LOWER_BOUND
                    indices.append(i)
        return [population[i] for i in indices]

    def _calculate_weights(self) -> list:
        """Simple weight adjusting to make sure all tests run an equal amount of times"""
        samples_min = min(self.tests_run_count)
        samples_max = max(self.tests_run_count)
        samples_width = samples_max - samples_min
        samples_mean = mean(self.tests_run_count)

        def _calculate_weight(test_count: int):
            if samples_width == 0:
                return SamplingFactor.MID_POINT
            weight = SamplingFactor.MID_POINT + (samples_mean - float(test_count)) / float(samples_width)
            # clamp is not set to [0.0, 1.0] to have better random distribution
            return clamp(
                weight,
                SamplingFactor.LOWER_BOUND + 0.05,
                SamplingFactor.UPPER_BOUND - 0.05,
            )

        return [_calculate_weight(c) for c in self.tests_run_count]

    def _es_query(self, extension_name: str, days: int, hours: int) -> dict:
        target_date = datetime.datetime.utcnow() - datetime.timedelta(days=days, hours=hours)

        kit_version = self.app_info["kit_version"]
        platform = self.app_info["platform"]
        branch = self.app_info["branch"]
        merge_request = self.app_info["merge_request"]

        query = {
            "aggs": {
                self.AGG_TEST_IDS: {
                    "terms": {"field": "test.s_test_id", "order": {"_count": "desc"}, "size": self.TEST_IDS_COUNT},
                    "aggs": {
                        self.AGG_LAST_PASSED: {
                            "top_hits": {
                                "_source": "test.b_passed",
                                "size": self.LAST_PASSED_COUNT,
                                "sort": [{"ts_created": {"order": "desc"}}],
                            }
                        }
                    },
                }
            },
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {"match_all": {}},
                        {"term": {"test.s_ext_test_id": extension_name}},
                        {"term": {"app.s_kit_version": kit_version}},
                        {"term": {"app.s_platform": platform}},
                        {"term": {"app.s_branch": branch}},
                        {"term": {"app.l_merge_request": merge_request}},
                        {
                            "range": {
                                "ts_created": {
                                    "gte": target_date.isoformat() + "Z",
                                    "format": "strict_date_optional_time",
                                }
                            }
                        },
                    ],
                }
            },
        }
        return query


def get_tests_sampling_to_skip(extension_name: str, sampling_factor: float, unittests: list) -> list:  # pragma: no cover
    """Return a list of tests that can be skipped for a given extension based on a sampling factor
    When using tests sampling we have to run:
      1) all new tests (not found on nvdf)
      2) all failed tests (ie: only consecutive failures, flaky tests are not considered)
      3) sampling tests (sampling factor * number of tests)
    By applying (1 - sampling factor) we get a list of tests to skip, which are garanteed not to contain any test
    from point 1 or 2.
    """
    ts = Sampling(get_app_info())
    ts.run_query(extension_name, unittests, is_running_on_ci())
    return ts.get_tests_to_skip(sampling_factor)
