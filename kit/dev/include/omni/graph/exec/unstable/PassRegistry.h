// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file PassRegistry.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IPassRegistry.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/IGlobalPass.h>
#include <omni/graph/exec/unstable/IPartitionPass.h>
#include <omni/graph/exec/unstable/IPassFactory.h>
#include <omni/graph/exec/unstable/IPassRegistry.h>
#include <omni/graph/exec/unstable/IPopulatePass.h>
#include <omni/graph/exec/unstable/Types.h>

#include <memory>
#include <string>
#include <vector>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Scoped object that registers a pass factory in its constructor and deregisters in the objects destructor.
//!
//! Useful for temporarily registering @ref IPassFactory, for example, in a unit test.
//!
//! When registering a pass in a plugin, rather than using this object, prefer using one of the pass registration macros
//! (e.g. @ref OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS()).  See @ref groupOmniGraphExecPassRegistration for a list of
//! registration macros.
class ScopedPassRegistration
{
public:
    //! Constructor.  Calls @ref IPassRegistry::registerPass() in the global pass registry.
    //!
    //! @p name must not be @c nullptr.
    //!
    //! Use helper macros like @ref OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS() rather than directly using this method. See
    //! @ref groupOmniGraphExecPassRegistration for a list of registration macros.
    //! Constructor.  Calls @ref IPassRegistry::registerPass().
    //!
    //! The given function should have the signature `IPass*(IGraphBuilder*)`.
    template <typename Fn>
    ScopedPassRegistration(
        PassType type, const char* name, Fn&& fn, const ConstName& nameToMatch = ConstName(), PassPriority priority = 0)
        : m_type(type), m_name(name), m_passId(0)
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(name);
        _register(createPassFactory(std::forward<Fn>(fn)).get(), nameToMatch, priority);
    }

    //! Constructor.  Calls @ref IPassRegistry::registerPass() in the global pass registry.
    //!
    //! @p name must not be @c nullptr.
    //!
    //! @p factory must not be @c nullptr.
    //!
    //! Use helper macros like @ref OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS() rather than directly using this method. See
    //! @ref groupOmniGraphExecPassRegistration for a list of registration macros.
    //! Constructor.  Calls @ref IPassRegistry::registerPass().
    ScopedPassRegistration(PassType type,
                           std::string&& name,
                           omni::core::ObjectParam<IPassFactory> factory,
                           const ConstName& nameToMatch = ConstName(),
                           PassPriority priority = 0)
        : m_type(type), m_name(std::move(name)), m_passId(0)
    {
        _register(factory.get(), nameToMatch, priority);
    }

    //! Destructor.  Calls @ref IPassRegistry::deregisterPass().
    ~ScopedPassRegistration() noexcept
    {
        if (m_registry)
        {
            m_registry->deregisterPass(m_type, m_passId);
        }
    }

private:
    CARB_PREVENT_COPY_AND_MOVE(ScopedPassRegistration);

    void _register(IPassFactory* factory, const ConstName& nameToMatch, PassPriority priority)
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(factory);
        m_registry = getPassRegistry();
        if (m_registry)
        {
            m_passId = getPassRegistry()->registerPass(m_type, m_name.c_str(), factory, nameToMatch, priority);
        }
    }

    IPassRegistry* m_registry;
    PassType m_type;
    std::string m_name;
    uint32_t m_passId;
};

#ifndef DOXYGEN_BUILD
namespace detail
{

struct PassRegistrationInfo
{
    PassType type;
    std::string name;
    PassFactoryPtr factory;
    ConstName nameToMatch;
    PassPriority priority;

    PassRegistrationInfo(
        PassType type_, const char* name_, PassFactoryPtr&& factory_, ConstName&& nameToMatch_, PassPriority priority_)
        : type(type_), name(name_), factory(std::move(factory_)), nameToMatch(std::move(nameToMatch_)), priority(priority_)
    {
    }
};

//! Return the per module (e.g. DLL) list of passes that should be registered.
//!
//! This function is an implementation detail and should not be directly used.  Rather, populate this list with one of
//! the following macros:
//!
//! - @ref OMNI_GRAPH_EXEC_REGISTER_PASS()
//!
//! - @ref OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS()
//!
//! This list is cleared after the module developer calls @ref registerModulePasses().
inline std::vector<PassRegistrationInfo>& getModulePassesToRegister() noexcept
{
    static std::vector<PassRegistrationInfo> sPasses;
    return sPasses;
}

//! Return the per module (e.g. DLL) list of passes that should be deregistered.
//!
//! This function is an implementation detail and should not be directly used.
//!
//! This list is populated by @ref registerModulePasses().
inline std::vector<std::unique_ptr<ScopedPassRegistration>>& getModulePassesToDeregister() noexcept
{
    static std::vector<std::unique_ptr<ScopedPassRegistration>> sPasses;
    return sPasses;
}

} // namespace detail

