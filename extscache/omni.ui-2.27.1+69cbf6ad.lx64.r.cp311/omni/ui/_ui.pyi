from __future__ import annotations
import omni.ui._ui
import typing
import carb._carb
import numpy
import omni.appwindow._appwindow
import omni.gpu_foundation_factory._gpu_foundation_factory
import omni.kit.renderer_capture._renderer_capture
_Shape = typing.Tuple[int, ...]

__all__ = [
    "AbstractField",
    "AbstractItem",
    "AbstractItemDelegate",
    "AbstractItemModel",
    "AbstractMultiField",
    "AbstractSlider",
    "AbstractValueModel",
    "Alignment",
    "ArrowHelper",
    "ArrowType",
    "Axis",
    "BezierCurve",
    "Button",
    "ByteImageProvider",
    "CanvasFrame",
    "CheckBox",
    "Circle",
    "CircleSizePolicy",
    "CollapsableFrame",
    "ColorStore",
    "ColorWidget",
    "ComboBox",
    "Container",
    "CornerFlag",
    "Direction",
    "DockPolicy",
    "DockPosition",
    "DockPreference",
    "DockSpace",
    "DynamicTextureProvider",
    "Ellipse",
    "FillPolicy",
    "FloatDrag",
    "FloatField",
    "FloatSlider",
    "FloatStore",
    "FocusPolicy",
    "FontStyle",
    "Fraction",
    "Frame",
    "FreeBezierCurve",
    "FreeCircle",
    "FreeEllipse",
    "FreeLine",
    "FreeRectangle",
    "FreeTriangle",
    "Grid",
    "HGrid",
    "HStack",
    "Image",
    "ImageProvider",
    "ImageWithProvider",
    "Inspector",
    "IntDrag",
    "IntField",
    "IntSlider",
    "InvisibleButton",
    "ItemModelHelper",
    "IwpFillPolicy",
    "Label",
    "Length",
    "Line",
    "MainWindow",
    "Menu",
    "MenuBar",
    "MenuDelegate",
    "MenuHelper",
    "MenuItem",
    "MenuItemCollection",
    "MultiFloatDragField",
    "MultiFloatField",
    "MultiIntDragField",
    "MultiIntField",
    "MultiStringField",
    "OffsetLine",
    "Percent",
    "Pixel",
    "Placer",
    "Plot",
    "ProgressBar",
    "RadioButton",
    "RadioCollection",
    "RasterImageProvider",
    "RasterPolicy",
    "Rectangle",
    "ScrollBarPolicy",
    "ScrollingFrame",
    "Separator",
    "ShadowFlag",
    "Shape",
    "ShapeAnchorHelper",
    "SimpleBoolModel",
    "SimpleFloatModel",
    "SimpleIntModel",
    "SimpleStringModel",
    "SliderDrawMode",
    "Spacer",
    "Stack",
    "StringField",
    "StringStore",
    "Style",
    "ToolBar",
    "ToolBarAxis",
    "ToolButton",
    "TreeView",
    "Triangle",
    "Type",
    "UIntDrag",
    "UIntSlider",
    "UnitType",
    "VGrid",
    "VStack",
    "ValueModelHelper",
    "VectorImageProvider",
    "WINDOW_FLAGS_FORCE_HORIZONTAL_SCROLLBAR",
    "WINDOW_FLAGS_FORCE_VERTICAL_SCROLLBAR",
    "WINDOW_FLAGS_MENU_BAR",
    "WINDOW_FLAGS_MODAL",
    "WINDOW_FLAGS_NONE",
    "WINDOW_FLAGS_NO_BACKGROUND",
    "WINDOW_FLAGS_NO_CLOSE",
    "WINDOW_FLAGS_NO_COLLAPSE",
    "WINDOW_FLAGS_NO_DOCKING",
    "WINDOW_FLAGS_NO_FOCUS_ON_APPEARING",
    "WINDOW_FLAGS_NO_MOUSE_INPUTS",
    "WINDOW_FLAGS_NO_MOVE",
    "WINDOW_FLAGS_NO_RESIZE",
    "WINDOW_FLAGS_NO_SAVED_SETTINGS",
    "WINDOW_FLAGS_NO_SCROLLBAR",
    "WINDOW_FLAGS_NO_SCROLL_WITH_MOUSE",
    "WINDOW_FLAGS_NO_TITLE_BAR",
    "WINDOW_FLAGS_POPUP",
    "WINDOW_FLAGS_SHOW_HORIZONTAL_SCROLLBAR",
    "Widget",
    "WidgetMouseDropEvent",
    "Window",
    "WindowHandle",
    "Workspace",
    "ZStack",
    "dock_window_in_window",
    "get_custom_glyph_code",
    "get_main_window_height",
    "get_main_window_width"
]


class AbstractField(Widget, ValueModelHelper):
    """
    The abstract widget that is base for any field, which is a one-line text editor.
    A field allows the user to enter and edit a single line of plain text. It's implemented using the model-view pattern and uses AbstractValueModel as the central component of the system.
    """
    def focus_keyboard(self, focus: bool = True) -> None: 
        """
        Puts cursor to this field or removes focus if
        focus
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class AbstractItem():
    """
    The object that is associated with the data entity of the AbstractItemModel.
    """
    def __init__(self) -> None: ...
    pass
class AbstractItemDelegate():
    """
    AbstractItemDelegate is used to generate widgets that display and edit data items from a model.
    """
    def __init__(self) -> None: 
        """
        Constructs AbstractItemDelegate.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    def build_branch(self, model: AbstractItemModel, item: AbstractItem = None, column_id: int = 0, level: int = 0, expanded: bool = False) -> None: 
        """
        This pure abstract method must be reimplemented to generate custom collapse/expand button.
        """
    def build_header(self, column_id: int = 0) -> None: 
        """
        This pure abstract method must be reimplemented to generate custom widgets for the header table.
        """
    def build_widget(self, model: AbstractItemModel, item: AbstractItem = None, index: int = 0, level: int = 0, expanded: bool = False) -> None: 
        """
        This pure abstract method must be reimplemented to generate custom widgets for specific item in the model.
        """
    pass
class AbstractItemModel():
    """
    The central component of the item widget. It is the application's dynamic data structure, independent of the user interface, and it directly manages the nested data. It follows closely model-view pattern. It's abstract, and it defines the standard interface to be able to interoperate with the components of the model-view architecture. It is not supposed to be instantiated directly. Instead, the user should subclass it to create a new model.
    The item model doesn't return the data itself. Instead, it returns the value model that can contain any data type and supports callbacks. Thus the client of the model can track the changes in both the item model and any value it holds.
    From any item, the item model can get both the value model and the nested items. Therefore, the model is flexible to represent anything from color to complicated tree-table construction.
    """
    def __init__(self) -> None: 
        """
        Constructs AbstractItemModel.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    def _item_changed(self, arg0: AbstractItem) -> None: ...
    def add_begin_edit_fn(self, arg0: typing.Callable[[AbstractItemModel, AbstractItem], None]) -> int: 
        """
        Adds the function that will be called every time the user starts the editing.
        The id of the callback that is used to remove the callback.
        """
    def add_end_edit_fn(self, arg0: typing.Callable[[AbstractItemModel, AbstractItem], None]) -> int: 
        """
        Adds the function that will be called every time the user finishes the editing.
        The id of the callback that is used to remove the callback.
        """
    def add_item_changed_fn(self, arg0: typing.Callable[[AbstractItemModel, AbstractItem], None]) -> int: 
        """
        Adds the function that will be called every time the value changes.
        The id of the callback that is used to remove the callback.
        """
    def append_child_item(self, parentItem: AbstractItem, model: AbstractValueModel) -> AbstractItem: 
        """
        Creates a new item from the value model and appends it to the list of the children of the given item.
        """
    def begin_edit(self, item: AbstractItem) -> None: 
        """
        Called when the user starts the editing. If it's a field, this method is called when the user activates the field and places the cursor inside.
        """
    def can_item_have_children(self, parentItem: AbstractItem = None) -> bool: 
        """
        Returns true if the item can have children. In this way the delegate usually draws +/- icon.


        ### Arguments:

            `id :`
                The item to request children from. If it's null, the children of root will be returned.
        """
    @typing.overload
    def drop(self, item_tagget: AbstractItem, item_source: AbstractItem, drop_location: int = -1) -> None: 
        """
        Called when the user droped one item to another.
        Small explanation why the same default value is declared in multiple places. We use the default value to be compatible with the previous API and especially with Stage 2.0. Thr signature in the old Python API is:
        def drop(self, target_item, source)
        drop(self, target_item, source)
        PyAbstractItemModel::drop
        AbstractItemModel.drop
        pybind11::class_<AbstractItemModel>.def("drop")
        AbstractItemModel

        Called when the user droped a string to the item.
        """
    @typing.overload
    def drop(self, item_tagget: AbstractItem, source: str, drop_location: int = -1) -> None: ...
    @typing.overload
    def drop_accepted(self, item_tagget: AbstractItem, item_source: AbstractItem, drop_location: int = -1) -> bool: 
        """
        Called to determine if the model can perform drag and drop to the given item. If this method returns false, the widget shouldn't highlight the visual element that represents this item.

        Called to determine if the model can perform drag and drop of the given string to the given item. If this method returns false, the widget shouldn't highlight the visual element that represents this item.
        """
    @typing.overload
    def drop_accepted(self, item_tagget: AbstractItem, source: str, drop_location: int = -1) -> bool: ...
    def end_edit(self, item: AbstractItem) -> None: 
        """
        Called when the user finishes the editing. If it's a field, this method is called when the user presses Enter or selects another field for editing. It's useful for undo/redo.
        """
    def get_drag_mime_data(self, item: AbstractItem = None) -> str: 
        """
        Returns Multipurpose Internet Mail Extensions (MIME) for drag and drop.
        """
    def get_item_children(self, parentItem: AbstractItem = None) -> typing.List[AbstractItem]: 
        """
        Returns the vector of items that are nested to the given parent item.


        ### Arguments:

            `id :`
                The item to request children from. If it's null, the children of root will be returned.
        """
    def get_item_value_model(self, item: AbstractItem = None, column_id: int = 0) -> AbstractValueModel: 
        """
        Get the value model associated with this item.


        ### Arguments:

            `item :`
                The item to request the value model from. If it's null, the root value model will be returned.

            `index :`
                The column number to get the value model.
        """
    def get_item_value_model_count(self, item: AbstractItem = None) -> int: 
        """
        Returns the number of columns this model item contains.
        """
    def remove_begin_edit_fn(self, arg0: int) -> None: 
        """
        Remove the callback by its id.


        ### Arguments:

            `id :`
                The id that addBeginEditFn returns.
        """
    def remove_end_edit_fn(self, arg0: int) -> None: 
        """
        Remove the callback by its id.


        ### Arguments:

            `id :`
                The id that addEndEditFn returns.
        """
    def remove_item(self, item: AbstractItem) -> None: 
        """
        Removes the item from the model.
        There is no parent here because we assume that the reimplemented model deals with its data and can figure out how to remove this item.
        """
    def remove_item_changed_fn(self, arg0: int) -> None: 
        """
        Remove the callback by its id.


        ### Arguments:

            `id :`
                The id that addValueChangedFn returns.
        """
    def subscribe_begin_edit_fn(self, arg0: typing.Callable[[AbstractItemModel, AbstractItem], None]) -> carb._carb.Subscription: 
        """
        Adds the function that will be called every time the user starts the editing.
        The id of the callback that is used to remove the callback.
        """
    def subscribe_end_edit_fn(self, arg0: typing.Callable[[AbstractItemModel, AbstractItem], None]) -> carb._carb.Subscription: 
        """
        Adds the function that will be called every time the user finishes the editing.
        The id of the callback that is used to remove the callback.
        """
    def subscribe_item_changed_fn(self, arg0: typing.Callable[[AbstractItemModel, AbstractItem], None]) -> carb._carb.Subscription: 
        """
        Adds the function that will be called every time the value changes.
        The id of the callback that is used to remove the callback.
        """
    pass
class AbstractMultiField(Widget, ItemModelHelper):
    """
    AbstractMultiField is the abstract class that has everything to create a custom widget per model item.
    The class that wants to create multiple widgets per item needs to reimplement the method _createField.
    """
    @property
    def column_count(self) -> int:
        """
        The max number of fields in a line.

        :type: int
        """
    @column_count.setter
    def column_count(self, arg1: int) -> None:
        """
        The max number of fields in a line.
        """
    @property
    def h_spacing(self) -> float:
        """
        Sets a non-stretchable horizontal space in pixels between child fields.

        :type: float
        """
    @h_spacing.setter
    def h_spacing(self, arg1: float) -> None:
        """
        Sets a non-stretchable horizontal space in pixels between child fields.
        """
    @property
    def v_spacing(self) -> float:
        """
        Sets a non-stretchable vertical space in pixels between child fields.

        :type: float
        """
    @v_spacing.setter
    def v_spacing(self, arg1: float) -> None:
        """
        Sets a non-stretchable vertical space in pixels between child fields.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class AbstractSlider(Widget, ValueModelHelper):
    """
    The abstract widget that is base for drags and sliders.
    """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class AbstractValueModel():
    """

    """
    def __init__(self) -> None: 
        """
        Constructs AbstractValueModel.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    def _value_changed(self) -> None: 
        """
        Called when any data of the model is changed. It will notify the subscribed widgets.
        """
    def add_begin_edit_fn(self, arg0: typing.Callable[[AbstractValueModel], None]) -> int: 
        """
        Adds the function that will be called every time the user starts the editing.
        The id of the callback that is used to remove the callback.
        """
    def add_end_edit_fn(self, arg0: typing.Callable[[AbstractValueModel], None]) -> int: 
        """
        Adds the function that will be called every time the user finishes the editing.
        The id of the callback that is used to remove the callback.
        """
    def add_value_changed_fn(self, arg0: typing.Callable[[AbstractValueModel], None]) -> int: 
        """
        Adds the function that will be called every time the value changes.
        The id of the callback that is used to remove the callback.
        """
    def begin_edit(self) -> None: 
        """
        Called when the user starts the editing. If it's a field, this method is called when the user activates the field and places the cursor inside. This method should be reimplemented.
        """
    def end_edit(self) -> None: 
        """
        Called when the user finishes the editing. If it's a field, this method is called when the user presses Enter or selects another field for editing. It's useful for undo/redo. This method should be reimplemented.
        """
    def get_value_as_bool(self) -> bool: 
        """
        Return the bool representation of the value.
        """
    def get_value_as_float(self) -> float: 
        """
        Return the float representation of the value.
        """
    def get_value_as_int(self) -> int: 
        """
        Return the int representation of the value.
        """
    def get_value_as_string(self) -> str: 
        """
        Return the string representation of the value.
        """
    def remove_begin_edit_fn(self, arg0: int) -> None: 
        """
        Remove the callback by its id.


        ### Arguments:

            `id :`
                The id that addBeginEditFn returns.
        """
    def remove_end_edit_fn(self, arg0: int) -> None: 
        """
        Remove the callback by its id.


        ### Arguments:

            `id :`
                The id that addEndEditFn returns.
        """
    def remove_value_changed_fn(self, arg0: int) -> None: 
        """
        Remove the callback by its id.


        ### Arguments:

            `id :`
                The id that addValueChangedFn returns.
        """
    @typing.overload
    def set_value(self, value: bool) -> None: 
        """
        Set the value.

        Set the value.

        Set the value.

        Set the value.
        """
    @typing.overload
    def set_value(self, value: int) -> None: ...
    @typing.overload
    def set_value(self, value: float) -> None: ...
    @typing.overload
    def set_value(self, value: str) -> None: ...
    def subscribe_begin_edit_fn(self, arg0: typing.Callable[[AbstractValueModel], None]) -> carb._carb.Subscription: 
        """
        Adds the function that will be called every time the user starts the editing.
        The id of the callback that is used to remove the callback.
        """
    def subscribe_end_edit_fn(self, arg0: typing.Callable[[AbstractValueModel], None]) -> carb._carb.Subscription: 
        """
        Adds the function that will be called every time the user finishes the editing.
        The id of the callback that is used to remove the callback.
        """
    def subscribe_item_changed_fn(self, arg0: typing.Callable[[AbstractValueModel], None]) -> carb._carb.Subscription: ...
    def subscribe_value_changed_fn(self, arg0: typing.Callable[[AbstractValueModel], None]) -> carb._carb.Subscription: 
        """
        Adds the function that will be called every time the value changes.
        The id of the callback that is used to remove the callback.
        """
    @property
    def as_bool(self) -> bool:
        """
        Return the bool representation of the value.

        :type: bool
        """
    @as_bool.setter
    def as_bool(self, arg1: bool) -> None:
        """
        Return the bool representation of the value.
        """
    @property
    def as_float(self) -> float:
        """
        Return the float representation of the value.

        :type: float
        """
    @as_float.setter
    def as_float(self, arg1: float) -> None:
        """
        Return the float representation of the value.
        """
    @property
    def as_int(self) -> int:
        """
        Return the int representation of the value.

        :type: int
        """
    @as_int.setter
    def as_int(self, arg1: int) -> None:
        """
        Return the int representation of the value.
        """
    @property
    def as_string(self) -> str:
        """
        Return the string representation of the value.

        :type: str
        """
    @as_string.setter
    def as_string(self, arg1: str) -> None:
        """
        Return the string representation of the value.
        """
    pass
class Alignment():
    """
    Members:

      UNDEFINED

      LEFT_TOP

      LEFT_CENTER

      LEFT_BOTTOM

      CENTER_TOP

      CENTER

      CENTER_BOTTOM

      RIGHT_TOP

      RIGHT_CENTER

      RIGHT_BOTTOM

      LEFT

      RIGHT

      H_CENTER

      TOP

      BOTTOM

      V_CENTER
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    BOTTOM: omni.ui._ui.Alignment # value = <Alignment.BOTTOM: 32>
    CENTER: omni.ui._ui.Alignment # value = <Alignment.CENTER: 72>
    CENTER_BOTTOM: omni.ui._ui.Alignment # value = <Alignment.CENTER_BOTTOM: 40>
    CENTER_TOP: omni.ui._ui.Alignment # value = <Alignment.CENTER_TOP: 24>
    H_CENTER: omni.ui._ui.Alignment # value = <Alignment.H_CENTER: 8>
    LEFT: omni.ui._ui.Alignment # value = <Alignment.LEFT: 2>
    LEFT_BOTTOM: omni.ui._ui.Alignment # value = <Alignment.LEFT_BOTTOM: 34>
    LEFT_CENTER: omni.ui._ui.Alignment # value = <Alignment.LEFT_CENTER: 66>
    LEFT_TOP: omni.ui._ui.Alignment # value = <Alignment.LEFT_TOP: 18>
    RIGHT: omni.ui._ui.Alignment # value = <Alignment.RIGHT: 4>
    RIGHT_BOTTOM: omni.ui._ui.Alignment # value = <Alignment.RIGHT_BOTTOM: 36>
    RIGHT_CENTER: omni.ui._ui.Alignment # value = <Alignment.RIGHT_CENTER: 68>
    RIGHT_TOP: omni.ui._ui.Alignment # value = <Alignment.RIGHT_TOP: 20>
    TOP: omni.ui._ui.Alignment # value = <Alignment.TOP: 16>
    UNDEFINED: omni.ui._ui.Alignment # value = <Alignment.UNDEFINED: 0>
    V_CENTER: omni.ui._ui.Alignment # value = <Alignment.V_CENTER: 64>
    __members__: dict # value = {'UNDEFINED': <Alignment.UNDEFINED: 0>, 'LEFT_TOP': <Alignment.LEFT_TOP: 18>, 'LEFT_CENTER': <Alignment.LEFT_CENTER: 66>, 'LEFT_BOTTOM': <Alignment.LEFT_BOTTOM: 34>, 'CENTER_TOP': <Alignment.CENTER_TOP: 24>, 'CENTER': <Alignment.CENTER: 72>, 'CENTER_BOTTOM': <Alignment.CENTER_BOTTOM: 40>, 'RIGHT_TOP': <Alignment.RIGHT_TOP: 20>, 'RIGHT_CENTER': <Alignment.RIGHT_CENTER: 68>, 'RIGHT_BOTTOM': <Alignment.RIGHT_BOTTOM: 36>, 'LEFT': <Alignment.LEFT: 2>, 'RIGHT': <Alignment.RIGHT: 4>, 'H_CENTER': <Alignment.H_CENTER: 8>, 'TOP': <Alignment.TOP: 16>, 'BOTTOM': <Alignment.BOTTOM: 32>, 'V_CENTER': <Alignment.V_CENTER: 64>}
    pass
class ArrowHelper():
    """
    The ArrowHelper widget provides a colored rectangle to display.
    """
    @property
    def begin_arrow_height(self) -> float:
        """
        This property holds the height of the begin arrow.

        :type: float
        """
    @begin_arrow_height.setter
    def begin_arrow_height(self, arg1: float) -> None:
        """
        This property holds the height of the begin arrow.
        """
    @property
    def begin_arrow_type(self) -> ArrowType:
        """
        This property holds the type of the begin arrow can only be eNone or eRrrow. By default, the arrow type is eNone.

        :type: ArrowType
        """
    @begin_arrow_type.setter
    def begin_arrow_type(self, arg1: ArrowType) -> None:
        """
        This property holds the type of the begin arrow can only be eNone or eRrrow. By default, the arrow type is eNone.
        """
    @property
    def begin_arrow_width(self) -> float:
        """
        This property holds the width of the begin arrow.

        :type: float
        """
    @begin_arrow_width.setter
    def begin_arrow_width(self, arg1: float) -> None:
        """
        This property holds the width of the begin arrow.
        """
    @property
    def end_arrow_height(self) -> float:
        """
        This property holds the height of the end arrow.

        :type: float
        """
    @end_arrow_height.setter
    def end_arrow_height(self, arg1: float) -> None:
        """
        This property holds the height of the end arrow.
        """
    @property
    def end_arrow_type(self) -> ArrowType:
        """
        This property holds the type of the end arrow can only be eNone or eRrrow. By default, the arrow type is eNone.

        :type: ArrowType
        """
    @end_arrow_type.setter
    def end_arrow_type(self, arg1: ArrowType) -> None:
        """
        This property holds the type of the end arrow can only be eNone or eRrrow. By default, the arrow type is eNone.
        """
    @property
    def end_arrow_width(self) -> float:
        """
        This property holds the width of the end arrow.

        :type: float
        """
    @end_arrow_width.setter
    def end_arrow_width(self, arg1: float) -> None:
        """
        This property holds the width of the end arrow.
        """
    pass
class ArrowType():
    """
    Members:

      NONE

      ARROW
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ARROW: omni.ui._ui.ArrowType # value = <ArrowType.ARROW: 1>
    NONE: omni.ui._ui.ArrowType # value = <ArrowType.NONE: 0>
    __members__: dict # value = {'NONE': <ArrowType.NONE: 0>, 'ARROW': <ArrowType.ARROW: 1>}
    pass
class Axis():
    """
    Members:

      NONE

      X

      Y

      XY
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    NONE: omni.ui._ui.Axis # value = <Axis.NONE: 0>
    X: omni.ui._ui.Axis # value = <Axis.X: 1>
    XY: omni.ui._ui.Axis # value = <Axis.XY: 3>
    Y: omni.ui._ui.Axis # value = <Axis.Y: 2>
    __members__: dict # value = {'NONE': <Axis.NONE: 0>, 'X': <Axis.X: 1>, 'Y': <Axis.Y: 2>, 'XY': <Axis.XY: 3>}
    pass
