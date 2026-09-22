// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//!
//! @brief DLL Boundary safe memory management functions
#pragma once

#include "Defines.h"
#include "Types.h"
#include "cpp/Bit.h"
#include "detail/DeferredLoad.h"

//! Internal function used by all other allocation functions.
//!
//! This function is the entry point into `carb.dll`/`libcarb.so` for @ref carb::allocate(), @ref carb::deallocate(),
//! and @ref carb::reallocate(). There are four modes to this function:
//! - If @p p is `nullptr` and @p size is `0`, no action is taken and `nullptr` is returned.
//! - If @p p is not `nullptr` and @p size is `0`, the given pointer is deallocated and `nullptr` is returned.
//! - If @p p is `nullptr` and @p size is non-zero, memory of the requested @p size and alignment specified by @p align
//!   is allocated and returned. If an allocation error occurs, `nullptr` is returned.
//! - If @p p is not `nullptr` and @p size is non-zero, the memory is reallocated and copied (as if by `std::memcpy`) to
//!   the new memory block, which is returned. If @p p can be resized in situ, the same @p p value is returned. If an
//!   error occurs, `nullptr` is returned.
//!
//! @note Using this function requires explicitly linking with `carb.dll`/`libcarb.so` if @ref CARB_REQUIRE_LINKED is
//! `1`. Otherwise, the caller must ensure that `carb.dll`/`libcarb.so` is already loaded before calling this function.
//! Use in situations where the Carbonite Framework is already loaded (i.e. plugins) does not require explicitly linking
//! against Carbonite as this function will be found dynamically at runtime.
//!
//! @warning Do not call this function directly. Instead call @ref carb::allocate(), @ref carb::deallocate(), or
//! @ref carb::reallocate()
//!
//! @see carb::allocate() carb::reallocate() carb::deallocate()
//! @param p The pointer to re-allocate or free. May be `nullptr`. See explanation above.
//! @param size The requested size of the memory region in bytes. See explanation above.
//! @param align The requested alignment of the memory region in bytes. Must be a power of two. See explanation above.
//! @returns Allocated memory, or `nullptr` upon deallocation, or `nullptr` on allocation when an error occurs.
#if CARB_REQUIRE_LINKED
CARB_DYNAMICLINK void* carbReallocate(void* p, size_t size, size_t align);
#else
CARB_DYNAMICLINK void* carbReallocate(void* p, size_t size, size_t align) CARB_ATTRIBUTE(weak);
#endif


