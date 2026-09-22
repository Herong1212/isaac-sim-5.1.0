import os
from functools import lru_cache

# GitLab CI/CD variables :
# https://docs.gitlab.com/ee/ci/variables/predefined_variables.html


@lru_cache()
def is_running_in_gitlab():
    return bool(os.getenv("GITLAB_CI"))


@lru_cache()
def get_gitlab_build_url() -> str:
    return os.getenv("CI_JOB_URL", "")
