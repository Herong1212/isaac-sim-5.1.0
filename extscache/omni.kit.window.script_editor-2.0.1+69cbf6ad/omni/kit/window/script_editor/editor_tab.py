import re
from typing import List, Optional

import carb
import omni.client
import omni.ui as ui
from omni.kit.widget.text_editor import TextEditor


class TabHeader:
    def __init__(self, index: int, on_clicked_fn: callable, on_close_fn: callable, filename: Optional[str] = None):
        self.index = index
        self._name = None
        self._on_clicked_fn = on_clicked_fn
        self._on_close_fn = on_close_fn
        self._name_label: Optional[ui.Label] = None
        self.set_filename(filename)
        self._build_ui()

    @property
    def name(self) -> str:
        return self._name if self._name else f"Python {self.index}"

    def set_filename(self, filename: Optional[str]) -> None:
        self._name = omni.client.break_url(filename).path.split("/")[-1] if filename else None
        if self._name_label:
            self._name_label.text = self._name

    def set_dirty(self, dirty: bool) -> None:
        self._dirty_label.name = "" if dirty else "transparent"

    def refresh_ui(self) -> None:
        # Toggle circle visibility to refresh size when font size changed
        self._circle.visible = True
        self._circle.visible = False

    def _build_ui(self) -> None:
        self._container = ui.ZStack(
            width=0, height=0, mouse_hovered_fn=self._on_header_hovered, mouse_pressed_fn=self._on_header_clicked
        )
        with self._container:
            ui.Rectangle(style_type_name_override="Tab.Header.Background")
            with ui.HStack(width=0, height=0):
                ui.Spacer(width=5)
                self._name_label = ui.Label(self.name, width=0, style_type_name_override="Tab.Header.Label")
                self._dirty_label = ui.Label(
                    "*", width=0, name="transparent", style_type_name_override="Tab.Header.Label"
                )
                ui.Spacer(width=6)
                with ui.ZStack(
                    mouse_hovered_fn=self._on_close_hovered, mouse_pressed_fn=self._on_close_clicked
                ) as self._close_container:
                    self._circle = ui.Circle(visible=False, style_type_name_override="Tab.Header.Circle")
                    with ui.ZStack():
                        # Here need a label for placeholder to make close image show in correct size when font size changed
                        ui.Label(" X ", width=0, name="transparent", style_type_name_override="Tab.Header.Label")
                        self._close_image = ui.Image(
                            fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                            alignment=ui.Alignment.CENTER,
                            style_type_name_override="Tab.Header.Image",
                        )
                ui.Spacer(width=5)

    def _on_header_hovered(self, hovered: bool) -> None:
        self._close_image.name = "close" if hovered and self.selected else ""

    def _on_close_hovered(self, hovered: bool) -> None:
        self._circle.visible = hovered and self.selected

    def _on_header_clicked(self, x, y, btn: int, flag) -> None:
        if btn == 0:
            self._on_clicked_fn()

    def _on_close_clicked(self, x, y, btn: int, flag) -> None:
        if btn == 0:
            self._on_close_fn()

    @property
    def selected(self) -> bool:
        return self._container.selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._container.selected = value

    @property
    def visible(self) -> bool:
        return self._container.visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._container.visible = value


