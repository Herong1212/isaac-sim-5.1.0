import omni.usd
import omni.kit.usd.layers
import weakref

from .layer_item import LayerItem
from .layer_icons import LayerIcons

from omni import ui


class LayerLinkDelegate(ui.AbstractItemDelegate):  # pragma: no cover
    def __init__(self, usd_context):
        super().__init__()

        self._usd_context = usd_context
        self._tree_view = None
        self._initialized = False
        self._prim_widget = None
        self._popup_menu = None

    def on_stage_attached(self):
        self._initialized = False

    def destroy(self):
        self._tree_view = None
        self._prim_widget = None
        self._popup_menu = None

    def set_tree_view(self, tree_view: ui.TreeView):
        self._tree_view = weakref.ref(tree_view)

    def set_prim_widget(self, layerlink_widget):
        self._prim_widget = weakref.ref(layerlink_widget)

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        pass

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per item"""
        if isinstance(item, LayerItem):
            if not self._initialized and self._tree_view() and item == model.root_layer_item:
                self._initialized = True
                self._tree_view().set_expanded(item, True, False)

            if column_id == 0:
                value_model = model.get_item_value_model(item, column_id)
                text = value_model.get_value_as_string()

                with ui.HStack(
                    height=32,
                    mouse_double_clicked_fn=lambda x, y, b, _: self._on_mouse_double_clicked(b, item, expanded),
                    mouse_pressed_fn=lambda x, y, b, _: self._on_mouse_pressed(b, item, expanded),
                    accept_drop_fn=lambda url: self._on_accept_drop(item, url),
                    drop_fn=lambda e: self._on_drop(item, e),
                ):
                    ui.Label(
                        text,
                        name="object_name",
                        style_type_name_override="TreeView.Item",
                        tooltip=item.identifier,
                    )

    def build_header(self, column_id):
        pass

    def _on_accept_drop(self, item, url):
        return True

    def _on_drop(self, item, e: ui.WidgetMouseDropEvent):
        if self._prim_widget is None:
            return

        specs = self._prim_widget().get_select_specs()
        if e.mime_data in specs:
            omni.kit.commands.execute(
                "LinkSpecs",
                spec_paths=specs,
                layer_identifiers=item.identifier,
                hierarchy=True,
                usd_context=self._usd_context
            )

    def _on_mouse_double_clicked(self, button, item, expanded):
        links = omni.kit.usd.layers.get_spec_links_for_layers(self._usd_context, item.identifier)
        prim_links = links.get(item.identifier, [])
        if self._prim_widget:
            self._prim_widget().select(prim_links)

    def _on_mouse_pressed(self, button, item, expanded):
        if button == 1 and self._tree_view:
            # If the selection doesn't contain the node we drag, we should clear the selection and select the node.
            if item not in self._tree_view().selection:
                self._tree_view().selection = [item]

            self._build_popup_menu()

    def _get_target_layers(self):
        layers = [selected.identifier for selected in self._tree_view().selection]
        return layers

    def _link_specs(self):
        if self._prim_widget is None:
            return
        specs = self._prim_widget().get_select_specs()
        if len(specs) == 0:
            return

        layers = self._get_target_layers()

        omni.kit.commands.execute(
            "LinkSpecs",
            spec_paths=specs,
            layer_identifiers=layers,
            hierarchy=True,
            usd_context=self._usd_context
        )

    def _unlink_specs(self):
        if self._prim_widget is None:
            return
        specs = self._prim_widget().get_select_specs()
        if len(specs) == 0:
            return

        layers = self._get_target_layers()

        omni.kit.commands.execute(
            "UnlinkSpecs",
            spec_paths=specs,
            layer_identifiers=layers,
            hierarchy=True,
            usd_context=self._usd_context
        )

    def clear_layer_links(self):
        layers = self._get_target_layers()

        omni.kit.commands.execute(
            "UnlinkSpecs",
            spec_paths="/",
            layer_identifiers=layers,
            hierarchy=True,
            usd_context=self._usd_context
        )

    def _build_popup_menu(self):
        self._popup_menu = ui.Menu("Layerlink popup menu", name="this")
        with self._popup_menu:
            ui.MenuItem("link selection specs", triggered_fn=self._link_specs)
            ui.MenuItem("unlink selection specs", triggered_fn=self._unlink_specs)
            ui.MenuItem("clear layer links", triggered_fn=self.clear_layer_links)
        self._popup_menu.show()

                # elif isinstance(target_item, LayerItem):
                # omni.kit.commands.execute(
                #     "LinkSpecsCommand",
                #     usd_context=self._usd_context,
                #     spec_paths=source,
                #     layer_identifiers=target_item.identifier,
                # )


class PrimLinkDelegate(ui.AbstractItemDelegate):  # pragma: no cover
    def __init__(self, usd_context):
        super().__init__()

        self._usd_context = usd_context
        self._tree_view = None
        self._layerlink_widget = None
        self._popup_menu = None

    def destroy(self):
        self._usd_context = None
        self._tree_view = None
        self._layerlink_widget = None
        self._popup_menu = None

    def set_tree_view(self, treeview: ui.TreeView):
        self._tree_view = weakref.ref(treeview)

    def set_layerlink_widget(self, layerlink_widget):
        self._layerlink_widget = weakref.ref(layerlink_widget)

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        if column_id == 2:
            with ui.HStack(width=20 * (level + 1), height=0):
                ui.Spacer()
                if model.can_item_have_children(item):
                    # Draw the +/- icon
                    image_name = "Minus" if expanded else "Plus"
                    ui.Image(
                        LayerIcons().get(image_name), width=10, height=10, style_type_name_override="TreeView.Item"
                    )
                    ui.Spacer(width=5)

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per item"""
        if column_id == 0:
            link_filename = LayerIcons().get("link")
            with ui.VStack(width=16, height=20):
                ui.Spacer()
                link_image = ui.Image(
                    link_filename,
                    width=12,
                    height=12,
                    alignment=ui.Alignment.CENTER,
                    name="object_icon",
                    style_type_name_override="LayerView.Image",
                )
                ui.Spacer()

            link_image.visible = item.linked
            item.set_linked_image(link_image)

        if column_id == 1:
            filename = LayerIcons().get("lock") if item.locked else LayerIcons().get("lock_open")
            image_style = {"": {"image_url": f'{filename}'}}

            with ui.VStack(width=16, height=20):
                ui.Spacer()
                lock_image = ui.Image(
                    width=12,
                    height=12,
                    alignment=ui.Alignment.CENTER,
                    style=image_style,
                    mouse_pressed_fn=lambda x, y, b, _: self._on_lock_pressed(b, item, expanded),
                )
                ui.Spacer()

            lock_image.visible = True
            item.set_locked_image(lock_image)

        if column_id == 2:
            value_model = model.get_item_value_model(item, column_id)
            text = value_model.get_value_as_string()

            with ui.HStack(
                height=20,
                width=100,
                mouse_double_clicked_fn=lambda x, y, b, _: self._on_mouse_double_clicked(b, item, expanded),
                mouse_pressed_fn=lambda x, y, b, _: self._on_mouse_pressed(b, item, expanded),
            ):
                ui.Label(
                    text,
                    name="object_name",
                    style_type_name_override="TreeView.Item",
                )

    def _on_mouse_double_clicked(self, button, item, expanded):
        if button == 0:
            links = omni.kit.usd.layers.get_spec_layer_links(self._usd_context, item.path, True)
            layers = links.get(item.path.pathString, [])
            if self._layerlink_widget:
                self._layerlink_widget().select(layers)

    def _on_lock_pressed(self, button, item, expanded):
        if item.locked:
            omni.kit.commands.execute(
                "UnlockSpecsCommand",
                usd_context=self._usd_context,
                spec_paths=item.path,
            )
        else:
            omni.kit.commands.execute(
                "LockSpecsCommand",
                usd_context=self._usd_context,
                spec_paths=item.path,
            )

    def _get_select_specs(self):
        specs = [item.path.pathString for item in self._tree_view().selection]
        return specs

    def _link_layers(self):
        layers = self._layerlink_widget().get_select_layers()
        if len(layers) == 0:
            return

        specs = self._get_select_specs()

        omni.kit.commands.execute(
            "LinkSpecs",
            spec_paths=specs,
            layer_identifiers=layers,
            hierarchy=True,
            usd_context=self._usd_context
        )

    def _unlink_layers(self):
        layers = self._layerlink_widget().get_select_layers()
        if len(layers) == 0:
            return

        specs = self._get_select_specs()

        omni.kit.commands.execute(
            "UnlinkSpecs",
            spec_paths=specs,
            layer_identifiers=layers,
            hierarchy=True,
            usd_context=self._usd_context
        )

    def clear_specs_links(self):
        specs = self._get_select_specs()

        omni.kit.commands.execute(
            "LinkSpecs",
            spec_paths=specs,
            layer_identifiers=[],
            additive=False,
            hierarchy=True,
            usd_context=self._usd_context
        )

    def _on_mouse_pressed(self, button, item, expanded):
        if button == 1 and self._tree_view:
            # If the selection doesn't contain the node we drag, we should clear the selection and select the node.
            if item not in self._tree_view().selection:
                self._tree_view().selection = [item]

            self._build_popup_menu()

    def _build_popup_menu(self):
        self._popup_menu = ui.Menu("Layerlink popup menu", name="this")
        with self._popup_menu:
            ui.MenuItem("link to selected layers", triggered_fn=self._link_layers)
            ui.MenuItem("unlink from selected layers", triggered_fn=self._unlink_layers)
            ui.MenuItem("clear all", triggered_fn=self.clear_specs_links)
        self._popup_menu.show()
