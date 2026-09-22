from typing import Callable, List

import carb
import carb.input
import omni
import uuid


class PromptButtonInfo:
    """ Prompt button's information"""
    def __init__(self, name: str, on_button_clicked_fn: Callable[[], None] = None):
        """
        Construtor.

        Args:
            name (str): The button's name.
            on_button_clicked_fn (Callable[[], None], optional): Function executed when this button clicked. The function signature is:
                void on_button_clicked_fn(). Defaults to None.
        """
        self._name = name
        self._on_button_clicked_fn = on_button_clicked_fn

    @property
    def name(self) -> str:
        """
        Get the button's name.

        Returns:
            str: Name of the button.
        """
        return self._name

    @property
    def on_button_clicked_fn(self) -> Callable[[], None]:
        """
        Get the button clicked function.

        Returns:
            Callable[[], None]: Function executed when this button clicked. The function signature is:
                void on_button_clicked_fn()
        """
        return self._on_button_clicked_fn


class PromptManager:
    """ Prompt Manager """
    
    _prompts = set([])

    @staticmethod
    def on_startup():
        pass

    @staticmethod
    def on_shutdown():
        """Remove all the prompts when shut down"""
        all_prompts = PromptManager._prompts
        PromptManager._prompts = set([])
        for prompt in all_prompts:
            prompt.destroy()

    @staticmethod
    def query_prompt_by_title(title: str):
        """
        Query the prompt by tiyle.

        Args:
            title (str): Prompt to query.
        
        Returns:
            prompt (:obj:'Prompt'): Prompt with the title in manager.
        """
        for prompt in PromptManager._prompts:
            if prompt._title == title:
                return prompt

        return None

    @staticmethod
    def add_prompt(prompt: 'Prompt'):
        """
        Add the prompt to mananger.

        Args:
            prompt (:obj:'Prompt'): Prompt to add.
        """
        if prompt not in PromptManager._prompts:
            PromptManager._prompts.add(prompt)

    @staticmethod
    def remove_prompt(prompt: 'Prompt'):
        """
        Remove the prompt from mananger.

        Args:
            prompt (:obj:'Prompt'): Prompt to be remove.
        """
        if prompt in PromptManager._prompts:
            PromptManager._prompts.remove(prompt)

    @staticmethod
    def post_simple_prompt(
        title: str, message: str,
        ok_button_info: PromptButtonInfo = PromptButtonInfo("OK", None),
        cancel_button_info: PromptButtonInfo = None,
        middle_button_info: PromptButtonInfo = None,
        middle_2_button_info: PromptButtonInfo = None,
        on_window_closed_fn: Callable[[], None] = None,
        modal=True,
        shortcut_keys=True,
        standalone=True,
        no_title_bar=False,
        width=None,
        height=None,
        callback_addons: List = [],
    ):
        """
        Post a simple prompt with given param. 
        Note: When standalone is true, it will hide all other managed prompts in this manager.

        Args:
            title (str): Text appearing in the titlebar of the window.
            message (str): Message being posed to the user.
            ok_button_info (:obj:'PromptButtonInfo'): Information for the ok button.
            cancel_button_info (:obj:'PromptButtonInfo'): Information for the last button.
            middle_button_info (:obj:'PromptButtonInfo'): Information for the middle button.
            middle_2_button_info (:obj:'PromptButtonInfo'): Information for the second middle button.
            on_window_closed_fn (Callable[[], None]): Function executed when the window is closed.The function signature is:
                void on_button_clicked_fn(). Defaults to None.
            modal (bool): True if the window is modal, shutting down other UI until an answer is received
            shortcut_keys (bool): If it can be confirmed or hidden with shortcut keys like Enter or ESC. Defaults to True.
            no_title_bar (bool): If it needs to show title bar. Defaults to True.
            width (int): The specified width. By default, it will use the computed width.
            height (int): The specified height. By default, it will use the computed height.
            callback_addons (List): Addon widgets which is appended in the prompt window. By default, it is empty.
        """

        def unwrap_button_info(button_info: PromptButtonInfo):
            if button_info:
                return button_info.name, button_info.on_button_clicked_fn
            else:
                return None, None

        ok_button_text, ok_button_fn = unwrap_button_info(ok_button_info)
        cancel_button_text, cancel_button_fn = unwrap_button_info(cancel_button_info)
        middle_button_text, middle_button_fn = unwrap_button_info(middle_button_info)
        middle_2_button_text, middle_2_button_fn = unwrap_button_info(middle_2_button_info)

        if standalone:
            prompts = PromptManager._prompts
            PromptManager._prompts = set([])
            for prompt in prompts:
                prompt.destroy()

        prompt = Prompt(
            title, message, ok_button_text=ok_button_text,
            cancel_button_text=cancel_button_text, middle_button_text=middle_button_text,
            middle_2_button_text=middle_2_button_text, ok_button_fn=ok_button_fn,
            cancel_button_fn=cancel_button_fn, middle_button_fn=middle_button_fn,
            middle_2_button_fn=middle_2_button_fn, modal=modal,
            on_closed_fn=on_window_closed_fn, shortcut_keys=shortcut_keys,
            no_title_bar=no_title_bar, width=width, height=height, callback_addons=callback_addons
        )
        prompt.show()

        return prompt


