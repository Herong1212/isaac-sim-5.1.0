import os


def get_test_data_root() -> str:
    from ..extension import ActionAndEventDataGenerationUtils

    return os.path.join(ActionAndEventDataGenerationUtils.get_ext_path(), "test_data")


MINIMAL_STAGE_URL = os.path.join(get_test_data_root(), "minimal.usd")
NAVMESH_AREA_TEST_STAGE_URL = os.path.join(get_test_data_root(), "navmesh_area_test.usd")
CHARACTER_FOLDER_URL = os.path.join(get_test_data_root(), "characters")
ANNOTATED_BOX_URL = os.path.join(get_test_data_root(), "annotated_box.usd")
