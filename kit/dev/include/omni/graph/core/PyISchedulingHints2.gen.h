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

inline auto bindePurityStatus(const py::module& m)
{
    py::enum_<omni::graph::core::ePurityStatus> e(
        m, "ePurityStatus", R"OMNI_BIND_RAW_(The purity of the node implementation. For some context, a "pure" node is
one whose initialize, compute, and release methods are entirely deterministic,
i.e. they will always produce the same output attribute values for a given set
of input attribute values, and do not access, rely on, or otherwise mutate data
external to the node's scope)OMNI_BIND_RAW_");
    e.value("E_IMPURE", omni::graph::core::ePurityStatus::eImpure,
            R"OMNI_BIND_RAW_(Node is assumed to not be pure)OMNI_BIND_RAW_");
    e.value("E_PURE", omni::graph::core::ePurityStatus::ePure,
            R"OMNI_BIND_RAW_(Node can be considered pure if explicitly specified by the node author)OMNI_BIND_RAW_");

    return e;
}

inline auto bindISchedulingHints2(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::ISchedulingHints2_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::ISchedulingHints2_abi>>,
               omni::core::Api<omni::graph::core::ISchedulingHints_abi>>
        clsParent(m, "_ISchedulingHints2");
    py::class_<omni::graph::core::ISchedulingHints2, omni::python::detail::PyObjectPtr<omni::graph::core::ISchedulingHints2>>
        cls(m, "ISchedulingHints2", clsParent,
            R"OMNI_BIND_RAW_(Interface extension for ISchedulingHints that adds a new "pure" hint)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::graph::core::ISchedulingHints2>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::ISchedulingHints2>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::graph::core::ISchedulingHints2 instantiation");
            }
            return tmp;
        }));
    cls.def_property("purity_status", &omni::graph::core::ISchedulingHints2::getPurityStatus,
                     &omni::graph::core::ISchedulingHints2::setPurityStatus);
    return omni::python::PyBind<omni::graph::core::ISchedulingHints2>::bind(cls);
}