class BezierCurve(Shape, Widget, ArrowHelper, ShapeAnchorHelper):
    """
    Smooth curve that can be scaled infinitely.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Initialize the curve.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

        `start_tangent_width: `    
        This property holds the X coordinate of the start of the curve relative to the width bound of the curve.

        `start_tangent_height: `    
        This property holds the Y coordinate of the start of the curve relative to the width bound of the curve.

        `end_tangent_width: `    
        This property holds the X coordinate of the end of the curve relative to the width bound of the curve.

        `end_tangent_height: `    
        This property holds the Y coordinate of the end of the curve relative to the width bound of the curve.

        `set_mouse_hovered_fn: `    
        Sets the function that will be called when the user use mouse enter/leave on the line. It's the override to prevent Widget from the bounding box logic. The function specification is: void onMouseHovered(bool hovered)

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.

            `anchor_position: `
                This property holds the parametric value of the curve anchor.

            `anchor_alignment: `
                This property holds the Alignment of the curve anchor.

            `set_anchor_fn: Callable`
                Sets the function that will be called for the curve anchor.

            `invalidate_anchor: `
                Function that causes the anchor frame to be redrawn.

            `get_closest_parametric_position: `
                Function that returns the closest parametric T value to a given x,y position.
        """
    def call_mouse_hovered_fn(self, arg0: bool) -> None: 
        """
        Sets the function that will be called when the user use mouse enter/leave on the line. It's the override to prevent Widget from the bounding box logic. The function specification is: void onMouseHovered(bool hovered)
        """
    def has_mouse_hovered_fn(self) -> bool: 
        """
        Sets the function that will be called when the user use mouse enter/leave on the line. It's the override to prevent Widget from the bounding box logic. The function specification is: void onMouseHovered(bool hovered)
        """
    def set_mouse_hovered_fn(self, fn: typing.Callable[[bool], None]) -> None: 
        """
        Sets the function that will be called when the user use mouse enter/leave on the line. It's the override to prevent Widget from the bounding box logic. The function specification is: void onMouseHovered(bool hovered)
        """
    @property
    def end_tangent_height(self) -> Length:
        """
        This property holds the Y coordinate of the end of the curve relative to the width bound of the curve.

        :type: Length
        """
    @end_tangent_height.setter
    def end_tangent_height(self, arg1: Length) -> None:
        """
        This property holds the Y coordinate of the end of the curve relative to the width bound of the curve.
        """
    @property
    def end_tangent_width(self) -> Length:
        """
        This property holds the X coordinate of the end of the curve relative to the width bound of the curve.

        :type: Length
        """
    @end_tangent_width.setter
    def end_tangent_width(self, arg1: Length) -> None:
        """
        This property holds the X coordinate of the end of the curve relative to the width bound of the curve.
        """
    @property
    def start_tangent_height(self) -> Length:
        """
        This property holds the Y coordinate of the start of the curve relative to the width bound of the curve.

        :type: Length
        """
    @start_tangent_height.setter
    def start_tangent_height(self, arg1: Length) -> None:
        """
        This property holds the Y coordinate of the start of the curve relative to the width bound of the curve.
        """
    @property
    def start_tangent_width(self) -> Length:
        """
        This property holds the X coordinate of the start of the curve relative to the width bound of the curve.

        :type: Length
        """
    @start_tangent_width.setter
    def start_tangent_width(self, arg1: Length) -> None:
        """
        This property holds the X coordinate of the start of the curve relative to the width bound of the curve.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Button(InvisibleButton, Widget):
    """
    The Button widget provides a command button.
    The command button, is perhaps the most commonly used widget in any graphical user interface. Click a button to execute a command. It is rectangular and typically displays a text label describing its action.
    """
    def __init__(self, text: str = '', **kwargs) -> None: 
        """
        Construct a button with a text on it.


        ### Arguments:

            `text :`
                The text for the button to use.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `text : str`
                This property holds the button's text.

            `image_url : str`
                This property holds the button's optional image URL.

            `image_width : float`
                This property holds the width of the image widget. Do not use this function to find the width of the image.

            `image_height : float`
                This property holds the height of the image widget. Do not use this function to find the height of the image.

            `spacing : float`
                Sets a non-stretchable space in points between image and text.

            `clicked_fn : Callable[[], None]`
                Sets the function that will be called when when the button is activated (i.e., pressed down then released while the mouse cursor is inside the button).

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def image_height(self) -> Length:
        """
        This property holds the height of the image widget. Do not use this function to find the height of the image.

        :type: Length
        """
    @image_height.setter
    def image_height(self, arg1: Length) -> None:
        """
        This property holds the height of the image widget. Do not use this function to find the height of the image.
        """
    @property
    def image_url(self) -> str:
        """
        This property holds the button's optional image URL.

        :type: str
        """
    @image_url.setter
    def image_url(self, arg1: str) -> None:
        """
        This property holds the button's optional image URL.
        """
    @property
    def image_width(self) -> Length:
        """
        This property holds the width of the image widget. Do not use this function to find the width of the image.

        :type: Length
        """
    @image_width.setter
    def image_width(self, arg1: Length) -> None:
        """
        This property holds the width of the image widget. Do not use this function to find the width of the image.
        """
    @property
    def spacing(self) -> float:
        """
        Sets a non-stretchable space in points between image and text.

        :type: float
        """
    @spacing.setter
    def spacing(self, arg1: float) -> None:
        """
        Sets a non-stretchable space in points between image and text.
        """
    @property
    def text(self) -> str:
        """
        This property holds the button's text.

        :type: str
        """
    @text.setter
    def text(self, arg1: str) -> None:
        """
        This property holds the button's text.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ByteImageProvider(ImageProvider):
    """
    doc
    """
    @typing.overload
    def __init__(self) -> None: 
        """
        doc

        doc
        """
    @staticmethod
    @typing.overload
    def __init__(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def set_bytes_data(*args, **kwargs) -> typing.Any: 
        """
        Sets Python sequence as byte data. The image provider will recognize flattened color values, or sequence within sequence and convert it into an image.
        """
    def set_bytes_data_from_gpu(self, gpu_bytes: int, sizes: typing.List[int], format: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat = TextureFormat.RGBA8_UNORM, stride: int = -1) -> None: 
        """
        Sets byte data from a copy of gpu memory at gpuBytes.
        """
    def set_data(self, arg0: typing.List[int], arg1: typing.List[int]) -> None: 
        """
        [DEPRECATED FUNCTION]
        """
    def set_data_array(self, arg0: numpy.ndarray[numpy.uint8], arg1: typing.List[int]) -> None: ...
    def set_raw_bytes_data(self, raw_bytes: capsule, sizes: typing.List[int], format: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat = TextureFormat.RGBA8_UNORM, stride: int = -1) -> None: 
        """
        Sets byte data that the image provider will turn raw pointer array into an image.
        """
    pass
class CanvasFrame(Frame, Container, Widget):
    """
    CanvasFrame is the widget that allows the user to pan and zoom its children with a mouse. It has the layout that can be infinitely moved in any direction.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructs CanvasFrame.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `pan_x : `
                The horizontal offset of the child item.

            `pan_y : `
                The vertical offset of the child item.

            `zoom : `
                The zoom minimum of the child item.

            `zoom_min : `
                The zoom maximum of the child item.

            `zoom_max : `
                The zoom level of the child item.

            `compatibility : `
                This boolean property controls the behavior of CanvasFrame. When set to true, the widget will function in the old way. When set to false, the widget will use a newer and faster implementation. This variable is included as a transition period to ensure that the update does not break any existing functionality. Please be aware that the old behavior may be deprecated in the future, so it is recommended to set this variable to false once you have thoroughly tested the new implementation.

            `pan_x_changed_fn : `
                The horizontal offset of the child item.

            `pan_y_changed_fn : `
                The vertical offset of the child item.

            `zoom_changed_fn : `
                The zoom level of the child item.

            `draggable : `
                Provides a convenient way to make the content draggable and zoomable.

            `horizontal_clipping : `
                When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for horizontal direction.

            `vertical_clipping : `
                When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for vertial direction.

            `separate_window : `
                A special mode where the child is placed to the transparent borderless window. We need it to be able to place the UI to the exact stacking order between other windows.

            `raster_policy : `
                Determine how the content of the frame should be rasterized.

            `build_fn : `
                Set the callback that will be called once the frame is visible and the content of the callback will override the frame child. It's useful for lazy load.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    def screen_to_canvas(self, x: float, y: float) -> typing.Tuple[float, float]: 
        """
        Transforms screen-space coordinates to canvas-space
        """
    def screen_to_canvas_x(self, x: float) -> float: 
        """
        Transforms screen-space X to canvas-space X.
        """
    def screen_to_canvas_y(self, y: float) -> float: 
        """
        Transforms screen-space Y to canvas-space Y.
        """
    def set_pan_key_shortcut(self, mouse_button: int, key_flag: int) -> None: 
        """
        Specify the mouse button and key to pan the canvas.
        """
    def set_pan_x_changed_fn(self, fn: typing.Callable[[float], None]) -> None: 
        """
        The horizontal offset of the child item.
        """
    def set_pan_y_changed_fn(self, fn: typing.Callable[[float], None]) -> None: 
        """
        The vertical offset of the child item.
        """
    def set_zoom_changed_fn(self, fn: typing.Callable[[float], None]) -> None: 
        """
        The zoom level of the child item.
        """
    def set_zoom_key_shortcut(self, mouse_button: int, key_flag: int) -> None: 
        """
        Specify the mouse button and key to zoom the canvas.
        """
    @property
    def compatibility(self) -> bool:
        """
        This boolean property controls the behavior of CanvasFrame. When set to true, the widget will function in the old way. When set to false, the widget will use a newer and faster implementation. This variable is included as a transition period to ensure that the update does not break any existing functionality. Please be aware that the old behavior may be deprecated in the future, so it is recommended to set this variable to false once you have thoroughly tested the new implementation.

        :type: bool
        """
    @compatibility.setter
    def compatibility(self, arg1: bool) -> None:
        """
        This boolean property controls the behavior of CanvasFrame. When set to true, the widget will function in the old way. When set to false, the widget will use a newer and faster implementation. This variable is included as a transition period to ensure that the update does not break any existing functionality. Please be aware that the old behavior may be deprecated in the future, so it is recommended to set this variable to false once you have thoroughly tested the new implementation.
        """
    @property
    def draggable(self) -> bool:
        """
        Provides a convenient way to make the content draggable and zoomable.

        :type: bool
        """
    @draggable.setter
    def draggable(self, arg1: bool) -> None:
        """
        Provides a convenient way to make the content draggable and zoomable.
        """
    @property
    def pan_x(self) -> float:
        """
        The horizontal offset of the child item.

        :type: float
        """
    @pan_x.setter
    def pan_x(self, arg1: float) -> None:
        """
        The horizontal offset of the child item.
        """
    @property
    def pan_y(self) -> float:
        """
        The vertical offset of the child item.

        :type: float
        """
    @pan_y.setter
    def pan_y(self, arg1: float) -> None:
        """
        The vertical offset of the child item.
        """
    @property
    def smooth_zoom(self) -> bool:
        """
        When true, zoom is smooth like in Bifrost even if the user is using mouse wheen that doesn't provide smooth scrolling.

        :type: bool
        """
    @smooth_zoom.setter
    def smooth_zoom(self, arg1: bool) -> None:
        """
        When true, zoom is smooth like in Bifrost even if the user is using mouse wheen that doesn't provide smooth scrolling.
        """
    @property
    def zoom(self) -> float:
        """
        The zoom level of the child item.

        :type: float
        """
    @zoom.setter
    def zoom(self, arg1: float) -> None:
        """
        The zoom level of the child item.
        """
    @property
    def zoom_max(self) -> float:
        """
        The zoom maximum of the child item.

        :type: float
        """
    @zoom_max.setter
    def zoom_max(self, arg1: float) -> None:
        """
        The zoom maximum of the child item.
        """
    @property
    def zoom_min(self) -> float:
        """
        The zoom minimum of the child item.

        :type: float
        """
    @zoom_min.setter
    def zoom_min(self, arg1: float) -> None:
        """
        The zoom minimum of the child item.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class CheckBox(Widget, ValueModelHelper):
    """
    A CheckBox is an option button that can be switched on (checked) or off (unchecked). Checkboxes are typically used to represent features in an application that can be enabled or disabled without affecting others.
    The checkbox is implemented using the model-view pattern. The model is the central component of this system. It is the application's dynamic data structure independent of the widget. It directly manages the data, logic, and rules of the checkbox. If the model is not specified, the simple one is created automatically when the object is constructed.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        CheckBox with specified model. If model is not specified, it's using the default one.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Circle(Shape, Widget):
    """
    The Circle widget provides a colored circle to display.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructs Circle.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment :`
                This property holds the alignment of the circle when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the circle is centered.

            `radius :`
                This property holds the radius of the circle when the fill policy is eFixed or eFixedCrop. By default, the circle radius is 0.

            `arc :`
                This property is the way to draw a half or a quarter of the circle. When it's eLeft, only left side of the circle is rendered. When it's eLeftTop, only left top quarter is rendered.

            `size_policy :`
                Define what happens when the source image has a different size than the item.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def alignment(self) -> Alignment:
        """
        This property holds the alignment of the circle when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the circle is centered.

        :type: Alignment
        """
    @alignment.setter
    def alignment(self, arg1: Alignment) -> None:
        """
        This property holds the alignment of the circle when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the circle is centered.
        """
    @property
    def arc(self) -> Alignment:
        """
        This property is the way to draw a half or a quarter of the circle. When it's eLeft, only left side of the circle is rendered. When it's eLeftTop, only left top quarter is rendered.

        :type: Alignment
        """
    @arc.setter
    def arc(self, arg1: Alignment) -> None:
        """
        This property is the way to draw a half or a quarter of the circle. When it's eLeft, only left side of the circle is rendered. When it's eLeftTop, only left top quarter is rendered.
        """
    @property
    def radius(self) -> float:
        """
        This property holds the radius of the circle when the fill policy is eFixed or eFixedCrop. By default, the circle radius is 0.

        :type: float
        """
    @radius.setter
    def radius(self, arg1: float) -> None:
        """
        This property holds the radius of the circle when the fill policy is eFixed or eFixedCrop. By default, the circle radius is 0.
        """
    @property
    def size_policy(self) -> CircleSizePolicy:
        """
        Define what happens when the source image has a different size than the item.

        :type: CircleSizePolicy
        """
    @size_policy.setter
    def size_policy(self, arg1: CircleSizePolicy) -> None:
        """
        Define what happens when the source image has a different size than the item.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class CircleSizePolicy():
    """
    Define what happens when the source image has a different size than the item.


    Members:

      STRETCH

      FIXED
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    FIXED: omni.ui._ui.CircleSizePolicy # value = <CircleSizePolicy.FIXED: 1>
    STRETCH: omni.ui._ui.CircleSizePolicy # value = <CircleSizePolicy.STRETCH: 0>
    __members__: dict # value = {'STRETCH': <CircleSizePolicy.STRETCH: 0>, 'FIXED': <CircleSizePolicy.FIXED: 1>}
    pass
class CollapsableFrame(Frame, Container, Widget):
    """
    CollapsableFrame is a frame widget that can hide or show its content. It has two states expanded and collapsed. When it's collapsed, it looks like a button. If it's expanded, it looks like a button and a frame with the content. It's handy to group properties, and temporarily hide them to get more space for something else.
    """
    def __init__(self, title: str = '', **kwargs) -> None: 
        """
        Constructs CollapsableFrame.


        ### Arguments:

            `text :`
                The text for the caption of the frame.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `collapsed : `
                The state of the CollapsableFrame.

            `title : `
                The header text.

            `alignment : `
                This property holds the alignment of the label in the default header. By default, the contents of the label are left-aligned and vertically-centered.

            `build_header_fn : `
                Set dynamic header that will be created dynamiclly when it is needed. The function is called inside a ui.Frame scope that the widget will be parented correctly.

            `collapsed_changed_fn : `
                The state of the CollapsableFrame.

            `horizontal_clipping : `
                When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for horizontal direction.

            `vertical_clipping : `
                When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for vertial direction.

            `separate_window : `
                A special mode where the child is placed to the transparent borderless window. We need it to be able to place the UI to the exact stacking order between other windows.

            `raster_policy : `
                Determine how the content of the frame should be rasterized.

            `build_fn : `
                Set the callback that will be called once the frame is visible and the content of the callback will override the frame child. It's useful for lazy load.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    def call_build_header_fn(self, arg0: bool, arg1: str) -> None: 
        """
        Set dynamic header that will be created dynamiclly when it is needed. The function is called inside a ui.Frame scope that the widget will be parented correctly.
        """
    def has_build_header_fn(self) -> bool: 
        """
        Set dynamic header that will be created dynamiclly when it is needed. The function is called inside a ui.Frame scope that the widget will be parented correctly.
        """
    def set_build_header_fn(self, fn: typing.Callable[[bool, str], None]) -> None: 
        """
        Set dynamic header that will be created dynamiclly when it is needed. The function is called inside a ui.Frame scope that the widget will be parented correctly.
        """
    def set_collapsed_changed_fn(self, fn: typing.Callable[[bool], None]) -> None: 
        """
        The state of the CollapsableFrame.
        """
    @property
    def alignment(self) -> Alignment:
        """
        This property holds the alignment of the label in the default header. By default, the contents of the label are left-aligned and vertically-centered.

        :type: Alignment
        """
    @alignment.setter
    def alignment(self, arg1: Alignment) -> None:
        """
        This property holds the alignment of the label in the default header. By default, the contents of the label are left-aligned and vertically-centered.
        """
    @property
    def collapsed(self) -> bool:
        """
        The state of the CollapsableFrame.

        :type: bool
        """
    @collapsed.setter
    def collapsed(self, arg1: bool) -> None:
        """
        The state of the CollapsableFrame.
        """
    @property
    def title(self) -> str:
        """
        The header text.

        :type: str
        """
    @title.setter
    def title(self, arg1: str) -> None:
        """
        The header text.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ColorStore():
    """
    A singleton that stores all the UI Style color properties of omni.ui.
    """
    @staticmethod
    def find(name: str) -> int: 
        """
        Return the index of the color with specific name.
        """
    @staticmethod
    def store(name: str, color: int) -> None: 
        """
        Save the color by name.
        """
    pass
class ColorWidget(Widget, ItemModelHelper):
    """
    The ColorWidget widget is a button that displays the color from the item model and can open a picker window to change the color.
    """
    @typing.overload
    def __init__(self, **kwargs) -> None: 
        """
        Construct ColorWidget.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @typing.overload
    def __init__(self, arg0: AbstractItemModel, **kwargs) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float, **kwargs) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float, arg3: float, **kwargs) -> None: ...
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ComboBox(Widget, ItemModelHelper):
    """
    The ComboBox widget is a combined button and a drop-down list.
    A combo box is a selection widget that displays the current item and can pop up a list of selectable items.
    The ComboBox is implemented using the model-view pattern. The model is the central component of this system. The root of the item model should contain the index of currently selected items, and the children of the root include all the items of the combo box.
    """
    def __init__(self, *args, **kwargs) -> None: 
        """
        Construct ComboBox.


        ### Arguments:

            `model :`
                The model that determines if the button is checked.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `arrow_only : bool`
                Determines if it's necessary to hide the text of the ComboBox.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Container(Widget):
    """
    Base class for all UI containers. Container can hold one or many other :class:`omni.ui.Widget` s
    """
    def __enter__(self) -> Container: ...
    def __exit__(self, arg0: object, arg1: object, arg2: object) -> None: ...
    def add_child(self, arg0: Widget) -> None: 
        """
        Adds widget to this container in a manner specific to the container. If it's allowed to have one sub-widget only, it will be overwriten.
        """
    def clear(self) -> None: 
        """
        Removes the container items from the container.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class CornerFlag():
    """
    Members:

      NONE

      TOP_LEFT

      TOP_RIGHT

      BOTTOM_LEFT

      BOTTOM_RIGHT

      TOP

      BOTTOM

      LEFT

      RIGHT

      ALL
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ALL: omni.ui._ui.CornerFlag # value = <CornerFlag.ALL: 15>
    BOTTOM: omni.ui._ui.CornerFlag # value = <CornerFlag.BOTTOM: 12>
    BOTTOM_LEFT: omni.ui._ui.CornerFlag # value = <CornerFlag.BOTTOM_LEFT: 4>
    BOTTOM_RIGHT: omni.ui._ui.CornerFlag # value = <CornerFlag.BOTTOM_RIGHT: 8>
    LEFT: omni.ui._ui.CornerFlag # value = <CornerFlag.LEFT: 5>
    NONE: omni.ui._ui.CornerFlag # value = <CornerFlag.NONE: 0>
    RIGHT: omni.ui._ui.CornerFlag # value = <CornerFlag.RIGHT: 10>
    TOP: omni.ui._ui.CornerFlag # value = <CornerFlag.TOP: 3>
    TOP_LEFT: omni.ui._ui.CornerFlag # value = <CornerFlag.TOP_LEFT: 1>
    TOP_RIGHT: omni.ui._ui.CornerFlag # value = <CornerFlag.TOP_RIGHT: 2>
    __members__: dict # value = {'NONE': <CornerFlag.NONE: 0>, 'TOP_LEFT': <CornerFlag.TOP_LEFT: 1>, 'TOP_RIGHT': <CornerFlag.TOP_RIGHT: 2>, 'BOTTOM_LEFT': <CornerFlag.BOTTOM_LEFT: 4>, 'BOTTOM_RIGHT': <CornerFlag.BOTTOM_RIGHT: 8>, 'TOP': <CornerFlag.TOP: 3>, 'BOTTOM': <CornerFlag.BOTTOM: 12>, 'LEFT': <CornerFlag.LEFT: 5>, 'RIGHT': <CornerFlag.RIGHT: 10>, 'ALL': <CornerFlag.ALL: 15>}
    pass
class Direction():
    """
    Members:

      LEFT_TO_RIGHT

      RIGHT_TO_LEFT

      TOP_TO_BOTTOM

      BOTTOM_TO_TOP

      BACK_TO_FRONT

      FRONT_TO_BACK
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    BACK_TO_FRONT: omni.ui._ui.Direction # value = <Direction.BACK_TO_FRONT: 4>
    BOTTOM_TO_TOP: omni.ui._ui.Direction # value = <Direction.BOTTOM_TO_TOP: 3>
    FRONT_TO_BACK: omni.ui._ui.Direction # value = <Direction.FRONT_TO_BACK: 5>
    LEFT_TO_RIGHT: omni.ui._ui.Direction # value = <Direction.LEFT_TO_RIGHT: 0>
    RIGHT_TO_LEFT: omni.ui._ui.Direction # value = <Direction.RIGHT_TO_LEFT: 1>
    TOP_TO_BOTTOM: omni.ui._ui.Direction # value = <Direction.TOP_TO_BOTTOM: 2>
    __members__: dict # value = {'LEFT_TO_RIGHT': <Direction.LEFT_TO_RIGHT: 0>, 'RIGHT_TO_LEFT': <Direction.RIGHT_TO_LEFT: 1>, 'TOP_TO_BOTTOM': <Direction.TOP_TO_BOTTOM: 2>, 'BOTTOM_TO_TOP': <Direction.BOTTOM_TO_TOP: 3>, 'BACK_TO_FRONT': <Direction.BACK_TO_FRONT: 4>, 'FRONT_TO_BACK': <Direction.FRONT_TO_BACK: 5>}
    pass
