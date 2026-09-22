from __future__ import annotations
import omni.ui_scene._scene
import typing
import carb._carb
import omni.ui._ui

__all__ = [
    "AbstractContainer",
    "AbstractGesture",
    "AbstractItem",
    "AbstractManipulatorItem",
    "AbstractManipulatorModel",
    "AbstractShape",
    "Arc",
    "ArcGesturePayload",
    "AspectRatioPolicy",
    "CameraModel",
    "ClickGesture",
    "Color4",
    "Cross",
    "Culling",
    "Curve",
    "CurveGesturePayload",
    "Dot",
    "DoubleClickGesture",
    "DragGesture",
    "GestureManager",
    "GestureState",
    "HoverGesture",
    "Image",
    "Label",
    "Line",
    "LineGesturePayload",
    "Manipulator",
    "ManipulatorGesture",
    "Matrix44",
    "MouseInput",
    "Points",
    "PointsGesturePayload",
    "PolygonMesh",
    "PolygonMeshGesturePayload",
    "Rectangle",
    "RectangleGesturePayload",
    "Scene",
    "SceneView",
    "Screen",
    "ScreenGesturePayload",
    "ScrollGesture",
    "ShapeGesture",
    "Space",
    "TexturedMesh",
    "TexturedMeshGesturePayload",
    "Transform",
    "TransformBasis",
    "Vector2",
    "Vector3",
    "Vector4",
    "Widget"
]


class AbstractContainer(AbstractItem):
    """
    Base class for all the items that have children.
    """
    def __enter__(self) -> AbstractContainer: ...
    def __exit__(self, arg0: object, arg1: object, arg2: object) -> None: ...
    def clear(self) -> None: 
        """
        Removes the container items from the container.
        """
    pass
class AbstractGesture():
    """
    The base class for the gestures to provides a way to capture mouse events in 3d scene.
    """
    class GesturePayload():
        @typing.overload
        def __init__(self, arg0: object, arg1: object, arg2: float) -> None: ...
        @typing.overload
        def __init__(self, arg0: AbstractGesture.GesturePayload) -> None: ...
        @property
        def item_closest_point(self) -> object:
            """
            :type: object
            """
        @property
        def ray_closest_point(self) -> object:
            """
            :type: object
            """
        @property
        def ray_distance(self) -> float:
            """
            :type: float
            """
        pass
    def __repr__(self) -> str: ...
    @typing.overload
    def get_gesture_payload(self) -> AbstractGesture.GesturePayload: 
        """
        Shortcut for sender.get_gesturePayload.
        OMNIUI_SCENE_API const*

        Shortcut for sender.get_gesturePayload.
        OMNIUI_SCENE_API const*
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> AbstractGesture.GesturePayload: ...
    def process(self) -> None: 
        """
        Process the gesture and call callbacks if necessary.
        """
    @property
    def gesture_payload(self) -> AbstractGesture.GesturePayload:
        """
        Shortcut for sender.get_gesturePayload.
        OMNIUI_SCENE_API const*

        :type: AbstractGesture.GesturePayload
        """
    @property
    def manager(self) -> GestureManager:
        """
        The Manager that controld this gesture.

        :type: GestureManager
        """
    @manager.setter
    def manager(self, arg1: GestureManager) -> None:
        """
        The Manager that controld this gesture.
        """
    @property
    def name(self) -> str:
        """
        The name of the object. It's used for debugging.

        :type: str
        """
    @name.setter
    def name(self, arg1: str) -> None:
        """
        The name of the object. It's used for debugging.
        """
    @property
    def state(self) -> GestureState:
        """
        Get the internal state of the gesture.

        :type: GestureState
        """
    @state.setter
    def state(self, arg1: GestureState) -> None:
        """
        Get the internal state of the gesture.
        """
    pass
class AbstractItem():
    """

    """
    def compute_visibility(self) -> bool: 
        """
        Calculate the effective visibility of this prim, as defined by its most ancestral invisible opinion, if any.
        """
    def transform_space(self, arg0: Space, arg1: Space, arg2: handle) -> object: 
        """
        Transform the given point from the coordinate system fromspace to the coordinate system tospace.
        """
    @property
    def scene_view(self) -> typing.Any:
        """
        The current SceneView this item is parented to.

        :type: typing.Any
        """
    @property
    def visible(self) -> bool:
        """
        This property holds whether the item is visible.

        :type: bool
        """
    @visible.setter
    def visible(self, arg1: bool) -> None:
        """
        This property holds whether the item is visible.
        """
    pass
class AbstractManipulatorItem():
    def __init__(self) -> None: ...
    pass
class CameraModel(AbstractManipulatorModel):
    """
    A model that holds projection and view matrices
    """
    def __init__(self, arg0: object, arg1: object) -> None: 
        """
        Initialize the camera with the given projection/view matrices.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `projection : `
                The camera projection matrix.

            `view : `
                The camera view matrix.
        """
    @property
    def projection(self) -> Matrix44:
        """
        The camera projection matrix.

        :type: Matrix44
        """
    @projection.setter
    def projection(self, arg1: handle) -> None:
        """
        The camera projection matrix.
        """
    @property
    def view(self) -> Matrix44:
        """
        The camera projection matrix.

        :type: Matrix44
        """
    @view.setter
    def view(self, arg1: handle) -> None:
        """
        The camera projection matrix.
        """
    pass
class AbstractManipulatorModel():
    """
    Bridge to data.
    Operates with double and int arrays.
    No strings.
    No tree, it's a flat list of items.
    Manipulator requires the model has specific items.
    """
    def __init__(self) -> None: ...
    def _item_changed(self, arg0: handle) -> None: 
        """
        Called when any data of the model is changed. It will notify the subscribed widgets.
        """
    def add_item_changed_fn(self, arg0: typing.Callable[[AbstractManipulatorModel, AbstractManipulatorItem], None]) -> int: 
        """
        Adds the function that will be called every time the value changes.
        The id of the callback that is used to remove the callback.
        """
    def get_as_bool(self, arg0: handle) -> bool: 
        """
        Shortcut for `get_as_ints` that returns the first item of the list.
        """
    def get_as_float(self, arg0: handle) -> float: 
        """
        Shortcut for `get_as_floats` that returns the first item of the list.
        """
    def get_as_floats(self, arg0: handle) -> typing.List[float]: 
        """
        Returns the Float values of the item.
        """
    def get_as_int(self, arg0: handle) -> int: 
        """
        Shortcut for `get_as_ints` that returns the first item of the list.
        """
    def get_as_ints(self, arg0: handle) -> typing.List[int]: 
        """
        Returns the int values of the item.
        """
    def get_item(self, arg0: str) -> AbstractManipulatorItem: 
        """
        Returns the items that represents the identifier.
        """
    def remove_item_changed_fn(self, arg0: int) -> None: 
        """
        Remove the callback by its id.


        ### Arguments:

            `id :`
                The id that addValueChangedFn returns.
        """
    def set_bool(self, arg0: handle, arg1: bool) -> None: 
        """
        Shortcut for `set_ints` that sets an array with the size of one.
        """
    def set_float(self, arg0: handle, arg1: float) -> None: 
        """
        Shortcut for `set_floats` that sets an array with the size of one.
        """
    def set_floats(self, arg0: handle, arg1: typing.List[float]) -> None: 
        """
        Sets the Float values of the item.
        """
    def set_int(self, arg0: handle, arg1: int) -> None: 
        """
        Shortcut for `set_ints` that sets an array with the size of one.
        """
    def set_ints(self, arg0: handle, arg1: typing.List[int]) -> None: 
        """
        Sets the int values of the item.
        """
    def subscribe_item_changed_fn(self, arg0: typing.Callable[[AbstractManipulatorModel, AbstractManipulatorItem], None]) -> carb._carb.Subscription: 
        """
        Adds the function that will be called every time the value changes.
        The id of the callback that is used to remove the callback.
        """
    pass
class Arc(AbstractShape, AbstractItem):
    """

    """
    def __init__(self, radius: float, **kwargs) -> None: 
        """
        Constructs Arc.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `begin : `
                The start angle of the arc. Angle placement and directions are (0 to 90): Y to Z, Z to X, X to Y

            `end : `
                The end angle of the arc. Angle placement and directions are (0 to 90): Y to Z, Z to X, X to Y

            `thickness : `
                The thickness of the line.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `color : `
                The color of the line.

            `tesselation : `
                Number of points on the curve.

            `axis : `
                The axis the circle plane is perpendicular to.

            `sector : `
                Draw two radii of the circle.

            `culling : `
                Draw two radii of the circle.

            `wireframe : `
                When true, it's a line. When false it's a mesh.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def get_gesture_payload(self) -> ArcGesturePayload: 
        """
        Contains all the information about the intersection.

        Contains all the information about the intersection at the specific state.
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> ArcGesturePayload: ...
    @property
    def axis(self) -> int:
        """
        The axis the circle plane is perpendicular to.

        :type: int
        """
    @axis.setter
    def axis(self, arg1: int) -> None:
        """
        The axis the circle plane is perpendicular to.
        """
    @property
    def begin(self) -> float:
        """
        The start angle of the arc. Angle placement and directions are (0 to 90): Y to Z, Z to X, X to Y

        :type: float
        """
    @begin.setter
    def begin(self, arg1: float) -> None:
        """
        The start angle of the arc. Angle placement and directions are (0 to 90): Y to Z, Z to X, X to Y
        """
    @property
    def color(self) -> object:
        """
        The color of the line.

        :type: object
        """
    @color.setter
    def color(self, arg1: handle) -> None:
        """
        The color of the line.
        """
    @property
    def culling(self) -> Culling:
        """
        Draw two radii of the circle.

        :type: Culling
        """
    @culling.setter
    def culling(self, arg1: Culling) -> None:
        """
        Draw two radii of the circle.
        """
    @property
    def end(self) -> float:
        """
        The end angle of the arc. Angle placement and directions are (0 to 90): Y to Z, Z to X, X to Y

        :type: float
        """
    @end.setter
    def end(self, arg1: float) -> None:
        """
        The end angle of the arc. Angle placement and directions are (0 to 90): Y to Z, Z to X, X to Y
        """
    @property
    def gesture_payload(self) -> ArcGesturePayload:
        """
        Contains all the information about the intersection.

        :type: ArcGesturePayload
        """
    @property
    def intersection_thickness(self) -> float:
        """
        The thickness of the line for the intersection.

        :type: float
        """
    @intersection_thickness.setter
    def intersection_thickness(self, arg1: float) -> None:
        """
        The thickness of the line for the intersection.
        """
    @property
    def radius(self) -> float:
        """
        :type: float
        """
    @radius.setter
    def radius(self, arg1: float) -> None:
        pass
    @property
    def sector(self) -> bool:
        """
        Draw two radii of the circle.

        :type: bool
        """
    @sector.setter
    def sector(self, arg1: bool) -> None:
        """
        Draw two radii of the circle.
        """
    @property
    def tesselation(self) -> int:
        """
        Number of points on the curve.

        :type: int
        """
    @tesselation.setter
    def tesselation(self, arg1: int) -> None:
        """
        Number of points on the curve.
        """
    @property
    def thickness(self) -> float:
        """
        The thickness of the line.

        :type: float
        """
    @thickness.setter
    def thickness(self, arg1: float) -> None:
        """
        The thickness of the line.
        """
    @property
    def wireframe(self) -> bool:
        """
        When true, it's a line. When false it's a mesh.

        :type: bool
        """
    @wireframe.setter
    def wireframe(self, arg1: bool) -> None:
        """
        When true, it's a line. When false it's a mesh.
        """
    pass
class AbstractShape(AbstractItem):
    """
    Base class for all the items that can be drawn and intersected with mouse pointer.
    """
    @typing.overload
    def get_gesture_payload(self) -> AbstractGesture.GesturePayload: 
        """
        Contains all the information about the intersection.

        Contains all the information about the intersection at the specific state.
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> AbstractGesture.GesturePayload: ...
    @property
    def gesture_payload(self) -> AbstractGesture.GesturePayload:
        """
        Contains all the information about the intersection.

        :type: AbstractGesture.GesturePayload
        """
    @property
    def gestures(self) -> typing.List[ShapeGesture]:
        """
        All the gestures assigned to this shape.

        :type: typing.List[ShapeGesture]
        """
    @gestures.setter
    def gestures(self, arg1: typing.List[ShapeGesture]) -> None:
        """
        All the gestures assigned to this shape.
        """
    pass
