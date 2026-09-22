# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import carb
from omni.asset_validator.core import BaseRuleChecker, ValidationRulesRegistry, add_registry_rule_callback

from .model import ApplicationModel
from .options import OptionGroup, OptionModel, OptionsItemModel, OptionsModel, OptionsWidget

__all__ = ["CategoriesModel", "CategoriesWidget"]


class RuleModel(OptionModel):
    def __init__(self, selected: bool, rule: type[BaseRuleChecker]):
        super().__init__(rule, rule.__name__, rule.GetDescription(), selected=selected)


class CategoryModel(OptionGroup):
    def __init__(self, name: str):
        super().__init__(name)


class CategoriesModel(OptionsModel):
    def __init__(self):
        super().__init__()
        self._subscription = add_registry_rule_callback(self.initialize)

    def initialize(self) -> None:
        hide_categories = carb.settings.get_settings().get("exts/omni.asset_validator.ui/hideDisabledCategories")
        hide_rules = carb.settings.get_settings().get("exts/omni.asset_validator.ui/hideDisabledRules")

        categories = list(ValidationRulesRegistry.categories(enabledOnly=hide_categories))
        # move "Usd:Schema" to the first
        schema_name = "Usd:Schema"
        if schema_name in categories:
            index = categories.index(schema_name)
            categories.pop(index)
            categories.insert(0, schema_name)

        self.clear()
        for category in categories:
            category_model = CategoryModel(category)
            for rule_type in ValidationRulesRegistry.rules(category, enabledOnly=hide_rules):
                category_model.append(RuleModel(False, rule_type))
            self.append(category_model)
        self.reset()

    def reset(self) -> None:
        selected_categories = carb.settings.get_settings().get("exts/omni.asset_validator.ui/selectedCategories")
        all_selected: bool = selected_categories is None or selected_categories == ["*"]
        for category in self:
            selected: bool = all_selected or category.name in selected_categories
            for rule in category:
                rule.selected = selected


class CategoriesWidget(OptionsWidget):
    def __init__(self, model: CategoriesModel | None = None):
        super().__init__(model=OptionsItemModel(model or ApplicationModel.get().categories_model))
