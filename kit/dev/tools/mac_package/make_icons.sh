#!/bin/bash

SCRIPT_DIR="$(dirname "${BASH_SOURCE}")"

echo "Regenerating the icon files from all the .iconset folders."
#find . -name *.iconset -exec iconutil -c icns {} \;

find $SCRIPT_DIR -name *.iconset -print0 |
    while IFS= read -r -d '' line; do
        echo "    processing '$line'..."
        iconutil -c icns "$line"

        if [[ $? == 0 ]]; then
            echo "        done!"
        else
            echo "        failed!"
        fi
    done
