#!/bin/bash
set -e
SCRIPT_DIR="$(dirname "${BASH_SOURCE}")"
# We want to allow specifying of multiple args in one env var; to correctly handle spaces, the args can be quoted, ie,
# in teamcity, we might set the param
#    env.OMNI_TEST_RUNNER_KIT_ARGS=foo "1 2 3" bar
# ...which we would want to evaluate to three args, ["foo", "1 2 3", "bar"]
# However, it's hard in bash to split a string, respecting quotes, in as a safe way.  Best solution I could find
# was:
#   - use xargs to do string parsing
#   - store in a bash array variable
#   - print the statement to set that variable, with `declare -p`
#   - eval the result of the above (which should be safe)
eval "$(echo "$OMNI_TEST_RUNNER_KIT_ARGS" |  xargs bash -c 'declare -a test_args_array=("$@"); declare -p test_args_array' --)"
source "$SCRIPT_DIR/../repo.sh" test "${test_args_array[@]}" "$@" || exit $?
