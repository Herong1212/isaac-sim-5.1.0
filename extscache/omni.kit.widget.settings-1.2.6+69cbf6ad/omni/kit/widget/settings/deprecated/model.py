"""
deprecated
"""
import typing # pragma: no cover

import carb # pragma: no cover
import carb.settings # pragma: no cover
import carb.dictionary # pragma: no cover
import carb.events # pragma: no cover
import omni.kit.ui # pragma: no cover
import omni.kit.commands # pragma: no cover
import omni.kit.app # pragma: no cover


class ChangeGroup: # pragma: no cover
    def __init__(self, direct_set=False):
        self.path = None
        self.value = None
        self.info = None
        self.direct_set = direct_set

    def _set_path(self, path):
        if self.path is None:
            self.path = path
        elif self.path != path:
            carb.log_error(f"grouped change with different path: {self.path} != {path}")
            return False
        return True

    def set_array_size(self, path, size, info):
        if self._set_path(path):
            # add resize
            self.value = [None] * size
            self.info = info

    def set_value(self, path, value, index, info):
        if self._set_path(path):
            if isinstance(self.value, list):
                self.value[index] = value
            else:
                self.value = value
            self.info = info

    def apply(self, model):
        prev_value = model._settings.get(self.path)

        new_value = self.value

        if isinstance(new_value, str):
            pass
        elif hasattr(new_value, "__getitem__"):
            new_value = tuple(new_value)

        if isinstance(new_value, str) and isinstance(prev_value, int):
            try:
                new_value = int(new_value)
            except ValueError:
                pass

        if self.info.transient:
            if self.path not in model._prev_values:
                model._prev_values[self.path] = prev_value
            model._settings.set(self.path, new_value)
        else:
            undo_value = model._prev_values.pop(self.path, prev_value)
            if self.direct_set:
                model._settings.set(self.path, new_value)
            else:
                omni.kit.commands.execute("ChangeSetting", path=self.path, value=new_value, prev=undo_value)


