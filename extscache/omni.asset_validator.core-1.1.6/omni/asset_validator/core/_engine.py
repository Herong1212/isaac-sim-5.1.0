# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

import fnmatch
from collections.abc import Callable
from functools import cache

import carb
import carb.events
import carb.settings
import omni.client
from omni.asset_validator._impl import BaseRuleChecker, CategoryRuleRegistry, ComplianceChecker, RequirementsRegistry
from omni.asset_validator._impl import ValidationEngine as _ValidationEngine

from ._compliance_checker import OmniComplianceChecker

__all__ = [
    "ValidationEngine",
    "ValidationRulesRegistry",
    "registerRule",
]


class ValidationEngine(_ValidationEngine):
    """An engine for running rule-checkers on a given Omniverse Asset.

    Rules are :py:class:`BaseRuleChecker` derived classes which perform specific validation checks over various aspects
    of a USD layer/stage. Rules must be registered with the :py:class:`ValidationRulesRegistry` and subsequently enabled
    on each instance of the :py:class:`ValidationEngine`.

    Validation can be performed asynchronously (using either :py:meth:`validate_async` or :py:meth:`validate_with_callbacks`)
    or blocking (via :py:meth:`validate`).

    Example:
        Construct an engine and validate several assets using the default-enabled rules:

        .. code-block:: python

            import omni.asset_validator.core

            engine = omni.asset_validator.core.ValidationEngine()

            # Validate a single Omniverse file
            print( engine.validate('omniverse://localhost/NVIDIA/Samples/Astronaut/Astronaut.usd') )

            # Search an Omniverse folder and recursively validate all USD files asynchronously
            # note a running asyncio EvenLoop is required
            task = engine.validate_with_callbacks(
                'omniverse://localhost/NVIDIA/Assets/ArchVis/Industrial/Containers/',
                asset_located_fn = lambda url: print(f'Validating "{url}"'),
                asset_validated_fn = lambda result: print(result),
            )
            task.add_done_callback(lambda task: print('validate_with_callbacks complete'))

            # Perform the same search & validate but await the results
            import asyncio
            async def test(url):
                results = await engine.validate_async(url)
                for result in results:
                    print(result)
            asyncio.ensure_future(test('omniverse://localhost/NVIDIA/Assets/ArchVis/Industrial/Containers/'))

            # Load a layer onto a stage and validate it in-memory, including any unsaved edits
            from pxr import Usd, Kind
            stage = Usd.Stage.Open('omniverse://localhost/NVIDIA/Samples/Astronaut/Astronaut.usd')
            prim = stage.DefinePrim(f'{stage.GetDefaultPrim().GetPath()}/MyCube', 'cube')
            Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)
            print( engine.validate(stage) )

            # Validate the current stage in any Kit based app (e.g. Create, View)
            import omni.usd
            print( engine.validate( omni.usd.get_context().get_stage() ) )
    """

    def __init__(self, *, init_rules: bool = True, variants: bool = True, initRules: bool = True) -> None:
        """
        Args:
            init_rules (bool): Whether to init (preload) all rules.
            variants (bool): Whether to process all variants.
            initRules (bool): Deprecated. Whether to init (preload) all rules. Use `init_rules` instead.
        """
        super().__init__(init_rules=init_rules and initRules, variants=variants)

    @property
    def initialized_rules(self) -> list[type[BaseRuleChecker]]:
        """
        Returns:
            A list of rules that have been initialized.
        """
        return [
            rule_type
            for category in ValidationRulesRegistry.categories(enabledOnly=True)
            for rule_type in ValidationRulesRegistry.rules(category, enabledOnly=True)
        ]

    @classmethod
    def _is_uri_found(cls, identifier: str) -> bool:
        status, _ = omni.client.stat(identifier)
        return status == omni.client.Result.OK

    @classmethod
    def _is_uri_prefix(cls, identifier: str) -> bool:
        status, entry = omni.client.stat(identifier)
        if status != omni.client.Result.OK:
            return False
        return entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN

    @classmethod
    def _list_uris(cls, prefix: str) -> list[str]:
        status, entries = omni.client.list(prefix)
        if status != omni.client.Result.OK:
            return []

        b_url = omni.client.break_url(prefix)
        all_assets: list[str] = []
        for entry in entries:
            entry_url = omni.client.make_url(
                b_url.scheme,
                b_url.user,
                b_url.host,
                b_url.port,  # unchanged
                f"{b_url.path}/{entry.relative_path}",
                b_url.query,
                b_url.fragment,  # unchanged
            )
            all_assets.append(entry_url)
        return all_assets

    def _create_compliance_checker(self) -> ComplianceChecker:
        checker = OmniComplianceChecker(
            stats=self.stats,
            skip_variants=not self.variants,
        )
        if self.init_rules:
            for rule_type in set(self.initialized_rules) - set(self.disabled_rules):
                checker.AddRule(rule_type)
        for rule_type in set(self.enabled_rules) - set(self.disabled_rules):
            checker.AddRule(rule_type)
        for requirement in self.enabled_requirements:
            if rule_type := RequirementsRegistry().get_validator(requirement):
                checker.AddRule(rule_type)
        return checker


