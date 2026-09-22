// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

inline auto bindINodeCategories(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::INodeCategories_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::INodeCategories_abi>>,
               omni::core::IObject>
        clsParent(m, "_INodeCategories");
    py::class_<omni::graph::core::INodeCategories, omni::python::detail::PyObjectPtr<omni::graph::core::INodeCategories>> cls(
        m, "INodeCategories", clsParent,
        R"OMNI_BIND_RAW_(Interface to the list of categories that a node type can belong to )OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::graph::core::INodeCategories>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::INodeCategories>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::graph::core::INodeCategories instantiation");
            }
            return tmp;
        }));
    cls.def_property_readonly("category_count", &omni::graph::core::INodeCategories::getCategoryCount);
    cls.def(
        "define_category",
        [](omni::graph::core::INodeCategories* self, const char* categoryName, const char* categoryDescription)
        {
            auto return_value = self->defineCategory(categoryName, categoryDescription);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Define a new category

@param[in] categoryName Name of the new category
@param[in] categoryDescription Description of the category

@return false if there was already a category with the given name)OMNI_BIND_RAW_",
        py::arg("category_name"), py::arg("category_description"));
    cls.def(
        "remove_category",
        [](omni::graph::core::INodeCategories* self, const char* categoryName)
        {
            auto return_value = self->removeCategory(categoryName);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Remove an existing category, mainly to manage the ones created by a node type for itself

@param[in] categoryName Name of the category to remove

@return false if there was no category with the given name)OMNI_BIND_RAW_",
        py::arg("category_name"));
    return omni::python::PyBind<omni::graph::core::INodeCategories>::bind(cls);
}
