#!/bin/bash
# parse_recording.sh - Invokes nv_parser with the specified binary file

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ $# -eq 0 ]; then
    echo "Error: Please provide an input file"
    echo "Usage: $(basename "$0") <path_to_bin_file>"
    exit 1
fi

# Get the absolute path of the input file
INPUT_FILE="$(realpath "$1")"

# Run the parser
"${SCRIPT_DIR}/nv_parser" "${INPUT_FILE}"

if [ $? -ne 0 ]; then
    echo
    echo "Parsing failed"
    read -p "Press Enter to continue..."
    exit 1
fi

echo
exit 0