class ValidationRulesRegistry:
    """A registry enabling external clients to add new rules to the engine.

    Rules **must derive from** :py:class:`BaseRuleChecker` and should re-implement the necessary
    virtual methods required for their specific check, as well as documenting with an
    appropriate user-facing message.

    Rules are registered to specific `categories` (`str` labels) to provide bulk enabling/disabling via carb settings
    and to make logical grouping in UIs or other documentation easier.

    Example:
        Define a new Rule that requires all prims to be meshes or xforms (e.g. if your app only handles these types)
        and register it with the validation framework under a custom category:

        .. code-block:: python

            import omni.asset_validator.core

            @omni.asset_validator.core.registerRule("MyOwnRules")
            class MyRuleChecker(omni.asset_validator.core.BaseRuleChecker):
                '''Check that all prims are meshes for xforms'''

                def CheckPrim(self, prim) -> None:
                    if prim.GetTypeName() not in ("Mesh", "Xform"):
                        self._AddFailedCheck(
                            f"Prim <{prim.GetPath()}> has unsupported type '{prim.GetTypeName()}'."
                        )

    By default all rules that ship with USD itself are registered into "Basic" category. "AtomicAsset"
    rules have been default disabled via carb settings.
    """

    @staticmethod
    @cache
    def init():
        """This is a wrapper over the category rules registry. However, some rules appear under different names due
        to specialization happening in this kit extension package, to avoid these problems we clear the current
        registry."""
        CategoryRuleRegistry().clear()

    @staticmethod
    def categories(enabledOnly: bool = False) -> tuple[str, ...]:
        """Query all registered categories

        Args:
            enabledOnly: Filter the results to only categories that are enabled (via carb settings)

        Returns:
            A tuple of category strings that can be used in :py:meth:`rules`
        """
        if enabledOnly:
            return ValidationRulesRegistry.__enabledCategories()
        return CategoryRuleRegistry().categories

    @staticmethod
    def rules(category: str, enabledOnly: bool = False) -> tuple[type[BaseRuleChecker], ...]:
        """Query all registered rules in a given category

        Args:
            category: Filter for rules only in a specific category
            enabledOnly: Filter the results to only rules that are enabled (via carb settings)

        Returns:
            A tuple of BaseRuleChecker derived classes
        """
        if enabledOnly:
            return ValidationRulesRegistry.__enabledRules(category)
        return CategoryRuleRegistry().get_rules(category)

    @staticmethod
    def registerRule(rule: type[BaseRuleChecker], category: str) -> None:
        """Register a new Rule to a specific category

        Args:
            rule: A BaseRuleChecker derived class that implements a specific check
            category: The label with which this rule will be associated
        """
        CategoryRuleRegistry().add(category, rule)
        event_stream = ValidationRulesRegistry._get_event_stream()
        event_stream.push()
        event_stream.pump()

    @staticmethod
    def deregisterRule(rule: type[BaseRuleChecker]) -> None:
        """Remove a specific Rule from the registry

        For convenience it is not required to specify the category, the rule will be removed from all categories,
        and subsequent empty categories will be removed from the registry.

        Args:
            rule: A BaseRuleChecker derived class that implements a specific check
        """
        CategoryRuleRegistry().remove(rule)
        event_stream = ValidationRulesRegistry._get_event_stream()
        event_stream.push()
        event_stream.pump()

    @staticmethod
    def rule(name: str) -> type[BaseRuleChecker] | None:
        """Query a registered rule by class name

        Args:
            name: The exact (case sensitive) class name of a previously registered rule

        Returns:
            A BaseRuleChecker derived class or None
        """
        return CategoryRuleRegistry().find_rule(name)

    @staticmethod
    def category(rule: type[BaseRuleChecker]) -> str:
        """Query the category of a specific rule

        Args:
            rule: A previously registered BaseRuleChecker derived class

        Returns:
            A valid category name or empty string
        """
        return CategoryRuleRegistry().get_category(rule) or ""

    @staticmethod
    def __enabledCategories() -> tuple[str, ...]:
        enabled_categories = carb.settings.get_settings().get("exts/omni.asset_validator.core/enabledCategories") or [
            "*"
        ]
        disabled_categories = carb.settings.get_settings().get("exts/omni.asset_validator.core/disabledCategories") or [
            "AtomicAsset",
        ]

        categories = []
        for category in CategoryRuleRegistry().categories:
            # skip disabled categories unless they are explicitly enabled (e.g. by a downstream ext/app setting)
            if category in enabled_categories:
                categories.append(category)
                continue

            if not any(fnmatch.fnmatchcase(category, pattern) for pattern in disabled_categories):
                categories.append(category)

        return tuple(categories)

    @staticmethod
    def __enabledRules(category: str) -> tuple[type[BaseRuleChecker], ...]:
        if category not in ValidationRulesRegistry.__enabledCategories():
            return tuple()

        enabled_rules = carb.settings.get_settings().get("exts/omni.asset_validator.core/enabledRules") or ["*"]
        disabled_rules = carb.settings.get_settings().get("exts/omni.asset_validator.core/disabledRules") or [""]

        rules = []
        for rule_type in CategoryRuleRegistry().get_rules(category):
            # skip disabled rules unless they are explicitly enabled (e.g. by a downstream ext/app setting)
            if rule_type.__name__ in enabled_rules:
                rules.append(rule_type)
                continue

            if not any(fnmatch.fnmatchcase(rule_type.__name__, pattern) for pattern in disabled_rules):
                rules.append(rule_type)

        return tuple(rules)

    @staticmethod
    @cache
    def _get_event_stream() -> carb.events.IEventStream:
        events = carb.events.get_events_interface()
        stream = events.create_event_stream()
        return stream

    @staticmethod
    def add_registry_rule_callback(callback: Callable[[], None]):
        """Add a callback to be called when a rule is registered."""
        stream = ValidationRulesRegistry._get_event_stream()
        return stream.create_subscription_to_pop(lambda _: callback())


