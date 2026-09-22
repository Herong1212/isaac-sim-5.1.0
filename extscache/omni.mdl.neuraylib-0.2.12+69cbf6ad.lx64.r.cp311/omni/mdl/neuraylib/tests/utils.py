import omni.kit.commands
import omni.kit.test
import omni.usd
import carb.settings
import carb
from pathlib import Path
from omni.kit.test_suite.helpers import wait_stage_loading

EXTENSION_DIR = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
TESTS_DIR = EXTENSION_DIR.joinpath('data', 'tests')
USD_DIR = TESTS_DIR.joinpath('usd')
USDZ_DIR = TESTS_DIR.joinpath('usdz')
MDL_DIR = TESTS_DIR.joinpath('mdl')

def isRendererIray():
    return "iray" == carb.settings.get_settings().get("/exts/omni/mdl/neuraylib/tests/renderer")

def isRendererRtx():
    return "rtx" == carb.settings.get_settings().get("/exts/omni/mdl/neuraylib/tests/renderer")

def get_usd_scene_path(usdSubpath: Path):
    path = USD_DIR.joinpath(usdSubpath)
    return str(path)

def get_usdz_scene_path(usdSubpath: Path):
    path = USDZ_DIR.joinpath(usdSubpath)
    return str(path)

def get_mdl_scene_path(usdSubpath: Path):
    path = MDL_DIR.joinpath(usdSubpath)
    return str(path)

def make_uri_with_scheme(absolute_path_or_uri: str):
    """creates a URI from a given absolute path or normalizes a given URI"""
    url_parts = omni.client.break_url(absolute_path_or_uri)
    uri = omni.client.make_url(
        scheme=(url_parts.scheme if url_parts.scheme else 'file'),
        user=url_parts.user,
        port=url_parts.port,
        host=url_parts.host,
        path=url_parts.path,
        query=url_parts.query,
        fragment=url_parts.fragment,
    )
    return omni.client.normalize_url(uri)


async def openNewStage():
    await omni.usd.get_context().new_stage_async()
    stage = omni.usd.get_context().get_stage()
    stage.SetDefaultPrim(stage.DefinePrim("/World"))
    await wait_stage_loading()

async def closeStage():
    await wait_stage_loading()
    await omni.usd.get_context().close_stage_async()
    await wait_stage_loading()

def log_info(message: str):
    R"""Print log message in both streams to see them while developing tests"""
    carb.log_info(message)
    print(message)
