// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// --------- Warning: This is a build system generated file. ----------

#pragma once

#include <omni/core/ITypeFactory.h>
#include <omni/python/PyBind.h>
#include <omni/python/PyString.h>
#include <omni/python/PyVec.h>

#include <sstream>

inline auto bindIInspectJsonSerializer(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::inspect::IInspectJsonSerializer_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::inspect::IInspectJsonSerializer_abi>>,
               omni::core::Api<omni::inspect::IInspector_abi>>
        clsParent(m, "_IInspectJsonSerializer");
    py::class_<omni::inspect::IInspectJsonSerializer, omni::python::detail::PyObjectPtr<omni::inspect::IInspectJsonSerializer>>
        cls(m, "IInspectJsonSerializer", clsParent,
            R"OMNI_BIND_RAW_(Base class for object inspection requests.)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::inspect::IInspectJsonSerializer>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::inspect::IInspectJsonSerializer>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::inspect::IInspectJsonSerializer instantiation");
            }
            return tmp;
        }));
    cls.def_property("output_to_file_path", nullptr,
                     [](omni::inspect::IInspectJsonSerializer* self, const char* filePath)
                     { self->setOutputToFilePath(filePath); });
    cls.def_property_readonly("output_location", &omni::inspect::IInspectJsonSerializer::getOutputLocation);
    cls.def("set_output_to_string", &omni::inspect::IInspectJsonSerializer::setOutputToString,
            R"OMNI_BIND_RAW_(Set the output location of the serializer data to be a local string.
No check is made to ensure that the string size doesn't get too large so when in doubt use a file path.)OMNI_BIND_RAW_");
    cls.def("as_string", &omni::inspect::IInspectJsonSerializer::asString,
            R"OMNI_BIND_RAW_(Get the current output as a string. If the output is being sent to a file path then read the file at that path
and return the contents of the file (with the usual caveats about file size).

@returns String representation of the output so far)OMNI_BIND_RAW_");
    cls.def("clear", &omni::inspect::IInspectJsonSerializer::clear,
            R"OMNI_BIND_RAW_(Clear the contents of the serializer output, either emptying the file or clearing the string, depending on
where the current output is directed.)OMNI_BIND_RAW_");
    cls.def(
        "write_key_with_length",
        [](omni::inspect::IInspectJsonSerializer* self, const char* key, size_t keyLen)
        {
            auto return_value = self->writeKeyWithLength(key, keyLen);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Write out a JSON key for an object property.

@param[in] key    The string value for the key. This can be nullptr.
@param[in] keyLen The length of @ref key, excluding the null terminator.
@returns whether or not validation succeeded.)OMNI_BIND_RAW_",
        py::arg("key"), py::arg("key_len"));
    cls.def(
        "write_key",
        [](omni::inspect::IInspectJsonSerializer* self, const char* key)
        {
            auto return_value = self->writeKey(key);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Write out a JSON key for an object property.

@param[in] key The key name for this property. This may be nullptr.
@returns whether or not validation succeeded.)OMNI_BIND_RAW_",
        py::arg("key"));
    cls.def("write_null", &omni::inspect::IInspectJsonSerializer::writeNull, R"OMNI_BIND_RAW_(Write out a JSON null value.

@returns whether or not validation succeeded.)OMNI_BIND_RAW_");
    cls.def("write_bool", &omni::inspect::IInspectJsonSerializer::writeBool,
            R"OMNI_BIND_RAW_(Write out a JSON boolean value.

@param[in] value The boolean value.
@returns whether or not validation succeeded.)OMNI_BIND_RAW_",
            py::arg("value"));
    cls.def("write_int", &omni::inspect::IInspectJsonSerializer::writeInt, R"OMNI_BIND_RAW_(Write out a JSON integer value.

@param[in] value The integer value.
@returns whether or not validation succeeded.)OMNI_BIND_RAW_",
            py::arg("value"));
    cls.def("write_u_int", &omni::inspect::IInspectJsonSerializer::writeUInt,
            R"OMNI_BIND_RAW_(Write out a JSON unsigned integer value.

@param[in] value The unsigned integer value.
@returns whether or not validation succeeded.)OMNI_BIND_RAW_",
            py::arg("value"));
    cls.def("write_int64", &omni::inspect::IInspectJsonSerializer::writeInt64,
            R"OMNI_BIND_RAW_(Write out a JSON 64-bit integer value.

@param[in] value The 64-bit integer value.
@returns whether or not validation succeeded.
@note 64 bit integers will be written as a string of they are too long
to be stored as a number that's interoperable with javascript's
double precision floating point format.)OMNI_BIND_RAW_",
            py::arg("value"));
    cls.def("write_u_int64", &omni::inspect::IInspectJsonSerializer::writeUInt64,
            R"OMNI_BIND_RAW_(Write out a JSON 64-bit unsigned integer value.

@param[in] value The 64-bit unsigned integer value.
@returns whether or not validation succeeded.
@note 64 bit integers will be written as a string of they are too long
to be stored as a number that's interoperable with javascript's
double precision floating point format.)OMNI_BIND_RAW_",
            py::arg("value"));
    cls.def("write_double", &omni::inspect::IInspectJsonSerializer::writeDouble,
            R"OMNI_BIND_RAW_(Write out a JSON double (aka number) value.

@param[in] value The double value.
@returns whether or not validation succeeded.)OMNI_BIND_RAW_",
            py::arg("value"));
    cls.def("write_float", &omni::inspect::IInspectJsonSerializer::writeFloat,
            R"OMNI_BIND_RAW_(Write out a JSON float (aka number) value.

@param[in] value The double value.
@returns whether or not validation succeeded.)OMNI_BIND_RAW_",
            py::arg("value"));
    cls.def(
        "write_string_with_length",
        [](omni::inspect::IInspectJsonSerializer* self, const char* value, size_t len)
        {
            auto return_value = self->writeStringWithLength(value, len);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Write out a JSON string value.

@param[in] value The string value. This can be nullptr if @p len is 0.
@param[in] len   The length of @p value, excluding the null terminator.
@returns whether or not validation succeeded.)OMNI_BIND_RAW_",
        py::arg("value"), py::arg("len"));
    cls.def(
        "write_string",
        [](omni::inspect::IInspectJsonSerializer* self, const char* value)
        {
            auto return_value = self->writeString(value);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Write out a JSON string value.

@param[in] value The string value. This can be nullptr.
@returns whether or not validation succeeded.)OMNI_BIND_RAW_",
        py::arg("value"));
    cls.def("open_array", &omni::inspect::IInspectJsonSerializer::openArray, R"OMNI_BIND_RAW_(Begin a JSON array.

@returns whether or not validation succeeded.
@note This may throw a std::bad_alloc or a std::length_error if the stack of scopes gets too large)OMNI_BIND_RAW_");
    cls.def("close_array", &omni::inspect::IInspectJsonSerializer::closeArray, R"OMNI_BIND_RAW_(Finish writing a JSON array.

@returns whether or not validation succeeded.)OMNI_BIND_RAW_");
    cls.def("open_object", &omni::inspect::IInspectJsonSerializer::openObject, R"OMNI_BIND_RAW_(Begin a JSON object.

@returns whether or not validation succeeded.)OMNI_BIND_RAW_");
    cls.def("close_object", &omni::inspect::IInspectJsonSerializer::closeObject,
            R"OMNI_BIND_RAW_(Finish writing a JSON object.

@returns whether or not validation succeeded.)OMNI_BIND_RAW_");
    cls.def("finish", &omni::inspect::IInspectJsonSerializer::finish,
            R"OMNI_BIND_RAW_(Finishes writing the entire JSON dictionary.

@returns whether or not validation succeeded.)OMNI_BIND_RAW_");
    return omni::python::PyBind<omni::inspect::IInspectJsonSerializer>::bind(cls);
}
