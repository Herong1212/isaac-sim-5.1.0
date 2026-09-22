#*****************************************************************************
# Copyright 2022 NVIDIA Corporation. All rights reserved.
#*****************************************************************************

import sys
import os
import gc
import platform
import traceback
import pathlib
from collections import deque
from enum import Enum
from pxr import Usd
from pxr import Ar
from pxr import Plug
from pxr import Sdr
from pxr import Sdf
from pxr import Tf
from pxr import UsdShade
from pxr import Gf
from pxr import UsdGeom
from pxr import Kind
from pxr import UsdUI
import numpy        # used to represent Vectors, Matrices, and Colors
import re           # For command line args
from copy import deepcopy # Dictionary merging
import tempfile
import carb
import carb.settings

import omni.kit.commands
import omni.kit.test
import omni.kit.app

# load the binding module
carb.log_info("MDL python binding about to load ...")
####################
# Omniverse code
from omni.mdl import pymdlsdk
from omni.mdl import pymdl
import omni.client
async def copy_async(texture_path, dst_path):
    result = await omni.client.copy_async(texture_path, dst_path)
    return (result == omni.client.Result.OK or result == omni.client.Result.ERROR_ALREADY_EXISTS)
# Omniverse code
####################

# TODO: loading fails for debug builds of the pymdlsdk.pyd (or pymdlsdk.so on unix) module
carb.log_info("MDL python binding loaded")

#--------------------------------------------------------------------------------------------------
# USD and misc utilities
#--------------------------------------------------------------------------------------------------

_NodePortMode = dict()
_NodePortMode['no_node_port'] = -1
_NodePortMode['node_port_value_only'] = 0
_NodePortMode['node_port_fields_only'] = 1
_NodePortMode['node_port_value_and_fields'] = 2


_MdlIValueKindToUSD = {
    pymdlsdk.IValue.Kind.VK_BOOL: Sdf.ValueTypeNames.Bool,
    pymdlsdk.IValue.Kind.VK_INT : Sdf.ValueTypeNames.Int,
    pymdlsdk.IValue.Kind.VK_ENUM : Sdf.ValueTypeNames.Int,
    pymdlsdk.IValue.Kind.VK_FLOAT : Sdf.ValueTypeNames.Float,
    pymdlsdk.IValue.Kind.VK_DOUBLE : Sdf.ValueTypeNames.Double,
    pymdlsdk.IValue.Kind.VK_STRING : Sdf.ValueTypeNames.String,
    pymdlsdk.IValue.Kind.VK_COLOR : Sdf.ValueTypeNames.Color3f,
    pymdlsdk.IValue.Kind.VK_STRUCT : Sdf.ValueTypeNames.Token,
    pymdlsdk.IValue.Kind.VK_TEXTURE : Sdf.ValueTypeNames.Asset,
    pymdlsdk.IValue.Kind.VK_LIGHT_PROFILE : Sdf.ValueTypeNames.Asset,
    pymdlsdk.IValue.Kind.VK_BSDF_MEASUREMENT : Sdf.ValueTypeNames.Asset
}


_MdlITypeKindToUSDTable = {
    pymdlsdk.IType.Kind.TK_BOOL: Sdf.ValueTypeNames.Bool,
    pymdlsdk.IType.Kind.TK_INT : Sdf.ValueTypeNames.Int,
    pymdlsdk.IType.Kind.TK_ENUM : Sdf.ValueTypeNames.Int,
    pymdlsdk.IType.Kind.TK_FLOAT : Sdf.ValueTypeNames.Float,
    pymdlsdk.IType.Kind.TK_DOUBLE : Sdf.ValueTypeNames.Double,
    pymdlsdk.IType.Kind.TK_STRING : Sdf.ValueTypeNames.String,
    pymdlsdk.IType.Kind.TK_COLOR : Sdf.ValueTypeNames.Color3f,
    pymdlsdk.IType.Kind.TK_STRUCT : Sdf.ValueTypeNames.Token,
    pymdlsdk.IType.Kind.TK_TEXTURE : Sdf.ValueTypeNames.Asset,
    pymdlsdk.IType.Kind.TK_LIGHT_PROFILE : Sdf.ValueTypeNames.Asset,
    pymdlsdk.IType.Kind.TK_BSDF_MEASUREMENT : Sdf.ValueTypeNames.Asset
}
# TODO:
# mi::neuraylib::IType::TK_BSDF
# mi::neuraylib::IType::TK_EDF
# mi::neuraylib::IType::TK_VDF

def MdlITypeToUSD(type):
    try:
        kind = type.kind
        if kind in _MdlITypeKindToUSDTable:
            return _MdlITypeKindToUSDTable[kind]
        else:
            if kind == pymdlsdk.IType.Kind.TK_VECTOR:
                size = type.size
                if type.element_type.kind == pymdlsdk.IType.Kind.TK_FLOAT:
                    if size == 2:
                        return Sdf.ValueTypeNames.Float2
                    elif size == 3:
                        return Sdf.ValueTypeNames.Float3
                    elif size == 4:
                        return Sdf.ValueTypeNames.Float4
                elif type.element_type.kind == pymdlsdk.IType.Kind.TK_INT or \
                    type.element_type.kind == pymdlsdk.IType.Kind.TK_BOOL:
                    if size == 2:
                        return Sdf.ValueTypeNames.Int2
                    elif size == 3:
                        return Sdf.ValueTypeNames.Int3
                    elif size == 4:
                        return Sdf.ValueTypeNames.Int4
                elif type.element_type.kind == pymdlsdk.IType.Kind.TK_DOUBLE:
                    if size == 2:
                        return Sdf.ValueTypeNames.Double2
                    elif size == 3:
                        return Sdf.ValueTypeNames.Double3
                    elif size == 4:
                        return Sdf.ValueTypeNames.Double4
        return None
    except Exception as e:
        carb.log_error("Error while converting MDL type to USD type")
        return None


def python_vector_to_usd_value(value):
    dtype = value.dtype
    size = value.size
    out = None
    if dtype == numpy.int32 or dtype == bool:
        if size == 2:
            out = Gf.Vec2i(0)
        elif size == 3:
            out = Gf.Vec3i(0)
        elif size == 4:
            out = Gf.Vec4i(0)
        if out != None:
            for i in range(size):
                out[i] = int(value[i][0])
    elif dtype == numpy.float32:
        if size == 2:
            out = Gf.Vec2f(0)
        elif size == 3:
            out = Gf.Vec3f(0)
        elif size == 4:
            out = Gf.Vec4f(0)
        if out != None:
            for i in range(size):
                out[i] = float(value[i][0])
    elif dtype == numpy.float64:
        if size == 2:
            out = Gf.Vec2d(0)
        elif size == 3:
            out = Gf.Vec3d(0)
        elif size == 4:
            out = Gf.Vec4d(0)
        if out != None:
            for i in range(size):
                out[i] = numpy.float64(value[i][0])
    return out

def custom_data_from_python_vector(value):
    dtype = value.dtype
    out = dict()
    if dtype == bool:
        size = value.size
        out = dict({"mdl":{"type" : "bool{}".format(size)}})
    return out

def python_matrix_to_usd_type(dtype, nrow, ncol):
    #     numpyType   Column Row           OutType
    m = { 'float32' : { 2 : { 2 : Sdf.ValueTypeNames.Matrix2d,
                                3 : Sdf.ValueTypeNames.Float3Array,
                                4 : Sdf.ValueTypeNames.Float4Array},
                          3 : { 2 : Sdf.ValueTypeNames.Float2Array,
                                3 : Sdf.ValueTypeNames.Matrix3d,
                                4 : Sdf.ValueTypeNames.Float4Array},
                          4 : { 2 : Sdf.ValueTypeNames.Float2Array,
                                3 : Sdf.ValueTypeNames.Float3Array,
                                4 : Sdf.ValueTypeNames.Matrix4d }},
          'float64' : { 2 : { 2 : Sdf.ValueTypeNames.Matrix2d,
                                3 : Sdf.ValueTypeNames.Double3Array,
                                4 : Sdf.ValueTypeNames.Double4Array},
                          3 : { 2 : Sdf.ValueTypeNames.Double2Array,
                                3 : Sdf.ValueTypeNames.Matrix3d,
                                4 : Sdf.ValueTypeNames.Double4Array},
                          4 : { 2 : Sdf.ValueTypeNames.Double2Array,
                                3 : Sdf.ValueTypeNames.Double3Array,
                                4 : Sdf.ValueTypeNames.Matrix4d }}}
    return m[dtype.name][ncol][nrow]

def python_matrix_to_usd_value(value):
    dtype = value.dtype
    nrow = value.shape[0]
    ncol = value.shape[1]
    out = None
    if dtype == numpy.float32:
        if ncol == 2:
            if nrow == 2:
                out = Gf.Matrix2d(0)
                out.SetColumn(0, Gf.Vec2d(float(value[0][0]), float(value[0][1])))
                out.SetColumn(1, Gf.Vec2d(float(value[1][0]), float(value[1][1])))
            elif nrow == 3:
                out = [Gf.Vec3f(float(value[0][0]), float(value[1][0]), float(value[2][0])),
                       Gf.Vec3f(float(value[0][1]), float(value[1][1]), float(value[2][1]))]
            elif nrow == 4:
                out = [Gf.Vec4f(float(value[0][0]), float(value[1][0]), float(value[2][0]), float(value[3][0])),
                       Gf.Vec4f(float(value[0][1]), float(value[1][1]), float(value[2][1]), float(value[3][1]))]
        elif ncol == 3:
            if nrow == 2:
                out = [Gf.Vec2f(float(value[0][0]), float(value[1][0])),
                       Gf.Vec2f(float(value[0][1]), float(value[1][1])),
                       Gf.Vec2f(float(value[0][2]), float(value[1][2]))]
            elif nrow == 3:
                out = Gf.Matrix3d(0)
                out.SetColumn(0, Gf.Vec3d(float(value[0][0]), float(value[0][1]), float(value[0][2])))
                out.SetColumn(1, Gf.Vec3d(float(value[1][0]), float(value[1][1]), float(value[1][2])))
                out.SetColumn(2, Gf.Vec3d(float(value[2][0]), float(value[2][1]), float(value[2][2])))
            elif nrow == 4:
                out = [Gf.Vec4f(float(value[0][0]), float(value[1][0]), float(value[2][0]), float(value[3][0])),
                       Gf.Vec4f(float(value[0][1]), float(value[1][1]), float(value[2][1]), float(value[3][1])),
                       Gf.Vec4f(float(value[0][2]), float(value[1][2]), float(value[2][2]), float(value[3][2]))]
        elif ncol == 4:
            if nrow == 2:
                out = [Gf.Vec2f(float(value[0][0]), float(value[1][0])),
                       Gf.Vec2f(float(value[0][1]), float(value[1][1])),
                       Gf.Vec2f(float(value[0][2]), float(value[1][2])),
                       Gf.Vec2f(float(value[0][3]), float(value[1][3]))]
            elif nrow == 3:
                out = [Gf.Vec3f(float(value[0][0]), float(value[1][0]), float(value[2][0])),
                       Gf.Vec3f(float(value[0][1]), float(value[1][1]), float(value[2][1])),
                       Gf.Vec3f(float(value[0][2]), float(value[1][2]), float(value[2][2])),
                       Gf.Vec3f(float(value[0][3]), float(value[1][3]), float(value[2][3]))]
            elif nrow == 4:
                out = Gf.Matrix4d(0)
                out.SetColumn(0, Gf.Vec4d(float(value[0][0]), float(value[0][1]), float(value[0][2]), float(value[0][3])))
                out.SetColumn(1, Gf.Vec4d(float(value[1][0]), float(value[1][1]), float(value[1][2]), float(value[1][3])))
                out.SetColumn(2, Gf.Vec4d(float(value[2][0]), float(value[2][1]), float(value[2][2]), float(value[2][3])))
                out.SetColumn(3, Gf.Vec4d(float(value[3][0]), float(value[3][1]), float(value[3][2]), float(value[3][3])))
    elif dtype == numpy.float64:
        if ncol == 2:
            if nrow == 2:
                out = Gf.Matrix2d(0)
                out.SetColumn(0, Gf.Vec2d(float(value[0][0]), float(value[0][1])))
                out.SetColumn(1, Gf.Vec2d(float(value[1][0]), float(value[1][1])))
            elif nrow == 3:
                out = [Gf.Vec3d(float(value[0][0]), float(value[1][0]), float(value[2][0])),
                       Gf.Vec3d(float(value[0][1]), float(value[1][1]), float(value[2][1]))]
            elif nrow == 4:
                out = [Gf.Vec4d(float(value[0][0]), float(value[1][0]), float(value[2][0]), float(value[3][0])),
                       Gf.Vec4d(float(value[0][1]), float(value[1][1]), float(value[2][1]), float(value[3][1]))]
        elif ncol == 3:
            if nrow == 2:
                out = [Gf.Vec2d(float(value[0][0]), float(value[1][0])),
                       Gf.Vec2d(float(value[0][1]), float(value[1][1])),
                       Gf.Vec2d(float(value[0][2]), float(value[1][2]))]
            elif nrow == 3:
                out = Gf.Matrix3d(0)
                out.SetColumn(0, Gf.Vec3d(float(value[0][0]), float(value[0][1]), float(value[0][2])))
                out.SetColumn(1, Gf.Vec3d(float(value[1][0]), float(value[1][1]), float(value[1][2])))
                out.SetColumn(2, Gf.Vec3d(float(value[2][0]), float(value[2][1]), float(value[2][2])))
            elif nrow == 4:
                out = [Gf.Vec4d(float(value[0][0]), float(value[1][0]), float(value[2][0]), float(value[3][0])),
                       Gf.Vec4d(float(value[0][1]), float(value[1][1]), float(value[2][1]), float(value[3][1])),
                       Gf.Vec4d(float(value[0][2]), float(value[1][2]), float(value[2][2]), float(value[3][2]))]
        elif ncol == 4:
            if nrow == 2:
                out = [Gf.Vec2d(float(value[0][0]), float(value[1][0])),
                       Gf.Vec2d(float(value[0][1]), float(value[1][1])),
                       Gf.Vec2d(float(value[0][2]), float(value[1][2])),
                       Gf.Vec2d(float(value[0][3]), float(value[1][3]))]
            elif nrow == 3:
                out = [Gf.Vec3d(float(value[0][0]), float(value[1][0]), float(value[2][0])),
                       Gf.Vec3d(float(value[0][1]), float(value[1][1]), float(value[2][1])),
                       Gf.Vec3d(float(value[0][2]), float(value[1][2]), float(value[2][2])),
                       Gf.Vec3d(float(value[0][3]), float(value[1][3]), float(value[2][3]))]
            elif nrow == 4:
                out = Gf.Matrix4d(0)
                out.SetColumn(0, Gf.Vec4d(float(value[0][0]), float(value[0][1]), float(value[0][2]), float(value[0][3])))
                out.SetColumn(1, Gf.Vec4d(float(value[1][0]), float(value[1][1]), float(value[1][2]), float(value[1][3])))
                out.SetColumn(2, Gf.Vec4d(float(value[2][0]), float(value[2][1]), float(value[2][2]), float(value[2][3])))
                out.SetColumn(3, Gf.Vec4d(float(value[3][0]), float(value[3][1]), float(value[3][2]), float(value[3][3])))
    return out

