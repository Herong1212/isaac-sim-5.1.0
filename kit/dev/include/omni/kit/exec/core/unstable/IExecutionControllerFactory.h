// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IExecutionControllerFactory.h
//!
//! @brief Defines @ref omni::kit::exec::core::unstable::IExecutionControllerFactory.
#pragma once

#include <omni/core/ITypeFactory.h>
#include <omni/graph/exec/unstable/IBase.h>

#include <type_traits>
#include <vector>

namespace omni
{

namespace usd
{

class IUsdMutex;

}

namespace kit
{
namespace exec
{
namespace core
{
namespace unstable
{

// forward declarations needed by interface declaration
class IClearCallback;
class IExecutionController;
class IExecutionControllerFactory;
class IExecutionControllerFactory_abi;

//! Factory for creating instances of @ref omni::kit::exec::core::unstable::IExecutionController.
//!
//! This interface also stores the "default" @ref omni::kit::exec::core::unstable::IExecutionController, which is
//! associated with Kit's "default" @c UsdContext.
//!
//! The factory is a singleton.  Access the singleton with @ref
//! omni::kit::exec::core::unstable::getExecutionControllerFactory().
class IExecutionControllerFactory_abi
    : public omni::core::Inherits<graph::exec::unstable::IBase,
                                  OMNI_TYPE_ID("omni.kit.exec.core.unstable.IExecutionControllerFactory")>
{
protected:
    //! Creates an @ref omni::kit::exec::core::unstable::IExecutionController.
    //!
    //! The given name should match the name of the @c UsdContext.
    //!
    //! The USD mutex should match the mutex of the @c UsdContext.
    //!
    //! The returned controller will have @ref omni::core::IObject::acquire() called on it.
    //!
    //! @p name must not be @c nullptr.
    //!
    //! @thread_safety This method is not thread safe.
    virtual IExecutionController* createExecutionController_abi(OMNI_ATTR("not_null, c_str") const char* name,
                                                                OMNI_ATTR("in, out")
                                                                    omni::usd::IUsdMutex* const usdMutex) noexcept = 0;

    //! Sets the "default" @ref omni::kit::exec::core::unstable::IExecutionController which should be owned by Kit's
    //! "default" @c UsdContext.
    //!
    //! The given controller must not be @c nullptr.
    //!
    //! This method must not be called if a default controller has already been set.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void setDefaultExecutionController_abi(OMNI_ATTR("not_null") IExecutionController* controller) noexcept = 0;

    //! Returns the "default" @ref omni::kit::exec::core::unstable::IExecutionController associated with the "default"
    //! @c UsdContext.
    //!
    //! The returned pointer may be @c nullptr.
    //!
    //! Prefer calling @ref getDefaultExecutionController() rather than directly calling this method.
    //!
    //! The returned controller will have @ref omni::core::IObject::acquire() called on it.
    //!
    //! @thread_safety This method is thread safe.
    virtual IExecutionController* getDefaultExecutionController_abi() noexcept = 0;

    //! Attempts to release references to all objects when unloading DLLs.
    //!
    //! State managed by controllers may store references to objects emanating from many DLLs.  As long as a controller
    //! stores a reference to an object, it will not be destructed.  This causes a problem when unloading DLLs. If a
    //! controller's graph/context stores a reference to an object created by "foo.dll" and "foo.dll" is unloaded, when
    //! the controller later releases its reference to the object, the object's @c release() method will call into
    //! unloaded code, causing a crash.
    //!
    //! The fix for this disastrous scenario is ensure that no outstanding references to objects created in "foo.dll"
    //! are present in the process.  This method attempts to do just that by releasing *all* references stored within
    //! all controllers/graphs/contexts.
    //!
    //! A plugin may choose to store references to execution framework objects originating from other modules.  In such
    //! a case, the plugin can be notified when this @c clear() method is called by invoking @ref
    //! omni::kit::exec::core::unstable::addClearCallback() when the plugin/module is loaded.
    //!
    //! Upon completion of this method, pointers to controllers created by this factory will remain valid, though
    //! references within the controllers to objects potentially created by other DLLs will have been released.
    //!
    //! The @p moduleHash is an implementation detail that aids in achieving more granular object cleanup based on the
    //! .dll/.so that's getting unloaded.
    //!
    //! @thread_safety This method is not thread safe and should be called by a single thread at a time.
    virtual void clear_abi(const uint64_t moduleHash) noexcept = 0;

    //! Adds a callback that will be invoked when @ref
    //! omni::kit::exec::core::unstable::IExecutionControllerFactory::clear() is called.
    //!
    //! @ref omni::kit::exec::core::unstable::IExecutionControllerFactory::clear() is called when a .dll/.so providing
    //! execution framework functionality is unloaded (e.g. a plugin that provides a pass or node definition). The
    //! purpose of the given callback is to provide the plugin calling this method an opportunity to remove pointers to
    //! code that may be unloaded.  For example, OmniGraph uses this callback to remove any @ref
    //! omni::graph::exec::unstable::IDef pointers in its plugins.
    //!
    //! Do not call this method directly.  Rather, call @ref OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED in either a plugin's
    //! @ref carbOnPluginStartup or @c onStarted.
    //!
    //! The given @p callback must not be @c nullptr.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void addClearCallback_abi(OMNI_ATTR("not_null") IClearCallback* callback) noexcept = 0;

    //! Removes a callback registered with @ref
    //! omni::kit::exec::core::unstable::IExecutionControllerFactory::addClearCallback.
    //!
    //! If @p callback is @c nullptr or was not registered, this function silently fails.
    //!
    //! This method should not be explicitly called, rather call @ref OMNI_KIT_EXEC_CORE_ON_MODULE_UNLOAD during
    //! plugin/module shutdown.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void removeClearCallback_abi(IClearCallback* callback) noexcept = 0;

    //! Generate a unique number that's tied to the factory singleton instance.
    //!
    //! Used as an implementation detail to identify modules (i.e. .dll/.so) that utilize the kit-EF integration layer.
    //!
    //! This method is not meant to be called explicitly by users.
    virtual const uint64_t _generateUniqueHash_abi() noexcept = 0;
};

//! Smart pointer for @ref omni::kit::exec::core::unstable::IExecutionControllerFactory.
using ExecutionControllerFactoryPtr = omni::core::ObjectPtr<IExecutionControllerFactory>;

//! Returns the singleton @ref omni::kit::exec::core::unstable::IExecutionControllerFactory.
//!
//! May return @c nullptr if the *omni.kit.exec.core* extension has not been loaded.
//!
//! The returned pointer does not have @ref omni::core::IObject::acquire() called on it.
inline IExecutionControllerFactory* getExecutionControllerFactory() noexcept;

//! Returns the "default" @ref omni::kit::exec::core::unstable::IExecutionController associated with the "default" @c
//! UsdContext.
//!
//! The returned pointer may be @c nullptr.
inline omni::core::ObjectPtr<IExecutionController> getDefaultExecutionController() noexcept;

//! Convenience inlined method for determining whether the "default"
//! @ref omni::kit::exec::core::unstable::IExecutionController associated with the "default" @c UsdContext.
//! is currently executing.
//!
//! Useful for scheduling post-process tasks.
inline const bool isDefaultExecutionControllerInExecute() noexcept;

//! Adds a callback that will be invoked when @ref omni::kit::exec::core::unstable::IExecutionControllerFactory::clear()
//! is called.
//!
//! @ref omni::kit::exec::core::unstable::IExecutionControllerFactory::clear() is called when a .dll/.so providing
//! execution framework functionality is unloaded (e.g. a plugin that provides a pass or node definition). The purpose
//! of the given callback is to provide the plugin calling @ref addClearCallback an opportunity to remove pointers to
//! code that may be unloaded.  For example, OmniGraph uses this callback to remove any @ref
//! omni::graph::exec::unstable::IDef pointers in its plugins.
//!
//! Do not call this method directly.  Rather, call @ref OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED in either a plugin's
//! @ref carbOnPluginStartup or @c onStarted.
//!
//! The callback will be removed/unregistered by @ref OMNI_KIT_EXEC_CORE_ON_MODULE_UNLOAD.
template <typename Fn>
inline void addClearCallback(Fn&& fn) noexcept;

//! Removes any @ref omni::kit::exec::core::unstable::IExecutionControllerFactory clear callback registered by the
//! plugin/module. This method should not be explicitly called, rather call @ref OMNI_KIT_EXEC_CORE_ON_MODULE_UNLOAD
//! during plugin/module shutdown.
inline void removeClearCallbacks() noexcept;

#ifndef DOXYGEN_BUILD
namespace detail
{

inline std::vector<IClearCallback*>& getClearCallbacks() noexcept
{
    // we store raw pointers rather than ObjectPtr to avoid static destruction issues
    static std::vector<IClearCallback*> sCallbacks;
    return sCallbacks;
}

//! Obtain a unique number that identifies the current module, which is stored as a globally-accessible (within the
//! .dll/.so) static variable.
inline const uint64_t getModuleHash() noexcept;

} // namespace detail
#endif // DOXYGEN_BUILD

} // namespace unstable
} // namespace core
} // namespace exec
} // namespace kit
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/kit/exec/core/unstable/IExecutionControllerFactory.gen.h>

//! @copydoc omni::kit::exec::core::unstable::IExecutionControllerFactory_abi
//!
//! @ingroup groupOmniKitExecCoreInterfaces
class omni::kit::exec::core::unstable::IExecutionControllerFactory
    : public omni::core::Generated<omni::kit::exec::core::unstable::IExecutionControllerFactory_abi>
{
public:
    //! Alternate implementation for creating an @ref omni::kit::exec::core::unstable::IExecutionController
    //! _without_ an associated USD context mutex.
    //!
    //! See @ref omni::kit::exec::core::unstable::IExecutionControllerFactory::createExecutionController_abi()
    //! for further details.
    inline omni::core::ObjectPtr<omni::kit::exec::core::unstable::IExecutionController> createExecutionController(
        const char* name) noexcept;

    //! @copydoc omni::kit::exec::core::unstable::IExecutionControllerFactory::createExecutionController_abi()
    inline omni::core::ObjectPtr<omni::kit::exec::core::unstable::IExecutionController> createExecutionController(
        const char* name, omni::usd::IUsdMutex& usdMutex) noexcept;
};

inline omni::kit::exec::core::unstable::IExecutionControllerFactory* omni::kit::exec::core::unstable::
    getExecutionControllerFactory() noexcept
{
    // createType() always calls acquire() and returns an ObjectPtr to make sure release() is called. we don't want to
    // hold a ref here to avoid static destruction issues. here we allow the returned ObjectPtr to destruct (after
    // calling get()) to release our ref. we know the DLL in which the singleton was created is maintaining a ref and
    // will keep the singleton alive for the lifetime of the DLL.
    static auto sSingleton = omni::core::createType<IExecutionControllerFactory>().get();
    return sSingleton;
}

inline omni::core::ObjectPtr<omni::kit::exec::core::unstable::IExecutionController> omni::kit::exec::core::unstable::
    getDefaultExecutionController() noexcept
{
    return getExecutionControllerFactory()->getDefaultExecutionController();
}

inline const uint64_t omni::kit::exec::core::unstable::detail::getModuleHash() noexcept
{
    static std::vector<uint64_t> sUniqueHash;
    if (sUniqueHash.empty())
    {
        sUniqueHash.emplace_back(getExecutionControllerFactory()->_generateUniqueHash());
    }
    return sUniqueHash.front();
}

// additional headers needed for API implementation
#include <omni/core/IObject.h>
#include <omni/kit/exec/core/unstable/IClearCallback.h>
#include <omni/kit/exec/core/unstable/IExecutionController.h>

inline const bool omni::kit::exec::core::unstable::isDefaultExecutionControllerInExecute() noexcept
{
    const auto defaultExecutionController = getExecutionControllerFactory()->getDefaultExecutionController();
    return (defaultExecutionController && defaultExecutionController->getContext()->inExecute());
}

template <typename Fn>
inline void omni::kit::exec::core::unstable::addClearCallback(Fn&& fn) noexcept
{
    class Callback : public graph::exec::unstable::Implements<IClearCallback>
    {
    public:
        Callback(Fn&& fn) noexcept : m_fn(std::move(fn))
        {
        }

    protected:
        void onClear_abi() noexcept override
        {
            m_fn();
        }

        Fn m_fn;
    };

    Callback* callback = new Callback(std::forward<Fn>(fn));
    detail::getClearCallbacks().emplace_back(callback);
    getExecutionControllerFactory()->addClearCallback(callback);
}

inline void omni::kit::exec::core::unstable::removeClearCallbacks() noexcept
{
    auto factory = getExecutionControllerFactory();
    auto& callbacks = detail::getClearCallbacks();
    while (!callbacks.empty())
    {
        auto callback = callbacks.back();
        factory->removeClearCallback(callback);
        callback->release();
        callbacks.pop_back();
    }
}

inline omni::core::ObjectPtr<omni::kit::exec::core::unstable::IExecutionController> omni::kit::exec::core::unstable::
    IExecutionControllerFactory::createExecutionController(const char* name) noexcept
{
    return omni::core::steal(createExecutionController_abi(name, nullptr));
}

inline omni::core::ObjectPtr<omni::kit::exec::core::unstable::IExecutionController> omni::kit::exec::core::unstable::
    IExecutionControllerFactory::createExecutionController(const char* name, omni::usd::IUsdMutex& usdMutex) noexcept
{
    return omni::core::steal(createExecutionController_abi(name, &usdMutex));
}

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/kit/exec/core/unstable/IExecutionControllerFactory.gen.h>
