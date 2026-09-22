import re
from pxr import Sdf, Usd
from typing import List
from typing import Optional
import omni.usd
import omni.ui as ui
import omni.kit.usd.layers as layers
from omni.kit.widget.stage import StageModel, StageItem
from ..layer_icons import LayerIcons


class PrimItem(StageItem):  # pragma: no cover
    def __init__(
        self,
        path: Sdf.Path,
        stage: Usd.Stage,
        stage_model: StageModel,
        flat=False,
        root_identifier=None,
        load_payloads=False,
        check_missing_references=False,
    ):
        super().__init__(
            path,
            stage,
            stage_model,
            flat=flat,
            root_identifier=root_identifier,
            load_payloads=load_payloads,
            check_missing_references=check_missing_references,
        )

        usd_context = omni.usd.get_context()
        links = omni.kit.usd.layers.get_spec_layer_links(usd_context, path, False)
        if links:
            self._linked = True
        else:
            self._linked = False
        self._linked_image = None

        self._locked = omni.kit.usd.layers.is_spec_locked(usd_context, path)
        self._locked_image = None

    @property
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, value: bool):
        if value != self._locked:
            self._locked = value
            if self._locked_image:
                filename = LayerIcons().get("lock") if value else LayerIcons().get("lock_open")
                image_style = {"": {"image_url": f'{filename}'} }
                self._locked_image.set_style(image_style)

    @property
    def linked(self):
        return self._linked

    @linked.setter
    def linked(self, value: bool):
        if value != self._linked:
            self._linked = value
            if self._linked_image:
                self._linked_image.visible = value

    def set_linked_image(self, image: ui.Image):
        self._linked_image = image

    def set_locked_image(self, image: ui.Image):
        self._locked_image = image


class PrimModel(StageModel):  # pragma: no cover
    def __init__(self, stage: Usd.Stage):
        super().__init__(stage, flat=None, load_payloads=False, check_missing_references=False)
        # replace the root item with PrimItem
        if self._root:
            self._root = PrimItem(
                Sdf.Path.absoluteRootPath,
                self.stage,
                self,
                False,
                self.stage.GetRootLayer().identifier,
                load_payloads=self.load_payloads,
                check_missing_references=self.check_missing_references,
            )

            self._layers = layers.get_layers()
            self._specs_linking = self._layers.get_specs_linking()
            self._specs_locking = self._layers.get_specs_locking()
            self._layers_event_subscription = self._layers.get_event_stream().create_subscription_to_pop(self._on_layer_events, name="Layers Prim Model")

    def destroy(self):
        self._layers_event_subscription = None
        self._layers = None
        self._specs_linking = None
        self._specs_locking = None
        super().destroy()

    # this copy from StageItem._get_stage_item_from_cache()
    # there two differents from StageItem,
    # if code of StageItem.populate_children_get_stage_item_from_cache() changed, should copy and change this too
    def _get_stage_item_from_cache(self, path: Sdf.Path, create_if_not_existed=False):
        stage_item = super()._get_stage_item_from_cache(path, False)
        if stage_item:
            return stage_item
        elif not create_if_not_existed:
            return None

        # Creates new
        stage_item = super()._get_stage_item_from_cache(path, True)
        if not stage_item:
            return None

        # Replaces it with customized PrimItem
        stage_item = PrimItem(
            path,
            self.stage,
            self,
            self.flat,
            load_payloads=self.load_payloads,
            check_missing_references=self.check_missing_references,
        )

        super()._remove_stage_item_from_cache(path)
        super()._cache_stage_item(stage_item)

        return stage_item

    def find(self, path: Sdf.Path):
        """Return item with the given path"""
        path = Sdf.Path(path)
        if path == Sdf.Path.absoluteRootPath:
            return self.root

        return super()._get_stage_item_from_cache(path)

    def get_item_value_model_count(self, item):
        """Reimplemented from AbstractItemModel"""
        return 3

    def get_item_value_model(self, item, column_id):
        """Reimplemented from AbstractItemModel"""
        if item is None:
            item = self.root

        if not item:
            return None

        if column_id == 2:
            return item.name_model

    def drop_accepted(self, target_item, source):
        return False

    def drop(self, target_item, source):
        return

    def _on_layer_events(self, event):
        payload = layers.get_layer_event_payload(event)
        if not payload:
            return

        if payload.event_type == layers.LayerEventType.SPECS_LINKING_CHANGED:
            for _, spec_paths in payload.layer_spec_paths.items():
                self._on_spec_links_changed(spec_paths)
        elif payload.event_type == layers.LayerEventType.SPECS_LOCKING_CHANGED:
            self._on_spec_locks_changed(payload.identifiers_or_spec_paths)

    def _on_spec_links_changed(self, spec_paths: List[str]):
        for spec_path in spec_paths:
            item = self.find(spec_path)
            if item:
                item.linked = self._specs_linking.is_spec_linked(spec_path)

    def _on_spec_locks_changed(self, spec_paths: List[str]):
        for spec_path in spec_paths:
            item = self.find(spec_path)
            if item:
                item.locked = self._specs_locking.is_spec_locked(spec_path)
