// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IBase.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IBase.
#pragma once

#include <omni/core/IObject.h>

//! @defgroup groupOmniGraphExecInterfaces API Interfaces
//!
//! @brief Convenience interfaces backed by a stable ABI.

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

class IBase;
class IBase_abi;
class ExecutionTask;

//! Base class for all @ref omni::graph::exec objects.
//!
//! This interface provides cheap casting between interfaces without calling @ref omni::core::IObject::acquire().
//!
//! The Execution Framework has a rich hierarchy of interfaces.  Users are expected to extend this hierarchy to define
//! custom behavior for their part of the execution graph.  These extensions are likely to implement a suite of
//! interfaces, many of which will want to access the custom functionality provided by the other interfaces in the
//! suite.
//!
//! As an example, a user can create a custom @ref omni::graph::exec::unstable::IExecutor (i.e. `IMyExecutor`), that
//! would like to access data on their custom @ref omni::graph::exec::unstable::INode objects (i.e. `IMyNode`). The core
//! framework does not know about the `IMyNode` interface and will only pass @ref omni::graph::exec::unstable::INode
//! objects to `IMyExecutor`.  To access the custom `IMyNode` functionality, `IMyExecutor` can call @ref
//! omni::core::cast() on the the given @ref omni::graph::exec::unstable::INode objects to cast to `IMyNode`.  Unlike
//! `dynamic_cast` or `reinterpret_cast`, @ref omni::core::cast() is ABI-safe.
//!
//! Unfortunately, @ref omni::core::cast(), by contract, internally calls @ref omni::core::IObject::acquire() on the
//! returned pointer.  This cost is small, but can add up in hot code paths.
//!
//! The purpose of @ref omni::graph::exec::unstable::IBase is to provide a casting method that does not call @ref
//! omni::core::IObject::acquire().  This micro optimization helps in hot code paths, albeit with the added danger of
//! potentially mismanaging the object's ref count.
//!
//! The cheap casting this interface provides should be accessed with @ref omni::graph::exec::unstable::cast().  To
//! avoid mismanaging the object's ref count, it is recommended to *always* use `auto` when storing the results of
//! calling methods in the Execution Framework.
class IBase_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.exec.unstable.IBase")>
{
protected:
    //! Casts this object to the type described the the given id.
    //!
    //! Returns @c nullptr if the cast was not successful.
    //!
    //! Unlike @ref omni::core::IObject::cast(), this casting method does not call @ref omni::core::IObject::acquire().
    //!
    //! @thread_safety This method is thread safe.
    virtual void* castWithoutAcquire_abi(omni::core::TypeId id) noexcept = 0;

