import os
from dataclasses import dataclass
from typing import ClassVar
import omni.kit.test
from omni.metropolis.utils.config_file.core import ConfigFileFormat, ConfigFile
from omni.metropolis.utils.config_file.section import Section
from omni.metropolis.utils.config_file.property import Property
from omni.metropolis.utils.unit_test.data import get_test_data_root

test_header = "omni.metropolis.utils.test_config_file"
test_version = "0.0.1"
test_file_path = os.path.join(get_test_data_root(), "test_config.yaml")

@dataclass
class TestSection01(Section):
    name: ClassVar[str] = "test_section_01"
    is_required: ClassVar[bool] = True

    test_int: Property[int] = None

    def __post_init__(self):
        self.test_int = Property(
            value_type=int,
            name="test_int",
            default_value=5,
            verify_funcs=[],
        )

@dataclass
class TestSection02(Section):
    name: ClassVar[str] = "test_section_02"
    is_required: ClassVar[bool] = False

    test_str: Property[int] = None

    def __post_init__(self):
        self.test_str = Property(
            value_type=str,
            name="test_str",
            default_value="my_test_string",
            verify_funcs=[],
        )


class TestConfigFile(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.config_file_format = ConfigFileFormat(
            name = "config file format test",
            required_header = test_header,
            required_version = test_version
        )
        self.config_file_format.register_section([TestSection01, TestSection02])

    async def tearDown(self):
        self.config_file_format = None

    def test_load_config_file(self):
        """
        Test if example config file can be loaded correctly.
        """
        self.assertTrue(self.config_file_format)

        # Test if test config can be loaded
        config_file: ConfigFile = self.config_file_format.load_config_file(test_file_path)
        self.assertTrue(config_file)

        # Test if test sections are loaded
        self.assertTrue(config_file.get_section("test_section_01"))
        self.assertTrue(config_file.get_property("test_section_01", "test_int"))
        self.assertTrue(config_file.get_section("test_section_02"))
        self.assertTrue(config_file.get_property("test_section_02", "test_str"))
