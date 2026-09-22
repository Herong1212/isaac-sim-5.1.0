# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from omni.asset_validator.core import IssuePredicate, IssuePredicates
from omni.kit.widget.filter import FilterButton
from omni.kit.widget.options_menu import OptionItem, OptionSeparator
from omni.kit.widget.searchfield import SearchField
from omni.ui import AbstractValueModel, HStack, SimpleBoolModel

from .model import ApplicationModel

__all__ = ["FiltersModel", "FilterWidget"]


class TokensModel(AbstractValueModel):
    def __init__(self):
        super().__init__()
        self._tokens = []

    @property
    def tokens(self) -> list[str]:
        return self._tokens

    @tokens.setter
    def tokens(self, tokens: list[str]) -> None:
        if self._tokens != tokens:
            self._tokens = tokens
            self._value_changed()


class FiltersModel:
    def __init__(self):
        # Property filters
        self.root_only_model = SimpleBoolModel(False)
        self.fixes_model = SimpleBoolModel(False)
        # Severity filters
        self.errors_model = SimpleBoolModel(True)
        self.failures_model = SimpleBoolModel(True)
        self.warnings_model = SimpleBoolModel(True)
        self.info_model = SimpleBoolModel(True)
        self.success_model = SimpleBoolModel(False)
        # Tag filters
        self.essential_model = SimpleBoolModel(True)
        self.correctness_model = SimpleBoolModel(True)
        self.limitations_model = SimpleBoolModel(True)
        self.performance_model = SimpleBoolModel(True)
        self.other_tags_model = SimpleBoolModel(True)
        # Search tokens
        self.tokens_model = TokensModel()

    @property
    def root_only(self) -> bool:
        return self.root_only_model.as_bool

    @root_only.setter
    def root_only(self, value) -> None:
        self.root_only_model.as_bool = value

    @property
    def fixes(self) -> bool:
        return self.fixes_model.as_bool

    @fixes.setter
    def fixes(self, value) -> None:
        self.fixes_model.as_bool = value

    @property
    def errors(self) -> bool:
        return self.errors_model.as_bool

    @errors.setter
    def errors(self, value) -> None:
        self.errors_model.as_bool = value

    @property
    def failures(self) -> bool:
        return self.failures_model.as_bool

    @failures.setter
    def failures(self, value) -> None:
        self.failures_model.as_bool = value

    @property
    def warnings(self) -> bool:
        return self.warnings_model.as_bool

    @warnings.setter
    def warnings(self, value) -> None:
        self.warnings_model.as_bool = value

    @property
    def info(self) -> bool:
        return self.info_model.as_bool

    @info.setter
    def info(self, value) -> None:
        self.info_model.as_bool = value

    @property
    def success(self) -> bool:
        return self.success_model.as_bool

    @success.setter
    def success(self, value) -> None:
        self.success_model.as_bool = value

    @property
    def essential(self) -> bool:
        return self.essential_model.as_bool

    @essential.setter
    def essential(self, value) -> None:
        self.essential_model.as_bool = value

    @property
    def correctness(self) -> bool:
        return self.correctness_model.as_bool

    @correctness.setter
    def correctness(self, value) -> None:
        self.correctness_model.as_bool = value

    @property
    def limitations(self) -> bool:
        return self.limitations_model.as_bool

    @limitations.setter
    def limitations(self, value) -> None:
        self.limitations_model.as_bool = value

    @property
    def performance(self) -> bool:
        return self.performance_model.as_bool

    @performance.setter
    def performance(self, value) -> None:
        self.performance_model.as_bool = value

    @property
    def other_tags(self) -> bool:
        return self.other_tags_model.as_bool

    @other_tags.setter
    def other_tags(self, value) -> None:
        self.other_tags_model.as_bool = value

    @property
    def tokens(self) -> list[str]:
        return self.tokens_model.tokens

    @tokens.setter
    def tokens(self, value: list[str]) -> None:
        self.tokens_model.tokens = value

    @property
    def options_models(self) -> list[AbstractValueModel]:
        return [
            self.root_only_model,
            self.fixes_model,
            # Severity
            self.errors_model,
            self.failures_model,
            self.warnings_model,
            self.info_model,
            self.success_model,
            # Tags
            self.essential_model,
            self.correctness_model,
            self.limitations_model,
            self.performance_model,
            self.other_tags_model,
        ]

    @property
    def predicate(self) -> IssuePredicate:
        predicates: list[IssuePredicate] = []
        if self.root_only:
            predicates.append(IssuePredicates.HasRootLayer())
        if self.fixes:
            predicates.append(IssuePredicates.HasFix())

        if self.info or self.errors or self.failures or self.warnings or self.success:
            conditions = []
            if self.errors:
                conditions.append(IssuePredicates.IsError())
            if self.failures:
                conditions.append(IssuePredicates.IsFailure())
            if self.warnings:
                conditions.append(IssuePredicates.IsWarning())
            if self.info:
                conditions.append(IssuePredicates.IsInfo())
            if self.success:
                conditions.append(IssuePredicates.IsSuccess())
            predicates.append(IssuePredicates.Or(*conditions))

        if self.essential or self.correctness or self.limitations or self.performance or self.other_tags:
            conditions = []
            if self.essential:
                conditions.append(IssuePredicates.HasTag("essential"))
            if self.correctness:
                conditions.append(IssuePredicates.HasTag("correctness"))
            if self.limitations:
                conditions.append(IssuePredicates.HasTag("limitation"))
            if self.performance:
                conditions.append(IssuePredicates.HasTag("performance"))
            if self.other_tags:
                conditions.append(
                    IssuePredicates.Not(
                        IssuePredicates.Or(
                            IssuePredicates.HasTag("essential"),
                            IssuePredicates.HasTag("correctness"),
                            IssuePredicates.HasTag("limitation"),
                            IssuePredicates.HasTag("performance"),
                        )
                    )
                )
            predicates.append(IssuePredicates.Or(*conditions))

        if self.tokens:
            conditions = []
            for token in self.tokens:
                conditions.append(IssuePredicates.MatchesToken(token))
            predicates.append(IssuePredicates.Or(*conditions))

        return IssuePredicates.And(*predicates)

    def clear(self) -> None:
        # Reset values
        self.root_only = False
        self.fixes = False
        self.errors = True
        self.failures = True
        self.warnings = True
        self.info = True
        self.essential = True
        self.correctness = True
        self.limitations = True
        self.performance = True
        self.tokens = []


