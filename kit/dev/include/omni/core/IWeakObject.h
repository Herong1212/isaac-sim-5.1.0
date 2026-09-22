// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IWeakObject.h
//!
//! @brief Defines @ref omni::core::IWeakObject.
#pragma once

#include <carb/cpp/Atomic.h> // atomic_ref
#include <carb/detail/DeferredLoad.h>
#include <omni/core/Api.h> // OMNI_API
#include <omni/core/Assert.h>
#include <omni/core/IObject.h>

#include <memory>

namespace omni
{
namespace core
{

class IWeakObject;
class IWeakObject_abi;
class IWeakObjectControlBlock;
class IWeakObjectControlBlock_abi;

//! Control block to maintain weak and strong reference counts for an object.
//!
//! The @ref IWeakObject interface supports the notion of "weak pointers".  Unlike "strong pointers" (e.g. @ref
//! ObjectPtr) weak pointers do not affect the pointee's reference count.  While this sounds like a raw pointer (and
//! possibly a bad idea), the magic of a weak pointer is that if the pointee's reference count goes to zero, the weak
//! pointer updates its internal pointer to `nullptr`.
//!
//! @ref IWeakObjectControlBlock is an ABI-safe object used to store a pointer to both the object and the object's
//! reference count (i.e. the "strong count").  This object additionally stores a "weak count", which is a count of
//! objects pointing to the @ref IWeakObjectControlBlock.
//!
//! Both @ref WeakPtr and @ref IWeakObject affect the "weak count".
//!
//! Only @ref ObjectPtr will affect the "strong count".
//!
//! Direct usage of this object should be avoided.  See @ref WeakPtr to learn how weak pointers are used in practice.
//!
//! **Advanced: Design Considerations**
//!
//! The design of ONI's weak pointers takes three main design considerations into account:
//!
//! - The user API should work similar to <a href="https://en.cppreference.com/w/cpp/memory/weak_ptr">std::weak_ptr</a>.
//!
//! - Enabling weak pointer support for an object should should not tank performance in hot code paths.
//!
//! - Weak pointers must be able to point to object's whose DLL has been unloaded from memory.
//!
//! Above, the final point has a strong affect on the implementation of weak pointers.  In particular, this object (i.e.
//! @ref IWeakObjectControlBlock).  Consider:
//!
//! - For a virtual function to be called successfully, the code implementing the virtual function must still be loaded.
//!
//! - An @ref IWeakObjectControlBlock may outlive the DLL that created the object to which it points.
//!
//! Rather than exposing a raw struct with the weak and strong counts (and associated inline code to manipulate them),
//! this interface is used to hide both the counts and the manipulation logic.  However, this introduces virtual
//! functions, which could potentially be unloaded.  To address the unloading problem, *carb.dll* provides
//! `omni::core::getOrCreateWeakObjectControlBlock()`.  This C-ABI returns an implementation of @ref
//! IWeakObjectControlBlock implemented within *carb.dll*. This effectively avoids the DLL unloading problem, since
//! *carb.dll* is considered a core dependency that cannot be unloaded and therefore the virtual function
//! implementations for @ref IWeakObjectControlBlock will always be loaded.
class IWeakObjectControlBlock_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.core.IWeakObjectControlBlock")>
{
protected:
    //! Returns a pointer to the object pointed to by this control block.  May return `nullptr`.
    //!
    //! If the object pointed to by this control block has a strong reference count of zero, `nullptr` is returned.
    //! Otherwise, @ref IObject::acquire() is called on the object before being returned.
    //!
    //! @thread_safety This method is thread safe.
    virtual IObject* getObject_abi() noexcept = 0;
};

//! Interface defining a contract for objects which support "weak"/non-owning references.
//!
//! This interface works tightly with @ref WeakPtr to implement weak pointers.  Users of weak pointers should focus on
//! @ref WeakPtr rather than this interface, as this interface is an implementation detail of the weak pointer ABI.
//!
//! Developers wishing to add weak pointer support to their objects must implement this interface, which is a
//! non-trivial task.  A default implementation is provided in @ref ImplementsWeak.
class IWeakObject_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.core.IWeakObject")>
{
protected:
    //! Returns a control block containing reference count information needed for the implementation of weak pointers.
    //!
    //! Users of weak pointers must never call this method.  Rather, they should focus on exclusively using @ref
    //! WeakPtr.
    //!
    //! Implementers of this method are encouraged to use the implementation found in @ref omni::core::ImplementsWeak.
    //!
    //! The returns pointer is never `nullptr`.
    //!
    //! The returned pointer will have @ref IObject::acquire() called on it before being returned.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null") IWeakObjectControlBlock* getWeakObjectControlBlock_abi() noexcept = 0;
};

} // namespace core
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/core/IWeakObject.gen.h>

namespace omni
{
namespace core
{

//! @copydoc omni::core::IWeakObjectControlBlock_abi
class IWeakObjectControlBlock : public omni::core::Generated<omni::core::IWeakObjectControlBlock_abi>
{
};

//! @copydoc omni::core::IWeakObject_abi
class IWeakObject : public omni::core::Generated<omni::core::IWeakObject_abi>
{
};

//! Weak pointer to ONI objects much like <a href="https://en.cppreference.com/w/cpp/memory/weak_ptr">std::weak_ptr</a>.
//!
//! The @ref IWeakObject interface support the notion of "weak pointers".  Unlike "strong pointers" (e.g. @ref
//! ObjectPtr) weak pointers do not affect the pointee's reference count.  While this sounds like a raw pointer (and
//! possibly a bad idea), the magic of a weak pointer is that if the pointee's reference count goes to zero, the weak
//! pointer updates its internal pointer to `nullptr`.
//!
//! Below are several practical use cases of weak pointers.
//!
//! **Breaking Reference Count Cycles**
//!
//! A reference count cycle happens when an object "A" contains an @ref ObjectPtr to object "B".  At this same time,
//! object "B" holds an @ref ObjectPtr to object "A".  Since each object increments the other's reference count, neither
//! is every destructed.  To break this cycle, one of the objects can hold a @ref WeakPtr to the other object.
//!
//! **Pointing to Objects Whose Code May Be Unloaded From Memory**
//!
//! Carbonite supports the notion of plugins that can be loaded, unloaded, and reloaded at runtime.  Often code from DLL
//! *X* holds an @ref ObjectPtr to code from DLL *Y*.  If the user unloads *Y*, and DLL *X* still wishes to use *Y*, the
//! application is likely to crash when DLL *X* attempts to access the unloaded code.
//!
//! Instead of storing an @ref ObjectPtr, a @ref WeakPtr can be used instead.  When DLL *X* wants to access the code in
//! DLL *Y*, @ref WeakPtr::getObjectPtr() is called, which converts the @ref WeakPtr into an @ref ObjectPtr.  Here, if
//! the underlying object's strong reference count is zero, the returned @ref ObjectPtr will point to `nullptr`.  DLL
//! *X* simply must check if the @ref ObjectPtr points to `nullptr` before using the pointer.
//!
//! Above, we make the assumption that DLL *Y* will either:
//!
//! - Refuse to unload as long as an object it produced has a non-zero strong reference count.
//!
//! - Will cleanup all external @ref ObjectPtr objects that hold a reference to an object produced by the DLL.  One way
//!   to implement this is for the plugin to allow callbacks to be registered with it that will be invoked when the DLL
//!   is about to unloaded.
//!
//! **Usage**
//!
//! Weak pointers should be used as follows:
//!
#ifdef CARB_DOC_BUILD
//! @snippet "source/tests/test.unit/omni.core/TestWeakPtr.cpp" carb-docs-weakptr-example-use
#endif

template <typename T>
class WeakPtr
{
public:
    //! Allow implicit conversion from nullptr to an WeakPtr.
    WeakPtr(std::nullptr_t = nullptr) noexcept
    {
    }

