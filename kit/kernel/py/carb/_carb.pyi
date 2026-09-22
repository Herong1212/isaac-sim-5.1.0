from __future__ import annotations
import carb._carb
import typing
import carb._carb.filesystem
import carb._carb.logging

__all__ = [
    "ColorRgb",
    "ColorRgbDouble",
    "ColorRgba",
    "ColorRgbaDouble",
    "Double2",
    "Double3",
    "Double4",
    "Float2",
    "Float3",
    "Float4",
    "Framework",
    "Int2",
    "Int3",
    "Int4",
    "InterfaceDesc",
    "PluginDesc",
    "PluginHotReload",
    "PluginImplDesc",
    "Subscription",
    "Uint2",
    "Uint3",
    "Uint4",
    "Version",
    "answer_question",
    "breakpoint",
    "filesystem",
    "get_framework",
    "log",
    "logging",
    "wait_for_native_debugger"
]


class ColorRgb():
    def __eq__(self, arg0: ColorRgb) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: ColorRgb) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class ColorRgbDouble():
    def __eq__(self, arg0: ColorRgbDouble) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: ColorRgbDouble) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class ColorRgba():
    def __eq__(self, arg0: ColorRgba) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float, arg3: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: ColorRgba) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class ColorRgbaDouble():
    def __eq__(self, arg0: ColorRgbaDouble) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float, arg3: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: ColorRgbaDouble) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class Double2():
    def __eq__(self, arg0: Double2) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Double2) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class Double3():
    def __eq__(self, arg0: Double3) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Double3) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class Double4():
    def __eq__(self, arg0: Double4) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float, arg3: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Double4) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class Float2():
    """
    Pair of floating point values. These can be accessed via the named attributes, `x` & `y`, but
    also support sequence access, making them work where a list or tuple is expected.

    >>> f = carb.Float2(1.0, 2.0)
    >>> f[0]
    1.0
    >>> f.y
    2.0
    """
    def __eq__(self, arg0: Float2) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Float2) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class Float3():
    """
    A triplet of floating point values. These can be accessed via the named attributes, `x`, `y` & `z`, but
            also support sequence access, making them work where a list or tuple is expected.

            >>> v = [1, 2, 3]
            f = carb.Float3(v)
            >>> f[0]
            1.0
            >>> f.y
            2.0
            >>> f[2]
            3.0
            
    """
    def __eq__(self, arg0: Float3) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Float3) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class Float4():
    """
    A quadruplet of floating point values. These can be accessed via the named attributes, `x`, `y`, `z` & `w`,
            but also support sequence access, making them work where a list or tuple is expected.

            >>> v = [1, 2, 3, 4]
            f = carb.Float4(v)
            >>> f[0]
            1.0
            >>> f.y
            2.0
            >>> f[2]
            3.0
            >>> f.w
            4.0
            
    """
    def __eq__(self, arg0: Float4) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> float: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: float, arg3: float) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Float4) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
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
class Framework():
    def get_plugins(self) -> typing.List[PluginDesc]: ...
    def load_plugins(self, loaded_file_wildcards: typing.List[str] = [], search_paths: typing.List[str] = []) -> None: ...
    def start_plugin(self, plugin: str) -> None: ...
    def startup(self, argv: typing.List[str] = [], config: str = None, initial_plugins_search_paths: typing.List[str] = [], config_format: str = 'toml') -> None: ...
    def try_reload_plugins(self) -> None: ...
    def unload_all_plugins(self) -> None: ...
    pass
class Int2():
    def __eq__(self, arg0: Int2) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> int: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Int2) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
    @property
    def x(self) -> int:
        """
        :type: int
        """
    @x.setter
    def x(self, arg0: int) -> None:
        pass
    @property
    def y(self) -> int:
        """
        :type: int
        """
    @y.setter
    def y(self, arg0: int) -> None:
        pass
    __hash__ = None
    pass
class Int3():
    def __eq__(self, arg0: Int3) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> int: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: int, arg1: int, arg2: int) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Int3) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
    @property
    def x(self) -> int:
        """
        :type: int
        """
    @x.setter
    def x(self, arg0: int) -> None:
        pass
    @property
    def y(self) -> int:
        """
        :type: int
        """
    @y.setter
    def y(self, arg0: int) -> None:
        pass
    @property
    def z(self) -> int:
        """
        :type: int
        """
    @z.setter
    def z(self, arg0: int) -> None:
        pass
    __hash__ = None
    pass
class Int4():
    def __eq__(self, arg0: Int4) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> int: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: int, arg1: int, arg2: int, arg3: int) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Int4) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
    @property
    def w(self) -> int:
        """
        :type: int
        """
    @w.setter
    def w(self, arg0: int) -> None:
        pass
    @property
    def x(self) -> int:
        """
        :type: int
        """
    @x.setter
    def x(self, arg0: int) -> None:
        pass
    @property
    def y(self) -> int:
        """
        :type: int
        """
    @y.setter
    def y(self, arg0: int) -> None:
        pass
    @property
    def z(self) -> int:
        """
        :type: int
        """
    @z.setter
    def z(self, arg0: int) -> None:
        pass
    __hash__ = None
    pass
class InterfaceDesc():
    def __repr__(self) -> str: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def version(self) -> Version:
        """
        :type: Version
        """
    pass