    //! Returns the number of different instances (this included) referencing the current object.
    //!
    //! @thread_safety This method is thread safe.
    virtual uint32_t getUseCount_abi() noexcept = 0;
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IBase.gen.h>


namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! @copydoc omni::graph::exec::unstable::IBase_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class IBase : public omni::core::Generated<omni::graph::exec::unstable::IBase_abi>
{
};

//! Casts the given pointer to the given interface (e.g. T).
//!
//! `nullptr` is accepted.
//!
//! Unlike @ref omni::core::cast(), this function does not call @ref omni::core::IObject::acquire() on the returned
//! pointer.
//!
//! @returns A valid pointer is returned if the given pointer implements the given interface.  Otherwise, `nullptr` is
//! returned.
template <typename T, typename U>
inline T* cast(U* ptr) noexcept
{
    static_assert(std::is_base_of<IBase, T>::value, "cast can only be used with classes that derive from IBase");
    if (ptr)
    {
        return reinterpret_cast<T*>(ptr->castWithoutAcquire(T::kTypeId));
    }
    else
    {
        return nullptr;
    }
}

//! Casts the given pointer to the given interface (e.g. T).
//!
//! `nullptr` is accepted.
//!
//! Unlike @ref omni::core::cast(), this function does not call @ref omni::core::IObject::acquire() on the returned
//! pointer.
//!
//! @returns A valid pointer is returned if the given pointer implements the given interface.  Otherwise, `nullptr` is
//! returned.
template <typename T, typename U>
inline T* cast(omni::core::ObjectParam<U> ptr) noexcept
{
    static_assert(std::is_base_of<IBase, T>::value, "cast can only be used with classes that derive from IBase");
    if (ptr)
    {
        return reinterpret_cast<T*>(ptr->castWithoutAcquire(T::kTypeId));
    }
    else
    {
        return nullptr;
    }
}

//! Casts the given pointer to the given interface (e.g. T).
//!
//! `nullptr` is accepted.
//!
//! Unlike @ref omni::core::cast(), this function does not call @ref omni::core::IObject::acquire() on the returned
//! pointer.
//!
//! @returns A valid pointer is returned if the given pointer implements the given interface.  Otherwise, `nullptr` is
//! returned.
template <typename T, typename U>
inline T* cast(omni::core::ObjectPtr<U> ptr) noexcept
{
    static_assert(std::is_base_of<IBase, T>::value, "cast can only be used with classes that derive from IBase");
    if (ptr)
    {
        return reinterpret_cast<T*>(ptr->castWithoutAcquire(T::kTypeId));
    }
    else
    {
        return nullptr;
    }
}

#ifndef DOXYGEN_BUILD
namespace details
{
template <typename T>
inline void* castWithoutAcquire(T* obj, omni::core::TypeId id) noexcept; // forward declaration
} // namespace details
#endif

//! Helper template for implementing the @ref castWithoutAcquire function for one or more interfaces.
template <typename T, typename... Rest>
struct ImplementsCastWithoutAcquire : public T, public Rest...
{
public:
    //! See @ref omni::core::IObject::cast.
    inline void* cast(omni::core::TypeId id) noexcept
    {
        // note: this implementation is needed to disambiguate which `cast` to call when using multiple inheritance. it
        // has zero-overhead.
        return static_cast<T*>(this)->cast(id);
    }

    //! See @ref omni::graph::exec::unstable::IBase_abi::castWithoutAcquire_abi.
    inline void* castWithoutAcquire(omni::core::TypeId id) noexcept
    {
        // note: this implementation is needed to disambiguate which `cast` to call when using multiple inheritance. it
        // has zero-overhead.
        return static_cast<T*>(this)->castWithoutAcquire(id);
    }

private:
    // given a type id, castImpl() check if the type id matches T's typeid.  if not, T's parent class type id is
    // checked. if T's parent class type id does not match, the grandparent class's type id is check.  this continues
    // until IObject's type id is checked.
    //
    // if no type id in T's inheritance chain match, the next interface in Rest is checked.
    //
    // it's expected the compiler can optimize away the recursion
    template <typename U, typename... Args>
    inline void* castImpl(omni::core::TypeId id) noexcept
    {
        // omni::core::detail::cast will march down the inheritance chain
        void* obj = omni::core::detail::cast<U>(this, id);
        if (nullptr == obj)
        {
            // check the next class (inheritance chain) provide in the inheritance list
            return castImpl<Args...>(id);
        }

        return obj;
    }

    // given a type id, castWithoutAcquireImpl() check if the type id matches T's typeid.  if not, T's parent class type
    // id is checked. if T's parent class type id does not match, the grandparent class's type id is check.  this
    // continues until IObject's type id is checked.
    //
    // if no type id in T's inheritance chain match, the next interface in Rest is checked.
    //
    // it's expected the compiler can optimize away the recursion
    template <typename U, typename... Args>
    inline void* castWithoutAcquireImpl(omni::core::TypeId id) noexcept
    {
        // details::castWithoutAcquire will march down the inheritance chain
        void* obj = details::castWithoutAcquire<U>(this, id);
        if (nullptr == obj)
        {
            // check the next class (inheritance chain) provide in the inheritance list
            return castWithoutAcquireImpl<Args...>(id);
        }

        return obj;
    }

    // this terminates walking across the types in the variadic template
    // LCOV_EXCL_START
    template <int = 0>
    inline void* castImpl(omni::core::TypeId) noexcept
    {
        return nullptr;
    }
    // LCOV_EXCL_STOP

