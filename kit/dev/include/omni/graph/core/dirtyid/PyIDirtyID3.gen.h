// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

inline auto bindIDirtyID3(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::unstable::IDirtyID3_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::unstable::IDirtyID3_abi>>,
               omni::core::Api<omni::graph::core::unstable::IDirtyID2_abi>>
        clsParent(m, "_IDirtyID3");
    py::class_<omni::graph::core::unstable::IDirtyID3, omni::python::detail::PyObjectPtr<omni::graph::core::unstable::IDirtyID3>>
        cls(m, "IDirtyID3", clsParent);
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::graph::core::unstable::IDirtyID3>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::unstable::IDirtyID3>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::graph::core::unstable::IDirtyID3 instantiation");
            }
            return tmp;
        }));
    cls.def("open", &omni::graph::core::unstable::IDirtyID3::open,
            R"OMNI_BIND_RAW_(@brief Opens a thread-local scope to ensure that a bundle is only made dirty once.
@return An identifier of the scope.)OMNI_BIND_RAW_");
    cls.def("close", &omni::graph::core::unstable::IDirtyID3::close,
            R"OMNI_BIND_RAW_(@brief Closes a previously opened scope.
Each call to open must be balanced with a call to close.
Please use the BundleWriteBlock API helper to do this robustly.
@param id The identifier that was returned by open.
@return Success if closed successfully, Fail when the scope was not open)OMNI_BIND_RAW_",
            py::arg("id"));
    return omni::python::PyBind<omni::graph::core::unstable::IDirtyID3>::bind(cls);
}