namespace carb
{
//! \cond DEV
namespace detail
{

CARB_DETAIL_DEFINE_DEFERRED_LOAD(getCarbReallocate, carbReallocate, (void* (*)(void*, size_t, size_t)));

} // namespace detail
//! \endcond

//! Allocates a block of memory.
//!
//! @note Any plugin (or the executable) may @ref allocate the memory and a different plugin (or the executable) may
//! @ref deallocate or @ref reallocate it.
//!
//! @note If carb.dll/libcarb.so is not loaded, this function will always return `nullptr`.
//!
//! @param size The size of the memory block requested, in bytes. Specifying '0' will return a valid pointer that
//! can be passed to @ref deallocate but cannot be used to store any information.
//! @param align The minimum alignment (in bytes) of the memory block requested. Must be a power of two. Values less
//!     than `sizeof(size_t)` are ignored. `0` indicates to use default system alignment (typically
//!     `2 * sizeof(void*)`).
//! @returns A non-`nullptr` memory block of @p size bytes with minimum alignment @p align. If an error occurred,
//!     or memory could not be allocated, `nullptr` is returned. The memory is not initialized.
inline void* allocate(size_t size, size_t align = 0) noexcept
{
    if (auto impl = detail::getCarbReallocate())
        return impl(nullptr, size, align);
    else
        return nullptr;
}

//! Deallocates a block of memory previously allocated with @ref allocate().
//!
//! @note Any plugin (or the executable) may @ref allocate the memory and a different plugin (or the executable) may
//! @ref deallocate or @ref reallocate it.
//!
//! @note If carb.dll/libcarb.so is not loaded, this function will silently do nothing. Since @ref allocate would have
//! returned `nullptr` in this case, this function should never be called.
//!
//! @param p The block of memory previously returned from @ref allocate() or @ref reallocate(), or `nullptr`.
inline void deallocate(void* p) noexcept
{
    if (p)
    {
        if (auto impl = detail::getCarbReallocate())
            impl(p, 0, 0);
    }
}

//! Reallocates a block of memory previously allocated with @ref allocate().
//!
//! This function changes the size of the memory block pointed to by @p p to @p size bytes with @p align alignment.
//! The contents are unchanged from the start of the memory block up to the minimum of the old size and @p size. If
//! @p size is larger than the old size, the added memory is not initialized. If @p p is `nullptr`, the call is
//! equivalent to `allocate(size, align)`; if @p size is `0` and @p p is not `nullptr`, the call is equivalent to
//! `deallocate(p)`. Unless @p p is `nullptr`, it must have been retrieved by an earlier call to @ref allocate() or
//! @ref reallocate(). If the memory region was moved in order to resize it, @p p will be freed as with `deallocate(p)`.
//!
//! @note Any plugin (or the executable) may @ref allocate the memory and a different plugin (or the executable) may
//! @ref deallocate or @ref reallocate it.
//!
//! @note If carb.dll/libcarb.so is not loaded, this function will always return @p p without side-effects.
//!
//! @param p The block of memory previously returned from @ref allocate() or @ref reallocate() if resizing is
//!     resizing is desired. If `nullptr` is passed as this parameter, the call behaves as if
//!     `allocate(size, align)` was called.
//! @param size The size of the memory block requested, in bytes. See above for further explanation.
//! @param align The minimum alignment (in bytes) of the memory block requested. Must be a power of two. Values less
//!     than `sizeof(size_t)` are ignored. Changing the alignment from a previous allocation is undefined behavior.
//!     `0` indicates to use default system alignment (typically `2 * sizeof(void*)`).
//! @returns A pointer to a block of memory of @p size bytes with minimum alignment @p align, unless an error
//!     occurs in which case `nullptr` is returned. If @p p is `nullptr` and @p size is `0` then `nullptr` is also
//!     returned.
inline void* reallocate(void* p, size_t size, size_t align = 0) noexcept
{
    if (auto impl = detail::getCarbReallocate())
        return impl(p, size, align);
    else
        return p;
}

/**
 * A class implementing the 'Allocator' C++ Named Requirement.
 *
 * This class is usable for C++ classes that require an allocator, such as `std::vector`.
 * @note This class requires dynamic or static linking to carb.dll/libcarb.so/libcarb.dylib in order to function.
 * @tparam T The type to allocate
 * @tparam Align The requested alignment as a `std::integral_constant<size_t, value>`. This must be a type in order to
 *   conform to the requirements of `std::allocator_traits` that template parameters be types. The constant value must
 *   be zero or a power of two. Zero indicates to use `T`'s required alignment.
 */
template <class T, class Align = std::integral_constant<size_t, 0>>
class Allocator
{
public:
    using pointer = T*; //!< pointer
    using const_pointer = const T*; //!< const_pointer
    using reference = T&; //!< reference
    using const_reference = const T&; //!< const_reference
    using void_pointer = void*; //!< void_pointer
    using const_void_pointer = const void*; //!< const_void_pointer
    using value_type = T; //!< value_type
    using size_type = std::size_t; //!< size_type
    using difference_type = std::ptrdiff_t; //!< difference_type

    static_assert(!Align::value || ::carb::cpp::has_single_bit(Align::value), "Must be a power of two");
    //! Alignment (non-standard)
    constexpr static size_t alignment = Align::value;

    //! A struct that allows determining an allocator for class `U` through the `other` type.
    template <class U>
    struct rebind
    {
        //! The type of `Allocator<U>`
        using other = Allocator<U, Align>;
    };