ValidationRulesRegistry.init()


def registerRule(category: str, skip: bool = False) -> Callable[[type[BaseRuleChecker]], type[BaseRuleChecker]]:
    """Decorator. Register a new :py:class:`BaseRuleChecker` to a specific category.

    Example:

    Register MyRule into the category "MyCategory" so that becomes part of the default initialized ValidationEngine.

    .. code-block:: python

        @registerRule("MyCategory")
        class MyRule(BaseRuleChecker):
            pass

    Args:
        category (str): The label with which this rule will be associated
        skip (bool): Whether to skip rule registration. Default false.
    """

    def _registerRule(rule_class: type[BaseRuleChecker]) -> type[BaseRuleChecker]:
        """
        Take the rule class and register under specific category.
        Return the rule class un altered.
        """
        if not skip:
            ValidationRulesRegistry.registerRule(rule_class, category)
        return rule_class

    return _registerRule


def add_registry_rule_callback(callback: Callable[[], None]):
    """
    Add a callback to be called when a rule is registered or deregistered.
    It returns a subscription object that can be used to unsubscribe.

    Example:

    .. code-block:: python

        subscription = add_registry_rule_callback(lambda: print("Rule registered"))

        @registerRule("MyCategory")
        class MyRule(BaseRuleChecker):
            pass

        # Output:
        # Rule registered
    """
    return ValidationRulesRegistry.add_registry_rule_callback(callback)