class Tab:
    def __init__(self, index: int, on_clicked_fn: callable, on_close_fn: callable, filename: Optional[str] = None):
        self.index = index
        self._filename: Optional[str] = filename
        self._on_clicked_fn = on_clicked_fn
        self._on_close_fn = on_close_fn
        self._header = None
        self._dirty = False

    def build_header(self) -> None:
        self._header = TabHeader(
            self.index,
            on_clicked_fn=self._on_header_clicked,
            on_close_fn=self._on_close_clicked,
            filename=self.filename,
        )

    def build_editor(self, palette: TextEditor.Palette = TextEditor.Palette.Dark) -> None:
        self._text_editor = TextEditor(
            text="", syntax=TextEditor.Syntax.PYTHON, identifier=f"script_editor_{self.index}"
        )
        self._text_editor.palette = palette
        self._text_editor.set_edited_fn(self._on_edited)

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value: str) -> None:
        self._filename = value
        self._header.set_filename(value)

    @property
    def text_editor(self) -> TextEditor:
        return self._text_editor

    @property
    def visible(self) -> bool:
        return self._text_editor.visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._text_editor.visible = value
        self._header.visible = value

    @property
    def text(self) -> str:
        return self._text_editor.text

    @text.setter
    def text(self, value: str) -> None:
        self._text_editor.text = value
        self._text_editor.set_error_markers({})

    @property
    def dirty(self) -> bool:
        if self.filename:
            return self._dirty
        else:
            return False

    @property
    def name(self) -> str:
        return self._header.name

    @property
    def file_changed(self) -> bool:
        if self.filename:
            return self._last_modified != self._get_last_modified()
        else:
            return False

    def set_active(self, active: bool) -> None:
        self._text_editor.visible = active
        self._header.selected = active

    def load_script(self, filename: str) -> bool:
        if filename and self.filename != filename:
            text = self._read_file(filename)
            if text is None:
                return False
            else:
                self.filename = filename
                self.text = text
                self._last_modified = self._get_last_modified()
                return True
        return False

    def save_script(self, filename: str) -> bool:
        def _encode_content(content):
            if type(content) == str:
                payload = bytes(content.encode("utf-8"))
            elif type(content) != type(None):
                payload = bytes(content)
            else:
                payload = bytes()

            return payload

        # Save to the file
        result = omni.client.write_file(filename, _encode_content(self.text))
        if result != omni.client.Result.OK:
            carb.log_error(f"[omni.kit.window.script_editor] Cannot write to {filename}, error code: {result}")
            return False
        carb.log_info(f"[omni.kit.window.script_editor] The scripts have saved to {filename}")
        if self.filename != filename:
            self.filename = filename
        self.text_editor.reset_edited()

    def reload_script(self) -> bool:
        text = self._read_file(self.filename)
        if text is None:
            return False
        else:
            self.text = text
            self._last_modified = self._get_last_modified()
            return True

    def reset_file_modified(self) -> None:
        self._last_modified = self._get_last_modified()

    def apply_error_message(self, error_message: str) -> None:
        markers = {}
        """Parse error like:
            NameError: name 's' is not defined
            At:
                c:/projects/kit/kit/_build/windows-x86_64/debug(2): <module>
        """
        # Look for first line number after 'At', e.g. (2)
        match = re.search("At\\:(.|\\n)*?\\((.*)\\)", error_message, flags=re.IGNORECASE)
        if match:
            line = int(match.group(2))
            markers[line] = error_message

        """Parse error like:
        //  IndentationError: ('expected an indented block', ('c:/projects/kit/kit/_build/windows-x86_64/debug', 8, 1,
        //  '1\n'))
        """
        # Look for line number, in this example: 8.
        match = re.search("\\(.*?\\(.*?,\\s*?(\\d*?),.*?,.*?\\)\\)", error_message, re.IGNORECASE)
        if match:
            line = int(match.group(1))
            markers[line] = error_message

        """Parse error like:
        //  IndentationError: unexpected indent (e:/temp/xjh4.1/script_1724306952.py, line 3)
        """
        # Look for line number, in this example: 3.
        match = re.search("IndentationError:.*?unexpected indent.*?\\(.*?, .*?(\\d*?)\\)", error_message, re.IGNORECASE)
        if match:
            line = int(match.group(1))
            markers[line] = error_message

        """Parse error like:
        //  SyntaxError: invalid syntax (e:/temp/x120c.0/script_1725517847.py, line 1)
        """
        # Look for line number, in this example: 3.
        match = re.search("SyntaxError:.*?invalid syntax.*?\\(.*?, .*?(\\d*?)\\)", error_message, re.IGNORECASE)
        if match:
            line = int(match.group(1))
            markers[line] = error_message

        # Fallback to putting error on first line if non was extracted:
        if not markers:
            carb.log_warn(f"Failed to parse error, please report a bug. Error:{error_message}")
            markers[0] = error_message

        self._text_editor.set_error_markers(markers)

    def clean_error_marks(self) -> None:
        self._text_editor.set_error_markers({})

    def refresh_ui(self) -> None:
        self._header.refresh_ui()

    def _read_file(self, filename) -> Optional[str]:
        result, _, content = omni.client.read_file(filename)
        if result != omni.client.Result.OK:
            carb.log_error(f"[omni.kit.window.script_editor] Can't read file {filename}, error code: {result}")
            return None

        data = memoryview(content).tobytes().decode("utf-8")
        return data

    def _get_last_modified(self) -> Optional[str]:
        result, entry = omni.client.stat(self.filename)
        return entry.modified_time if result == omni.client.Result.OK else None

    def _on_edited(self, edited: bool) -> None:
        self._dirty = edited
        self._header.set_dirty(self.dirty)

    def _on_header_clicked(self) -> None:
        self._on_clicked_fn(self)

    def _on_close_clicked(self) -> None:
        self._on_close_fn(self)
