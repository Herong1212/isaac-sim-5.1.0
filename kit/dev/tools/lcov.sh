#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$(realpath "$(dirname "${BASH_SOURCE}")")"

rm -rf _lcov
mkdir _lcov

mode=${1-}
if [[ ! $mode || ! ( $mode == "--capture" || $mode == "--zerocounters" ) ]]; then
    echo "Run lcov.sh with either --capture or --zerocounter argument."
    exit 1
fi


if [[ $mode == "--zerocounters" ]]; then
    echo "Clearing coverage results. Run code again before calling lcov again!"
    "$SCRIPT_DIR/../_build/host-deps/linbuild/linbuild.sh" \
        --with-volume="$(pwd)/../../.." \
        -- /usr/bin/bash -c 'lcov --directory . --zerocounters'
    exit 1
fi

if [[ $mode == "--capture" ]]; then
    "$SCRIPT_DIR/../_build/host-deps/linbuild/linbuild.sh" \
        --with-volume="$(pwd)/../../.." \
        -- /usr/bin/bash -c 'lcov --directory . --capture --output-file _lcov/kit.info && genhtml _lcov/kit.info --output-directory=_lcov --prefix=`pwd`'
    exit 1
fi