class ArcGesturePayload(AbstractGesture.GesturePayload):
    @property
    def angle(self) -> float:
        """
        :type: float
        """
    @property
    def culled(self) -> bool:
        """
        :type: bool
        """
    @property
    def distance_to_center(self) -> float:
        """
        :type: float
        """
    @property
    def moved(self) -> object:
        """
        :type: object
        """
    @property
    def moved_angle(self) -> float:
        """
        :type: float
        """
    @property
    def moved_distance_to_center(self) -> float:
        """
        :type: float
        """
    pass
class AspectRatioPolicy():
    """
    Members:

      STRETCH

      PRESERVE_ASPECT_FIT

      PRESERVE_ASPECT_CROP

      PRESERVE_ASPECT_VERTICAL

      PRESERVE_ASPECT_HORIZONTAL
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
    PRESERVE_ASPECT_CROP: omni.ui_scene._scene.AspectRatioPolicy # value = <AspectRatioPolicy.PRESERVE_ASPECT_CROP: 2>
    PRESERVE_ASPECT_FIT: omni.ui_scene._scene.AspectRatioPolicy # value = <AspectRatioPolicy.PRESERVE_ASPECT_FIT: 1>
    PRESERVE_ASPECT_HORIZONTAL: omni.ui_scene._scene.AspectRatioPolicy # value = <AspectRatioPolicy.PRESERVE_ASPECT_HORIZONTAL: 4>
    PRESERVE_ASPECT_VERTICAL: omni.ui_scene._scene.AspectRatioPolicy # value = <AspectRatioPolicy.PRESERVE_ASPECT_VERTICAL: 3>
    STRETCH: omni.ui_scene._scene.AspectRatioPolicy # value = <AspectRatioPolicy.STRETCH: 0>
    __members__: dict # value = {'STRETCH': <AspectRatioPolicy.STRETCH: 0>, 'PRESERVE_ASPECT_FIT': <AspectRatioPolicy.PRESERVE_ASPECT_FIT: 1>, 'PRESERVE_ASPECT_CROP': <AspectRatioPolicy.PRESERVE_ASPECT_CROP: 2>, 'PRESERVE_ASPECT_VERTICAL': <AspectRatioPolicy.PRESERVE_ASPECT_VERTICAL: 3>, 'PRESERVE_ASPECT_HORIZONTAL': <AspectRatioPolicy.PRESERVE_ASPECT_HORIZONTAL: 4>}
    pass
class ClickGesture(ShapeGesture, AbstractGesture):
    """
    The gesture that provides a way to capture click mouse event.
    """
    @staticmethod
    def __init__(*args, **kwargs) -> typing.Any: 
        """
        Constructs an gesture to track when the user clicked the mouse.


        ### Arguments:

            `onEnded :`
                Function that is called when the user clicked the mouse button.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `mouse_button : `
                The mouse button this gesture is watching.

            `modifiers : `
                The modifier that should be pressed to trigger this gesture.

            `on_ended_fn : `
                Called when the user releases the button.

            `name : `
                The name of the object. It's used for debugging.

            `manager : `
                The Manager that controld this gesture.
        """
    def __repr__(self) -> str: ...
    @staticmethod
    def call_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user releases the button.
        """
    def has_on_ended_fn(self) -> bool: 
        """
        Called when the user releases the button.
        """
    @staticmethod
    def set_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user releases the button.
        """
    @property
    def modifiers(self) -> int:
        """
        The modifier that should be pressed to trigger this gesture.

        :type: int
        """
    @modifiers.setter
    def modifiers(self, arg1: int) -> None:
        """
        The modifier that should be pressed to trigger this gesture.
        """
    @property
    def mouse_button(self) -> int:
        """
        The mouse button this gesture is watching.

        :type: int
        """
    @mouse_button.setter
    def mouse_button(self, arg1: int) -> None:
        """
        The mouse button this gesture is watching.
        """
    pass
class Color4():
    def __add__(self, arg0: Vector4) -> Vector4: ...
    def __eq__(self, arg0: Vector4) -> bool: ...
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __init__(self, c: Vector4) -> None: ...
    @typing.overload
    def __init__(self, r: float = 0.0) -> None: ...
    @typing.overload
    def __init__(self, r: float, g: float, b: float, a: float) -> None: ...
    def __repr__(self) -> str: ...
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @property
    def a(self) -> float:
        """
        :type: float
        """
    @a.setter
    def a(self, arg0: float) -> None:
        pass
    @property
    def b(self) -> float:
        """
        :type: float
        """
    @b.setter
    def b(self, arg0: float) -> None:
        pass
    @property
    def g(self) -> float:
        """
        :type: float
        """
    @g.setter
    def g(self, arg0: float) -> None:
        pass
    @property
    def r(self) -> float:
        """
        :type: float
        """
    @r.setter
    def r(self, arg0: float) -> None:
        pass
    __hash__ = None
    pass
class Culling():
    """
    Members:

      NONE

      BACK

      FRONT
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
    BACK: omni.ui_scene._scene.Culling # value = <Culling.BACK: 1>
    FRONT: omni.ui_scene._scene.Culling # value = <Culling.FRONT: 2>
    NONE: omni.ui_scene._scene.Culling # value = <Culling.NONE: 0>
    __members__: dict # value = {'NONE': <Culling.NONE: 0>, 'BACK': <Culling.BACK: 1>, 'FRONT': <Culling.FRONT: 2>}
    pass