def python_array_to_usd_type(value):
    array_simple_conversion = {
        bool : Sdf.ValueTypeNames.BoolArray,
        int : Sdf.ValueTypeNames.IntArray,
        # TODO: enum?
        # AddArrayOfSimpleConversion(mi::neuraylib::IType::TK_ENUM, SdfValueTypeNames->IntArray);
        float : Sdf.ValueTypeNames.FloatArray,
        # TODO: double ?
        # AddArrayOfSimpleConversion(mi::neuraylib::IType::TK_DOUBLE, SdfValueTypeNames->DoubleArray);
        str : Sdf.ValueTypeNames.StringArray,
        pymdlsdk.IType.Kind.TK_COLOR :  Sdf.ValueTypeNames.Color3fArray
        # TODO: AddArrayOfSimpleConversion(mi::neuraylib::IType::TK_STRUCT, SdfValueTypeNames->TokenArray);
        # TODO: AddArrayOfSimpleConversion(mi::neuraylib::IType::TK_TEXTURE, SdfValueTypeNames->AssetArray);
        }

    array_of_vector_conversion = {
        numpy.bool_ : { 2 : Sdf.ValueTypeNames.Int2Array,
                        3 : Sdf.ValueTypeNames.Int3Array,
                        4 : Sdf.ValueTypeNames.Int4Array },
        numpy.int32 : { 2 : Sdf.ValueTypeNames.Int2Array,
                        3 : Sdf.ValueTypeNames.Int3Array,
                        4 : Sdf.ValueTypeNames.Int4Array },
        numpy.float32 : { 2 : Sdf.ValueTypeNames.Float2Array,
                          3 : Sdf.ValueTypeNames.Float3Array,
                          4 : Sdf.ValueTypeNames.Float4Array },
        numpy.float64 : { 2 : Sdf.ValueTypeNames.Double2Array,
                          3 : Sdf.ValueTypeNames.Double3Array,
                          4 : Sdf.ValueTypeNames.Double4Array }
    }

    # // Array of matrix
    #     numpyType   Column Row           OutType
    array_of_matrix = \
        { numpy.float32 : { 2 : { 2 : Sdf.ValueTypeNames.Matrix2dArray,
                                3 : Sdf.ValueTypeNames.FloatArray,
                                4 : Sdf.ValueTypeNames.FloatArray},
                          3 : { 2 : Sdf.ValueTypeNames.FloatArray,
                                3 : Sdf.ValueTypeNames.Matrix3dArray,
                                4 : Sdf.ValueTypeNames.FloatArray},
                          4 : { 2 : Sdf.ValueTypeNames.FloatArray,
                                3 : Sdf.ValueTypeNames.FloatArray,
                                4 : Sdf.ValueTypeNames.Matrix4dArray }},
          numpy.float64 : { 2 : { 2 : Sdf.ValueTypeNames.Matrix2dArray,
                                3 : Sdf.ValueTypeNames.DoubleArray,
                                4 : Sdf.ValueTypeNames.DoubleArray},
                          3 : { 2 : Sdf.ValueTypeNames.DoubleArray,
                                3 : Sdf.ValueTypeNames.Matrix3dArray,
                                4 : Sdf.ValueTypeNames.DoubleArray},
                          4 : { 2 : Sdf.ValueTypeNames.DoubleArray,
                                3 : Sdf.ValueTypeNames.DoubleArray,
                                4 : Sdf.ValueTypeNames.Matrix4dArray }}}


    dtype = type(value[0])
    if dtype in array_simple_conversion:
        return array_simple_conversion[dtype]
    elif dtype == numpy.ndarray:
        shape = value[0].shape
        # Array
        if len(shape) > 1 and shape[1] > 1:
            # Array of matrices
            elemtype = type(value[0][0][0])
            if elemtype in array_of_matrix:
                if shape[1] in array_of_matrix[elemtype]:
                    if shape[0] in array_of_matrix[elemtype][shape[1]]:
                        return array_of_matrix[elemtype][shape[1]][shape[0]]
        elif type(value[0][0]) == numpy.ndarray:
            # Array of vectors
            etype = type(value[0][0][0])
            size = len(value[0])
            if etype in array_of_vector_conversion:
                if size in array_of_vector_conversion[etype]:
                    return array_of_vector_conversion[etype][size]
            else:
                carb.log_warn("Array of vector type not supported for type/size: {}/{}".format(etype, size))
        elif len(value[0]) == 3:
            # Assume this is a color
            return array_simple_conversion[pymdlsdk.IType.Kind.TK_COLOR]
        else:
            carb.log_warn("Array type not supported for type/shape: {}/{}".format(dtype, shape))
    else:
        carb.log_warn("Type not supported for type: {}".format(dtype))

def python_array_to_usd_value(value):
    dtype = type(value[0])
    out = None
    if dtype == bool or \
        dtype == int or \
        dtype == float or \
        dtype == str:
        return value
    elif dtype == numpy.ndarray:
        # Array
        shape = value[0].shape
        if len(shape) > 1 and shape[1] > 1:
            # Array of matrices
            elemtype = type(value[0][0][0])
            nrow = shape[0]
            ncol = shape[1]
            out = None
            arraysize = len(value)
            if ncol == nrow:
                if ncol == 2:
                    mattype = Gf.Matrix2d
                if ncol == 3:
                    mattype = Gf.Matrix3d
                if ncol == 4:
                    mattype = Gf.Matrix4d
                out = []
                for i in range(arraysize):
                    mat = mattype(0)
                    for c in range(ncol):
                        row = []
                        for r in range(nrow):
                            row.append(float(value[i][c][r]))
                        mat.SetColumn(c, row)
                    out.append(mat)
            else:
                if elemtype == numpy.float32:
                    otype = float
                elif elemtype == numpy.float64:
                    otype = numpy.float64
                out = []
                for i in range(arraysize):
                    for c in range(ncol):
                        for r in range(nrow):
                            out.append(otype(value[i][r][c]))
        elif type(value[0][0]) == numpy.ndarray:
            # Array of vectors
            etype = type(value[0][0][0])
            size = len(value)
            out = []
            if etype == numpy.bool_ or \
               etype == numpy.int32:
                otype = int
            elif etype == numpy.float32:
                otype = float
            elif etype == numpy.float64:
                otype = numpy.float64
            itemsize = len(value[0])
            for i in range(size):
                ll = []
                for j in range(itemsize):
                    ll.append(otype(value[i][j]))
                out.append(ll)
        elif len(value[0]) == 3:
            # Assume this is a color
            size = len(value)
            out = []
            for i in range(size):
                out.append([value[0][0], value[0][1], value[0][2]])
    return out

def custom_data_from_python_array(value):
    # type = dict({"mdl":{"type" : "array of matrix"}})
    out = dict()
    dtype = type(value[0])
    arraysize = len(value)
    if dtype == numpy.ndarray:
        # Array
        shape = value[0].shape
        if len(shape) > 1 and shape[1] > 1:
            # Array of matrices
            elemtype = type(value[0][0][0])
            nrow = shape[0]
            ncol = shape[1]
            elemtype = type(value[0][0][0])
            if ncol != nrow or elemtype == numpy.float32:
                # Non square matrices
                typename = ""
                if elemtype == numpy.float32:
                    typename = "float"
                elif elemtype == numpy.float64:
                    typename = "double"
                out = dict({"mdl":{"type" : "{}{}x{}[{}]".format(typename, ncol, nrow, arraysize)}})
        elif type(value[0][0]) == numpy.ndarray:
            # Array of vectors
            etype = type(value[0][0][0])
            if etype == numpy.bool_:
                itemsize = len(value[0])
                out = dict({"mdl":{"type" : "bool{}[{}]".format(itemsize, arraysize)}})
    return out

def mdl_type_to_usd_type(val : pymdl.ArgumentConstant):
    if not val:
        return None
    kind = val.type.kind
    USDType = MdlITypeToUSD(val.type)
    if not USDType is None:
        return USDType
    else:
        # A bit more work is required to derive the type
        if kind == pymdlsdk.IType.Kind.TK_VECTOR:
        # TK_VECTOR is covered by MdlITypeToUSD
        #     return python_vector_to_usd_type(val.value.dtype, val.value.size)
            pass
        elif kind == pymdlsdk.IType.Kind.TK_MATRIX:
            return python_matrix_to_usd_type(val.value.dtype, val.value.shape[0], val.value.shape[1])
        elif kind == pymdlsdk.IType.Kind.TK_ARRAY:
            return python_array_to_usd_type(val.value)
    return None

class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def top(self):
        return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)

# When converting from MDL to USD user can choose the USD output format
# SHADER: A single shader is output at the root of the USD Stage
# MATERIAL: A single material is output at the root of the USD Stage
# MATERIAL_AND_GEOMETRY: Geometry and Material (bound to the geometry) are output in the USD Stage
class OutputType(Enum):
    SHADER = 1
    MATERIAL = 2
    MATERIAL_AND_GEOMETRY = 3

class ConverterContext():
    def __init__(self):
        self.neuray: pymdlsdk.INeuray = None
        self.db_scope_name: str = ""
        self.transaction: pymdlsdk.ITransaction = None
        self.mdl_factory: pymdlsdk.IMdl_factory = None
        self.stage = None
        self.modules = Stack()
        self.usd_materials = Stack()
        self.parameter_names = Stack()
        self.usd_shaders = Stack()
        self.custom_data = Stack()
        self.type_annotation = True
        self.mdl_to_usd_output = OutputType.SHADER
        self.mdl_to_usd_output_material_nested_shaders = False # Nested/deep or flat shader tree
        self.ov_neuray = None
        GetUniqueNameInStage.s_uniqueID = 0 # Reset the unique name counter to get same output between 2 runs

    def enable_type_annotation(self):
        self.type_annotation = True

    def disable_type_annotation(self):
        self.type_annotation = False

    def is_type_annotation_enabled(self):
        return self.type_annotation == True

    def set_neuray(self, neuray: pymdlsdk.INeuray):
        self.neuray = neuray
        self.mdl_factory = neuray.get_api_component(pymdlsdk.IMdl_factory)

    def set_dbScopeName(self, db_scope_name: str):
        self.db_scope_name = db_scope_name

    def set_transaction(self, transaction: pymdlsdk.ITransaction):
        self.transaction = transaction

    def set_stage(self, stage):
        self.stage = stage

    def push_module(self, module):
        self.modules.push(module)

    def pop_module(self):
        return self.modules.pop()

    def current_module(self):
        return self.modules.top()

    def push_usd_material(self, material):
        self.usd_materials.push(material)

    def pop_usd_material(self):
        return self.usd_materials.pop()

    def current_usd_material(self):
        return self.usd_materials.top()

    def push_parameter_name(self, parm):
        self.parameter_names.push(parm)

    def pop_parameter_name(self):
        return self.parameter_names.pop()

    def current_parameter_name(self):
        return self.parameter_names.top()

    def push_usd_shader(self, shader):
        self.usd_shaders.push(shader)

    def pop_usd_shader(self):
        return self.usd_shaders.pop()

    def current_usd_shader(self):
        return self.usd_shaders.top()

    def push_custom_data(self, custom_data):
        self.custom_data.push(custom_data)

    def pop_custom_data(self):
        return self.custom_data.pop()

    def current_custom_data(self):
        return self.custom_data.top()

# Example: 'mdl::OmniSurface::OmniSurfaceBase::OmniSurfaceBase'
# Return: 'OmniSurface/OmniSurfaceBase.mdl'
def prototype_to_source_asset(prototype):
    source_asset = prototype
    if source_asset[:5] == "mdl::":
        source_asset = source_asset[3:] # Remove leading "mdl"
    if source_asset[:2] == "::":
        source_asset = source_asset[2:] # Remove leading "::"
    ll = source_asset.split("::")
    source_asset = '/'.join(ll[0:-1]) # Drop last part which is material name
    source_asset = source_asset + ".mdl" # Append ".mdl" extension
    return source_asset