class DockPolicy():
    """
    Members:

      DO_NOTHING

      CURRENT_WINDOW_IS_ACTIVE

      TARGET_WINDOW_IS_ACTIVE
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    CURRENT_WINDOW_IS_ACTIVE: omni.ui._ui.DockPolicy # value = <DockPolicy.CURRENT_WINDOW_IS_ACTIVE: 1>
    DO_NOTHING: omni.ui._ui.DockPolicy # value = <DockPolicy.DO_NOTHING: 0>
    TARGET_WINDOW_IS_ACTIVE: omni.ui._ui.DockPolicy # value = <DockPolicy.TARGET_WINDOW_IS_ACTIVE: 2>
    __members__: dict # value = {'DO_NOTHING': <DockPolicy.DO_NOTHING: 0>, 'CURRENT_WINDOW_IS_ACTIVE': <DockPolicy.CURRENT_WINDOW_IS_ACTIVE: 1>, 'TARGET_WINDOW_IS_ACTIVE': <DockPolicy.TARGET_WINDOW_IS_ACTIVE: 2>}
    pass
class DockPosition():
    """
    Members:

      RIGHT

      LEFT

      TOP

      BOTTOM

      SAME
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    BOTTOM: omni.ui._ui.DockPosition # value = <DockPosition.BOTTOM: 3>
    LEFT: omni.ui._ui.DockPosition # value = <DockPosition.LEFT: 0>
    RIGHT: omni.ui._ui.DockPosition # value = <DockPosition.RIGHT: 1>
    SAME: omni.ui._ui.DockPosition # value = <DockPosition.SAME: 4>
    TOP: omni.ui._ui.DockPosition # value = <DockPosition.TOP: 2>
    __members__: dict # value = {'RIGHT': <DockPosition.RIGHT: 1>, 'LEFT': <DockPosition.LEFT: 0>, 'TOP': <DockPosition.TOP: 2>, 'BOTTOM': <DockPosition.BOTTOM: 3>, 'SAME': <DockPosition.SAME: 4>}
    pass
class DockPreference():
    """
    Members:

      DISABLED

      MAIN

      RIGHT

      LEFT

      RIGHT_TOP

      RIGHT_BOTTOM

      LEFT_BOTTOM
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    DISABLED: omni.ui._ui.DockPreference # value = <DockPreference.DISABLED: 0>
    LEFT: omni.ui._ui.DockPreference # value = <DockPreference.LEFT: 3>
    LEFT_BOTTOM: omni.ui._ui.DockPreference # value = <DockPreference.LEFT_BOTTOM: 6>
    MAIN: omni.ui._ui.DockPreference # value = <DockPreference.MAIN: 1>
    RIGHT: omni.ui._ui.DockPreference # value = <DockPreference.RIGHT: 2>
    RIGHT_BOTTOM: omni.ui._ui.DockPreference # value = <DockPreference.RIGHT_BOTTOM: 5>
    RIGHT_TOP: omni.ui._ui.DockPreference # value = <DockPreference.RIGHT_TOP: 4>
    __members__: dict # value = {'DISABLED': <DockPreference.DISABLED: 0>, 'MAIN': <DockPreference.MAIN: 1>, 'RIGHT': <DockPreference.RIGHT: 2>, 'LEFT': <DockPreference.LEFT: 3>, 'RIGHT_TOP': <DockPreference.RIGHT_TOP: 4>, 'RIGHT_BOTTOM': <DockPreference.RIGHT_BOTTOM: 5>, 'LEFT_BOTTOM': <DockPreference.LEFT_BOTTOM: 6>}
    pass
class DockSpace():
    """
    The DockSpace class represents Dock Space for the OS Window.
    """
    def __init__(self, arg0: object, **kwargs) -> None: 
        """
        Construct the main window, add it to the underlying windowing system, and makes it appear.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    @property
    def dock_frame(self) -> Frame:
        """
        This represents Styling opportunity for the Window background.

        :type: Frame
        """
    pass
class DynamicTextureProvider(ByteImageProvider, ImageProvider):
    """
    doc
    """
    def __init__(self, arg0: str) -> None: 
        """
        doc
        """
    pass
class Ellipse(Shape, Widget):
    """
    Constructs Ellipse.

        `kwargs : dict`
            See below

    ### Keyword Arguments:

        `width : ui.Length`
            This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

        `height : ui.Length`
            This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

        `name : str`
            The name of the widget that user can set.

        `style_type_name_override : str`
            By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

        `identifier : str`
            An optional identifier of the widget we can use to refer to it in queries.

        `visible : bool`
            This property holds whether the widget is visible.

        `visibleMin : float`
            If the current zoom factor and DPI is less than this value, the widget is not visible.

        `visibleMax : float`
            If the current zoom factor and DPI is bigger than this value, the widget is not visible.

        `tooltip : str`
            Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

        `tooltip_fn : Callable`
            Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

        `tooltip_offset_x : float`
            Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

        `tooltip_offset_y : float`
            Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

        `enabled : bool`
            This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

        `selected : bool`
            This property holds a flag that specifies the widget has to use eSelected state of the style.

        `checked : bool`
            This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

        `dragging : bool`
            This property holds if the widget is being dragged.

        `opaque_for_mouse_events : bool`
            If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

        `explicit_hover : bool`
            If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

        `skip_draw_when_clipped : bool`
            The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

        `mouse_moved_fn : Callable`
            Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

        `mouse_pressed_fn : Callable`
            Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

        `mouse_released_fn : Callable`
            Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

        `mouse_double_clicked_fn : Callable`
            Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

        `mouse_wheel_fn : Callable`
            Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

        `mouse_hovered_fn : Callable`
            Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

        `drag_fn : Callable`
            Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

        `accept_drop_fn : Callable`
            Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

        `drop_fn : Callable`
            Specify that this Widget accepts drops and set the callback to the drop operation.

        `computed_content_size_changed_fn : Callable`
            Called when the size of the widget is changed.
    """
    def __init__(self, **kwargs) -> None: ...
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FillPolicy():
    """
    Members:

      STRETCH

      PRESERVE_ASPECT_FIT

      PRESERVE_ASPECT_CROP
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    PRESERVE_ASPECT_CROP: omni.ui._ui.FillPolicy # value = <FillPolicy.PRESERVE_ASPECT_CROP: 2>
    PRESERVE_ASPECT_FIT: omni.ui._ui.FillPolicy # value = <FillPolicy.PRESERVE_ASPECT_FIT: 1>
    STRETCH: omni.ui._ui.FillPolicy # value = <FillPolicy.STRETCH: 0>
    __members__: dict # value = {'STRETCH': <FillPolicy.STRETCH: 0>, 'PRESERVE_ASPECT_FIT': <FillPolicy.PRESERVE_ASPECT_FIT: 1>, 'PRESERVE_ASPECT_CROP': <FillPolicy.PRESERVE_ASPECT_CROP: 2>}
    pass
class FloatDrag(FloatSlider, AbstractSlider, Widget, ValueModelHelper):
    """
    The drag widget that looks like a field but it's possible to change the value with dragging.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Construct FloatDrag.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `min : float`
                This property holds the slider's minimum value.

            `max : float`
                This property holds the slider's maximum value.

            `step : float`
                This property controls the steping speed on the drag.

            `format : str`
                This property overrides automatic formatting if needed.

            `precision : uint32_t`
                This property holds the slider value's float precision.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FloatField(AbstractField, Widget, ValueModelHelper):
    """
    The FloatField widget is a one-line text editor with a string model.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Construct FloatField.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `precision : uint32_t`
                This property holds the field value's float precision.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def precision(self) -> int:
        """
        This property holds the field value's float precision.

        :type: int
        """
    @precision.setter
    def precision(self, arg1: int) -> None:
        """
        This property holds the field value's float precision.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FloatSlider(AbstractSlider, Widget, ValueModelHelper):
    """
    The slider is the classic widget for controlling a bounded value. It lets the user move a slider handle along a horizontal groove and translates the handle's position into a float value within the legal range.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Construct FloatSlider.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `min : float`
                This property holds the slider's minimum value.

            `max : float`
                This property holds the slider's maximum value.

            `step : float`
                This property controls the steping speed on the drag.

            `format : str`
                This property overrides automatic formatting if needed.

            `precision : uint32_t`
                This property holds the slider value's float precision.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def format(self) -> str:
        """
        This property overrides automatic formatting if needed.

        :type: str
        """
    @format.setter
    def format(self, arg1: str) -> None:
        """
        This property overrides automatic formatting if needed.
        """
    @property
    def max(self) -> float:
        """
        This property holds the slider's maximum value.

        :type: float
        """
    @max.setter
    def max(self, arg1: float) -> None:
        """
        This property holds the slider's maximum value.
        """
    @property
    def min(self) -> float:
        """
        This property holds the slider's minimum value.

        :type: float
        """
    @min.setter
    def min(self, arg1: float) -> None:
        """
        This property holds the slider's minimum value.
        """
    @property
    def precision(self) -> int:
        """
        This property holds the slider value's float precision.

        :type: int
        """
    @precision.setter
    def precision(self, arg1: int) -> None:
        """
        This property holds the slider value's float precision.
        """
    @property
    def step(self) -> float:
        """
        This property controls the steping speed on the drag.

        :type: float
        """
    @step.setter
    def step(self, arg1: float) -> None:
        """
        This property controls the steping speed on the drag.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FloatStore():
    """
    A singleton that stores all the UI Style float properties of omni.ui.
    """
    @staticmethod
    def find(name: str) -> float: 
        """
        Return the index of the color with specific name.
        """
    @staticmethod
    def store(name: str, value: float) -> None: 
        """
        Save the color by name.
        """
    pass
class FocusPolicy():
    """
    Members:

      DEFAULT

      FOCUS_ON_LEFT_MOUSE_DOWN

      FOCUS_ON_ANY_MOUSE_DOWN

      FOCUS_ON_HOVER
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    DEFAULT: omni.ui._ui.FocusPolicy # value = <FocusPolicy.DEFAULT: 0>
    FOCUS_ON_ANY_MOUSE_DOWN: omni.ui._ui.FocusPolicy # value = <FocusPolicy.FOCUS_ON_ANY_MOUSE_DOWN: 1>
    FOCUS_ON_HOVER: omni.ui._ui.FocusPolicy # value = <FocusPolicy.FOCUS_ON_HOVER: 2>
    FOCUS_ON_LEFT_MOUSE_DOWN: omni.ui._ui.FocusPolicy # value = <FocusPolicy.DEFAULT: 0>
    __members__: dict # value = {'DEFAULT': <FocusPolicy.DEFAULT: 0>, 'FOCUS_ON_LEFT_MOUSE_DOWN': <FocusPolicy.DEFAULT: 0>, 'FOCUS_ON_ANY_MOUSE_DOWN': <FocusPolicy.FOCUS_ON_ANY_MOUSE_DOWN: 1>, 'FOCUS_ON_HOVER': <FocusPolicy.FOCUS_ON_HOVER: 2>}
    pass
class FontStyle():
    """
    Supported font styles.

    Members:

      NONE

      NORMAL

      LARGE

      SMALL

      EXTRA_LARGE

      XXL

      XXXL

      EXTRA_SMALL

      XXS

      XXXS

      ULTRA
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    EXTRA_LARGE: omni.ui._ui.FontStyle # value = <FontStyle.EXTRA_LARGE: 4>
    EXTRA_SMALL: omni.ui._ui.FontStyle # value = <FontStyle.EXTRA_SMALL: 7>
    LARGE: omni.ui._ui.FontStyle # value = <FontStyle.LARGE: 2>
    NONE: omni.ui._ui.FontStyle # value = <FontStyle.NONE: 0>
    NORMAL: omni.ui._ui.FontStyle # value = <FontStyle.NORMAL: 1>
    SMALL: omni.ui._ui.FontStyle # value = <FontStyle.SMALL: 3>
    ULTRA: omni.ui._ui.FontStyle # value = <FontStyle.ULTRA: 10>
    XXL: omni.ui._ui.FontStyle # value = <FontStyle.XXL: 5>
    XXS: omni.ui._ui.FontStyle # value = <FontStyle.XXS: 8>
    XXXL: omni.ui._ui.FontStyle # value = <FontStyle.XXL: 5>
    XXXS: omni.ui._ui.FontStyle # value = <FontStyle.XXXS: 9>
    __members__: dict # value = {'NONE': <FontStyle.NONE: 0>, 'NORMAL': <FontStyle.NORMAL: 1>, 'LARGE': <FontStyle.LARGE: 2>, 'SMALL': <FontStyle.SMALL: 3>, 'EXTRA_LARGE': <FontStyle.EXTRA_LARGE: 4>, 'XXL': <FontStyle.XXL: 5>, 'XXXL': <FontStyle.XXL: 5>, 'EXTRA_SMALL': <FontStyle.EXTRA_SMALL: 7>, 'XXS': <FontStyle.XXS: 8>, 'XXXS': <FontStyle.XXXS: 9>, 'ULTRA': <FontStyle.ULTRA: 10>}
    pass
