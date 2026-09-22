import asyncio
from functools import partial

import omni.client
import omni.ui as ui
import omni.usd
from omni.kit.widget.filebrowser import find_thumbnails_for_files_async
from omni.warehouse_creator.styles import get_style
from omni.warehouse_creator.widgets.WarehouseTileCard import WarehouseTileCardWidget
from pxr import Usd


def list_variant_references(prim, vset):
    currentSelection = vset.GetVariantSelection()
    references = {}
    pay = omni.usd.get_composed_references_from_prim(prim)
    if not pay:
        pay = omni.usd.get_composed_payloads_from_prim(prim)
    rel, layer = pay[0]
    absolute = rel.assetPath
    if not omni.client.utils.os.path.isabs(rel.assetPath):
        absolute = omni.client.combine_urls(layer.identifier, rel.assetPath)
    stage = Usd.Stage.Open(absolute)
    layer = stage.GetRootLayer()
    path = stage.GetDefaultPrim().GetPrimPath()

    # with Usd.EditContext(prim.GetStage(), prim.GetStage().GetSessionLayer()):
    for v in vset.GetVariantNames():
        # vset.SetVariantSelection(v)
        path_with_variant = path.AppendVariantSelection(vset.GetName(), v)
        obj_with_variant = layer.GetObjectAtPath(path_with_variant)
        absolute = obj_with_variant.primSpec.payloadList.GetAddedOrExplicitItems()[0].assetPath
        if not omni.client.utils.os.path.isabs(absolute):
            absolute = omni.client.combine_urls(layer.identifier, absolute)
        references[v] = absolute
    return references


class WarehouseVariantGridView:
    def __init__(self, theme: str, parent_prims, variant_set_name, **kwargs):
        self._cards = {}
        self._selections = []
        self._style = get_style()
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        self.size = 90
        self._card_width = self.size
        self._card_height = self.size
        self._scale = 1.0
        self.parent_prims = parent_prims
        self.variant_set_name = variant_set_name
        self._widget = ui.VGrid(
            column_width=self._scale * self._card_width,
            row_height=self._scale * self._card_height,
            width=ui.Fraction(1),
            height=ui.Pixel(self._card_height),
            # mouse_double_clicked_fn=partial(self._on_mouse_double_clicked, None),
            style_type_name_override="GridView.Grid",
            style=self._style,
            auto_resize=True,
        )
        self.build_grid()

    def build_widget(self, item: WarehouseTileCardWidget):
        """Create a widget per item"""
        if not item:
            return
        item.build_widget()

    def _on_mouse_pressed(self, card: WarehouseTileCardWidget, *args):
        if type(card) == float:
            return
        self.clear_selections()
        self.add_selection(card)

        if self._selection_changed_fn:
            self._selection_changed_fn(self.selections[0])
        # print("end mouse pressed")

    @property
    def selections(self) -> [WarehouseTileCardWidget]:
        # print("selections getter")
        return [card.name for card in self._selections]

    @selections.setter
    def selections(self, selections: [WarehouseTileCardWidget]):
        # print("selections setter")
        cards = [self._cards[item] for item in selections if item in self._cards]
        self.clear_selections()
        self.extend_selections(cards)

    @property
    def visible(self) -> bool:
        if self._widget:
            return self._widget.visible
        return False

    @visible.setter
    def visible(self, value):
        if self._cards:
            self._widget.visible = value
            for card in self._cards.values():
                if card:
                    card.selected = False
        else:
            self.build_grid()
        self.clear_selections()

    def build_grid(self):
        self._widget.clear()
        with self._widget:
            self._cards.clear()
            if self.parent_prims:
                vset = self.parent_prims[0].GetVariantSet(self.variant_set_name)
                variants = vset.GetVariantNames()
                selected = set(
                    [p.GetVariantSet(self.variant_set_name).GetVariantSelection() for p in self.parent_prims]
                )
                references = list_variant_references(self.parent_prims[0], vset)
            self._cards = {
                n: WarehouseTileCardWidget(
                    name=n,
                    usd_asset=references[n],
                    size=self.size,
                    selected=n in selected,
                    mouse_pressed_fn=partial(
                        self._on_mouse_pressed,
                    ),
                )
                for n in variants
            }
            self._selections = [c for c in self._cards.values() if c.selected]

    def build_widget(self, item: WarehouseTileCardWidget):
        """Create a widget per item"""
        if not item:
            return
        item.build_widget()

    def clear_selections(self):
        for selection in self._selections:
            selection.selected = False
        self._selections.clear()

    def extend_selections(self, cards: [WarehouseTileCardWidget]):
        for card in cards:
            self.add_selection(card)

    def add_selection(self, card: WarehouseTileCardWidget):
        if card and card not in self._selections:
            card.selected = True
            self._selections.append(card)

    def remove_selection(self, card: WarehouseTileCardWidget):
        if card and card in self._selections:
            card.selected = False
            self._selections.remove(card)
