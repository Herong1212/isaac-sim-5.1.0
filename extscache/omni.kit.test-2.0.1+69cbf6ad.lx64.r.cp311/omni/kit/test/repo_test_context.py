import json
import logging
import os

logger = logging.getLogger(__name__)


class RepoTestContext:  # pragma: no cover
    def __init__(self):
        self.context = None

        repo_test_context_file = os.environ.get("REPO_TEST_CONTEXT", None)
        if repo_test_context_file and os.path.exists(repo_test_context_file):
            print("Found repo test context file:", repo_test_context_file)
            with open(repo_test_context_file) as f:
                self.context = json.load(f)
                logger.info("repo test context:", self.context)

    def get(self):
        return self.context
