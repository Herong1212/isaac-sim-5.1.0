# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

from functools import singledispatchmethod

import omni.client
import omni.usd
from omni.asset_validator.core import (
    AssetType,
    Identifier,
    Issue,
    LayerId,
    PrimId,
    PropertyId,
    SchemaBaseId,
    SpecId,
    StageId,
)
from omni.ui import AbstractItem, AbstractItemModel, AbstractValueModel

__all__ = ["FixAtModel", "FixAtItem", "FixAtItemModel"]


class FixAtModel(AbstractValueModel):
    def __init__(self, fix_sites: list[SpecId]):
        super().__init__()
        self._selected = 0
        self._fix_sites = fix_sites

    def set_value(self, value: int) -> None:
        self._selected = value
        self._value_changed()

    def get_value_as_int(self) -> int:
        return self._selected

    @property
    def fix_site(self) -> SpecId | None:
        if not self._fix_sites:
            return None
        fix_site: SpecId = self._fix_sites[self._selected]
        if fix_site.path.IsAbsoluteRootPath():
            return None
        return fix_site


class FixAtItem(AbstractItem):
    """Every option in ComboBox."""

    def __init__(self, issue: Issue, spec_id: SpecId):
        super().__init__()
        self.model = omni.ui.SimpleStringModel(self._format(issue, spec_id))

    def _format(self, issue: Issue, spec_id: SpecId) -> str:
        return f"{self._prefix(spec_id)} {self._make_relative(self._path(issue.at), self._path(spec_id))}"

    def _prefix(self, spec_id: SpecId) -> str:
        if spec_id.path.IsPrimPath():
            return f"Prim({spec_id.path}) at"
        elif spec_id.path.IsPropertyPath():
            return f"Property({spec_id.path}) at"
        else:
            return ""

    @singledispatchmethod
    def _path(self, identifier: Identifier) -> str:
        return ""

    @_path.register(LayerId)
    def _path_layer_id(self, identifier: LayerId) -> str:
        return identifier.identifier

    @_path.register(SpecId)
    def _path_spec_id(self, identifier: SpecId) -> str:
        return self._path(identifier.layer_id)

    @_path.register(StageId)
    def _path_stage_id(self, identifier: StageId) -> str:
        return self._path(identifier.root_layer)

    @_path.register(PrimId)
    def _path_prim_id(self, identifier: PrimId) -> str:
        return self._path(identifier.stage_id)

    @_path.register(PropertyId)
    def _path_property_id(self, identifier: PropertyId) -> str:
        return self._path(identifier.prim_id)

    @_path.register(SchemaBaseId)
    def _path_schema_base_id(self, identifier: SchemaBaseId) -> str:
        return self._path(identifier.prim_id)

    def _make_relative(self, base_path: str, path: str) -> str:
        url: omni.client.Url = omni.client.break_url(base_path)
        base_url: str = omni.client.make_url(
            url.scheme, url.user, url.host, url.port, url.path, url.query, url.fragment
        )
        url: omni.client.Url = omni.client.break_url(path)
        path_url: str = omni.client.make_url(
            url.scheme, url.user, url.host, url.port, url.path, url.query, url.fragment
        )
        return f"Layer({omni.client.make_relative_url(base_url, path_url)})"


class FixAtItemModel(AbstractItemModel):
    """
    Model for Nodes UI (ComboBox).
    """

    def __init__(self, model):
        super().__init__()
        self._model = model.as_fix
        self._subscription = self._model.subscribe_value_changed_fn(lambda _: self._item_changed(None))

        self._items = []
        for fix_site in model.issue.all_fix_sites:
            self._items.append(FixAtItem(model.issue, fix_site))

    def get_item_children(self, _):
        return self._items

    def get_item_value_model(self, item, _):
        if item is None:
            return self._model
        return item.model

    @property
    def asset(self) -> AssetType:
        return self._asset

    @property
    def selected(self) -> SpecId | None:
        if not self._items:
            return None
        return self._model.fix_site