class Curve(AbstractShape, AbstractItem):
    """
    Represents the curve.
    """
    class CurveType():
        """
        Members:

          LINEAR

          CUBIC
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
        CUBIC: omni.ui_scene._scene.Curve.CurveType # value = <CurveType.CUBIC: 1>
        LINEAR: omni.ui_scene._scene.Curve.CurveType # value = <CurveType.LINEAR: 0>
        __members__: dict # value = {'LINEAR': <CurveType.LINEAR: 0>, 'CUBIC': <CurveType.CUBIC: 1>}
        pass
    def __init__(self, arg0: object, **kwargs) -> None: 
        """
        Constructs Curve.


        ### Arguments:

            `positions :`
                List of positions

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `positions : `
                The list of positions which defines the curve. It has at least two positions. The curve has len(positions)-1

            `colors : `
                The list of colors which defines color per vertex. It has the same length as positions.

            `thicknesses : `
                The list of thicknesses which defines thickness per vertex. It has the same length as positions.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `curve_type : `
                The curve interpolation type.

            `tessellation : `
                The number of points per curve segment. It can't be less than 2.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def get_gesture_payload(self) -> CurveGesturePayload: 
        """
        Contains all the information about the intersection.

        Contains all the information about the intersection at the specific state.
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> CurveGesturePayload: ...
    @property
    def colors(self) -> object:
        """
        The list of colors which defines color per vertex. It has the same length as positions.

        :type: object
        """
    @colors.setter
    def colors(self, arg1: handle) -> None:
        """
        The list of colors which defines color per vertex. It has the same length as positions.
        """
    @property
    def curve_type(self) -> Curve.CurveType:
        """
        The curve interpolation type.

        :type: Curve.CurveType
        """
    @curve_type.setter
    def curve_type(self, arg1: Curve.CurveType) -> None:
        """
        The curve interpolation type.
        """
    @property
    def gesture_payload(self) -> CurveGesturePayload:
        """
        Contains all the information about the intersection.

        :type: CurveGesturePayload
        """
    @property
    def intersection_thicknesses(self) -> float:
        """
        The thickness of the line for the intersection.

        :type: float
        """
    @intersection_thicknesses.setter
    def intersection_thicknesses(self, arg1: float) -> None:
        """
        The thickness of the line for the intersection.
        """
    @property
    def positions(self) -> object:
        """
        The list of positions which defines the curve. It has at least two positions. The curve has len(positions)-1

        :type: object
        """
    @positions.setter
    def positions(self, arg1: handle) -> None:
        """
        The list of positions which defines the curve. It has at least two positions. The curve has len(positions)-1
        """
    @property
    def tesselation(self) -> int:
        """
        The number of points per curve segment. It can't be less than 2.

        :type: int
        """
    @tesselation.setter
    def tesselation(self, arg1: int) -> None:
        """
        The number of points per curve segment. It can't be less than 2.
        """
    @property
    def tessellation(self) -> int:
        """
        The number of points per curve segment. It can't be less than 2.

        :type: int
        """
    @tessellation.setter
    def tessellation(self, arg1: int) -> None:
        """
        The number of points per curve segment. It can't be less than 2.
        """
    @property
    def thicknesses(self) -> typing.List[float]:
        """
        The list of thicknesses which defines thickness per vertex. It has the same length as positions.

        :type: typing.List[float]
        """
    @thicknesses.setter
    def thicknesses(self, arg1: typing.List[float]) -> None:
        """
        The list of thicknesses which defines thickness per vertex. It has the same length as positions.
        """
    pass
class CurveGesturePayload(AbstractGesture.GesturePayload):
    @property
    def curve_distance(self) -> float:
        """
        :type: float
        """
    @property
    def moved(self) -> object:
        """
        :type: object
        """
    @property
    def moved_distance(self) -> float:
        """
        :type: float
        """
    pass
class DoubleClickGesture(ClickGesture, ShapeGesture, AbstractGesture):
    """
    The gesture that provides a way to capture double clicks.
    """
    @staticmethod
    def __init__(*args, **kwargs) -> typing.Any: 
        """
        Construct the gesture to track double clicks.


        ### Arguments:

            `onEnded :`
                Called when the user double clicked

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `mouse_button : `
                The mouse button this gesture is watching.

            `modifiers : `
                The modifier that should be pressed to trigger this gesture.

            `on_ended_fn : `
                Called when the user releases the button.

            `name : `
                The name of the object. It's used for debugging.

            `manager : `
                The Manager that controld this gesture.
        """
    def __repr__(self) -> str: ...
    @staticmethod
    def call_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user releases the button.
        """
    def has_on_ended_fn(self) -> bool: 
        """
        Called when the user releases the button.
        """
    @staticmethod
    def set_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user releases the button.
        """
    pass
class DragGesture(ShapeGesture, AbstractGesture):
    """
    The gesture that provides a way to capture click-and-drag mouse event.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Construct the gesture to track mouse drags.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `mouse_button : `
                Mouse button that should be active to start the gesture.

            `modifiers : `
                The keyboard modifier that should be active ti start the gesture.

            `check_mouse_moved : `
                The check_mouse_moved property is a boolean flag that determines whether the DragGesture should verify if the 2D screen position of the mouse has changed before invoking the on_changed method. This property is essential in a 3D environment, as changes in the camera position can result in the mouse pointing to different locations in the 3D world even when the 2D screen position remains unchanged.

        Usage
        When check_mouse_moved is set to True, the DragGesture will only call the on_changed method if the actual 2D screen position of the mouse has changed. This can be useful when you want to ensure that the on_changed method is only triggered when there is a genuine change in the mouse's 2D screen position.
        If check_mouse_moved is set to False, the DragGesture will not check for changes in the mouse's 2D screen position before calling the on_changed method. This can be useful when you want the on_changed method to be invoked even if the mouse's 2D screen position hasn't changed, such as when the camera position is altered, and the mouse now points to a different location in the 3D world.

            `on_began_fn : `
                Called if the callback is not set when the user clicks the mouse button.

            `on_changed_fn : `
                Called if the callback is not set when the user moves the clicked button.

            `on_ended_fn : `
                Called if the callback is not set when the user releases the mouse button.

            `name : `
                The name of the object. It's used for debugging.

            `manager : `
                The Manager that controld this gesture.
        """
    def __repr__(self) -> str: ...
    @staticmethod
    def call_on_began_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user starts drag.
        """
    @staticmethod
    def call_on_changed_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user is dragging.
        """
    @staticmethod
    def call_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user releases the mouse and finishes the drag.
        """
    def has_on_began_fn(self) -> bool: 
        """
        Called when the user starts drag.
        """
    def has_on_changed_fn(self) -> bool: 
        """
        Called when the user is dragging.
        """
    def has_on_ended_fn(self) -> bool: 
        """
        Called when the user releases the mouse and finishes the drag.
        """
    @staticmethod
    def set_on_began_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user starts drag.
        """
    @staticmethod
    def set_on_changed_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user is dragging.
        """
    @staticmethod
    def set_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user releases the mouse and finishes the drag.
        """
    @property
    def check_mouse_moved(self) -> bool:
        """
        The check_mouse_moved property is a boolean flag that determines whether the DragGesture should verify if the 2D screen position of the mouse has changed before invoking the on_changed method. This property is essential in a 3D environment, as changes in the camera position can result in the mouse pointing to different locations in the 3D world even when the 2D screen position remains unchanged.

        Usage
        When check_mouse_moved is set to True, the DragGesture will only call the on_changed method if the actual 2D screen position of the mouse has changed. This can be useful when you want to ensure that the on_changed method is only triggered when there is a genuine change in the mouse's 2D screen position.
        If check_mouse_moved is set to False, the DragGesture will not check for changes in the mouse's 2D screen position before calling the on_changed method. This can be useful when you want the on_changed method to be invoked even if the mouse's 2D screen position hasn't changed, such as when the camera position is altered, and the mouse now points to a different location in the 3D world.

        :type: bool
        """
    @check_mouse_moved.setter
    def check_mouse_moved(self, arg1: bool) -> None:
        """
        The check_mouse_moved property is a boolean flag that determines whether the DragGesture should verify if the 2D screen position of the mouse has changed before invoking the on_changed method. This property is essential in a 3D environment, as changes in the camera position can result in the mouse pointing to different locations in the 3D world even when the 2D screen position remains unchanged.

        Usage
        When check_mouse_moved is set to True, the DragGesture will only call the on_changed method if the actual 2D screen position of the mouse has changed. This can be useful when you want to ensure that the on_changed method is only triggered when there is a genuine change in the mouse's 2D screen position.
        If check_mouse_moved is set to False, the DragGesture will not check for changes in the mouse's 2D screen position before calling the on_changed method. This can be useful when you want the on_changed method to be invoked even if the mouse's 2D screen position hasn't changed, such as when the camera position is altered, and the mouse now points to a different location in the 3D world.
        """
    @property
    def modifiers(self) -> int:
        """
        The keyboard modifier that should be active ti start the gesture.

        :type: int
        """
    @modifiers.setter
    def modifiers(self, arg1: int) -> None:
        """
        The keyboard modifier that should be active ti start the gesture.
        """
    @property
    def mouse_button(self) -> int:
        """
        Mouse button that should be active to start the gesture.

        :type: int
        """
    @mouse_button.setter
    def mouse_button(self, arg1: int) -> None:
        """
        Mouse button that should be active to start the gesture.
        """
    pass
class GestureManager():
    """
    The object that controls batch processing and preventing of gestures. Typically each scene has a default manager and if the user wants to have own prevention logic, he can reimplement it.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:
        """
    @staticmethod
    def amend_input(*args, **kwargs) -> typing.Any: 
        """
        Called once a frame. Should be overriden to inject own input to the gestures.
        """
    def can_be_prevented(self, arg0: AbstractGesture) -> bool: 
        """
        Called per gesture. Determines if the gesture can be prevented.
        """
    def should_prevent(self, arg0: AbstractGesture, arg1: AbstractGesture) -> bool: 
        """
        Called per gesture. Determines if the gesture should be prevented with another gesture. Useful to resolve intersections.
        """
    pass
class GestureState():
    """
    Members:

      NONE

      POSSIBLE

      BEGAN

      CHANGED

      ENDED

      CANCELED

      PREVENTED
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
    BEGAN: omni.ui_scene._scene.GestureState # value = <GestureState.BEGAN: 2>
    CANCELED: omni.ui_scene._scene.GestureState # value = <GestureState.CANCELED: 5>
    CHANGED: omni.ui_scene._scene.GestureState # value = <GestureState.CHANGED: 3>
    ENDED: omni.ui_scene._scene.GestureState # value = <GestureState.ENDED: 4>
    NONE: omni.ui_scene._scene.GestureState # value = <GestureState.NONE: 0>
    POSSIBLE: omni.ui_scene._scene.GestureState # value = <GestureState.POSSIBLE: 1>
    PREVENTED: omni.ui_scene._scene.GestureState # value = <GestureState.PREVENTED: 6>
    __members__: dict # value = {'NONE': <GestureState.NONE: 0>, 'POSSIBLE': <GestureState.POSSIBLE: 1>, 'BEGAN': <GestureState.BEGAN: 2>, 'CHANGED': <GestureState.CHANGED: 3>, 'ENDED': <GestureState.ENDED: 4>, 'CANCELED': <GestureState.CANCELED: 5>, 'PREVENTED': <GestureState.PREVENTED: 6>}
    pass
