"""Contains support code for AutoNode that will soon be deprecated"""

from __future__ import annotations

import enum
from collections import namedtuple

import carb
import numpy as np
from omni.graph.tools import deprecated_function

from .dtype import (
    Color3d,
    Color3f,
    Color3h,
    Color4d,
    Color4f,
    Color4h,
    Double,
    Double2,
    Double3,
    Double4,
    Float,
    Float2,
    Float3,
    Float4,
    Frame,
    Half,
    Half2,
    Half3,
    Half4,
    Int,
    Int2,
    Int3,
    Int4,
    Matrix2d,
    Matrix3d,
    Matrix4d,
    Normal3d,
    Normal3f,
    Normal3h,
    Point3d,
    Point3f,
    Point3h,
    Quatd,
    Quatf,
    Quath,
    TexCoord2d,
    TexCoord2f,
    TexCoord2h,
    TexCoord3d,
    TexCoord3f,
    TexCoord3h,
    Timecode,
    Token,
    UChar,
    UInt,
    Vector3d,
    Vector3f,
    Vector3h,
)


def int_to_int32(input: int) -> Int:
    return input & 0xFFFFFFFF


def int_to_uchar(input: int) -> UChar:
    return input & 0xFF


TypeDesc = namedtuple(
    "TypeDesc",
    [
        "type",
        "og_type",
        "type_to_og",
        "type_to_og_conversion_method",
        "og_to_type",
        "og_to_type_conversion_method",
        "default",
    ],
)


