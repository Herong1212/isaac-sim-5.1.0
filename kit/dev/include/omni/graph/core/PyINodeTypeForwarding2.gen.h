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

inline auto bindINodeTypeForwarding2(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::INodeTypeForwarding2_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::INodeTypeForwarding2_abi>>,
               omni::core::Api<omni::graph::core::unstable::INodeTypeForwarding_abi>>
        clsParent(m, "_INodeTypeForwarding2");
    py::class_<omni::graph::core::INodeTypeForwarding2,
               omni::python::detail::PyObjectPtr<omni::graph::core::INodeTypeForwarding2>>
        cls(m, "INodeTypeForwarding2", clsParent,
            R"OMNI_BIND_RAW_(@brief Interface that creates a forward on a request for a node type to a different node type

There are a couple of different common use cases for needing a forward:
- Node type gets renamed
- Node type moves from one extension to another

The node type forward specifies the unique node type name so if extension omni.my.extension has a node whose type
is specified as "MyNode" then the forward must be from "omni.my.extension.MyNode".

The forwarding is version-based as well, where the version is a minimum number required for forwarding, the usual
node version update mechanism not withstanding. For example, if you set up a forward from "omni.nodes.MyNode" version
2 to "omni.my_nodes.MyNode" version 3 then any larger version number is forwarded to the same location:
- omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
- omni.nodes.MyNode(3) -> omni.my_nodes.MyNode(3)
- omni.nodes.MyNode(4) -> omni.my_nodes.MyNode(3)

The forwards can also have multiple versions forwarding to different locations, so if on top of the above forward
you also add a forward from "omni.nodes.MyNode" version 3 to "omni.new_nodes.MyNode" version 4 then these become
the example forward locations:
- omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
- omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
- omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4)

Version numbers lower than the first forward are left as-is
- omni.nodes.MyNode(1) -> omni.nodes.MyNode(1)

@note The usual mechanism of calling updateVersionNumber on a node is only applied after a forward so in the above
      cases requesting omni.nodes.MyNode(2) does not call updateVersionNumber(1,2) on your omni.nodes.MyNode
      implementation.

Node type forwards are associative, so if A forwards to B and B forwards to C then when you request A you get C.
Adding a new forward from omni.my_nodes.MyNode(3) to omni.new_nodes.MyNode(2) above yields this forwarding:
- omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3) -> omni.new_nodes.MyNode(2)
- omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
- omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4))OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::graph::core::INodeTypeForwarding2>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::INodeTypeForwarding2>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::graph::core::INodeTypeForwarding2 instantiation");
            }
            return tmp;
        }));
    cls.def(
        "inspect",
        [](omni::graph::core::INodeTypeForwarding2* self, omni::inspect::IInspector* inspector)
        {
            auto return_value = self->inspect(inspector);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Runs the inspector on the scheduling hints.

@param[in] inspector The inspector class
@return true if the inspection ran successfully, false if the inspection type is not supported)OMNI_BIND_RAW_",
        py::arg("inspector"));
    return omni::python::PyBind<omni::graph::core::INodeTypeForwarding2>::bind(cls);
}
