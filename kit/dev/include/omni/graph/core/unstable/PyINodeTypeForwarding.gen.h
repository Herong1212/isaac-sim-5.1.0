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

inline auto bindINodeTypeForwarding(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::graph::core::unstable::INodeTypeForwarding_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::graph::core::unstable::INodeTypeForwarding_abi>>,
               omni::core::IObject>
        clsParent(m, "_INodeTypeForwarding");
    py::class_<omni::graph::core::unstable::INodeTypeForwarding,
               omni::python::detail::PyObjectPtr<omni::graph::core::unstable::INodeTypeForwarding>>
        cls(m, "INodeTypeForwarding", clsParent,
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
            auto tmp = omni::core::cast<omni::graph::core::unstable::INodeTypeForwarding>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::graph::core::unstable::INodeTypeForwarding>();
            if (!tmp)
            {
                throw std::runtime_error(
                    "unable to create omni::graph::core::unstable::INodeTypeForwarding instantiation");
            }
            return tmp;
        }));
    cls.def_property_readonly("forward_count", &omni::graph::core::unstable::INodeTypeForwarding::getForwardCount);
    cls.def(
        "define_forward",
        [](omni::graph::core::unstable::INodeTypeForwarding* self, const char* forwardName, int forwardVersion,
           const char* replacementName, int replacementVersion, const char* replacementExtensionId)
        {
            auto return_value = self->defineForward(
                forwardName, forwardVersion, replacementName, replacementVersion, replacementExtensionId);

            return return_value;
        },
        R"OMNI_BIND_RAW_(@brief Define a new node type forward.
It is allowed to have the same forwardName to be defined more than once, however the "forwardVersion" must be
different from any existing ones. Later "forwardVersion" numbers will supersede earlier ones in this case.
For example if you have these two forwards set up:
- OldNode,1 -> BetterNode,1,omni.better.extension
- OldNode,2 -> MuchBetterNode,1,omni.much_better.extension

then when version 1 of "OldNode" is requested it will treat it as if you requested "BetterNode", but when
versions 2 or later are requested it will instead treat it as if you requested "MuchBetterNode". These can be
chained together:
- OldNode,1 -> BetterNode,1,omni.better.extension
- BetterNode,1 -> MuchBetterNode,1,omni.much_better.extension

@param[in] forwardName Name to be replaced
@param[in] forwardVersion The first version of the forward name to be replaced
@param[in] replacementName Node type name that replaces the forwarded name
@param[in] replacementVersion Version of the node type that replaces the forwarded name
@param[in] extensionId Extension ID in which the replacement node type can be found
@return false if there was already an forward with the given name and initial version number)OMNI_BIND_RAW_",
        py::arg("forward_name"), py::arg("forward_version"), py::arg("replacement_name"),
        py::arg("replacement_version"), py::arg("replacement_extension_id"));
    cls.def(
        "remove_forward",
        [](omni::graph::core::unstable::INodeTypeForwarding* self, const char* forwardName, int forwardVersion)
        {
            auto return_value = self->removeForward(forwardName, forwardVersion);

            return return_value;
        },
        R"OMNI_BIND_RAW_(@brief Remove an existing node type forward.
Since an forwardName + forwardVersion combination is unique there is no need to pass in the replacement information.
Only the forward with the matching version is removed. Any others with the same name remain untouched.

@param[in] forwardName Forward to be removed
@param[in] forwardVersion The version at which the forward is to be removed
@return false if there was already an forward with the given name and initial version number)OMNI_BIND_RAW_",
        py::arg("forward_name"), py::arg("forward_version"));
    cls.def(
        "remove_forwarded_type",
        [](omni::graph::core::unstable::INodeTypeForwarding* self, const char* referencedName, int referencedVersion)
        {
            auto return_value = self->removeForwardedType(referencedName, referencedVersion);

            return return_value;
        },
        R"OMNI_BIND_RAW_(@brief Remove forwards referencing a given node type name.

@param[in] referencedName Forward to be removed
@param[in] referencedVersion The version at which the forward is to be removed
@return number of forwards to the given type that were removed)OMNI_BIND_RAW_",
        py::arg("referenced_name"), py::arg("referenced_version"));
    return omni::python::PyBind<omni::graph::core::unstable::INodeTypeForwarding>::bind(cls);
}