class Fraction(Length):
    """
    Fraction length is made to take the space of the parent widget, divides it up into a row of boxes, and makes each child widget fill one box.
    """
    def __init__(self, value: float) -> None: 
        """
        Construct Fraction.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    pass
class Frame(Container, Widget):
    """
    The Frame is a widget that can hold one child widget.
    Frame is used to crop the contents of a child widget or to draw small widget in a big view. The child widget must be specified with addChild().
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructs Frame.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `horizontal_clipping : `
                When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for horizontal direction.

            `vertical_clipping : `
                When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for vertial direction.

            `separate_window : `
                A special mode where the child is placed to the transparent borderless window. We need it to be able to place the UI to the exact stacking order between other windows.

            `raster_policy : `
                Determine how the content of the frame should be rasterized.

            `build_fn : `
                Set the callback that will be called once the frame is visible and the content of the callback will override the frame child. It's useful for lazy load.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    def call_build_fn(self) -> None: 
        """
        Set the callback that will be called once the frame is visible and the content of the callback will override the frame child. It's useful for lazy load.
        """
    def has_build_fn(self) -> bool: 
        """
        Set the callback that will be called once the frame is visible and the content of the callback will override the frame child. It's useful for lazy load.
        """
    def invalidate_raster(self) -> None: 
        """
        This method regenerates the raster image of the widget, even if the widget's content has not changed. This can be used with both the eOnDemand and eAuto raster policies, and is used to update the content displayed in the widget. Note that this operation may be resource-intensive, and should be used sparingly.
        """
    def rebuild(self) -> None: 
        """
        After this method is called, the next drawing cycle build_fn will be called again to rebuild everything.
        """
    def set_build_fn(self, fn: typing.Callable[[], None]) -> None: 
        """
        Set the callback that will be called once the frame is visible and the content of the callback will override the frame child. It's useful for lazy load.
        """
    @property
    def frozen(self) -> bool:
        """
        A special mode where the child is placed to the transparent borderless window. We need it to be able to place the UI to the exact stacking order between other windows.

        :type: bool
        """
    @frozen.setter
    def frozen(self, arg1: bool) -> None:
        """
        A special mode where the child is placed to the transparent borderless window. We need it to be able to place the UI to the exact stacking order between other windows.
        """
    @property
    def horizontal_clipping(self) -> bool:
        """
        When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for horizontal direction.

        :type: bool
        """
    @horizontal_clipping.setter
    def horizontal_clipping(self, arg1: bool) -> None:
        """
        When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for horizontal direction.
        """
    @property
    def raster_policy(self) -> RasterPolicy:
        """
        Determine how the content of the frame should be rasterized.

        :type: RasterPolicy
        """
    @raster_policy.setter
    def raster_policy(self, arg1: RasterPolicy) -> None:
        """
        Determine how the content of the frame should be rasterized.
        """
    @property
    def separate_window(self) -> bool:
        """
        A special mode where the child is placed to the transparent borderless window. We need it to be able to place the UI to the exact stacking order between other windows.

        :type: bool
        """
    @separate_window.setter
    def separate_window(self, arg1: bool) -> None:
        """
        A special mode where the child is placed to the transparent borderless window. We need it to be able to place the UI to the exact stacking order between other windows.
        """
    @property
    def vertical_clipping(self) -> bool:
        """
        When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for vertial direction.

        :type: bool
        """
    @vertical_clipping.setter
    def vertical_clipping(self, arg1: bool) -> None:
        """
        When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for vertial direction.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FreeBezierCurve(BezierCurve, Shape, Widget, ArrowHelper, ShapeAnchorHelper):
    """
    Smooth curve that can be scaled infinitely.

    The free widget is the widget that is independent of the layout. It means it is stuck to other widgets. When initializing, it's necessary to provide two widgets, and the shape is drawn from one widget position to the another.
    """
    def __init__(self, arg0: Widget, arg1: Widget, **kwargs) -> None: 
        """
        Initialize the shape with bounds limited to the positions of the given widgets.


        ### Arguments:

            `start :`
                The bound corner is in the center of this given widget.

            `end :`
                The bound corner is in the center of this given widget.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

        `start_tangent_width: `    
        This property holds the X coordinate of the start of the curve relative to the width bound of the curve.

        `start_tangent_height: `    
        This property holds the Y coordinate of the start of the curve relative to the width bound of the curve.

        `end_tangent_width: `    
        This property holds the X coordinate of the end of the curve relative to the width bound of the curve.

        `end_tangent_height: `    
        This property holds the Y coordinate of the end of the curve relative to the width bound of the curve.

        `set_mouse_hovered_fn: `    
        Sets the function that will be called when the user use mouse enter/leave on the line. It's the override to prevent Widget from the bounding box logic. The function specification is: void onMouseHovered(bool hovered)

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.

            `anchor_position: `
                This property holds the parametric value of the curve anchor.

            `anchor_alignment: `
                This property holds the Alignment of the curve anchor.

            `set_anchor_fn: Callable`
                Sets the function that will be called for the curve anchor.

            `invalidate_anchor: `
                Function that causes the anchor frame to be redrawn.

            `get_closest_parametric_position: `
                Function that returns the closest parametric T value to a given x,y position.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FreeCircle(Circle, Shape, Widget):
    """
    The Circle widget provides a colored circle to display.

    The free widget is the widget that is independent of the layout. It means it is stuck to other widgets. When initializing, it's necessary to provide two widgets, and the shape is drawn from one widget position to the another.
    """
    def __init__(self, arg0: Widget, arg1: Widget, **kwargs) -> None: 
        """
        Initialize the shape with bounds limited to the positions of the given widgets.


        ### Arguments:

            `start :`
                The bound corner is in the center of this given widget.

            `end :`
                The bound corner is in the center of this given widget.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment :`
                This property holds the alignment of the circle when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the circle is centered.

            `radius :`
                This property holds the radius of the circle when the fill policy is eFixed or eFixedCrop. By default, the circle radius is 0.

            `arc :`
                This property is the way to draw a half or a quarter of the circle. When it's eLeft, only left side of the circle is rendered. When it's eLeftTop, only left top quarter is rendered.

            `size_policy :`
                Define what happens when the source image has a different size than the item.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FreeEllipse(Ellipse, Shape, Widget):
    """
    The Ellipse widget provides a colored ellipse to display.

    The free widget is the widget that is independent of the layout. It means it is stuck to other widgets. When initializing, it's necessary to provide two widgets, and the shape is drawn from one widget position to the another.
    """
    def __init__(self, arg0: Widget, arg1: Widget, **kwargs) -> None: 
        """
        Initialize the shape with bounds limited to the positions of the given widgets.


        ### Arguments:

            `start :`
                The bound corner is in the center of this given widget.

            `end :`
                The bound corner is in the center of this given widget.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FreeLine(Line, Shape, Widget, ArrowHelper, ShapeAnchorHelper):
    """
    The Line widget provides a colored line to display.

    The free widget is the widget that is independent of the layout. It means it is stuck to other widgets. When initializing, it's necessary to provide two widgets, and the shape is drawn from one widget position to the another.
    """
    def __init__(self, arg0: Widget, arg1: Widget, **kwargs) -> None: 
        """
        Initialize the shape with bounds limited to the positions of the given widgets.


        ### Arguments:

            `start :`
                The bound corner is in the center of this given widget.

            `end :`
                The bound corner is in the center of this given widget.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment : `
                This property that holds the alignment of the Line can only be LEFT, RIGHT, V_CENTER, H_CENTER , BOTTOM, TOP. By default, the Line is H_Center.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.

            `anchor_position: `
                This property holds the parametric value of the curve anchor.

            `anchor_alignment: `
                This property holds the Alignment of the curve anchor.

            `set_anchor_fn: Callable`
                Sets the function that will be called for the curve anchor.

            `invalidate_anchor: `
                Function that causes the anchor frame to be redrawn.

            `get_closest_parametric_position: `
                Function that returns the closest parametric T value to a given x,y position.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FreeRectangle(Rectangle, Shape, Widget):
    """
    The Rectangle widget provides a colored rectangle to display.

    The free widget is the widget that is independent of the layout. It means it is stuck to other widgets. When initializing, it's necessary to provide two widgets, and the shape is drawn from one widget position to the another.
    """
    def __init__(self, arg0: Widget, arg1: Widget, **kwargs) -> None: 
        """
        Initialize the shape with bounds limited to the positions of the given widgets.


        ### Arguments:

            `start :`
                The bound corner is in the center of this given widget.

            `end :`
                The bound corner is in the center of this given widget.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class FreeTriangle(Triangle, Shape, Widget):
    """
    The Triangle widget provides a colored triangle to display.

    The free widget is the widget that is independent of the layout. It means it is stuck to other widgets. When initializing, it's necessary to provide two widgets, and the shape is drawn from one widget position to the another.
    """
    def __init__(self, arg0: Widget, arg1: Widget, **kwargs) -> None: 
        """
        Initialize the shape with bounds limited to the positions of the given widgets.


        ### Arguments:

            `start :`
                The bound corner is in the center of this given widget.

            `end :`
                The bound corner is in the center of this given widget.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment : `
                This property holds the alignment of the triangle when the fill policy is ePreserveAspectFit or ePreserveAspectCrop.    By default, the triangle is centered.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class HGrid(Grid, Stack, Container, Widget):
    """
    Shortcut for Grid{eLeftToRight}. The grid grows from left to right with the widgets placed.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct a grid that grow from left to right with the widgets placed.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `column_width : `
                The width of the column. It's only possible to set it if the grid is vertical. Once it's set, the column count depends on the size of the widget.

            `row_height : `
                The height of the row. It's only possible to set it if the grid is horizontal. Once it's set, the row count depends on the size of the widget.

            `column_count : `
                The number of columns. It's only possible to set it if the grid is vertical. Once it's set, the column width depends on the widget size.

            `row_count : `
                The number of rows. It's only possible to set it if the grid is horizontal. Once it's set, the row height depends on the widget size.

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Grid(Stack, Container, Widget):
    """
    Grid is a container that arranges its child views in a grid. The grid vertical/horizontal direction is the direction the grid size growing with creating more children.
    """
    def __init__(self, arg0: Direction, **kwargs) -> None: 
        """
        Constructor.


        ### Arguments:

            `direction :`
                Determines the direction the widget grows when adding more children.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `column_width : `
                The width of the column. It's only possible to set it if the grid is vertical. Once it's set, the column count depends on the size of the widget.

            `row_height : `
                The height of the row. It's only possible to set it if the grid is horizontal. Once it's set, the row count depends on the size of the widget.

            `column_count : `
                The number of columns. It's only possible to set it if the grid is vertical. Once it's set, the column width depends on the widget size.

            `row_count : `
                The number of rows. It's only possible to set it if the grid is horizontal. Once it's set, the row height depends on the widget size.

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def column_count(self) -> int:
        """
        The number of columns. It's only possible to set it if the grid is vertical. Once it's set, the column width depends on the widget size.

        :type: int
        """
    @column_count.setter
    def column_count(self, arg1: int) -> None:
        """
        The number of columns. It's only possible to set it if the grid is vertical. Once it's set, the column width depends on the widget size.
        """
    @property
    def column_width(self) -> float:
        """
        The width of the column. It's only possible to set it if the grid is vertical. Once it's set, the column count depends on the size of the widget.

        :type: float
        """
    @column_width.setter
    def column_width(self, arg1: float) -> None:
        """
        The width of the column. It's only possible to set it if the grid is vertical. Once it's set, the column count depends on the size of the widget.
        """
    @property
    def row_count(self) -> int:
        """
        The number of rows. It's only possible to set it if the grid is horizontal. Once it's set, the row height depends on the widget size.

        :type: int
        """
    @row_count.setter
    def row_count(self, arg1: int) -> None:
        """
        The number of rows. It's only possible to set it if the grid is horizontal. Once it's set, the row height depends on the widget size.
        """
    @property
    def row_height(self) -> float:
        """
        The height of the row. It's only possible to set it if the grid is horizontal. Once it's set, the row count depends on the size of the widget.

        :type: float
        """
    @row_height.setter
    def row_height(self, arg1: float) -> None:
        """
        The height of the row. It's only possible to set it if the grid is horizontal. Once it's set, the row count depends on the size of the widget.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class HStack(Stack, Container, Widget):
    """
    Shortcut for Stack{eLeftToRight}. The widgets are placed in a row, with suitable sizes.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct a stack with the widgets placed in a row from left to right.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Image(Widget):
    """
    The Image widget displays an image.
    The source of the image is specified as a URL using the source property. By default, specifying the width and height of the item causes the image to be scaled to that size. This behavior can be changed by setting the fill_mode property, allowing the image to be stretched or scaled instead. The property alignment controls where to align the scaled image.
    """
    @typing.overload
    def __init__(self, arg0: str, **kwargs) -> None: 
        """
        Construct image with given url. If the url is empty, it gets the image URL from styling.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment : `
                This property holds the alignment of the image when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the image is centered.

            `fill_policy : `
                Define what happens when the source image has a different size than the item.

            `pixel_aligned : `
                Prevents image blurring when it's placed to fractional position (like x=0.5, y=0.5)

            `progress_changed_fn : `
                The progress of the image loading.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.

        Construct image with given url. If the url is empty, it gets the image URL from styling.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment : `
                This property holds the alignment of the image when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the image is centered.

            `fill_policy : `
                Define what happens when the source image has a different size than the item.

            `pixel_aligned : `
                Prevents image blurring when it's placed to fractional position (like x=0.5, y=0.5)

            `progress_changed_fn : `
                The progress of the image loading.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @typing.overload
    def __init__(self, **kwargs) -> None: ...
    def set_progress_changed_fn(self, fn: typing.Callable[[float], None]) -> None: 
        """
        The progress of the image loading.
        """
    @property
    def alignment(self) -> Alignment:
        """
        This property holds the alignment of the image when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the image is centered.

        :type: Alignment
        """
    @alignment.setter
    def alignment(self, arg1: Alignment) -> None:
        """
        This property holds the alignment of the image when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the image is centered.
        """
    @property
    def fill_policy(self) -> FillPolicy:
        """
        Define what happens when the source image has a different size than the item.

        :type: FillPolicy
        """
    @fill_policy.setter
    def fill_policy(self, arg1: FillPolicy) -> None:
        """
        Define what happens when the source image has a different size than the item.
        """
    @property
    def pixel_aligned(self) -> bool:
        """
        Prevents image blurring when it's placed to fractional position (like x=0.5, y=0.5)

        :type: bool
        """
    @pixel_aligned.setter
    def pixel_aligned(self, arg1: bool) -> None:
        """
        Prevents image blurring when it's placed to fractional position (like x=0.5, y=0.5)
        """
    @property
    def progress(self) -> float:
        """
        The progress of the image loading.

        :type: float
        """
    @property
    def source_url(self) -> str:
        """
        This property holds the image URL. It can be an
        omni:
        file:

        :type: str
        """
    @source_url.setter
    def source_url(self, arg1: str) -> None:
        """
        This property holds the image URL. It can be an
        omni:
        file:
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ImageProvider():
    """
    ImageProvider class, the goal of this class is to provide ImGui reference for the image to be rendered.
    """
    def __init__(self, **kwargs) -> None: 
        """
        doc
        """
    def destroy(self) -> None: ...
    def get_managed_resource(self) -> omni.gpu_foundation_factory._gpu_foundation_factory.RpResource: ...
    @typing.overload
    def set_image_data(self, arg0: capsule, arg1: int, arg2: int, arg3: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat) -> None: ...
    @typing.overload
    def set_image_data(self, rp_resource: omni.gpu_foundation_factory._gpu_foundation_factory.RpResource, presentation_key: int = 0, metadata: omni.kit.renderer_capture._renderer_capture.Metadata = None) -> None: ...
    @property
    def height(self) -> int:
        """
        Gets image height.

        :type: int
        """
    @property
    def is_reference_valid(self) -> bool:
        """
        Returns true if ImGui reference is valid, false otherwise.

        :type: bool
        """
    @property
    def width(self) -> int:
        """
        Gets image width.

        :type: int
        """
    pass
class ImageWithProvider(Widget):
    """
    The Image widget displays an image.
    The source of the image is specified as a URL using the source property. By default, specifying the width and height of the item causes the image to be scaled to that size. This behavior can be changed by setting the fill_mode property, allowing the image to be stretched or scaled instead. The property alignment controls where to align the scaled image.
    """
    @typing.overload
    def __init__(self, arg0: ImageProvider, **kwargs) -> None: 
        """
        Construct image with given ImageProvider. If the ImageProvider is nullptr, it gets the image URL from styling.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment : `
                This property holds the alignment of the image when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the image is centered.

            `fill_policy : `
                Define what happens when the source image has a different size than the item.

            `pixel_aligned : `
                Prevents image blurring when it's placed to fractional position (like x=0.5, y=0.5)

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @typing.overload
    def __init__(self, arg0: str, **kwargs) -> None: ...
    @typing.overload
    def __init__(self, **kwargs) -> None: ...
    def prepare_draw(self, width: float, height: float) -> None: 
        """
        Force call `ImageProvider::prepareDraw` to ensure the next draw call the image is loaded. It can be used to load the image for a hidden widget or to set the rasterization resolution.
        """
    @property
    def alignment(self) -> Alignment:
        """
        This property holds the alignment of the image when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the image is centered.

        :type: Alignment
        """
    @alignment.setter
    def alignment(self, arg1: Alignment) -> None:
        """
        This property holds the alignment of the image when the fill policy is ePreserveAspectFit or ePreserveAspectCrop. By default, the image is centered.
        """
    @property
    def fill_policy(self) -> IwpFillPolicy:
        """
        Define what happens when the source image has a different size than the item.

        :type: IwpFillPolicy
        """
    @fill_policy.setter
    def fill_policy(self, arg1: IwpFillPolicy) -> None:
        """
        Define what happens when the source image has a different size than the item.
        """
    @property
    def pixel_aligned(self) -> bool:
        """
        Prevents image blurring when it's placed to fractional position (like x=0.5, y=0.5)

        :type: bool
        """
    @pixel_aligned.setter
    def pixel_aligned(self, arg1: bool) -> None:
        """
        Prevents image blurring when it's placed to fractional position (like x=0.5, y=0.5)
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Inspector():
    """
    Inspector is the helper to check the internal state of the widget. It's not recommended to use it for the routine UI.
    """
    @staticmethod
    def begin_computed_height_metric() -> None: 
        """
        Start counting how many times Widget::setComputedHeight is called
        """
    @staticmethod
    def begin_computed_width_metric() -> None: 
        """
        Start counting how many times Widget::setComputedWidth is called
        """
    @staticmethod
    def end_computed_height_metric() -> int: 
        """
        Start counting how many times Widget::setComputedHeight is called and return the number
        """
    @staticmethod
    def end_computed_width_metric() -> int: 
        """
        Start counting how many times Widget::setComputedWidth is called and return the number
        """
    @staticmethod
    def get_children(widget: Widget) -> typing.List[Widget]: 
        """
        Get the children of the given Widget.
        """
    @staticmethod
    def get_resolved_style(*args, **kwargs) -> typing.Any: 
        """
        Get the resolved style of the given Widget.
        """
    @staticmethod
    def get_stored_font_atlases() -> typing.List[typing.Tuple[str, int]]: 
        """
        Provides the information about font atlases
        """
    pass
class IntDrag(IntSlider, AbstractSlider, Widget, ValueModelHelper):
    """
    The drag widget that looks like a field but it's possible to change the value with dragging.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Constructs IntDrag.


        ### Arguments:

            `model :`
                The widget's model. If the model is not assigned, the default model is created.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `step : `
                This property controls the steping speed on the drag, its float to enable slower speed, but of course the value on the Control are still integer.

            `min : `
                This property holds the slider's minimum value.

            `max : `
                This property holds the slider's maximum value.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def step(self) -> float:
        """
        This property controls the steping speed on the drag, its float to enable slower speed, but of course the value on the Control are still integer.

        :type: float
        """
    @step.setter
    def step(self, arg1: float) -> None:
        """
        This property controls the steping speed on the drag, its float to enable slower speed, but of course the value on the Control are still integer.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class IntField(AbstractField, Widget, ValueModelHelper):
    """
    The IntField widget is a one-line text editor with a string model.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Construct IntField.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class IntSlider(AbstractSlider, Widget, ValueModelHelper):
    """
    The slider is the classic widget for controlling a bounded value. It lets the user move a slider handle along a horizontal groove and translates the handle's position into an integer value within the legal range.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Constructs IntSlider.


        ### Arguments:

            `model :`
                The widget's model. If the model is not assigned, the default model is created.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `min : `
                This property holds the slider's minimum value.

            `max : `
                This property holds the slider's maximum value.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def max(self) -> int:
        """
        This property holds the slider's maximum value.

        :type: int
        """
    @max.setter
    def max(self, arg1: int) -> None:
        """
        This property holds the slider's maximum value.
        """
    @property
    def min(self) -> int:
        """
        This property holds the slider's minimum value.

        :type: int
        """
    @min.setter
    def min(self, arg1: int) -> None:
        """
        This property holds the slider's minimum value.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class InvisibleButton(Widget):
    """
    The InvisibleButton widget provides a transparent command button.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `clicked_fn : Callable[[], None]`
                Sets the function that will be called when when the button is activated (i.e., pressed down then released while the mouse cursor is inside the button).

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    def call_clicked_fn(self) -> None: 
        """
        Sets the function that will be called when when the button is activated (i.e., pressed down then released while the mouse cursor is inside the button).
        """
    def has_clicked_fn(self) -> bool: 
        """
        Sets the function that will be called when when the button is activated (i.e., pressed down then released while the mouse cursor is inside the button).
        """
    def set_clicked_fn(self, fn: typing.Callable[[], None]) -> None: 
        """
        Sets the function that will be called when when the button is activated (i.e., pressed down then released while the mouse cursor is inside the button).
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ItemModelHelper():
    """
    The ItemModelHelper class provides the basic functionality for item widget classes.
    """
    @property
    def model(self) -> AbstractItemModel:
        """
        Returns the current model.

        :type: AbstractItemModel
        """
    @model.setter
    def model(self, arg1: AbstractItemModel) -> None:
        """
        Returns the current model.
        """
    pass
class IwpFillPolicy():
    """
    Members:

      IWP_STRETCH

      IWP_PRESERVE_ASPECT_FIT

      IWP_PRESERVE_ASPECT_CROP
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    IWP_PRESERVE_ASPECT_CROP: omni.ui._ui.IwpFillPolicy # value = <IwpFillPolicy.IWP_PRESERVE_ASPECT_CROP: 2>
    IWP_PRESERVE_ASPECT_FIT: omni.ui._ui.IwpFillPolicy # value = <IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT: 1>
    IWP_STRETCH: omni.ui._ui.IwpFillPolicy # value = <IwpFillPolicy.IWP_STRETCH: 0>
    __members__: dict # value = {'IWP_STRETCH': <IwpFillPolicy.IWP_STRETCH: 0>, 'IWP_PRESERVE_ASPECT_FIT': <IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT: 1>, 'IWP_PRESERVE_ASPECT_CROP': <IwpFillPolicy.IWP_PRESERVE_ASPECT_CROP: 2>}
    pass
class Label(Widget):
    """
    The Label widget provides a text to display.
    Label is used for displaying text. No additional to Widget user interaction functionality is provided.
    """
    def __init__(self, arg0: str, **kwargs) -> None: 
        """
        Create a label with the given text.


        ### Arguments:

            `text :`
                The text for the label.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment : `
                This property holds the alignment of the label's contents. By default, the contents of the label are left-aligned and vertically-centered.

            `word_wrap : `
                This property holds the label's word-wrapping policy If this property is true then label text is wrapped where necessary at word-breaks; otherwise it is not wrapped at all. By default, word wrap is disabled.

            `elided_text : `
                When the text of a big length has to be displayed in a small area, it can be useful to give the user a visual hint that not all text is visible. Label can elide text that doesn't fit in the area. When this property is true, Label elides the middle of the last visible line and replaces it with "...".

            `elided_text_str : `
                Customized elidedText string when elidedText is True, default is ....
            `hide_text_after_hash : `
                Hide anything after a '##' string or not
            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def alignment(self) -> Alignment:
        """
        This property holds the alignment of the label's contents. By default, the contents of the label are left-aligned and vertically-centered.

        :type: Alignment
        """
    @alignment.setter
    def alignment(self, arg1: Alignment) -> None:
        """
        This property holds the alignment of the label's contents. By default, the contents of the label are left-aligned and vertically-centered.
        """
    @property
    def elided_text(self) -> bool:
        """
        When the text of a big length has to be displayed in a small area, it can be useful to give the user a visual hint that not all text is visible. Label can elide text that doesn't fit in the area. When this property is true, Label elides the middle of the last visible line and replaces it with "...".

        :type: bool
        """
    @elided_text.setter
    def elided_text(self, arg1: bool) -> None:
        """
        When the text of a big length has to be displayed in a small area, it can be useful to give the user a visual hint that not all text is visible. Label can elide text that doesn't fit in the area. When this property is true, Label elides the middle of the last visible line and replaces it with "...".
        """
    @property
    def elided_text_str(self) -> str:
        """
        Customized elidedText string when elidedText is True, default is ....

        :type: str
        """
    @elided_text_str.setter
    def elided_text_str(self, arg1: str) -> None:
        """
        Customized elidedText string when elidedText is True, default is ....
        """
    @property
    def exact_content_height(self) -> float:
        """
        Return the exact height of the content of this label. Computed content height is a size hint and may be bigger than the text in the label.

        :type: float
        """
    @property
    def exact_content_width(self) -> float:
        """
        Return the exact width of the content of this label. Computed content width is a size hint and may be bigger than the text in the label.

        :type: float
        """
    @property
    def hide_text_after_hash(self) -> bool:
        """
        Hide anything after a '##' string or not

        :type: bool
        """
    @hide_text_after_hash.setter
    def hide_text_after_hash(self, arg1: bool) -> None:
        """
        Hide anything after a '##' string or not
        """
    @property
    def text(self) -> str:
        """
        This property holds the label's text.

        :type: str
        """
    @text.setter
    def text(self, arg1: str) -> None:
        """
        This property holds the label's text.
        """
    @property
    def word_wrap(self) -> bool:
        """
        This property holds the label's word-wrapping policy If this property is true then label text is wrapped where necessary at word-breaks; otherwise it is not wrapped at all. By default, word wrap is disabled.

        :type: bool
        """
    @word_wrap.setter
    def word_wrap(self, arg1: bool) -> None:
        """
        This property holds the label's word-wrapping policy If this property is true then label text is wrapped where necessary at word-breaks; otherwise it is not wrapped at all. By default, word wrap is disabled.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Length():
    """
    OMNI.UI has several different units for expressing a length.
    Many widget properties take "Length" values, such as width, height, minWidth, minHeight, etc. Pixel is the absolute length unit. Percent and Fraction are relative length units, and they specify a length relative to the parent length. Relative length units are scaled with the parent.
    """
    def __add__(self, value: float) -> float: ...
    def __float__(self) -> float: ...
    def __iadd__(self, value: float) -> float: ...
    def __imul__(self, value: float) -> Length: ...
    @staticmethod
    @typing.overload
    def __init__(*args, **kwargs) -> typing.Any: 
        """
        Construct Length.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    @typing.overload
    def __init__(self, arg0: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: int) -> None: ...
    def __isub__(self, value: float) -> float: ...
    def __itruediv__(self, value: float) -> Length: ...
    def __mul__(self, value: float) -> Length: ...
    def __radd__(self, value: float) -> float: ...
    def __repr__(self) -> str: ...
    def __rmul__(self, value: float) -> Length: ...
    def __rsub__(self, value: float) -> float: ...
    def __rtruediv__(self, value: float) -> Length: ...
    def __str__(self) -> str: ...
    def __sub__(self, value: float) -> float: ...
    def __truediv__(self, value: float) -> Length: ...
    @property
    def unit(self) -> typing.Any:
        """
        (:obj:`.UnitType.`) Unit.

        :type: typing.Any
        """
    @unit.setter
    def unit(*args, **kwargs) -> None:
        """
        (:obj:`.UnitType.`) Unit.
        """
    @property
    def value(self) -> float:
        """
        (float) Value

        :type: float
        """
    @value.setter
    def value(self, arg0: float) -> None:
        """
        (float) Value
        """
    pass
class Line(Shape, Widget, ArrowHelper, ShapeAnchorHelper):
    """
    The Line widget provides a colored line to display.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructs Line.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment : `
                This property that holds the alignment of the Line can only be LEFT, RIGHT, V_CENTER, H_CENTER , BOTTOM, TOP. By default, the Line is H_Center.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.

            `anchor_position: `
                This property holds the parametric value of the curve anchor.

            `anchor_alignment: `
                This property holds the Alignment of the curve anchor.

            `set_anchor_fn: Callable`
                Sets the function that will be called for the curve anchor.

            `invalidate_anchor: `
                Function that causes the anchor frame to be redrawn.

            `get_closest_parametric_position: `
                Function that returns the closest parametric T value to a given x,y position.
        """
    @property
    def alignment(self) -> Alignment:
        """
        This property that holds the alignment of the Line can only be LEFT, RIGHT, V_CENTER, H_CENTER , BOTTOM, TOP. By default, the Line is H_Center.

        :type: Alignment
        """
    @alignment.setter
    def alignment(self, arg1: Alignment) -> None:
        """
        This property that holds the alignment of the Line can only be LEFT, RIGHT, V_CENTER, H_CENTER , BOTTOM, TOP. By default, the Line is H_Center.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class MainWindow():
    """
    The MainWindow class represents Main Window for the Application, draw optional MainMenuBar and StatusBar.
    """
    def __init__(self, show_foreground: bool = False, **kwargs) -> None: 
        """
        Construct the main window, add it to the underlying windowing system, and makes it appear.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    def set_active(self, active: bool, show_foreground: bool = True) -> None: 
        """
        Set whether the MainWindow is in an active state
        """
    @property
    def cpp_status_bar_enabled(self) -> bool:
        """
        Workaround to reserve space for C++ status bar.

        :type: bool
        """
    @cpp_status_bar_enabled.setter
    def cpp_status_bar_enabled(self, arg1: bool) -> None:
        """
        Workaround to reserve space for C++ status bar.
        """
    @property
    def main_frame(self) -> Frame:
        """
        This represents Styling opportunity for the Window background.

        :type: Frame
        """
    @property
    def main_menu_bar(self) -> MenuBar:
        """
        The main MenuBar for the application.

        :type: MenuBar
        """
    @property
    def show_foreground(self) -> bool:
        """
        When show_foreground is True, MainWindow prevents other windows from showing.

        :type: bool
        """
    @show_foreground.setter
    def show_foreground(self, arg1: bool) -> None:
        """
        When show_foreground is True, MainWindow prevents other windows from showing.
        """
    @property
    def status_bar_frame(self) -> Frame:
        """
        The StatusBar Frame is empty by default and is meant to be filled by other part of the system.

        :type: Frame
        """
    pass