# ================================================================================
class TypeConversion:
    """Static class for storing conversion methods between python types and Omnigraph types"""

    class Method(enum.Enum):
        """Conversion method to go from source type to destination type"""

        ASSIGN = (0,)
        """Return the value to be assigned to the destination"""
        MODIFY = 1
        """Pass in the destination object to be modified in place"""

    # flake8: noqa: E241
    types = [
        TypeDesc(bool, "bool", bool, Method.ASSIGN, None, Method.ASSIGN, False),
        TypeDesc(Color3d, "colord[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Color3f, "colorf[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Color3h, "colorh[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Color4d, "colord[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(Color4f, "colorf[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(Color4h, "colorh[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(Double, "double", None, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(Double2, "double[2]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0)),
        TypeDesc(Double3, "double[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Double4, "double[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(float, "double", None, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(Float, "float", float, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(Float2, "float[2]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0)),
        TypeDesc(Float3, "float[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Float4, "float[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(
            Frame,
            "frame[4]",
            None,
            Method.ASSIGN,
            None,
            Method.ASSIGN,
            ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
        ),
        TypeDesc(Half, "half", np.half, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(Half2, "half[2]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0)),
        TypeDesc(Half3, "half[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Half4, "half[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(int, "int64", None, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(Int, "int", int_to_int32, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(Int2, "int[2]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0)),
        TypeDesc(Int3, "int[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Int4, "int[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(Matrix2d, "matrixd[2]", None, Method.ASSIGN, None, Method.ASSIGN, ((1, 0), (0, 1))),
        TypeDesc(Matrix3d, "matrixd[3]", None, Method.ASSIGN, None, Method.ASSIGN, ((1, 0, 0), (0, 1, 0), (0, 0, 1))),
        TypeDesc(
            Matrix4d,
            "matrixd[4]",
            None,
            Method.ASSIGN,
            None,
            Method.ASSIGN,
            ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
        ),
        TypeDesc(Normal3d, "normald[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Normal3f, "normalf[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Normal3h, "normalh[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Point3d, "pointd[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Point3f, "pointf[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Point3h, "pointh[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Quatd, "quatd[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(Quatf, "quatf[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(Quath, "quath[4]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0, 0)),
        TypeDesc(str, "string", None, Method.ASSIGN, None, Method.ASSIGN, ""),
        TypeDesc(TexCoord2d, "texcoordd[2]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0)),
        TypeDesc(TexCoord2f, "texcoordf[2]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0)),
        TypeDesc(TexCoord2h, "texcoordh[2]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0)),
        TypeDesc(TexCoord3d, "texcoordd[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(TexCoord3f, "texcoordf[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(TexCoord3h, "texcoordh[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Timecode, "timecode", None, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(Token, "token", None, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(UInt, "uint", int_to_uchar, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(UChar, "uchar", int_to_uchar, Method.ASSIGN, None, Method.ASSIGN, 0),
        TypeDesc(Vector3d, "vectord[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Vector3f, "vectorf[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
        TypeDesc(Vector3h, "vectorh[3]", None, Method.ASSIGN, None, Method.ASSIGN, (0, 0, 0)),
    ]

    user_types = []

    # --------------------------------------------------------------------------------
    def __init__(self):
        raise RuntimeError("TypeConversion is a static class, do not instantiate")

    # --------------------------------------------------------------------------------
    @classmethod
    @deprecated_function("Use og.Controller.attribute_type of og.AttributeType instead")
    def from_type(cls, type_desc: type) -> TypeDesc | None:
        """Searches the conversion registry using a python type.

        Args:
            type_desc: python type to convert

        Returns:
            TypeDesc for the found python type if it's found, None otherwise
        """
        for tb in cls.user_types:
            if tb.type == type_desc:
                return tb
        for tb in cls.types:
            if tb.type == type_desc:
                return tb
        return None

    # --------------------------------------------------------------------------------
    @classmethod
    @deprecated_function("Use og.Controller.attribute_type of og.AttributeType instead")
    def from_ogn_type(cls, og_type: str) -> TypeDesc | None:
        """Searches the conversion registry using an Omnigraph type.
        Searches the user types first, defaults to the system types.

        Args:
            og_type: string representing the incoming ogn type

        Returns:
            TypeDesc for the found python type if it's found, None otherwise
        """

        # TODO (OS): Solve for arrays
        for tb in cls.user_types:
            og_coded_type = tb.og_type
            if og_coded_type == og_type:
                return tb
        for tb in cls.types:
            og_coded_type = tb.og_type
            if og_coded_type == og_type:
                return tb
        return None

    # --------------------------------------------------------------------------------
    @classmethod
    @deprecated_function("Type conversions are no longer used")
    def register_type_conversion(
        cls,
        python_type: type,
        ogn_typename: str,
        python_to_ogn: callable = None,
        python_to_ogn_method: Method = Method.ASSIGN,
        ogn_to_python: callable = None,
        ogn_to_python_method: Method = Method.ASSIGN,
        default=None,
    ):
        """Registers a type conversion between a python type and an ogn type.
        Masks any existing system setting. If a previous user-submitted type conversion is registered,
        it will be overridden.

        Args:
            python_type: Type representation in python.
            ogn_typename: String representation of the ogn type. Node generation will fail on unrecognized types.
            python_to_ogn: [optional] function to convert a python return value to an OGN struct.
                           Signature is Callable[[[python_type], object]. Defaults to None
            ogn_to_python: [optional] function to convert an OGN struct to a python return value.
                           Signature is Callable[[[object], python_type]. Defaults to None
            ogn_to_python_method: [optional] Type
        """
        desc = TypeDesc(
            python_type, ogn_typename, python_to_ogn, python_to_ogn_method, ogn_to_python, ogn_to_python_method, default
        )
        unregistered = cls.unregister_type_conversion(python_type)
        if unregistered:
            carb.log_warn(
                "Registering an autograph type conversion for {type}->{ogn_typename} replaces anohter conversion for: {desc.type}->{og_type}"
            )

        cls.user_types.append(desc)

    # --------------------------------------------------------------------------------
    @classmethod
    @deprecated_function("Type conversions are no longer used")
    def unregister_type_conversion(cls, python_type: type = None, ogn_type_name: str = None) -> TypeDesc | None:
        """Unregisters a type conversion from python to ogn.
        Doesn't unregister system types.

        Args:
            python_type: the python type to be removed from support
            ogn_type_name: the ogn type name type to be removed from support

        Returns:
            The TypeDesc tuple just unregistered, or none.
        """
        if python_type is not None:
            for desc in cls.user_types:
                if desc.type == python_type:
                    cls.user_types.remove(desc)
                    return desc
        if ogn_type_name is not None:
            for desc in cls.user_types:
                if desc.og_type == ogn_type_name:
                    cls.user_types.remove(desc)
                    return desc
        return None