#    define OMNI_GRAPH_EXEC_CONCAT_(a_, b_) a_##b_
#    define OMNI_GRAPH_EXEC_CONCAT(a_, b_) OMNI_GRAPH_EXEC_CONCAT_(a_, b_)
#    define OMNI_GRAPH_EXEC_REGISTER_PASS_(type_, class_, var_, nameToMatch, priority_)                                \
        static auto var_ = []()                                                                                        \
        {                                                                                                              \
            omni::graph::exec::unstable::detail::getModulePassesToRegister().emplace_back(                             \
                type_, #class_,                                                                                        \
                omni::graph::exec::unstable::createPassFactory([](omni::graph::exec::unstable::IGraphBuilder* b)       \
                                                               { return class_::create(b); }),                         \
                omni::graph::exec::unstable::ConstName(nameToMatch), priority_);                                       \
            return 0;                                                                                                  \
        }()
#endif

//! @defgroup groupOmniGraphExecPassRegistration Pass Registration
//!
//! @brief Macros to register a plugin's passes.
//!
//! Pass registration macros should be called at global scope (not within a function/method).
//!
//! In order to avoid accidentally registering a pass twice, it is recommended to call registration macros from a *.cpp*
//! file rather than a *.h* file.
//!
//! Registration macros only add the pass to a list of passes to register.  This is useful if you have passes defined in
//! several **.cpp** files in your module.  It is up to the module developer to call @ref registerModulePasses()  and
//! @ref deregisterModulePasses() to perform the actual registration.
//!
//! See @ref  groupOmniGraphExecPasses for more pass related functionality.
//!
//! @ingroup  groupOmniGraphExecPasses

//! Adds an @ref omni::graph::exec::unstable::IPass to a list to be registered at the module's (i.e.g DLL) startup.
//!
//! @param type_   A @ref omni::graph::exec::unstable::PassType.
//!
//! @param class_  An implementation of @ref omni::graph::exec::unstable::IPass.
//!
//! This macro should be called at global scope (not within a function/method).
//!
//! In order to avoid accidentally registering a pass twice, it is recommended to call this macro from a *.cpp* file
//! rather than a *.h* file.
//!
//! This macro only adds the pass to a list of passes to register.  This is useful if you have passes defined in several
//! **.cpp** files in your module.  It is up to the module developer to call @ref
//! omni::graph::exec::unstable::registerModulePasses()  and
//! @ref omni::graph::exec::unstable::deregisterModulePasses() to perform the actual registration.
//!
//! See @ref groupOmniGraphExecPassRegistration for more information about pass registration.
//!
//! @ingroup groupOmniGraphExecPassRegistration
#define OMNI_GRAPH_EXEC_REGISTER_PASS(type_, class_)                                                                   \
    OMNI_GRAPH_EXEC_REGISTER_PASS_(type_, class_, OMNI_GRAPH_EXEC_CONCAT(sRegisterPass, __LINE__), "", 0)

//! Adds an @ref omni::graph::exec::unstable::IPopulatePass to a list to be registered as type
//! @ref omni::graph::exec::unstable::PassType::ePopulate at the module's (i.e.g DLL) startup.
//!
//! @param class_  An implementation of @ref omni::graph::exec::unstable::IPopulatePass.
//!
//! @param defNameToPopulate_  The name of the definition, @ref omni::graph::exec::unstable::IDef, this pass should
//! populate.  An example would be "OmniGraph".
//!
//! This macro should be called at global scope (not within a function/method).
//!
//! In order to avoid accidentally registering a pass twice, it is recommended to call this macro from a *.cpp* file
//! rather than a *.h* file.
//!
//! See @ref groupOmniGraphExecPassRegistration for more information about pass registration.
//!
//! @ingroup groupOmniGraphExecPassRegistration
#define OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS(class_, defNameToPopulate_)                                             \
    static_assert(std::is_base_of<omni::graph::exec::unstable::IPopulatePass, class_>::value,                          \
                  "Registering a class that doesn't implement IPopulatePass");                                         \
    OMNI_GRAPH_EXEC_REGISTER_PASS_(omni::graph::exec::unstable::PassType::ePopulate, class_,                           \
                                   OMNI_GRAPH_EXEC_CONCAT(sRegisterPass, __LINE__), defNameToPopulate_, 0)