def __get_stage_folder(stage):
    stageFolder: str = os.path.dirname(str(stage.GetRootLayer().resolvedPath))
    url_parts = omni.client.break_url(stageFolder)
    if not url_parts.scheme:
        stageFolder = pathlib.Path(stageFolder).as_posix()
    return make_uri_with_scheme(stageFolder)

def module_mdl_name_to_source_asset(context, module_mdl_name):
    if module_mdl_name == '::%3Cbuiltins%3E':
        return 'mdl-builtin.mdl'
    unmangle_helper = UnmangleAndFixMDLSearchPath(context)
    stageFolder = None
    if not context.stage is None:
        stageFolder = __get_stage_folder(context.stage)

    (isMangled, wasSuccess, newmodule_mdl_name) = unmangle_helper.unmangle_mdl_module(module_mdl_name, stageFolder)
    if wasSuccess and newmodule_mdl_name != module_mdl_name:
        if not newmodule_mdl_name.endswith(".mdl"):
            newmodule_mdl_name = newmodule_mdl_name + '.mdl'
        return newmodule_mdl_name
    if isMangled and not wasSuccess:
        # Better return empty asset than garbage asset
        return ''

    source_asset = module_mdl_name
    if source_asset[:5] == "mdl::":
        source_asset = source_asset[3:] # Remove leading "mdl"
    if source_asset[:2] == "::":
        source_asset = source_asset[2:] # Remove leading "::"
    source_asset = source_asset.replace("::", "/") # Replace "::" with "/"
    source_asset = source_asset + ".mdl" # Append ".mdl" extension
    return source_asset

def source_asset_to_module_name(source_asset, context):
    module_name = source_asset
    module_name = os.path.normpath(module_name)
    if os.path.isabs(module_name):
        # Absolute path, try to find a mathing search path and remove it
        with context.neuray.get_api_component(pymdlsdk.IMdl_configuration) as cfg:
            if cfg.is_valid_interface():
                for i in range(cfg.get_mdl_paths_length()):
                    sp = cfg.get_mdl_path(i)
                    sp = os.path.normpath(sp.get_c_str())
                    if module_name.find(sp) == 0:
                        module_name = module_name[len(sp):]
                        break
    # Split path
    ll = module_name.split(os.sep)
    # Concat path using '::' separator
    module_name = "::".join(ll)
    if not module_name[0:2] == "::":
        # Prepend '::'
        module_name = "::" + module_name
    if module_name[-4:] == ".mdl":
        # Remove '.mdl' extension
        module_name = module_name[0:-4]
    return module_name

def db_name_to_prim_name(dbname):
    name = dbname
    name = name.split("(")[0] # Remove arguments
    name = name.split("::")[-1] # Remove package, module
    name = name.replace(".", "_") # Replace '.'
    return name

def mdl_name_to_sub_identifier(mdl_name, fct_call=False):
    sub_id = mdl_name
    if sub_id[:5] == "mdl::":
        sub_id = sub_id[3:] # Remove leading "mdl"
    # split the identifier from the arguments
    names = sub_id.split("(")
    # keep only the last name from the identifier
    sub_id = names[0].split("::")[-1]
    if fct_call:
        # concat with args
        if len(names) > 1:
            sub_id = sub_id + "(" + names[1]
    return sub_id

# Return a unique SdfPath for the current stage
class GetUniqueNameInStage:
    s_uniqueID = 0
    @staticmethod
    def get(stage, path):
        unique_path = path
        while stage.GetPrimAtPath(unique_path).IsValid():
            unique_path = Sdf.Path(str(path) + str(GetUniqueNameInStage.s_uniqueID))
            GetUniqueNameInStage.s_uniqueID += 1
        return unique_path

class GetUniqueName:
    s_uniqueID = 0
    @staticmethod
    def get(transaction, prefix_in):
        prefix = prefix_in
        if len(prefix)==0:
            prefix = "elt"
        if not transaction.access_as(pymdlsdk.IInterface, prefix).is_valid_interface():
            return prefix
        while True:
            prefix = prefix_in + "_" + str(GetUniqueName.s_uniqueID)
            GetUniqueName.s_uniqueID += 1
            if not transaction.access_as(pymdlsdk.IInterface, prefix).is_valid_interface():
                return prefix

def removeHeadings(text : str, heading : str):
    if text.startswith(heading):
        return text[len(heading):]
    return text

def material_to_stage_output_material(context, function: pymdl.FunctionDefinition):
    return material_to_stage_output_material_and_geo(context, function, want_geometry = False)

def material_to_stage_output_material_and_geo(context, function: pymdl.FunctionDefinition, want_geometry = True):
    neuray = context.neuray
    transaction = context.transaction
    stage = context.stage

    db_name = function.dbName

    materialName = db_name_to_prim_name(db_name)

    currentUSDMaterial = None
    # if a current USD Material is set, create the shader below the given material
    if context.usd_materials.size() > 0:
        currentUSDMaterial = context.current_usd_material()

    if currentUSDMaterial:
        rootPath = currentUSDMaterial.GetPrim().GetParent().GetPath()
        materialName = currentUSDMaterial.GetPrim().GetName()
    else:
        # Start at root
        rootPath = Sdf.Path('/')

    spherePrim = None

    if want_geometry:
        xform = UsdGeom.Xform.Define(stage,"/World")
        # Add geometry
        spherePrim = UsdGeom.Sphere.Define(stage, xform.GetPath().AppendChild('Geom'))
        model = Usd.ModelAPI(xform)
        model.SetKind(Kind.Tokens.component)
        # Create Looks scope
        # Scope is the simplest grouping primitive...
        scope = UsdGeom.Scope.Define(stage, xform.GetPath().AppendChild('Looks'))
        rootPath = scope.GetPath()
        model = Usd.ModelAPI(scope)
        model.SetKind(Kind.Tokens.model)

    material = None

    # Create material
    material = UsdShade.Material.Define(stage, rootPath.AppendChild(materialName))
    if spherePrim != None:
        # Bind material to geometry
        UsdShade.MaterialBindingAPI(spherePrim).Bind(material)

    # Create surface shader
    surfaceShader = UsdShade.Shader.Define(stage, material.GetPath().AppendChild("Shader"))
    # Create surface shader output port
    outPort = surfaceShader.CreateOutput('out', Sdf.ValueTypeNames.Token)

    # Create material output port
    terminal = material.CreateOutput('mdl:surface', Sdf.ValueTypeNames.Token)
    # Connect material output to shader output
    terminal.ConnectToSource(outPort)

    terminal = material.CreateOutput('mdl:volume', Sdf.ValueTypeNames.Token)
    terminal.ConnectToSource(outPort)

    terminal = material.CreateOutput('mdl:displacement', Sdf.ValueTypeNames.Token)
    terminal.ConnectToSource(outPort)

    # Determine module asset
    module_interface : pymdl.Module
    module_interface = context.current_module()
    module = module_interface.mdlName
    source_asset = module_mdl_name_to_source_asset(context, module)

    # Example:
    # uniform token info:implementationSource = "sourceAsset"
    # uniform asset info:mdl:sourceAsset = @nvidia/core_definitions.mdl@
    # uniform token info:mdl:sourceAsset:subIdentifier = "::nvidia::core_definitions::flex_material"
    surfaceShader.GetImplementationSourceAttr().Set("sourceAsset")
    surfaceShader.SetSourceAsset(Sdf.AssetPath(source_asset), "mdl")
    node_identifier = function_to_sub_identifier(context, function)
    surfaceShader.GetPrim().CreateAttribute("info:mdl:sourceAsset:subIdentifier", Sdf.ValueTypeNames.Token, False, Sdf.VariabilityUniform).Set(node_identifier)

    context.stage.SetDefaultPrim(material.GetPrim())

    context.push_usd_material(material)
    context.push_usd_shader(surfaceShader)
    context.push_custom_data(dict())

    definition_to_stage(context, function)

    # Annotations
    anno_dict = get_annotations_dict(context, function)
    add_annotations_to_prim(surfaceShader.GetPrim(), anno_dict)
    add_annotations_to_node(surfaceShader, anno_dict)

    context.pop_custom_data()
    context.pop_usd_shader()
    context.pop_usd_material()

    return True

def material_to_stage_output_shader(context, function: pymdl.FunctionDefinition):
    neuray = context.neuray
    transaction = context.transaction
    stage = context.stage

    db_name = function.dbName

    materialName = db_name_to_prim_name(db_name)
    currentUSDMaterial = None
    # if a current USD Material is set, create the shader below the given material
    if context.usd_materials.size() > 0:
        currentUSDMaterial = context.current_usd_material()

    if currentUSDMaterial:
        rootPath = currentUSDMaterial.GetPath()
    else:
        # Start at root
        rootPath = Sdf.Path('/')

    material = UsdShade.Shader.Define(stage, rootPath.AppendChild(materialName))
    # Create output port
    outPort = material.CreateOutput('out', Sdf.ValueTypeNames.Token)
    outPort.SetRenderType("material")

    # Determine module asset
    module_interface : pymdl.Module
    module_interface = context.current_module()
    module = module_interface.mdlName
    source_asset = module_mdl_name_to_source_asset(context, module)

    # Example:
    # uniform token info:implementationSource = "sourceAsset"
    # uniform asset info:mdl:sourceAsset = @nvidia/core_definitions.mdl@
    # uniform token info:mdl:sourceAsset:subIdentifier = "::nvidia::core_definitions::flex_material"
    material.GetImplementationSourceAttr().Set("sourceAsset")
    material.SetSourceAsset(Sdf.AssetPath(source_asset), "mdl")
    node_identifier = function_to_sub_identifier(context, function)
    material.GetPrim().CreateAttribute("info:mdl:sourceAsset:subIdentifier", Sdf.ValueTypeNames.Token, False, Sdf.VariabilityUniform).Set(node_identifier)

    context.stage.SetDefaultPrim(material.GetPrim())

    context.push_usd_material(material)
    context.push_usd_shader(material)
    context.push_custom_data(dict())

    definition_to_stage(context, function)

    # Annotations
    anno_dict = get_annotations_dict(context, function)
    add_annotations_to_prim(material.GetPrim(), anno_dict)
    add_annotations_to_node(material, anno_dict)

    context.pop_custom_data()
    context.pop_usd_shader()
    context.pop_usd_material()

    if currentUSDMaterial:
        terminal = currentUSDMaterial.GetOutput('mdl:surface')
        # Connect material output to shader output
        terminal.ConnectToSource(outPort)

    return True

def material_to_stage(context, function: pymdl.FunctionDefinition):
    if function is None:
        carb.log_error(f"Invalid MDL material")
        return False

    if context.mdl_to_usd_output == OutputType.SHADER:
        return material_to_stage_output_shader(context, function)
    elif context.mdl_to_usd_output == OutputType.MATERIAL:
        return material_to_stage_output_material(context, function)
    elif context.mdl_to_usd_output == OutputType.MATERIAL_AND_GEOMETRY:
        return material_to_stage_output_material_and_geo(context, function)

def module_to_stage(context, module: pymdl.Module):

    context.push_module(module)

    for simple_name, overloads in module.functions.items():
        f: pymdl.FunctionDefinition
        for f in overloads:
            material_to_stage(context, f)

    context.push_custom_data(dict())
    anno_dict = get_annotations_dict(context, module)
    context.pop_custom_data()
    add_annotations_to_stage(context, context.stage, anno_dict)

    context.pop_module()

def mdl_prim_to_usd(context : ConverterContext, stage: Usd.Stage, prim: Usd.Prim, createNewMaterial: bool = False):
    inst_name = None
    mdl_entity = None
    mdl_entity_snapshot = None
    if context.ov_neuray == None:
        return

    # Get the shader prim from Material
    shader_prim = get_shader_prim(context.stage, prim.GetPath())

    mdl_entity = context.ov_neuray.createMdlEntity(shader_prim.GetPath().pathString, dbScopeName=context.ov_neuray.getCurrentDefaultScope())
    mdl_entity_snapshot = None
    if not mdl_entity.getMdlModule() == None:
        mdl_entity_snapshot = context.ov_neuray.createMdlEntitySnapshot(mdl_entity)
        inst_name = mdl_entity_snapshot.dbName

    source_asset = Sdf.AssetPath("")
    shader = UsdShade.Shader(shader_prim)
    if shader:
        imp_source = shader.GetImplementationSourceAttr().Get()
        if imp_source == "sourceAsset":
            # Retrieve module name
            source_asset = shader.GetSourceAsset("mdl")

    material = UsdShade.Material(prim)

    if createNewMaterial:
        rootPath = Sdf.Path(prim.GetPath().GetParentPath())
        # Create material
        materialName = prim.GetName() + "_converted"
        # Find unique name
        materialName = GetUniqueNameInStage.get(stage, rootPath.AppendChild(materialName))
        material = UsdShade.Material.Define(stage, materialName)

    # Create surface shader
    surfaceShader = UsdShade.Shader.Define(stage, material.GetPath().AppendChild(shader_prim.GetName()))
    # Create output port
    outPort = surfaceShader.CreateOutput('out', Sdf.ValueTypeNames.Token)

    # Create material output port
    terminal = material.CreateOutput('mdl:surface', Sdf.ValueTypeNames.Token)
    # Connect material output to shader output
    terminal.ConnectToSource(outPort)

    terminal = material.CreateOutput('mdl:volume', Sdf.ValueTypeNames.Token)
    terminal.ConnectToSource(outPort)

    terminal = material.CreateOutput('mdl:displacement', Sdf.ValueTypeNames.Token)
    terminal.ConnectToSource(outPort)

    context.push_usd_material(material)
    context.push_usd_shader(surfaceShader)
    context.push_custom_data(dict())

    fctCall = pymdl.FunctionCall._fetchFromDb(context.transaction, inst_name)

    handle_function_call(context, fctCall)

    context.pop_usd_material()
    context.pop_usd_shader()
    context.pop_custom_data()

    if not mdl_entity_snapshot == None:
        context.ov_neuray.destroyMdlEntitySnapshot(mdl_entity_snapshot)
    if not mdl_entity == None:
        context.ov_neuray.destroyMdlEntity(mdl_entity)


