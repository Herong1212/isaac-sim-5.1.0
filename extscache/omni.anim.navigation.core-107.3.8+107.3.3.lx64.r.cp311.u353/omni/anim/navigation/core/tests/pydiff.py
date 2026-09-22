#!/usr/bin/env python

import argparse
import difflib
import math
import os
import re
import shutil
import sys

# Allowable relative tolerance for comparing floating-point values
# TODO: Consider using a smaller tolerance when floats are clearly double-precision
RELATIVE_TOLERANCE = 1e-6

# Allowable absolute tolerance for comparing floating-point values
ABSOLUTE_TOLERANCE = 1e-12

# Regular expression for a simple floating-point literal
FLOAT_PATTERN = re.compile("([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?)")


def diff_files(file_one, file_two):

    with open(file_one) as fo:
        file_one_contents = fo.readlines()
    with open(file_two) as ft:
        file_two_contents = ft.readlines()

    # We could change a lot of output parameters here, like use html output,
    # limit the number of context lines, etc. Currently showing a single
    # context line because the lines can be very long.
    diff = list(difflib.unified_diff(file_one_contents, file_two_contents, file_one, file_two, n=1))

    match = True
    if diff and is_diff_within_tolerance(diff):
        sys.stdout.write(f"WARNING: In comparing {file_one} versus {file_two}:")
        sys.stdout.write(
            f" Diffs detected but ignored (all corresponding values are within a relative tolerance of {RELATIVE_TOLERANCE})."
        )
        sys.stdout.write(f" This might be due to small floating-point discrepancies across test platforms.\n")
    else:
        for line in diff:
            sys.stdout.write(line)
            match = False

    if match:
        return 0
    else:
        if "HDTEST_UPDATE_BASELINE" in os.environ:
            sys.stdout.write(f"UPDATING BASELINE FILE {file_one} from {file_two}\n")
            shutil.copyfile(file_two, file_one)
    return -1


def is_diff_within_tolerance(diff):
    """
    Attempt to scrape the given unified diff for floating-point literals
    and compare corresponding values based on RELATIVE_TOLERANCE,
    returning False if any comparison fails, True otherwise.
    Please see https://en.wikipedia.org/wiki/Diff#Unified_format
    This is not a perfect solution and hopefully we will replace it
    with a proper USD diff that supports a similar numerical tolerance
    for floating-point comparisons.
    Parameters:
      diff - a list of lines over the unified diff output
    """
    file_one_hunk = []
    file_two_hunk = []

    def is_hunk_within_tolerance():
        len1 = len(file_one_hunk)
        len2 = len(file_two_hunk)

        if len1 != len2:
            # This is more than just a small floating-point discrepancy between platforms!
            return False

        if not len1:
            # Nothing to compare
            return True

        for index in range(len1):
            # Parse floating-point literals
            literals1 = [float(m[0]) for m in re.findall(FLOAT_PATTERN, file_one_hunk[index])]
            literals2 = [float(m[0]) for m in re.findall(FLOAT_PATTERN, file_two_hunk[index])]
            count1 = len(literals1)
            count2 = len(literals2)

            if count1 != count2:
                return False

            if not count1:
                # This is a purely non-numerical diff and therefore must fail the comparison
                sys.stdout.write(f"Purely non-numerical diff(s)\n")
                return False

            for i in range(count1):
                v1 = literals1[i]
                v2 = literals2[i]
                if not math.isclose(v1, v2, rel_tol=RELATIVE_TOLERANCE):
                    if math.isclose(v1, v2, rel_tol=RELATIVE_TOLERANCE, abs_tol=ABSOLUTE_TOLERANCE):
                        sys.stdout.write(f"WARNING: Exceeded relative tolerance {RELATIVE_TOLERANCE}")
                        sys.stdout.write(f" but not absolute tolerance {ABSOLUTE_TOLERANCE}:")
                        sys.stdout.write(f" {v1} versus {v2}\n")
                    else:
                        sys.stdout.write(
                            f"Exceeded both tolerances (rel={RELATIVE_TOLERANCE}, abs={ABSOLUTE_TOLERANCE}):"
                        )
                        sys.stdout.write(f" {v1} versus {v2}\n")
                        return False

            # Compare the remaining non-numerical portions
            remainder1 = re.sub(FLOAT_PATTERN, "", file_one_hunk[index][1:])
            remainder2 = re.sub(FLOAT_PATTERN, "", file_two_hunk[index][1:])
            if remainder1 != remainder2:
                sys.stdout.write(f"Unequal non-numerical portions\n")
                return False

        return True

    for line in diff:
        if line.startswith("---") or line.startswith("+++"):
            # Header line (ignore)
            pass
        elif line.startswith("@@"):
            # Hunk range information
            if not is_hunk_within_tolerance():
                return False
            file_one_hunk = []
            file_two_hunk = []
        elif line.startswith("-"):
            # Deletion line
            file_one_hunk.append(line)
        elif line.startswith("+"):
            # Addition line
            file_two_hunk.append(line)
        else:
            # Contextual line (ignore)
            pass

    return is_hunk_within_tolerance()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_one")
    parser.add_argument("file_two")
    options = parser.parse_args()

    sys.exit(diff_files(options.file_one, options.file_two))