class HoverGesture(ShapeGesture, AbstractGesture):
    """
    The gesture that provides a way to capture event when mouse enters/leaves the item.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructs an gesture to track when the user clicked the mouse.


        ### Arguments:

            `onEnded :`
                Function that is called when the user clicked the mouse button.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `mouse_button : `
                The mouse button this gesture is watching.

            `modifiers : `
                The modifier that should be pressed to trigger this gesture.

            `on_began_fn : `
                Called if the callback is not set and the mouse enters the item.

            `on_changed_fn : `
                Called if the callback is not set and the mouse is hovering the item.

            `on_ended_fn : `
                Called if the callback is not set and the mouse leaves the item.

            `name : `
                The name of the object. It's used for debugging.

            `manager : `
                The Manager that controld this gesture.
        """
    def __repr__(self) -> str: ...
    @staticmethod
    def call_on_began_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the mouse enters the item.
        """
    @staticmethod
    def call_on_changed_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the mouse is hovering the item.
        """
    @staticmethod
    def call_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the mouse leaves the item.
        """
    def has_on_began_fn(self) -> bool: 
        """
        Called when the mouse enters the item.
        """
    def has_on_changed_fn(self) -> bool: 
        """
        Called when the mouse is hovering the item.
        """
    def has_on_ended_fn(self) -> bool: 
        """
        Called when the mouse leaves the item.
        """
    @staticmethod
    def set_on_began_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the mouse enters the item.
        """
    @staticmethod
    def set_on_changed_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the mouse is hovering the item.
        """
    @staticmethod
    def set_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the mouse leaves the item.
        """
    @property
    def modifiers(self) -> int:
        """
        The modifier that should be pressed to trigger this gesture.

        :type: int
        """
    @modifiers.setter
    def modifiers(self, arg1: int) -> None:
        """
        The modifier that should be pressed to trigger this gesture.
        """
    @property
    def mouse_button(self) -> int:
        """
        The mouse button this gesture is watching.

        :type: int
        """
    @mouse_button.setter
    def mouse_button(self, arg1: int) -> None:
        """
        The mouse button this gesture is watching.
        """
    pass
