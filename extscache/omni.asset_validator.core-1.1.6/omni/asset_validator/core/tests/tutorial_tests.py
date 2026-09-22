# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib
import re
from io import StringIO
from unittest import skipIf
from unittest.mock import patch

import omni.asset_validator.core
import omni.kit.test
from pxr import Usd  # noqa: F401


class TutorialTest(omni.kit.test.AsyncTestCase):

    maxDiff = None

    def exec_snippet(self, name: str):
        snippet: str = (
            pathlib.Path(omni.asset_validator.core.__file__)
            .parents[3]
            .joinpath(f"docs/tutorial/snippets/{name}.py")
            .read_text()
        )
        with patch("sys.stdout", new=StringIO()) as output:
            exec(snippet)
            content: str = output.getvalue()
            return re.sub(
                r"=['\"\s](.*\.usda@?)['\"\s]",
                lambda match: match.group(0).replace(match.group(1), "any.usda"),
                content,
            )

    def out_snippet(self, name: str):
        content: str = (
            pathlib.Path(omni.asset_validator.core.__file__)
            .parents[3]
            .joinpath(f"docs/tutorial/snippets/{name}.out")
            .read_text()
        )
        return re.sub(
            r"=['\"\s](.*\.usda@?)['\"\s]",
            lambda match: match.group(0).replace(match.group(1), "any.usda"),
            content,
        )

    def assert_no_output(self, key: str) -> None:
        actual: str = self.exec_snippet(key)
        self.assertFalse(actual)

    def assert_output_equal(self, key: str) -> None:
        actual: str = self.exec_snippet(key)
        expected: str = self.out_snippet(key)
        self.assertEqual(
            actual.lower().strip(),
            expected.lower().strip(),
        )

    def test_simple_validation(self):
        self.assert_output_equal("simple_validation")

    @skipIf(
        omni.asset_validator.core.is_omni_skel_upgrade_disabled(),
        "print_rules does not include OmniSkelUpgradeChecker",
    )
    def test_print_rules(self):
        self.assert_output_equal("print_rules")

    def test_rule_validation(self):
        self.assert_output_equal("rule_validation")

    def test_simple_fix(self):
        self.assert_no_output("simple_fix")

    def test_rule_fixing(self):
        self.assert_no_output("rule_fixing")

    def test_custom_rule_empty(self):
        self.assert_output_equal("custom_rule_empty")

    def test_custom_rule_full(self):
        self.assert_output_equal("custom_rule_full")

    def test_custom_rule_validate(self):
        self.assert_output_equal("custom_rule_validate")

    def test_custom_rule_fix(self):
        self.assert_output_equal("custom_rule_fix")

    def test_custom_rule_register(self):
        try:
            self.assert_output_equal("custom_rule_register")
        finally:
            rule = omni.asset_validator.core.ValidationRulesRegistry.rule("MyRule")
            omni.asset_validator.core.ValidationRulesRegistry.deregisterRule(rule)

    def test_fix_at_all(self):
        self.assert_output_equal("fix_at_all")

    def test_fix_at_site(self):
        self.assert_output_equal("fix_at_site")
