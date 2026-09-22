@echo off

setlocal
pushd %~dp0\..\..
call repo.bat test -c release -s etm -- --/exts/omni.kit.etm.runner/include=[omni.graph.nodes]
endlocal
popd