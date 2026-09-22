#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$(realpath "$(dirname "${BASH_SOURCE}")")"

err=""
git_root=$(git rev-parse --show-toplevel) || err=$?
if [[ ! -z $err ]]; then
    >&2 echo "cannot find the root of the git repo"
    >&2 echo "unable to find the directory to run gcov from"
    >&2 echo "was this script run from outside the kit repo?"
    exit $err
fi

pushd "$git_root" >/dev/null 2>&1
if [[ ! -d "./kit/_build/intermediate/linux-x86_64" ]]; then
    >&2 echo "the 'kit/_build/intermediate/linux-x86_64/' directory was not found"
    >&2 echo "a full build needs to be performed before this tool is run"
    popd >/dev/null 2>&1
    exit 1
fi

# gcov needs to be run from the directory where the build took place
pushd kit/_build/intermediate/linux-x86_64/ >/dev/null 2>&1

# the output directory
mkdir -p gcov

readarray -t directories < <(find . -maxdepth 1 -type d)
for d in "${directories[@]}"; do
    if [[ "$d" == '.' ]] || [[ "$d" == ".." ]]; then
        continue
    fi
    echo "$d"
    out_dir="gcov/$d/"
    mkdir -p "$out_dir"
    "$SCRIPT_DIR/../_build/host-deps/linbuild/linbuild.sh" \
        --with-volume="$(pwd)/../../.." \
        -- gcov "$d"/x86_64/debug/*.gcno
    mv ./*.gcov "$out_dir" >/dev/null 2>&1 || true
    rm -d "$out_dir" >/dev/null 2>&1 || true # delete it if it's empty
done

# archive the coverage files
tar cvJf ../../../coverage.tar.xz ./gcov

# delete the temporary directory
rm -rf ./gcov

popd >/dev/null 2>&1
popd >/dev/null 2>&1

echo "the output files are in coverage.tar.xz in the root of the kit tree"
echo "if you have built without --coverage or you have not run the debug unit"
echo "tests yet, the archive will only contain an empty directory"
echo "only the files that have had code executed will show up in the output"

