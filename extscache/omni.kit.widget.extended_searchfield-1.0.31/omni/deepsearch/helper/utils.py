# Copyright (c) 2020-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# standard modules
import io
import base64

# third party modules
from PIL import Image


def image_to_base64(input: Image, format: str = "JPEG") -> str:
    """Covert image to base64 format

    Args:
        input: PIL image type

    Returns:
        str: base64 encoding of an image
    """
    with io.BytesIO() as output:
        input.convert("RGB").save(output, format=format)
        content = base64.b64encode(output.getvalue()).decode("ascii")
    return content


def image_from_base64(input: str) -> Image:
    """Convert base64 encoded image to PIL Image format.

    Args:
        input (str): input base64 encoded image

    Returns:
        Image: PIL image
    """
    msg = base64.b64decode(input.encode("ascii"))
    buf = io.BytesIO(msg)
    return Image.open(buf)