class MenuBar(Menu, Stack, Container, Widget, MenuHelper):
    """
    The MenuBar class provides a MenuBar at the top of the Window, could also be the MainMenuBar of the MainWindow.
    it can only contain Menu, at the moment there is no way to remove item appart from clearing it all together
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct MenuBar.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `tearable : bool`
                The ability to tear the window off.

            `shown_changed_fn : `
                If the pulldown menu is shown on the screen.

            `teared_changed_fn : `
                If the window is teared off.

            `on_build_fn : `
                Called to re-create new children.

            `text : str`
                This property holds the menu's text.

            `hotkey_text : str`
                This property holds the menu's hotkey text.

            `checkable : bool`
                This property holds whether this menu item is checkable. A checkable item is one which has an on/off state.

            `hide_on_click : bool`
                Hide or keep the window when the user clicked this item.

            `delegate : MenuDelegate`
                The delegate that generates a widget per menu item.

            `triggered_fn : void`
                Sets the function that is called when an action is activated by the user; for example, when the user clicks a menu option, or presses an action's shortcut key combination.

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class MenuItemCollection(Menu, Stack, Container, Widget, MenuHelper):
    """
    The MenuItemCollection is the menu that unchecks children when one of them is checked.
    """
    def __init__(self, text: str = '', **kwargs) -> None: 
        """
        Construct MenuItemCollection.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `tearable : bool`
                The ability to tear the window off.

            `shown_changed_fn : `
                If the pulldown menu is shown on the screen.

            `teared_changed_fn : `
                If the window is teared off.

            `on_build_fn : `
                Called to re-create new children.

            `text : str`
                This property holds the menu's text.

            `hotkey_text : str`
                This property holds the menu's hotkey text.

            `checkable : bool`
                This property holds whether this menu item is checkable. A checkable item is one which has an on/off state.

            `hide_on_click : bool`
                Hide or keep the window when the user clicked this item.

            `delegate : MenuDelegate`
                The delegate that generates a widget per menu item.

            `triggered_fn : void`
                Sets the function that is called when an action is activated by the user; for example, when the user clicks a menu option, or presses an action's shortcut key combination.

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Menu(Stack, Container, Widget, MenuHelper):
    """
    The Menu class provides a menu widget for use in menu bars, context menus, and other popup menus.
    It can be either a pull-down menu in a menu bar or a standalone context menu. Pull-down menus are shown by the menu bar when the user clicks on the respective item. Context menus are usually invoked by some special keyboard key or by right-clicking.
    """
    def __init__(self, text: str = '', **kwargs) -> None: 
        """
        Construct Menu.


        ### Arguments:

            `text :`
                The text for the menu.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `tearable : bool`
                The ability to tear the window off.

            `shown_changed_fn : `
                If the pulldown menu is shown on the screen.

            `teared_changed_fn : `
                If the window is teared off.

            `on_build_fn : `
                Called to re-create new children.

            `text : str`
                This property holds the menu's text.

            `hotkey_text : str`
                This property holds the menu's hotkey text.

            `checkable : bool`
                This property holds whether this menu item is checkable. A checkable item is one which has an on/off state.

            `hide_on_click : bool`
                Hide or keep the window when the user clicked this item.

            `delegate : MenuDelegate`
                The delegate that generates a widget per menu item.

            `triggered_fn : void`
                Sets the function that is called when an action is activated by the user; for example, when the user clicks a menu option, or presses an action's shortcut key combination.

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    def call_on_build_fn(self) -> None: 
        """
        Called to re-create new children.
        """
    @staticmethod
    def get_current() -> Menu: 
        """
        Return the menu that is currently shown.
        """
    def has_on_build_fn(self) -> bool: 
        """
        Called to re-create new children.
        """
    def hide(self) -> None: 
        """
        Close the menu window. It only works for pop-up context menu and for teared off menu.
        """
    def invalidate(self) -> None: 
        """
        Make Menu dirty so onBuild will be executed to replace the children.
        """
    def set_on_build_fn(self, fn: typing.Callable[[], None]) -> None: 
        """
        Called to re-create new children.
        """
    def set_shown_changed_fn(self, fn: typing.Callable[[bool], None]) -> None: 
        """
        If the pulldown menu is shown on the screen.
        """
    def set_teared_changed_fn(self, fn: typing.Callable[[bool], None]) -> None: 
        """
        If the window is teared off.
        """
    def show(self) -> None: 
        """
        Create a popup window and show the menu in it. It's usually used for context menus that are typically invoked by some special keyboard key or by right-clicking.
        """
    def show_at(self, arg0: float, arg1: float) -> None: 
        """
        Create a popup window and show the menu in it. This enable to popup the menu at specific position. X and Y are in points to make it easier to the Python users.
        """
    def tear_at(self, arg0: float, arg1: float) -> None: 
        """
        Create a popup window and show the menu in it. This tear the menu at specific position. X and Y are in points to make it easier to the Python users.
        """
    @property
    def shown(self) -> bool:
        """
        If the pulldown menu is shown on the screen.

        :type: bool
        """
    @property
    def tearable(self) -> bool:
        """
        The ability to tear the window off.

        :type: bool
        """
    @tearable.setter
    def tearable(self, arg1: bool) -> None:
        """
        The ability to tear the window off.
        """
    @property
    def teared(self) -> bool:
        """
        If the window is teared off.

        :type: bool
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class MenuDelegate():
    """
    MenuDelegate is used to generate widgets that represent the menu item.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `on_build_item : `
                Called to create a new item.

            `on_build_title : `
                Called to create a new title.

            `on_build_status : `
                Called to create a new widget on the bottom of the window.

            `propagate : `
                Determine if Menu children should use this delegate when they don't have the own one.
        """
    @staticmethod
    def build_item(*args, **kwargs) -> typing.Any: 
        """
        This method must be reimplemented to generate custom item.
        """
    @staticmethod
    def build_status(*args, **kwargs) -> typing.Any: 
        """
        This method must be reimplemented to generate custom widgets on the bottom of the window.
        """
    @staticmethod
    def build_title(*args, **kwargs) -> typing.Any: 
        """
        This method must be reimplemented to generate custom title.
        """
    @staticmethod
    def call_on_build_item_fn(*args, **kwargs) -> typing.Any: 
        """
        Called to create a new item.
        """
    @staticmethod
    def call_on_build_status_fn(*args, **kwargs) -> typing.Any: 
        """
        Called to create a new widget on the bottom of the window.
        """
    @staticmethod
    def call_on_build_title_fn(*args, **kwargs) -> typing.Any: 
        """
        Called to create a new title.
        """
    def has_on_build_item_fn(self) -> bool: 
        """
        Called to create a new item.
        """
    def has_on_build_status_fn(self) -> bool: 
        """
        Called to create a new widget on the bottom of the window.
        """
    def has_on_build_title_fn(self) -> bool: 
        """
        Called to create a new title.
        """
    @staticmethod
    def set_default_delegate(delegate: MenuDelegate) -> None: 
        """
        Set the default delegate to use it when the item doesn't have a delegate.
        """
    @staticmethod
    def set_on_build_item_fn(*args, **kwargs) -> typing.Any: 
        """
        Called to create a new item.
        """
    @staticmethod
    def set_on_build_status_fn(*args, **kwargs) -> typing.Any: 
        """
        Called to create a new widget on the bottom of the window.
        """
    @staticmethod
    def set_on_build_title_fn(*args, **kwargs) -> typing.Any: 
        """
        Called to create a new title.
        """
    @property
    def propagate(self) -> bool:
        """
        :type: bool
        """
    @propagate.setter
    def propagate(self, arg1: bool) -> None:
        pass
    pass
class MenuItem(Widget, MenuHelper):
    """
    A MenuItem represents the items the Menu consists of.
    MenuItem can be inserted only once in the menu.
    """
    def __init__(self, arg0: str, **kwargs) -> None: 
        """
        Construct MenuItem.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `text : str`
                This property holds the menu's text.

            `hotkey_text : str`
                This property holds the menu's hotkey text.

            `checkable : bool`
                This property holds whether this menu item is checkable. A checkable item is one which has an on/off state.

            `hide_on_click : bool`
                Hide or keep the window when the user clicked this item.

            `delegate : MenuDelegate`
                The delegate that generates a widget per menu item.

            `triggered_fn : void`
                Sets the function that is called when an action is activated by the user; for example, when the user clicks a menu option, or presses an action's shortcut key combination.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class MenuHelper():
    """
    The helper class for the menu that draws the menu line.
    """
    def call_triggered_fn(self) -> None: 
        """
        Sets the function that is called when an action is activated by the user; for example, when the user clicks a menu option, or presses an action's shortcut key combination.
        """
    def has_triggered_fn(self) -> bool: 
        """
        Sets the function that is called when an action is activated by the user; for example, when the user clicks a menu option, or presses an action's shortcut key combination.
        """
    def set_triggered_fn(self, fn: typing.Callable[[], None]) -> None: 
        """
        Sets the function that is called when an action is activated by the user; for example, when the user clicks a menu option, or presses an action's shortcut key combination.
        """
    @property
    def checkable(self) -> bool:
        """
        This property holds whether this menu item is checkable. A checkable item is one which has an on/off state.

        :type: bool
        """
    @checkable.setter
    def checkable(self, arg1: bool) -> None:
        """
        This property holds whether this menu item is checkable. A checkable item is one which has an on/off state.
        """
    @property
    def delegate(self) -> MenuDelegate:
        """
        :type: MenuDelegate
        """
    @delegate.setter
    def delegate(self, arg1: MenuDelegate) -> None:
        pass
    @property
    def hide_on_click(self) -> bool:
        """
        Hide or keep the window when the user clicked this item.

        :type: bool
        """
    @hide_on_click.setter
    def hide_on_click(self, arg1: bool) -> None:
        """
        Hide or keep the window when the user clicked this item.
        """
    @property
    def hotkey_text(self) -> str:
        """
        This property holds the menu's hotkey text.

        :type: str
        """
    @hotkey_text.setter
    def hotkey_text(self, arg1: str) -> None:
        """
        This property holds the menu's hotkey text.
        """
    @property
    def menu_compatibility(self) -> bool:
        """
        :type: bool
        """
    @menu_compatibility.setter
    def menu_compatibility(self, arg1: bool) -> None:
        pass
    @property
    def text(self) -> str:
        """
        This property holds the menu's text.

        :type: str
        """
    @text.setter
    def text(self, arg1: str) -> None:
        """
        This property holds the menu's text.
        """
    pass
class MultiFloatDragField(AbstractMultiField, Widget, ItemModelHelper):
    """
    MultiFloatDragField is the widget that has a sub widget (FloatDrag) per model item.
    It's handy to use it for multi-component data, like for example, float3 or color.
    """
    @typing.overload
    def __init__(self, **kwargs) -> None: 
        """
        Constructs MultiFloatDragField.


        ### Arguments:

            `model :`
                The widget's model. If the model is not assigned, the default model is created.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `min : `
                This property holds the drag's minimum value.

            `max : `
                This property holds the drag's maximum value.

            `step : `
                This property controls the steping speed on the drag.

            `column_count : `
                The max number of fields in a line.

            `h_spacing : `
                Sets a non-stretchable horizontal space in pixels between child fields.

            `v_spacing : `
                Sets a non-stretchable vertical space in pixels between child fields.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @typing.overload
    def __init__(self, arg0: AbstractItemModel, **kwargs) -> None: ...
    @typing.overload
    def __init__(self, *args, **kwargs) -> None: ...
    @property
    def max(self) -> float:
        """
        This property holds the drag's maximum value.

        :type: float
        """
    @max.setter
    def max(self, arg1: float) -> None:
        """
        This property holds the drag's maximum value.
        """
    @property
    def min(self) -> float:
        """
        This property holds the drag's minimum value.

        :type: float
        """
    @min.setter
    def min(self, arg1: float) -> None:
        """
        This property holds the drag's minimum value.
        """
    @property
    def step(self) -> float:
        """
        This property controls the steping speed on the drag.

        :type: float
        """
    @step.setter
    def step(self, arg1: float) -> None:
        """
        This property controls the steping speed on the drag.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class MultiFloatField(AbstractMultiField, Widget, ItemModelHelper):
    """
    MultiFloatField is the widget that has a sub widget (FloatField) per model item.
    It's handy to use it for multi-component data, like for example, float3 or color.
    """
    @typing.overload
    def __init__(self, **kwargs) -> None: 
        """
        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `column_count : `
                The max number of fields in a line.

            `h_spacing : `
                Sets a non-stretchable horizontal space in pixels between child fields.

            `v_spacing : `
                Sets a non-stretchable vertical space in pixels between child fields.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @typing.overload
    def __init__(self, arg0: AbstractItemModel, **kwargs) -> None: ...
    @typing.overload
    def __init__(self, *args, **kwargs) -> None: ...
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class MultiIntDragField(AbstractMultiField, Widget, ItemModelHelper):
    """
    MultiIntDragField is the widget that has a sub widget (IntDrag) per model item.
    It's handy to use it for multi-component data, like for example, int3.
    """
    @typing.overload
    def __init__(self, **kwargs) -> None: 
        """
        Constructs MultiIntDragField.


        ### Arguments:

            `model :`
                The widget's model. If the model is not assigned, the default model is created.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `min : `
                This property holds the drag's minimum value.

            `max : `
                This property holds the drag's maximum value.

            `step : `
                This property controls the steping speed on the drag.

            `column_count : `
                The max number of fields in a line.

            `h_spacing : `
                Sets a non-stretchable horizontal space in pixels between child fields.

            `v_spacing : `
                Sets a non-stretchable vertical space in pixels between child fields.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @typing.overload
    def __init__(self, arg0: AbstractItemModel, **kwargs) -> None: ...
    @typing.overload
    def __init__(self, *args, **kwargs) -> None: ...
    @property
    def max(self) -> int:
        """
        This property holds the drag's maximum value.

        :type: int
        """
    @max.setter
    def max(self, arg1: int) -> None:
        """
        This property holds the drag's maximum value.
        """
    @property
    def min(self) -> int:
        """
        This property holds the drag's minimum value.

        :type: int
        """
    @min.setter
    def min(self, arg1: int) -> None:
        """
        This property holds the drag's minimum value.
        """
    @property
    def step(self) -> float:
        """
        This property controls the steping speed on the drag.

        :type: float
        """
    @step.setter
    def step(self, arg1: float) -> None:
        """
        This property controls the steping speed on the drag.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class MultiIntField(AbstractMultiField, Widget, ItemModelHelper):
    """
    MultiIntField is the widget that has a sub widget (IntField) per model item.
    It's handy to use it for multi-component data, like for example, int3.
    """
    @typing.overload
    def __init__(self, **kwargs) -> None: 
        """
        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `column_count : `
                The max number of fields in a line.

            `h_spacing : `
                Sets a non-stretchable horizontal space in pixels between child fields.

            `v_spacing : `
                Sets a non-stretchable vertical space in pixels between child fields.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @typing.overload
    def __init__(self, arg0: AbstractItemModel, **kwargs) -> None: ...
    @typing.overload
    def __init__(self, *args, **kwargs) -> None: ...
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class MultiStringField(AbstractMultiField, Widget, ItemModelHelper):
    """
    MultiStringField is the widget that has a sub widget (StringField) per model item.
    It's handy to use it for string arrays.
    """
    @typing.overload
    def __init__(self, **kwargs) -> None: 
        """
        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `column_count : `
                The max number of fields in a line.

            `h_spacing : `
                Sets a non-stretchable horizontal space in pixels between child fields.

            `v_spacing : `
                Sets a non-stretchable vertical space in pixels between child fields.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @typing.overload
    def __init__(self, arg0: AbstractItemModel, **kwargs) -> None: ...
    @typing.overload
    def __init__(self, *args, **kwargs) -> None: ...
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class OffsetLine(FreeLine, Line, Shape, Widget, ArrowHelper, ShapeAnchorHelper):
    """
    The free widget is the widget that is independent of the layout. It draws the line stuck to the bounds of other widgets.
    """
    def __init__(self, arg0: Widget, arg1: Widget, **kwargs) -> None: ...
    @property
    def bound_offset(self) -> float:
        """
        The offset from the bounds of the widgets this line is stuck to.

        :type: float
        """
    @bound_offset.setter
    def bound_offset(self, arg1: float) -> None:
        """
        The offset from the bounds of the widgets this line is stuck to.
        """
    @property
    def offset(self) -> float:
        """
        The offset to the direction of the line normal.

        :type: float
        """
    @offset.setter
    def offset(self, arg1: float) -> None:
        """
        The offset to the direction of the line normal.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Percent(Length):
    """
    Percent is the length in percents from the parent widget.
    """
    def __init__(self, value: float) -> None: 
        """
        Construct Percent.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    pass
class Pixel(Length):
    """
    Pixel length is exact length in pixels.
    """
    def __init__(self, value: float) -> None: 
        """
        Construct Pixel.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    pass
class Placer(Container, Widget):
    """
    The Placer class place a single widget to a particular position based on the offet.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct Placer.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `offset_x : toLength`
                offsetX defines the offset placement for the child widget relative to the Placer

            `offset_y : toLength`
                offsetY defines the offset placement for the child widget relative to the Placer

            `draggable : bool`
                Provides a convenient way to make an item draggable.

            `drag_axis : Axis`
                Sets if dragging can be horizontally or vertically.

            `stable_size : bool`
                The placer size depends on the position of the child when false.

            `raster_policy : `
                Determine how the content of the frame should be rasterized.

            `offset_x_changed_fn : Callable[[ui.Length], None]`
                offsetX defines the offset placement for the child widget relative to the Placer

            `offset_y_changed_fn : Callable[[ui.Length], None]`
                offsetY defines the offset placement for the child widget relative to the Placer

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    def invalidate_raster(self) -> None: 
        """
        This method regenerates the raster image of the widget, even if the widget's content has not changed. This can be used with both the eOnDemand and eAuto raster policies, and is used to update the content displayed in the widget. Note that this operation may be resource-intensive, and should be used sparingly.
        """
    def set_offset_x_changed_fn(self, arg0: typing.Callable[[Length], None]) -> None: 
        """
        offsetX defines the offset placement for the child widget relative to the Placer
        """
    def set_offset_y_changed_fn(self, arg0: typing.Callable[[Length], None]) -> None: 
        """
        offsetY defines the offset placement for the child widget relative to the Placer
        """
    @property
    def drag_axis(self) -> Axis:
        """
        Sets if dragging can be horizontally or vertically.

        :type: Axis
        """
    @drag_axis.setter
    def drag_axis(self, arg1: Axis) -> None:
        """
        Sets if dragging can be horizontally or vertically.
        """
    @property
    def draggable(self) -> bool:
        """
        Provides a convenient way to make an item draggable.

        :type: bool
        """
    @draggable.setter
    def draggable(self, arg1: bool) -> None:
        """
        Provides a convenient way to make an item draggable.
        """
    @property
    def frames_to_start_drag(self) -> int:
        """
        The placer size depends on the position of the child when false.

        :type: int
        """
    @frames_to_start_drag.setter
    def frames_to_start_drag(self, arg1: int) -> None:
        """
        The placer size depends on the position of the child when false.
        """
    @property
    def offset_x(self) -> Length:
        """
        offsetX defines the offset placement for the child widget relative to the Placer

        :type: Length
        """
    @offset_x.setter
    def offset_x(self, arg1: handle) -> None:
        """
        offsetX defines the offset placement for the child widget relative to the Placer
        """
    @property
    def offset_y(self) -> Length:
        """
        offsetY defines the offset placement for the child widget relative to the Placer

        :type: Length
        """
    @offset_y.setter
    def offset_y(self, arg1: handle) -> None:
        """
        offsetY defines the offset placement for the child widget relative to the Placer
        """
    @property
    def raster_policy(self) -> RasterPolicy:
        """
        Determine how the content of the frame should be rasterized.

        :type: RasterPolicy
        """
    @raster_policy.setter
    def raster_policy(self, arg1: RasterPolicy) -> None:
        """
        Determine how the content of the frame should be rasterized.
        """
    @property
    def stable_size(self) -> bool:
        """
        The placer size depends on the position of the child when false.

        :type: bool
        """
    @stable_size.setter
    def stable_size(self, arg1: bool) -> None:
        """
        The placer size depends on the position of the child when false.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Plot(Widget):
    """
    The Plot widget provides a line/histogram to display.
    """
    def __init__(self, type: Type = Type.LINE, scale_min: float = 3.4028234663852886e+38, scale_max: float = 3.4028234663852886e+38, *args, **kwargs) -> None: 
        """
        Construct Plot.


        ### Arguments:

            `type :`
                The type of the image, can be line or histogram.

            `scaleMin :`
                The minimal scale value.

            `scaleMax :`
                The maximum scale value.

            `valueList :`
                The list of values to draw the image.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `value_offset : int`
                This property holds the value offset. By default, the value is 0.

            `value_stride : int`
                This property holds the stride to get value list. By default, the value is 1.

            `title : str`
                This property holds the title of the image.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    def set_data(self, *args) -> None: 
        """
        Sets the image data value.
        """
    def set_data_provider_fn(self, arg0: typing.Callable[[int], float], arg1: int) -> None: 
        """
        Sets the function that will be called when when data required.
        """
    def set_xy_data(self, arg0: typing.List[typing.Tuple[float, float]]) -> None: ...
    @property
    def scale_max(self) -> float:
        """
        This property holds the max scale values. By default, the value is FLT_MAX.

        :type: float
        """
    @scale_max.setter
    def scale_max(self, arg1: float) -> None:
        """
        This property holds the max scale values. By default, the value is FLT_MAX.
        """
    @property
    def scale_min(self) -> float:
        """
        This property holds the min scale values. By default, the value is FLT_MAX.

        :type: float
        """
    @scale_min.setter
    def scale_min(self, arg1: float) -> None:
        """
        This property holds the min scale values. By default, the value is FLT_MAX.
        """
    @property
    def title(self) -> str:
        """
        This property holds the title of the image.

        :type: str
        """
    @title.setter
    def title(self, arg1: str) -> None:
        """
        This property holds the title of the image.
        """
    @property
    def type(self) -> Type:
        """
        This property holds the type of the image, can only be line or histogram. By default, the type is line.

        :type: Type
        """
    @type.setter
    def type(self, arg1: Type) -> None:
        """
        This property holds the type of the image, can only be line or histogram. By default, the type is line.
        """
    @property
    def value_offset(self) -> int:
        """
        This property holds the value offset. By default, the value is 0.

        :type: int
        """
    @value_offset.setter
    def value_offset(self, arg1: int) -> None:
        """
        This property holds the value offset. By default, the value is 0.
        """
    @property
    def value_stride(self) -> int:
        """
        This property holds the stride to get value list. By default, the value is 1.

        :type: int
        """
    @value_stride.setter
    def value_stride(self, arg1: int) -> None:
        """
        This property holds the stride to get value list. By default, the value is 1.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ProgressBar(Widget, ValueModelHelper):
    """
    A progressbar is a classic widget for showing the progress of an operation.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Construct ProgressBar.


        ### Arguments:

            `model :`
                The model that determines if the button is checked.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class RadioButton(Button, InvisibleButton, Widget):
    """
    RadioButton is the widget that allows the user to choose only one of a predefined set of mutually exclusive options.
    RadioButtons are arranged in collections of two or more with the class RadioCollection, which is the central component of the system and controls the behavior of all the RadioButtons in the collection.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructs RadioButton.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `radio_collection : `
                This property holds the button's text.

            `text : str`
                This property holds the button's text.

            `image_url : str`
                This property holds the button's optional image URL.

            `image_width : float`
                This property holds the width of the image widget. Do not use this function to find the width of the image.

            `image_height : float`
                This property holds the height of the image widget. Do not use this function to find the height of the image.

            `spacing : float`
                Sets a non-stretchable space in points between image and text.

            `clicked_fn : Callable[[], None]`
                Sets the function that will be called when when the button is activated (i.e., pressed down then released while the mouse cursor is inside the button).

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def radio_collection(self) -> RadioCollection:
        """
        This property holds the button's text.

        :type: RadioCollection
        """
    @radio_collection.setter
    def radio_collection(self, arg1: RadioCollection) -> None:
        """
        This property holds the button's text.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class RadioCollection(ValueModelHelper):
    """
    Radio Collection is a class that groups RadioButtons and coordinates their state.
    It makes sure that the choice is mutually exclusive, it means when the user selects a radio button, any previously selected radio button in the same collection becomes deselected.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Constructs RadioCollection.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    pass
class RasterImageProvider(ImageProvider):
    """
    doc
    """
    def __init__(self, source_url: str = None, **kwargs) -> None: 
        """
        doc
        """
    @property
    def max_mip_levels(self) -> int:
        """
        Maximum number of mip map levels allowed

        :type: int
        """
    @max_mip_levels.setter
    def max_mip_levels(self, arg1: int) -> None:
        """
        Maximum number of mip map levels allowed
        """
    @property
    def source_url(self) -> str:
        """
        Sets byte data that the image provider will turn into an image.

        :type: str
        """
    @source_url.setter
    def source_url(self, arg1: str) -> None:
        """
        Sets byte data that the image provider will turn into an image.
        """
    pass
class RasterPolicy():
    """
    Used to set the rasterization behaviour.


    Members:

      NEVER : Do not rasterize the widget at any time.


      ON_DEMAND : Rasterize the widget as soon as possible and always use the rasterized version. This means that the widget will only be updated when the user called invalidateRaster.


      AUTO : Automatically determine whether to rasterize the widget based on performance considerations. If necessary, the widget will be rasterized and updated when its content changes.
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    AUTO: omni.ui._ui.RasterPolicy # value = <RasterPolicy.AUTO: 2>
    NEVER: omni.ui._ui.RasterPolicy # value = <RasterPolicy.NEVER: 0>
    ON_DEMAND: omni.ui._ui.RasterPolicy # value = <RasterPolicy.ON_DEMAND: 1>
    __members__: dict # value = {'NEVER': <RasterPolicy.NEVER: 0>, 'ON_DEMAND': <RasterPolicy.ON_DEMAND: 1>, 'AUTO': <RasterPolicy.AUTO: 2>}
    pass
