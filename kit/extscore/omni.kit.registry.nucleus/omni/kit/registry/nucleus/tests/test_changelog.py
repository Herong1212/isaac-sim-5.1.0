

import datetime
import os
import omni.kit.test
import omni.kit.registry.nucleus
from omni.kit.registry.nucleus.utils import changelog_parser
import unittest

class TestChangelogParser(omni.kit.test.AsyncTestCase):

    curr_dir = os.path.split(__file__)[0]
    changelog1_path = os.path.join(curr_dir, "CHANGELOG1.md")

    async def test_version_parse(self):
        res = changelog_parser.parse_version('## [0.1.1] - 2021-03-16')
        self.assertTrue(res==('0.1.1', datetime.date(2021, 3, 16)))

    async def test_changelog_parse(self):
        package_version = "0.1.1"
        found_version = False
        changelog = open(self.changelog1_path).read()
        for version, date, content in changelog_parser.parse_changelog(changelog):
            if version == package_version:
               found_version = True
        self.assertTrue(found_version)