class Image(Rectangle, AbstractShape, AbstractItem):
    """

    """
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
        PRESERVE_ASPECT_CROP: omni.ui_scene._scene.Image.FillPolicy # value = <FillPolicy.PRESERVE_ASPECT_CROP: 2>
        PRESERVE_ASPECT_FIT: omni.ui_scene._scene.Image.FillPolicy # value = <FillPolicy.PRESERVE_ASPECT_FIT: 1>
        STRETCH: omni.ui_scene._scene.Image.FillPolicy # value = <FillPolicy.STRETCH: 0>
        __members__: dict # value = {'STRETCH': <FillPolicy.STRETCH: 0>, 'PRESERVE_ASPECT_FIT': <FillPolicy.PRESERVE_ASPECT_FIT: 1>, 'PRESERVE_ASPECT_CROP': <FillPolicy.PRESERVE_ASPECT_CROP: 2>}
        pass
    @typing.overload
    def __init__(self, source_url: str, width: float = 1.0, height: float = 1.0, **kwargs) -> None: 
        """
        Created an image with the given URL.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `source_url : `
                This property holds the image URL. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `image_provider : `
                This property holds the image provider. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `fill_policy : `
                Define what happens when the source image has a different size than the item.

            `image_width : `
                The resolution for rasterization of svg and for ImageProvider.

            `image_height : `
                The resolution of rasterization of svg and for ImageProvider.

            `width : `
                The size of the rectangle.

            `height : `
                The size of the rectangle.

            `thickness : `
                The thickness of the line.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `color : `
                The color of the line.

            `axis : `
                The axis the rectangle is perpendicular to.

            `wireframe : `
                When true, it's a line. When false it's a mesh.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.

        Created an image with the given provider.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `source_url : `
                This property holds the image URL. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `image_provider : `
                This property holds the image provider. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `fill_policy : `
                Define what happens when the source image has a different size than the item.

            `image_width : `
                The resolution for rasterization of svg and for ImageProvider.

            `image_height : `
                The resolution of rasterization of svg and for ImageProvider.

            `width : `
                The size of the rectangle.

            `height : `
                The size of the rectangle.

            `thickness : `
                The thickness of the line.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `color : `
                The color of the line.

            `axis : `
                The axis the rectangle is perpendicular to.

            `wireframe : `
                When true, it's a line. When false it's a mesh.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.

        Created an empty image.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `source_url : `
                This property holds the image URL. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `image_provider : `
                This property holds the image provider. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `fill_policy : `
                Define what happens when the source image has a different size than the item.

            `image_width : `
                The resolution for rasterization of svg and for ImageProvider.

            `image_height : `
                The resolution of rasterization of svg and for ImageProvider.

            `width : `
                The size of the rectangle.

            `height : `
                The size of the rectangle.

            `thickness : `
                The thickness of the line.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `color : `
                The color of the line.

            `axis : `
                The axis the rectangle is perpendicular to.

            `wireframe : `
                When true, it's a line. When false it's a mesh.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def __init__(self, image_provider: ImageProvider, width: float = 1.0, height: float = 1.0, **kwargs) -> None: ...
    @typing.overload
    def __init__(self, width: float = 1.0, height: float = 1.0, **kwargs) -> None: ...
    @property
    def fill_policy(self) -> Image.FillPolicy:
        """
        Define what happens when the source image has a different size than the item.

        :type: Image.FillPolicy
        """
    @fill_policy.setter
    def fill_policy(self, arg1: Image.FillPolicy) -> None:
        """
        Define what happens when the source image has a different size than the item.
        """
    @property
    def image_height(self) -> int:
        """
        The resolution of rasterization of svg and for ImageProvider.

        :type: int
        """
    @image_height.setter
    def image_height(self, arg1: int) -> None:
        """
        The resolution of rasterization of svg and for ImageProvider.
        """
    @property
    def image_provider(self) -> ImageProvider:
        """
        This property holds the image provider. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

        :type: ImageProvider
        """
    @image_provider.setter
    def image_provider(self, arg1: ImageProvider) -> None:
        """
        This property holds the image provider. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.
        """
    @property
    def image_width(self) -> int:
        """
        The resolution for rasterization of svg and for ImageProvider.

        :type: int
        """
    @image_width.setter
    def image_width(self, arg1: int) -> None:
        """
        The resolution for rasterization of svg and for ImageProvider.
        """
    @property
    def source_url(self) -> str:
        """
        This property holds the image URL. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

        :type: str
        """
    @source_url.setter
    def source_url(self, arg1: str) -> None:
        """
        This property holds the image URL. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.
        """
    pass
class Label(AbstractShape, AbstractItem):
    """
    Defines a standard label for user interface items
    """
    def __init__(self, arg0: str, **kwargs) -> None: 
        """
        A standard label for user interface items.


        ### Arguments:

            `text :`
                The string with the text to display

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `color : `
                The color of the text.

            `size : `
                The font size.

            `alignment : `
                This property holds the alignment of the label's contents. By default, the contents of the label are left-aligned and vertically-centered.

            `text : `
                This property holds the label's text.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @property
    def alignment(self) -> omni.ui._ui.Alignment:
        """
        This property holds the alignment of the label's contents. By default, the contents of the label are left-aligned and vertically-centered.

        :type: omni.ui._ui.Alignment
        """
    @alignment.setter
    def alignment(self, arg1: omni.ui._ui.Alignment) -> None:
        """
        This property holds the alignment of the label's contents. By default, the contents of the label are left-aligned and vertically-centered.
        """
    @property
    def color(self) -> object:
        """
        The color of the text.

        :type: object
        """
    @color.setter
    def color(self, arg1: handle) -> None:
        """
        The color of the text.
        """
    @property
    def size(self) -> float:
        """
        The font size.

        :type: float
        """
    @size.setter
    def size(self, arg1: float) -> None:
        """
        The font size.
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
    pass
class Line(AbstractShape, AbstractItem):
    """

    """
    @typing.overload
    def __init__(self, **kwargs) -> None: 
        """
        A simple line.


        ### Arguments:

            `start :`
                The start point of the line

            `end :`
                The end point of the line

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `start : `
                The start point of the line.

            `end : `
                The end point of the line.

            `color : `
                The line color.

            `thickness : `
                The line thickness.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.

        A simple line.


        ### Arguments:

            `start :`
                The start point of the line

            `end :`
                The end point of the line

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `start : `
                The start point of the line.

            `end : `
                The end point of the line.

            `color : `
                The line color.

            `thickness : `
                The line thickness.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def __init__(self, arg0: object, arg1: object, **kwargs) -> None: ...
    @typing.overload
    def get_gesture_payload(self) -> LineGesturePayload: 
        """
        Contains all the information about the intersection.

        Contains all the information about the intersection at the specific state.
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> LineGesturePayload: ...
    @property
    def color(self) -> object:
        """
        The line color.

        :type: object
        """
    @color.setter
    def color(self, arg1: handle) -> None:
        """
        The line color.
        """
    @property
    def end(self) -> object:
        """
        The end point of the line.

        :type: object
        """
    @end.setter
    def end(self, arg1: handle) -> None:
        """
        The end point of the line.
        """
    @property
    def gesture_payload(self) -> LineGesturePayload:
        """
        Contains all the information about the intersection.

        :type: LineGesturePayload
        """
    @property
    def intersection_thickness(self) -> float:
        """
        The thickness of the line for the intersection.

        :type: float
        """
    @intersection_thickness.setter
    def intersection_thickness(self, arg1: float) -> None:
        """
        The thickness of the line for the intersection.
        """
    @property
    def start(self) -> object:
        """
        The start point of the line.

        :type: object
        """
    @start.setter
    def start(self, arg1: handle) -> None:
        """
        The start point of the line.
        """
    @property
    def thickness(self) -> float:
        """
        The line thickness.

        :type: float
        """
    @thickness.setter
    def thickness(self, arg1: float) -> None:
        """
        The line thickness.
        """
    pass
class LineGesturePayload(AbstractGesture.GesturePayload):
    @property
    def line_closest_point(self) -> object:
        """
        :type: object
        """
    @property
    def line_distance(self) -> float:
        """
        :type: float
        """
    @property
    def moved(self) -> object:
        """
        :type: object
        """
    pass
class Manipulator(AbstractContainer, AbstractItem):
    """
    The base object for the custom manipulators.
    """
    def __init__(self, **kwargs) -> None: ...
    def _process_gesture(self, arg0: object, arg1: GestureState, arg2: AbstractGesture.GesturePayload) -> None: 
        """
        Process the ManipulatorGestures that can be casted to the given type
        """
    def call_on_build_fn(self, arg0: Manipulator) -> None: 
        """
        Called when Manipulator is dirty to build the content. It's another way to build the manipulator's content on the case the user doesn't want to reimplement the class.
        """
    def has_on_build_fn(self) -> bool: 
        """
        Called when Manipulator is dirty to build the content. It's another way to build the manipulator's content on the case the user doesn't want to reimplement the class.
        """
    def invalidate(self) -> None: 
        """
        Make Manipulator dirty so onBuild will be executed in _preDrawContent.
        """
    def on_build(self) -> None: 
        """
        Called when Manipulator is dirty to build the content. It's another way to build the manipulator's content on the case the user doesn't want to reimplement the class.
        """
    @staticmethod
    def on_model_updated(*args, **kwargs) -> typing.Any: 
        """
        Called by the model when the model value is changed. The class should react to the changes.


        ### Arguments:

            `item :`
                The item in the model that is changed. If it's NULL, the root is changed.
        """
    def set_on_build_fn(self, fn: typing.Callable[[Manipulator], None]) -> None: 
        """
        Called when Manipulator is dirty to build the content. It's another way to build the manipulator's content on the case the user doesn't want to reimplement the class.
        """
    @property
    def gestures(self) -> typing.List[ManipulatorGesture]:
        """
        All the gestures assigned to this manipulator.

        :type: typing.List[ManipulatorGesture]
        """
    @gestures.setter
    def gestures(self, arg1: typing.List[ManipulatorGesture]) -> None:
        """
        All the gestures assigned to this manipulator.
        """
    @property
    def model(self) -> AbstractManipulatorModel:
        """
        Returns the current model.

        :type: AbstractManipulatorModel
        """
    @model.setter
    def model(self, arg1: AbstractManipulatorModel) -> None:
        """
        Returns the current model.
        """
    pass
class ManipulatorGesture(AbstractGesture):
    """
    The base class for the gestures to provides a way to capture events of the manipulator objects.
    """
    def __init__(self, **kwargs) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def sender(self) -> typing.Any:
        """
        Returns the relevant shape driving the gesture.

        :type: typing.Any
        """
    pass
class Matrix44():
    """
    Stores a 4x4 matrix of float elements. A basic type.
    Matrices are defined to be in row-major order.
    The matrix mode is required to define the matrix that resets the transformation to fit the geometry into NDC, Screen space, or rotate it to the camera direction.
    """
    def __eq__(self, arg0: Matrix44) -> bool: ...
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __init__(self, m: Matrix44) -> None: ...
    @typing.overload
    def __init__(self, x: float = 1.0) -> None: ...
    @typing.overload
    def __init__(self, a1: float, a2: float, a3: float, a4: float, a5: float, a6: float, a7: float, a8: float, a9: float, a10: float, a11: float, a12: float, a13: float, a14: float, a15: float, a16: float) -> None: ...
    @typing.overload
    def __mul__(self, arg0: Matrix44) -> Matrix44: ...
    @staticmethod
    @typing.overload
    def __mul__(*args, **kwargs) -> typing.Any: ...
    def __ne__(self, arg0: Matrix44) -> bool: ...
    def __repr__(self) -> str: ...
    def __rmul__(self, arg0: Matrix44) -> Matrix44: ...
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    def get_inverse(self) -> Matrix44: ...
    @staticmethod
    def get_rotation_matrix(x: float, y: float, z: float, degrees: bool = False) -> Matrix44: 
        """
        Creates a matrix to specify a rotation around each axis.


        ### Arguments:

            `degrees :`
                true if the angles are specified in degrees
        """
    @staticmethod
    def get_scale_matrix(x: float, y: float, z: float) -> Matrix44: 
        """
        Creates a matrix to specify a scaling with the given scale factor per axis.
        """
    @staticmethod
    def get_translation_matrix(x: float, y: float, z: float) -> Matrix44: 
        """
        Creates a matrix to specify a translation at the given coordinates.
        """
    def set_look_at_view(self, arg0: Matrix44) -> Matrix44: ...
    @property
    def inversed(self) -> Matrix44:
        """
        :type: Matrix44
        """
    __hash__ = None
    pass
class MouseInput():
    def __init__(self) -> None: ...
    @property
    def clicked(self) -> int:
        """
        :type: int
        """
    @clicked.setter
    def clicked(self, arg0: int) -> None:
        pass
    @property
    def double_clicked(self) -> int:
        """
        :type: int
        """
    @double_clicked.setter
    def double_clicked(self, arg0: int) -> None:
        pass
    @property
    def down(self) -> int:
        """
        :type: int
        """
    @down.setter
    def down(self, arg0: int) -> None:
        pass
    @property
    def modifiers(self) -> int:
        """
        :type: int
        """
    @modifiers.setter
    def modifiers(self, arg0: int) -> None:
        pass
    @property
    def mouse(self) -> Vector2:
        """
        :type: Vector2
        """
    @mouse.setter
    def mouse(self, arg0: Vector2) -> None:
        pass
    @property
    def mouse_direction(self) -> Vector3:
        """
        :type: Vector3
        """
    @mouse_direction.setter
    def mouse_direction(self, arg0: Vector3) -> None:
        pass
    @property
    def mouse_origin(self) -> Vector3:
        """
        :type: Vector3
        """
    @mouse_origin.setter
    def mouse_origin(self, arg0: Vector3) -> None:
        pass
    @property
    def mouse_wheel(self) -> Vector2:
        """
        :type: Vector2
        """
    @mouse_wheel.setter
    def mouse_wheel(self, arg0: Vector2) -> None:
        pass
    @property
    def released(self) -> int:
        """
        :type: int
        """
    @released.setter
    def released(self, arg0: int) -> None:
        pass
    pass
class Points(AbstractShape, AbstractItem):
    """
    Represents the point cloud.
    """
    def __init__(self, arg0: object, **kwargs) -> None: 
        """
        Constructs the point cloud object.


        ### Arguments:

            `positions :`
                List of positions

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `positions : `
                List with positions of the points.

            `colors : `
                List of colors of the points.

            `sizes : `
                List of point sizes.

            `intersection_sizes : `
                The size of the points for the intersection.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def get_gesture_payload(self) -> PointsGesturePayload: 
        """
        Contains all the information about the intersection.

        Contains all the information about the intersection at the specific state.
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> PointsGesturePayload: ...
    @property
    def colors(self) -> object:
        """
        List of colors of the points.

        :type: object
        """
    @colors.setter
    def colors(self, arg1: handle) -> None:
        """
        List of colors of the points.
        """
    @property
    def gesture_payload(self) -> PointsGesturePayload:
        """
        Contains all the information about the intersection.

        :type: PointsGesturePayload
        """
    @property
    def intersection_sizes(self) -> float:
        """
        The size of the points for the intersection.

        :type: float
        """
    @intersection_sizes.setter
    def intersection_sizes(self, arg1: float) -> None:
        """
        The size of the points for the intersection.
        """
    @property
    def positions(self) -> object:
        """
        List with positions of the points.

        :type: object
        """
    @positions.setter
    def positions(self, arg1: handle) -> None:
        """
        List with positions of the points.
        """
    @property
    def sizes(self) -> typing.List[float]:
        """
        List of point sizes.

        :type: typing.List[float]
        """
    @sizes.setter
    def sizes(self, arg1: typing.List[float]) -> None:
        """
        List of point sizes.
        """
    pass
class PointsGesturePayload(AbstractGesture.GesturePayload):
    @property
    def closest_point(self) -> int:
        """
        :type: int
        """
    @property
    def distance_to_point(self) -> float:
        """
        :type: float
        """
    @property
    def moved(self) -> object:
        """
        :type: object
        """
    pass
class PolygonMesh(AbstractShape, AbstractItem):
    """
    Encodes a mesh.
    """
    def __init__(self, positions: object, colors: object, vertex_counts: typing.List[int], vertex_indices: typing.List[int], **kwargs) -> None: 
        """
        Construct a mesh with predefined properties.


        ### Arguments:

            `positions :`
                Describes points in local space.

            `colors :`
                Describes colors per vertex.

            `vertexCounts :`
                The number of vertices in each face.

            `vertexIndices :`
                The list of the index of each vertex of each face in the mesh.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `positions : `
                The primary geometry attribute, describes points in local space.

            `colors : `
                Describes colors per vertex.

            `vertex_counts : `
                Provides the number of vertices in each face of the mesh, which is also the number of consecutive indices in vertex_indices that define the face. The length of this attribute is the number of faces in the mesh.

            `vertex_indices : `
                Flat list of the index (into the points attribute) of each vertex of each face in the mesh.

            `thicknesses : `
                When wireframe is true, it defines the thicknesses of lines.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `wireframe: `
                When true, the mesh is drawn as lines.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def get_gesture_payload(self) -> PolygonMeshGesturePayload: 
        """
        Contains all the information about the intersection.

        Contains all the information about the intersection at the specific state.
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> PolygonMeshGesturePayload: ...
    @property
    def colors(self) -> object:
        """
        Describes colors per vertex.

        :type: object
        """
    @colors.setter
    def colors(self, arg1: handle) -> None:
        """
        Describes colors per vertex.
        """
    @property
    def gesture_payload(self) -> PolygonMeshGesturePayload:
        """
        Contains all the information about the intersection.

        :type: PolygonMeshGesturePayload
        """
    @property
    def intersection_thicknesses(self) -> float:
        """
        The thickness of the line for the intersection.

        :type: float
        """
    @intersection_thicknesses.setter
    def intersection_thicknesses(self, arg1: float) -> None:
        """
        The thickness of the line for the intersection.
        """
    @property
    def positions(self) -> object:
        """
        The primary geometry attribute, describes points in local space.

        :type: object
        """
    @positions.setter
    def positions(self, arg1: handle) -> None:
        """
        The primary geometry attribute, describes points in local space.
        """
    @property
    def thicknesses(self) -> typing.List[float]:
        """
        When wireframe is true, it defines the thicknesses of lines.

        :type: typing.List[float]
        """
    @thicknesses.setter
    def thicknesses(self, arg1: typing.List[float]) -> None:
        """
        When wireframe is true, it defines the thicknesses of lines.
        """
    @property
    def vertex_counts(self) -> typing.List[int]:
        """
        Provides the number of vertices in each face of the mesh, which is also the number of consecutive indices in vertex_indices that define the face. The length of this attribute is the number of faces in the mesh.

        :type: typing.List[int]
        """
    @vertex_counts.setter
    def vertex_counts(self, arg1: typing.List[int]) -> None:
        """
        Provides the number of vertices in each face of the mesh, which is also the number of consecutive indices in vertex_indices that define the face. The length of this attribute is the number of faces in the mesh.
        """
    @property
    def vertex_indices(self) -> typing.List[int]:
        """
        Flat list of the index (into the points attribute) of each vertex of each face in the mesh.

        :type: typing.List[int]
        """
    @vertex_indices.setter
    def vertex_indices(self, arg1: typing.List[int]) -> None:
        """
        Flat list of the index (into the points attribute) of each vertex of each face in the mesh.
        """
    @property
    def wireframe(self) -> bool:
        """
        When true, the mesh is drawn as lines.

        :type: bool
        """
    @wireframe.setter
    def wireframe(self, arg1: bool) -> None:
        """
        When true, the mesh is drawn as lines.
        """
    pass
class PolygonMeshGesturePayload(AbstractGesture.GesturePayload):
    @property
    def face_id(self) -> int:
        """
        :type: int
        """
    @property
    def s(self) -> float:
        """
        :type: float
        """
    @property
    def t(self) -> float:
        """
        :type: float
        """
    pass
class Rectangle(AbstractShape, AbstractItem):
    """

    """
    def __init__(self, width: float = 1.0, height: float = 1.0, **kwargs) -> None: 
        """
        Construct a rectangle with predefined size.


        ### Arguments:

            `width :`
                The size of the rectangle

            `height :`
                The size of the rectangle

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `width : `
                The size of the rectangle.

            `height : `
                The size of the rectangle.

            `thickness : `
                The thickness of the line.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `color : `
                The color of the line.

            `axis : `
                The axis the rectangle is perpendicular to.

            `wireframe : `
                When true, it's a line. When false it's a mesh.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def get_gesture_payload(self) -> RectangleGesturePayload: 
        """
        Contains all the information about the intersection.

        Contains all the information about the intersection at the specific state.
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> RectangleGesturePayload: ...
    @property
    def axis(self) -> int:
        """
        The axis the rectangle is perpendicular to.

        :type: int
        """
    @axis.setter
    def axis(self, arg1: int) -> None:
        """
        The axis the rectangle is perpendicular to.
        """
    @property
    def color(self) -> object:
        """
        The color of the line.

        :type: object
        """
    @color.setter
    def color(self, arg1: handle) -> None:
        """
        The color of the line.
        """
    @property
    def gesture_payload(self) -> RectangleGesturePayload:
        """
        Contains all the information about the intersection.

        :type: RectangleGesturePayload
        """
    @property
    def height(self) -> float:
        """
        The size of the rectangle.

        :type: float
        """
    @height.setter
    def height(self, arg1: float) -> None:
        """
        The size of the rectangle.
        """
    @property
    def intersection_thickness(self) -> float:
        """
        The thickness of the line for the intersection.

        :type: float
        """
    @intersection_thickness.setter
    def intersection_thickness(self, arg1: float) -> None:
        """
        The thickness of the line for the intersection.
        """
    @property
    def thickness(self) -> float:
        """
        The thickness of the line.

        :type: float
        """
    @thickness.setter
    def thickness(self, arg1: float) -> None:
        """
        The thickness of the line.
        """
    @property
    def width(self) -> float:
        """
        The size of the rectangle.

        :type: float
        """
    @width.setter
    def width(self, arg1: float) -> None:
        """
        The size of the rectangle.
        """
    @property
    def wireframe(self) -> bool:
        """
        When true, it's a line. When false it's a mesh.

        :type: bool
        """
    @wireframe.setter
    def wireframe(self, arg1: bool) -> None:
        """
        When true, it's a line. When false it's a mesh.
        """
    pass
class RectangleGesturePayload(AbstractGesture.GesturePayload):
    @property
    def moved(self) -> object:
        """
        :type: object
        """
    @property
    def moved_s(self) -> float:
        """
        :type: float
        """
    @property
    def moved_t(self) -> float:
        """
        :type: float
        """
    @property
    def s(self) -> float:
        """
        :type: float
        """
    @property
    def t(self) -> float:
        """
        :type: float
        """
    pass
class Scene(AbstractContainer, AbstractItem):
    """
    Top level module string
    Represents the root of the scene and holds the shapes, gestures and managers.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructor
            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `visible : `
                This property holds whether the item is visible.
        """
    @property
    def draw_list_buffer_count(self) -> int:
        """
        Return the number of buffers used. Using for unit testing.

        :type: int
        """
    pass
class SceneView(omni.ui._ui.Widget):
    """
    The widget to render omni.ui.scene.
    """
    def __init__(self, model: AbstractManipulatorModel = None, **kwargs) -> None: 
        """
        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `aspect_ratio_policy : `
                Define what happens when the aspect ratio of the camera is different from the aspect ratio of the widget.

            `model : `
                The camera view matrix. It's a shortcut for Matrix44(SceneView.model.get_as_floats("view"))

            `screen_aspect_ratio : `
                Aspect ratio of the rendering screen. This screen will be fit to the widget. SceneView simulates the behavior of the Kit viewport where the rendered image (screen) fits into the viewport (widget), and the camera has multiple policies that modify the camera projection matrix's aspect ratio to match it to the screen aspect ratio. When screen_aspect_ratio is 0, Screen size matches the Widget bounds.

            `child_windows_input : `
                When it's false, the mouse events from other widgets inside the bounds are ignored. We need it to filter out mouse events from mouse events of widgets in `ui.VStack(content_clipping=1)`.

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
    def get_ray_from_ndc(self, ndc: Vector2) -> typing.Tuple[Vector3, Vector3]: 
        """
        Convert NDC 2D [-1..1] coordinates to 3D ray.
        """
    @property
    def aspect_ratio_policy(self) -> AspectRatioPolicy:
        """
        Define what happens when the aspect ratio of the camera is different from the aspect ratio of the widget.

        :type: AspectRatioPolicy
        """
    @aspect_ratio_policy.setter
    def aspect_ratio_policy(self, arg1: AspectRatioPolicy) -> None:
        """
        Define what happens when the aspect ratio of the camera is different from the aspect ratio of the widget.
        """
    @property
    def cache_draw_buffer(self) -> bool:
        """
        When it's true, the caching draw buffer optimization is enabled.

        :type: bool
        """
    @cache_draw_buffer.setter
    def cache_draw_buffer(self, arg1: bool) -> None:
        """
        When it's true, the caching draw buffer optimization is enabled.
        """
    @property
    def child_windows_input(self) -> bool:
        """
        When it's false, the mouse events from other widgets inside the bounds are ignored. We need it to filter out mouse events from mouse events of widgets in `ui.VStack(content_clipping=1)`.

        :type: bool
        """
    @child_windows_input.setter
    def child_windows_input(self, arg1: bool) -> None:
        """
        When it's false, the mouse events from other widgets inside the bounds are ignored. We need it to filter out mouse events from mouse events of widgets in `ui.VStack(content_clipping=1)`.
        """
    @property
    def model(self) -> AbstractManipulatorModel:
        """
        Returns the current model.

        :type: AbstractManipulatorModel
        """
    @model.setter
    def model(self, arg1: AbstractManipulatorModel) -> None:
        """
        Returns the current model.
        """
    @property
    def projection(self) -> Matrix44:
        """
        The camera projection matrix. It's a shortcut for Matrix44(SceneView.model.get_as_floats("projection"))

        :type: Matrix44
        """
    @projection.setter
    def projection(self, arg1: handle) -> None:
        """
        The camera projection matrix. It's a shortcut for Matrix44(SceneView.model.get_as_floats("projection"))
        """
    @property
    def scene(self) -> Scene:
        """
        The container that holds the shapes, gestures and managers.

        :type: Scene
        """
    @scene.setter
    def scene(self, arg1: Scene) -> None:
        """
        The container that holds the shapes, gestures and managers.
        """
    @property
    def screen_aspect_ratio(self) -> float:
        """
        Aspect ratio of the rendering screen. This screen will be fit to the widget. SceneView simulates the behavior of the Kit viewport where the rendered image (screen) fits into the viewport (widget), and the camera has multiple policies that modify the camera projection matrix's aspect ratio to match it to the screen aspect ratio. When screen_aspect_ratio is 0, Screen size matches the Widget bounds.

        :type: float
        """
    @screen_aspect_ratio.setter
    def screen_aspect_ratio(self, arg1: float) -> None:
        """
        Aspect ratio of the rendering screen. This screen will be fit to the widget. SceneView simulates the behavior of the Kit viewport where the rendered image (screen) fits into the viewport (widget), and the camera has multiple policies that modify the camera projection matrix's aspect ratio to match it to the screen aspect ratio. When screen_aspect_ratio is 0, Screen size matches the Widget bounds.
        """
    @property
    def view(self) -> Matrix44:
        """
        The camera view matrix. It's a shortcut for Matrix44(SceneView.model.get_as_floats("view"))

        :type: Matrix44
        """
    @view.setter
    def view(self, arg1: handle) -> None:
        """
        The camera view matrix. It's a shortcut for Matrix44(SceneView.model.get_as_floats("view"))
        """
    FLAG_WANT_CAPTURE_KEYBOARD = 1073741824
    pass
