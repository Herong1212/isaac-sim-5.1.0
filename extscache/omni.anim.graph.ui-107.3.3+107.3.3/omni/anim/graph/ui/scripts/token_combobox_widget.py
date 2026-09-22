import omni.ui as ui
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from typing import List, Tuple, Union
from pxr import Sdf

class TokenItemModel(ui.AbstractItemModel):
    """Model for handling the token drop down menu"""

    class AllowedTokenItem(ui.AbstractItem):
        def __init__(self, item):
            super().__init__()
            self.token = item
            self.model = ui.SimpleStringModel(item)

    def __init__(
        self, model: ui.AbstractItemModel, allowed_tokens: Union[List[str], List[Tuple[str, str]]]
    ):
        ui.AbstractItemModel.__init__(self)
        self._model = model

        # if it's a list of strings, the tokens are used as is.
        if isinstance(allowed_tokens[0], str):
            self._allowed_tokens = [TokenItemModel.AllowedTokenItem(token) for token in allowed_tokens]
            self._actual_tokens = list(allowed_tokens)
        # if it's a list of tuples, the first item is the displayed value, the second is the actual value
        elif isinstance(allowed_tokens[1], tuple):
            self._allowed_tokens = [TokenItemModel.AllowedTokenItem(token[0]) for token in allowed_tokens]
            self._actual_tokens = [token[1] for token in allowed_tokens]
        else:
            raise TypeError("allowed_tokens must be a list of strings or list of string pairs")

        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(self._current_index_changed)
        current = self._get_value_from_model()

        # set the current item
        if self._is_actual_token(current):
            self._current_index.set_value(self._get_item_index(current))
        else:
            self._allowed_tokens.insert(0, TokenItemModel.AllowedTokenItem(current))
            self._actual_tokens.insert(0, current)
            self._current_index.set_value(0)

    def get_item_children(self, item):
        return self._allowed_tokens

    def _current_index_changed(self, model):
        """Called when the current selection is changed"""
        self._update_value()

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._current_index
        return item.model

    def get_value_as_token(self):
        index = self._current_index.as_int
        return self._allowed_tokens[index].token

    def is_allowed_token(self, token):
        """Checks if a display token is valid"""
        return token in [allowed.token for allowed in self._allowed_tokens]

    def _is_actual_token(self, token):
        """Checks if an actual token is listed"""
        return token in self._actual_tokens

    def _get_value_from_model(self):
        """Gets the current value of the model"""
        # The model returns the tokens as list
        return self._model.get_value_as_string()

    def _get_item_index(self, item: str):
        """Get the index of the actual token"""
        return self._actual_tokens.index(item)

    def _update_value(self):
        new_value = self._actual_tokens[self._current_index.as_int]
        self._model.set_value(new_value)
        self._item_changed(None)


class TokenComboBoxWidget:
    def __init__(self, stage, attr_name, prim_paths, metadata, additional_widget_kwargs):
        self._combo_box = None
        self._metadata = metadata
        self._additional_widget_kwargs = additional_widget_kwargs
        self._model = UsdAttributeModel(stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata)
        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)

    def clean(self):
        if self._model is not None:
            self._model.clean()
        self._model = None
        self._combo_box = None
        self._frame = None

    def _build(self):
        allowed_tokens = None
        if self._metadata is not None:
            allowed_tokens = self._metadata.get("allowedTokens", None)

        widget_kwargs = {"name": "choices"}
        if self._additional_widget_kwargs is not None:
            widget_kwargs.update(self._additional_widget_kwargs)

        combo_model = TokenItemModel(self._model, allowed_tokens)
        self._combo_box = ui.ComboBox(combo_model, **widget_kwargs)

    def _set_dirty(self):
        self._frame.rebuild()


from omni.kit.window.property.templates import (
    HORIZONTAL_SPACING,
    LABEL_WIDTH,
)

def build_token_combobox_prop(
    stage,
    attr_name,
    metadata,
    property_type,
    prim_paths: List[Sdf.Path],
    additional_label_kwargs=None,
    additional_widget_kwargs=None,
):
    with ui.HStack(spacing=HORIZONTAL_SPACING):
        with ui.VStack(width=LABEL_WIDTH):
            UsdPropertiesWidgetBuilder._create_label(attr_name, metadata, additional_label_kwargs)
        ui.Spacer(width=5)
        return TokenComboBoxWidget(stage, attr_name, prim_paths, metadata, additional_widget_kwargs)
