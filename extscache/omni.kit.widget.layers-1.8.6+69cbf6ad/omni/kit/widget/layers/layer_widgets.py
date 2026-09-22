__all__ = [
    "get_type_icon",
    "create_icon_images",
    "build_prim_spec_widget",
    "create_layer_name_widget",
    "build_layer_widget"
    ]
import weakref

from functools import partial
try:
    from omni.kit.widget.live_session_management import stop_or_show_live_session_widget, build_live_session_user_layout
    from omni.kit.widget.live_session_management.reload_widget import build_reload_widget
    have_session_management = True
except ModuleNotFoundError:
    have_session_management = False
from omni import ui
from .prim_spec_item import PrimSpecSpecifier, PrimSpecItem
from .layer_item import LayerItem
from .layer_model import LayerModel
from .layer_icons import LayerIcons
from .context_menu import ContextMenu
from .path_utils import PathUtils
from .layer_settings import LayerSettings


TOOLTIP_STYLE = {
    "color": ui.color("#979797"),
    "Tooltip": {"background_color": 0xEE222222}
}


def get_type_icon(node_type):
    """Convert USD Type to icon file name"""
    icons = LayerIcons()
    if node_type in ["DistantLight", "SphereLight", "RectLight", "DiskLight", "CylinderLight", "DomeLight"]:
        return icons.get(node_type, "Light")
    return icons.get(node_type, "Prim")


def create_icon_images(layout, item: PrimSpecItem):
    specifier = item.specifier
    node_type = item.type_name
    instanceable = item.instanceable

    # Gray out the icon if the filter string is not in the text
    iconname = "object_icon"
    icon_filenames = []
    icon_filenames.append(get_type_icon(node_type))

    icons = LayerIcons()
    if instanceable:
        icon_filenames.append(icons.get("Instance"))
    if specifier == PrimSpecSpecifier.OVER_ONLY:
        icon_filenames.append(icons.get("layer_delta"))
    elif specifier == PrimSpecSpecifier.OVER_WITH_REFERENCE:
        icon_filenames.append(icons.get("Reference"))
        icon_filenames.append(icons.get("layer_delta"))
    elif specifier == PrimSpecSpecifier.DEF_WITH_REFERENCE:
        icon_filenames.append(icons.get("Reference"))
    elif specifier == PrimSpecSpecifier.OVER_WITH_PAYLOAD:
        icon_filenames.append(icons.get("Payload"))
        icon_filenames.append(icons.get("layer_delta"))
    elif specifier == PrimSpecSpecifier.DEF_WITH_PAYLOAD:
        icon_filenames.append(icons.get("Payload"))
    elif specifier == PrimSpecSpecifier.DEF_ONLY and not node_type:
        prim_icon = icons.get("Prim")
        if prim_icon not in icon_filenames:
            icon_filenames.append(icons.get("Prim"))

    if item.locked:
        icon_filenames.append(icons.get("menu_lock"))
    elif item.linked:
        icon_filenames.append(icons.get("link"))

    layout.clear()
    with layout:
        for icon_filename in icon_filenames:
            if (
                icon_filename == icons.get("layer_delta") or
                icon_filename == icons.get("menu_lock") or
                icon_filename == icons.get("link")
            ):
                # TODO: There is a bug of alignment of svg in stack
                # The following is to use spacer to implement RIGHT_BOTTOM align
                with ui.VStack(width=20, height=20):
                    ui.Spacer(width=20, height=8)
                    with ui.HStack(width=20, height=12):
                        ui.Spacer(width=8)
                        ui.Image(
                            icon_filename,
                            width=12,
                            height=12,
                            alignment=ui.Alignment.RIGHT_BOTTOM,
                            name=iconname,
                            style_type_name_override="LayerView.Image",
                        )
            else:
                ui.Image(icon_filename, name=iconname, style_type_name_override="LayerView.Image")


def build_prim_spec_widget(
    context_menu: ContextMenu, model: LayerModel, item: PrimSpecItem, column_id: int, expanded: bool
):
    value_model = model.get_item_value_model(item, column_id)
    if not value_model:
        return

    if column_id == 0:
        with ui.HStack(spacing=4, height=20):
            with ui.VStack(width=0):
                ui.Spacer()
                # Draw all icons on top of each other
                image_layout = ui.ZStack(width=20, height=20)
                create_icon_images(image_layout, item)
                ui.Spacer()

            text = value_model.get_value_as_string()

            weakref_item = weakref.ref(item)
            weakref_menu = weakref.ref(context_menu)
            with ui.HStack():
                name_label = ui.Label(
                    text,
                    width=ui.Fraction(1),
                    name="object_name",
                    style_type_name_override="LayerView.Item",
                )

        def prim_flags_changed(value_model):
            is_muted = item.layer_item.muted_or_parent_muted
            if is_muted:
                name_label.name = "object_name_grey"
            elif item.has_missing_reference:
                name_label.name = "object_name_missing"
                name_label.set_tooltip("Missing references found.")
            else:
                name_label.name = "object_name"
            create_icon_images(image_layout, item)

        prim_flags_changed(value_model)
        value_model.callback_id = value_model.subscribe_value_changed_fn(prim_flags_changed)
    else:
        return