class Screen(AbstractShape, AbstractItem):
    """
    The empty shape that triggers all the gestures at any place. Is used to track gestures when the user clicked the empty space. For example for cameras.
    """
    def __init__(self, **kwargs) -> None: 
        """
        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def get_gesture_payload(self) -> ScreenGesturePayload: 
        """
        Contains all the information about the intersection.

        Contains all the information about the intersection at the specific state.
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> ScreenGesturePayload: ...
    @property
    def gesture_payload(self) -> ScreenGesturePayload:
        """
        Contains all the information about the intersection.

        :type: ScreenGesturePayload
        """
    pass
class ScreenGesturePayload(AbstractGesture.GesturePayload):
    @property
    def direction(self) -> object:
        """
        :type: object
        """
    @property
    def mouse(self) -> object:
        """
        :type: object
        """
    @property
    def mouse_moved(self) -> object:
        """
        :type: object
        """
    @property
    def moved(self) -> object:
        """
        :type: object
        """
    pass
class ScrollGesture(ShapeGesture, AbstractGesture):
    """
    The gesture that provides a way to capture mouse scroll event.
    """
    @staticmethod
    def __init__(*args, **kwargs) -> typing.Any: 
        """
        Constructs an gesture to track when the user clicked the mouse.


        ### Arguments:

            `onEnded :`
                Function that is called when the user clicked the mouse button.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `mouse_button : `
                The mouse button this gesture is watching.

            `modifiers : `
                The modifier that should be pressed to trigger this gesture.

            `on_ended_fn : `
                Called when the user scrolls.

            `name : `
                The name of the object. It's used for debugging.

            `manager : `
                The Manager that controld this gesture.
        """
    def __repr__(self) -> str: ...
    @staticmethod
    def call_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user scrolls.
        """
    def has_on_ended_fn(self) -> bool: 
        """
        Called when the user scrolls.
        """
    @staticmethod
    def set_on_ended_fn(*args, **kwargs) -> typing.Any: 
        """
        Called when the user scrolls.
        """
    @property
    def modifiers(self) -> int:
        """
        The modifier that should be pressed to trigger this gesture.

        :type: int
        """
    @modifiers.setter
    def modifiers(self, arg1: int) -> None:
        """
        The modifier that should be pressed to trigger this gesture.
        """
    @property
    def mouse_button(self) -> int:
        """
        The mouse button this gesture is watching.

        :type: int
        """
    @mouse_button.setter
    def mouse_button(self, arg1: int) -> None:
        """
        The mouse button this gesture is watching.
        """
    @property
    def scroll(self) -> object:
        """
        Returns the current scroll state.

        :type: object
        """
    pass
class ShapeGesture(AbstractGesture):
    """
    The base class for the gestures to provides a way to capture mouse events in 3d scene.
    """
    def __repr__(self) -> str: ...
    @property
    def raw_input(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def sender(self) -> typing.Any:
        """
        :type: typing.Any
        """
    pass
class Space():
    """
    Members:

      CURRENT

      WORLD

      OBJECT

      NDC

      SCREEN
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
    CURRENT: omni.ui_scene._scene.Space # value = <Space.CURRENT: 0>
    NDC: omni.ui_scene._scene.Space # value = <Space.NDC: 3>
    OBJECT: omni.ui_scene._scene.Space # value = <Space.OBJECT: 2>
    SCREEN: omni.ui_scene._scene.Space # value = <Space.SCREEN: 4>
    WORLD: omni.ui_scene._scene.Space # value = <Space.WORLD: 1>
    __members__: dict # value = {'CURRENT': <Space.CURRENT: 0>, 'WORLD': <Space.WORLD: 1>, 'OBJECT': <Space.OBJECT: 2>, 'NDC': <Space.NDC: 3>, 'SCREEN': <Space.SCREEN: 4>}
    pass
