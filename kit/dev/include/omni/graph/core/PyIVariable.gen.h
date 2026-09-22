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

inline auto bindeVariableScope(const py::module& m)
{
    py::enum_<omni::graph::core::eVariableScope> e(
        m, "eVariableScope", R"OMNI_BIND_RAW_(Scope in which the variable has been made available)OMNI_BIND_RAW_");
    e.value("E_PRIVATE", omni::graph::core::eVariableScope::ePrivate,
            R"OMNI_BIND_RAW_(Variable is accessible only to its graph )OMNI_BIND_RAW_");
    e.value("E_READ_ONLY", omni::graph::core::eVariableScope::eReadOnly,
            R"OMNI_BIND_RAW_(Variable can be read by other graphs )OMNI_BIND_RAW_");
    e.value("E_PUBLIC", omni::graph::core::eVariableScope::ePublic,
            R"OMNI_BIND_RAW_(Variable can be read/written by other graphs )OMNI_BIND_RAW_");

    return e;
}

inline auto bindIVariable(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::IVariable_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::IVariable_abi>>, omni::core::IObject>
        clsParent(m, "_IVariable");
    py::class_<omni::graph::core::IVariable, omni::python::detail::PyObjectPtr<omni::graph::core::IVariable>> cls(
        m, "IVariable", clsParent,
        R"OMNI_BIND_RAW_(Object that contains a value that is local to a graph, available from anywhere in the graph)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::graph::core::IVariable>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::IVariable>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::graph::core::IVariable instantiation");
            }
            return tmp;
        }));
    cls.def_property_readonly("name", &omni::graph::core::IVariable::getName);
    cls.def_property_readonly("source_path", &omni::graph::core::IVariable::getSourcePath);
    cls.def_property("category", &omni::graph::core::IVariable::getCategory,
                     [](omni::graph::core::IVariable* self, const char* category) { self->setCategory(category); });
    cls.def_property("display_name", &omni::graph::core::IVariable::getDisplayName,
                     [](omni::graph::core::IVariable* self, const char* displayName)
                     { self->setDisplayName(displayName); });
    cls.def_property("tooltip", &omni::graph::core::IVariable::getTooltip,
                     [](omni::graph::core::IVariable* self, const char* toolTip) { self->setTooltip(toolTip); });
    cls.def_property("scope", &omni::graph::core::IVariable::getScope, &omni::graph::core::IVariable::setScope);
    cls.def_property_readonly("valid", &omni::graph::core::IVariable::isValid);
    return omni::python::PyBind<omni::graph::core::IVariable>::bind(cls);
}
