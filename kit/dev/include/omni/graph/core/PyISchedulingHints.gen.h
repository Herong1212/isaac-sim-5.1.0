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

inline auto bindeAccessType(const py::module& m)
{
    py::enum_<omni::graph::core::eAccessType> e(
        m, "eAccessType",
        R"OMNI_BIND_RAW_(How does the node access the data described by the enum eAccessLocation)OMNI_BIND_RAW_");
    e.value("E_NONE", omni::graph::core::eAccessType::eNone,
            R"OMNI_BIND_RAW_(There is no access to data of the associated type)OMNI_BIND_RAW_");
    e.value("E_READ", omni::graph::core::eAccessType::eRead,
            R"OMNI_BIND_RAW_(There is only read access to data of the associated type)OMNI_BIND_RAW_");
    e.value("E_WRITE", omni::graph::core::eAccessType::eWrite,
            R"OMNI_BIND_RAW_(There is only write access to data of the associated type)OMNI_BIND_RAW_");
    e.value("E_READ_WRITE", omni::graph::core::eAccessType::eReadWrite,
            R"OMNI_BIND_RAW_(There is both read and write access to data of the associated type)OMNI_BIND_RAW_");

    return e;
}

inline auto bindeAccessLocation(const py::module& m)
{
    py::enum_<omni::graph::core::eAccessLocation> e(
        m, "eAccessLocation", R"OMNI_BIND_RAW_(What type of non-attribute data does this node access)OMNI_BIND_RAW_");
    e.value("E_USD", omni::graph::core::eAccessLocation::eUsd,
            R"OMNI_BIND_RAW_(Accesses the USD stage data)OMNI_BIND_RAW_");
    e.value("E_GLOBAL", omni::graph::core::eAccessLocation::eGlobal,
            R"OMNI_BIND_RAW_(Accesses data that is not part of the node or node type)OMNI_BIND_RAW_");
    e.value("E_STATIC", omni::graph::core::eAccessLocation::eStatic,
            R"OMNI_BIND_RAW_(Accesses data that is shared by every instance of a particular node type)OMNI_BIND_RAW_");
    e.value("E_TOPOLOGY", omni::graph::core::eAccessLocation::eTopology,
            R"OMNI_BIND_RAW_(Accesses information on the topology of the graph to which the node belongs)OMNI_BIND_RAW_");

    return e;
}

inline auto bindeThreadSafety(const py::module& m)
{
    py::enum_<omni::graph::core::eThreadSafety> e(
        m, "eThreadSafety", R"OMNI_BIND_RAW_(How thread safe is the node during evaluation)OMNI_BIND_RAW_");
    e.value("E_SAFE", omni::graph::core::eThreadSafety::eSafe,
            R"OMNI_BIND_RAW_(Nodes can be evaluated in multiple threads safely)OMNI_BIND_RAW_");
    e.value("E_UNSAFE", omni::graph::core::eThreadSafety::eUnsafe,
            R"OMNI_BIND_RAW_(Nodes cannot be evaluated in multiple threads safely)OMNI_BIND_RAW_");
    e.value("E_UNKNOWN", omni::graph::core::eThreadSafety::eUnknown,
            R"OMNI_BIND_RAW_(The thread safety status of the node type is unknown)OMNI_BIND_RAW_");

    return e;
}

inline auto bindeComputeRule(const py::module& m)
{
    py::enum_<omni::graph::core::eComputeRule> e(
        m, "eComputeRule", R"OMNI_BIND_RAW_(How the node is allowed to be computed)OMNI_BIND_RAW_");
    e.value("E_DEFAULT", omni::graph::core::eComputeRule::eDefault,
            R"OMNI_BIND_RAW_(Nodes are computed according to the default evaluator rules)OMNI_BIND_RAW_");
    e.value(
        "E_ON_REQUEST", omni::graph::core::eComputeRule::eOnRequest,
        R"OMNI_BIND_RAW_(The evaluator may skip computing this node until explicitly requested with INode::requestCompute)OMNI_BIND_RAW_");

    return e;
}

inline auto bindISchedulingHints(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::ISchedulingHints_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::ISchedulingHints_abi>>,
               omni::core::IObject>
        clsParent(m, "_ISchedulingHints");
    py::class_<omni::graph::core::ISchedulingHints, omni::python::detail::PyObjectPtr<omni::graph::core::ISchedulingHints>> cls(
        m, "ISchedulingHints", clsParent,
        R"OMNI_BIND_RAW_(Interface to the list of scheduling hints that can be applied to a node type)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::graph::core::ISchedulingHints>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::ISchedulingHints>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::graph::core::ISchedulingHints instantiation");
            }
            return tmp;
        }));
    cls.def_property("thread_safety", &omni::graph::core::ISchedulingHints::getThreadSafety,
                     &omni::graph::core::ISchedulingHints::setThreadSafety);
    cls.def_property("compute_rule", &omni::graph::core::ISchedulingHints::getComputeRule,
                     &omni::graph::core::ISchedulingHints::setComputeRule);
    cls.def("get_data_access", &omni::graph::core::ISchedulingHints::getDataAccess,
            R"OMNI_BIND_RAW_(Get the type of access the node has for a given data type

@param[in] dataType Type of data for which access type is being modified
@returns Value of the access type flag)OMNI_BIND_RAW_",
            py::arg("data_type"));
    cls.def("set_data_access", &omni::graph::core::ISchedulingHints::setDataAccess,
            R"OMNI_BIND_RAW_(Set the flag describing how a node accesses particular data in its compute _abi (defaults to no access).
Setting any of these flags will, in most cases, automatically mark the node as "not threadsafe".
One current exception to this is allowing a node to be both threadsafe and a writer to USD, since
such behavior can be achieved if delayed writebacks (e.g. "registerForUSDWriteBack") are utilized
in the node's compute method.

@param[in] dataType Type of data for which access type is being modified
@param[in] newAccessType New value of the access type flag)OMNI_BIND_RAW_",
            py::arg("data_type"), py::arg("new_access_type"));
    cls.def(
        "inspect",
        [](omni::graph::core::ISchedulingHints* self, omni::inspect::IInspector* inspector)
        {
            auto return_value = self->inspect(inspector);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Runs the inspector on the scheduling hints.

@param[in] inspector The inspector class
@return true if the inspection ran successfully, false if the inspection type is not supported)OMNI_BIND_RAW_",
        py::arg("inspector"));
    return omni::python::PyBind<omni::graph::core::ISchedulingHints>::bind(cls);
}