#--------------------------------------------------------------------------------------------------
# MDL Python Example
#--------------------------------------------------------------------------------------------------

# Reconstruct source asset from a struct symbol
# Examples:
#   return 'base.mdl' for symbol '::base::texture_return'
#   return is 'package/poly.mdl' for symbol '::package::poly::polygon'
# Notes:
#   No support for MDLE
def get_source_asset_from_struct_symbol(symbol : str):
    if not symbol is None:
        scope = symbol.rfind("::")
        assert(scope != -1) # this can happen for builtins
        symbol = symbol[2:scope] + '.mdl'
        symbol = symbol.replace("::","/")
    return symbol

# return usd_value, connection, usd_type
def get_usd_value_and_type(context, val : pymdl.ArgumentConstant):
    if not val:
        return (None, None, None)
    kind = val.type.kind

    usd_type = mdl_type_to_usd_type(val)
    if usd_type == None:
        return (None, None, None)

    usd_val = None
    connection = None
    # -------------------------------- Atomic ---------------------------------
    if  kind == pymdlsdk.IType.Kind.TK_BOOL or \
        kind == pymdlsdk.IType.Kind.TK_INT or \
        kind == pymdlsdk.IType.Kind.TK_FLOAT or \
        kind == pymdlsdk.IType.Kind.TK_DOUBLE or \
        kind == pymdlsdk.IType.Kind.TK_STRING:
        usd_val = val.value
    elif kind == pymdlsdk.IType.Kind.TK_ENUM:
        usd_val = val.value[1]
    # -------------------------------- Compound ---------------------------------
    elif kind == pymdlsdk.IType.Kind.TK_VECTOR:
        usd_val = python_vector_to_usd_value(val.value)
        if context.is_type_annotation_enabled():
            custom_data = custom_data_from_python_vector(val.value)
            context.current_custom_data().update(custom_data)
    elif kind == pymdlsdk.IType.Kind.TK_MATRIX:
        usd_val = python_matrix_to_usd_value(val.value)
    elif kind == pymdlsdk.IType.Kind.TK_COLOR:
        usd_val = Gf.Vec3f(val.value[0], val.value[1], val.value[2])
    elif kind == pymdlsdk.IType.Kind.TK_ARRAY:
        usd_val = python_array_to_usd_value(val.value)
        if context.is_type_annotation_enabled():
            custom_data = custom_data_from_python_array(val.value)
            context.current_custom_data().update(custom_data)
    elif kind == pymdlsdk.IType.Kind.TK_STRUCT:
        parm_name = context.current_parameter_name()
        shader = context.current_usd_shader()
        usd_mat = context.current_usd_shader()
        node_identifier = mdl_name_to_sub_identifier(val.type.symbol)
        new_shader = UsdShade.Shader.Define(context.stage,
            GetUniqueNameInStage.get(context.stage, usd_mat.GetPath().AppendChild(node_identifier + '_' + parm_name)))
        context.push_usd_shader(new_shader)
        new_shader.GetImplementationSourceAttr().Set("sourceAsset")
        new_shader.GetPrim().CreateAttribute("info:mdl:sourceAsset:subIdentifier",
            Sdf.ValueTypeNames.Token, False, Sdf.VariabilityUniform).Set(node_identifier)
        module : str = get_source_asset_from_struct_symbol(val.type.symbol)
        if not module is None:
            new_shader.SetSourceAsset(module, "mdl")
        # Reconstruct the struct constructor from the struct fields
        args = []
        for item in val.value:
            field_name = item
            context.push_parameter_name(field_name)
            context.push_custom_data(dict())
            v = val.value[item]
            handle_value(context, v)
            args.append(val.value[item].type.name)
            context.pop_custom_data()
            context.pop_parameter_name()
        signature = node_identifier + '('
        if len(args) > 0:
            signature = signature + args[0]
            args.remove(args[0])
            for a in args:
                signature = signature + ',' + a
        signature = signature + ')'
        new_shader.GetPrim().CreateAttribute("info:mdl:sourceAsset:subIdentifier",
            Sdf.ValueTypeNames.Token, False, Sdf.VariabilityUniform).Set(signature)
        connection = new_shader.CreateOutput('out', Sdf.ValueTypeNames.Token)
        context.pop_usd_shader()
    # -------------------------------- Resource ---------------------------------
    elif kind == pymdlsdk.IType.Kind.TK_TEXTURE:
        ftex = val.value[0]
        gamma = val.value[1]

        if not ftex is None:
            with context.transaction.access_as(pymdlsdk.ITexture, ftex) as text:
                if text.is_valid_interface():
                    with context.transaction.access_as(pymdlsdk.IImage, text.get_image()) as image:
                        if image.is_valid_interface():
                            usd_val = image.get_filename(0,0)

        if usd_val is None:
            # initialize the value to null in case there is no texture path currently defined
            usd_val = Sdf.AssetPath("")
            filepath = None
            if len(val.value) > 2 and not val.value[2] is None:
                filepath = os.path.normpath(val.value[2])
            if not filepath is None:
                stageFolder = None
                if not context.stage is None:
                    stageFolder = __get_stage_folder(context.stage)

                helper = UnmangleAndFixMDLSearchPath(context)
                (isMangled, usd_val) = helper.unmangle_uri(filepath, stageFolder)
    elif kind == pymdlsdk.IType.Kind.TK_LIGHT_PROFILE:
        lightprofile = val.value[0]
        if not lightprofile is None:
            with context.transaction.access_as(pymdlsdk.ILightprofile, lightprofile) as obj:
                if obj.is_valid_interface():
                    usd_val = obj.get_filename()

        if usd_val is None:
            filepath = None
            if len(val.value) > 1 and not val.value[1] is None:
                filepath = os.path.normpath(val.value[1])
            if not filepath is None:
                stageFolder = None
                if not context.stage is None:
                    stageFolder = __get_stage_folder(context.stage)

                helper = UnmangleAndFixMDLSearchPath(context)
                (isMangled, usd_val) = helper.unmangle_uri(filepath, stageFolder)
    elif kind == pymdlsdk.IType.Kind.TK_BSDF_MEASUREMENT:
        bsdfmeasurement = val.value[0]
        if not bsdfmeasurement is None:
            with context.transaction.access_as(pymdlsdk.IBsdf_measurement, bsdfmeasurement) as obj:
                if obj.is_valid_interface():
                    usd_val = obj.get_filename()

        if usd_val is None:
            filepath = None
            if len(val.value) > 1 and not val.value[1] is None:
                filepath = os.path.normpath(val.value[1])
            if not filepath is None:
                stageFolder = None
                if not context.stage is None:
                    stageFolder = __get_stage_folder(context.stage)

                helper = UnmangleAndFixMDLSearchPath(context)
                (isMangled, usd_val) = helper.unmangle_uri(filepath, stageFolder)
    else:
        carb.log_warn("Error: Unknown IValue Kind for parm/kind: {}/{}".format(context.current_parameter_name(), kind))

    return (usd_val, connection, usd_type)

def dict_of_dicts_merge(x, y):
    z = {}
    overlapping_keys = x.keys() & y.keys()
    for key in overlapping_keys:
        z[key] = dict_of_dicts_merge(x[key], y[key])
    for key in x.keys() - overlapping_keys:
        z[key] = deepcopy(x[key])
    for key in y.keys() - overlapping_keys:
        z[key] = deepcopy(y[key])
    return z

# Return a dictionary of pair [string, value]
#
def get_annotations_dict(context, val):
    main_dict = dict()
    # We do not want to collect type annotations during conversion of annotation expressions
    # Otherwise the type for the annotations is mized with the parameter annotations
    context.disable_type_annotation()
    try:
        # Handle annotations
        if val.annotations:
            anno_dict = dict()
            # print(f"  Annotations:")
            anno: pymdl.Annotation
            for anno in val.annotations:
                # print(f"  - Simple Name: {anno.simpleName}")
                # print(f"    Qualified Name: {anno.name}")
                # // Special case of annotations without expressions, e.g. ::anno::hidden()
                # // We create a boolean VtValue and set it to true
                # // Annotation:
                # //   ::anno::hidden()
                # // becomes:
                # //   bool "::anno::hidden()" = 1
                if len(anno.arguments.items()) == 0:
                    usd_value = True
                    usd_type = bool
                    anno_dict[anno.name] = usd_value
                arg: pymdl.val
                for arg_name, arg in anno.arguments.items():
                    # print(f"    ({arg.type.kind}) {arg_name}: {arg.value}")
                    (usd_value, connection, usd_type) = get_usd_value_and_type(context, arg)
                    # print(f"    ({usd_value}) {connection}: {usd_type}")
                    if usd_value != None and usd_type != None:
                        anno_dict[anno.name+"::"+arg_name] = usd_value
            if len(anno_dict) > 0:
                main_dict.update(dict({"mdl" : {"annotations": anno_dict}}))

        # Handle special values, concat (possibly empty) context dictionary
        main_dict = dict_of_dicts_merge(main_dict, context.current_custom_data())

    except Exception as e:
        carb.log_warn("Error while retrieving annotations")
    finally:
        context.enable_type_annotation()
        return main_dict

def add_annotations_to_stage(context, stage, anno_dict):
    try:
        if "::anno::display_name(string)::name" in anno_dict["mdl"]["annotations"]:
            stage.SetMetadata('comment', 'Conversion from MDL module: ' + anno_dict["mdl"]["annotations"]["::anno::display_name(string)::name"])
        else:
            if context.current_module() != None:
                stage.SetMetadata('comment', 'Conversion from MDL module: ' + context.current_module().mdlName)

        # TODO: Add more annotations to Stage as Metadata: version, ...
    except:
        pass

def add_annotations_to_node(node, anno_dict):
    # display name, group and description
    #
    # sdrMetadata = {
    #     dictionary ui = {
    #         string displayGroup = "float2_parm group"
    #     }
    # }
    #
    if "mdl" in anno_dict and "annotations" in anno_dict["mdl"]:
        for anno, key in ( \
            ("::anno::display_name(string)::name", "ui:displayName"), \
            ("::anno::in_group(string)::group", "ui:displayGroup"), \
            ("::anno::in_group(string,string)::group", "ui:displayGroup"), \
            ("::anno::in_group(string,string,string)::group", "ui:displayGroup"), \
            ("::anno::description(string)::description", "ui:description")):
            if anno in anno_dict["mdl"]["annotations"]:
                node.SetSdrMetadataByKey( key, anno_dict["mdl"]["annotations"][anno])
    #
    # See Also:
    #
    # ui = Usd.SceneGraphPrimAPI(minput.GetAttr())
    # a = ui.CreateDisplayNameAttr()
    #
    # TODO: Could also use?
    #
    # minput.GetAttr().SetDisplayName("FOOBAR")
    # minput.GetAttr().SetDisplayGroup("GROUP")
    try:
        if "::anno::display_name(string)::name" in anno_dict["mdl"]["annotations"]:
            node.GetAttr().SetDisplayName(anno_dict["mdl"]["annotations"]["::anno::display_name(string)::name"])
        for anno in ( \
            "::anno::in_group(string)::group", \
            "::anno::in_group(string,string)::group", \
            "::anno::in_group(string,string,string)::group" \
            ):
            if anno in anno_dict["mdl"]["annotations"]:
                node.GetAttr().SetDisplayGroup(anno_dict["mdl"]["annotations"][anno])
    except:
        pass

def add_annotations_to_prim(usd_prim, anno_dict):
    if len(anno_dict) > 0:
        cd = usd_prim.GetCustomData()
        cd.update(anno_dict)
        usd_prim.SetCustomData(cd)

    try:
        ui = UsdUI.UsdUIBackdrop(usd_prim)
        if "::anno::description(string)::description" in anno_dict["mdl"]["annotations"]:
            ui.CreateDescriptionAttr(anno_dict["mdl"]["annotations"]["::anno::description(string)::description"])
    except:
        pass

    try:
        ui = UsdUI.SceneGraphPrimAPI(usd_prim)
        if "::anno::display_name(string)::name" in anno_dict["mdl"]["annotations"]:
            ui.CreateDisplayNameAttr(anno_dict["mdl"]["annotations"]["::anno::display_name(string)::name"])
        for anno in ( \
            "::anno::in_group(string)::group", \
            "::anno::in_group(string,string)::group", \
            "::anno::in_group(string,string,string)::group" \
            ):
            if anno in anno_dict["mdl"]["annotations"]:
                ui.CreateDisplayGroupAttr(anno_dict["mdl"]["annotations"][anno])
    except:
        pass

    # Hidden
    if "mdl" in anno_dict and "annotations" in anno_dict["mdl"]:
        if "::anno::hidden()" in anno_dict["mdl"]["annotations"]:
            if anno_dict["mdl"]["annotations"]["::anno::hidden()"]:
                usd_prim.SetHidden(True)

