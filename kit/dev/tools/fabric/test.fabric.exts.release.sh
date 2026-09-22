#!/bin/bash
set -e # exit on error
cd "$(dirname "$0")"/../../

./repo.sh test -c release -s etm -- --/exts/omni.kit.etm.runner/include=[omni.graph.nodes]
