# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


def docstring(app, what, name, obj, options, lines):
    """
    Convert the docstring of omni.ui to the format understandable by sphinx.
    We need it to use the same docstring in HTML documentation and in VSCode.

    Example:

        Input lines:

        ```
        Creates Dummy Object

        ## Arguments:
            `text : str`
                Nothing important

            `kwargs : dict`
                See Below

        ## Keyword Arguments:
            `total_width : float`
                Full width of this object

            `height_changed_fn : Callable[[], None]`
                Called when height is changed
        ```

        Output lines:

        ```
        Creates Dummy Object

        :type text: str
        :param text: Nothing important

        :type kwargs: dict
        :param kwargs: See Below

        :Keyword Arguments:
            * **total_width** (*float*) -- Full width of this object

            * **height_changed_fn** (*Callable[[], None]*) -- Called when height is changed
        ```

    """

    for exclude in app.config.vscode_to_sphinx_exclude:
        # Blacklist for docstring modules.
        if name.startswith(exclude):
            return

    # Buffer for processed lines
    converted_lines = []

    # False if we are in args section, True if we are in keword section
    keyword = None
    # The previous parameter and its type
    param = None
    param_type = None

    for line in lines:
        if line == "### Arguments:":
            # Args section
            keyword = False
            continue
        elif line == "### Keyword Arguments:":
            # Keyword section
            converted_lines.append(":Keyword Arguments:")
            keyword = True
            continue

        # Check if the line has the following format:
        # "            `text : str`"
        stripped = line.strip()
        if stripped and stripped[0] == "`" and stripped[-1] == "`" and stripped.count(":") == 1:
            # It's a param
            stripped = stripped[1:-1]
            # Name and type
            param, param_type = stripped.split(":")
            param = param.strip()
            param_type = param_type.strip()
            continue

        # Check if the previous line was the declaration of parameter
        if param or param_type:
            if not keyword:
                # We are in Args section
                if param_type:
                    converted_lines.append(f":type {param}: {param_type}")
                converted_lines.append(f":param {param}: {line}")
            else:
                # We are in Keyword section
                if param_type:
                    converted_lines.append(f"    * **{param}** (*{param_type}*) -- {line}")
                else:
                    converted_lines.append(f"    * **{param}** -- {line}")
            param = None
            param_type = None
            continue

        converted_lines.append(line)

    lines[:] = converted_lines


def setup(app):
    """Initialize Sphinx extension."""
    import sphinx

    app.connect("autodoc-process-docstring", docstring)

    # Blacklist for this extension. If you don't want the extension to process the module, add it to this config.
    app.add_config_value("vscode_to_sphinx_exclude", [], "html")