def handle_value(context, val : pymdl.ArgumentConstant):
    if not val:
        return

    (usd_value, connection, usd_type) = get_usd_value_and_type(context, val)
    if (usd_value == None and connection == None) or usd_type == None:
        return

    parm_name = context.current_parameter_name()
    shader = context.current_usd_shader()
    # check if the param already exists (and dont set the value if so)
    minput = shader.GetInput(parm_name)
    if not minput:
        minput = shader.CreateInput(parm_name, usd_type)
        if usd_value != None:
            minput.Set(usd_value)
        else:
            minput.ConnectToSource(connection)

    anno_dict = get_annotations_dict(context, val)
    add_annotations_to_prim(minput.GetAttr(), anno_dict)
    add_annotations_to_node(minput, anno_dict)
    if val.type.kind == pymdlsdk.IType.Kind.TK_ENUM:
        minput.SetRenderType(val.type.symbol)

def handle_expression_constant(context, expression_constant : pymdl.ArgumentConstant):
    if not expression_constant:
        return
    handle_value(context, expression_constant)

def function_to_sub_identifier(context, fct:pymdl.FunctionDefinition):

    if not fct:
        return '[unknown]'

    module = pymdl.Module._fetchFromDb(context.transaction, fct.moduleDbName)
    if len(module.functions[fct.mdlSimpleName]) == 1:
        # Function has no overload
        return mdl_name_to_sub_identifier(fct.mdlName, False)
    else:
        return mdl_name_to_sub_identifier(fct.mdlName, True)

def sanity_check_function_call(context, function_call : pymdl.FunctionCall):
    if not function_call:
        return None

    fdef_db_name = function_call.functionDefinition
    function_def = pymdl.FunctionDefinition._fetchFromDb(context.transaction, fdef_db_name)
    if not function_def:
        carb.log_error(f"Can not access function definition for: '{fdef_db_name}'")
        return None

    # Determine if function definition is variant
    fctdef = context.transaction.access_as(pymdlsdk.IFunction_definition, function_def.dbName)
    if not fctdef.is_valid_interface():
        carb.log_error(f"Can not access function definition for: '{function_def.dbName}'")
        return None

    # Is this function a variant?
    prototype = fctdef.get_prototype()
    if prototype:
        # Substitute function definition with the variant function
        function_def = pymdl.FunctionDefinition._fetchFromDb(context.transaction, prototype)
        if not function_def:
            carb.log_error(f"Can not access function definition for: '{prototype}'")
            return None

    return function_def

def get_node_port_mode(context, function_def):
    anno_dict = get_annotations_dict(context, function_def.returnValue)
    mode_anno = '::anno::node_output_port_default(::anno::node_port_mode)::mode'
    if len(anno_dict.keys()) > 0 and mode_anno in anno_dict["mdl"]["annotations"]:
        value = anno_dict["mdl"]["annotations"][mode_anno]
        return value
    return _NodePortMode['no_node_port']

def output_exists_for_function(context, expression_call, portName):
    if not expression_call:
        return False
    transaction = context.transaction
    fcall : pymdl.FunctionCall
    fcall = pymdl.FunctionCall._fetchFromDb(transaction, expression_call.value)
    if fcall:
        function_def : pymdl.FunctionDefinition = sanity_check_function_call(context, fcall)
        if function_def:
            node_port_mode = get_node_port_mode(context, function_def)
            if node_port_mode == _NodePortMode['node_port_fields_only'] or \
                node_port_mode == _NodePortMode['node_port_value_and_fields']:

                fctdef = context.transaction.access_as(pymdlsdk.IFunction_definition, function_def.dbName)
                MDL_IType = fctdef.get_return_type().skip_all_type_aliases()
                MDL_Type = pymdl.Type(MDL_IType)
                if MDL_Type.kind == pymdlsdk.IType.Kind.TK_STRUCT:
                    MDL_StructType = MDL_IType.get_interface(pymdlsdk.IType_structure)
                    if MDL_StructType.is_valid_interface():
                        for field in range(MDL_StructType.get_size()):
                            name = MDL_StructType.get_field_name(field)
                            if name == portName:
                                return True
    return False

def handle_function_call(context, function_call : pymdl.FunctionCall):
    function_def : pymdl.FunctionDefinition = sanity_check_function_call(context, function_call)
    if not function_def:
        return
    fctdef = context.transaction.access_as(pymdlsdk.IFunction_definition, function_def.dbName)
    if fctdef.get_semantic() == fctdef.Semantics.DS_INTRINSIC_DAG_FIELD_ACCESS:
        portName = function_def.mdlSimpleName.split('.')[-1]
        if len(function_call.parameters.items()) == 1:
            for name, argument in function_call.parameters.items():
                if isinstance(argument, pymdl.ArgumentCall):
                    # Find out if the child shader has the required portName
                    argument_call : pymdl.ArgumentCall
                    argument_call = argument
                    if output_exists_for_function(context, argument_call, portName):
                        (child_shader, outPort) = handle_expression_call(context, argument_call)
                        outPort = child_shader.GetOutput(portName)
                        return (child_shader, outPort)

    sourceAsset = module_mdl_name_to_source_asset(context, function_def.mdlModuleName)
    node_identifier = function_to_sub_identifier(context, function_def)
    shader = context.current_usd_shader()
    shader.GetImplementationSourceAttr().Set("sourceAsset")
    shader.SetSourceAsset(Sdf.AssetPath(sourceAsset), "mdl")
    shader.GetPrim().CreateAttribute("info:mdl:sourceAsset:subIdentifier", Sdf.ValueTypeNames.Token, False, Sdf.VariabilityUniform).Set(node_identifier)

    # Inspect the return type and create corresponding output ports
    return_type = Sdf.ValueTypeNames.Token
    MDL_IType = fctdef.get_return_type().skip_all_type_aliases()
    MDL_Type: pymdl.Type = pymdl.Type(MDL_IType)
    USDType = MdlITypeToUSD(MDL_Type)
    # USDType = MdlITypeToUSD(function_call.returnType)
    if not USDType is None:
        return_type = USDType
    else:
        carb.log_warn(f"Warning: Can not map MDL type {function_call.returnType.kind} to USD")

    # Do not create output if not requested
    MDL_StructType = MDL_IType.get_interface(pymdlsdk.IType_structure)
    node_port_mode = get_node_port_mode(context, function_def)
    if node_port_mode != _NodePortMode['node_port_fields_only']:
        shader.CreateOutput('out', return_type)
        if MDL_StructType.is_valid_interface():
            outPort = shader.GetOutput('out')
            outPort.SetRenderType(MDL_Type.name.split('::')[-1])  # having only simple names could be an issue

    if MDL_Type.kind == pymdlsdk.IType.Kind.TK_STRUCT:
        if node_port_mode == _NodePortMode['node_port_fields_only'] or \
            node_port_mode == _NodePortMode['node_port_value_and_fields']:
            if MDL_StructType.is_valid_interface():
                for field in range(MDL_StructType.get_size()):
                    name = MDL_StructType.get_field_name(field)
                    type = MDL_StructType.get_field_type(field)
                    MDL_FieldType: pymdl.Type = pymdl.Type(type)
                    USD_FieldType = MdlITypeToUSD(MDL_FieldType)
                    if not USD_FieldType is None:
                        shader.CreateOutput(name, USD_FieldType)
                        outPort = shader.GetOutput(name)
                        outPort.SetRenderType(MDL_FieldType.name)
                    else:
                        carb.log_warn(f"Warning: Can not map MDL type {MDL_FieldType.kind} to USD")

    for name, argument in function_call.parameters.items():

        context.push_parameter_name(name)
        context.push_custom_data(dict())

        handle_expression(context, argument)

        context.pop_custom_data()
        context.pop_parameter_name()

    outPort = shader.GetOutput('out')
    return (shader, outPort)

def handle_material_instance(context, minst):
    if not minst.is_valid_interface():
        return
    pass

def handle_expression_call(context, expression_call : pymdl.ArgumentCall):
    if not expression_call:
        return
    neuray = context.neuray
    transaction = context.transaction

    # NEW
    fcall : pymdl.FunctionCall
    fcall = pymdl.FunctionCall._fetchFromDb(transaction, expression_call.value)
    if fcall:
        return handle_function_call(context, fcall)
    # TODO?
    # minst = transaction.access_as(pymdlsdk.IFunction_call, expression_call.get_call())
    # if minst.is_valid_interface():
    #     handle_material_instance(context, minst)

def handle_expression_parameter(context, expression_parameter):
    if not expression_parameter.is_valid_interface():
        return
    pass

def handle_expression_direct_call(context, expression_direct_call):
    if not expression_direct_call.is_valid_interface():
        return
    pass

def handle_expression_temporary(context, expression_temporary):
    if not expression_temporary.is_valid_interface():
        return
    pass

def handle_expression(context, argument : pymdl.Argument):
    if not argument:
        return

    if isinstance(argument, pymdl.ArgumentConstant):
        # A constant expression. See #mi::neuraylib::IExpression_constant.
        # argument_cst = pymdl.ArgumentConstant(argument) # FAILS
        argument_cst : pymdl.ArgumentConstant
        argument_cst = argument
        handle_expression_constant(context, argument_cst)
    elif isinstance(argument, pymdl.ArgumentCall):
        # Need to:
        # - create a parameter of the given type
        # - create a new shader in the current material
        # - Connect the parameter to the new shader
        # - Evaluate the expression
        expression_kind = argument.type.kind
        # If the exact return type can not be determined (e.g. vectors, where to get the size?) set the parm type to Token by default
        parm_type = Sdf.ValueTypeNames.Token
        parm_name = context.current_parameter_name()
        USDType = MdlITypeToUSD(argument.type)
        if not USDType is None:
            parm_type = USDType
        else:
            carb.log_warn("Warning: Indirect call expression parm/kind : {}/{}".format(parm_name,argument.type.kind))

        # - create a parameter of the given type
        usd_shader = context.current_usd_shader()
        minput = usd_shader.CreateInput(parm_name, parm_type)
        # By default shaders are not nested, they are created immediately under the material
        usd_mat = context.current_usd_material()
        if context.mdl_to_usd_output_material_nested_shaders == True:
            # Nested shaders case, create under current shader
            usd_mat = context.current_usd_shader()
        # - create a new shader in thecurrent material (or current shader in the nested case)
        shName = GetUniqueNameInStage.get(context.stage, usd_mat.GetPath().AppendChild(parm_name))
        shader = UsdShade.Shader.Define(context.stage, shName)

        context.push_usd_shader(shader)

        # - Evaluate the expression
        argument_call : pymdl.ArgumentCall
        argument_call = argument
        (child_shader, outPort) = handle_expression_call(context, argument_call)

        # Annotations
        anno_dict = get_annotations_dict(context, argument_call)
        add_annotations_to_prim(minput.GetAttr(), anno_dict)
        add_annotations_to_node(minput, anno_dict)
        add_annotations_to_prim(shader.GetPrim(), anno_dict)
        add_annotations_to_node(shader, anno_dict)

        minput.ConnectToSource(outPort)

        context.pop_usd_shader()

        return

    # TODO
    # elif kind == pymdlsdk.IExpression.Kind.EK_PARAMETER:
    #     # A parameter reference expression. See #mi::neuraylib::IExpression_parameter.
    #     # handle_expression_parameter(context, expression.get_interface(pymdlsdk.IExpression_parameter))
    #     pass
    # elif kind == pymdlsdk.IExpression.Kind.EK_DIRECT_CALL:
    #     # A direct call expression. See #mi::neuraylib::IExpression_direct_call.
    #     # handle_expression_direct_call(context, expression.get_interface(pymdlsdk.IExpression_direct_call))
    #     pass
    # elif kind == pymdlsdk.IExpression.Kind.EK_TEMPORARY:
    #     # A temporary reference expression. See #mi::neuraylib::IExpression_temporary.
    #     # handle_expression_temporary(context, expression.get_interface(pymdlsdk.IExpression_temporary))
    #     pass

def definition_to_stage(context, function: pymdl.FunctionDefinition):
    neuray = context.neuray
    transaction = context.transaction

    argument: pymdl.Argument
    for name, argument in function.parameters.items():
        # print(f"* Name: {name}")
        # print(f"  Type: {argument.type.kind}")
        # if argument.type.symbol:
        #     print(f"  Type Symbol: {argument.type.symbol}")
        # print(f"  Value: {argument.value}")
        # print(f"  Value is Constant: {isinstance(argument, pymdl.ArgumentConstant)}")
        # print(f"  Value is Attachment: {isinstance(argument, pymdl.ArgumentCall)}")

        context.push_parameter_name(name)
        context.push_custom_data(dict())

        handle_expression(context, argument)

        context.pop_custom_data()
        context.pop_parameter_name()

def get_db_module_name(neuray, module_mdl_name):
    """Return the db name of the given module."""

    module_db_name = None
    # When the module is loaded we can access it and all its definitions by accessing the DB
    # for that we need to get a the database name of the module using the factory
    with neuray.get_api_component(pymdlsdk.IMdl_factory) as factory:
        with factory.get_db_module_name(module_mdl_name) as istring:
            if istring.is_valid_interface():
                module_db_name = istring.get_c_str() # note, even though this name simple and could
                                                     # be constructed by string operations, use the
                                                     # factory to be save in case of unicode encodings
                                                     # and potential upcoming changes in the future

        # # shortcut for the function above
        # # this chaining is a bit special. In the C++ interface it's not possible without
        # # leaking memory. Here we create the smart pointer automatically. However, the IString
        # # which is created temporay here is released at the end the `load_module` function, right?
        # # This might be unexpected, especially when we rely on the RAII pattern and that
        # # objects are disposed at certain points in time (usually before committing a transaction)
        # module_db_name_2 = factory.get_db_module_name(module_mdl_name).get_c_str()
        # # note, we plan to map compatible types to python. E.g. the IString class may disappear
        # return module_db_name_2
    return module_db_name