    //! Strong pointer to weak pointer conversion.
    WeakPtr(const omni::core::ObjectPtr<T>& strong) noexcept
    {
        if (strong)
        {
            m_ref = strong->getWeakObjectControlBlock();
        }
    }

    //! Raw pointer to weak pointer conversion.
    WeakPtr(T* strong) noexcept
    {
        if (strong)
        {
            m_ref = strong->getWeakObjectControlBlock();
        }
    }

    //! Copy constructor.
    WeakPtr(const WeakPtr& other) noexcept = default;

    //! Move constructor.
    WeakPtr(WeakPtr&& other) noexcept = default;

    ~WeakPtr() noexcept = default;

    //! Assignment operator.
    //!
    //! @thread_safety This method is not thread safe.
    WeakPtr& operator=(const WeakPtr& other) noexcept = default;

    //! Move assignment operator.
    //!
    //! @thread_safety This method is not thread safe.
    WeakPtr& operator=(WeakPtr&& other) noexcept = default;

    //! Returns an @ref omni::core::ObjectPtr to the object to which this weak pointer is pointing.
    //!
    //! The returned object will point to `nullptr` if there are no "strong" references to the underlying object.
    //! Otherwise, if a non-`nullptr` pointer is returned, the object will live at least as long as the returned @ref
    //! omni::core::ObjectPtr.
    //!
    //! To understand how/when to use weak pointers and this method, consult the class documentation for @ref
    //! omni::core::WeakPtr.
    //!
    //! Equivalent to @ref WeakPtr::lock().
    //!
    //! @thread_safety This method is not thread safe.
    omni::core::ObjectPtr<T> getObjectPtr() const noexcept
    {
        if (m_ref)
        {
            return m_ref->getObject().template as<T>();
        }

        return nullptr;
    }

