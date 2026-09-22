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

inline auto bindIPrimView(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::IPrimView_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::IPrimView_abi>>, omni::core::IObject>
        clsParent(m, "_IPrimView");
    py::class_<omni::graph::core::IPrimView, omni::python::detail::PyObjectPtr<omni::graph::core::IPrimView>> cls(
        m, "IPrimView", clsParent,
        R"OMNI_BIND_RAW_(PrimView is an interface that provides a view to a set of prims for use with OmniGraph instancing.

The prim view provides both a list of prims, and a layout of which prims can be treated as consecutive data in fabric)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::graph::core::IPrimView>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::IPrimView>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::graph::core::IPrimView instantiation");
            }
            return tmp;
        }));
    cls.def_property_readonly("prim_count", &omni::graph::core::IPrimView::getPrimCount);
    return omni::python::PyBind<omni::graph::core::IPrimView>::bind(cls);
}