#--------------------------------------------------------------------------------------------------

def get_db_definition_name(neuray, function_mdl_name):
    """Return the db name of the given function definition."""

    with neuray.get_api_component(pymdlsdk.IMdl_factory) as factory:
        with factory.get_db_definition_name(function_mdl_name) as istring:
            if istring.is_valid_interface():
                return istring.get_c_str()
    return None

#--------------------------------------------------------------------------------------------------
def edit_instance(transaction, inst_name):
    return transaction.edit_as(pymdlsdk.IFunction_call, inst_name)

#--------------------------------------------------------------------------------------------------
def dump_material_instance(context, inst_name):
    transaction = context.transaction
    inst = edit_instance(transaction, inst_name)
    if not inst.is_valid_interface():
        return
    carb.log_info("============ MDL Dump =============")
    carb.log_info(inst_name)
    carb.log_info("")
    neuray = context.neuray
    factory = neuray.get_api_component(pymdlsdk.IMdl_factory)
    expression_factory = factory.create_expression_factory(transaction)
    count = inst.get_parameter_count()
    arguments = inst.get_arguments()
    for index in range(count):
        argument = arguments.get_expression(index)
        name = inst.get_parameter_name(index)
        argument_text = expression_factory.dump(argument, name, 1)
        carb.log_info(argument_text.get_c_str())
    carb.log_info("============ MDL Dump =============")

#--------------------------------------------------------------------------------------------------
# Return a shader prim corresponding to the input prim_path.
# If prim_path is a shader, return the corresponding prim.
# If prim_path is a material, return the first shader found in the list of children.
def get_shader_prim(stage, prim_path):
    prim = stage.GetPrimAtPath(Sdf.Path(prim_path))
    if UsdShade.Shader(prim):
        return prim
    if UsdShade.Material(prim):
        mat = UsdShade.Material(prim)
        if mat.GetOutput("mdl:surface") and mat.GetOutput("mdl:surface").HasConnectedSource():
            (src, name, t) = mat.GetOutput("mdl:surface").GetConnectedSource()
            if UsdShade.Shader(src):
                return src.GetPrim()
        for prim in prim.GetChildren():
            if UsdShade.Shader(prim):
                return prim
    if UsdShade.NodeGraph(prim):
        ng = UsdShade.NodeGraph(prim)
        if ng.GetOutput("out") and ng.GetOutput("out").HasConnectedSource():
            (src, name, t) = ng.GetOutput("out").GetConnectedSource()
            if UsdShade.Shader(src):
                return src.GetPrim()
        for prim in prim.GetChildren():
            if UsdShade.Shader(prim):
                return prim
    return None

#--------------------------------------------------------------------------------------------------
async def convert_usd_to_mdl(context, prim_path, output_filename):
    inst_name = None
    mdl_entity = None
    mdl_entity_snapshot = None
    if not context.ov_neuray == None:
        # We are in OV

        # Get the shader prim from Material
        shader_prim_path = get_shader_prim(context.stage, prim_path)

        if shader_prim_path == None:
            carb.log_error(f"Error: can not access prim: '{prim_path}'")
            return None

        mdl_entity = context.ov_neuray.createMdlEntity(shader_prim_path.GetPath().pathString, context.ov_neuray.getCurrentDefaultScope())

        if mdl_entity == None:
            carb.log_error(f"Failed to create entity for shader: '{shader_prim_path}'")

        if not mdl_entity.valid():
            carb.log_error(f"Invalid entity for shader: '{shader_prim_path}'")

        mdl_entity_snapshot = None
        if not mdl_entity.getMdlModule() == None:
            mdl_entity_snapshot = context.ov_neuray.createMdlEntitySnapshot(mdl_entity)
            inst_name = mdl_entity_snapshot.dbName
        else:
            carb.log_error(f"Error: can not access entity: '{prim_path}'")

    if  inst_name is not None:
        dump_material_instance(context, inst_name)
        if output_filename:
            # we use a temporary folder for resources from the server
            with tempfile.TemporaryDirectory() as temp_dir:
                success  = await save_instance_to_module(context, inst_name, prim_path, temp_dir, output_filename)
                if not success:
                    inst_name = None

    if not context.ov_neuray == None:
        # We are in OV
        if not mdl_entity_snapshot == None:
            context.ov_neuray.destroyMdlEntitySnapshot(mdl_entity_snapshot)
        if not mdl_entity == None:
            context.ov_neuray.destroyMdlEntity(mdl_entity)

    return inst_name

#--------------------------------------------------------------------------------------------------
# Split the input string or list of strings using given the split char
# Return a list of strings
def split_list(list_of_strings, split_char):
    res = []
    if type(list_of_strings) == list:
        for s in list_of_strings:
            res += s.split(split_char)
    else:
        res = list_of_strings.split(split_char)
    return res

#--------------------------------------------------------------------------------------------------
# Remove all occurences of element from the list
def remove_all_occurences_of_element_from_list(element, alist):
    try:
        while True:
            alist.remove(element)
    except:
        pass
    finally:
        return alist

#--------------------------------------------------------------------------------------------------
# Split the input string or list of strings using all the input split chars
def multi_split_list(list_of_strings, list_of_splits):
    res = list_of_strings
    for split in list_of_splits:
        res = split_list(res, split)
    return res

#--------------------------------------------------------------------------------------------------
# Identify a line containing an MD import declaration
# From the MDL 1.7 specs:
# import : import qualified_import {, qualified_import} ;
#        | [export] using import_path
#           import ( * | simple_name {, simple_name} ) ;
def is_import_line(token_list):
    if 'import' in token_list:
        if token_list[0] == 'import' or token_list[0] == 'export' or token_list[0] == 'using':
            return True
    return False

#--------------------------------------------------------------------------------------------------
# Construct a set or strings found in an MDL module
# Split the input strings using several separators (' ',';','(', ')')
# if filter_import_lines is set to True, then only process lines beginning with 'import'
def find_tokens(lines, filter_import_lines = False):
    all_ids = set()
    input_list = lines
    if not type(lines) == list:
        input_list = [lines]
    for l in input_list:
        ids = multi_split_list(l, [' ',';','(', ')'])
        remove_all_occurences_of_element_from_list('', ids)
        if filter_import_lines:
            if not is_import_line(ids):
                continue
        for id in ids:
            if not id.find('::') == -1:
                tokens = id.split('::')
                for t in tokens:
                    if len(t) > 0:
                        all_ids.add(t)
    return all_ids

#--------------------------------------------------------------------------------------------------
# Find MDL identifier in this line of text if text is an import statement
def find_import(line):
    ids = multi_split_list(line, [' ',';','(', ')'])
    remove_all_occurences_of_element_from_list('', ids)
    if is_import_line(ids):
        for id in ids:
            if not id.find('::') == -1:
                return id
    return ''

#--------------------------------------------------------------------------------------------------
# Find MDL identifier in this line of text
def find_identifiers(line):
    rtn_identifiers = set()
    ids = multi_split_list(line, [' ', ';', '(', ')', ',', '\n'])
    remove_all_occurences_of_element_from_list('', ids)
    for id in ids:
        if not id.find('::') == -1:
            rtn_identifiers.add(id)
    return rtn_identifiers

#--------------------------------------------------------------------------------------------------
# Checks if a given identifier is mangled based on the existance of an encoded uri scheme
# assuming that mangled names are always valid URIs that have a scheme
# unmangling regular MDL paths will basically replace only "::" by "/"
# unmangling encoded paths will result in a URIs with a scheme in front!
def is_identifier_mangled(identifier: str, context: ConverterContext) -> bool:
    unmangled_identifier: str = context.ov_neuray._unmangleUri(identifier, "::")
    url_parts = omni.client.break_url(unmangled_identifier)
    return url_parts.scheme != None and url_parts.scheme != ""

#--------------------------------------------------------------------------------------------------
# Appends a URI scheme if not present.
# Note, use only if the input path is known to be absolute!
def make_uri_with_scheme(absolute_path_or_uri: str):
    """creates a URI from a given absolute path or normalizes a given URI"""
    url_parts = omni.client.break_url(absolute_path_or_uri)
    uri = omni.client.make_url(
        scheme=(url_parts.scheme if url_parts.scheme else 'file'),
        user=url_parts.user,
        port=url_parts.port,
        host=url_parts.host,
        path=url_parts.path,
        query=url_parts.query,
        fragment=url_parts.fragment,
    )
    return omni.client.normalize_url(uri)


#--------------------------------------------------------------------------------------------------
# Substitute source strings with target strings found in the input table in the input lines
# Input lines is a string or list of strings
def replace_tokens(lines, table):
    if type(lines) == list:
        for i in range(len(lines)):
            for k in table.keys():
                lines[i] = lines[i].replace(k, table[k])
        return lines
    else:
        for k in table.keys():
            lines = lines.replace(k, table[k])
    return lines

#--------------------------------------------------------------------------------------------------
# Helper to perfom unmangling on MDL module files and MDL identifiers
# Un-mangling is only done in the framework of OV if an un-mangling routine exists
class Unmangle:
    _unmangle_routine = None
    unmangle_uri_routine = None
    def __init__(self, context):
        if context.ov_neuray != None:
            if "_unmangleMdlModulePath" in dir(context.ov_neuray):
                self._unmangle_routine = context.ov_neuray._unmangleMdlModulePath
            if "_unmangleUri" in dir(context.ov_neuray):
                self.unmangle_uri_routine = context.ov_neuray._unmangleUri

    # Un-mangle a single token
    # token should not contain any '::'
    def _unmangle_token(self, token):
        assert(token.find("::") == -1)

        # Un-mangle the input token
        # Add prefix otherwise unmangling has not effect
        unmangled_token = self._unmangle_routine("::" + token)

        # Remove any '.mdl' extension from unmangled token
        if len(unmangled_token) > 4 and unmangled_token[-4:] == '.mdl':
            unmangled_token = unmangled_token[:-4]

        unmangled = (unmangled_token != token)

        return (unmangled, unmangled_token)

    # Build an un-mangling mapping table from the input list of tokens
    def build_mapping_table(self, token_list):
        table = dict()
        for token in token_list:
            (unmangled_flag, unmangled_token) = self._unmangle_token(token)
            if unmangled_flag:
                table[token] = unmangled_token
        return table

    # Un-mangled an MDL identifier
    # Return a tuple (True if unmagling was done, unmangled value)
    def unmangle_mdl_identifier(self, source):
        if self._unmangle_routine == None:
            return (False, source)
        token_list = find_tokens(source)
        table = self.build_mapping_table(token_list)
        unmangled_str = replace_tokens(source, table)
        return (unmangled_str != source, unmangled_str)

#--------------------------------------------------------------------------------------------------
def generate_export_header():
    ext_id: str = omni.kit.app.get_app().get_extension_manager().get_extension_id_by_module(__name__)
    ext_id_dash_pos: int = ext_id.rfind('-')
    version_parts: list[str] = ext_id[ext_id_dash_pos+1:].split('.')
    return [
        f"// exported by: omni.mdl.usd_converter [{version_parts[0]}.{version_parts[1]}.{version_parts[2]}]\n",
        f"// --/exts/omni.mdl.usd_converter/allowRelativeExports={carb.settings.get_settings().get('exts/omni.mdl.usd_converter/allowRelativeExports')}\n",
        f"// --/exts/omni.mdl.usd_converter/allowRelativeExportUpwardLevels={carb.settings.get_settings().get('exts/omni.mdl.usd_converter/allowRelativeExportUpwardLevels')}\n",
        f"\n"
    ]