def create_layer_name_widget(model: LayerModel, value_model, item: LayerItem, context_menu: ContextMenu, expanded: bool):
    text = value_model.get_value_as_string()
    layout = ui.HStack(width=ui.Fraction(1))
    with layout:
        with ui.ZStack(width=0, height=0):
            with ui.ZStack(width=0, height=0):
                with ui.VStack(width=0):
                    ui.Spacer()
                    layers_icon = ui.Image(width=20, height=20, name="layers")
                    ui.Spacer()
                with ui.VStack():
                    ui.Spacer(height=4)
                    with ui.HStack():
                        ui.Spacer()
                        lightning_image = ui.Image(width=14, height=14, name="layers_lightning")
                        ui.Spacer()
                    ui.Spacer()

            with ui.VStack(width=0):
                ui.Spacer(height=6)
                with ui.HStack(width=0, height=0):
                    ui.Spacer(width=6)
                    lock_image = ui.Image(width=14, height=14, name="layer_read_only_lock")

        ui.Spacer(width=3)
        with ui.ZStack():
            with ui.VStack():
                ui.Spacer()
                if not model.normal_mode and item.edit_layer_in_auto_authoring_mode:
                    ui.Rectangle(name="edit_layer_with_corner", height=20)
                elif item.is_edit_target:
                    ui.Rectangle(name="edit_target_with_corner", height=20)
                elif item.selected:
                    ui.Rectangle(name="selected", height=20)
                else:
                    ui.Rectangle(name="normal", height=20)
                ui.Spacer()
            with ui.HStack():
                if (
                    (not model.normal_mode and item.edit_layer_in_auto_authoring_mode) or
                    item.is_edit_target
                ):
                    ui.Spacer(width=3)
                label = ui.Label(
                    text,
                    name="object_name",
                    style_type_name_override="LayerView.Item",
                )

            label.set_tooltip(item.identifier)

    return layout, layers_icon, label, lock_image, lightning_image


def _build_live_users_tooltip(live_session, icon_size):
    all_users = live_session.peer_users
    total_users = len(all_users)
    with ui.VStack():
        with ui.HStack(style={"color": ui.color("#757575")}):
            ui.Spacer(width=20)
            ui.Label(f"{total_users} Users Connected", style={"font_size": 12}, width=0)
            ui.Spacer(width=20)
        ui.Spacer(height=0)
        ui.Separator(style={"color": ui.color("#4f4f4f")})
        ui.Spacer(height=4)

        for user in all_users:
            item_title = f"{user.user_name} ({user.from_app})"
            if live_session.owner == user.user_name:
                item_title += " - owner"
            with ui.HStack(identifier=user.user_id):
                build_live_session_user_layout(user, icon_size, "")
                ui.Spacer(width=4)
                ui.Label(item_title, style={"font_size": 14})
            ui.Spacer(height=2)