class PluginDesc():
    @property
    def dependencies(self) -> typing.List[InterfaceDesc]:
        """
        :type: typing.List[InterfaceDesc]
        """
    @property
    def impl(self) -> PluginImplDesc:
        """
        :type: PluginImplDesc
        """
    @property
    def interfaces(self) -> typing.List[InterfaceDesc]:
        """
        :type: typing.List[InterfaceDesc]
        """
    @property
    def libPath(self) -> str:
        """
        :type: str
        """
    pass
class PluginHotReload():
    """
    Members:

      DISABLED

      ENABLED
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
    DISABLED: carb._carb.PluginHotReload # value = <PluginHotReload.DISABLED: 0>
    ENABLED: carb._carb.PluginHotReload # value = <PluginHotReload.ENABLED: 1>
    __members__: dict # value = {'DISABLED': <PluginHotReload.DISABLED: 0>, 'ENABLED': <PluginHotReload.ENABLED: 1>}
    pass
class PluginImplDesc():
    @property
    def author(self) -> str:
        """
        :type: str
        """
    @property
    def build(self) -> str:
        """
        :type: str
        """
    @property
    def description(self) -> str:
        """
        :type: str
        """
    @property
    def hotReload(self) -> PluginHotReload:
        """
        :type: PluginHotReload
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    pass
class Subscription():
    """
    Subscription holder.

    This object is returned by different subscription functions. Subscription lifetime is associated with this object. You can
    it while you need subscribed callback to be called. Then you can explicitly make it equal to `None` or call `unsubscribe` method or `del` it to unsubscribe.

    Quite common patter of usage is when you have a class which subscribes to various callbacks and you want to subscription to stay valid while class instance is alive.

    .. code-block:: python

        class Foo:
            def __init__(self):
                events = carb.events.get_events_interface()
                stream = events.create_event_stream()
                self._event_sub = stream.subscribe_to_pop(0, self._on_event)

            def _on_event(self, e):
                print(f'event {e}')

    >>> f = Foo()
    >>> # f receives some events
    >>> f._event_sub = None
    >>> f = None
    """
    def __init__(self, arg0: typing.Callable[[], None]) -> None: ...
    def unsubscribe(self) -> None: ...
    pass
class Uint2():
    def __eq__(self, arg0: Uint2) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> int: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Uint2) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
    @property
    def x(self) -> int:
        """
        :type: int
        """
    @x.setter
    def x(self, arg0: int) -> None:
        pass
    @property
    def y(self) -> int:
        """
        :type: int
        """
    @y.setter
    def y(self, arg0: int) -> None:
        pass
    __hash__ = None
    pass
class Uint3():
    def __eq__(self, arg0: Uint3) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> int: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: int, arg1: int, arg2: int) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Uint3) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
    @property
    def x(self) -> int:
        """
        :type: int
        """
    @x.setter
    def x(self, arg0: int) -> None:
        pass
    @property
    def y(self) -> int:
        """
        :type: int
        """
    @y.setter
    def y(self, arg0: int) -> None:
        pass
    @property
    def z(self) -> int:
        """
        :type: int
        """
    @z.setter
    def z(self, arg0: int) -> None:
        pass
    __hash__ = None
    pass
class Uint4():
    def __eq__(self, arg0: Uint4) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> int: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: int, arg1: int, arg2: int, arg3: int) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Sequence) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: Uint4) -> bool: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None: ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.Sequence) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
    @property
    def w(self) -> int:
        """
        :type: int
        """
    @w.setter
    def w(self, arg0: int) -> None:
        pass
    @property
    def x(self) -> int:
        """
        :type: int
        """
    @x.setter
    def x(self, arg0: int) -> None:
        pass
    @property
    def y(self) -> int:
        """
        :type: int
        """
    @y.setter
    def y(self, arg0: int) -> None:
        pass
    @property
    def z(self) -> int:
        """
        :type: int
        """
    @z.setter
    def z(self, arg0: int) -> None:
        pass
    __hash__ = None
    pass
class Version():
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: int, arg1: int) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def major(self) -> int:
        """
        :type: int
        """
    @property
    def minor(self) -> int:
        """
        :type: int
        """
    pass
def answer_question(question: str) -> str:
    """
    This function can answer some questions.

    It currently only answers a limited set of questions so don't expect it to know everything.

    Args:
        question: The question passed to the function, trailing question mark is not necessary and
            casing is not important.

    Returns:
        The answer to the question or empty string if it doesn't know the answer.
    """
def breakpoint() -> None:
    """
    Issues a hardware breakpoint.

    Warning: If a native debugger is not attached, this can cause an application
    error resulting in a crash.

    Args:
        None

    Returns:
        None
            
    """
def get_framework(*args, **kwargs) -> typing.Any:
    pass
def log(source: str, level: int, fileName: str, functionName: str, lineNumber: int, message: str) -> None:
    pass
def wait_for_native_debugger(timeout: float = -1.0, stop: bool = False, quiet: bool = False) -> bool:
    """
    Waits for a debugger to attach.

    Args:
        timeout: The time in seconds to wait. Negative values mean to wait forever.
                 A value of 0 will check if a native debugger is attached without
                 waiting. Optional, default value is -1.
        stop:    If True, a breakpoint is triggered immediately after a debugger
                 attaches. If a timeout is reached instead, no breakpoint is
                 triggered. Optional, default value is False.
        quiet:   When called if a debugger is not already attached a message is
                 printed to stdout unless this is True. Optional, default value is
                 False.

    Returns:
        True if a native debugger attached, False if a timeout is reached.
                 
    """
filesystem = carb._carb.filesystem
logging = carb._carb.logging