    // this terminates walking across the types in the variadic template
    template <int = 0>
    inline void* castWithoutAcquireImpl(omni::core::TypeId) noexcept
    {
        return nullptr;
    }

protected:
    virtual ~ImplementsCastWithoutAcquire() noexcept = default;

    //! @copydoc omni::core::IObject_abi::cast_abi
    void* cast_abi(omni::core::TypeId id) noexcept override
    {
        return castImpl<T, Rest...>(id);
    }

    //! @copydoc omni::graph::exec::unstable::IBase_abi::castWithoutAcquire_abi
    void* castWithoutAcquire_abi(omni::core::TypeId id) noexcept override
    {
        return castWithoutAcquireImpl<T, Rest...>(id);
    }
};

//! Helper template for implementing one or more interfaces.
//!
//! Similar functionality as @ref omni::core::Implements but adds support for @ref ImplementsCastWithoutAcquire.
template <typename T, typename... Rest>
struct Implements : public ImplementsCastWithoutAcquire<T, Rest...>
{
public:
    //! @copydoc omni::core::IObject::acquire.
    inline void acquire() noexcept
    {
        // note: this implementation is needed to disambiguate which `cast` to call when using multiple inheritance. it
        // has zero-overhead.
        static_cast<T*>(this)->acquire();
    }

    //! @copydoc omni::core::IObject::release.
    inline void release() noexcept
    {
        // note: this implementation is needed to disambiguate which `cast` to call when using multiple inheritance. it
        // has zero-overhead.
        static_cast<T*>(this)->release();
    }

    //! @copydoc omni::graph::exec::unstable::IBase_abi::getUseCount_abi
    inline uint32_t getUseCount() noexcept
    {
        // note: this implementation is needed to disambiguate which `cast` to call when using multiple inheritance. it
        // has zero-overhead.
        return static_cast<T*>(this)->getUseCount();
    }

protected:
    std::atomic<uint32_t> m_refCount{ 1 }; //!< Reference count.

    virtual ~Implements() noexcept = default;

    //! @copydoc omni::core::IObject_abi::acquire_abi()
    void acquire_abi() noexcept override
    {
        m_refCount.fetch_add(1, std::memory_order_relaxed);
    }

    //! @copydoc omni::core::IObject_abi::release_abi()
    void release_abi() noexcept override
    {
        if (0 == m_refCount.fetch_sub(1, std::memory_order_release) - 1)
        {
            std::atomic_thread_fence(std::memory_order_acquire);
            delete this;
        }
    }

    //! Returns the number of different instances (this included) referencing the current object.
    uint32_t getUseCount_abi() noexcept override
    {
        return m_refCount;
    }
};

#ifndef DOXYGEN_BUILD
namespace details
{
//! Given a type, this function walks the inheritance chain for the type, checking if the id of the type matches the
//! given id.
//!
//! Implementation detail.  Do not call.
template <typename T>
inline void* castWithoutAcquire(T* obj, omni::core::TypeId id) noexcept
{
    if (T::kTypeId == id)
    {
        return obj;
    }
    else
    {
        return castWithoutAcquire<typename T::BaseType>(obj, id); // call cast again, but with the parent type
    }
}

//! Specialization of `castWithoutAcquire<T>(T*, TypeId)` for @ref omni::graph::exec::unstable::IBase. @ref
//! omni::graph::exec::unstable::IBase always terminates the recursive template since it does not have a base class.
//!
//! Implementation detail.  Do not call.
template <>
inline void* castWithoutAcquire<IBase>(IBase* obj, omni::core::TypeId id) noexcept
{
    if (IBase::kTypeId == id)
    {
        return obj;
    }
    else
    {
        return nullptr;
    }
}
} // namespace details
#endif

//! Helper utility to access the number of different instances referencing the given object.
//!
//! It does it without modifying the referencing count.
template <typename T>
inline uint32_t useCount(T* ptr) noexcept
{
    static_assert(std::is_base_of<IBase, T>::value, "useCount can only be used with classes that derive from IBase");
    if (ptr)
    {
        return ptr->getUseCount();
    }
    else
    {
        return 0;
    }
}

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IBase.gen.h>
