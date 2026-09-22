// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// DO NOT MODIFY THIS FILE. This is a generated file.
// This file was generated from: StructuredLog.Cloud.schema

#pragma once

#include <carb/BindingsPythonUtils.h>
#include "StructuredLog.Cloud.gen.h"

namespace omni
{
namespace telemetry
{

struct Struct_Wrap_startup_ident
{
    /** The identifier of the cluster this pod is running on. */
    std::string cluster;

    /** The identifier of the node this pod is running on.  This will be
     *  either a hostname or the IPv4/IPv6 address of the node.
     */
    std::string node;
};

struct Struct_Wrap_startup_application
{
    /** The name of the app that is starting up. */
    std::string name;

    /** The version of the app that is starting up. */
    std::string version;
};

struct Struct_Wrap_exit_application
{
    /** The name of the app that is starting up. */
    std::string name;

    /** The version of the app that is starting up. */
    std::string version;
};

class Wrap_omni_carb_cloud
{
public:
    Wrap_omni_carb_cloud() = default;
    ~Wrap_omni_carb_cloud() = default;

    void startup_sendEvent(std::string cloud_link_id,
                           const Struct_Wrap_startup_ident& ident,
                           const Struct_Wrap_startup_application& application)
    {
        Schema_omni_carb_cloud_1_0::Struct_startup_ident ident_ = {};
        ident_.cluster = ident.cluster;
        ident_.node = ident.node;
        Schema_omni_carb_cloud_1_0::Struct_startup_application application_ = {};
        application_.name = application.name;
        application_.version = application.version;
        OMNI_STRUCTURED_LOG(Schema_omni_carb_cloud_1_0::startup, cloud_link_id, ident_, application_);
    }

    void heartbeat_sendEvent(std::string cloud_link_id)
    {
        OMNI_STRUCTURED_LOG(Schema_omni_carb_cloud_1_0::heartbeat, cloud_link_id);
    }

    void exit_sendEvent(std::string cloud_link_id, const Struct_Wrap_exit_application& application, bool exit_abnormally)
    {
        Schema_omni_carb_cloud_1_0::Struct_exit_application application_ = {};
        application_.name = application.name;
        application_.version = application.version;
        OMNI_STRUCTURED_LOG(Schema_omni_carb_cloud_1_0::exit, cloud_link_id, application_, exit_abnormally);
    }
};

inline void definePythonModule_omni_carb_cloud(py::module& m)
{
    using namespace omni::structuredlog;
    m.doc() = "bindings for structured log schema omni.carb.cloud";

    {
        py::class_<Struct_Wrap_startup_ident> bind_ident(m, "Struct_startup_ident");
        bind_ident.def(py::init<>());
        bind_ident.def_readwrite("cluster", &Struct_Wrap_startup_ident::cluster);
        bind_ident.def_readwrite("node", &Struct_Wrap_startup_ident::node);
    }

    {
        py::class_<Struct_Wrap_startup_application> bind_application(m, "Struct_startup_application");
        bind_application.def(py::init<>());
        bind_application.def_readwrite("name", &Struct_Wrap_startup_application::name);
        bind_application.def_readwrite("version", &Struct_Wrap_startup_application::version);
    }

    {
        py::class_<Struct_Wrap_exit_application> bind_application(m, "Struct_exit_application");
        bind_application.def(py::init<>());
        bind_application.def_readwrite("name", &Struct_Wrap_exit_application::name);
        bind_application.def_readwrite("version", &Struct_Wrap_exit_application::version);
    }

    // the main structured log class
    py::class_<Wrap_omni_carb_cloud>(m, "Schema_omni_carb_cloud_1_0")
        .def(py::init<>())
        .def("startup_sendEvent", &Wrap_omni_carb_cloud::startup_sendEvent, py::arg("cloud_link_id"), py::arg("ident"),
             py::arg("application"))
        .def("heartbeat_sendEvent", &Wrap_omni_carb_cloud::heartbeat_sendEvent, py::arg("cloud_link_id"))
        .def("exit_sendEvent", &Wrap_omni_carb_cloud::exit_sendEvent, py::arg("cloud_link_id"), py::arg("application"),
             py::arg("exit_abnormally"));
}

} // namespace telemetry
} // namespace omni
