import os
import runpy

if os.name == 'nt':
    os.environ['PXR_USD_WINDOWS_DLL_PATH'] = ' ' # prevent usd from running add_dll_directory twice
    for path in os.getenv('PATH', '').split(os.pathsep):
        if os.path.exists(path) and path != '.':
            os.add_dll_directory(path)

runpy.run_module("sphinx.ext.autosummary.generate", run_name="__main__")
