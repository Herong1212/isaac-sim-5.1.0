import omni.kit.test
import omni.client
import omni.kit.app
from ..semver import SemanticVersion


class TestSemanticVersion(omni.kit.test.AsyncTestCase):
    async def test_parse_valid_version(self):
        version_str = "1.2.3-alpha.1+build.123"
        version = SemanticVersion.parse(version_str)
        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.prerelease, "alpha.1")
        self.assertEqual(version.build, "build.123")

    async def test_parse_invalid_version(self):
        with self.assertRaises(ValueError):
            SemanticVersion.parse("invalid.version.string")

    async def test_version_comparison(self):
        v1 = SemanticVersion.parse("1.0.0")
        v2 = SemanticVersion.parse("2.0.0")
        self.assertTrue(v1 < v2)
        self.assertTrue(v1 <= v2)
        self.assertTrue(v2 > v1)
        self.assertTrue(v2 >= v1)
        self.assertTrue(v1 != v2)

    async def test_version_equality(self):
        v1 = SemanticVersion.parse("1.0.0")
        v2 = SemanticVersion.parse("1.0.0")
        self.assertTrue(v1 == v2)
        self.assertFalse(v1 != v2)

    async def test_version_prerelease_comparison(self):
        v1 = SemanticVersion.parse("1.0.0-alpha")
        v2 = SemanticVersion.parse("1.0.0-beta")
        self.assertTrue(v1 < v2)
        self.assertTrue(v2 > v1)

    async def test_version_to_tuple(self):
        version = SemanticVersion.parse("1.2.3-alpha.1+build.123")
        self.assertEqual(version.to_tuple(), (1, 2, 3, "alpha.1", "build.123"))

    async def test_version_str(self):
        version = SemanticVersion.parse("1.2.3-alpha.1+build.123")
        self.assertEqual(str(version), "1.2.3-alpha.1+build.123")