#--------------------------------------------------------------------------------------------------
# This unmangling class uses MDL search path to trim down MDL identifiers
# It uses also MDL aliases to perform substitutions in the MDL identifier
class UnmangleAndFixMDLSearchPath(Unmangle):
    def __init__(self, context):
        # Build MDL search path list
        self.mdl_search_paths = list()
        with context.neuray.get_api_component(pymdlsdk.IMdl_configuration) as cfg:
            if cfg.is_valid_interface():
                for i in range(cfg.get_mdl_paths_length()):
                    sp = cfg.get_mdl_path(i)
                    sp = omni.client.normalize_url(sp.get_c_str())
                    self.mdl_search_paths.append(sp)

        super().__init__(context)

    # Determine if this identifier is mangled
    def __is_mangled_identifier(self, id):
        token_list = id.split("::")
        remove_all_occurences_of_element_from_list('', token_list)
        for token in token_list:
            (unmangled_flag, unmangled_token) = self._unmangle_token(token)
            if unmangled_flag:
                return unmangled_flag
        return False

    # Remove path
    def __try_to_remove_path(self, input_path:str, test_path:str):
        pi: omni.client.Url = omni.client.break_url(input_path)
        pt:  omni.client.Url = omni.client.break_url(test_path)
        pis = pi.scheme
        pts = pt.scheme
        pip = omni.client.normalize_url(pi.path)
        ptp = omni.client.normalize_url(pt.path)
        if not pis and not pts:
            # No scheme, continue
            pass
        else:
            if not pis and pts:
                # one scheme is mssing, what to do?
                # return (False, input_path)
                pass
            elif pis and not pts:
                # one scheme is mssing, what to do?
                # return (False, input_path)
                pass
            elif not (pis == pts):
                # different schemes, path can not be compared
                return (False, input_path)

        # Get rid off all single quotes in the incoming filename
        pip = re.sub("'", '', pip)
        # Remove the test path only when the path is found at the head of id
        if pip.startswith(ptp):
            pip = pip[len(ptp):]
            return(True, pip)
        return (False, input_path)

    # Build mapping table for a given mangled identifier
    # Using the stored MDL search paths and the MDL aliases
    def __build_table_from_mangled_id(self, id, aliases, makeRelativeIfFailure: bool = False, relativeFolder : str = None):
        key = ''
        value = ''
        # unmangle using _unmangleMdlModulePath
        startsWithDoublecolumn = id.startswith('::')
        if not startsWithDoublecolumn:
            unmangled_id = self._unmangle_routine("::" + id)
        else:
            unmangled_id = self._unmangle_routine(id)

        # Replace aliases
        for alias in aliases.keys():
            unmangled_id = unmangled_id.replace(aliases[alias], alias)

        # Remove MDL seach path
        search_path_removed = False
        mapping_table = dict()
        for sp in self.mdl_search_paths:
            (search_path_removed, unmangled_id) = self.__try_to_remove_path(unmangled_id, sp)
            if search_path_removed:
                break
        # Conversion is done only if we did find search path prefix in the identifier
        if search_path_removed:
            replaced = unmangled_id
            replaced = replaced.replace('/', '::')
            replaced = replaced.replace('.mdl::', '::')
            replaced = re.sub('.mdl$', '', replaced) # Replace '.mdl' suffix
            if not replaced.startswith('::') and startsWithDoublecolumn:
                # Add '::' in front if they are missing
                replaced = '::' + replaced
            what_to_replace = id
            mapping_table[what_to_replace] = replaced
            return (True, mapping_table)
        else:
            if makeRelativeIfFailure:
                # Turn absolute path to relative
                path_removed = False
                if not relativeFolder is None:
                    # if not relativeFolder.startswith(os.sep):
                    #     relativeFolder = os.sep + relativeFolder
                    # file_prefix = 'file:'
                    # if not relativeFolder.startswith(file_prefix):
                    #     relativeFolder = file_prefix + relativeFolder
                    (path_removed, unmangled_id) = self.__try_to_remove_path(unmangled_id, relativeFolder)
                if path_removed:
                    # If path was removed, the id is relative, add '.' in front
                    if unmangled_id.startswith('/'):
                        unmangled_id = '.' + unmangled_id
                else:
                    # unmangled_id = os.path.basename(unmangled_id)
                    pass
                replaced = unmangled_id
                replaced = replaced.replace('/', '::')
                replaced = replaced.replace('.mdl::', '::')
                replaced = re.sub('.mdl$', '', replaced) # Replace '.mdl' suffix
                if not startsWithDoublecolumn:
                    # Remove heading '::' or '.::'
                    replaced = removeHeadings(replaced, '.::')
                    replaced = removeHeadings(replaced, '::')
                what_to_replace = id
                mapping_table[what_to_replace] = replaced
                return (True, mapping_table)
        return (False, mapping_table)


    # Un-mangle an MDL file and create a new un-mangled output file
    # Return (is identifier mangled, demangling and removing search path succeeded, un-mangled module name)
    def unmangle_mdl_module(self, module, relativeFolder : str = None):
        if self._unmangle_routine == None:
            return (False, True, module)

        rtn = module
        isMangled = self.__is_mangled_identifier(module)
        makeRelativeIfFailure = True
        (success, mapping_table) = self.__build_table_from_mangled_id(
            module,
            dict(),
            makeRelativeIfFailure,
            relativeFolder)
        if success:
            rtn = mapping_table[module]
            if rtn.find('::') == 0:
                rtn = rtn[2:]
            rtn = rtn.replace("::", "/")
        return (isMangled, success, rtn)

    def unmangle_uri(self, uri, relativeFolder : str = None):
        if self.unmangle_uri_routine == None:
            return (False, True, uri)

        rtn = self.unmangle_uri_routine(uri, os.sep)
        removed = False
        if not relativeFolder is None:
            # if not relativeFolder.startswith(os.sep):
            #     relativeFolder = os.sep + relativeFolder
            # file_prefix = 'file:'
            # if not relativeFolder.startswith(file_prefix):
            #     relativeFolder = file_prefix + relativeFolder
            (removed, rtn) = self.__try_to_remove_path(rtn, relativeFolder)
            if removed:
                # If path was removed, the id is relative, add '.' in front
                if rtn.startswith('/'):
                    rtn = '.' + rtn
        return (removed, rtn)

#--------------------------------------------------------------------------------------------------

_mdl_reserved_words: list[str] = [
    'annotation', 'auto', 'bool', 'bool2', 'bool3', 'bool4', 'break', 'bsdf', 'bsdf_measurement',
    'case', 'cast', 'color', 'const', 'continue', 'default', 'do', 'double', 'double2', 'double2x2',
    'double2x3', 'double3', 'double3x2', 'double3x3', 'double3x4', 'double4', 'double4x3', 'double4x4',
    'double4x2', 'double2x4', 'edf', 'else', 'enum', 'export', 'false', 'float', 'float2', 'float2x2',
    'float2x3', 'float3', 'float3x2', 'float3x3', 'float3x4', 'float4', 'float4x3', 'float4x4',
    'float4x2', 'float2x4', 'for', 'hair_bsdf', 'if', 'import', 'in', 'int', 'int2', 'int3', 'int4',
    'intensity_mode', 'intensity_power', 'intensity_radiant_exitance', 'let', 'light_profile', 'material',
    'material_emission', 'material_geometry', 'material_surface', 'material_volume', 'mdl', 'module',
    'package', 'return', 'string', 'struct', 'switch', 'texture_2d', 'texture_3d', 'texture_cube',
    'texture_ptex', 'true', 'typedef', 'uniform', 'using', 'varying', 'vdf', 'while', 'catch', 'char',
    'class', 'const_cast', 'delete', 'dynamic_cast', 'explicit', 'extern', 'external', 'foreach',
    'friend', 'goto', 'graph', 'half', 'half2', 'half2x2', 'half2x3', 'half3', 'half3x2', 'half3x3',
    'half3x4', 'half4', 'half4x3', 'half4x4', 'half4x2', 'half2x4', 'inline', 'inout', 'lambda',
    'long', 'mutable', 'namespace', 'native', 'new', 'operator', 'out', 'phenomenon', 'private',
    'protected', 'public', 'reinterpret_cast', 'sampler', 'shader', 'short', 'signed', 'sizeof',
    'static', 'static_cast', 'technique', 'template', 'this', 'throw', 'try', 'typeid', 'typename',
    'union', 'unsigned', 'virtual', 'void', 'volatile', 'wchar_t'
    ]

def is_reserved_word(name : str):
    # there will be an API function for this soon
    return name in _mdl_reserved_words

#--------------------------------------------------------------------------------------------------

# the db name of a texture is constructed here:
# rendering\include\rtx\neuraylib\NeurayLibUtils.h
# computeSceneIdentifierTexture
def parse_ov_resource_name(texture_db_name : str):
    # drop the db prefix
    texture_db_name = texture_db_name[5:]
    undescore = texture_db_name.rfind('_')
    texture_db_name = texture_db_name[:undescore]
    undescore = texture_db_name.rfind('_')
    return texture_db_name[:undescore]

async def prepare_resources_for_export(context: ConverterContext, inst_name: str, temp_dir: str):

    functionCall = pymdl.FunctionCall._fetchFromDb(context.transaction, inst_name)
    for name, param in functionCall.parameters.items():
        if param.type.kind == pymdlsdk.IType.Kind.TK_TEXTURE:
            if param.value[2]:
                # we do have a resolved file name but no matching IValue
                # this is due to the resource handling in RTX
                resource_uri: str = context.ov_neuray._unmangleUri(param.value[2], "/")
                resource_uri = resource_uri.replace("<", "%3C")  # encode special characters
                resource_uri = resource_uri.replace(">", "%3E")
                url_parts = omni.client.break_url(resource_uri)
                if url_parts.scheme == None or url_parts.scheme == "":
                    carb.log_warn(f"Refererenced texture path is not a URI: {resource_uri}")
            elif param.value[0]:
                resource_uri: str = parse_ov_resource_name(param.value[0])
            else:
                continue

            rtxNeurayLib = omni.mdl.neuraylib.get_neuraylib()
            texture_list = rtxNeurayLib.ResolveTiledResourceUri(resource_uri)

            # create a subfolder using the full URI hash to identify existing resources
            # note, in case of tiled resources, all resources will end up in that folder without changing the actual file names
            resource_uri_hash: str = str(hash(resource_uri))
            dst_dir: str = os.path.join(temp_dir, resource_uri_hash)

            # the image name to set in neuray is based on the file mask
            new_image_uri: str = pathlib.Path(os.path.join(dst_dir, os.path.basename(resource_uri))).as_posix()

            # if a resource is used on mutiple parameters we reuse the same resource without copying multiple times
            # since the dst_dir contains the hash only need to check for existance
            if not os.path.exists(dst_dir):
                os.mkdir(dst_dir)
                resource_num: int = 0
                for tp in texture_list:
                    tp: str = tp
                    try:
                        if "%5B" in tp:
                            # decode because the uri is percent encoded
                            from urllib.parse import unquote
                            tp = unquote(tp)

                        if Ar.IsPackageRelativePath(tp):
                            tp = str(Ar.GetResolver().Resolve(tp))

                            # Use Inner here to split package from content
                            inner_split = Ar.SplitPackageRelativePathInner(tp)
                            _, extension = os.path.splitext(inner_split[1])
                            dst_path = os.path.join(dst_dir, f"{resource_num}_{name}{extension}")

                            # we need to compute a uri but we don't have infos about the tile set from packages
                            new_image_uri: str = pathlib.Path(dst_path).as_posix()
                            if len(texture_list) > 1:
                                carb.log_verbose(f"No support for exporting tiled resource from packages: {inner_split[0]}")

                            carb.log_verbose(f"Copy resource from {tp} to {dst_path}.")
                            omni.kit.commands.execute("SerializeAsset", asset_path=tp, serialized_path=dst_path)
                        else:
                            basename: str = os.path.basename(tp)
                            dst_path: str = os.path.join(dst_dir, basename)  # name of the resource (tile) on disk
                            carb.log_verbose(f"Copy resource from {tp} to {dst_path}.")
                            result = await copy_async(tp, dst_path)
                            if not result:
                                carb.log_error(f"Cannot copy from {tp} to {dst_path}, error code: {result}.")
                                continue
                    except Exception as e:
                        carb.log_warn(f"Exception while copying resource from {tp} to {dst_path}.\n{e}")
                        continue
                    carb.log_verbose(f"Downloaded resource from {tp} to {dst_path}. Will be deleted after export.")

            # create a new image
            new_image_db_name: str = "mdlexp::" + new_image_uri
            with context.transaction.create("Image", 0, None) as new_interface:
                with new_interface.get_interface(pymdlsdk.IImage) as new_image:
                    # because this API is not URI aware we need to decode the markers
                    new_image.reset_file(new_image_uri.replace("%3C", "<").replace("%3E", ">"))
                    ret: int = context.transaction.store(new_image, new_image_db_name)
                    if ret != 0:
                        carb.log_error(f"Failed to store new image to DB\n\ttemp uri: {new_image_uri}\n\tdb name: {new_image_db_name}")
                    context.transaction.remove(new_image_db_name)  # drop after transaction is closed

            # assign the image to the texture
            if param.value[0] != None:
                # todo make sure the transaction is aborted, we don't want this change visible to other components
                with context.transaction.edit_as(pymdlsdk.ITexture, param.value[0]) as itexture:
                    itexture.set_image(new_image_db_name)
                    itexture.set_gamma(param.value[1])  # TODO check if srgb and linear work with floating precission here
            # create the ITexture and it's IValue_texture
            else:
                call: pymdlsdk.IFunction_call = None
                with context.transaction.edit_as(pymdlsdk.IFunction_call, inst_name) as call:
                    # create an ITexture that references the new image
                    new_texture_db_name: str = "mdlexp::" + resource_uri + "_texture"
                    with context.transaction.create("Texture") as new_interface:
                        new_texture: pymdlsdk.ITexture = None
                        with new_interface.get_interface(pymdlsdk.ITexture) as new_texture:
                            new_texture.set_image(new_image_db_name)
                            new_texture.set_gamma(param.value[1])  # TODO check if srgb and linear work with floating precission here
                            ret: int = context.transaction.store(new_texture, new_texture_db_name)
                            if ret != 0:
                                carb.log_error(f"Failed to store new texture to DB\n\tdb name: {new_texture_db_name}")
                            context.transaction.remove(new_texture_db_name)  # drop after transaction is closed
                    # create IValue_texture that references the created texture
                    ef: pymdlsdk.IExpression_factory = context.mdl_factory.create_expression_factory(context.transaction)
                    vf: pymdlsdk.IValue_factory = ef.get_value_factory()
                    func_def: pymdlsdk.IFunction_definition = context.transaction.access_as(pymdlsdk.IFunction_definition, call.get_function_definition())
                    func_param_types: pymdlsdk.IType_list = func_def.get_parameter_types()
                    texture_type: pymdlsdk.IType = func_param_types.get_type(name)
                    value: pymdlsdk.IValue = vf.create(texture_type)
                    value_texture: pymdlsdk.IValue_texture = value.get_interface(pymdlsdk.IValue_texture)
                    value_texture.set_value(new_texture_db_name)
                    expr: pymdlsdk.IExpression_constant = ef.create_constant(value_texture)
                    call.set_argument(name, expr)

        if isinstance(param, pymdl.ArgumentCall):
            # print(f"* Name: {name}")
            # print(f"  Type Kind: {param.type.kind}")
            # print(f"    dbName: {param.value}")
            await prepare_resources_for_export(context, param.value, temp_dir)