class TexturedMesh(PolygonMesh, AbstractShape, AbstractItem):
    """
    Encodes a polygonal mesh with free-form textures.
    """
    @typing.overload
    def __init__(self, source_url: str, uvs: object, positions: object, colors: object, vertex_counts: typing.List[int], vertex_indices: typing.List[int], legacy_flipped_v: bool = True, **kwargs) -> None: 
        """
        Construct a mesh with predefined properties.


        ### Arguments:

            `sourceUrl :`
                Describes the texture image url.

            `uvs :`
                Describes uvs for the image texture.

            `positions :`
                Describes points in local space.

            `colors :`
                Describes colors per vertex.

            `vertexCounts :`
                The number of vertices in each face.

            `vertexIndices :`
                The list of the index of each vertex of each face in the mesh.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `uvs : `
                This property holds the texture coordinates of the mesh.

            `source_url : `
                This property holds the image URL. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `image_provider : `
                This property holds the image provider. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `image_width : `
                The resolution for rasterization of svg and for ImageProvider.

            `image_height : `
                The resolution of rasterization of svg and for ImageProvider.

            `positions : `
                The primary geometry attribute, describes points in local space.

            `colors : `
                Describes colors per vertex.

            `vertex_counts : `
                Provides the number of vertices in each face of the mesh, which is also the number of consecutive indices in vertex_indices that define the face. The length of this attribute is the number of faces in the mesh.

            `vertex_indices : `
                Flat list of the index (into the points attribute) of each vertex of each face in the mesh.

            `thicknesses : `
                When wireframe is true, it defines the thicknesses of lines.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `wireframe: `
                When true, the mesh is drawn as lines.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.

        Construct a mesh with predefined properties.


        ### Arguments:

            `imageProvider :`
                Describes the texture image provider.

            `uvs :`
                Describes uvs for the image texture.

            `positions :`
                Describes points in local space.

            `colors :`
                Describes colors per vertex.

            `vertexCounts :`
                The number of vertices in each face.

            `vertexIndices :`
                The list of the index of each vertex of each face in the mesh.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `uvs : `
                This property holds the texture coordinates of the mesh.

            `source_url : `
                This property holds the image URL. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `image_provider : `
                This property holds the image provider. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

            `image_width : `
                The resolution for rasterization of svg and for ImageProvider.

            `image_height : `
                The resolution of rasterization of svg and for ImageProvider.

            `positions : `
                The primary geometry attribute, describes points in local space.

            `colors : `
                Describes colors per vertex.

            `vertex_counts : `
                Provides the number of vertices in each face of the mesh, which is also the number of consecutive indices in vertex_indices that define the face. The length of this attribute is the number of faces in the mesh.

            `vertex_indices : `
                Flat list of the index (into the points attribute) of each vertex of each face in the mesh.

            `thicknesses : `
                When wireframe is true, it defines the thicknesses of lines.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `wireframe: `
                When true, the mesh is drawn as lines.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def __init__(self, image_provider: omni.ui._ui.ImageProvider, uvs: object, positions: object, colors: object, vertex_counts: typing.List[int], vertex_indices: typing.List[int], legacy_flipped_v: bool = True, **kwargs) -> None: ...
    @typing.overload
    def get_gesture_payload(self) -> TexturedMeshGesturePayload: 
        """
        Contains all the information about the intersection.

        Contains all the information about the intersection at the specific state.
        """
    @typing.overload
    def get_gesture_payload(self, arg0: GestureState) -> TexturedMeshGesturePayload: ...
    @property
    def gesture_payload(self) -> TexturedMeshGesturePayload:
        """
        Contains all the information about the intersection.

        :type: TexturedMeshGesturePayload
        """
    @property
    def image_height(self) -> int:
        """
        The resolution of rasterization of svg and for ImageProvider.

        :type: int
        """
    @image_height.setter
    def image_height(self, arg1: int) -> None:
        """
        The resolution of rasterization of svg and for ImageProvider.
        """
    @property
    def image_provider(self) -> omni.ui._ui.ImageProvider:
        """
        This property holds the image provider. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

        :type: omni.ui._ui.ImageProvider
        """
    @image_provider.setter
    def image_provider(self, arg1: omni.ui._ui.ImageProvider) -> None:
        """
        This property holds the image provider. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.
        """
    @property
    def image_width(self) -> int:
        """
        The resolution for rasterization of svg and for ImageProvider.

        :type: int
        """
    @image_width.setter
    def image_width(self, arg1: int) -> None:
        """
        The resolution for rasterization of svg and for ImageProvider.
        """
    @property
    def source_url(self) -> str:
        """
        This property holds the image URL. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.

        :type: str
        """
    @source_url.setter
    def source_url(self, arg1: str) -> None:
        """
        This property holds the image URL. It can be an "omni:" path, a "file:" path, a direct path or the path relative to the application root directory.
        """
    @property
    def uvs(self) -> object:
        """
        This property holds the texture coordinates of the mesh.

        :type: object
        """
    @uvs.setter
    def uvs(self, arg1: handle) -> None:
        """
        This property holds the texture coordinates of the mesh.
        """
    pass
class TexturedMeshGesturePayload(PolygonMeshGesturePayload, AbstractGesture.GesturePayload):
    @property
    def u(self) -> float:
        """
        :type: float
        """
    @property
    def v(self) -> float:
        """
        :type: float
        """
    pass
class Transform(AbstractContainer, AbstractItem):
    """
    Transforms children with component affine transformations.
    """
    class LookAt():
        """
        Members:

          NONE

          CAMERA
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
        CAMERA: omni.ui_scene._scene.Transform.LookAt # value = <LookAt.CAMERA: 1>
        NONE: omni.ui_scene._scene.Transform.LookAt # value = <LookAt.NONE: 0>
        __members__: dict # value = {'NONE': <LookAt.NONE: 0>, 'CAMERA': <LookAt.CAMERA: 1>}
        pass
    @typing.overload
    def __init__(self, **kwargs) -> None: 
        """
        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `transform : `
                Single transformation matrix.

            `scale_to : `
                Which space the current transform will be rescaled before applying the matrix. It's useful to make the object the same size regardless the distance to the camera.

            `look_at : `
                Rotates this transform to align the direction with the camera.

            `basis : `
                A custom basis for representing this transform's coordinate system.

            `visible : `
                This property holds whether the item is visible.

        Constructor.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `transform : `
                Single transformation matrix.

            `scale_to : `
                Which space the current transform will be rescaled before applying the matrix. It's useful to make the object the same size regardless the distance to the camera.

            `look_at : `
                Rotates this transform to align the direction with the camera.

            `basis : `
                A custom basis for representing this transform's coordinate system.

            `visible : `
                This property holds whether the item is visible.
        """
    @typing.overload
    def __init__(self, arg0: object, **kwargs) -> None: ...
    @property
    def basis(self) -> TransformBasis:
        """
        A custom basis for representing this transform's coordinate system.

        :type: TransformBasis
        """
    @basis.setter
    def basis(self, arg1: TransformBasis) -> None:
        """
        A custom basis for representing this transform's coordinate system.
        """
    @property
    def look_at(self) -> Transform.LookAt:
        """
        Rotates this transform to align the direction with the camera.

        :type: Transform.LookAt
        """
    @look_at.setter
    def look_at(self, arg1: Transform.LookAt) -> None:
        """
        Rotates this transform to align the direction with the camera.
        """
    @property
    def scale_to(self) -> Space:
        """
        Which space the current transform will be rescaled before applying the matrix. It's useful to make the object the same size regardless the distance to the camera.

        :type: Space
        """
    @scale_to.setter
    def scale_to(self, arg1: Space) -> None:
        """
        Which space the current transform will be rescaled before applying the matrix. It's useful to make the object the same size regardless the distance to the camera.
        """
    @property
    def transform(self) -> Matrix44:
        """
        Single transformation matrix.

        :type: Matrix44
        """
    @transform.setter
    def transform(self, arg1: handle) -> None:
        """
        Single transformation matrix.
        """
    pass