    //! Returns an @ref omni::core::ObjectPtr to the object to which this weak pointer is pointing.
    //!
    //! The returned object will point to `nullptr` if there are no "strong" references to the underlying object.
    //! Otherwise, if a non-`nullptr` pointer is returned, the object will live at least as long as the returned @ref
    //! omni::core::ObjectPtr.
    //!
    //! To understand how/when to use weak pointers and this method, consult the class documentation for @ref
    //! omni::core::WeakPtr.
    //!
    //! Equivalent to @ref WeakPtr::getObjectPtr().
    //!
    //! @thread_safety This method is not thread safe.
    omni::core::ObjectPtr<T> lock() const noexcept
    {
        if (m_ref)
        {
            return m_ref->getObject().template as<T>();
        }

        return nullptr;
    }

private:
    ObjectPtr<IWeakObjectControlBlock> m_ref;
};

#ifndef DOXYGEN_BUILD
namespace detail
{

enum class WeakObjectControlBlockOp
{
    eIncrementStrong = 0,
    eDecrementStrong = 1,
    eDecrementWeak = 2,
    eGetStrongCount = 3, // for testing
    eGetWeakCount = 4, // for testing
    eHasControlBlock = 5, // for testing
};

} // namespace detail
#endif // DOXYGEN_BUILD

} // namespace core
} // namespace omni

// carb.dll C-ABI to hide the implementation details of a weak object's control block.  see IWeakObject's class docs for
// motivation.
#ifndef DOXYGEN_BUILD
#    if CARB_REQUIRE_LINKED
OMNI_API omni::core::IWeakObjectControlBlock* omniWeakObjectGetOrCreateControlBlock(omni::core::IObject* obj,
                                                                                    uintptr_t* refCountOrEncodedPtr);
OMNI_API uint32_t omniWeakObjectControlBlockOp(uintptr_t* refCountOrEncodedPtr, omni::core::WeakObjectControlBlockOp op);
#    else
OMNI_API omni::core::IWeakObjectControlBlock* omniWeakObjectGetOrCreateControlBlock(omni::core::IObject* obj,
                                                                                    uintptr_t* refCountOrEncodedPtr)
    CARB_ATTRIBUTE(weak);
OMNI_API uint32_t omniWeakObjectControlBlockOp(uintptr_t* refCountOrEncodedPtr,
                                               omni::core::detail::WeakObjectControlBlockOp op) CARB_ATTRIBUTE(weak);
#    endif
#endif // DOXYGEN_BUILD

namespace omni
{
namespace core
{

#ifndef DOXYGEN_BUILD
namespace detail
{

CARB_DETAIL_DEFINE_DEFERRED_LOAD(loadWeakObjectGetOrCreateControlBlock,
                                 omniWeakObjectGetOrCreateControlBlock,
                                 (omni::core::IWeakObjectControlBlock * (*)(omni::core::IObject*, uintptr_t*)));

//! Returns an implementation of @ref omni::core::IWeakObjectControlBlock provided by *carb.dll*.
//!
//! This method is an implementation detail and should not directly be called by users.
//!
//! The provided parameter, @p refCountOrPtr, is a pointer that points to a value.  That value can represent either:
//!
//! - An object's reference count (i.e. strong count).
//!
//! - An **encoded** pointer to an @ref omni::core::IWeakObjectControlBlock object.
//!
//! The purpose of this function is to determine if the value is either a reference count or an encoded pointer to the
//! control block.  If it is a reference count, an @ref omni::core::IWeakObjectControlBlock is allocated and the value
//! is updated to point to this new block.  If the value is already an encoded pointer to a control block, the control
//! block's weak reference count is incremented (i.e. @ref omni::core::IObject::acquire() is called on the *control
//! block*).
//!
//! In both cases, a pointer to the control block is returned.  It is up to the caller to ensure @ref
//! omni::core::IObject::release() is called on the returned pointer once the object is no longer in use.
//!
//! See @ref omni::core::IWeakObjectControlBlock for motivation as to why this function is needed.
//!
//! See @ref omni::core::WeakPtr and @ref omni::core::ImplementsWeak to understand how to use weak pointers and how to
//! enable weak pointer support in your objects.
//!
//! @thread_safety All operations on the given value are thread safe.
inline omni::core::IWeakObjectControlBlock* getOrCreateWeakObjectControlBlock(omni::core::IObject* obj,
                                                                              uintptr_t* refCountOrEncodedPtr)
{
    auto impl = detail::loadWeakObjectGetOrCreateControlBlock();
    OMNI_ASSERT(impl);
    return impl(obj, refCountOrEncodedPtr);
}

CARB_DETAIL_DEFINE_DEFERRED_LOAD(loadWeakObjectControlBlockOp,
                                 omniWeakObjectControlBlockOp,
                                 (uint32_t(*)(uintptr_t*, WeakObjectControlBlockOp)));


//! Increments the strong count of an object that is implemented with @ref omni::core::ImplementsWeak.
//!
//! This method is an implementation detail and should not directly be called by users.
//!
//! The provided parameter, @p refCountOrPtr, is a pointer that points to a value.  That value can represent either:
//!
//! - An object's reference count (i.e. strong count).
//!
//! - An **encoded** pointer to an @ref omni::core::IWeakObjectControlBlock object.
//!
//! This method determines which of the above cases is true and atomically increments the strong count.
//!
//! See @ref omni::core::IWeakObjectControlBlock for motivation as to why this function is needed.
//!
//! See @ref omni::core::WeakPtr and @ref omni::core::ImplementsWeak to understand how to use weak pointers and how to
//! enable weak pointer support in your objects.
//!
//! @thread_safety All operations on the given value are thread safe.
inline uint32_t incrementWeakObjectStrongCount(uintptr_t* refCountOrEncodedPtr)
{
    auto impl = detail::loadWeakObjectControlBlockOp();
    OMNI_ASSERT(impl);
    return impl(refCountOrEncodedPtr, WeakObjectControlBlockOp::eIncrementStrong);
}

//! Decrements the strong count of an object that is implemented with @ref omni::core::ImplementsWeak.
//!
//! This method is an implementation detail and should not directly be called by users.
//!
//! The provided parameter, @p refCountOrPtr, is a pointer that points to a value.  That value can represent either:
//!
//! - An object's reference count (i.e. strong count).
//!
//! - An **encoded** pointer to an @ref omni::core::IWeakObjectControlBlock object.
//!
//! This method determines which of the above cases is true and atomically decrements the strong count.
//!
//! See @ref omni::core::IWeakObjectControlBlock for motivation as to why this function is needed.
//!
//! See @ref omni::core::WeakPtr and @ref omni::core::ImplementsWeak to understand how to use weak pointers and how to
//! enable weak pointer support in your objects.
//!
//! @thread_safety All operations on the given value are thread safe.
inline uint32_t decrementWeakObjectStrongCount(uintptr_t* refCountOrEncodedPtr)
{
    auto impl = detail::loadWeakObjectControlBlockOp();
    OMNI_ASSERT(impl);
    return impl(refCountOrEncodedPtr, WeakObjectControlBlockOp::eDecrementStrong);
}

//! Decrements the weak count of an object that is implemented with @ref omni::core::ImplementsWeak.
//!
//! This method is an implementation detail and should not directly be called by users.
//!
//! The provided parameter, @p refCountOrPtr, is a pointer that points to a value.  That value can represent either:
//!
//! - An object's reference count (i.e. strong count).
//!
//! - An **encoded** pointer to an @ref omni::core::IWeakObjectControlBlock object.
//!
//! This method determines which of the above cases is true and atomically decrements the weak count.
//!
//! See @ref omni::core::IWeakObjectControlBlock for motivation as to why this function is needed.
//!
//! See @ref omni::core::WeakPtr and @ref omni::core::ImplementsWeak to understand how to use weak pointers and how to
//! enable weak pointer support in your objects.
//!
//! @thread_safety All operations on the given value are thread safe.
inline void decrementWeakObjectWeakCount(uintptr_t* refCountOrEncodedPtr)
{
    auto impl = detail::loadWeakObjectControlBlockOp();
    OMNI_ASSERT(impl);
    (void)impl(refCountOrEncodedPtr, WeakObjectControlBlockOp::eDecrementWeak);
}

//! Returns the strong count of an object that is implemented with @ref omni::core::ImplementsWeak.
//!
//! This method is an implementation detail and should not directly be called by users.
//!
//! The provided parameter, @p refCountOrPtr, is a pointer that points to a value.  That value can represent either:
//!
//! - An object's reference count (i.e. strong count).
//!
//! - An **encoded** pointer to an @ref omni::core::IWeakObjectControlBlock object.
//!
//! This method determines which of the above cases is true and returns the strong count.
//!
//! See @ref omni::core::IWeakObjectControlBlock for motivation as to why this function is needed.
//!
//! See @ref omni::core::WeakPtr and @ref omni::core::ImplementsWeak to understand how to use weak pointers and how to
//! enable weak pointer support in your objects.
//!
//! @thread_safety All operations on the given value are thread safe.
inline uint32_t getWeakObjectStrongCount(uintptr_t* refCountOrEncodedPtr)
{
    auto impl = detail::loadWeakObjectControlBlockOp();
    OMNI_ASSERT(impl);
    return impl(refCountOrEncodedPtr, WeakObjectControlBlockOp::eGetStrongCount);
}

//! Returns the weak count of an object that is implemented with @ref omni::core::ImplementsWeak.
//!
//! This method is an implementation detail and should not directly be called by users.
//!
//! The provided parameter, @p refCountOrPtr, is a pointer that points to a value.  That value can represent either:
//!
//! - An object's reference count (i.e. strong count).
//!
//! - An **encoded** pointer to an @ref omni::core::IWeakObjectControlBlock object.
//!
//! This method determines which of the above cases is true and returns the weak count.
//!
//! See @ref omni::core::IWeakObjectControlBlock for motivation as to why this function is needed.
//!
//! See @ref omni::core::WeakPtr and @ref omni::core::ImplementsWeak to understand how to use weak pointers and how to
//! enable weak pointer support in your objects.
//!
//! @thread_safety All operations on the given value are thread safe.
inline uint32_t getWeakObjectWeakCount(uintptr_t* refCountOrEncodedPtr)
{
    auto impl = detail::loadWeakObjectControlBlockOp();
    OMNI_ASSERT(impl);
    return impl(refCountOrEncodedPtr, WeakObjectControlBlockOp::eGetWeakCount);
}

//! Returns the `true` on object that is implemented with @ref omni::core::ImplementsWeak has had a weak pointer
//! attached to it.
//!
//! This method is an implementation detail and should not directly be called by users.
//!
//! The provided parameter, @p refCountOrPtr, is a pointer that points to a value.  That value can represent either:
//!
//! - An object's reference count (i.e. strong count).
//!
//! - An **encoded** pointer to an @ref omni::core::IWeakObjectControlBlock object.
//!
//! This method determines which of the above cases is true and return true if the value points to a control block.
//!
//! See @ref omni::core::IWeakObjectControlBlock for motivation as to why this function is needed.
//!
//! See @ref omni::core::WeakPtr and @ref omni::core::ImplementsWeak to understand how to use weak pointers and how to
//! enable weak pointer support in your objects.
//!
//! @thread_safety All operations on the given value are thread safe.
inline bool hasWeakObjectControlBlock(uintptr_t* refCountOrEncodedPtr)
{
    auto impl = detail::loadWeakObjectControlBlockOp();
    OMNI_ASSERT(impl);
    return (0 != impl(refCountOrEncodedPtr, WeakObjectControlBlockOp::eHasControlBlock));
}

} // namespace detail
#endif // DOXYGEN_BUILD

//! Helper template for implementing one or more interfaces that support weak pointers.
//!
//! This class has similar functionality as @ref Implements but adds support for @ref IWeakObject.
//!
//! As an example, consider the following interface:
//!
#ifdef CARB_DOC_BUILD
//! @snippet "source/tests/test.unit/omni.core/TestWeakPtr.cpp" carb-docs-weakptr-example-interface
#endif
//!
//! Note that the interface inherits from @ref IWeakObject rather than @ref IObject.
//!
//! To implement the interface above, @ref ImplementsWeak (i.e. this class) can be used as follows:
//!
#ifdef CARB_DOC_BUILD
//! @snippet "source/tests/test.unit/omni.core/TestWeakPtr.cpp" carb-docs-weakptr-example-class
#endif
template <typename T, typename... Rest>
struct ImplementsWeak : public ImplementsCast<T, Rest...>
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

