import datetime
import logging
import os
from collections import defaultdict

import carb

from .utils import get_test_output_path
from .nvdf import get_app_info, query_nvdf

logger = logging.getLogger(__name__)

FLAKY_TESTS_QUERY_DAYS = 30


class FlakyTestAnalyzer:
    """Basic Flaky Tests Analyzer"""

    AGG_TEST_IDS = "ids"
    AGG_LAST_EXT_CONFIG = "config"
    BUCKET_PASSED = "passed"
    BUCKET_FAILED = "failed"

    tests_failed = set()
    ext_failed = defaultdict(list)

    def __init__(
        self, ext_test_id: str = "*", query_days=FLAKY_TESTS_QUERY_DAYS, exclude_consecutive_failure: bool = True
    ):
        self.ext_test_id = ext_test_id
        self.query_days = query_days
        self.exclude_consecutive_failure = exclude_consecutive_failure
        self.app_info = get_app_info()
        self.query_result = self._query_nvdf()

    def should_skip_test(self) -> bool:
        if not self.query_result:
            carb.log_info(f"{self.ext_test_id} query error - skipping test")
            return True
        if len(self.tests_failed) == 0:
            carb.log_info(f"{self.ext_test_id} has no failed tests in last {self.query_days} days - skipping test")
            return True
        return False

    def get_flaky_tests(self, ext_id: str) -> list:
        return self.ext_failed.get(ext_id, [])

    def generate_playlist(self) -> str:
        test_output_path = get_test_output_path()
        os.makedirs(test_output_path, exist_ok=True)

        filename = "flakytest_" + self.ext_test_id.replace(".", "_").replace(":", "-")
        filepath = os.path.join(test_output_path, f"{filename}_playlist.log")
        if self._write_playlist(filepath):
            return filepath

    def _write_playlist(self, filepath: str) -> bool:
        try:
            with open(filepath, "w") as f:
                f.write("\n".join(self.tests_failed))
            return True
        except IOError as e:
            carb.log_warn(f"Error writing to {filepath} -> {e}")
        return False

    def _query_nvdf(self) -> bool:
        query = self._es_query(days=self.query_days, hours=0)
        r = query_nvdf(query)

        for aggs in r.get("aggregations", {}).get(self.AGG_TEST_IDS, {}).get("buckets", {}):
            test_id = aggs.get("key")
            test_config = aggs.get("config", {}).get("hits", {}).get("hits")
            if not test_config or not test_config[0]:
                continue
            test_config = test_config[0]
            ext_test_id = test_config.get("fields", {}).get("test.s_ext_test_id")
            if not ext_test_id or not ext_test_id[0]:
                continue
            ext_test_id = ext_test_id[0]
            passed = aggs.get(self.BUCKET_PASSED, {}).get("doc_count", 0)
            failed = aggs.get(self.BUCKET_FAILED, {}).get("doc_count", 0)
            ratio = 0
            if passed != 0 and failed != 0:
                ratio = failed / (passed + failed)
            carb.log_info(
                f"{test_id} passed: {passed} failed: {failed} ({ratio * 100:.2f}% fail rate) in last {self.query_days} days"
            )
            if failed == 0:
                continue
            self.ext_failed[ext_test_id].append(
                {"test_id": test_id, "passed": passed, "failed": failed, "ratio": ratio}
            )
            self.tests_failed.add(test_id)

        return True

    def _es_query(self, days: int, hours: int) -> dict:
        target_date = datetime.datetime.utcnow() - datetime.timedelta(days=days, hours=hours)

        kit_version = self.app_info["kit_version"]
        carb.log_info(f"NVDF query for {self.ext_test_id} on Kit {kit_version}, last {days} days")

        query = {
            "aggs": {
                self.AGG_TEST_IDS: {
                    "terms": {"field": "test.s_test_id", "order": {self.BUCKET_FAILED: "desc"}, "size": 1000},
                    "aggs": {
                        self.AGG_LAST_EXT_CONFIG: {
                            "top_hits": {
                                "fields": [{"field": "test.s_ext_test_id"}],
                                "_source": False,
                                "size": 1,
                                "sort": [{"ts_created": {"order": "desc"}}],
                            }
                        },
                        self.BUCKET_PASSED: {
                            "filter": {
                                "bool": {
                                    "filter": [{"term": {"test.b_passed": True}}],
                                }
                            }
                        },
                        self.BUCKET_FAILED: {
                            "filter": {
                                "bool": {
                                    "filter": [{"term": {"test.b_passed": False}}],
                                }
                            }
                        },
                    },
                }
            },
            "size": 0,
            "query": {
                "bool": {
                    # filter out consecutive failure
                    # not (test.b_consecutive_failure : * and test.b_consecutive_failure : true)
                    "must_not": {
                        "bool": {
                            "filter": [
                                {
                                    "bool": {
                                        "should": [{"exists": {"field": "test.b_consecutive_failure"}}],
                                        "minimum_should_match": 1,
                                    }
                                },
                                {
                                    "bool": {
                                        "should": [
                                            {"term": {"test.b_consecutive_failure": self.exclude_consecutive_failure}}
                                        ],
                                        "minimum_should_match": 1,
                                    }
                                },
                            ]
                        }
                    },
                    "filter": [
                        {"term": {"test.s_ext_test_id": self.ext_test_id}},
                        {"term": {"test.s_test_type": "unittest"}},
                        {"term": {"test.b_skipped": False}},
                        {"term": {"test.b_unreliable": False}},
                        {"term": {"test.b_parallel_run": False}},  # Exclude parallel_run results
                        {"term": {"app.s_kit_version": kit_version}},
                        {"term": {"app.l_merge_request": 0}},  # Should we enable flaky tests from MR? For now excluded.
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