def build_layer_widget(context_menu: ContextMenu, model: LayerModel, item: LayerItem, column_id: int, expanded: bool):
    global have_session_management
    value_model = model.get_item_value_model(item, column_id)
    if not value_model:
        return

    selected = item.edit_layer_in_auto_authoring_mode or item.is_edit_target
    is_live_path = PathUtils.is_omni_live(item.identifier)
    is_layer_in_live_session = item.is_in_live_session
    is_root_layer_in_live_session = model.root_layer_item.is_in_live_session
    is_in_live_session = is_root_layer_in_live_session or is_layer_in_live_session
    is_omni_objects_enabled_path = PathUtils.is_omni_objects_enabled_path(item.identifier)
    if column_id == 0:
        label_layout, layers_icon, name_label, lock_image, lightning_image = create_layer_name_widget(
            model, value_model, item, context_menu, expanded
        )

        def name_model_changed(model):
            normal_mode = item.model.normal_mode
            if item.is_omni_live_path:
                layers_icon.name = "layers_edit_target"
            elif item.missing:
                layers_icon.name = "layers_missing"
            elif not item.latest:
                layers_icon.name = "layers_outdate"
            elif not normal_mode and item.edit_layer_in_auto_authoring_mode:
                layers_icon.name = "layers_edit_target"
            elif normal_mode and item.is_edit_target:
                layers_icon.name = "layers_edit_target"
            elif not normal_mode and item.has_child_edit_layer:
                layers_icon.name = "layers_has_child_edit_target"
            elif normal_mode and item.has_child_edit_target:
                layers_icon.name = "layers_has_child_edit_target"
            else:
                layers_icon.name = "layers"

            lock_image.visible = not item.editable
            is_muted = item.muted_or_parent_muted
            if item.missing:
                name_label.name = "object_name_missing"
            elif not item.latest:
                name_label.name = "object_name_outdated"
            elif is_muted:
                name_label.name = "object_name_grey"
            elif (item.model.auto_authoring_mode or item.model.spec_linking_mode) and item.edit_layer_in_auto_authoring_mode:
                name_label.name = "edit_target"
            elif item.is_edit_target:
                name_label.name = "edit_target"
            else:
                name_label.name = "object_name"

            text = model.get_value_as_string()
            name_label.text = text
            name_label.set_tooltip(item.identifier)

            if item.is_omni_live_path:
                lightning_image.visible = True
            else:
                lightning_image.visible = False

        name_model_changed(value_model)
        value_model.callback_id = value_model.subscribe_value_changed_fn(name_model_changed)

        def double_clicked(model: LayerModel, item: LayerItem):
            # Double click on base layer will forward it to live session layer.
            if item.is_in_live_session:
                model.set_edit_target(item.live_session_layer, True)
            else:
                muted = item.muted_or_parent_muted
                writable = item.editable
                is_missing_layer = item.missing
                is_edit_target = item.is_edit_target
                if not muted and writable and not is_missing_layer:
                    if model.auto_authoring_mode or model.spec_linking_mode:
                        if not item.edit_layer_in_auto_authoring_mode:
                            model.default_edit_layer = item.identifier
                    elif not is_edit_target:
                        model.set_edit_target(item, True)

        label_layout.set_mouse_double_clicked_fn(lambda *_: double_clicked(model, item))
    elif (
        have_session_management
        and column_id == 1 and not item.missing and not is_live_path and is_omni_objects_enabled_path
        and not item.read_only_on_disk
    ):
        with ui.ZStack(width=0, height=0):
            with ui.VStack(width=0, height=0):
                ui.Spacer(width=20, height=18)
                with ui.HStack(width=0):
                    ui.Spacer(width=14)
                    ui.Image(width=6, height=6, alignment=ui.Alignment.RIGHT_BOTTOM, name="drop_down")
            live_button = ui.ToolButton(value_model, name="live_update", image_width=18, image_height=18)

        def on_button_clicked(x, y, b, m):
            quick = (b == 0)
            if quick:
                menu_widget = stop_or_show_live_session_widget(
                    item.model.usd_context,
                    stop_session_forcely=True,
                    layer_identifier=item.identifier,
                    quick_join="Default"
                )
                item.auto_reload = False
                item.model.refresh()
                return

            menu_widget = stop_or_show_live_session_widget(
                item.model.usd_context, show_join_options=True, layer_identifier=item.identifier
            )

            if not menu_widget:
                return

            # Try to align it with the button.
            button = live_button
            drop_down_x = button.screen_position_x
            drop_down_y = button.screen_position_y
            drop_down_height = button.computed_height
            # FIXME: The width of context menu cannot be got. Using fixed width here.

            menu_widget.show_at(
                drop_down_x - 104,
                drop_down_y + drop_down_height / 2 + 2
            )
        live_button.set_mouse_pressed_fn(on_button_clicked)
    elif (
        column_id == 2 and not item.anonymous and not item.missing and
        not is_live_path and not item.is_live_session_layer
    ):
        dirty_button = ui.ToolButton(value_model, name="dirty", image_width=14, image_height=14)

        def save_model_changed(_):
            if not item.editable:
                dirty_button.enabled = False
                dirty_button.set_tooltip("Read only")
                dirty_button.name = "dirty_readonly"
            elif item.is_live_session_layer or item.dirty:
                if item.is_live_session_layer:
                    if item.selected:
                        dirty_button.name = "merge_down_selected"
                    else:
                        dirty_button.name = "merge_down"
                    dirty_button.checked = item.has_content
                    dirty_button.enabled = item.has_content
                else:
                    if is_in_live_session:
                        dirty_button.set_tooltip("Cannot save Layer in Live Session.")
                    else:
                        dirty_button.set_tooltip("Save Layer")
                    if item.selected:
                        dirty_button.name = "dirty_selected"
                    else:
                        dirty_button.name = "dirty"
                    dirty_button.checked = not is_in_live_session
                    dirty_button.enabled = not is_in_live_session
            else:
                if item.selected:
                    dirty_button.name = "dirty_selected"
                else:
                    dirty_button.name = "dirty"
                dirty_button.checked = False
                dirty_button.enabled = False

        save_model_changed(value_model)
        value_model.callback_id = value_model.subscribe_value_changed_fn(save_model_changed)
    elif column_id == 3 and not item.reserved and not item.missing:
        local_muteness_button = ui.ToolButton(value_model, identifier="local_mute", image_width=14, image_height=14)

        def local_muteness_model_changed(value_model):
            muted = value_model.get_value_as_bool()
            if model.global_muteness_scope or selected:
                local_muteness_button.name = "muteness_disable"
                local_muteness_button.enabled = False
                local_muteness_button.set_tooltip(
                    "Cannot mute authoring layer."
                )
            else:
                local_muteness_button.enabled = True
                local_muteness_button.name = "muteness_enable"
                local_muteness_button.set_tooltip(
                    "Mute layer"
                )
            local_muteness_button.checked = muted

        local_muteness_model_changed(value_model)
        value_model.callback_id = value_model.subscribe_value_changed_fn(local_muteness_model_changed)
    else:
        if item.is_live_session_layer:
            if column_id == 4 or column_id == 5:
                peer_user = value_model.peer_user
                if not peer_user:
                    return

                tooltip = f"{peer_user.user_name} ({peer_user.from_app})"
                with ui.ZStack(identifier=peer_user.user_id, width=0, height=0):
                    build_live_session_user_layout(peer_user, size=18, tooltip=tooltip)
            elif column_id == 6:
                current_live_session = item.current_live_session
                if current_live_session:
                    peer_users = current_live_session.peer_users
                    user_count = len(peer_users)
                    if user_count > 2:
                        with ui.ZStack():
                            ui.Label(value_model.get_value_as_string(), style={"font_size": 16}, aligment=ui.Alignment.V_CENTER)
                            button = ui.InvisibleButton(style=TOOLTIP_STYLE)
                            button.set_tooltip_fn(partial(_build_live_users_tooltip, current_live_session, 18))
        elif column_id == 4 and not item.reserved and not item.missing and not item.from_session_layer:
            global_muteness_button = ui.ToolButton(value_model, identifier="global_mute", image_width=14, image_height=14)

            def global_muteness_model_changed(value_model):
                muted = value_model.get_value_as_bool()
                if not model.global_muteness_scope or selected:
                    global_muteness_button.name = "muteness_disable"
                    global_muteness_button.enabled = False
                    if selected and model.global_muteness_scope:
                        global_muteness_button.set_tooltip(
                            "Cannot mute authoring layer."
                        )
                else:
                    global_muteness_button.enabled = True
                    global_muteness_button.name = "muteness_enable"
                global_muteness_button.checked = muted

                if not selected or not model.global_muteness_scope:
                    global_muteness_button.set_tooltip(
                        "Mute layer and persist the change into root layer"
                    )

            global_muteness_model_changed(value_model)
            value_model.callback_id = value_model.subscribe_value_changed_fn(global_muteness_model_changed)
        elif have_session_management and column_id == 5 and not item.is_omni_live_path and item.is_omni_layer and not item.missing and not item.read_only_on_disk:
            g_auto = LayerSettings().auto_reload_sublayers
            button = build_reload_widget(item.identifier, item.usd_context, item.outdated, item.auto_reload, g_auto)
        elif (
            column_id == 6 and not item.read_only_on_disk and not item.reserved and
            not item.anonymous and not item.missing and not item.from_session_layer
        ):
            button = ui.ToolButton(value_model, identifier="lock", image_width=14, image_height=14)

            def lock_model_changed(value_model):
                button.name = "lock"
                if selected:
                    button.enabled = False
                    button.set_tooltip("Cannot lock authoring target.")
                else:
                    button.set_tooltip(
                        "Layer lock is an extended concept in Kit. It does not change\n"
                        "real file permission but adds a flag inside layer's custom data.\n"
                        "When a layer is locked, you cannot set it as edit target nor edit it.\n"
                    )
                locked = value_model.get_value_as_bool()
                button.checked = locked

            lock_model_changed(value_model)
            value_model.callback_id = value_model.subscribe_value_changed_fn(lock_model_changed)
        else:
            return