    //! @copydoc omni::core::IWeakObject::getWeakObjectControlBlock_abi.
    inline ObjectPtr<IWeakObjectControlBlock> getWeakObjectControlBlock() noexcept
    {
        // note: this implementation is needed to disambiguate which `getWeakObjectControlBlock` to call when using
        // multiple inheritance. it has zero-overhead.
        return static_cast<T*>(this)->getWeakObjectControlBlock();
    }

protected:
    //! Destructor
    virtual ~ImplementsWeak() noexcept
    {
        // decrementWeakObjectWeakCount() will no-op if a control block has not been created
        omni::core::detail::decrementWeakObjectWeakCount(&m_refCountOrPtr);
    }

    //! @copydoc omni::core::IObject::acquire.
    virtual void acquire_abi() noexcept override
    {
        omni::core::detail::incrementWeakObjectStrongCount(&m_refCountOrPtr);
    }

    //! @copydoc omni::core::IObject::release.
    virtual void release_abi() noexcept override
    {
        if (0 == omni::core::detail::decrementWeakObjectStrongCount(&m_refCountOrPtr))
        {
            delete this;
        }
    }

    //! @copydoc omni::core::IWeakObject::getWeakObjectControlBlock
    virtual IWeakObjectControlBlock* getWeakObjectControlBlock_abi() noexcept override
    {
        return omni::core::detail::getOrCreateWeakObjectControlBlock(static_cast<T*>(this), &m_refCountOrPtr);
    }

#ifndef DOXYGEN_BUILD
    //! Return the strong reference count.  Should only be used for testing and debugging.
    uint32_t _getStrongCount() noexcept
    {
        return omni::core::detail::getWeakObjectStrongCount(&m_refCountOrPtr);
    }

    //! Return `true` if a weak object control block has been created for this object. Should only be used for testing
    //! and debugging.
    bool _hasWeakObjectControlBlock() noexcept
    {
        return omni::core::detail::hasWeakObjectControlBlock(&m_refCountOrPtr);
    }
#endif

private:
    // by default, this value stores the reference count of the object.
    //
    // however, when getWeakObjectControlBlock_abi() is called, this memory is repurposed to store a pointer to an
    // IWeakObjectControlBlock. it's the IWeakObjectControlBlock that will store both a strong and weak reference count
    // for this object.
    //
    // the pointer to the IWeakObjectControlBlock count is "encoded" so that we can easily determine if this memory is a
    // reference count or a pointer to an IWeakObjectControlBlock.
    //
    // the encoding of this pointer is an implementation detail and not exposed to the user.
    //
    // this value should be treated as opaque.
    uintptr_t m_refCountOrPtr{ 1 };
};

} // namespace core
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/core/IWeakObject.gen.h>