class Rectangle(Shape, Widget):
    """
    The Rectangle widget provides a colored rectangle to display.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructs Rectangle.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ScrollBarPolicy():
    """
    Members:

      SCROLLBAR_AS_NEEDED

      SCROLLBAR_ALWAYS_OFF

      SCROLLBAR_ALWAYS_ON
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    SCROLLBAR_ALWAYS_OFF: omni.ui._ui.ScrollBarPolicy # value = <ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF: 1>
    SCROLLBAR_ALWAYS_ON: omni.ui._ui.ScrollBarPolicy # value = <ScrollBarPolicy.SCROLLBAR_ALWAYS_ON: 2>
    SCROLLBAR_AS_NEEDED: omni.ui._ui.ScrollBarPolicy # value = <ScrollBarPolicy.SCROLLBAR_AS_NEEDED: 0>
    __members__: dict # value = {'SCROLLBAR_AS_NEEDED': <ScrollBarPolicy.SCROLLBAR_AS_NEEDED: 0>, 'SCROLLBAR_ALWAYS_OFF': <ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF: 1>, 'SCROLLBAR_ALWAYS_ON': <ScrollBarPolicy.SCROLLBAR_ALWAYS_ON: 2>}
    pass
class ScrollingFrame(Frame, Container, Widget):
    """
    The ScrollingFrame class provides the ability to scroll onto another widget.
    ScrollingFrame is used to display the contents of a child widget within a frame. If the widget exceeds the size of the frame, the frame can provide scroll bars so that the entire area of the child widget can be viewed. The child widget must be specified with addChild().
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct ScrollingFrame.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `scroll_x : float`
                The horizontal position of the scroll bar. When it's changed, the contents will be scrolled accordingly.

            `scroll_x_max : float`
                The max position of the horizontal scroll bar.

            `scroll_x_changed_fn : Callable[[float], None]`
                The horizontal position of the scroll bar. When it's changed, the contents will be scrolled accordingly.

            `scroll_y : float`
                The vertical position of the scroll bar. When it's changed, the contents will be scrolled accordingly.

            `scroll_y_max : float`
                The max position of the vertical scroll bar.

            `scroll_y_changed_fn : Callable[[float], None]`
                The vertical position of the scroll bar. When it's changed, the contents will be scrolled accordingly.

            `horizontal_scrollbar_policy : ui.ScrollBarPolicy`
                This property holds the policy for the horizontal scroll bar.

            `vertical_scrollbar_policy : ui.ScrollBarPolicy`
                This property holds the policy for the vertical scroll bar.

            `horizontal_clipping : `
                When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for horizontal direction.

            `vertical_clipping : `
                When the content of the frame is bigger than the frame the exceeding part is not drawn if the clipping is on. It only works for vertial direction.

            `separate_window : `
                A special mode where the child is placed to the transparent borderless window. We need it to be able to place the UI to the exact stacking order between other windows.

            `raster_policy : `
                Determine how the content of the frame should be rasterized.

            `build_fn : `
                Set the callback that will be called once the frame is visible and the content of the callback will override the frame child. It's useful for lazy load.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    def set_scroll_x_changed_fn(self, arg0: typing.Callable[[float], None]) -> None: 
        """
        The horizontal position of the scroll bar. When it's changed, the contents will be scrolled accordingly.
        """
    def set_scroll_y_changed_fn(self, arg0: typing.Callable[[float], None]) -> None: 
        """
        The vertical position of the scroll bar. When it's changed, the contents will be scrolled accordingly.
        """
    @property
    def horizontal_scrollbar_policy(self) -> ScrollBarPolicy:
        """
        This property holds the policy for the horizontal scroll bar.

        :type: ScrollBarPolicy
        """
    @horizontal_scrollbar_policy.setter
    def horizontal_scrollbar_policy(self, arg1: ScrollBarPolicy) -> None:
        """
        This property holds the policy for the horizontal scroll bar.
        """
    @property
    def scroll_x(self) -> float:
        """
        The horizontal position of the scroll bar. When it's changed, the contents will be scrolled accordingly.

        :type: float
        """
    @scroll_x.setter
    def scroll_x(self, arg1: float) -> None:
        """
        The horizontal position of the scroll bar. When it's changed, the contents will be scrolled accordingly.
        """
    @property
    def scroll_x_max(self) -> float:
        """
        The max position of the horizontal scroll bar.

        :type: float
        """
    @property
    def scroll_y(self) -> float:
        """
        The vertical position of the scroll bar. When it's changed, the contents will be scrolled accordingly.

        :type: float
        """
    @scroll_y.setter
    def scroll_y(self, arg1: float) -> None:
        """
        The vertical position of the scroll bar. When it's changed, the contents will be scrolled accordingly.
        """
    @property
    def scroll_y_max(self) -> float:
        """
        The max position of the vertical scroll bar.

        :type: float
        """
    @property
    def vertical_scrollbar_policy(self) -> ScrollBarPolicy:
        """
        This property holds the policy for the vertical scroll bar.

        :type: ScrollBarPolicy
        """
    @vertical_scrollbar_policy.setter
    def vertical_scrollbar_policy(self, arg1: ScrollBarPolicy) -> None:
        """
        This property holds the policy for the vertical scroll bar.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Separator(Widget, MenuHelper):
    """
    The Separator class provides blank space.
    Normally, it's used to create separator line in the UI elements
    """
    def __init__(self, text: str = '', **kwargs) -> None: 
        """
        Construct Separator.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `text : str`
                This property holds the menu's text.

            `hotkey_text : str`
                This property holds the menu's hotkey text.

            `checkable : bool`
                This property holds whether this menu item is checkable. A checkable item is one which has an on/off state.

            `hide_on_click : bool`
                Hide or keep the window when the user clicked this item.

            `delegate : MenuDelegate`
                The delegate that generates a widget per menu item.

            `triggered_fn : void`
                Sets the function that is called when an action is activated by the user; for example, when the user clicks a menu option, or presses an action's shortcut key combination.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ShadowFlag():
    """
    Members:

      NONE

      CUT_OUT_SHAPE_BACKGROUND
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    CUT_OUT_SHAPE_BACKGROUND: omni.ui._ui.ShadowFlag # value = <ShadowFlag.CUT_OUT_SHAPE_BACKGROUND: 1>
    NONE: omni.ui._ui.ShadowFlag # value = <ShadowFlag.NONE: 0>
    __members__: dict # value = {'NONE': <ShadowFlag.NONE: 0>, 'CUT_OUT_SHAPE_BACKGROUND': <ShadowFlag.CUT_OUT_SHAPE_BACKGROUND: 1>}
    pass
class Shape(Widget):
    """
    The Shape widget provides a base class for all the Shape Widget. Currently implemented are Rectangle, Circle, Triangle, Line, Ellipse and BezierCurve.
    """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ShapeAnchorHelper():
    """
    The ShapeAnchorHelper provides common functionality for Shape Anchors.
    """
    def call_anchor_fn(self) -> None: 
        """
        Sets the function that will be called for the curve anchor.
        """
    def get_closest_parametric_position(self, position_x: float, position_y: float) -> float: 
        """
        Function that returns the closest parametric T value to a given x,y position.
        """
    def has_anchor_fn(self) -> bool: 
        """
        Sets the function that will be called for the curve anchor.
        """
    def invalidate_anchor(self) -> None: 
        """
        Function that causes the anchor frame to be redrawn.
        """
    def set_anchor_fn(self, fn: typing.Callable[[], None]) -> None: 
        """
        Sets the function that will be called for the curve anchor.
        """
    @property
    def anchor_alignment(self) -> Alignment:
        """
        This property holds the Alignment of the curve anchor.

        :type: Alignment
        """
    @anchor_alignment.setter
    def anchor_alignment(self, arg1: Alignment) -> None:
        """
        This property holds the Alignment of the curve anchor.
        """
    @property
    def anchor_position(self) -> float:
        """
        This property holds the parametric value of the curve anchor.

        :type: float
        """
    @anchor_position.setter
    def anchor_position(self, arg1: float) -> None:
        """
        This property holds the parametric value of the curve anchor.
        """
    pass
class SimpleBoolModel(AbstractValueModel):
    """
    A very simple bool model.
    """
    def __init__(self, default_value: bool = False, **kwargs) -> None: ...
    def get_max(self) -> bool: ...
    def get_min(self) -> bool: ...
    def set_max(self, arg0: bool) -> None: ...
    def set_min(self, arg0: bool) -> None: ...
    @property
    def max(self) -> bool:
        """
        This property holds the model's maximum value.

        :type: bool
        """
    @max.setter
    def max(self, arg1: bool) -> None:
        """
        This property holds the model's maximum value.
        """
    @property
    def min(self) -> bool:
        """
        This property holds the model's minimum value.

        :type: bool
        """
    @min.setter
    def min(self, arg1: bool) -> None:
        """
        This property holds the model's minimum value.
        """
    pass
class SimpleFloatModel(AbstractValueModel):
    """
    A very simple double model.
    """
    def __init__(self, default_value: float = 0.0, **kwargs) -> None: ...
    def get_max(self) -> float: ...
    def get_min(self) -> float: ...
    def set_max(self, arg0: float) -> None: ...
    def set_min(self, arg0: float) -> None: ...
    @property
    def max(self) -> float:
        """
        This property holds the model's minimum value.

        :type: float
        """
    @max.setter
    def max(self, arg1: float) -> None:
        """
        This property holds the model's minimum value.
        """
    @property
    def min(self) -> float:
        """
        This property holds the model's minimum value.

        :type: float
        """
    @min.setter
    def min(self, arg1: float) -> None:
        """
        This property holds the model's minimum value.
        """
    pass
class SimpleIntModel(AbstractValueModel):
    """
    A very simple Int model.
    """
    def __init__(self, default_value: int = 0, **kwargs) -> None: ...
    def get_max(self) -> int: ...
    def get_min(self) -> int: ...
    def set_max(self, arg0: int) -> None: ...
    def set_min(self, arg0: int) -> None: ...
    @property
    def max(self) -> int:
        """
        This property holds the model's minimum value.

        :type: int
        """
    @max.setter
    def max(self, arg1: int) -> None:
        """
        This property holds the model's minimum value.
        """
    @property
    def min(self) -> int:
        """
        This property holds the model's minimum value.

        :type: int
        """
    @min.setter
    def min(self, arg1: int) -> None:
        """
        This property holds the model's minimum value.
        """
    pass
class SimpleStringModel(AbstractValueModel):
    """
    A very simple value model that holds a single string.
    """
    def __init__(self, defaultValue: str = '') -> None: ...
    pass
class SliderDrawMode():
    """
    Members:

      FILLED

      HANDLE

      DRAG
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    DRAG: omni.ui._ui.SliderDrawMode # value = <SliderDrawMode.DRAG: 2>
    FILLED: omni.ui._ui.SliderDrawMode # value = <SliderDrawMode.FILLED: 0>
    HANDLE: omni.ui._ui.SliderDrawMode # value = <SliderDrawMode.HANDLE: 1>
    __members__: dict # value = {'FILLED': <SliderDrawMode.FILLED: 0>, 'HANDLE': <SliderDrawMode.HANDLE: 1>, 'DRAG': <SliderDrawMode.DRAG: 2>}
    pass
class Spacer(Widget):
    """
    The Spacer class provides blank space.
    Normally, it's used to place other widgets correctly in a layout.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct Spacer.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Stack(Container, Widget):
    """
    The Stack class lines up child widgets horizontally, vertically or sorted in a Z-order.
    """
    def __init__(self, arg0: Direction, **kwargs) -> None: 
        """
        Constructor.


        ### Arguments:

            `direction :`
                Determines the orientation of the Stack.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def content_clipping(self) -> bool:
        """
        Determines if the child widgets should be clipped by the rectangle of this Stack.

        :type: bool
        """
    @content_clipping.setter
    def content_clipping(self, arg1: bool) -> None:
        """
        Determines if the child widgets should be clipped by the rectangle of this Stack.
        """
    @property
    def direction(self) -> Direction:
        """
        This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

        :type: Direction
        """
    @direction.setter
    def direction(self, arg1: Direction) -> None:
        """
        This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.
        """
    @property
    def send_mouse_events_to_back(self) -> bool:
        """
        When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

        :type: bool
        """
    @send_mouse_events_to_back.setter
    def send_mouse_events_to_back(self, arg1: bool) -> None:
        """
        When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.
        """
    @property
    def spacing(self) -> float:
        """
        Sets a non-stretchable space in pixels between child items of this layout.

        :type: float
        """
    @spacing.setter
    def spacing(self, arg1: float) -> None:
        """
        Sets a non-stretchable space in pixels between child items of this layout.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class StringField(AbstractField, Widget, ValueModelHelper):
    """
    The StringField widget is a one-line text editor with a string model.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Constructs StringField.


        ### Arguments:

            `model :`
                The widget's model. If the model is not assigned, the default model is created.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `password_mode : `
                This property holds the password mode. If the field is in the password mode when the entered text is obscured.

            `read_only : `
                This property holds if the field is read-only.

            `multiline : `
                Multiline allows to press enter and create a new line.

            `allow_tab_input : `
                This property holds if the field allows Tab input.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def allow_tab_input(self) -> bool:
        """
        This property holds if the field allows Tab input.

        :type: bool
        """
    @allow_tab_input.setter
    def allow_tab_input(self, arg1: bool) -> None:
        """
        This property holds if the field allows Tab input.
        """
    @property
    def multiline(self) -> bool:
        """
        Multiline allows to press enter and create a new line.

        :type: bool
        """
    @multiline.setter
    def multiline(self, arg1: bool) -> None:
        """
        Multiline allows to press enter and create a new line.
        """
    @property
    def password_mode(self) -> bool:
        """
        This property holds the password mode. If the field is in the password mode when the entered text is obscured.

        :type: bool
        """
    @password_mode.setter
    def password_mode(self, arg1: bool) -> None:
        """
        This property holds the password mode. If the field is in the password mode when the entered text is obscured.
        """
    @property
    def read_only(self) -> bool:
        """
        This property holds if the field is read-only.

        :type: bool
        """
    @read_only.setter
    def read_only(self, arg1: bool) -> None:
        """
        This property holds if the field is read-only.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class StringStore():
    """
    A singleton that stores all the UI Style string properties of omni.ui.
    """
    @staticmethod
    def find(name: str) -> str: 
        """
        Return the index of the color with specific name.
        """
    @staticmethod
    def store(name: str, string: str) -> None: 
        """
        Save the color by name.
        """
    pass
class Style():
    """
    A singleton that controls the global style of the session.
    """
    @staticmethod
    def get_instance() -> Style: 
        """
        Get the instance of this singleton object.
        """
    @property
    def default(self) -> object:
        """
        Set the default root style. It's the style that is preselected when no alternative is specified.

        :type: object
        """
    @default.setter
    def default(self, arg1: handle) -> None:
        """
        Set the default root style. It's the style that is preselected when no alternative is specified.
        """
    pass
class ToolBar(Window, WindowHandle):
    """
    The ToolBar class represents a window in the underlying windowing system that as some fixed size property.
    """
    def __init__(self, title: str, **kwargs) -> None: 
        """
        Construct ToolBar.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `axis : ui.Axis`
                @breif axis for the toolbar

            `axis_changed_fn : Callable[[ui.Axis], None]`
                @breif axis for the toolbar

            `flags : `
                This property set the Flags for the Window.

            `visible : `
                This property holds whether the window is visible.

            `title : `
                This property holds the window's title.

            `padding_x : `
                This property set the padding to the frame on the X axis.

            `padding_y : `
                This property set the padding to the frame on the Y axis.

            `width : `
                This property holds the window Width.

            `height : `
                This property holds the window Height.

            `position_x : `
                This property set/get the position of the window in the X Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.

            `position_y : `
                This property set/get the position of the window in the Y Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.

            `auto_resize : `
                setup the window to resize automatically based on its content

            `noTabBar : `
                setup the visibility of the TabBar Handle, this is the small triangle at the corner of the view If it is not shown then it is not possible to undock that window and it need to be closed/moved programatically

            `tabBarTooltip : `
                This property sets the tooltip when hovering over window's tabbar.

            `raster_policy : `
                Determine how the content of the window should be rastered.

            `width_changed_fn : `
                This property holds the window Width.

            `height_changed_fn : `
                This property holds the window Height.

            `visibility_changed_fn : `
                This property holds whether the window is visible.
        """
    def set_axis_changed_fn(self, arg0: typing.Callable[[ToolBarAxis], None]) -> None: ...
    @property
    def axis(self) -> ToolBarAxis:
        """
        :type: ToolBarAxis
        """
    @axis.setter
    def axis(self, arg1: ToolBarAxis) -> None:
        pass
    pass
class ToolBarAxis():
    """
    Members:

      X

      Y
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    X: omni.ui._ui.ToolBarAxis # value = <ToolBarAxis.X: 0>
    Y: omni.ui._ui.ToolBarAxis # value = <ToolBarAxis.Y: 1>
    __members__: dict # value = {'X': <ToolBarAxis.X: 0>, 'Y': <ToolBarAxis.Y: 1>}
    pass
class ToolButton(Button, InvisibleButton, Widget, ValueModelHelper):
    """
    ToolButton is functionally similar to Button, but provides a model that determines if the button is checked. This button toggles between checked (on) and unchecked (off) when the user clicks it.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Construct a checkable button with the model. If the bodel is not provided, then the default model is created.


        ### Arguments:

            `model :`
                The model that determines if the button is checked.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `text : str`
                This property holds the button's text.

            `image_url : str`
                This property holds the button's optional image URL.

            `image_width : float`
                This property holds the width of the image widget. Do not use this function to find the width of the image.

            `image_height : float`
                This property holds the height of the image widget. Do not use this function to find the height of the image.

            `spacing : float`
                Sets a non-stretchable space in points between image and text.

            `clicked_fn : Callable[[], None]`
                Sets the function that will be called when when the button is activated (i.e., pressed down then released while the mouse cursor is inside the button).

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class TreeView(Widget, ItemModelHelper):
    """
    TreeView is a widget that presents a hierarchical view of information. Each item can have a number of subitems. An indentation often visualizes this in a list. An item can be expanded to reveal subitems, if any exist, and collapsed to hide subitems.
    TreeView can be used in file manager applications, where it allows the user to navigate the file system directories. They are also used to present hierarchical data, such as the scene object hierarchy.
    TreeView uses a model/view pattern to manage the relationship between data and the way it is presented. The separation of functionality gives developers greater flexibility to customize the presentation of items and provides a standard interface to allow a wide range of data sources to be used with other widgets.
    TreeView is responsible for the presentation of model data to the user and processing user input. To allow some flexibility in the way the data is presented, the creation of the sub-widgets is performed by the delegate. It provides the ability to customize any sub-item of TreeView.
    """
    @typing.overload
    def __init__(self, **kwargs) -> None: 
        """
        Create TreeView with default model.

        Create TreeView with the given model.


        ### Arguments:

            `model :`
                The given model.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `delegate : `
                The Item delegate that generates a widget per item.

            `header_visible : `
                This property holds if the header is shown or not.

            `selection : `
                Set current selection.

            `expand_on_branch_click : `
                This flag allows to prevent expanding when the user clicks the plus icon. It's used in the case the user wants to control how the items expanded or collapsed.

            `keep_alive : `
                When true, the tree nodes are never destroyed even if they are disappeared from the model. It's useul for the temporary filtering if it's necessary to display thousands of nodes.

            `keep_expanded : `
                Expand all the nodes and keep them expanded regardless their state.

            `drop_between_items : `
                When true, the tree nodes can be dropped between items.

            `column_widths : `
                Widths of the columns. If not set, the width is Fraction(1).

            `min_column_widths : `
                Minimum widths of the columns. If not set, the width is Pixel(0).

            `columns_resizable : `
                When true, the columns can be resized with the mouse.

            `selection_changed_fn : `
                Set the callback that is called when the selection is changed.

            `root_expanded : `
                The expanded state of the root item. Changing this flag doesn't make the children repopulated.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @typing.overload
    def __init__(self, arg0: AbstractItemModel, **kwargs) -> None: ...
    def call_hover_changed_fn(self, arg0: AbstractItem, arg1: bool) -> None: 
        """
        Set the callback that is called when the item hover status is changed.
        """
    def call_selection_changed_fn(self, arg0: typing.List[AbstractItem]) -> None: 
        """
        Set the callback that is called when the selection is changed.
        """
    def clear_selection(self) -> None: 
        """
        Deselects all selected items.
        """
    def dirty_widgets(self) -> None: 
        """
        When called, it will make the delegate to regenerate all visible widgets the next frame.
        """
    def extend_selection(self, item: AbstractItem) -> None: 
        """
        Extends the current selection selecting all the items between currently selected nodes and the given item. It's when user does shift+click.
        """
    def has_hover_changed_fn(self) -> bool: 
        """
        Set the callback that is called when the item hover status is changed.
        """
    def has_selection_changed_fn(self) -> bool: 
        """
        Set the callback that is called when the selection is changed.
        """
    def is_expanded(self, item: AbstractItem) -> bool: 
        """
        Returns true if the given item is expanded.
        """
    def set_expanded(self, item: AbstractItem, expanded: bool, recursive: bool) -> None: 
        """
        Sets the given item expanded or collapsed.


        ### Arguments:

            `item :`
                The item to expand or collapse.

            `expanded :`
                True if it's necessary to expand, false to collapse.

            `recursive :`
                True if it's necessary to expand children.
        """
    def set_hover_changed_fn(self, fn: typing.Callable[[AbstractItem, bool], None]) -> None: 
        """
        Set the callback that is called when the item hover status is changed.
        """
    def set_selection_changed_fn(self, fn: typing.Callable[[typing.List[AbstractItem]], None]) -> None: 
        """
        Set the callback that is called when the selection is changed.
        """
    def toggle_selection(self, item: AbstractItem) -> None: 
        """
        Switches the selection state of the given item.
        """
    @property
    def column_widths(self) -> typing.List[Length]:
        """
        Widths of the columns. If not set, the width is Fraction(1).

        :type: typing.List[Length]
        """
    @column_widths.setter
    def column_widths(self, arg1: typing.List[Length]) -> None:
        """
        Widths of the columns. If not set, the width is Fraction(1).
        """
    @property
    def columns_resizable(self) -> bool:
        """
        When true, the columns can be resized with the mouse.

        :type: bool
        """
    @columns_resizable.setter
    def columns_resizable(self, arg1: bool) -> None:
        """
        When true, the columns can be resized with the mouse.
        """
    @property
    def drop_between_items(self) -> bool:
        """
        When true, the tree nodes can be dropped between items.

        :type: bool
        """
    @drop_between_items.setter
    def drop_between_items(self, arg1: bool) -> None:
        """
        When true, the tree nodes can be dropped between items.
        """
    @property
    def expand_on_branch_click(self) -> bool:
        """
        This flag allows to prevent expanding when the user clicks the plus icon. It's used in the case the user wants to control how the items expanded or collapsed.

        :type: bool
        """
    @expand_on_branch_click.setter
    def expand_on_branch_click(self, arg1: bool) -> None:
        """
        This flag allows to prevent expanding when the user clicks the plus icon. It's used in the case the user wants to control how the items expanded or collapsed.
        """
    @property
    def fixed_width_columns(self) -> typing.List[bool]:
        """
        This property holds the list of whether a column can be resized or not.

        :type: typing.List[bool]
        """
    @fixed_width_columns.setter
    def fixed_width_columns(self, arg1: typing.List[bool]) -> None:
        """
        This property holds the list of whether a column can be resized or not.
        """
    @property
    def header_visible(self) -> bool:
        """
        This property holds if the header is shown or not.

        :type: bool
        """
    @header_visible.setter
    def header_visible(self, arg1: bool) -> None:
        """
        This property holds if the header is shown or not.
        """
    @property
    def keep_alive(self) -> bool:
        """
        When true, the tree nodes are never destroyed even if they are disappeared from the model. It's useul for the temporary filtering if it's necessary to display thousands of nodes.

        :type: bool
        """
    @keep_alive.setter
    def keep_alive(self, arg1: bool) -> None:
        """
        When true, the tree nodes are never destroyed even if they are disappeared from the model. It's useul for the temporary filtering if it's necessary to display thousands of nodes.
        """
    @property
    def keep_expanded(self) -> bool:
        """
        Expand all the nodes and keep them expanded regardless their state.

        :type: bool
        """
    @keep_expanded.setter
    def keep_expanded(self, arg1: bool) -> None:
        """
        Expand all the nodes and keep them expanded regardless their state.
        """
    @property
    def min_column_widths(self) -> typing.List[Length]:
        """
        Minimum widths of the columns. If not set, the width is Pixel(0).

        :type: typing.List[Length]
        """
    @min_column_widths.setter
    def min_column_widths(self, arg1: typing.List[Length]) -> None:
        """
        Minimum widths of the columns. If not set, the width is Pixel(0).
        """
    @property
    def resizeable_on_columns_resized(self) -> bool:
        """
        When true, the treeview is resizable when columns are resized. Otherwise, treeview width is fixed when columns are resized.

        :type: bool
        """
    @resizeable_on_columns_resized.setter
    def resizeable_on_columns_resized(self, arg1: bool) -> None:
        """
        When true, the treeview is resizable when columns are resized. Otherwise, treeview width is fixed when columns are resized.
        """
    @property
    def root_expanded(self) -> bool:
        """
        The expanded state of the root item. Changing this flag doesn't make the children repopulated.

        :type: bool
        """
    @root_expanded.setter
    def root_expanded(self, arg1: bool) -> None:
        """
        The expanded state of the root item. Changing this flag doesn't make the children repopulated.
        """
    @property
    def root_visible(self) -> bool:
        """
        This property holds if the root is shown. It can be used to make a single level tree appear like a simple list.

        :type: bool
        """
    @root_visible.setter
    def root_visible(self, arg1: bool) -> None:
        """
        This property holds if the root is shown. It can be used to make a single level tree appear like a simple list.
        """
    @property
    def selection(self) -> typing.List[AbstractItem]:
        """
        Set current selection.

        :type: typing.List[AbstractItem]
        """
    @selection.setter
    def selection(self, arg1: typing.List[AbstractItem]) -> None:
        """
        Set current selection.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Triangle(Shape, Widget):
    """
    The Triangle widget provides a colored triangle to display.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructs Triangle.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `alignment : `
                This property holds the alignment of the triangle when the fill policy is ePreserveAspectFit or ePreserveAspectCrop.    By default, the triangle is centered.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def alignment(self) -> Alignment:
        """
        This property holds the alignment of the triangle when the fill policy is ePreserveAspectFit or ePreserveAspectCrop.    By default, the triangle is centered.

        :type: Alignment
        """
    @alignment.setter
    def alignment(self, arg1: Alignment) -> None:
        """
        This property holds the alignment of the triangle when the fill policy is ePreserveAspectFit or ePreserveAspectCrop.    By default, the triangle is centered.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Type():
    """
    Members:

      LINE

      HISTOGRAM

      LINE2D
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    HISTOGRAM: omni.ui._ui.Type # value = <Type.HISTOGRAM: 1>
    LINE: omni.ui._ui.Type # value = <Type.LINE: 0>
    LINE2D: omni.ui._ui.Type # value = <Type.LINE2D: 2>
    __members__: dict # value = {'LINE': <Type.LINE: 0>, 'HISTOGRAM': <Type.HISTOGRAM: 1>, 'LINE2D': <Type.LINE2D: 2>}
    pass
class UIntDrag(UIntSlider, AbstractSlider, Widget, ValueModelHelper):
    """

    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Constructs UIntDrag.


        ### Arguments:

            `model :`
                The widget's model. If the model is not assigned, the default model is created.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `step : `
                This property controls the steping speed on the drag, its float to enable slower speed, but of course the value on the Control are still integer.

            `min : `
                This property holds the slider's minimum value.

            `max : `
                This property holds the slider's maximum value.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def step(self) -> float:
        """
        This property controls the steping speed on the drag, its float to enable slower speed, but of course the value on the Control are still integer.

        :type: float
        """
    @step.setter
    def step(self, arg1: float) -> None:
        """
        This property controls the steping speed on the drag, its float to enable slower speed, but of course the value on the Control are still integer.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class UIntSlider(AbstractSlider, Widget, ValueModelHelper):
    """
    The slider is the classic widget for controlling a bounded value. It lets the user move a slider handle along a horizontal groove and translates the handle's position into an integer value within the legal range.
    The difference with IntSlider is that UIntSlider has unsigned min/max.
    """
    def __init__(self, model: AbstractValueModel = None, **kwargs) -> None: 
        """
        Constructs UIntSlider.


        ### Arguments:

            `model :`
                The widget's model. If the model is not assigned, the default model is created.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `min : `
                This property holds the slider's minimum value.

            `max : `
                This property holds the slider's maximum value.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    @property
    def max(self) -> int:
        """
        This property holds the slider's maximum value.

        :type: int
        """
    @max.setter
    def max(self, arg1: int) -> None:
        """
        This property holds the slider's maximum value.
        """
    @property
    def min(self) -> int:
        """
        This property holds the slider's minimum value.

        :type: int
        """
    @min.setter
    def min(self, arg1: int) -> None:
        """
        This property holds the slider's minimum value.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class UnitType():
    """
                Unit types.

                Widths, heights or other UI length can be specified in pixels or relative to window (or child window) size.
            

    Members:

      PIXEL

      PERCENT

      FRACTION
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    FRACTION: omni.ui._ui.UnitType # value = <UnitType.FRACTION: 2>
    PERCENT: omni.ui._ui.UnitType # value = <UnitType.PERCENT: 1>
    PIXEL: omni.ui._ui.UnitType # value = <UnitType.PIXEL: 0>
    __members__: dict # value = {'PIXEL': <UnitType.PIXEL: 0>, 'PERCENT': <UnitType.PERCENT: 1>, 'FRACTION': <UnitType.FRACTION: 2>}
    pass
