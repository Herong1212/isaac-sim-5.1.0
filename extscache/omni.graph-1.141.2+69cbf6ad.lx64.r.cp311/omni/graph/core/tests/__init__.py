"""
Imports from the test module are only recommended for use in OmniGraph tests.

To get documentation on this module and methods import this file into a Python interpreter and run dir/help, like this:

.. code-block:: python

    import omni.graph.core.tests as ogts
    dir(ogts)
    help(ogts.load_test_file)
"""

# fmt: off
# isort: off

# Exported interface for testing utilities that are of general use.
# (Others exist but are legacy or specific to one use only and imported directly)
from ._unittest_support import construct_test_class
from ._unittest_support import OmniGraphTestConfiguration
from .omnigraph_test_utils import OmniGraphTestCase
from .omnigraph_test_utils import OmniGraphTestCaseNoClear
from .omnigraph_test_utils import SettingContext
from .omnigraph_test_utils import TestContextManager
from .expected_error import ExpectedError
from .omnigraph_test_utils import create_cone
from .omnigraph_test_utils import create_cube
from .omnigraph_test_utils import create_grid_mesh
from .omnigraph_test_utils import create_input_and_output_grid_meshes
from .omnigraph_test_utils import create_sphere
from .omnigraph_test_utils import DataTypeHelper
from .omnigraph_test_utils import dump_graph
from .omnigraph_test_utils import insert_sublayer
from .omnigraph_test_utils import load_test_file
from .omnigraph_test_utils import test_case_class
from .omnigraph_test_utils import verify_connections
from .omnigraph_test_utils import verify_node_existence
from .omnigraph_test_utils import verify_values
from .validation import validate_abi_interface


scan_for_test_modules = True
"""The presence of this object causes the test runner to automatically scan the directory for unit test cases"""

# ==============================================================================================================
#   _____   ______  _____   _____   ______  _____         _______  ______  _____
#  |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
#  | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
#  | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
#  | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
#  |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/
#

# isort: on
# fmt: on
