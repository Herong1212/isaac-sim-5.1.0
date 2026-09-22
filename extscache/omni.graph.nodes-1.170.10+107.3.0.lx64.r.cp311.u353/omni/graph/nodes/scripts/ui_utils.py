# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import string
from pathlib import Path
from typing import Callable

import omni.graph.core as og
import omni.ui as ui
from omni.kit.window.property.templates import HORIZONTAL_SPACING

__string_cache = []


def _get_attribute_ui_name(name: str) -> str:
    """
    Takes a raw name and formats it for use as the corresponding nice name in the UI.

    o  (For attribute names) Standard namespaces ('inputs', 'outputs', 'state') are stripped off the front.
    o  (For attribute names) Any remaining namespaces are converted to words within the name.
    o  Underscores are converted to spaces.
    o  Mixed-case words are broken into separate words (e.g. 'primaryRGBColor' -> 'primary RGB Color').
    o  Words which are all lower-case are capitalized (e.g. 'primary' -> 'Primary').
    """
    # Replace '_' with ':' so they will be split
    name.replace("_", ":")
    # Split out namespaces
    words = name.split(":")
    # If the first namespace is one of our standard ones, get rid of it.
    if len(words) > 1 and words[0] in ("inputs", "outputs", "state"):
        words.pop(0)
    words_out = []
    for word in words:
        # if word is all lower or all upper append it
        if word.islower() or word.isupper():
            words_out.append(word)
            continue
        # Mixed case.
        # Lower-case followed by upper-case breaks between them. E.g. 'usdPrim' -> 'usd Prim'
        # Upper-case followed by lower-case breaks before them. E.g: 'USDPrim' -> 'USD Prim'
        # Combined example: abcDEFgHi -> abc DE Fg Hi
        sub_word = ""
        uppers = ""
        for c in word:
            if c.isupper():
                if not uppers and sub_word:
                    words_out.append(sub_word)
                    sub_word = ""
                uppers += c
            else:
                if len(uppers) > 1:
                    words_out.append(uppers[:-1])
                sub_word += uppers[-1:] + c
                uppers = ""

        if sub_word:
            words_out.append(sub_word)
        elif uppers:
            words_out.append(uppers)

    # Title-case any words which are all lower case.
    return " ".join([word.title() if word.islower() else word for word in words_out])


def _get_string_permutation(n: int) -> str:
    """
    Gets the name of the attribute at the given index,
    assuming the name is n-th permutation of the letters of the alphabet,
    starting from single characters.

    Args:
        n: the index of the permutation
    Return:
        str: the n-th string in lexicographical order.
    """
    max_index = len(__string_cache)
    if max_index <= n:
        for i in range(max_index, n + 1):
            __string_cache.append(_convert_index_to_string_permutation(i + 1))

    return __string_cache[n]


def _convert_index_to_string_permutation(index: int) -> str:
    """Converts a 1-based index to an alphabetical string which is a permutation of the letters of the alphabet.

    For example:
    1 = a
    2 = b
    ...
    26 = z
    27 = aa
    28 = ab
    ...

    Args:
        index: The number to convert to a string. Represents the index in the lexicographical sequence of generated strings.
    Returns:
        str: index'th string in lexicographic order.
    """
    if index <= 0:
        return ""

    alphabet = list(string.ascii_lowercase)
    size = len(alphabet)

    result = ""
    while index > 0:
        r = index % size  # noqa: S001
        if r == 0:
            r = size
        index = (int)((index - r) / size)
        result += alphabet[r - 1]

    return result[::-1]


def _retrieve_existing_numeric_dynamic_inputs(node: og.Node) -> tuple[list[og.Attribute], int]:
    """
    Retrieves the node inputs which follow the 'inputs:input{num}' naming convention.

    Args:
        node: the node reflected in the property panel
    Return:
        ([og.Attribute], int): Tuple with the list of input attributes and the largest input index.
    """

    # Retrieve all existing attributes of the form "inputs:input{num}"
    # Also find the largest suffix among all such attributes
    # Returned largest suffix = -1 if there are no such attributes
    input_attribs = [attrib for attrib in node.get_attributes() if attrib.get_name()[:12] == "inputs:input"]
    largest_suffix = -1
    if not input_attribs:
        return ([], largest_suffix)

    for attrib in input_attribs:
        largest_suffix = max(largest_suffix, int(attrib.get_name()[12:]))
    return (input_attribs, largest_suffix)


def _retrieve_existing_alphabetic_dynamic_inputs(node: og.Node) -> tuple[list[og.Attribute], int]:
    """
    Retrieves the node inputs which follow the 'inputs:abc' naming convention.
    The sequence "abc" is a permutation of the letters of the alphabet,
    generated sequentially starting with single characters.

    Args:
        node: the node reflected in the property panel
    Return:
        ([og.Attribute], int): Tuple with the list of input attributes and the largest input index.
    """
    # Retrieve all existing attributes of the form "inputs:abc
    # The sequence "abc" represents the n-th permutation of the letters of the alphabet,
    # starting from single characters

    input_attribs = [attrib for attrib in node.get_attributes() if attrib.get_name()[:7] == "inputs:"]
    if not input_attribs:
        return ([], -1)

    largest_index = len(input_attribs) - 1
    return (input_attribs, largest_index)


def _retrieve_existing_alphabetic_dynamic_outputs(node: og.Node) -> tuple[list[og.Attribute], int]:
    """
    Retrieves the node outputs which follow the 'outputs:abc' naming convention.
    The sequence "abc" is a permutation of the letters of the alphabet,
    generated sequentially starting with single characters.

    Args:
        node: the node reflected in the property panel
    Return:
        ([og.Attribute], int): Tuple with the list of outputs attributes and the largest output index.
    """
    # Retrieve all existing attributes of the form "outputs:abc
    # The sequence "abc" represents the n-th permutation of the letters of the alphabet,
    # starting from single characters

    output_attribs = [attrib for attrib in node.get_attributes() if attrib.get_name()[:8] == "outputs:"]
    if not output_attribs:
        return ([], -1)

    largest_index = len(output_attribs) - 1
    return (output_attribs, largest_index)


def _build_add_remove_buttons(
    layout, on_add_fn: Callable, on_remove_fn: Callable, on_remove_enabled_fn: Callable[[], bool]
):
    """
    Creates the add (+) / remove (-) buttons for the property panel list control.

    Args:
        layout: the property panel layout instance
        on_add_fn: callback invoked when the add button is pushed
        on_remove_fn: callback invoked when the remove button is pushed
        on_remove_enabled_fn: callback invoked when creating the remove button to check if the button is enabled or not
    """
    icons_path = Path(__file__).absolute().parent.parent.parent.parent.parent.joinpath("icons")

    with ui.HStack(height=0, spacing=HORIZONTAL_SPACING):
        ui.Spacer()
        layout.add_button = ui.Button(
            image_url=f"{icons_path.joinpath('add.svg')}",
            width=22,
            height=22,
            style={"Button": {"background_color": 0x1F2124}},
            clicked_fn=on_add_fn,
            tooltip_fn=lambda: ui.Label("Add New Input"),
        )
        layout.remove_button = ui.Button(
            image_url=f"{icons_path.joinpath('remove.svg')}",
            width=22,
            height=22,
            style={"Button": {"background_color": 0x1F2124}},
            enabled=on_remove_enabled_fn(),
            clicked_fn=on_remove_fn,
            tooltip_fn=lambda: ui.Label("Remove Input"),
        )