class VGrid(Grid, Stack, Container, Widget):
    """
    Shortcut for Grid{eTopToBottom}. The grid grows from top to bottom with the widgets placed.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct a grid that grows from top to bottom with the widgets placed.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `column_width : `
                The width of the column. It's only possible to set it if the grid is vertical. Once it's set, the column count depends on the size of the widget.

            `row_height : `
                The height of the row. It's only possible to set it if the grid is horizontal. Once it's set, the row count depends on the size of the widget.

            `column_count : `
                The number of columns. It's only possible to set it if the grid is vertical. Once it's set, the column width depends on the widget size.

            `row_count : `
                The number of rows. It's only possible to set it if the grid is horizontal. Once it's set, the row height depends on the widget size.

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class VStack(Stack, Container, Widget):
    """
    Shortcut for Stack{eTopToBottom}. The widgets are placed in a column, with suitable sizes.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct a stack with the widgets placed in a column from top to bottom.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class ValueModelHelper():
    """
    The ValueModelHelper class provides the basic functionality for value widget classes. ValueModelHelper class is the     base class for every standard widget that uses a AbstractValueModel. ValueModelHelper is an abstract class and      itself cannot be instantiated. It provides a standard interface for interoperating with models.
    """
    @property
    def model(self) -> AbstractValueModel:
        """
        :type: AbstractValueModel
        """
    @model.setter
    def model(self, arg1: AbstractValueModel) -> None:
        pass
    pass
class VectorImageProvider(ImageProvider):
    """
    doc
    """
    def __init__(self, source_url: str = None, **kwargs) -> None: 
        """
        doc
        """
    @property
    def max_mip_levels(self) -> int:
        """
        Maximum number of mip map levels allowed

        :type: int
        """
    @max_mip_levels.setter
    def max_mip_levels(self, arg1: int) -> None:
        """
        Maximum number of mip map levels allowed
        """
    @property
    def source_url(self) -> str:
        """
        Sets the vector image URL. Asset loading doesn't happen immediately, but rather is started the next time widget is visible, in prepareDraw call.

        :type: str
        """
    @source_url.setter
    def source_url(self, arg1: str) -> None:
        """
        Sets the vector image URL. Asset loading doesn't happen immediately, but rather is started the next time widget is visible, in prepareDraw call.
        """
    pass