//! Adds an @ref omni::graph::exec::unstable::IPartitionPass to a list to be registered as type
//! @ref omni::graph::exec::unstable::PassType::ePartitioning at the module's (i.e.g DLL) startup.
//!
//! @param class_  An implementation of @ref omni::graph::exec::unstable::IPartitionPass.
//!
//! @param priority_  @ref omni::graph::exec::unstable::PassPriority used to resolve conflicts between passes
//!
//! This macro should be called at global scope (not within a function/method).
//!
//! In order to avoid accidentally registering a pass twice, it is recommended to call this macro from a *.cpp* file
//! rather than a *.h* file.
//!
//! See @ref groupOmniGraphExecPassRegistration for more information about pass registration.
//!
//! @ingroup groupOmniGraphExecPassRegistration
#define OMNI_GRAPH_EXEC_REGISTER_PARTITION_PASS(class_, priority_)                                                     \
    static_assert(std::is_base_of<omni::graph::exec::unstable::IPartitionPass, class_>::value,                         \
                  "Registering a class that doesn't implement IPartitionPass");                                        \
    OMNI_GRAPH_EXEC_REGISTER_PASS_(omni::graph::exec::unstable::PassType::ePartitioning, class_,                       \
                                   OMNI_GRAPH_EXEC_CONCAT(sRegisterPass, __LINE__), "", priority_)

//! Adds an @ref omni::graph::exec::unstable::IGlobalPass to a list to be registered as type
//! @ref omni::graph::exec::unstable::PassType::eGlobal at the module's (i.e.g DLL) startup.
//!
//! @param class_  An implementation of @ref omni::graph::exec::unstable::IGlobalPass.
//!
//! This macro should be called at global scope (not within a function/method).
//!
//! In order to avoid accidentally registering a pass twice, it is recommended to call this macro from a *.cpp* file
//! rather than a *.h* file.
//!
//! See @ref groupOmniGraphExecPassRegistration for more information about pass registration.
//!
//! @ingroup groupOmniGraphExecPassRegistration
#define OMNI_GRAPH_EXEC_REGISTER_GLOBAL_PASS(class_)                                                                   \
    static_assert(std::is_base_of<omni::graph::exec::unstable::IGlobalPass, class_>::value,                            \
                  "Registering a class that doesn't implement IGlobalPass");                                           \
    OMNI_GRAPH_EXEC_REGISTER_PASS_(omni::graph::exec::unstable::PassType::eGlobal, class_,                             \
                                   OMNI_GRAPH_EXEC_CONCAT(sRegisterPass, __LINE__), "", 0)

//! Registers the module's @ref omni::graph::exec::unstable::IPass factories with @ref
//! omni::graph::exec::unstable::IPassRegistry.
//!
//! This function should be called in the module's function registered with omni::core::OMNI_MODULE_ON_MODULE_STARTED().
//! This is usually called @c onStarted().
//!
//! When developing a Kit extension, prefer calling @c OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED() rather than this function.
//!
//! See @ref groupOmniGraphExecPassRegistration for more information about pass registration.
//!
//! @thread_safety This function is not thread safe.
//!
//! @ingroup groupOmniGraphExecPassRegistration
inline void registerModulePasses() noexcept
{
    auto& toRegister = detail::getModulePassesToRegister();
    auto& toDeregister = detail::getModulePassesToDeregister();
    for (auto& pass : toRegister)
    {
        toDeregister.emplace_back(std::make_unique<ScopedPassRegistration>(
            pass.type, std::move(pass.name), std::move(pass.factory), std::move(pass.nameToMatch), pass.priority));
    }
    toRegister.clear();
}

//! Deregisters the module's @ref omni::graph::exec::unstable::IPass factories with @ref IPassRegistry.
//!
//! Failure to call this function may lead to crashes during program shutdown.
//!
//! This function should be called in the module's function registered with omni::core::OMNI_MODULE_ON_MODULE_UNLOAD().
//! This is usually called @c onUnload().
//!
//! When developing a Kit extension, prefer calling @c OMNI_KIT_EXEC_CORE_ON_MODULE_UNLOAD() rather than this function.
//!
//! See @ref groupOmniGraphExecPassRegistration for more information about pass registration.
//!
//! @thread_safety This function is not thread safe.
//!
//! @ingroup groupOmniGraphExecPassRegistration
inline void deregisterModulePasses() noexcept
{
    detail::getModulePassesToDeregister().clear();
}

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
