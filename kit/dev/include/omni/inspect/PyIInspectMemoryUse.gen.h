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

inline auto bindIInspectMemoryUse(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::inspect::IInspectMemoryUse_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::inspect::IInspectMemoryUse_abi>>,
               omni::core::Api<omni::inspect::IInspector_abi>>
        clsParent(m, "_IInspectMemoryUse");
    py::class_<omni::inspect::IInspectMemoryUse, omni::python::detail::PyObjectPtr<omni::inspect::IInspectMemoryUse>> cls(
        m, "IInspectMemoryUse", clsParent, R"OMNI_BIND_RAW_(Base class for object inspection requests.)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::inspect::IInspectMemoryUse>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::inspect::IInspectMemoryUse>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::inspect::IInspectMemoryUse instantiation");
            }
            return tmp;
        }));
    cls.def(
        "use_memory",
        [](omni::inspect::IInspectMemoryUse* self, const void* ptr, size_t bytesUsed)
        {
            auto return_value = self->useMemory(ptr, bytesUsed);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Add a block of used memory
Returns false if the memory was not recorded (e.g. because it was already recorded)

@param[in] ptr Pointer to the memory location being logged as in-use
@param[in] bytesUsed Number of bytes in use at that location)OMNI_BIND_RAW_",
        py::arg("ptr"), py::arg("bytes_used"));
    cls.def("reset", &omni::inspect::IInspectMemoryUse::reset,
            R"OMNI_BIND_RAW_(Reset the memory usage data to a zero state)OMNI_BIND_RAW_");
    cls.def(
        "total_used", &omni::inspect::IInspectMemoryUse::totalUsed,
        R"OMNI_BIND_RAW_(@returns the total number of bytes of memory used since creation or the last call to reset().)OMNI_BIND_RAW_");
    return omni::python::PyBind<omni::inspect::IInspectMemoryUse>::bind(cls);
}