# ExportHelper: Helps to save files to URI (file and on server).
# If we want to export a file to a server, this helper:
#   1- creates a temp folder,
#   2- substitutes the original server folder with the temp folder,
#   3- files are saved/exported to the temp folder,
#   4- when finalize() is called, the content of the temp folder is saved to server and temp folder is deleted
# To avoid special casing here, we do the same for local files, i.e. `file:/`
class ExportHelper:
    def __init__(self, out_filename):
        self.export_uri = make_uri_with_scheme(out_filename)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temporary_export_uri = os.path.join(self.temp_dir.name, os.path.basename(out_filename))

    async def finalize(self, copy_files: bool = True):
        # copy files usually only if there was no error
        if copy_files:
            from_dir = os.path.dirname(self.temporary_export_uri)
            to_dir = os.path.dirname(self.export_uri)
            for ld in os.listdir(from_dir):
                f = os.path.basename(ld)
                result = await copy_async(os.path.join(from_dir, f), to_dir + '/' + f)
                if not result:
                    carb.log_error(f"Cannot copy from {f} to {to_dir}, error code: {result}.")
                else:
                    carb.log_info(f"Copied resource {f} to {to_dir}.")
        # Delete temp folder
        self.temp_dir.cleanup()

# Since OV support MDL modules outside of search paths we need special care after exporting to
# make sure the exported modules are as standard conform as possible. That means we try to restore
# search path modules and also try to make other imports relative to the exported one if possible
class PostProcessExportedModule:

    # helper to hold replacement mappings
    class Replacement_mapping:
        def __init__(self):
            self.import_search: str = ""
            self.import_replace: str = ""
            self.usage_search: str = ""
            self.usage_replace: str = ""

        @staticmethod
        def quote_reserved_names(uri: str, context: ConverterContext):
            # process package names to make sure they are valid MDL identifier
            segments: list[str] = uri.split('::')
            for s in range(len(segments)):
                if segments[s] != '' and segments[s] != '.' and segments[s] != '..' and not context.mdl_factory.is_valid_mdl_identifier(segments[s]):
                    segments[s] = "'" + segments[s] + "'"
            uri = '::'.join(segments)
            return uri

        @staticmethod
        def compute_for_search_path(search_path_uri: str, context: ConverterContext) -> "PostProcessExportedModule.Replacement_mapping":
            if search_path_uri.endswith('/'):
                search_path_uri = search_path_uri[:-1]  # drop trailing slashes
            mangled_search_path_uri: str = context.ov_neuray._mangleUri(search_path_uri, "::")
            mangled_search_path_uri = PostProcessExportedModule.Replacement_mapping.quote_reserved_names(mangled_search_path_uri, context)

            replacement: PostProcessExportedModule.Replacement_mapping = PostProcessExportedModule.Replacement_mapping()
            replacement.import_search = mangled_search_path_uri
            replacement.import_replace = ""                                # the empty string, just drop the leading search path
            replacement.usage_search = mangled_search_path_uri[2:] + "::"  # drop leading and keep add trailing `::` because the
                                                                           # usages don't start with colons
            replacement.usage_replace = ""                                 # empty string, just drop the leading search path
            return replacement

    def __init__(self, out_file_uri: str, context: ConverterContext):
        self.mdl_search_paths: list[str] = []
        self.replacement_mappings: list[PostProcessExportedModule.Replacement_mapping] = []

        with context.neuray.get_api_component(pymdlsdk.IMdl_configuration) as cfg:
            if cfg.is_valid_interface():
                for i in range(cfg.get_mdl_paths_length()):
                    sp = cfg.get_mdl_path(i).get_c_str()
                    sp = omni.client.normalize_url(sp)
                    self.mdl_search_paths.append(sp)

        # in OV we have nested search paths which is bad because paths are not unique when tying to map back
        # it would make sense to prefer the shortest possible search path because we can make sure relative
        # imports that go up do work
        # however in ov, modules are usually used absolute from search paths deeper in, so we try to match
        # those first
        self.mdl_search_paths.sort()
        for sp in self.mdl_search_paths:
            self.replacement_mappings.append(PostProcessExportedModule.Replacement_mapping.compute_for_search_path(sp, context))

        # add a general replacement rule for absolute paths
        # assuming an output directory:
        #   file:/D:/Content/a/b/sub
        # and content references that like these we want to map to:
        # (A)   file:/D:/Content/a/b/sub                ->        .::
        # (B)   file:/D:/Content/a/b                    ->        ..::
        # (C)   file:/D:/Content/c/d                    ->        ..::..::..::c::d
        # (D)   file:/E:/Content/c/d                    ->        (keep absolute)
        # (E)   omniverse://ov.nivida.com/Content/a/b   ->        (keep absolute)
        # the mappings should look like this
        # (A)   <OUTDIR>                ->      .
        # (B)   <OUTDIR>/..             ->      ..
        # (...) <OUTDIR>/../..          ->      ../..
        # (C)   <OUTDIR>/../../..       ->      ../../..
        # (D)   don't touch
        # (E)   don't touch
        if carb.settings.get_settings().get("exts/omni.mdl.usd_converter/allowRelativeExports"):
            url_parts = omni.client.break_url(out_file_uri)
            out_folder_path: str = url_parts.path[:url_parts.path.rfind("/")]
            out_folder_path_segments: list[str] = out_folder_path.split("/")

            max_upwards_levels: int = carb.settings.get_settings().get_as_int("exts/omni.mdl.usd_converter/allowRelativeExportUpwardLevels")
            upwards: str = ""

            # since the path starts with '/', the first segment will be empty. The second segment is the drive or root-level folder on unix
            # so we replace only paths that differ starting with the third segement (even for unix, root-level change would be another absolute path)
            for i in range(0, len(out_folder_path_segments) - 2):
                current_folder_uri: str = omni.client.make_url(scheme=url_parts.scheme, host=url_parts.host, path='/'.join(out_folder_path_segments))
                out_folder_path_segments.pop()
                mapping: PostProcessExportedModule.Replacement_mapping = PostProcessExportedModule.Replacement_mapping.compute_for_search_path(current_folder_uri, context)
                if i == 0:
                    mapping.import_replace = "."  # make the path realtive to the stage folder
                    upwards =  ".."               # init the upwards for the next iteration
                else:
                    mapping.import_replace = upwards
                    upwards =  upwards + "::.."

                # remove unneccessary mangling
                mapping.import_replace = PostProcessExportedModule.Replacement_mapping.quote_reserved_names(mapping.import_replace, context)
                self.replacement_mappings.append(mapping)

                # print(f"Rule:             {current_folder_uri}")
                # print(f"- Import Search:  {mapping.import_search}")
                # print(f"- Import Replace: {mapping.import_replace}")
                # print(f"- Usage Search:   {mapping.usage_search}")
                # print(f"- Usage Replace:  {mapping.usage_replace}\n\n")

                if i == max_upwards_levels:
                    return
        else:
            # we don't allow relative exports
            pass

    #  MDL-1374: this is probably not user code proof but it sould handle the output of the printer
    def __workaround_fix_reserved_words_wrongly_produced_by_the_printer(self, import_line: str) -> str:
        for reserved in _mdl_reserved_words:
            import_line = import_line.replace(f"::{reserved}::", f"::'{reserved}'::")  # regular imports
            import_line = import_line.replace(f"::{reserved} ", f"::'{reserved}' ")   # can appear in using statements
        return import_line

    # run the post processing on a module, mainly to remove mangled names
    def process(self, local_file_uri: str):
        url_parts = omni.client.break_url(local_file_uri)
        lines: list[str] = []
        with open(url_parts.path, 'r') as f_in:
            lines = f_in.readlines()
        with open(url_parts.path, 'w') as f_out:
            f_out.writelines(generate_export_header())
            line: str
            for line in lines:
                line_stripped: str = line.strip()
                if line_stripped.startswith('import') or line_stripped.startswith('using'):
                    # apply a workaround for a bug that is there till including iray/neuray 2023.1.3
                    line = self.__workaround_fix_reserved_words_wrongly_produced_by_the_printer(line)
                    # apply replacement mappings
                    mapping: PostProcessExportedModule.Replacement_mapping
                    for mapping in self.replacement_mappings:
                        line = line.replace(mapping.import_search, mapping.import_replace)
                else:
                    # handle import lines different from usings
                    mapping: PostProcessExportedModule.Replacement_mapping
                    for mapping in self.replacement_mappings:
                        line = line.replace(mapping.usage_search, mapping.usage_replace)
                f_out.write(line)


async def save_instance_to_module(context, inst_name, usd_prim, temp_dir, out_filename):
    carb.log_info("============ MDL Save Instance to Module =============")
    neuray = context.neuray
    transaction = context.transaction
    stage = context.stage

    # access shader prim
    prim = get_shader_prim(stage, usd_prim)
    prim_name = usd_prim.pathString.split('/')[-1]

    if out_filename == None or os.path.isdir(out_filename) or os.path.splitext(out_filename)[1] != '.mdl':
        carb.log_error(f"Error: output filename is invalid, expected an .mdl file: '{out_filename}'")
        return False

    # Handle Nucleus: OM-46539 Graph to MDL fails to copy Nucleus textures to local filesystem when exporting
    export_helper = ExportHelper(out_filename)
    out_filename = None # do not use anymore

    # Sanity checks
    with transaction.access_as(pymdlsdk.IFunction_call, inst_name) as inst:
        if inst == None or not inst.is_valid_interface():
            carb.log_error("Error: Invalid instance name (IFunction_call): {}".format(inst_name))
            return False
        with transaction.access_as(pymdlsdk.IFunction_definition, inst.get_function_definition()) as fd:
            if fd == None or not fd.is_valid_interface():
                carb.log_error("Error: Invalid IFunction_definition: {}".format(inst.get_function_definition()))
                return False
            module = pymdl.Module._fetchFromDb(transaction, fd.get_module())
            if module == None:
                carb.log_error("Error: Invalid Module: {}".format(fd.get_module()))
                return False

    # since resourcse are handled by the renderer we need to pass them to neuray before exporting
    await prepare_resources_for_export(context, inst_name, temp_dir)

    factory: pymdlsdk.IMdl_factory = neuray.get_api_component(pymdlsdk.IMdl_factory)
    execution_context = factory.create_execution_context()

    # Create the module builder.
    module_name = "mdl::new_module_28f8c871b7034e55a0541be81655ffb1"
    module_builder = factory.create_module_builder(
        transaction,
        module_name,
        pymdlsdk.Mdl_version.MDL_VERSION_1_8, # Force 1.8 because of an outstanding bugfix that did not make it into neuray 2023.0.2
        pymdlsdk.Mdl_version.MDL_VERSION_LATEST,
        execution_context)

    if not module_builder.is_valid_interface():
        carb.log_error("Error: Failed to create module builder")
        return False

    module_builder.clear_module(execution_context)

    # Create a variant
    success = False
    with transaction.access_as(pymdlsdk.IFunction_call, inst_name) as inst, \
        factory.create_expression_factory(transaction) as ef, \
        ef.create_annotation_block() as empty_anno_block:
        if inst.is_valid_interface():

            if is_reserved_word(prim_name):
                variant_name = "Main"
            else:
                variant_name = prim_name

            result = module_builder.add_variant(
                variant_name,
                inst.get_function_definition(),
                inst.get_arguments(),
                empty_anno_block,
                empty_anno_block,
                True,
                execution_context)
            if result != 0:
                carb.log_error("Error: Failed to add variant to module builder:\n\t'{}'\n\t'{}'\n\t'{}'".format(prim.GetName(), inst.get_function_definition(), inst.get_arguments()))
                for i in range(execution_context.get_messages_count()):
                    carb.log_error(execution_context.get_message(i).get_string())

            if result == 0:
                with neuray.get_api_component(pymdlsdk.IMdl_impexp_api) as imp_exp:
                    rtn = -1
                    execution_context.set_option("bundle_resources", True)
                    rtn = imp_exp.export_module(transaction, module_name, export_helper.temporary_export_uri, execution_context)

                    if rtn >= 0:
                        if not context.stage is None:
                            stageFolder = __get_stage_folder(context.stage)

                        # dump the mangled file
                        if  carb.settings.get_settings().get_as_bool("exts/omni.mdl.usd_converter/tests/debugdumps"):
                            import omni.kit.test
                            filename_base: str = os.path.splitext(os.path.basename(export_helper.temporary_export_uri))[0]
                            await copy_async(
                                export_helper.temporary_export_uri,
                                os.path.join(omni.kit.test.get_test_output_path(), f"{filename_base}.mangeled.mdl"))

                        # unmangle
                        postProcessor: PostProcessExportedModule = PostProcessExportedModule(export_helper.export_uri, context)
                        postProcessor.process(export_helper.temporary_export_uri)

                        carb.log_info(f"Success: Material '{prim_name}' exported to module '{export_helper.temporary_export_uri}'")
                        # Copy files to Nucleus if needed
                        await export_helper.finalize()
                        success = True
                    else:
                        carb.log_error(f"Failure: Could not export Material '{prim_name}' to module '{export_helper.export_uri}'")
                        await export_helper.finalize(copy_files = False)

    module_builder.clear_module(execution_context)
    return success