    //! Constructor
    constexpr Allocator() noexcept = default;

    //! Copy constructor
    constexpr Allocator(const Allocator&) noexcept = default;

    //! Copy-assign operator
    constexpr Allocator& operator=(const Allocator&) noexcept = default;

    //! Copy constructor
    template <class U, class UAlign>
    constexpr Allocator(const Allocator<U, UAlign>& other) noexcept
    {
        CARB_UNUSED(other);
    }

    //! Copy-assign operator
    template <class U, class UAlign>
    constexpr Allocator& operator=(const Allocator<U, UAlign>& other) noexcept
    {
        CARB_UNUSED(other);
        return *this;
    }

    //! Destructor
    ~Allocator() = default;

    //! Equality operator
    [[nodiscard]] constexpr bool operator==(const Allocator& other) const noexcept
    {
        CARB_UNUSED(other);
        return true;
    }

    //! Inequality operator
    [[nodiscard]] constexpr bool operator!=(const Allocator& other) const noexcept
    {
        CARB_UNUSED(other);
        return false;
    }

    /**
     * Allocates suitable storage for an array object of type `T[n]` and creates the array, but does not construct array
     * elements.
     *
     * If \ref alignment is suitable (that is, not less than the required alignment of `T`) it is used, otherwise the
     * required alignment of `T` is used.
     * @throws std::bad_alloc if exceptions are enabled (\ref CARB_EXCEPTIONS_ENABLED) and the underlying
     *   \ref carb::allocate() failed.
     * @param n The number of elements of `T` to allocate space for.
     * @returns A pointer to memory that can contain an array of type `T[n]`, but no array elements have been
     * constructed.
     */
    [[nodiscard]] pointer allocate(size_type n = 1)
    {
        auto align = ::carb_max(+alignment, alignof(T));
        auto p = ::carb::allocate(sizeof(T) * n, align);
#if CARB_EXCEPTIONS_ENABLED
        if (!p)
        {
            throw std::bad_alloc();
        }
#endif
        return pointer(p);
    }

    /**
     * Same as \ref allocate(size_type) but may use \p p (`nullptr` or a pointer obtained from \ref allocate()) to aid
     * locality.
     * @param n The number of elements of `T` to allocate space for.
     * @param p May be `nullptr` or a pointer obtained from \ref allocate(). If non-`nullptr`, \p p is returned.
     * @returns A pointer to memory that can contain an array of type `T[n]`, but no array elements have been
     * constructed.
     */
    [[nodiscard]] pointer allocate(size_type n, const_void_pointer p)
    {
        return p ? pointer(p) : allocate(n);
    }

    /**
     * Deallocates storage pointed to by `p`, which must be a value returned by a previous call to \ref allocate() that
     * has not been invalidated by an intervening call to `deallocate`.
     * @param p A value returned by a previous call to \ref allocate() and not previously passed to `deallocate`.
     * @param n Must be the same size value that was originally passed to \ref allocate().
     */
    void deallocate(pointer p, size_type n) noexcept /*strengthened*/
    {
        CARB_UNUSED(n);
        ::carb::deallocate(p);
    }

    /**
     * Returns the largest value that can be passed to \ref allocate().
     * @returns the largest value that can be passed to \ref allocate().
     */
    [[nodiscard]] size_type max_size() const noexcept
    {
        return size_type(-1);
    }

    /**
     * Constructs an object of type `X` in previously-allocated storage at the address pointed to by `p`, using `args`
     * as the constructor arguments.
     * @param p The pointer at which to construct.
     * @param args The constructor arguments.
     */
    template <class X, class... Args>
    void construct(X* const p, Args&&... args)
    {
        ::new (const_cast<void*>(static_cast<const volatile void*>(p))) X(std::forward<Args>(args)...);
    }