class Prompt:
    """Pop up a prompt window that asks the user a simple question with up to four buttons for answers.

    Callbacks are executed for each button press, as well as when the window is closed manually.
    """
    def __init__(
        self,
        title,
        text,
        ok_button_text="OK",
        cancel_button_text=None,
        middle_button_text=None,
        middle_2_button_text=None,
        ok_button_fn=None,
        cancel_button_fn=None,
        middle_button_fn=None,
        middle_2_button_fn=None,
        modal=False,
        on_closed_fn=None,
        shortcut_keys=True,
        no_title_bar=False,
        width=None,
        height=None,
        callback_addons: List = []
    ):
        """Initialize the callbacks and window information

        Args:
            title (str): Text appearing in the titlebar of the window.
            text (str): Text of the question being posed to the user.
            ok_button_text (str): Text for the first button.
            cancel_button_text (str): Text for the last button.
            middle_button_text (str): Text for the middle button.
            middle_button_2_text (str): Text for the second middle button.
            ok_button_fn (Callable[[], None]): Function executed when the first button is pressed.The function signature is:
                void on_button_clicked_fn(). Defaults to None.
            cancel_button_fn (Callable[[], None]):: Function executed when the last button is pressed.The function signature is:
                void on_button_clicked_fn(). Defaults to None.
            middle_button_fn (Callable[[], None]):: Function executed when the middle button is pressed.The function signature is:
                void on_button_clicked_fn(). Defaults to None.
            middle_2_button_fn (Callable[[], None]):: Function executed when the second middle button is pressed.The function signature is:
                void on_button_clicked_fn(). Defaults to None.
            modal (bool): True if the window is modal, shutting down other UI until an answer is received
            on_closed_fn (Callable[[], None]):: Function executed when the window is closed without hitting a button.The function signature is:
                void on_button_clicked_fn(). Defaults to None.
            shortcut_keys (bool): If it can be confirmed or hidden with shortcut keys like Enter or ESC. Defaults to True.
            no_title_bar (bool): If it needs to show title bar. Defaults to True.
            width (int): The specified width. By default, it will use the computed width.
            height (int): The specified height. By default, it will use the computed height.
            callback_addons (List): Addon widgets which is appended in the prompt window. By default, it is empty.
        """
        self._title = title
        self._text = text
        self._cancel_button_text = cancel_button_text
        self._cancel_button_fn = cancel_button_fn
        self._ok_button_fn = ok_button_fn
        self._ok_button_text = ok_button_text
        self._middle_button_text = middle_button_text
        self._middle_button_fn = middle_button_fn
        self._middle_2_button_text = middle_2_button_text
        self._middle_2_button_fn = middle_2_button_fn
        self._modal = modal
        self._on_closed_fn = on_closed_fn
        self._button_clicked = False
        self._shortcut_keys = shortcut_keys
        self._no_title_bar = no_title_bar
        self._width = width
        self._height = height
        self._callback_addons = callback_addons

        self._key_functions = {
            int(carb.input.KeyboardInput.ENTER): self._on_ok_button_fn,
            int(carb.input.KeyboardInput.ESCAPE): self._on_cancel_button_fn
        }

        self._buttons = []
        self._build_ui()

    def __del__(self):
        self.destroy()

    def destroy(self):
        """ Destructor. """
        for button in self._buttons:
            button.set_clicked_fn(None)
        self._buttons.clear()
        self.hide()
        if self._window:
            self._window.set_visibility_changed_fn(None)
            self._window = None

    def __enter__(self):
        """Called on entering a 'with' loop"""
        self.show()
        return self

    def __exit__(self, type, value, trace):
        """Called on exiting a 'with' loop"""
        self.hide()

    @property
    def visible(self):
        """
        Get the prompt's visible stat.

        Returns:
            bool: True is prompt is visible else False.
        """
        return self.is_visible()

    @visible.setter
    def visible(self, value: bool):
        """
        Get the prompt's visible stat.

        Args:
            value (bool): True to show prompt, False to hide.
        """
        if value:
            self.show()
        else:
            self.hide()

    def show(self):
        """Make the prompt window visible"""
        if not self._window:
            self._build_ui()
        self._window.visible = True
        self._button_clicked = False
        PromptManager.add_prompt(self)

    def hide(self):
        """Make the prompt window invisible"""
        if self._window:
            self._window.visible = False
        PromptManager.remove_prompt(self)

    def is_visible(self) -> bool:
        """
        Returns True if the prompt is currently visible.
        
        Returns:
            bool
        """
        return self._window and self._window.visible

    def set_text(self, text):
        """Set a new question label"""
        self._text_label.text = text

    def set_confirm_fn(self, on_ok_button_clicked):
        """Define a new callback for when the first (okay) button is clicked"""
        self._ok_button_fn = on_ok_button_clicked

    def set_cancel_fn(self, on_cancel_button_clicked):
        """Define a new callback for when the third (cancel) button is clicked"""
        self._cancel_button_fn = on_cancel_button_clicked

    def set_middle_button_fn(self, on_middle_button_clicked):
        """Define a new callback for when the second (middle) button is clicked"""
        self._middle_button_fn = on_middle_button_clicked

    def set_middle_2_button_fn(self, on_middle_2_button_clicked):
        """Define a new callback for when the second (middle) button is clicked"""
        self._middle_2_button_fn = on_middle_2_button_clicked

    def set_on_closed_fn(self, on_on_closed):
        """Define a new callback for when the window is closed without pressing a button"""
        self._on_closed_fn = on_on_closed

    def _on_visibility_changed(self, new_visibility: bool):
        """Callback executed when visibility of the window closes"""
        if not new_visibility:
            if not self._button_clicked and self._on_closed_fn is not None:
                self._on_closed_fn()

            self.hide()

    def _on_ok_button_fn(self):
        """Callback executed when the first (okay) button is pressed"""
        self._button_clicked = True
        self.hide()
        if self._ok_button_fn:
            self._ok_button_fn()

    def _on_cancel_button_fn(self):
        """Callback executed when the third (cancel) button is pressed"""
        self._button_clicked = True
        self.hide()
        if self._cancel_button_fn:
            self._cancel_button_fn()

    def _on_middle_button_fn(self):
        """Callback executed when the second (middle) button is pressed"""
        self._button_clicked = True
        self.hide()
        if self._middle_button_fn:
            self._middle_button_fn()

    def _on_closed_fn(self):
        """Callback executed when the window is closed without pressing a button"""
        self._button_clicked = True
        self.hide()
        if self._on_closed_fn:
            self._on_closed_fn()

    def _on_middle_2_button_fn(self):
        self._button_clicked = True
        self.hide()
        if self._middle_2_button_fn:
            self._middle_2_button_fn()

    def _on_key_pressed_fn(self, key, mod, pressed):
        if not pressed or not self._shortcut_keys:
            return

        func = self._key_functions.get(key)
        if func:
            func()

    def _build_ui(self):
        """Construct the window based on the current parameters"""
        num_buttons = 0
        if self._ok_button_text:
            num_buttons += 1

        if self._cancel_button_text:
            num_buttons += 1

        if self._middle_button_text:
            num_buttons += 1

        if self._middle_2_button_text:
            num_buttons += 1

        button_width = 120
        spacer_width = 60
        if self._width:
            window_width = self._width
        else:
            window_width = button_width * num_buttons + spacer_width * 2
            if window_width < 400:
                window_width = 400

        if self._height:
            window_height = self._height
        else:
            window_height = 0

        if self._title:
            window_id = self._title
        else:
            # Generates unique id for this window to make sure all prompts are unique.
            window_id = f"##{str(uuid.uuid1())}"

        self._window = omni.ui.Window(
            window_id, visible=False, height=window_height, width=window_width,
            dockPreference=omni.ui.DockPreference.DISABLED,
            visibility_changed_fn=self._on_visibility_changed,
        )
        self._window.flags = (
            omni.ui.WINDOW_FLAGS_NO_COLLAPSE | omni.ui.WINDOW_FLAGS_NO_SCROLLBAR |
            omni.ui.WINDOW_FLAGS_NO_RESIZE | omni.ui.WINDOW_FLAGS_NO_MOVE
        )
        self._window.set_key_pressed_fn(self._on_key_pressed_fn)

        if self._no_title_bar:
            self._window.flags = self._window.flags | omni.ui.WINDOW_FLAGS_NO_TITLE_BAR

        if self._modal:
            self._window.flags = self._window.flags | omni.ui.WINDOW_FLAGS_MODAL

        num_buttons = 0
        if self._ok_button_text:
            num_buttons += 1

        if self._cancel_button_text:
            num_buttons += 1

        if self._middle_button_text:
            num_buttons += 1

        if self._middle_2_button_text:
            num_buttons += 1

        button_width = 120

        with self._window.frame:
            with omni.ui.VStack(height=0):
                omni.ui.Spacer(width=0, height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Spacer(width=40)
                    self._text_label = omni.ui.Label(
                        self._text, word_wrap=True, width=self._window.width - 80, height=0, name="prompt_text"
                    )
                    omni.ui.Spacer(width=40)
                omni.ui.Spacer(width=0, height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Spacer(height=0)
                    if self._ok_button_text:
                        ok_button = omni.ui.Button(self._ok_button_text, name="confirm_button", width=button_width, height=0)
                        ok_button.set_clicked_fn(self._on_ok_button_fn)
                        self._buttons.append(ok_button)
                    if self._middle_button_text:
                        middle_button = omni.ui.Button(self._middle_button_text, name="middle_button", width=button_width, height=0)
                        middle_button.set_clicked_fn(self._on_middle_button_fn)
                        self._buttons.append(middle_button)
                    if self._middle_2_button_text:
                        middle_2_button = omni.ui.Button(self._middle_2_button_text, name="middle_2_button", width=button_width, height=0)
                        middle_2_button.set_clicked_fn(self._on_middle_2_button_fn)
                        self._buttons.append(middle_2_button)
                    if self._cancel_button_text:
                        cancel_button = omni.ui.Button(self._cancel_button_text, name="cancel_button", width=button_width, height=0)
                        cancel_button.set_clicked_fn(self._on_cancel_button_fn)
                        self._buttons.append(cancel_button)
                    omni.ui.Spacer(height=0)
                omni.ui.Spacer(width=0, height=10)
                for callback in self._callback_addons:
                    if callback and callable(callback):
                        callback()