class Widget():
    """
    The Widget class is the base class of all user interface objects.
    The widget is the atom of the user interface: it receives mouse, keyboard and other events, and paints a representation of itself on the screen. Every widget is rectangular. A widget is clipped by its parent and by the widgets in front of it.
    """
    def __init__(self, **kwargs) -> None: ...
    def call_accept_drop_fn(self, arg0: str) -> bool: 
        """
        Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.
        """
    def call_computed_content_size_changed_fn(self) -> None: 
        """
        Called when the size of the widget is changed.
        """
    def call_drag_fn(self) -> str: 
        """
        Specify that this Widget is draggable, and set the callback that is attached to the drag operation.
        """
    def call_drop_fn(self, arg0: WidgetMouseDropEvent) -> None: 
        """
        Specify that this Widget accepts drops and set the callback to the drop operation.
        """
    def call_key_pressed_fn(self, arg0: int, arg1: int, arg2: bool) -> None: 
        """
        Sets the function that will be called when the user presses the keyboard key when the mouse clicks the widget.
        """
    def call_mouse_double_clicked_fn(self, arg0: float, arg1: float, arg2: int, arg3: int) -> None: 
        """
        Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)
        """
    def call_mouse_hovered_fn(self, arg0: bool) -> None: 
        """
        Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)
        """
    def call_mouse_moved_fn(self, arg0: float, arg1: float, arg2: int, arg3: bool) -> None: 
        """
        Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)
        """
    def call_mouse_pressed_fn(self, arg0: float, arg1: float, arg2: int, arg3: int) -> None: 
        """
        Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.
        """
    def call_mouse_released_fn(self, arg0: float, arg1: float, arg2: int, arg3: int) -> None: 
        """
        Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)
        """
    def call_mouse_wheel_fn(self, arg0: float, arg1: float, arg2: int) -> None: 
        """
        Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)
        """
    def call_tooltip_fn(self) -> None: 
        """
        Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.
        """
    def destroy(self) -> None: 
        """
        Removes all the callbacks and circular references.
        """
    def has_accept_drop_fn(self) -> bool: 
        """
        Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.
        """
    def has_computed_content_size_changed_fn(self) -> bool: 
        """
        Called when the size of the widget is changed.
        """
    def has_drag_fn(self) -> bool: 
        """
        Specify that this Widget is draggable, and set the callback that is attached to the drag operation.
        """
    def has_drop_fn(self) -> bool: 
        """
        Specify that this Widget accepts drops and set the callback to the drop operation.
        """
    def has_key_pressed_fn(self) -> bool: 
        """
        Sets the function that will be called when the user presses the keyboard key when the mouse clicks the widget.
        """
    def has_mouse_double_clicked_fn(self) -> bool: 
        """
        Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)
        """
    def has_mouse_hovered_fn(self) -> bool: 
        """
        Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)
        """
    def has_mouse_moved_fn(self) -> bool: 
        """
        Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)
        """
    def has_mouse_pressed_fn(self) -> bool: 
        """
        Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.
        """
    def has_mouse_released_fn(self) -> bool: 
        """
        Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)
        """
    def has_mouse_wheel_fn(self) -> bool: 
        """
        Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)
        """
    def has_tooltip_fn(self) -> bool: 
        """
        Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.
        """
    def scroll_here(self, center_ratio_x: float = 0.0, center_ratio_y: float = 0.0) -> None: 
        """
        Adjust scrolling amount in two axes to make current item visible.


        ### Arguments:

            `centerRatioX :`
                0.0: left, 0.5: center, 1.0: right

            `centerRatioY :`
                0.0: top, 0.5: center, 1.0: bottom
        """
    def scroll_here_x(self, center_ratio: float = 0.0) -> None: 
        """
        Adjust scrolling amount to make current item visible.


        ### Arguments:

            `centerRatio :`
                0.0: left, 0.5: center, 1.0: right
        """
    def scroll_here_y(self, center_ratio: float = 0.0) -> None: 
        """
        Adjust scrolling amount to make current item visible.


        ### Arguments:

            `centerRatio :`
                0.0: top, 0.5: center, 1.0: bottom
        """
    def set_accept_drop_fn(self, fn: typing.Callable[[str], bool]) -> None: 
        """
        Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.
        """
    def set_checked_changed_fn(self, fn: typing.Callable[[bool], None]) -> None: 
        """
        This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.
        """
    def set_computed_content_size_changed_fn(self, fn: typing.Callable[[], None]) -> None: 
        """
        Called when the size of the widget is changed.
        """
    def set_drag_fn(self, fn: typing.Callable[[], str]) -> None: 
        """
        Specify that this Widget is draggable, and set the callback that is attached to the drag operation.
        """
    def set_drop_fn(self, fn: typing.Callable[[WidgetMouseDropEvent], None]) -> None: 
        """
        Specify that this Widget accepts drops and set the callback to the drop operation.
        """
    def set_key_pressed_fn(self, fn: typing.Callable[[int, int, bool], None]) -> None: 
        """
        Sets the function that will be called when the user presses the keyboard key when the mouse clicks the widget.
        """
    def set_mouse_double_clicked_fn(self, fn: typing.Callable[[float, float, int, int], None]) -> None: 
        """
        Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)
        """
    def set_mouse_hovered_fn(self, fn: typing.Callable[[bool], None]) -> None: 
        """
        Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)
        """
    def set_mouse_moved_fn(self, fn: typing.Callable[[float, float, int, bool], None]) -> None: 
        """
        Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)
        """
    def set_mouse_pressed_fn(self, fn: typing.Callable[[float, float, int, int], None]) -> None: 
        """
        Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.
        """
    def set_mouse_released_fn(self, fn: typing.Callable[[float, float, int, int], None]) -> None: 
        """
        Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)
        """
    def set_mouse_wheel_fn(self, fn: typing.Callable[[float, float, int], None]) -> None: 
        """
        Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)
        """
    def set_style(self, arg0: handle) -> None: 
        """
        Set the current style. The style contains a description of customizations to the widget's style.
        """
    def set_tooltip(self, tooltip_label: str) -> None: 
        """
        Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style
        """
    def set_tooltip_fn(self, fn: typing.Callable[[], None]) -> None: 
        """
        Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.
        """
    @property
    def checked(self) -> bool:
        """
        This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

        :type: bool
        """
    @checked.setter
    def checked(self, arg1: bool) -> None:
        """
        This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.
        """
    @property
    def computed_content_height(self) -> float:
        """
        Returns the final computed height of the content of the widget.
        It's in puplic section. For the explanation why please see the draw() method.

        :type: float
        """
    @property
    def computed_content_width(self) -> float:
        """
        Returns the final computed width of the content of the widget.
        It's in puplic section. For the explanation why please see the draw() method.

        :type: float
        """
    @property
    def computed_height(self) -> float:
        """
        Returns the final computed height of the widget. It includes margins.
        It's in puplic section. For the explanation why please see the draw() method.

        :type: float
        """
    @property
    def computed_width(self) -> float:
        """
        Returns the final computed width of the widget. It includes margins.
        It's in puplic section. For the explanation why please see the draw() method.

        :type: float
        """
    @property
    def dragging(self) -> bool:
        """
        This property holds if the widget is being dragged.

        :type: bool
        """
    @dragging.setter
    def dragging(self, arg1: bool) -> None:
        """
        This property holds if the widget is being dragged.
        """
    @property
    def enabled(self) -> bool:
        """
        This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

        :type: bool
        """
    @enabled.setter
    def enabled(self, arg1: bool) -> None:
        """
        This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.
        """
    @property
    def explicit_hover(self) -> bool:
        """
        If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

        :type: bool
        """
    @explicit_hover.setter
    def explicit_hover(self, arg1: bool) -> None:
        """
        If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either
        """
    @property
    def height(self) -> Length:
        """
        This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

        :type: Length
        """
    @height.setter
    def height(self, arg1: Length) -> None:
        """
        This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.
        """
    @property
    def identifier(self) -> str:
        """
        An optional identifier of the widget we can use to refer to it in queries.

        :type: str
        """
    @identifier.setter
    def identifier(self, arg1: str) -> None:
        """
        An optional identifier of the widget we can use to refer to it in queries.
        """
    @property
    def name(self) -> str:
        """
        The name of the widget that user can set.

        :type: str
        """
    @name.setter
    def name(self, arg1: str) -> None:
        """
        The name of the widget that user can set.
        """
    @property
    def opaque_for_mouse_events(self) -> bool:
        """
        If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

        :type: bool
        """
    @opaque_for_mouse_events.setter
    def opaque_for_mouse_events(self, arg1: bool) -> None:
        """
        If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either
        """
    @property
    def screen_position_x(self) -> float:
        """
        Returns the X Screen coordinate the widget was last draw. This is in Screen Pixel size.
        It's a float because we need negative numbers and precise position considering DPI scale factor.

        :type: float
        """
    @property
    def screen_position_y(self) -> float:
        """
        Returns the Y Screen coordinate the widget was last draw. This is in Screen Pixel size.
        It's a float because we need negative numbers and precise position considering DPI scale factor.

        :type: float
        """
    @property
    def scroll_only_window_hovered(self) -> bool:
        """
        When it's false, the scroll callback is called even if other window is hovered.

        :type: bool
        """
    @scroll_only_window_hovered.setter
    def scroll_only_window_hovered(self, arg1: bool) -> None:
        """
        When it's false, the scroll callback is called even if other window is hovered.
        """
    @property
    def selected(self) -> bool:
        """
        This property holds a flag that specifies the widget has to use eSelected state of the style.

        :type: bool
        """
    @selected.setter
    def selected(self, arg1: bool) -> None:
        """
        This property holds a flag that specifies the widget has to use eSelected state of the style.
        """
    @property
    def skip_draw_when_clipped(self) -> bool:
        """
        The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

        :type: bool
        """
    @skip_draw_when_clipped.setter
    def skip_draw_when_clipped(self, arg1: bool) -> None:
        """
        The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.
        """
    @property
    def style(self) -> object:
        """
        The local style. When the user calls
        setStyle()

        :type: object
        """
    @style.setter
    def style(self, arg1: handle) -> None:
        """
        The local style. When the user calls
        setStyle()
        """
    @property
    def style_type_name_override(self) -> str:
        """
        By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

        :type: str
        """
    @style_type_name_override.setter
    def style_type_name_override(self, arg1: str) -> None:
        """
        By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.
        """
    @property
    def tooltip(self) -> str:
        """
        Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

        :type: str
        """
    @tooltip.setter
    def tooltip(self, arg1: str) -> None:
        """
        Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style
        """
    @property
    def tooltip_offset_x(self) -> float:
        """
        Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

        :type: float
        """
    @tooltip_offset_x.setter
    def tooltip_offset_x(self, arg1: float) -> None:
        """
        Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.
        """
    @property
    def tooltip_offset_y(self) -> float:
        """
        Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

        :type: float
        """
    @tooltip_offset_y.setter
    def tooltip_offset_y(self, arg1: float) -> None:
        """
        Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.
        """
    @property
    def visible(self) -> bool:
        """
        This property holds whether the widget is visible.

        :type: bool
        """
    @visible.setter
    def visible(self, arg1: bool) -> None:
        """
        This property holds whether the widget is visible.
        """
    @property
    def visible_max(self) -> float:
        """
        If the current zoom factor and DPI is bigger than this value, the widget is not visible.

        :type: float
        """
    @visible_max.setter
    def visible_max(self, arg1: float) -> None:
        """
        If the current zoom factor and DPI is bigger than this value, the widget is not visible.
        """
    @property
    def visible_min(self) -> float:
        """
        If the current zoom factor and DPI is less than this value, the widget is not visible.

        :type: float
        """
    @visible_min.setter
    def visible_min(self, arg1: float) -> None:
        """
        If the current zoom factor and DPI is less than this value, the widget is not visible.
        """
    @property
    def width(self) -> Length:
        """
        This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

        :type: Length
        """
    @width.setter
    def width(self, arg1: Length) -> None:
        """
        This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class WidgetMouseDropEvent():
    """
    Holds the data which is sent when a drag and drop action is completed.
    """
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def mime_data(self) -> str:
        """
        The data that was dropped on the widget.

        :type: str
        """
    @property
    def x(self) -> float:
        """
        Position where the drop was made.

        :type: float
        """
    @property
    def y(self) -> float:
        """
        Position where the drop was made.

        :type: float
        """
    pass
class Window(WindowHandle):
    """
    The Window class represents a window in the underlying windowing system.
    This window is a child window of main Kit window. And it can be docked.
    Rasterization
    omni.ui generates vertices every frame to render UI elements. One of the features of the framework is the ability to bake a DrawList per window and reuse it if the content has not changed, which can significantly improve performance. However, in some cases, such as the Viewport window and Console window, it may not be possible to detect whether the window content has changed, leading to a frozen window. To address this problem, you can control the rasterization behavior by adjusting RasterPolicy. The RasterPolicy is an enumeration class that defines the rasterization behavior of a window. It has three possible values:
    NEVER: Do not rasterize the widget at any time. ON_DEMAND: Rasterize the widget as soon as possible and always use the rasterized version. The widget will only be updated when the user calls invalidateRaster. AUTO: Automatically determine whether to rasterize the widget based on performance considerations. If necessary, the widget will be rasterized and updated when its content changes.
    To resolve the frozen window issue, you can manually set the RasterPolicy of the problematic window to Never. This will force the window to rasterize its content and use the rasterized version until the user explicitly calls invalidateRaster to request an update.
    window = ui.Window("Test window", raster_policy=ui.RasterPolicy.NEVER)
    """
    def __init__(self, title: str, dockPreference: DockPreference = DockPreference.DISABLED, **kwargs) -> None: 
        """
        Construct the window, add it to the underlying windowing system, and makes it appear.


        ### Arguments:

            `title :`
                The window title. It's also used as an internal window ID.

            `dockPrefence :`
                In the old Kit determines where the window should be docked. In Kit Next it's unused.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `flags : `
                This property set the Flags for the Window.

            `visible : `
                This property holds whether the window is visible.

            `title : `
                This property holds the window's title.

            `padding_x : `
                This property set the padding to the frame on the X axis.

            `padding_y : `
                This property set the padding to the frame on the Y axis.

            `width : `
                This property holds the window Width.

            `height : `
                This property holds the window Height.

            `position_x : `
                This property set/get the position of the window in the X Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.

            `position_y : `
                This property set/get the position of the window in the Y Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.

            `auto_resize : `
                setup the window to resize automatically based on its content

            `noTabBar : `
                setup the visibility of the TabBar Handle, this is the small triangle at the corner of the view If it is not shown then it is not possible to undock that window and it need to be closed/moved programatically

            `tabBarTooltip : `
                This property sets the tooltip when hovering over window's tabbar.

            `raster_policy : `
                Determine how the content of the window should be rastered.

            `width_changed_fn : `
                This property holds the window Width.

            `height_changed_fn : `
                This property holds the window Height.

            `visibility_changed_fn : `
                This property holds whether the window is visible.
        """
    def call_key_pressed_fn(self, arg0: int, arg1: int, arg2: bool) -> None: 
        """
        Sets the function that will be called when the user presses the keyboard key on the focused window.
        """
    def deferred_dock_in(self, target_window: str, active_window: DockPolicy = DockPolicy.DO_NOTHING) -> None: 
        """
        Deferred docking. We need it when we want to dock windows before they were actually created. It's helpful when extension initialization, before any window is created.


        ### Arguments:

            `targetWindowTitle :`
                Dock to window with this title when it appears.

            `activeWindow :`
                Make target or this window active when docked.
        """
    def destroy(self) -> None: 
        """
        Removes all the callbacks and circular references.
        """
    def dock_in_window(self, title: str, dockPosition: DockPosition, ratio: float = 0.5) -> bool: 
        """
        place the window in a specific docking position based on a target window name. We will find the target window dock node and insert this window in it, either by spliting on ratio or on top if the window is not found false is return, otherwise true
        """
    @staticmethod
    def get_window_callback(*args, **kwargs) -> typing.Any: 
        """
        Returns window set draw callback pointer for the given UI window.
        """
    def has_key_pressed_fn(self) -> bool: 
        """
        Sets the function that will be called when the user presses the keyboard key on the focused window.
        """
    def move_to_app_window(self, arg0: omni.appwindow._appwindow.IAppWindow) -> None: 
        """
        Moves the window to the specific OS window.
        """
    def move_to_main_os_window(self) -> None: 
        """
        Bring back the Window callback to the Main Window and destroy the Current OS Window.
        """
    def move_to_new_os_window(self) -> bool: 
        """
        Move the Window Callback to a new OS Window.
        """
    def notify_app_window_change(self, arg0: omni.appwindow._appwindow.IAppWindow) -> None: 
        """
        Notifies the window that window set has changed.
        """
    def setPosition(self, x: float, y: float) -> None: 
        """
        This property set/get the position of the window in both axis calling the property.
        """
    def set_active(self, active: bool) -> None: 
        """
        Set whether the Window is in an active state
        """
    def set_docked_changed_fn(self, arg0: typing.Callable[[bool], None]) -> None: 
        """
        Has true if this window is docked. False otherwise. It's a read-only property.
        """
    def set_focused_changed_fn(self, arg0: typing.Callable[[bool], None]) -> None: 
        """
        Read only property that is true when the window is focused.
        """
    def set_height_changed_fn(self, arg0: typing.Callable[[float], None]) -> None: 
        """
        This property holds the window Height.
        """
    def set_key_pressed_fn(self, fn: typing.Callable[[int, int, bool], None]) -> None: 
        """
        Sets the function that will be called when the user presses the keyboard key on the focused window.
        """
    def set_position_x_changed_fn(self, arg0: typing.Callable[[float], None]) -> None: 
        """
        This property set/get the position of the window in the X Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.
        """
    def set_position_y_changed_fn(self, arg0: typing.Callable[[float], None]) -> None: 
        """
        This property set/get the position of the window in the Y Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.
        """
    def set_selected_in_dock_changed_fn(self, arg0: typing.Callable[[bool], None]) -> None: 
        """
        Has true if this window is currently selected in the dock. False otherwise. It's a read-only property.
        """
    def set_top_modal(self) -> None: 
        """
        Brings this window to the top level of modal windows.
        """
    def set_visibility_changed_fn(self, arg0: typing.Callable[[bool], None]) -> None: 
        """
        This property holds whether the window is visible.
        """
    def set_width_changed_fn(self, arg0: typing.Callable[[float], None]) -> None: 
        """
        This property holds the window Width.
        """
    @property
    def app_window(self) -> omni.appwindow._appwindow.IAppWindow:
        """
        :type: omni.appwindow._appwindow.IAppWindow
        """
    @property
    def auto_resize(self) -> bool:
        """
        setup the window to resize automatically based on its content

        :type: bool
        """
    @auto_resize.setter
    def auto_resize(self, arg1: bool) -> None:
        """
        setup the window to resize automatically based on its content
        """
    @property
    def detachable(self) -> bool:
        """
        If the window is able to be separated from the main application window.

        :type: bool
        """
    @detachable.setter
    def detachable(self, arg1: bool) -> None:
        """
        If the window is able to be separated from the main application window.
        """
    @property
    def docked(self) -> bool:
        """
        Has true if this window is docked. False otherwise. It's a read-only property.

        :type: bool
        """
    @property
    def exclusive_keyboard(self) -> bool:
        """
        When true, only the current window will receive keyboard events when it's focused. It's useful to override the global key bindings.

        :type: bool
        """
    @exclusive_keyboard.setter
    def exclusive_keyboard(self, arg1: bool) -> None:
        """
        When true, only the current window will receive keyboard events when it's focused. It's useful to override the global key bindings.
        """
    @property
    def flags(self) -> int:
        """
        This property set the Flags for the Window.

        :type: int
        """
    @flags.setter
    def flags(self, arg1: int) -> None:
        """
        This property set the Flags for the Window.
        """
    @property
    def focus_policy(self) -> FocusPolicy:
        """
        How the Window gains focus.

        :type: FocusPolicy
        """
    @focus_policy.setter
    def focus_policy(self, arg1: FocusPolicy) -> None:
        """
        How the Window gains focus.
        """
    @property
    def focused(self) -> bool:
        """
        Read only property that is true when the window is focused.

        :type: bool
        """
    @property
    def frame(self) -> Frame:
        """
        The main layout of this window.

        :type: Frame
        """
    @property
    def height(self) -> float:
        """
        This property holds the window Height.

        :type: float
        """
    @height.setter
    def height(self, arg1: float) -> None:
        """
        This property holds the window Height.
        """
    @property
    def menu_bar(self) -> MenuBar:
        """
        :type: MenuBar
        """
    @property
    def noTabBar(self) -> bool:
        """
        setup the visibility of the TabBar Handle, this is the small triangle at the corner of the view If it is not shown then it is not possible to undock that window and it need to be closed/moved programatically

        :type: bool
        """
    @noTabBar.setter
    def noTabBar(self, arg1: bool) -> None:
        """
        setup the visibility of the TabBar Handle, this is the small triangle at the corner of the view If it is not shown then it is not possible to undock that window and it need to be closed/moved programatically
        """
    @property
    def padding_x(self) -> float:
        """
        This property set the padding to the frame on the X axis.

        :type: float
        """
    @padding_x.setter
    def padding_x(self, arg1: float) -> None:
        """
        This property set the padding to the frame on the X axis.
        """
    @property
    def padding_y(self) -> float:
        """
        This property set the padding to the frame on the Y axis.

        :type: float
        """
    @padding_y.setter
    def padding_y(self, arg1: float) -> None:
        """
        This property set the padding to the frame on the Y axis.
        """
    @property
    def position_x(self) -> float:
        """
        This property set/get the position of the window in the X Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.

        :type: float
        """
    @position_x.setter
    def position_x(self, arg1: float) -> None:
        """
        This property set/get the position of the window in the X Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.
        """
    @property
    def position_y(self) -> float:
        """
        This property set/get the position of the window in the Y Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.

        :type: float
        """
    @position_y.setter
    def position_y(self, arg1: float) -> None:
        """
        This property set/get the position of the window in the Y Axis. The default is kWindowFloatInvalid because we send the window position to the underlying system only if the position is explicitly set by the user. Otherwise the underlying system decides the position.
        """
    @property
    def raster_policy(self) -> RasterPolicy:
        """
        Determine how the content of the window should be rastered.

        :type: RasterPolicy
        """
    @raster_policy.setter
    def raster_policy(self, arg1: RasterPolicy) -> None:
        """
        Determine how the content of the window should be rastered.
        """
    @property
    def selected_in_dock(self) -> bool:
        """
        Has true if this window is currently selected in the dock. False otherwise. It's a read-only property.

        :type: bool
        """
    @property
    def tabBar_tooltip(self) -> str:
        """
        This property sets the tooltip when hovering over window's tabbar.

        :type: str
        """
    @tabBar_tooltip.setter
    def tabBar_tooltip(self, arg1: str) -> None:
        """
        This property sets the tooltip when hovering over window's tabbar.
        """
    @property
    def title(self) -> str:
        """
        This property holds the window's title.

        :type: str
        """
    @title.setter
    def title(self, arg1: str) -> None:
        """
        This property holds the window's title.
        """
    @property
    def visible(self) -> bool:
        """
        This property holds whether the window is visible.

        :type: bool
        """
    @visible.setter
    def visible(self, arg1: bool) -> None:
        """
        This property holds whether the window is visible.
        """
    @property
    def width(self) -> float:
        """
        This property holds the window Width.

        :type: float
        """
    @width.setter
    def width(self, arg1: float) -> None:
        """
        This property holds the window Width.
        """
    pass
class WindowHandle():
    """
    WindowHandle is a handle object to control any of the windows in Kit. It can be created any time, and if it's destroyed, the source window doesn't disappear.
    """
    def __repr__(self) -> str: ...
    def dock_in(self, window: WindowHandle, dock_position: DockPosition, ratio: float = 0.5) -> None: 
        """
        Dock the window to the existing window. It can split the window to two parts or it can convert the window to a docking tab.
        """
    def focus(self) -> None: 
        """
        Brings the window to the top. If it's a docked window, it makes the window currently visible in the dock.
        """
    def is_selected_in_dock(self) -> bool: 
        """
        Return true is the window is the current window in the docking area.
        """
    def notify_app_window_change(self, arg0: omni.appwindow._appwindow.IAppWindow) -> None: 
        """
        Notifies the UI window that the AppWindow it attached to has changed.
        """
    def undock(self) -> None: 
        """
        Undock the window and make it floating.
        """
    @property
    def dock_id(self) -> int:
        """
        Returns ID of the dock node this window is docked to.

        :type: int
        """
    @property
    def dock_order(self) -> int:
        """
        The position of the window in the dock.

        :type: int
        """
    @dock_order.setter
    def dock_order(self, arg1: int) -> None:
        """
        The position of the window in the dock.
        """
    @property
    def dock_tab_bar_enabled(self) -> bool:
        """
        Checks if the current docking space is disabled. The disabled docking tab bar can't be shown by the user.

        :type: bool
        """
    @dock_tab_bar_enabled.setter
    def dock_tab_bar_enabled(self, arg1: bool) -> None:
        """
        Checks if the current docking space is disabled. The disabled docking tab bar can't be shown by the user.
        """
    @property
    def dock_tab_bar_visible(self) -> bool:
        """
        Checks if the current docking space has the tab bar.

        :type: bool
        """
    @dock_tab_bar_visible.setter
    def dock_tab_bar_visible(self, arg1: bool) -> None:
        """
        Checks if the current docking space has the tab bar.
        """
    @property
    def docked(self) -> bool:
        """
        True if this window is docked. False otherwise.

        :type: bool
        """
    @property
    def height(self) -> float:
        """
        The height of the window in points.

        :type: float
        """
    @height.setter
    def height(self, arg1: float) -> None:
        """
        The height of the window in points.
        """
    @property
    def position_x(self) -> float:
        """
        The position of the window in points.

        :type: float
        """
    @position_x.setter
    def position_x(self, arg1: float) -> None:
        """
        The position of the window in points.
        """
    @property
    def position_y(self) -> float:
        """
        The position of the window in points.

        :type: float
        """
    @position_y.setter
    def position_y(self, arg1: float) -> None:
        """
        The position of the window in points.
        """
    @property
    def title(self) -> str:
        """
        The title of the window.

        :type: str
        """
    @property
    def visible(self) -> object:
        """
        Returns whether the window is visible.

        :type: object
        """
    @visible.setter
    def visible(self, arg1: bool) -> None:
        """
        Returns whether the window is visible.
        """
    @property
    def width(self) -> float:
        """
        The width of the window in points.

        :type: float
        """
    @width.setter
    def width(self, arg1: float) -> None:
        """
        The width of the window in points.
        """
    pass
class Workspace():
    """
    Workspace object provides access to the windows in Kit.
    """
    @staticmethod
    def clear() -> None: 
        """
        Undock all.
        """
    @staticmethod
    def get_dock_children_id(dock_id: int) -> object: 
        """
        Get two dock children of the given dock ID.
        true if the given dock ID has children


        ### Arguments:

            `dockId :`
                the given dock ID

            `first :`
                output. the first child dock ID

            `second :`
                output. the second child dock ID
        """
    @staticmethod
    def get_dock_id_height(dock_id: int) -> float: 
        """
        Returns the height of the docking node.
        It's different from the window height because it considers dock tab bar.


        ### Arguments:

            `dockId :`
                the given dock ID
        """
    @staticmethod
    def get_dock_id_width(dock_id: int) -> float: 
        """
        Returns the width of the docking node.


        ### Arguments:

            `dockId :`
                the given dock ID
        """
    @staticmethod
    def get_dock_position(dock_id: int) -> DockPosition: 
        """
        Returns the position of the given dock ID. Left/Right/Top/Bottom.
        """
    @staticmethod
    def get_docked_neighbours(member: WindowHandle) -> typing.List[WindowHandle]: 
        """
        Get all the windows that docked with the given widow.
        """
    @staticmethod
    def get_docked_windows(dock_id: int) -> typing.List[WindowHandle]: 
        """
        Get all the windows of the given dock ID.
        """
    @staticmethod
    def get_dpi_scale() -> float: 
        """
        Returns current DPI Scale.
        """
    @staticmethod
    def get_main_window_height() -> float: 
        """
        Get the height in points of the current main window.
        """
    @staticmethod
    def get_main_window_width() -> float: 
        """
        Get the width in points of the current main window.
        """
    @staticmethod
    def get_parent_dock_id(dock_id: int) -> int: 
        """
        Return the parent Dock Node ID.


        ### Arguments:

            `dockId :`
                the child Dock Node ID to get parent
        """
    @staticmethod
    def get_selected_window_index(dock_id: int) -> int: 
        """
        Get currently selected window inedx from the given dock id.
        """
    @staticmethod
    def get_show_window_titles() -> typing.List[str]: 
        """
        Get all window titles that have a show window callback.
        """
    @staticmethod
    def get_window(title: str) -> WindowHandle: 
        """
        Find Window by name.
        """
    @staticmethod
    def get_window_from_callback(*args, **kwargs) -> typing.Any: 
        """
        Find Window by window callback.
        """
    @staticmethod
    def get_windows() -> typing.List[WindowHandle]: 
        """
        Returns the list of windows ordered from back to front.
        If the window is a Omni::UI window, it can be upcasted.
        """
    @staticmethod
    def remove_window_visibility_changed_callback(fn: int) -> None: 
        """
        Remove the callback that is triggered when window's visibility changed.
        """
    @staticmethod
    def set_dock_id_height(dock_id: int, height: float) -> None: 
        """
        Set the height of the dock node.
        It also sets the height of parent nodes if necessary and modifies the height of siblings.


        ### Arguments:

            `dockId :`
                the given dock ID

            `height :`
                the given height
        """
    @staticmethod
    def set_dock_id_width(dock_id: int, width: float) -> None: 
        """
        Set the width of the dock node.
        It also sets the width of parent nodes if necessary and modifies the width of siblings.


        ### Arguments:

            `dockId :`
                the given dock ID

            `width :`
                the given width
        """
    @staticmethod
    def set_show_window_fn(title: str, fn: typing.Callable[[bool], None]) -> None: 
        """
        Add the callback to create a window with the given title. When the callback's argument is true, it's necessary to create the window. Otherwise remove.
        """
    @staticmethod
    def set_window_created_callback(fn: typing.Callable[[WindowHandle], None]) -> None: 
        """
        Addd the callback that is triggered when a new window is created.
        """
    @staticmethod
    def set_window_visibility_changed_callback(fn: typing.Callable[[str, bool], None]) -> int: 
        """
        Add the callback that is triggered when window's visibility changed.
        """
    @staticmethod
    def show_window(title: str, show: bool = True) -> bool: 
        """
        Makes the window visible or create the window with the callback provided with set_show_window_fn.
        true if the window is already created, otherwise it's necessary to wait one frame


        ### Arguments:

            `title :`
                the given window title

            `show :`
                true to show, false to hide
        """
    pass
class ZStack(Stack, Container, Widget):
    """
    Shortcut for Stack{eBackToFront}. The widgets are placed sorted in a Z-order in top right corner with suitable sizes.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct a stack with the widgets placed in a Z-order with sorting from background to foreground.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `direction : `
                This type is used to determine the direction of the layout. If the Stack's orientation is eLeftToRight the widgets are placed in a horizontal row, from left to right. If the Stack's orientation is eRightToLeft the widgets are placed in a horizontal row, from right to left. If the Stack's orientation is eTopToBottom, the widgets are placed in a vertical column, from top to bottom. If the Stack's orientation is eBottomToTop, the widgets are placed in a vertical column, from bottom to top. If the Stack's orientation is eBackToFront, the widgets are placed sorted in a Z-order in top right corner. If the Stack's orientation is eFrontToBack, the widgets are placed sorted in a Z-order in top right corner, the first widget goes to front.

            `content_clipping : `
                Determines if the child widgets should be clipped by the rectangle of this Stack.

            `spacing : `
                Sets a non-stretchable space in pixels between child items of this layout.

            `send_mouse_events_to_back : `
                When children of a Z-based stack overlap mouse events are normally sent to the topmost one. Setting this property true will invert that behavior, sending mouse events to the bottom-most child.

            `width : ui.Length`
                This property holds the width of the widget relative to its parent. Do not use this function to find the width of a screen.

            `height : ui.Length`
                This property holds the height of the widget relative to its parent. Do not use this function to find the height of a screen.

            `name : str`
                The name of the widget that user can set.

            `style_type_name_override : str`
                By default, we use typeName to look up the style. But sometimes it's necessary to use a custom name. For example, when a widget is a part of another widget. (Label is a part of Button) This property can override the name to use in style.

            `identifier : str`
                An optional identifier of the widget we can use to refer to it in queries.

            `visible : bool`
                This property holds whether the widget is visible.

            `visibleMin : float`
                If the current zoom factor and DPI is less than this value, the widget is not visible.

            `visibleMax : float`
                If the current zoom factor and DPI is bigger than this value, the widget is not visible.

            `tooltip : str`
                Set a basic tooltip for the widget, this will simply be a Label, it will follow the Tooltip style

            `tooltip_fn : Callable`
                Set dynamic tooltip that will be created dynamiclly the first time it is needed. the function is called inside a ui.Frame scope that the widget will be parented correctly.

            `tooltip_offset_x : float`
                Set the X tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `tooltip_offset_y : float`
                Set the Y tooltip offset in points. In a normal state, the tooltip position is linked to the mouse position. If the tooltip offset is non zero, the top left corner of the tooltip is linked to the top left corner of the widget, and this property defines the relative position the tooltip should be shown.

            `enabled : bool`
                This property holds whether the widget is enabled. In general an enabled widget handles keyboard and mouse events; a disabled widget does not. And widgets display themselves differently when they are disabled.

            `selected : bool`
                This property holds a flag that specifies the widget has to use eSelected state of the style.

            `checked : bool`
                This property holds a flag that specifies the widget has to use eChecked state of the style. It's on the Widget level because the button can have sub-widgets that are also should be checked.

            `dragging : bool`
                This property holds if the widget is being dragged.

            `opaque_for_mouse_events : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `explicit_hover : bool`
                If the widgets has callback functions it will by default not capture the events if it is the top most widget and setup this option to true, so they don't get routed to the child widgets either

            `skip_draw_when_clipped : bool`
                The flag that specifies if it's necessary to bypass the whole draw cycle if the bounding box is clipped with a scrolling frame. It's needed to avoid the limitation of 65535 primitives in a single draw list.

            `mouse_moved_fn : Callable`
                Sets the function that will be called when the user moves the mouse inside the widget. Mouse move events only occur if a mouse button is pressed while the mouse is being moved. void onMouseMoved(float x, float y, int32_t modifier)

            `mouse_pressed_fn : Callable`
                Sets the function that will be called when the user presses the mouse button inside the widget. The function should be like this: void onMousePressed(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier) Where 'button' is the number of the mouse button pressed. 'modifier' is the flag for the keyboard modifier key.

            `mouse_released_fn : Callable`
                Sets the function that will be called when the user releases the mouse button if this button was pressed inside the widget. void onMouseReleased(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_double_clicked_fn : Callable`
                Sets the function that will be called when the user presses the mouse button twice inside the widget. The function specification is the same as in setMousePressedFn. void onMouseDoubleClicked(float x, float y, int32_t button, carb::input::KeyboardModifierFlags modifier)

            `mouse_wheel_fn : Callable`
                Sets the function that will be called when the user uses mouse wheel on the focused window. The function specification is the same as in setMousePressedFn. void onMouseWheel(float x, float y, carb::input::KeyboardModifierFlags modifier)

            `mouse_hovered_fn : Callable`
                Sets the function that will be called when the user use mouse enter/leave on the focused window. function specification is the same as in setMouseHovedFn. void onMouseHovered(bool hovered)

            `drag_fn : Callable`
                Specify that this Widget is draggable, and set the callback that is attached to the drag operation.

            `accept_drop_fn : Callable`
                Specify that this Widget can accept specific drops and set the callback that is called to check if the drop can be accepted.

            `drop_fn : Callable`
                Specify that this Widget accepts drops and set the callback to the drop operation.

            `computed_content_size_changed_fn : Callable`
                Called when the size of the widget is changed.
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
def dock_window_in_window(arg0: str, arg1: str, arg2: DockPosition, arg3: float) -> bool:
    """
    place a named window in a specific docking position based on a target window name. We will find the target window dock node and insert this named window in it, either by spliting on ratio or on top if the windows is not found false is return, otherwise true
    """
def get_custom_glyph_code(file_path: str, font_style: FontStyle = FontStyle.NORMAL) -> str:
    """
    Get glyph code.

    Args:
        file_path (str): Path to svg file
        font_style(:class:`.FontStyle`): font style to use.
    """
def get_main_window_height() -> float:
    """
    Get the height in points of the current main window.
    """
def get_main_window_width() -> float:
    """
    Get the width in points of the current main window.
    """
WINDOW_FLAGS_FORCE_HORIZONTAL_SCROLLBAR = 32768
WINDOW_FLAGS_FORCE_VERTICAL_SCROLLBAR = 16384
WINDOW_FLAGS_MENU_BAR = 1024
WINDOW_FLAGS_MODAL = 134217728
WINDOW_FLAGS_NONE = 0
WINDOW_FLAGS_NO_BACKGROUND = 128
WINDOW_FLAGS_NO_CLOSE = 2147483648
WINDOW_FLAGS_NO_COLLAPSE = 32
WINDOW_FLAGS_NO_DOCKING = 2097152
WINDOW_FLAGS_NO_FOCUS_ON_APPEARING = 4096
WINDOW_FLAGS_NO_MOUSE_INPUTS = 512
WINDOW_FLAGS_NO_MOVE = 4
WINDOW_FLAGS_NO_RESIZE = 2
WINDOW_FLAGS_NO_SAVED_SETTINGS = 256
WINDOW_FLAGS_NO_SCROLLBAR = 8
WINDOW_FLAGS_NO_SCROLL_WITH_MOUSE = 16
WINDOW_FLAGS_NO_TITLE_BAR = 1
WINDOW_FLAGS_POPUP = 67108864
WINDOW_FLAGS_SHOW_HORIZONTAL_SCROLLBAR = 2048