class FilterWidget:

    def __init__(self, model: ApplicationModel | None = None):
        self._model = model or ApplicationModel.get()
        self._report_context_menu = None
        self._subscriptions = [
            option_model.subscribe_value_changed_fn(self._on_predicate_update)
            for option_model in self._model.filters_model.options_models
        ]
        with HStack(height=0):
            SearchField(on_search_fn=self._on_search_fn)
            FilterButton(
                [
                    OptionItem("Show root only issues", model=self._model.filters_model.root_only_model, default=False),
                    OptionItem(
                        "Show only issues with fixes", model=self._model.filters_model.fixes_model, default=False
                    ),
                    OptionSeparator(),
                    OptionItem("Show errors", model=self._model.filters_model.errors_model, default=True),
                    OptionItem("Show failures", model=self._model.filters_model.failures_model, default=True),
                    OptionItem("Show warnings", model=self._model.filters_model.warnings_model, default=True),
                    OptionItem("Show infos", model=self._model.filters_model.info_model, default=True),
                    OptionItem("Show success", model=self._model.filters_model.success_model, default=False),
                    OptionSeparator(),
                    OptionItem("Show tag essential", model=self._model.filters_model.essential_model, default=True),
                    OptionItem("Show tag correctness", model=self._model.filters_model.correctness_model, default=True),
                    OptionItem("Show tag limitations", model=self._model.filters_model.limitations_model, default=True),
                    OptionItem("Show tag performance", model=self._model.filters_model.performance_model, default=True),
                    OptionItem("Show other tags", model=self._model.filters_model.other_tags_model, default=True),
                ]
            )

    def _on_search_fn(self, tokens: list[str] | None):
        if tokens is not None:
            self._model.filters_model.tokens = tokens
            self._model.results.apply_filter(self._model.filters_model.predicate)
        else:
            self._model.filters_model.tokens = []
            self._model.results.apply_filter(self._model.filters_model.predicate)

    def _on_predicate_update(self, _):
        self._model.results.apply_filter(self._model.filters_model.predicate)
