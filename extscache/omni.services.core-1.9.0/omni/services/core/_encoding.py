# Copyright (c) 2020-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import typing

import carb


_encoders = {}


def register_encoder(name: str, encoder: typing.Any):
    """ Register a data encoder.

        The encoder is expected to have a `compress` and `decompress` function
    """
    if not hasattr(encoder, "compress") or not hasattr(encoder, "decompress"):
        raise AttributeError(f"{name} is missing the 'compress' or 'decompress' (or both) function. Cannot register encoder.")
    _encoders[name] = encoder


def get_encoder(name: str):
    """ Returns the encoder for the given name.

        Raises:
         - KeyError: Raised when given encoder is not found.
    """
    return _encoders[name]


try:
    import gzip
    register_encoder("gzip", gzip)
except Exception as exc:
    carb.log_error(f"Failed to register gzip as a decoder: {exc}")


try:
    import zlib
    register_encoder("deflate", zlib)
except Exception as exc:
    carb.log_error(f"Failed to register deflate as a decoder: {exc}")
