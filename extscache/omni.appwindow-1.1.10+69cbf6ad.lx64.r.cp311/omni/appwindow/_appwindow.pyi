from __future__ import annotations
import omni.appwindow._appwindow
import typing
import carb._carb
import carb.events._events

__all__ = [
    "IAppWindow",
    "IAppWindowFactory",
    "POSITION_CENTERED",
    "POSITION_UNSET",
    "WindowType",
    "acquire_app_window_factory_interface",
    "get_default_app_window"
]


class IAppWindow():
    """
    Application window carb object
    """
    def broadcast_input_blocking_state(self, should_block: bool) -> None: 
        """
        Sets the forced rejecting of all input events for all device types.

        Args:
            should_block: Whether we should block the device input or not.
        """
    def focus(self) -> None: 
        """
        Set the application window in focus.
        """
    def get_action_mapping_set_path(self) -> str: 
        """
        Gets current action mapping set settings path.

        Return:
            The action mapping set settings path.
        """
    def get_clipboard(self) -> str: 
        """
        Gets the text from the clipboard associated with the window.

        Return:
            The text in the window's clipboard.
        """
    def get_cursor_blink(self) -> bool: 
        """
        Gets the cursor (caret) blinks state in input fields

        Return:
            True if cursor (caret) blinks in input fields.
        """
    def get_dpi_scale(self) -> float: 
        """
        Gets the DPI scale.

        Return:
            The DPI scale.
        """
    def get_dpi_scale_override(self) -> float: 
        """
        Gets DPI scale override.

        Return:
            DPI scale override.
        """
    @staticmethod
    def get_gamepad(*args, **kwargs) -> typing.Any: 
        """
        Gets the gamepads associated available.

        Return:
            The window gamepad or nullptr if index is invalid.
        """
    def get_height(self) -> int: 
        """
        Get the window height.

        Return:
            The window height.
        """
    @staticmethod
    def get_input_blocking_state(*args, **kwargs) -> typing.Any: 
        """
        Gets whether the input for a certain device types is being blocked.

        Args:
            device_type: The input device type, e.g. keyboard, mouse or gamepad.

        Return:
            Whether the input for a certain device types is being blocked.
        """
    @staticmethod
    def get_keyboard(*args, **kwargs) -> typing.Any: 
        """
        Gets the keyboard associated with the window.

        Return:
            The window keyboard.
        """
    @staticmethod
    def get_mouse(*args, **kwargs) -> typing.Any: 
        """
        Gets the mouse associated with the window.

        Return:
            The window mouse.
        """
    def get_position(self) -> carb._carb.Int2: 
        """
        Get the window position.

        Return:
            The window position.
        """
    def get_size(self) -> carb._carb.Uint2: 
        """
        Get the window size.

        Return:
            The window size.
        """
    def get_title(self) -> str: 
        """
        Gets the window title.

        Return:
            The window title.
        """
    def get_ui_scale(self) -> float: 
        """
        Gets the UI scale. Includes UI scale multiplier and OS DPI scale.

        Return:
            UI scale. Includes UI scale multiplier and OS DPI scale.
        """
    def get_width(self) -> int: 
        """
        Get the window width.

        Return:
            The window width.
        """
    @staticmethod
    def get_window(*args, **kwargs) -> typing.Any: 
        """
        Get the Carbonite window the editor is working with, or nullptr if headless.

        Return:
            Carbonite window the editor is working with, or nullptr if headless.
        """
    def get_window_close_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Gets the event stream that fires events on window close.

        Return:
            The event stream that fires events on window close.
        """
    def get_window_content_scale_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Get the event stream that fires events on window DPI scale change.

        Content scale event stream provides DPI and "real DPI". The first one is affected by the DPI override,
        while the second one is raw hardware DPI induced this event.

        Return:
            The event stream that fires events on window DPI scale change.
        """
    def get_window_drop_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Get the event stream that fires events on window drag-n-drop events.

        Return:
            The event stream that fires events on window drag-n-drop events.
        """
    def get_window_focus_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Get the event stream that fires events on window focus change.

        Return:
            The event stream that fires events on window focus change.
        """
    def get_window_minimize_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Get the event stream that fires events on window minimize change.

        Return:
            The event stream that fires events on window minimize change.
        """
    def get_window_move_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Gets the event stream that fires events on window move.

        Return:
            The event stream that fires events on window move.
        """
    def get_window_resize_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Gets the event stream that fires events on window resize.

        Return:
            The event stream that fires events on window resize.
        """
    def is_focused(self) -> bool: 
        """
        Returns True if the application window is focused; False if not in focus.
        """
    def is_fullscreen(self) -> bool: 
        """
        Gets the fullscreen state of editor Window.

        Return:
            True if Editor is fullscreen.
        """
    def is_maximized(self) -> bool: 
        """
        Gets the maxinized state of editor Window.

        Return:
            True if Editor is maximized.
        """
    def maximize_window(self) -> None: 
        """
        Maximize the editor window.
        """
    def move(self, x: int, y: int) -> None: 
        """
        Move the Window.

        Args:
            x: The x coordinate of the window.
            y: The y coordinate of the window.
        """
    def resize(self, width: int, height: int) -> None: 
        """
        Resizes the window.
        Args:
            width: The width of the window.
            height: The height of the window.
        """
    def restore_window(self) -> None: 
        """
        Restore the editor window (exit maximize/minimize).
        """
    def set_clipboard(self, text: str) -> None: 
        """
        Sets the text in the clipboard associated with the window.

        Args:
            text: The text in the window's clipboard.
        """
    def set_dpi_scale_override(self, dpi_scale_override: float) -> None: 
        """
        Sets the DPI scale override. Negative value means no override.

        Args:
            dpi_scale_override: DPI scale overrides.
        """
    def set_fullscreen(self, fullscreen: bool) -> None: 
        """
        Sets fullscreen state of editor Window.

        Args:
            fullscreen: true to set Editor Window to fullscreen.
        """
    @staticmethod
    def set_input_blocking_state(*args, **kwargs) -> typing.Any: 
        """
        Sets the forced rejecting of all input events from a certain device type.

        Args:
            device_type: The input device type, e.g. keyboard, mouse or gamepad.
            should_block: Whether we should block the device input or not.
        """
    def shutdown(self) -> bool: 
        """
        Deinitializes the window.

        Return:
            Whether the shutdown operation was completed successfully.
        """
    def startup(self, name: str = '') -> bool: 
        """
        Initializes the window taking parameters from carb::settings.

        Args:
            name: Name that identifies the window, can be nullptr.
        Return:
            Whether the startup operation was completed successfully.
        """
    def startup_with_desc(self, title: str, width: int, height: int, x: int = 18446744073709551614, y: int = 18446744073709551614, decorations: bool = True, resize: bool = True, always_on_top: bool = False, scale_to_monitor: bool = True, dpi_scale_override: float = -1.0, cursor_blink: bool = True) -> None: 
        """
        Initializes the window with custom description.

        Args:
            title: the window title.
            width: the window width.
            height: the window height.
            x: the x coordinate of the window.
            y: the y coordinate of the window.
            decorations: if window has full decorations.
            resize: if allows window resize.
            always_on_top: if the window is always on top.
            scale_to_monitor: if the scale fits to the monitor size.
            dpi_scale_override: DPI scale overrides.
            cursor_blink: if cursor (caret) blinks in input fields or not.

        Return:
            Whether the startup operation was completed successfully.
        """
    def update(self, dt: float) -> None: 
        """
        Call one update loop iteration on application.

        Normally, explicitly calling update is not required, as in presence of IApp interface,
        a subscription will be created that will be this function automatically.

        Args:
            dt: Time elapsed since previous call. If <0 application ignores passed value and measures elapsed time automatically
        """
    @property
    def ui_scale_multiplier(self) -> float:
        """
                         Get the UI scale multiplier that is applied on top of the OS DPI scale.

                         Return:
                             The UI scale multiplier that is applied on top of the OS DPI scale.
                     

        :type: float
        """
    @ui_scale_multiplier.setter
    def ui_scale_multiplier(self, arg1: float) -> None:
        """
        Get the UI scale multiplier that is applied on top of the OS DPI scale.

        Return:
            The UI scale multiplier that is applied on top of the OS DPI scale.
        """
    pass
class IAppWindowFactory():
    """
    Application window creation factory
    """
    def create_window_by_type(self, window_type: WindowType) -> IAppWindow: 
        """
        Create application window according to the input window type.

        Args:
            window_type: Type of the window: virtual or OS.

        Return:
            Application window carb object pointer.
        """
    def create_window_from_settings(self) -> IAppWindow: 
        """
        Create application window.

        Return:
            The application window carb object pointer.
        """
    def create_window_ptr_by_type(self, window_type: WindowType) -> IAppWindow: 
        """
        Create application window from the input settings.

        Args:
            window_type: Type of the window: virtual or OS.

        Return:
            Application window pointer.
        """
    def create_window_ptr_from_settings(self) -> IAppWindow: 
        """
        Create application window from the input settings.

        Return:
            Application window pointer.
        """
    def destroy_window_ptr(self, app_window: IAppWindow) -> None: 
        """
        Destroy the input application window.

        Args:
            app_window: The application window pointer.
        """
    def get_app_window(self) -> IAppWindow: 
        """
        Get default application window.

        Return:
            The application window pointer.
        """
    def get_default_window(self) -> IAppWindow: 
        """
        Get default application window.

        Return:
            The application window pointer.
        """
    def get_window_at(self, index: int) -> IAppWindow: 
        """
             Get application window by the input index.

        Args:
             index: window index

             Return:
                 The application window pointer.
         
        """
    def get_window_count(self) -> int: 
        """
        Get the number of application windows.

        Return:
            The number of application windows.
        """
    def get_windows(self) -> tuple: 
        """
        Get a tuple of all the application windows.

        Return:
            A tuple of all the application windows.
        """
    def set_default_window(self, Arg0: IAppWindow) -> None: 
        """
        Set default application window.

        Args:
           Arg0: The input application window pointer.
        """
    pass
class WindowType():
    """
    Window type

    Members:

      OS : OS window, for application with graphical user interface

      VIRTUAL : Virtual window, for headless application
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
    OS: omni.appwindow._appwindow.WindowType # value = <WindowType.OS: 1>
    VIRTUAL: omni.appwindow._appwindow.WindowType # value = <WindowType.VIRTUAL: 0>
    __members__: dict # value = {'OS': <WindowType.OS: 1>, 'VIRTUAL': <WindowType.VIRTUAL: 0>}
    pass
def acquire_app_window_factory_interface(*args, **kwargs) -> typing.Any:
    """
    Gets application window factory interface from either plugin name or library path, default to library path if that is defined.

    Args:
        plugin_name: The plugin name for binding.
        library_path: The library path for binding.
    Return:
        The application window factory interface from either plugin name or library path.
    """
def get_default_app_window(*args, **kwargs) -> typing.Any:
    """
    Gets default application window

        Returns:
            Application window pointer.
        
    """
POSITION_CENTERED = 18446744073709551615
POSITION_UNSET = 18446744073709551614
