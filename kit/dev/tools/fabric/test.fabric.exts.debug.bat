@echo off

setlocal
pushd %~dp0\..\..
call repo.bat test -c debug -s etm -- --/exts/omni.kit.etm.runner/include=[omni.graph.nodes]
endlocal
popd