from .._neuraylib import NeurayLib, acquire_interface
import omni.mdl.pymdlsdk as pymdlsdk
from functools import lru_cache
import omni.kit.app

@lru_cache()
def get_neuraylib() -> NeurayLib:
    """Returns cached ``omni.mdl.neuraylib.NeurayLib`` interface"""
    return acquire_interface()

def ensure_running():
    """Make sure that neuray is running and MDL resolution through USD is possible."""

    # acquire neuray instance from OV
    # get API access because it has a lazy initialization
    # attache to python bindings to not create a dangling handle, immediately release
    ov_neuraylib = get_neuraylib()
    ov_neuraylib_handle = ov_neuraylib.getNeurayAPI()
    _ = pymdlsdk.attach_ineuray(ov_neuraylib_handle)
    _ = None

@omni.kit.app.deprecated("use ensure_running instead")
def EnsureRunning():
    ensure_running()