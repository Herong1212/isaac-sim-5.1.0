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

inline auto bindBundleChangeType(const py::module& m)
{
    py::enum_<omni::graph::core::BundleChangeType> e(
        m, "BundleChangeType", R"OMNI_BIND_RAW_(Enumeration representing the type of change that occurred in a bundle.

This enumeration is used to identify the kind of modification that has taken place in a bundle or attribute.
It's used as the return type for functions that check bundles and attributes, signaling whether those have been
modified or not.)OMNI_BIND_RAW_");
    e.value("NONE", omni::graph::core::BundleChangeType::None,
            R"OMNI_BIND_RAW_(Indicates that no change has occurred in the bundle.)OMNI_BIND_RAW_");
    e.value("MODIFIED", omni::graph::core::BundleChangeType::Modified,
            R"OMNI_BIND_RAW_(Indicates that the bundle has been modified.)OMNI_BIND_RAW_");

    return e;
}

inline auto bindIBundleChanges(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::IBundleChanges_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::IBundleChanges_abi>>,
               omni::core::IObject>
        clsParent(m, "_IBundleChanges");
    py::class_<omni::graph::core::IBundleChanges, omni::python::detail::PyObjectPtr<omni::graph::core::IBundleChanges>> cls(
        m, "IBundleChanges", clsParent,
        R"OMNI_BIND_RAW_(Interface for monitoring and handling changes in bundles and attributes.

The IBundleChanges_abi is an interface that provides methods for checking whether bundles and attributes
have been modified, and cleaning them if they have been modified. This is particularly useful in scenarios
where it's crucial to track changes and maintain the state of bundles and attributes.

This interface provides several methods for checking and cleaning modifications, each catering to different
use cases such as handling single bundles, multiple bundles, attributes, or specific attributes of a single bundle.

The methods of this interface return a BundleChangeType enumeration that indicates whether the checked entity
(bundle or attribute) has been modified.)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::graph::core::IBundleChanges>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::IBundleChanges>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::graph::core::IBundleChanges instantiation");
            }
            return tmp;
        }));
    cls.def(
        "activate_change_tracking",
        [](omni::graph::core::IBundleChanges* self, omni::graph::core::BundleHandle* handle)
        {
            auto return_value = self->activateChangeTracking(*handle);

            return return_value;
        },
        R"OMNI_BIND_RAW_(@brief Activate tracking for specific bundle on its attributes and children.
@param handle to the specific bundles to enable change tracking.
@return An omni::core::Result indicating the success of the operation.)OMNI_BIND_RAW_",
        py::arg("handle"));
    cls.def(
        "deactivate_change_tracking",
        [](omni::graph::core::IBundleChanges* self, omni::graph::core::BundleHandle* handle)
        {
            auto return_value = self->deactivateChangeTracking(*handle);

            return return_value;
        },
        R"OMNI_BIND_RAW_(@brief Deactivate tracking for specific bundle on its attributes and children.
@param handle to the specific bundles to enable change tracking.
@return An omni::core::Result indicating the success of the operation.)OMNI_BIND_RAW_",
        py::arg("handle"));
    cls.def("clear_changes", &omni::graph::core::IBundleChanges::clearChanges, R"OMNI_BIND_RAW_(Clears all recorded changes.

This method is used to clear or reset all the recorded changes of the bundles and attributes.
It can be used when the changes have been processed and need to be discarded.

An omni::core::Result indicating the success of the operation.)OMNI_BIND_RAW_");
    return omni::python::PyBind<omni::graph::core::IBundleChanges>::bind(cls);
}
