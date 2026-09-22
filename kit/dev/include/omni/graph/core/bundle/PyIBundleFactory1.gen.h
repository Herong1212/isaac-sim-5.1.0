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

inline auto bindIBundleFactory(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::IBundleFactory_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::IBundleFactory_abi>>,
               omni::core::IObject>
        clsParent(m, "_IBundleFactory");
    py::class_<omni::graph::core::IBundleFactory, omni::python::detail::PyObjectPtr<omni::graph::core::IBundleFactory>> cls(
        m, "IBundleFactory", clsParent, R"OMNI_BIND_RAW_(Interface to create new bundles)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::graph::core::IBundleFactory>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::IBundleFactory>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::graph::core::IBundleFactory instantiation");
            }
            return tmp;
        }));
    return omni::python::PyBind<omni::graph::core::IBundleFactory>::bind(cls);
}