class TransformBasis():
    def __init__(self, **kwargs) -> None: ...
    def get_matrix(self) -> Matrix44: ...
    pass
class Vector2():
    def __add__(self, arg0: Vector2) -> Vector2: ...
    def __eq__(self, arg0: Vector2) -> bool: ...
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __init__(self, v: Vector2) -> None: ...
    @typing.overload
    def __init__(self, x: float = 0.0) -> None: ...
    @typing.overload
    def __init__(self, x: float, y: float) -> None: ...
    def __repr__(self) -> str: ...
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    def get_length(self) -> float: ...
    def get_normalized(self) -> Vector2: ...
    @property
    def x(self) -> float:
        """
        :type: float
        """
    @x.setter
    def x(self, arg0: float) -> None:
        pass
    @property
    def y(self) -> float:
        """
        :type: float
        """
    @y.setter
    def y(self, arg0: float) -> None:
        pass
    __hash__ = None
    pass
class Vector3():
    def __add__(self, arg0: Vector3) -> Vector3: ...
    def __eq__(self, arg0: Vector3) -> bool: ...
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __init__(self, v: Vector3) -> None: ...
    @typing.overload
    def __init__(self, x: float = 0.0) -> None: ...
    @typing.overload
    def __init__(self, x: float, y: float, z: float) -> None: ...
    def __matmul__(self, arg0: Vector3) -> float: ...
    def __mul__(self, arg0: Vector3) -> Vector3: ...
    def __repr__(self) -> str: ...
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    def get_length(self) -> float: ...
    def get_normalized(self) -> Vector3: ...
    @property
    def x(self) -> float:
        """
        :type: float
        """
    @x.setter
    def x(self, arg0: float) -> None:
        pass
    @property
    def y(self) -> float:
        """
        :type: float
        """
    @y.setter
    def y(self, arg0: float) -> None:
        pass
    @property
    def z(self) -> float:
        """
        :type: float
        """
    @z.setter
    def z(self, arg0: float) -> None:
        pass
    __hash__ = None
    pass
class Vector4():
    def __add__(self, arg0: Vector4) -> Vector4: ...
    def __eq__(self, arg0: Vector4) -> bool: ...
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __init__(self, v: Vector4) -> None: ...
    @typing.overload
    def __init__(self, x: float = 0.0) -> None: ...
    @typing.overload
    def __init__(self, x: float, y: float, z: float, w: float) -> None: ...
    @typing.overload
    def __init__(self, v: Vector3, w: float) -> None: ...
    def __repr__(self) -> str: ...
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    def get_length(self) -> float: ...
    def get_normalized(self) -> Vector4: ...
    @property
    def w(self) -> float:
        """
        :type: float
        """
    @w.setter
    def w(self, arg0: float) -> None:
        pass
    @property
    def x(self) -> float:
        """
        :type: float
        """
    @x.setter
    def x(self, arg0: float) -> None:
        pass
    @property
    def y(self) -> float:
        """
        :type: float
        """
    @y.setter
    def y(self, arg0: float) -> None:
        pass
    @property
    def z(self) -> float:
        """
        :type: float
        """
    @z.setter
    def z(self, arg0: float) -> None:
        pass
    __hash__ = None
    pass
class Widget(Rectangle, AbstractShape, AbstractItem):
    """
    The shape that contains the omni.ui widgets. It automatically creates IAppWindow and transfers its content to the texture of the rectangle. It interacts with the mouse and sends the mouse events to the underlying window, so interacting with the UI on this rectangle is smooth for the user.
    """
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
        PRESERVE_ASPECT_CROP: omni.ui_scene._scene.Widget.FillPolicy # value = <FillPolicy.PRESERVE_ASPECT_CROP: 2>
        PRESERVE_ASPECT_FIT: omni.ui_scene._scene.Widget.FillPolicy # value = <FillPolicy.PRESERVE_ASPECT_FIT: 1>
        STRETCH: omni.ui_scene._scene.Widget.FillPolicy # value = <FillPolicy.STRETCH: 0>
        __members__: dict # value = {'STRETCH': <FillPolicy.STRETCH: 0>, 'PRESERVE_ASPECT_FIT': <FillPolicy.PRESERVE_ASPECT_FIT: 1>, 'PRESERVE_ASPECT_CROP': <FillPolicy.PRESERVE_ASPECT_CROP: 2>}
        pass
    class UpdatePolicy():
        """
        Members:

          ON_DEMAND

          ALWAYS

          ON_MOUSE_HOVERED
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
        ALWAYS: omni.ui_scene._scene.Widget.UpdatePolicy # value = <UpdatePolicy.ALWAYS: 1>
        ON_DEMAND: omni.ui_scene._scene.Widget.UpdatePolicy # value = <UpdatePolicy.ON_DEMAND: 0>
        ON_MOUSE_HOVERED: omni.ui_scene._scene.Widget.UpdatePolicy # value = <UpdatePolicy.ON_MOUSE_HOVERED: 2>
        __members__: dict # value = {'ON_DEMAND': <UpdatePolicy.ON_DEMAND: 0>, 'ALWAYS': <UpdatePolicy.ALWAYS: 1>, 'ON_MOUSE_HOVERED': <UpdatePolicy.ON_MOUSE_HOVERED: 2>}
        pass
    def __init__(self, width: float, height: float, **kwargs) -> None: 
        """
        Created an empty image.

            `kwargs : dict`
                See below

        ### Keyword Arguments:

            `fill_policy : `
                Define what happens when the source image has a different size than the item.

            `update_policy : `
                Define when to redraw the widget.

            `resolution_scale : `
                The resolution scale of the widget.

            `resolution_width : `
                The resolution of the widget framebuffer.

            `resolution_height : `
                The resolution of the widget framebuffer.

            `width : `
                The size of the rectangle.

            `height : `
                The size of the rectangle.

            `thickness : `
                The thickness of the line.

            `intersection_thickness : `
                The thickness of the line for the intersection.

            `color : `
                The color of the line.

            `axis : `
                The axis the rectangle is perpendicular to.

            `wireframe : `
                When true, it's a line. When false it's a mesh.

            `gesture : `
                All the gestures assigned to this shape.

            `gestures : `
                All the gestures assigned to this shape.

            `visible : `
                This property holds whether the item is visible.
        """
    def invalidate(self) -> None: 
        """
        Rebuild and recapture the widgets at the next frame. If
        frame
        build_fn
        """
    @property
    def fill_policy(self) -> Widget.FillPolicy:
        """
        Define what happens when the source image has a different size than the item.

        :type: Widget.FillPolicy
        """
    @fill_policy.setter
    def fill_policy(self, arg1: Widget.FillPolicy) -> None:
        """
        Define what happens when the source image has a different size than the item.
        """
    @property
    def frame(self) -> omni.ui._ui.Frame:
        """
        Return the main frame of the widget.

        :type: omni.ui._ui.Frame
        """
    @property
    def resolution_height(self) -> int:
        """
        The resolution of the widget framebuffer.

        :type: int
        """
    @resolution_height.setter
    def resolution_height(self, arg1: int) -> None:
        """
        The resolution of the widget framebuffer.
        """
    @property
    def resolution_scale(self) -> float:
        """
        The resolution scale of the widget.

        :type: float
        """
    @resolution_scale.setter
    def resolution_scale(self, arg1: float) -> None:
        """
        The resolution scale of the widget.
        """
    @property
    def resolution_width(self) -> int:
        """
        The resolution of the widget framebuffer.

        :type: int
        """
    @resolution_width.setter
    def resolution_width(self, arg1: int) -> None:
        """
        The resolution of the widget framebuffer.
        """
    @property
    def update_policy(self) -> Widget.UpdatePolicy:
        """
        Define when to redraw the widget.

        :type: Widget.UpdatePolicy
        """
    @update_policy.setter
    def update_policy(self, arg1: Widget.UpdatePolicy) -> None:
        """
        Define when to redraw the widget.
        """
    pass
def Cross(arg0: handle, arg1: handle) -> object:
    pass
def Dot(arg0: handle, arg1: handle) -> float:
    pass
