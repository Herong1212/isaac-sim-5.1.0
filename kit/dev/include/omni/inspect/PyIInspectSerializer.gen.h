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

inline auto bindIInspectSerializer(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::inspect::IInspectSerializer_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::inspect::IInspectSerializer_abi>>,
               omni::core::Api<omni::inspect::IInspector_abi>>
        clsParent(m, "_IInspectSerializer");
    py::class_<omni::inspect::IInspectSerializer, omni::python::detail::PyObjectPtr<omni::inspect::IInspectSerializer>> cls(
        m, "IInspectSerializer", clsParent,
        R"OMNI_BIND_RAW_(Base class for object serialization requests.)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::inspect::IInspectSerializer>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::inspect::IInspectSerializer>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::inspect::IInspectSerializer instantiation");
            }
            return tmp;
        }));
    cls.def_property("output_to_file_path", nullptr,
                     [](omni::inspect::IInspectSerializer* self, const char* filePath)
                     { self->setOutputToFilePath(filePath); });
    cls.def_property_readonly("output_location", &omni::inspect::IInspectSerializer::getOutputLocation);
    cls.def(
        "write_string", [](omni::inspect::IInspectSerializer* self, const char* toWrite) { self->writeString(toWrite); },
        R"OMNI_BIND_RAW_(Write a fixed string to the serializer output location

@param[in] toWrite String to be written to the serializer)OMNI_BIND_RAW_",
        py::arg("to_write"));
    cls.def("set_output_to_string", &omni::inspect::IInspectSerializer::setOutputToString,
            R"OMNI_BIND_RAW_(Set the output location of the serializer data to be a local string.
No check is made to ensure that the string size doesn't get too large so when in doubt use a file path.)OMNI_BIND_RAW_");
    cls.def("as_string", &omni::inspect::IInspectSerializer::asString, R"OMNI_BIND_RAW_(Get the current output as a string.

@returns The output that has been sent to the serializer. If the output is being sent to a file path then read
the file at that path and return the contents of the file. If the output is being sent to stdout or stderr
then nothing is returned as that output is unavailable after flushing.)OMNI_BIND_RAW_");
    cls.def("clear", &omni::inspect::IInspectSerializer::clear,
            R"OMNI_BIND_RAW_(Clear the contents of the serializer output, either emptying the file or clearing the string, depending on
where the current output is directed.)OMNI_BIND_RAW_");
    return omni::python::PyBind<omni::inspect::IInspectSerializer>::bind(cls);
}
