# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import carb
import omni.asset_validator.core
import omni.asset_validator.simready
import omni.kit.test
from pxr import Usd


class MyRuleChecker(omni.asset_validator.core.BaseRuleChecker):
    """
    Check that all prims are meshes for xforms
    """

    def CheckPrim(self, prim) -> None:
        if prim.GetTypeName() not in ("Mesh", "Xform"):
            self._AddFailedCheck(f"Prim <{prim.GetPath()}> has unsupported type '{prim.GetTypeName()}'.")


def _GET_OMNI_CATEGORY_TEST():
    result = {
        "Omni:Basic": 4,
        "Omni:Layout": 2,
        "Omni:Material": 5,
        "Omni:Geometry": 8,
        "Usd:Schema": 5,
        "Usd:Performance": 4,
        "Usd:Physics": 4,
    }
    if Usd.GetVersion() >= (0, 24, 3):
        result["Omni:Basic"] = 5

    if not omni.asset_validator.core.is_omni_skel_upgrade_disabled():
        result["Omni:Skel"] = 1
    return result


class ValidationRulesRegistryTest(omni.kit.test.AsyncTestCase):
    """
    A map of compliance check tests to the number of registered tests. Do not modify.
    """

    DEFAULT_CATEGORY_TEST = {
        "Basic": 7,
        "AtomicAsset": 3,
    }
    """
    A map of Omni categories and the number of registered tests.
    """
    OMNI_CATEGORY_TEST = _GET_OMNI_CATEGORY_TEST()

    OMNI_SIMREADY_TEST = {
        "Omni:SimReady": 11,
    }

    ALL_CATEGORY_TEST = {**DEFAULT_CATEGORY_TEST, **OMNI_CATEGORY_TEST, **OMNI_SIMREADY_TEST}

    def setUp(self) -> None:
        super().setUp()
        self.__enabledCategories = (
            carb.settings.get_settings().get("exts/omni.asset_validator.core/enabledCategories") or []
        )
        self.__disabledCategories = (
            carb.settings.get_settings().get("exts/omni.asset_validator.core/disabledCategories") or []
        )
        self.__enabledRules = carb.settings.get_settings().get("exts/omni.asset_validator.core/enabledRules") or []
        self.__disabledRules = carb.settings.get_settings().get("exts/omni.asset_validator.core/disabledRules") or []

    def tearDown(self) -> None:
        super().tearDown()
        carb.settings.get_settings().set("exts/omni.asset_validator.core/enabledCategories", self.__enabledCategories)
        carb.settings.get_settings().set("exts/omni.asset_validator.core/disabledCategories", self.__disabledCategories)
        carb.settings.get_settings().set("exts/omni.asset_validator.core/enabledRules", self.__enabledRules)
        carb.settings.get_settings().set("exts/omni.asset_validator.core/disabledRules", self.__disabledRules)
        omni.asset_validator.core.ValidationRulesRegistry.deregisterRule(MyRuleChecker)

    def testCategories(self):
        self.assertCountEqual(
            omni.asset_validator.core.ValidationRulesRegistry.categories(), self.ALL_CATEGORY_TEST.keys()
        )
        self.assertCountEqual(
            omni.asset_validator.core.ValidationRulesRegistry.categories(enabledOnly=True),
            ("Basic", *tuple(self.OMNI_CATEGORY_TEST.keys())),
        )

    def testCategorySettings(self):
        self.assertEqual(carb.settings.get_settings().get("exts/omni.asset_validator.core/enabledCategories"), ["*"])
        self.assertEqual(
            carb.settings.get_settings().get("exts/omni.asset_validator.core/disabledCategories"),
            ["AtomicAsset", "Omni:SimReady"],
        )
        self.assertCountEqual(
            omni.asset_validator.core.ValidationRulesRegistry.categories(enabledOnly=True),
            ("Basic", *tuple(self.OMNI_CATEGORY_TEST.keys())),
        )

        # explicitly enabling overrides disabling
        carb.settings.get_settings().set(
            "exts/omni.asset_validator.core/enabledCategories", ["AtomicAsset", "Omni:SimReady"]
        )
        self.assertCountEqual(
            omni.asset_validator.core.ValidationRulesRegistry.categories(enabledOnly=True),
            self.ALL_CATEGORY_TEST.keys(),
        )

        # wildcards can be used to disable, explicit enabling still takes precedence
        carb.settings.get_settings().set("exts/omni.asset_validator.core/disabledCategories", ["*"])
        self.assertEqual(
            omni.asset_validator.core.ValidationRulesRegistry.categories(enabledOnly=True),
            (
                "AtomicAsset",
                "Omni:SimReady",
            ),
        )

    def testRules(self):

        for category, num_rules in self.ALL_CATEGORY_TEST.items():
            rules = omni.asset_validator.core.ValidationRulesRegistry.rules(category)
            self.assertEqual(len(rules), num_rules)
            for rule in rules:
                self.assertTrue(issubclass(rule, omni.asset_validator.core.BaseRuleChecker))
                self.assertNotEqual(rule.GetDescription(), omni.asset_validator.core.BaseRuleChecker.GetDescription())
                self.assertEqual(rule, omni.asset_validator.core.ValidationRulesRegistry.rule(rule.__name__))
                self.assertEqual(category, omni.asset_validator.core.ValidationRulesRegistry.category(rule))

    def testRuleSettings(self):
        self.assertEqual(carb.settings.get_settings().get("exts/omni.asset_validator.core/enabledRules"), ["*"])
        self.assertEqual(carb.settings.get_settings().get("exts/omni.asset_validator.core/disabledRules"), [""])
        for category, num_rules in (
            ("Basic", 7),
            ("AtomicAsset", 0),  # note 3 are registered
            ("SimReady", 0),  # note 1 are registered
            *self.OMNI_CATEGORY_TEST.items(),
        ):
            self.assertEqual(
                len(omni.asset_validator.core.ValidationRulesRegistry.rules(category, enabledOnly=True)), num_rules
            )

        # wildcards can be used to disable rules
        carb.settings.get_settings().set("exts/omni.asset_validator.core/disabledRules", ["*Texture*", "*Encap*"])
        for category, num_rules in (
            ("Basic", 4),  # note 7 are registered
            ("AtomicAsset", 0),  # note 3 are registered
            ("SimReady", 0),  # note 1 are registered
            *self.OMNI_CATEGORY_TEST.items(),
        ):
            self.assertEqual(
                len(omni.asset_validator.core.ValidationRulesRegistry.rules(category, enabledOnly=True)), num_rules
            )

        # explicitly enabling rules overrides disabling
        carb.settings.get_settings().set(
            "exts/omni.asset_validator.core/enabledRules", ["NormalMapTextureChecker", "PrimEncapsulationChecker"]
        )
        for category, num_rules in (
            ("Basic", 6),  # note 7 are registered
            ("AtomicAsset", 0),  # note 3 are registered
            ("SimReady", 0),  # note 1 are registered
            *self.OMNI_CATEGORY_TEST.items(),
        ):
            self.assertEqual(
                len(omni.asset_validator.core.ValidationRulesRegistry.rules(category, enabledOnly=True)), num_rules
            )

        # explicitly enabling rules in a disabled category has no effect
        carb.settings.get_settings().set("exts/omni.asset_validator.core/enabledRules", ["AnchoredAssetPathsChecker"])
        self.assertEqual(
            len(omni.asset_validator.core.ValidationRulesRegistry.rules("AtomicAsset", enabledOnly=True)), 0
        )

    def testCustomRuleRegistration(self):
        omni.asset_validator.core.ValidationRulesRegistry.registerRule(MyRuleChecker, "MyOwnRules")
        self.assertTrue("MyOwnRules" in omni.asset_validator.core.ValidationRulesRegistry.categories())
        # category is created
        self.assertTrue(MyRuleChecker in omni.asset_validator.core.ValidationRulesRegistry.rules("MyOwnRules"))
        # does not affect other categories
        self.assertFalse(MyRuleChecker in omni.asset_validator.core.ValidationRulesRegistry.rules("Basic"))
        self.assertFalse(MyRuleChecker in omni.asset_validator.core.ValidationRulesRegistry.rules("AtomicAsset"))
        self.assertFalse(MyRuleChecker in omni.asset_validator.core.ValidationRulesRegistry.rules("Omni:Layout"))
        self.assertFalse(MyRuleChecker in omni.asset_validator.core.ValidationRulesRegistry.rules("Usd:Schema"))

        omni.asset_validator.core.ValidationRulesRegistry.deregisterRule(MyRuleChecker)
        # category is cleaned up if all rules are deregistered
        self.assertFalse("MyOwnRules" in omni.asset_validator.core.ValidationRulesRegistry.categories())
        for category in omni.asset_validator.core.ValidationRulesRegistry.categories():
            self.assertFalse(MyRuleChecker in omni.asset_validator.core.ValidationRulesRegistry.rules(category))

        # can add to existing categories
        omni.asset_validator.core.ValidationRulesRegistry.registerRule(MyRuleChecker, "Basic")
        self.assertFalse("MyOwnRules" in omni.asset_validator.core.ValidationRulesRegistry.categories())
        self.assertTrue(MyRuleChecker in omni.asset_validator.core.ValidationRulesRegistry.rules("Basic"))

        # re-registering also re-categorizes
        omni.asset_validator.core.ValidationRulesRegistry.registerRule(MyRuleChecker, "AtomicAsset")
        self.assertFalse("MyOwnRules" in omni.asset_validator.core.ValidationRulesRegistry.categories())
        self.assertFalse(MyRuleChecker in omni.asset_validator.core.ValidationRulesRegistry.rules("Basic"))
        self.assertTrue(MyRuleChecker in omni.asset_validator.core.ValidationRulesRegistry.rules("AtomicAsset"))

    def testCustomRuleDeregistration(self):
        class DummyRuleChecker(omni.asset_validator.core.BaseRuleChecker):
            """
            Dummy rule to reproduce a crash when calling deregisterRule
            """

        registry = omni.asset_validator.core.ValidationRulesRegistry

        # Deregistering an unregistered rule should not do anything
        registry.deregisterRule(MyRuleChecker)
        self.assertIsNone(registry.rule(MyRuleChecker.__name__))

        # Register two rules in the different categories
        registry.registerRule(MyRuleChecker, "MyOwnRules")
        registry.registerRule(DummyRuleChecker, "MyDummyRules")

        # Deregistering a registered rule should remove it
        registry.deregisterRule(MyRuleChecker)
        self.assertIsNone(registry.rule(MyRuleChecker.__name__))

        # Dummy rule & category should still exist
        self.assertTrue("MyDummyRules" in registry.categories())
        self.assertIsNotNone(registry.rule(DummyRuleChecker.__name__))

        # Restore to initial state by removing DummyRuleChecker,
        # so other tests are not influenced by this.
        registry.deregisterRule(DummyRuleChecker)
        self.assertIsNone(registry.rule(DummyRuleChecker.__name__))
