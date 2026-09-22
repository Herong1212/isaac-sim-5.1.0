// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IPassTypeRegistry.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IPassTypeRegistry.
#pragma once

#include <omni/graph/exec/unstable/ConstName.h>
#include <omni/graph/exec/unstable/ElementAt.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Types.h>

#include <cstring>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class IPassFactory;
class IPassTypeRegistry;
class IPassTypeRegistry_abi;

//! ABI-safe struct to hold registered @ref omni::graph::exec::unstable::IPassFactory objects.
//!
//! @ref PassTypeRegistryEntry can be safely passed by pointer or value across the ABI.
struct PassTypeRegistryEntry
{
    //! The ID for the pass that uniquely identifies it. Useful
    //! for pass deregistration.
    uint32_t id;

    //! The name of the pass type.
    const char* name;

    //! Factory interface for creating an instance of the pass.
    //!
    //! This struct does not acquire this pointer.
    //!
    //! This pointer is never @c nullptr.
    IPassFactory* factory;

    //! Some passes (e.g. populate passes) desire to affect only a subset of the nodes and/or definitions in a graph.
    //! This field is used to specify the name of the node/definitions the pass wishes to affect.
    //!
    //! The meaning of this field is pass type dependent. Many passes ignore this field.
    //!
    //! This pointer is never @c nullptr.
    const ConstName* nameToMatch;

    //! Some pass types (e.g. partition passes) are designed such that only a single pass should affect an entity. When
    //! multiple passes wish to affect an entity, this priority value can be used to resolve the conflict. The meaning
    //! of the priority value is pass type specific. Many passes ignore this value.
    PassPriority priority;

    //! Reserved padding space.
    uint32_t reserved;
};

#ifndef DOXYGEN_BUILD // macros called in namespaces seem to upset doxygen
OMNI_STATIC_ASSERT_CAN_BE_PASSED_BY_VALUE_IN_ABI(PassTypeRegistryEntry);
static_assert(CARB_OFFSETOF2(PassTypeRegistryEntry, id) == 0, "unexpected id offset");
static_assert(CARB_OFFSETOF2(PassTypeRegistryEntry, name) == 8, "unexpected name offset");
static_assert(CARB_OFFSETOF2(PassTypeRegistryEntry, factory) == 16, "unexpected factory offset");
static_assert(CARB_OFFSETOF2(PassTypeRegistryEntry, nameToMatch) == 24, "unexpected hash offset");
static_assert(CARB_OFFSETOF2(PassTypeRegistryEntry, priority) == 32, "unexpected hash offset");
static_assert(40 == sizeof(PassTypeRegistryEntry), "PassTypeRegistryEntry is an unexpected size");
#endif

//! @ref omni::graph::exec::unstable::IPassFactory registry for a particular @ref omni::graph::exec::unstable::PassType.
//!
//! Instances of this object are generally accessed via @ref
//! omni::graph::exec::unstable::IPassRegistry::getPassTypeRegistry() by @ref omni::graph::exec::unstable::IPassPipeline
//! during graph construction.
//!
//! See @rstref{Pass Concepts <ef_pass_concepts>} for an in-depth guide on how passes are used during graph
//! construction.
//!
//! See @ref groupOmniGraphExecPassRegistration for more information about pass registration.
//!
//! See @ref groupOmniGraphExecPasses for more pass related functionality.
class IPassTypeRegistry_abi : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                                          OMNI_TYPE_ID("omni.graph.exec.unstable.IPassTypeRegistry")>
{
protected:
    //! Returns the number of registered passes.
    //!
    //! @thread_safety This method is not thread safe.
    virtual uint64_t getPassCount_abi() noexcept = 0;

    //! Returns the information about the registered pass at the given index.
    //!
    //! @p index must not be greater than the number of registered passes for this type.
    //!
    //! The memory to which the returned entry points will remain valid until the next time a pass is either added or
    //! removed from this type registry.
    //!
    //! @thread_safety This method is not thread safe.
    virtual PassTypeRegistryEntry getPassAt_abi(uint64_t index) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IPassTypeRegistry.
using PassTypeRegistryPtr = omni::core::ObjectPtr<IPassTypeRegistry>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IPassTypeRegistry.gen.h>

//! @copydoc omni::graph::exec::unstable::IPassTypeRegistry_abi
//!
//! @ingroup groupOmniGraphExecPassRegistration groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IPassTypeRegistry
    : public omni::core::Generated<omni::graph::exec::unstable::IPassTypeRegistry_abi>
{
public:
    //! Implementation detail to access registry ABI
    struct GetPass
    {
        //! Access element at a given index
        static void getAt(IPassTypeRegistry* owner, uint64_t index, PassTypeRegistryEntry* out)
        {
            *out = owner->getPassAt(index);
        }

        //! Returns element count
        static uint64_t getCount(IPassTypeRegistry* owner)
        {
            return owner->getPassCount();
        }
    };

    //! Implementation detail that wraps index-based node access with iterators.
    using Passes = detail::ElementAt<IPassTypeRegistry, PassTypeRegistryEntry, GetPass>;

    //! Returns an object that allows the list of passes to be iterated over (i.e. using range-based for loops).
    //!
    //! The returned iterator is valid as long as this pass type registry is not mutated (e.g. a pass is added or
    //! removed from the registry).
    Passes getPasses() noexcept
    {
        return Passes(this);
    }
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IPassFactory.h>

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IPassTypeRegistry.gen.h>
