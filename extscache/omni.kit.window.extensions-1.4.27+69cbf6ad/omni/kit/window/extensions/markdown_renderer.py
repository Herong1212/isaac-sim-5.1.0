# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides the MarkdownText class to render markdown-formatted text within a UI context using omni.ui."""

__all__ = ["MarkdownText"]

import asyncio
import contextlib
import os
import os.path
import re

import carb
import omni.ui as ui

from .common import build_doc_urls, get_icons_path
from .styles import get_style
from .utils import open_url

CODEBLOCK_ID = "$$_C_O_D_E_$$"  # noqa: N806
STAR_ID = "$$_S_T_A_R_$$"  # noqa: N806


class MarkdownText:
    """A class for rendering markdown text within a UI context.

    This class takes a markdown-formatted string and displays it using
    the appropriate styles for headings and regular text lines.

    Args:
        content (str): Markdown-formatted string to be rendered."""

    def __init__(self, content, ext_info, ext_item):
        """Initializes a new instance of the MarkdownText class, which parses markdown content and creates a styled UI representation."""
        self._local_path = ext_info.get("path", None) if ext_info else None
        self._display_edited = False
        self._ansi_escape_remove = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        self._table_data = None
        self._table_length = 0
        self._codeblock_data = None
        self._codeblock_type = ""

        with ui.VStack(height=0, style=get_style(self)):
            self._build_info_text()

            code_block = False
            for line in content.splitlines():
                heading, line = self._consume_heading(line, code_block, ext_item)
                style_name = "text"

                if line == CODEBLOCK_ID:
                    code_block = not code_block
                    if code_block:
                        self._codeblock_type = heading
                    elif self._codeblock_data:
                        self._build_codeblock(style_name, self._codeblock_type)
                    continue

                if heading > 0:
                    style_name = f"H{heading}"

                if code_block:
                    self._add_codeblock_data(line)
                else:
                    lsline = line.lstrip()
                    if lsline.startswith("\033[0;3"):
                        lsline = lsline[7:].lstrip()

                    if self._table_data and not (lsline.startswith("|") and lsline.endswith("|")):
                        self._build_table(style_name)

                    if lsline.startswith("|") and lsline.endswith("|"):
                        self._add_table_data(lsline)
                    elif lsline.lstrip().startswith("![") and "](" in lsline:
                        self._build_imagelink(style_name, lsline)
                    elif lsline.lstrip().startswith("[") and "](" in lsline:
                        self._build_hyperlink(style_name, lsline)
                    elif lsline.lstrip().startswith("> "):
                        self._build_blockquote(style_name, lsline)
                    else:
                        is_bullet, indent, code, updated_str = self._is_bullet(line)
                        if is_bullet:
                            self._build_bullet(style_name, indent, code, updated_str)
                        elif line.find("](") > 0:
                            lsline = self._ansi_escape_remove.sub("", lsline)
                            with ui.HStack(width=0):
                                while lsline.find("](") > 0:
                                    index1 = lsline.find("[")
                                    index2 = lsline[index1:].find(")") if index1 > 0 else 0
                                    if index1 > 0 and index2 > 0:
                                        self._build_label(style_name, lsline[: index1 - 1])
                                        self._build_hyperlink(style_name, lsline[index1 : index1 + index2 + 1])
                                        lsline = lsline[index1 + index2 + 1 :]

                                self._build_label(style_name, lsline)
                        else:
                            self._build_label(style_name, line)

            ui.Spacer(height=20)

        self._show_info_text(ext_item)

    def _consume_heading(self, line, code_block, ext_item):
        fixed_header = "**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`"
        if line == fixed_header and ext_item:
            line = line.replace("{{ extension_version }},", f"{ext_item.id} \0")

        heading = 0
        mds = line.replace("~~~", "```")
        # remove unsupported codes
        if mds.startswith("* "):
            mds = f"- {mds[2:]}"
        elif mds.startswith(" * "):
            mds = f"- {mds[3:]}"
        mds = mds.replace("*_", "")
        mds = mds.replace("_*", "")
        mds = mds.replace("\\*", STAR_ID)
        mds = mds.replace("*", "")
        mds = mds.replace(STAR_ID, "*")
        if mds != line:
            self._display_edited = True

        if mds.startswith("```"):
            return mds[3:], CODEBLOCK_ID
        if not code_block:
            while mds.startswith("#"):
                if mds.startswith("#"):
                    mds = mds[1:]
                    heading += 1

        if "`" in mds:
            parts = mds.split("`")
            mds = []
            style = False
            for part in parts:
                mds.append(f"\033[0;32m{part}" if style else f"\033[0;37m{part}"),  # noqa: PLW0106
                style = not style
            mds = "".join(mds)

        return heading, mds.rstrip()

    def _is_bullet(self, line):
        # remove ansi codes
        if line.startswith("\033[0;3"):
            line = line[7:]

        # calculate indent
        indent = 0
        while line.startswith(" "):
            line = line[1:]
            indent += 1
        if indent > 2:
            indent = int((indent - 2) / 2)
        else:
            indent = 0

        # find bullet points
        if line.startswith("- "):
            return True, indent, "- ", line[2:]

        if "." in line:
            index = line.find(". ")
            if index > 0 and index < 5 and line[:index].isnumeric():
                return True, indent, line[: index + 1], line[index + 1 :]

        return False, 0, "", ""

    def _build_label(self, style_name, line, width=None, height=None):
        # ansi codes not supported
        line = self._ansi_escape_remove.sub("", line)

        ui.Label(
            line.lstrip(),
            name=style_name,
            width=width if width is not None else ui.Fraction(1),
            height=height if height is not None else ui.Fraction(1),
            word_wrap=style_name == "text",
            elided_text=style_name != "text",
        )

    def _build_hyperlink(self, style_name, line):
        def set_if_valid(url, def_url):
            url = os.path.normpath(url.replace("\\", "/"))
            if os.path.exists(url):
                return url
            return def_url

        line = self._ansi_escape_remove.sub("", line)
        trailing_line = ""
        index = line.find(")")
        if index != -1:
            trailing_line = line[index + 1 :]
            line = line[:index]

        parts = line[1:].split("](")
        parts[1] = parts[1].split('"')[0].rstrip()
        file_url = parts[1]
        if self._local_path and not file_url.startswith("http"):
            file_url = set_if_valid(f"{self._local_path}/{parts[1]}", file_url)
            file_url = set_if_valid(f"{self._local_path}/{parts[1]}.md", file_url)
            file_url = set_if_valid(f"{self._local_path}/docs/{parts[1]}", file_url)
            file_url = set_if_valid(f"{self._local_path}/docs/{parts[1]}.md", file_url)

        button = None
        if trailing_line:
            with ui.HStack():
                button = ui.Button(
                    parts[0] if parts[0] else parts[1],
                    clicked_fn=lambda b=None, url=file_url: open_url(url),
                    width=0,
                    height=16,
                    name="InstallButton",
                )
                self._build_label(style_name, trailing_line)
        else:
            with ui.HStack():
                with ui.Placer(offset_x=0, offset_y=-4):
                    button = ui.Button(
                        parts[0] if parts[0] else parts[1],
                        clicked_fn=lambda b=None, url=file_url: open_url(url),
                        width=0,
                        height=16,
                        name="InstallButton",
                    )

        if button and not file_url.startswith("http") and not os.path.exists(file_url):
            carb.log_warn(f"Hyperlink error: {file_url} not found")
            button.enabled = False
            button.tooltip = f'Hyperlink path "{parts[1]}" not found'
            button.set_style({"background_color": 0xFF888888, "color": 0xFF111111})

    def _build_imagelink(self, style_name, line):
        # Checking if we have Pillow imported
        try:
            import PIL
        except ImportError:
            # Install Pillow if it's not installed
            import omni.kit.pipapi

            omni.kit.pipapi.install("Pillow", module="PIL")

        import PIL  # noqa: F401, F811

        if self._local_path:
            parts = line[2:].replace(")", "").split("](")
            parts[1] = parts[1].split('"')[0].rstrip()
            image_path = f"{self._local_path}/{parts[1]}".replace("\\", "/")
            if not os.path.isfile(image_path):
                image_path = f"{self._local_path}/docs/{parts[1]}".replace("\\", "/")

            if os.path.isfile(image_path):
                ui.Spacer(height=10)

                widget = ui.Image(
                    image_path,
                    alignment=ui.Alignment.CENTER,
                    fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                    width=0,
                    height=0,
                )
                ui.Spacer(height=10)

                async def get_image_size(widget, url):
                    import PIL  # noqa: F401, F811
                    from PIL import Image

                    with contextlib.suppress(PIL.UnidentifiedImageError):
                        with Image.open(url) as img:
                            widget.width = ui.Length(img.size[0])
                            widget.height = ui.Length(img.size[1])

                asyncio.ensure_future(get_image_size(widget, image_path))

    def _add_codeblock_data(self, line):
        if not self._codeblock_data:
            self._codeblock_data = []
        self._codeblock_data.append(self._ansi_escape_remove.sub("", line))

    def _build_codeblock(self, style_name, block_type):
        try:
            import omni.kit.widget.text_editor as te
        except ImportError:
            te = None

        if block_type == "{csv-table}":
            te = None

        style = get_style(self)["Label::codeblock"]
        lines = "\n".join(self._codeblock_data)

        while lines[0] == "\n":
            lines = lines[1:]

        with ui.ZStack():
            with ui.HStack():
                ui.Rectangle(style={"background_color": 0xFF101010})
                ui.Spacer(width=8)

            if te:
                syntax = te.TextEditor.Syntax.NONE
                match block_type:
                    case "text":
                        syntax = te.TextEditor.Syntax.NONE
                    case "python":
                        syntax = te.TextEditor.Syntax.PYTHON
                    case "c":
                        syntax = te.TextEditor.Syntax.C
                    case "cpp":
                        syntax = te.TextEditor.Syntax.CPLUSPLUS
                    case "sql":
                        syntax = te.TextEditor.Syntax.SQL
                    case "glsl":
                        syntax = te.TextEditor.Syntax.GLSL
                    case "lua":
                        syntax = te.TextEditor.Syntax.LUA
                    case "hlsl":
                        syntax = te.TextEditor.Syntax.HLSL
                    case "angelscript":
                        syntax = te.TextEditor.Syntax.ANGELSCRIPT
                    case _:
                        # print(f">> unsupported block_type {block_type}")
                        pass

                with ui.VStack():
                    with ui.ZStack(height=0):
                        label = ui.Label(lines, name="codeblock", word_wrap=True)
                        label.text = "\n" * (label.text.count("\n") + 2)
                        te.TextEditor(
                            text=lines,
                            read_only=True,
                            style=style,
                            alignment=ui.Alignment.LEFT_TOP,
                            syntax=syntax,
                        )
            else:
                with ui.VStack():
                    ui.Spacer(height=4)
                    with ui.HStack():
                        ui.Spacer(width=4)
                        ui.Label(lines, name="codeblock", word_wrap=True)
                    ui.Spacer(height=6)

        self._codeblock_data = None

    def _build_blockquote(self, style_name, line):
        with ui.ZStack():
            with ui.HStack():
                ui.Rectangle(style={"background_color": 0xFF333333})
                ui.Spacer(width=8)

            with ui.VStack():
                ui.Spacer(height=4)
                with ui.HStack():
                    ui.Spacer(width=4)
                    ui.Label(line[2:], name="text", word_wrap=True)
                ui.Spacer(height=6)

    def _build_bullet(self, style_name, indent, code, line):
        with ui.HStack():
            for _ in range(indent):
                ui.Spacer(width=16, height=16)

            if code == "- ":
                ui.Image(
                    width=16,
                    height=16,
                    style={
                        "Image": {
                            "image_url": f"{get_icons_path()}/data/bullet.png",
                            "border_width": 8,
                            "border_color": 0xFF23211F,
                            "border_radius": 15,
                        }
                    },
                )
                ui.Spacer(width=4)
            else:
                self._build_label(style_name, code, width=22, height=0)

            if line.lstrip().startswith("[") and "](" in line:
                self._build_hyperlink(style_name, line)
            else:
                self._build_label(style_name, line)

    def _build_table(self, style_name):
        with ui.Frame():
            with ui.VStack():
                ui.Spacer(height=8)
                for row, parts in enumerate(self._table_data):
                    with ui.VStack():
                        with ui.HStack():
                            for column, part in enumerate(parts):
                                if row == 1:
                                    ui.Line(style={"color": 0xFFFFFFFF}, height=16)
                                else:
                                    # is there a better way to have fixed width on 1st column?
                                    if column == 0:
                                        ui.Label(
                                            part, name="text", width=self._table_length * 8, height=0, word_wrap=True
                                        )
                                    else:
                                        ui.Label(part, name="text", height=0, word_wrap=True)
                            ui.Spacer(width=8)

                        if row > 1:
                            with ui.HStack():
                                ui.Line(style={"color": 0xFF444444}, height=16)
                                ui.Spacer(width=8)
                ui.Spacer(height=8)

        self._table_data = []

    def _add_table_data(self, line):
        if not self._table_data:
            self._table_data = []
            self._table_length = 0

        line = self._ansi_escape_remove.sub("", line)
        parts = line[1:-1].split("|")
        data = []
        for index, part in enumerate(parts):
            # remove HTML tags as we can't handle those
            part = re.sub("<[^<]+?>", "", part.strip())
            data.append(part)
            if index == 0 and len(part) > self._table_length:
                self._table_length = len(part)
        self._table_data.append(data)

    def _build_info_text(self):
        self._info_text = ui.Label(
            "TBA", name="H3", height=0, word_wrap=True, style={"color": 0xFF0076B9}, visible=False
        )

    def _show_info_text(self, ext_item):
        # Async check for URLs and if valid show the button
        async def check_urls(doc_urls, set_visible_fn):
            def check_url_sync(url):
                import urllib

                try:
                    return urllib.request.urlopen(url).getcode() == 200
                except urllib.error.HTTPError:
                    return False

            for doc_url in doc_urls:
                # run sync code on other thread not to block
                if await asyncio.get_event_loop().run_in_executor(None, check_url_sync, doc_url):
                    set_visible_fn(True)
                    break

        if ext_item:
            doc_urls = build_doc_urls(ext_item)
            if doc_urls and self._display_edited:

                def set_visible(state: bool):
                    if state:
                        self._info_text.text = 'This is only a approximation of the document and maybe incomplete. Click on "?" icon above to see full document\n\n'
                    else:
                        self._info_text.text = "This is only a approximation of the document and maybe incomplete.\n\n"
                    self._info_text.visible = True

                asyncio.ensure_future(check_urls(doc_urls, set_visible))