    /**
     * Destructs an object of type `X` pointed to by `p` but does not deallocate any storage.
     * @param p The pointer to an object of type `X` to destroy.
     */
    template <class X>
    void destroy(X* const p)
    {
        p->~X();
    }
};

/**
 * An object can inherit from this class in order to use Carbonite allocation functions for creation/deletion.
 */
template <size_t Align = 0>
class UseCarbAllocatorAligned
{
public:
    //! The alignment amount used by this allocator
    constexpr static size_t alignment = Align;

    //! \cond DEV
    static void* operator new(std::size_t count)
    {
        return carb::allocate(count, alignment);
    }
    static void* operator new[](std::size_t count)
    {
        return carb::allocate(count, alignment);
    }
    static void* operator new(std::size_t count, const std::nothrow_t&) noexcept
    {
        return carb::allocate(count, alignment);
    }
    static void* operator new[](std::size_t count, const std::nothrow_t&) noexcept
    {
        return carb::allocate(count, alignment);
    }
    static void* operator new(std::size_t count, void* placement) noexcept
    {
        CARB_UNUSED(count);
        return placement;
    }
    static void* operator new[](std::size_t count, void* placement) noexcept
    {
        CARB_UNUSED(count);
        return placement;
    }
    static void operator delete(void* ptr)
    {
        carb::deallocate(ptr);
    }
    static void operator delete[](void* ptr)
    {
        carb::deallocate(ptr);
    }
    static void operator delete(void* ptr, const std::nothrow_t&)
    {
        carb::deallocate(ptr);
    }
    static void operator delete[](void* ptr, const std::nothrow_t&)
    {
        carb::deallocate(ptr);
    }
    static void operator delete(void* ptr, void* placement)
    {
        CARB_ASSERT(ptr == placement);
        CARB_UNUSED(ptr, placement);
    }
    static void operator delete[](void* ptr, void* placement)
    {
        CARB_ASSERT(ptr == placement);
        CARB_UNUSED(ptr, placement);
    }
    static void* operator new(std::size_t count, std::align_val_t al)
    {
        return carb::allocate(count, ::carb_max(alignment, size_t(al)));
    }
    static void* operator new[](std::size_t count, std::align_val_t al)
    {
        return carb::allocate(count, ::carb_max(alignment, size_t(al)));
    }
    static void* operator new(std::size_t count, std::align_val_t al, const std::nothrow_t&)
    {
        return carb::allocate(count, ::carb_max(alignment, size_t(al)));
    }
    static void* operator new[](std::size_t count, std::align_val_t al, const std::nothrow_t&)
    {
        return carb::allocate(count, ::carb_max(alignment, size_t(al)));
    }
    static void operator delete(void* ptr, std::align_val_t)
    {
        carb::deallocate(ptr);
    }
    static void operator delete[](void* ptr, std::align_val_t)
    {
        carb::deallocate(ptr);
    }
    static void operator delete(void* ptr, std::align_val_t, const std::nothrow_t&)
    {
        carb::deallocate(ptr);
    }
    static void operator delete[](void* ptr, std::align_val_t, const std::nothrow_t&)
    {
        carb::deallocate(ptr);
    }
    //! \endcond
};

/** Allocated object deleter helper class.  This is suitable for use in various STL container
 *  classes that accept a functor responsible for deleting an object that was allocated using
 *  an allocation system other than new/delete.  This particular implementation ensures the
 *  object is destructed before deallocating its memory.
 */
template <class T>
class Deleter
{
public:
    /** Functor operator to destruct and deallocate an object that was allocated and constructed
     *  using one of the carb::allocate() family of functions.
     *
     *  @tparam T       The data type of the object to delete.
     *  @param[in] p    The object to be destroyed.
     */
    void operator()(T* p) noexcept
    {
        p->~T();
        carb::deallocate(p);
    }
};

/**
 * An object can inherit from this class in order to use Carbonite allocation functions for creation/deletion.
 */
using UseCarbAllocator = UseCarbAllocatorAligned<>;

} // namespace carb