class UiModel(omni.kit.ui.Model): # pragma: no cover
    def __init__(self, direct_set=False):
        omni.kit.ui.Model.__init__(self)
        self._subs = {}
        self._prev_values = {}
        self._change_group = None
        self._settings = carb.settings.get_settings()
        self._dictionary = carb.dictionary.get_dictionary()
        self._direct_set = direct_set
        self._change_group_refcount = 0

        self._TYPE_MAPPER = {}
        self._TYPE_MAPPER[carb.dictionary.ItemType.BOOL] = omni.kit.ui.ModelNodeType.BOOL
        self._TYPE_MAPPER[carb.dictionary.ItemType.INT] = omni.kit.ui.ModelNodeType.NUMBER
        self._TYPE_MAPPER[carb.dictionary.ItemType.FLOAT] = omni.kit.ui.ModelNodeType.NUMBER
        self._TYPE_MAPPER[carb.dictionary.ItemType.STRING] = omni.kit.ui.ModelNodeType.STRING
        self._TYPE_MAPPER[carb.dictionary.ItemType.DICTIONARY] = omni.kit.ui.ModelNodeType.OBJECT
        self._TYPE_MAPPER[carb.dictionary.ItemType.COUNT] = omni.kit.ui.ModelNodeType.UNKNOWN

    def _get_sanitized_path(self, path):
        if path is not None and len(path) > 0 and path[0] == "/":
            return path[1:]
        return ""

    def _is_array(item):
        # Hacky way and get_keys() call is slow
        if item is not None and len(item) > 0 and "0" in item.get_keys():
            v = item["0"]
            return isinstance(v, int) or isinstance(v, float) or isinstance(v, bool) or isinstance(v, str)
        return False

    def get_type(self, path, meta):
        settings_dict = self._settings.get_settings_dictionary("")
        path = self._get_sanitized_path(path)
        item = self._dictionary.get_item(settings_dict, path)
        item_type = self._dictionary.get_item_type(item)

        if item_type == carb.dictionary.ItemType.DICTIONARY:
            if UiModel._is_array(item):
                return omni.kit.ui.ModelNodeType.ARRAY

        return self._TYPE_MAPPER[item_type]

    def get_array_size(self, path, meta):
        settings_dict = self._settings.get_settings_dictionary("")
        path = self._get_sanitized_path(path)
        item = self._dictionary.get_item(settings_dict, path)
        item_type = self._dictionary.get_item_type(item)
        if item_type == carb.dictionary.ItemType.DICTIONARY:
            if UiModel._is_array(item):
                return len(item)
        return 0

    def get_value(self, path, meta, index, is_time_sampled, time):
        if not meta:
            value = self._settings.get(path)
            if isinstance(value, str):
                return value
            elif hasattr(value, "__getitem__"):
                return value[index]
            else:
                return value
        else:
            if meta == omni.kit.ui.MODEL_META_WIDGET_TYPE:
                return self._get_widget_type_for_setting(path, index)
            if meta == omni.kit.ui.MODEL_META_SERIALIZED_CONTENTS:
                settings_item = self._settings.get(path)
                return "%s" % (settings_item,)

        return None

    def begin_change_group(self):
        if self._change_group_refcount == 0:
            self._change_group = ChangeGroup(direct_set=self._direct_set)
        self._change_group_refcount += 1

    def end_change_group(self):
        if self._change_group:
            self._change_group_refcount -= 1
            if self._change_group_refcount != 0:
                return

            self._change_group.apply(self)
            self._change_group = None

    def set_array_size(self, path, meta, size, is_time_sampled, time, info):
        change = self._change_group if self._change_group else ChangeGroup(direct_set=self._direct_set)
        change.set_array_size(path, size, info)
        if not self._change_group:
            change.apply(self)

    def set_value(self, path, meta, value, index, is_time_sampled, time, info):
        change = self._change_group if self._change_group else ChangeGroup(direct_set=self._direct_set)
        change.set_value(path, value, index, info)
        if not self._change_group:
            change.apply(self)

    def on_subscribe_to_change(self, path, meta, stream):
        if path in self._subs:
            return

        def on_change(item, event_type, path=path):
            self.signal_change(path)

        self._subs[path] = omni.kit.app.SettingChangeSubscription(path, on_change)

    def on_unsubscribe_to_change(self, path, meta, stream):
        if path in self._subs:
            del self._subs[path]

    def get_key_count(self, path, meta):
        settings_dict = self._settings.get_settings_dictionary("")
        if len(path) > 0 and path[0] == "/":
            path = path[1:]
        parent_item = self._dictionary.get_item(settings_dict, path)
        return self._dictionary.get_item_child_count(parent_item)

    def get_key(self, path, meta, index):
        settings_dict = self._settings.get_settings_dictionary("")
        if len(path) > 0 and path[0] == "/":
            path = path[1:]
        parent_item = self._dictionary.get_item(settings_dict, path)
        key_item = self._dictionary.get_item_child_by_index(parent_item, index)
        return self._dictionary.get_item_name(key_item)

    def _get_widget_type_for_setting(self, path, index):
        settings_dict = self._settings.get_settings_dictionary("")
        path = self._get_sanitized_path(path)
        item = self._dictionary.get_item(settings_dict, path)
        if UiModel._is_array(item):
            size = len(item)
            value = item["0"]
            if size == 2 and isinstance(value, int):
                return "DragInt2"
            elif size == 2 and isinstance(value, float):
                return "DragDouble2"
            elif size == 3 and isinstance(value, float):
                return "DragDouble3"
            elif size == 4 and isinstance(value, float):
                return "DragDouble4"
            elif size == 16 and isinstance(value, float):
                return "Transform"
        return ""


def get_ui_model() -> UiModel: # pragma: no cover
    """Returns :class:`UiModel` singleton"""

    if not hasattr(get_ui_model, "model"):
        get_ui_model.model = UiModel(direct_set=False)
    return get_ui_model.model
