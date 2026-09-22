// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief HandleDatabase definition file.
#pragma once

#include "../Defines.h"

#include "../container/LocklessQueue.h"
#include "../cpp/Bit.h"
#include "../cpp/Optional.h"
#include "../logging/Log.h"

#include <algorithm>
#include <atomic>
#include <cstdint>
#include <memory>
#include <mutex>
#include <stack>
#include <vector>

CARB_IGNOREWARNING_MSC_WITH_PUSH(4201) // nonstandard extension used: nameless struct/union

namespace carb
{
namespace extras
{

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
struct HandleRef;

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
struct ConstHandleRef;

//! Bitwise state values returned by \ref carb::extras::HandleDatabase::getSharedState().
enum SharedState
{
    //! The handle or mapped entry is not shared. If \ref HandleDatabase::markShared() is always called before a
    //! handle can be used then this value guarantees that the calling thread has sole access to the mapped entry.
    eNotShared = 0,

    //! The handle or mapped entry is shared by having a reference count over one.
    eReferenced = 1 << 0,

    //! The handle for a mapped entry is marked as shared. Once marked as 'shared' in this fashion, the handle remains
    //! 'shared' for its lifetime. Marking as 'shared' means that a handle is known outside of the system that created
    //! it and can be used by any thread to increase the reference count.
    eMarkedShared = 1 << 1,
};

/**
 * Provides an OS-style mapping of a Handle to a Resource.
 *
 * Essentially HandleDatabase is a fast thread-safe reference-counted associative container.
 *
 * @thread_safety Unless otherwise mentioned, HandleDatabase functions may be called simultaneously from multiple
 * threads.
 *
 * A given Handle value is typically never reused, however, it is possible for a handle value to be reused if billions
 * of handles are requested.
 *
 * The HandleDatabase can store at most `(2^31)-1` items, or 2,147,483,647 items simultaneously, provided the memory
 * exists to support it.
 *
 * @par Implementation Details
 * @parblock
 * HandleDatabase achieves its speed and thread-safety by having a fixed-size base array (`m_bucket`) where the first
 * index is a initial size, and each subsequent entry doubles the previous entry.
 * These base arrays are never freed, simplifying thread safety and allowing HandleDatabase to be mostly lockless.
 * This array-of-arrays forms a non-contiguous indexable array where the base array and offset can be computed from an
 * index value (see `indexToBucketAndOffset`).
 *
 * See below for how the handle bits are used.
 * @endparblock
 *
 * @par Handles and sharing
 * @parblock
 * Handles are essentially a non-counted weak referencing system where only the number of strong references are known.
 * The number of weak references are not tracked. Once the number of strong references drops to zero, the handle is
 * destroyed and will no longer be able to be used to access a mapped object.
 *
 * The number of strong references belonging to a handle or mapped object can be obtained with
 * \ref HandleDatabase::debugGetRefCount().
 *
 * However, HandleDatabase is thread-safe. In a multi-threaded environment the number of references can be changed by
 * other threads at any time. This makes the reference count stale by the time it is read by the calling thread. For
 * this reason it is not advised to use the number of reference counts in a multithreaded environment.
 *
 * It can still be useful to know what the shared-state of a handle is. To determine this, call
 * \ref HandleDatabase::getSharedState() which returns a bitwise value of \ref SharedState. When created, handles are
 * considered to be \ref SharedState::eNotShared and have a strong reference count of one. Whenever the reference count
 * is above one, \ref HandleDatabase::getSharedState() will report \ref SharedState::eReferenced. If the handle was ever
 * used to increment the reference count, or if the handle is explicitly marked as 'shared' with
 * \ref HandleDatabase::markShared(), then \ref HandleDatabase::getSharedState() will include the
 * \ref SharedState::eMarkedShared bit as well. This bit means that the handle is valid and in use, so the number of
 * weak references is not known. The \ref SharedState::eMarkedShared bit remains for the lifetime of the handle.
 * @endparblock
 *
 * @par Bit allocation
 * @parblock
 * HandleDatabase always uses a 64-bit type as a key and opaquely controls the bits within those keys. The bits are
 * divided up into two contiguous categories: \a Index and \a Lifecycle. For type safety, it is recommended to use an
 * opaque pointer or a `CARB_STRONGTYPE` as a key since the value of the key is meaningless outside of
 * HandleDatabase.
 *
 * The total number of bits between \a Index and \a Lifecycle may not exceed 64. However, a minimum of 16 bits can be
 * used. In this case only the least-significant bits of the handle will be used and the unused bits will be ignored,
 * allowing an application to use these bits for other purposes.
 *
 * The \a Index is used as a random access locator, such as an array index. By default the `IndexBits` template
 * parameter is 32, meaning that 32 bits are allocated for \a Index. The maximum number of items is given by
 * `2 ^ IndexBits - 1` and is available by \ref getMaxSize(). The minimum number of bits for \a Index is 8, and the
 * maximum is 32.
 *
 * The \a Lifecycle is used as a check on the ownership of a handle. Every time an index is reused, the \a Lifecycle is
 * incremented by one. Whenever a mapped value is found via its handle, the \a Lifecycle of the handle is checked
 * against the current index's lifecycle value. If the value doesn't match current, the handle is stale or invalid and
 * cannot be used to access the current index. When the \a Lifecycle value rolls over, an internal bit is permanently
 * set to 1 indicating that all handle values that refer to the given index were previously valid (which enables
 * functionality for \ref handleWasValid()). This \a rollover bit is taken from the bits allocated for \a Lifecycle, but
 * is not present in the lifecycle bits of the handle returned to the user. When the rollover bit is set, this means
 * that handle values can then be re-used. Re-using handles increases the possibility of a stale handle being used to
 * access a current value. By default, 32 bits are allocated for \a Lifecycle, meaning that an index must be reused 2^31
 * times before a handle will be re-used. A lower number of bits increases the likelihood of reusing a handle. The
 * minimum number of bits for \a Lifecycle is 8, and the maximum is 32.
 *
 * The \a Index portion is in the least significant bits of the handle, and the \a Lifecycle portion in the more
 * significant portion above that. The remaining most-significant bits (if any) may be used by the application.
 * @endparblock
 *
 * @tparam Mapped The "value" type that is associated with a Handle.
 * @tparam Handle The "key" type. Must be an unsigned integer or pointer type and 64-bit. This is an opaque type that
 * cannot be dereferenced.
 * @tparam Allocator The allocator that will be used to allocate memory. Must be capable of allocating large contiguous
 * blocks of memory.
 * @tparam IndexBits The number of bits to use for indexing. Must be at least 8 and may not exceed 32. Default is 32.
 * @tparam LifecycleBits The number of bits to use for handle lifecycle. Must be at least 8 and may not exceed 32. One
 *   of the bits allocated here is reserved as a rollover flag. Default is 32.
 */
template <class Mapped, class Handle, class Allocator = std::allocator<Mapped>, size_t IndexBits = 32, size_t LifecycleBits = 32>
class CARB_VIZ HandleDatabase
{
public:
    // Check conditions on bits
    static_assert(IndexBits >= 8, "IndexBits must be at least 8");
    static_assert(IndexBits <= 32, "IndexBits must not exceed 32");
    static_assert(LifecycleBits >= 8, "LifecycleBits must be at least 8");
    static_assert(LifecycleBits <= 32, "LifecycleBits must not exceed 32");
    static_assert((IndexBits + LifecycleBits) <= 64, "(IndexBits + LifecycleBits) must not exceed 64");

    //! The number of bits used for index and given by the class template parameter `IndexBits`.
    constexpr static size_t kIndexBits = IndexBits;

    //! The number of bits used for lifecycle and given by the class template parameter `LifecycleBits`.
    constexpr static size_t kLifecycleBits = LifecycleBits;

    //! An alias to Mapped; the mapped value type.
    using MappedType = Mapped;

    //! An alias to Handle; the key type used to associate a mapped value type.
    using HandleType = Handle;

    //! An alias to Allocator; the allocator used to allocate memory.
    using AllocatorType = Allocator;

    //! An alias to the HandleRef for this HandleDatabase.
    using HandleRefType = HandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>;

    //! An alias to the ConstHandleRef for this HandleDatabase.
    using ConstHandleRefType = ConstHandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>;

    //! @a Deprecated: Use HandleRefType instead.
    using scoped_handle_ref_type = HandleRefType;

    /**
     * Constructor.
     * @thread_safety The constructor must complete in a single thread before any other functions may be called on
     * `*this`.
     */
    constexpr HandleDatabase() noexcept;

    /**
     * Destructor.
     * @thread_safety All other functions on `*this` must be finished before the destructor can be called.
     */
    ~HandleDatabase();

    /**
     * Checks to see if a handle is valid or was ever valid in the past.
     * @param handle The Handle to check.
     * @returns `true` if a @p handle is currently valid or was valid in the past and has since been released; `false`
     * otherwise.
     */
    bool handleWasValid(Handle handle) const;

    /**
     * Checks to see if a handle is currently valid.
     * @param handle The Handle to check.
     * @returns `true` if a @p handle is currently valid; `false` otherwise.
     */
    bool handleIsValid(Handle handle) const;

    /**
     * Creates a new Mapped type with the given arguments.
     * @param args The arguments to pass to the Mapped constructor.
     * @returns A `std::pair` of the Handle that can uniquely identify the new Mapped type, and a pointer to the newly
     * constructed Mapped type.
     */
    template <class... Args>
    std::pair<Handle, Mapped*> createHandle(Args&&... args);

    /**
     * Attempts to find the Mapped type represented by @p handle.
     * @thread_safety Not thread-safe as the Mapped type could be destroyed if another thread calls release().
     * @warning This function should not be used unless the thread calling it holds a reference count. It is recommended
     *   instead to use \ref makeScopedRef() to validate the handle and add a reference.
     * @param handle A handle previously returned from createHandle(). Invalid or previously-valid handles will merely
     * result in a `nullptr` result without an assert or any other side-effects.
     * @returns A pointer to a valid Mapped type if the handle was valid; `nullptr` otherwise.
     */
    [[nodiscard]] Mapped* getValueFromHandle(Handle handle) const;

    /**
     * Retrieves the Handle representing @p mapped.
     * @param mapped A pointer to the mapped type. If `nullptr`, \p mapped has been fully released, or \p mapped is not
     *   owned by `*this`, behavior is undefined.
     * @returns The Handle representing @p mapped.
     */
    [[nodiscard]] Handle getHandleFromValue(const Mapped* mapped) const;

    /**
     * Atomically attempts to add a reference for the given Handle.
     * @note This operation, if successful, implicitly marks a handle as shared as via \ref markShared().
     * @param handle A handle previously returned from createHandle(). Invalid or previously-valid handles will merely
     * result in a `nullptr` result without an assert or any other side-effects.
     * @param outRefCount (Optional) If non-`nullptr`, will receive the new reference count provided that the function
     *   returns a non-`nullptr` value. If the function returns `nullptr`, this value is unchanged. Note however that
     *   reference counts can be changed by other threads, so this value may be stale before it is read by the calling
     *   thread.
     * @returns A pointer to a valid Mapped type if a reference could be added; `nullptr` otherwise.
     */
    Mapped* tryAddRef(Handle handle, size_t* outRefCount = nullptr);

    /**
     * Atomically adds a reference for the given Handle; fatal if @p handle is invalid.
     * @note This operation implicitly marks a handle as shared as via \ref markShared().
     * @param handle A valid handle previously returned from createHandle(). Invalid or previously-valid handles will
     * result in `std::terminate()` being called.
     * @returns The new reference count. Note however that reference counts can be changed by other threads, so this
     *   value may be stale before it is read by the calling thread.
     */
    size_t addRef(Handle handle);

    /**
     * Atomically adds a reference for the Handle representing @p mapped.
     * @note This operation **does not** mark the handle representing @p mapped as shared per \ref markShared().
     * @param mapped A pointer to the mapped type. If `nullptr`, \p mapped has been fully released, or \p mapped is not
     *   owned by `*this`, behavior is undefined.
     * @returns The new reference count. Note however that reference counts can be changed by other threads, so this
     *   value may be stale before it is read by the calling thread.
     */
    size_t addRef(Mapped* mapped);

    /**
     * Atomically releases a reference for the given Handle, potentially freeing the associated Mapped type.
     * @param handle A valid handle previously returned from createHandle(). Invalid or previously-valid handles will
     * result in an assert in Debug builds, but return `false` with no side effects in Release builds.
     * @returns `true` if the last reference was released and @p handle is no longer valid; `false` if Handle is not
     * valid or is previously-valid or a non-final reference was released.
     */
    bool release(Handle handle);

    /**
     * Atomically releases a reference for the Handle representing @p mapped.
     * @param mapped A pointer to the mapped type. If `nullptr`, \p mapped has been fully released, or \p mapped is not
     *   owned by `*this`, behavior is undefined.
     * @returns `true` if the last reference was released and @p mapped is no longer valid; `false` if a reference other
     * than the last reference was released.
     */
    bool release(Mapped* mapped);

    /**
     * Atomically releases a reference if and only if it's the last reference.
     * @param handle A valid handle previously returned from createHandle(). Invalid or previously-valid handles will
     * result in an assert in Debug builds, but return `false` with no side effects in Release builds.
     * @returns `true` if the last reference was released and @p handle is no longer valid; `false` otherwise.
     */
    bool releaseIfLastRef(Handle handle);

    /**
     * Atomically releases a reference if and only if it's the last reference.
     * @param mapped A pointer to the mapped type. If `nullptr`, \p mapped has been fully released, or \p mapped is not
     *   owned by `*this`, behavior is undefined.
     * @returns `true` if the last reference was released and @p mapped is no longer valid; `false` otherwise.
     */
    bool releaseIfLastRef(Mapped* mapped);

    /**
     * Attempts to atomically add a reference to @p handle, and returns a HandleRef to @p handle.
     * @param handle A handle previously returned from createHandle(). Invalid or previously-valid handles will merely
     * result in an empty \ref HandleRef result without an assert or any other side-effects.
     * @returns If \ref tryAddRef() would return a valid Mapped type for @p handle, then a \ref HandleRef that manages
     *   the reference is returned; otherwise an empty \ref HandleRef is returned.
     */
    HandleRefType makeScopedRef(Handle handle);

    /**
     * Attempts to atomically add a reference to @p handle, and returns a ConstHandleRef to @p handle.
     * @param handle A handle previously returned from createHandle(). Invalid or previously-valid handles will merely
     * result in an empty \ref ConstHandleRef result without an assert or any other side-effects.
     * @returns If \ref tryAddRef() would return a valid Mapped type for @p handle, then a \ref ConstHandleRef that
     *   manages the reference is returned; otherwise an empty \ref ConstHandleRef is returned.
     */
    ConstHandleRefType makeScopedRef(Handle handle) const;

    /**
     * Calls the provided `Func` invocable object for each valid handle and its associated mapped type.
     * @thread_safety The `Mapped*` passed to \p f is not safe to use if any other thread would be calling
     * releaseIfLastRef() or release() to release the last reference of a Handle. In these situations it is instead
     * recommended to try to add a reference to the `Handle` passed to \p f in order to assure validity.
     * @param f An invocable object with signature `void(Handle, Mapped*)`. Note that there also exists a version of
     *   `forEachHandle` that can accept `bool(Handle, Mapped*)` and can early out. Technically any non-bool return type
     *   is allowed but any return values are ignored. It is highly recommended to ignore the `Mapped*` unless
     *   it is guaranteed that no other threads may be modifying the `HandleDatabase`, in which case it is recommend to
     *   instead try to add a reference to the `Handle` in order to assure validity.
     */
    template <class Func CARB_NO_DOC(
        ,
        std::enable_if_t<!std::is_same<bool, decltype(std::declval<Func>()(std::declval<Handle>(), std::declval<Mapped*>()))>::value,
                         bool> = false)>
    void forEachHandle(Func&& f) const
    {
        for (uint32_t i = 0; i != kBuckets; ++i)
        {
            // We are done once we encounter a null pointer
            HandleData* data = getDbIndex(i, std::memory_order_acquire);
            if (!data)
                break;

            uint32_t const kBucketSize = getBucketSize(i);
            uint32_t const kBucketOffset = getBucketOffset(i);
            for (uint32_t j = 0; j != kBucketSize; ++j)
            {
                Metadata meta = data[j].metadata.load(std::memory_order_acquire);
                if ((meta.refCount & kRefMask) != 0)
                {
                    // Valid handle
                    auto handle = makeHandle(kBucketOffset + j, meta.lifecycle);

                    // Call the functor
                    f(handle, std::addressof(data[j].val));
                }
            }
        }
    }

    /**
     * Calls the provided `Func` invocable object for each valid handle and its associated mapped type until the
     * invocable object returns `false`.
     * @thread_safety The `Mapped*` passed to \p f is not safe to use if any other thread would be calling
     * releaseIfLastRef() or release() to release the last reference of a Handle. In these situations it is instead
     * recommended to try to add a reference to the `Handle` passed to \p f in order to assure validity.
     * @param f An invocable object with signature `bool(Handle, Mapped*)`. If the invocable object returns `false`,
     *   iteration terminates immediately and returns `false`. It is highly recommended to ignore the `Mapped*` unless
     *   it is guaranteed that no other threads may be modifying the `HandleDatabase`, in which case it is recommend to
     *   instead try to add a reference to the `Handle` in order to assure validity.
     * @returns \c true if iteration completed over the entirety of `*this`; \c false if \p f returned \c false causing
     *   iteration to be aborted early.
     */
    template <class Func CARB_NO_DOC(
        ,
        std::enable_if_t<std::is_same<bool, decltype(std::declval<Func>()(std::declval<Handle>(), std::declval<Mapped*>()))>::value,
                         bool> = true)>
    bool forEachHandle(Func&& f) const
    {
        for (uint32_t i = 0; i < kBuckets; ++i)
        {
            // We are done once we encounter a null pointer
            HandleData* data = getDbIndex(i, std::memory_order_acquire);
            if (!data)
                break;

            uint32_t const kBucketSize = getBucketSize(i);
            uint32_t const kBucketOffset = getBucketOffset(i);
            for (uint32_t j = 0; j != kBucketSize; ++j)
            {
                Metadata meta = data[j].metadata.load(std::memory_order_acquire);
                if ((meta.refCount & kRefMask) != 0)
                {
                    // Valid handle
                    auto handle = makeHandle(kBucketOffset + j, meta.lifecycle);

                    // Call the functor
                    if (!f(handle, std::addressof(data[j].val)))
                        return false;
                }
            }
        }
        return true;
    }

    /**
     * Iterates over all valid handles and sets their reference counts to zero, destroying the associated mapped type.
     * @thread_safety This function is NOT safe to call if any other thread is calling ANY other HandleDatabase function
     * except for clear() or handleWasValid().
     * @returns The number of handles that were released to zero.
     */
    size_t clear();

    /**
     * Causes the calling thread to wait until the given handle has been fully released.
     * @param h The handle to wait for.
     */
    void awaitFinalRelease(Handle h) const;

    /**
     * Retrieves the reference count (debugging only).
     *
     * Obtains the reference count observed by the calling thread at the time of function call. Since handles are
     * effectively weak references, even a returned reference count of 1 does not guarantee that the object is owned
     * only by the calling thread. To safely determine if an entry is shared, use \ref getSharedState().
     * @see getSharedState()
     * @warning This function should be used for debugging only. Other threads may change the reference count by handle
     *   which makes the return value of this function possibly stale at the time the calling thread reads it.
     * @param handle The handle.
     * @returns A \ref cpp::optional containing the reference count observed. If \p handle is not valid,
     *   `cpp::nullopt` is returned.
     */
    cpp::optional<size_t> debugGetRefCount(Handle handle) const noexcept;

    /**
     * Retrieves the reference count (debugging only).
     *
     * Obtains the reference count observed by the calling thread at the time of function call. Since handles are
     * effectively weak references, even a returned reference count of 1 does not guarantee that the object is owned
     * only by the calling thread. To safely determine if an entry is shared, use \ref getSharedState().
     * @see getSharedState()
     * @warning This function should be used for debugging only. Other threads may change the reference count by handle
     *   which makes the return value of this function possibly stale at the time the calling thread reads it.
     * @param mapped A pointer to the mapped type. If `nullptr`, \p mapped has been fully released, or \p mapped is not
     *   owned by `*this`, behavior is undefined.
     * @returns The reference count observed.
     */
    size_t debugGetRefCount(const Mapped* mapped) const noexcept;

    /**
     * Explicitly and atomically marks a handle as shared.
     *
     * A shared handle means that it has been returned outside of the system that manages the handle and the reference
     * count of the handle may be changed at any point by another thread. Once a handle is marked shared by this
     * function, it will remain shared for its entire lifetime.
     * @param handle The handle to validate and mark as shared.
     * @param previouslyShared (Optional) If provided, receives the previous shared state.
     * @retval true If `*previouslyShared` was false, the \p handle is valid and has been marked as shared. If
     *   `*previouslyShared` was true, \p handle *appears* to be valid at the time this function was called.
     * @retval false The \p handle is not valid. \p previouslyShared (if provided) is unchanged.
     */
    bool markShared(Handle handle, bool* previouslyShared = nullptr) noexcept;

    /**
     * Explicitly and atomically marks the handle referring to a mapped object as shared.
     *
     * A shared handle means that it has been returned outside of the system that manages the handle and the reference
     * count of the handle may be changed at any point by another thread. Once a handle is marked shared by this
     * function, it will remain shared for its entire lifetime.
     * @param mapped A pointer to the mapped type. If `nullptr`, \p mapped has been fully released, or \p mapped is not
     *   owned by `*this`, behavior is undefined.
     * @param previouslyShared (Optional) If provided, receives the previous shared state.
     */
    void markShared(Mapped* mapped, bool* previouslyShared = nullptr) noexcept;

    /**
     * Tests a handle for validity and whether that handle is shared.
     *
     * @see markShared() SharedState
     * @param handle The handle to validate and check.
     * @returns `cpp::nullopt` if the \p handle is not valid. Otherwise a \ref SharedState value indicating
     *   how the handle is shared.
     */
    cpp::optional<SharedState> getSharedState(Handle handle) const noexcept;

    /**
     * Tests whether a mapped entry is shared.
     *
     * @see markShared() SharedState
     * @param mapped A pointer to the mapped type. If `nullptr`, \p mapped has been fully released, or \p mapped is not
     *   owned by `*this`, behavior is undefined.
     * @returns A \ref SharedState value indicating how the handle is shared.
     */
    SharedState getSharedState(const Mapped* mapped) const noexcept;

    /**
     * Returns the maximum number of items that can be contained in this HandleDatabase.
     * @returns The maximum number of items that can be contained in `*this`.
     */
    constexpr size_t getMaxSize() const noexcept
    {
        return kIndexMask;
    }

private:
    // So that we don't have a bucket of 1 entry, our first bucket has a minimum population
    CARB_VIZ static constexpr uint32_t kFirstBucketPop = 16;
    CARB_VIZ static constexpr uint32_t _kFirstBucketBits = cpp::countr_zero_constexpr(kFirstBucketPop);
    static_assert(cpp::has_single_bit(kFirstBucketPop), "Must be a power of two");
    CARB_VIZ static constexpr uint32_t kBuckets = kIndexBits - _kFirstBucketBits + 1; ///< Number of buckets

    static constexpr uint32_t kIndexMask = uint32_t(-1) >> (32 - kIndexBits);
    static_assert(cpp::has_single_bit(uint64_t(kIndexMask) + 1), "Must be a bit mask");

    static constexpr uint32_t kRolloverFlag = uint32_t(1) << (kLifecycleBits - 1);
    static constexpr uint32_t kLifecycleMask = kRolloverFlag - 1;
    static_assert(cpp::has_single_bit(kRolloverFlag), "Must be a flag");
    static_assert(cpp::has_single_bit(kLifecycleMask + 1), "Must be a bit mask");

    // Ref counts are always 32 bits.
    static constexpr uint32_t kSharedFlag = 0x80000000u;
    static constexpr uint32_t kRefMask = 0x7fffffffu;

    static Handle makeHandle(uint32_t index, uint32_t lifecycle) noexcept
    {
        // Check preconditions:
        CARB_ASSERT(!(index & ~kIndexMask)); // only index bits allowed
        CARB_ASSERT(!(lifecycle & ~(kLifecycleMask | kRolloverFlag))); // only lifecycle bits allowed
        return cpp::bit_cast<Handle>(uint64_t(index) | (uint64_t(lifecycle & kLifecycleMask) << kIndexBits));
    }

    static std::pair<uint32_t, uint32_t> handleComponents(Handle h) noexcept
    {
        auto bits = cpp::bit_cast<uint64_t>(h);
        return { uint32_t(bits & kIndexMask), uint32_t(bits >> kIndexBits) & kLifecycleMask };
    }

    // A struct for tracking the refcount and lifecycle.
    struct alignas(uint64_t) Metadata
    {
        uint32_t refCount{ 0 };
        CARB_VIZ uint32_t lifecycle{ 0 };

        constexpr Metadata() noexcept = default;
    };

    struct HandleData
    {
        // This union will either be the free link and index, or the constructed mapped type
        union
        {
            struct
            {
                container::LocklessQueueLink<HandleData> link;
                uint32_t index;
            };
            // This `val` is only constructed when the HandleData is in use
            Mapped val;
        };

        // Metadata, but the union allows us to access the refCount atomically, separately.
        union
        {
            CARB_VIZ std::atomic<Metadata> metadata;
            std::atomic_uint32_t refCount; // Must share memory address with metadata.refCount
        };

        constexpr HandleData(uint32_t idx) noexcept : index(idx), metadata{}
        {
        }

        // Empty destructor, required because of the union with non-trivial types
        ~HandleData() noexcept
        {
        }
    };
    static_assert(alignof(HandleData) >= alignof(Mapped),
                  "Invalid assumption: HandleData alignment should meet or exceed Mapped alignment");
    static_assert(sizeof(Handle) == sizeof(uint64_t), "Handle should be 64-bit");

    using HandleDataAllocator = typename std::allocator_traits<Allocator>::template rebind_alloc<HandleData>;
    using AllocatorTraits = std::allocator_traits<HandleDataAllocator>;

    static constexpr uint32_t getBucketSize(uint32_t bucket) noexcept
    {
        return bucket == 0 ? kFirstBucketPop : 1u << (bucket + _kFirstBucketBits - 1);
    }
    static constexpr uint32_t getBucketOffset(uint32_t bucket) noexcept
    {
        return bucket == 0 ? 0 : getBucketSize(bucket);
    }

    static std::pair<uint32_t, uint32_t> indexToBucketAndOffset(uint32_t index) noexcept;
    HandleData* expandDatabase();
    HandleData* getHandleData(uint32_t index) const;
    HandleData* getHandleData(const Mapped* mapped) const;

    void destroyMapped(HandleData* mapped, uint32_t index);

    HandleData* getDbIndex(size_t index, std::memory_order = std::memory_order_seq_cst) const;

    // m_bucket is fixed size and written atomically in expandDatabase(). It never contracts and therefore
    // does not require a mutex
    CARB_VIZ std::atomic<HandleData*> m_bucket[kBuckets] = {};
    struct Members : HandleDataAllocator
    {
        // The "tasking timing" test performs much better with m_free as a queue instead of a stack.
        container::LocklessQueue<HandleData, &HandleData::link> m_free;
    } m_emo;
    // An atomic used as a condition variable of sorts to notify about destruction
    carb::cpp::atomic_size_t m_destructNotifier{ 0 };
};

/**
 * A smart-reference class for a Handle associated with a HandleDatabase.
 *
 * When HandleRef is destroyed, the associated handle is released with the HandleDatabase.
 */
template <class Mapped, class Handle, class Allocator = std::allocator<Mapped>, size_t IndexBits = 32, size_t LifecycleBits = 32>
struct ConstHandleRef
{
public:
    //! An alias to Mapped; the mapped value type.
    using MappedType = const Mapped;

    //! An alias to `const Mapped&`.
    using ReferenceType = const Mapped&;

    //! An alias to `const Mapped*`.
    using PointerType = const Mapped*;

    //! An alias to Handle; the key type used to associate a mapped value type.
    using HandleType = Handle;

    //! An alias to Allocator; the allocator used to allocate memory.
    using AllocatorType = Allocator;

    //! The type specification for the associated HandleDatabase.
    using Database = HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>;

    //! @a Deprecated: Use MappedType instead.
    using element_type = MappedType;
    //! @a Deprecated: Use HandleType instead.
    using handle_type = HandleType;

    /**
     * Default constructor. Produces an empty HandleRef.
     */
    constexpr ConstHandleRef() noexcept = default;

    /**
     * Attempts to atomically reference a Handle from the given @p database.
     * @param database The HandleDatabase containing @p handle.
     * @param handle The handle previously returned from HandleDatabase::createHandle(). Providing an invalid or
     * previously-valid handle results in an empty HandleRef.
     */
    ConstHandleRef(Database& database, Handle handle) noexcept : m_mapped(database.tryAddRef(handle))
    {
        if (m_mapped)
        {
            m_database = std::addressof(database);
            m_handle = handle;
        }
    }

    /**
     * Destructor. If `*this` is non-empty, releases the associated Handle with the associated HandleDatabase.
     */
    ~ConstHandleRef() noexcept
    {
        reset();
    }

    /**
     * Move-constructor. Post-condition: @p other is an empty HandleRef.
     * @param other The other HandleRef to move a reference from.
     */
    ConstHandleRef(ConstHandleRef&& other) noexcept
    {
        swap(other);
    }

    /**
     * Move-assign operator. Swaps state with @p other.
     * @param other The other HandleRef to move a reference from.
     */
    ConstHandleRef& operator=(ConstHandleRef&& other) noexcept
    {
        swap(other);
        return *this;
    }

    // Specifically non-Copyable in order to reduce implicit usage.
    // Use the explicit `clone()` function if a copy is desired
    CARB_PREVENT_COPY(ConstHandleRef);

    /**
     * Explicitly adds a reference to any referenced handle and returns a HandleRef.
     * @returns A HandleRef holding its own reference for the contained handle. May be empty if `*this` is empty.
     */
    [[nodiscard]] ConstHandleRef clone() const noexcept
    {
        if (m_mapped)
            m_database->addRef(m_mapped);
        return ConstHandleRef{ m_database, m_handle, m_mapped };
    }

    /**
     * Dereferences and returns a pointer to the mapped type.
     * @warning Undefined behavior if `*this` is empty.
     * @returns A pointer to the mapped type.
     */
    PointerType operator->() noexcept
    {
        return get();
    }

    /**
     * Dereferences and returns a const pointer to the mapped type.
     * @warning Undefined behavior if `*this` is empty.
     * @returns A const pointer to the mapped type.
     */
    PointerType operator->() const noexcept
    {
        return get();
    }

    /**
     * Dereferences and returns a reference to the mapped type.
     * @warning Undefined behavior if `*this` is empty.
     * @returns A reference to the mapped type.
     */
    ReferenceType operator*() noexcept
    {
        CARB_ASSERT(get());
        return *get();
    }

    /**
     * Dereferences and returns a const reference to the mapped type.
     * @warning Undefined behavior if `*this` is empty.
     * @returns A const reference to the mapped type.
     */
    ReferenceType operator*() const noexcept
    {
        CARB_ASSERT(get());
        return *get();
    }

    /**
     * Returns a pointer to the mapped type, or `nullptr` if empty.
     * @returns A pointer to the mapped type or `nullptr` if empty.
     */
    PointerType get() noexcept
    {
        return this->m_mapped;
    }

    /**
     * Returns a const pointer to the mapped type, or `nullptr` if empty.
     * @returns A const pointer to the mapped type or `nullptr` if empty.
     */
    PointerType get() const noexcept
    {
        return this->m_mapped;
    }

    /**
     * Returns the Handle referenced by `*this`.
     * @returns The Handle referenced by `*this`.
     */
    Handle handle() const noexcept
    {
        return this->m_handle;
    }

    /**
     * Tests if `*this` contains a valid reference.
     * @returns `true` if `*this` maintains a valid reference; `false` if `*this` is empty.
     */
    explicit operator bool() const noexcept
    {
        return get() != nullptr;
    }

    /**
     * Releases any associated reference and resets `*this` to empty.
     */
    void reset()
    {
        if (auto mapped = std::exchange(m_mapped, nullptr))
            m_database->release(mapped);
        m_database = nullptr;
        m_handle = HandleType{};
    }

    /**
     * Releases the ownership of the managed object, if any.
     *
     * The caller becomes responsible for ownership of the returned object and must release it from the handle database.
     * @returns The managed object or `nullptr` if there was no managed object.
     */
    [[nodiscard]] Mapped* release() noexcept
    {
        return std::exchange(m_mapped, nullptr);
    }

    /**
     * Swaps state with another HandleRef.
     */
    void swap(ConstHandleRef& rhs)
    {
        if (this != &rhs)
        {
            std::swap(m_database, rhs.m_database);
            std::swap(m_handle, rhs.m_handle);
            std::swap(m_mapped, rhs.m_mapped);
        }
    }

protected:
    Database* m_database{}; ///< Handle database this reference points into.
    Handle m_handle{}; ///< Handle that this reference currently represents.
    Mapped* m_mapped{}; ///< The mapped value for this reference.

    /**
     *  Protected constructor.  Not to be used externally.
     */
    constexpr ConstHandleRef(Database* db, Handle h, Mapped* m) noexcept : m_database(db), m_handle(h), m_mapped(m)
    {
    }
};

/**
 * A smart-reference class for a Handle associated with a HandleDatabase.
 *
 * When HandleRef is destroyed, the associated handle is released with the HandleDatabase.
 */
template <class Mapped, class Handle, class Allocator = std::allocator<Mapped>, size_t IndexBits = 32, size_t LifecycleBits = 32>
struct HandleRef : public ConstHandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>
{
    /** Base type used for this container. */
    using BaseType = ConstHandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>;

public:
    //! An alias to Mapped; the mapped value type.
    using MappedType = Mapped;

    //! An alias to `Mapped&`.
    using ReferenceType = Mapped&;

    //! An alias to `Mapped*`.
    using PointerType = Mapped*;

    //! An alias to Handle; the key type used to associate a mapped value type.
    using HandleType = Handle;

    //! An alias to Allocator; the allocator used to allocate memory.
    using AllocatorType = Allocator;

    //! The type specification for the associated HandleDatabase.
    using Database = HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>;

    //! @a Deprecated: Use MappedType instead.
    using element_type = MappedType;
    //! @a Deprecated: Use HandleType instead.
    using handle_type = HandleType;

    /**
     * Default constructor. Produces an empty HandleRef.
     */
    constexpr HandleRef() noexcept = default;

    /**
     * Attempts to atomically reference a Handle from the given @p database.
     * @param database The HandleDatabase containing @p handle.
     * @param handle The handle previously returned from HandleDatabase::createHandle(). Providing an invalid or
     * previously-valid handle results in an empty HandleRef.
     */
    HandleRef(Database& database, Handle handle) noexcept : BaseType(database, handle)
    {
    }

    /**
     * Explicitly adds a reference to any referenced handle and returns a HandleRef.
     * @returns A HandleRef holding its own reference for the contained handle. May be empty if `*this` is empty.
     */
    [[nodiscard]] HandleRef clone() const noexcept
    {
        if (this->m_mapped)
            this->m_database->addRef(this->m_mapped);
        return HandleRef{ this->m_database, this->m_handle, this->m_mapped };
    }

    /**
     * Dereferences and returns a pointer to the mapped type.
     * @warning Undefined behavior if `*this` is empty.
     * @returns A pointer to the mapped type.
     */
    PointerType operator->() noexcept
    {
        return get();
    }

    /**
     * Dereferences and returns a const pointer to the mapped type.
     * @warning Undefined behavior if `*this` is empty.
     * @returns A const pointer to the mapped type.
     */
    PointerType operator->() const noexcept
    {
        return get();
    }

    /**
     * Dereferences and returns a reference to the mapped type.
     * @warning Undefined behavior if `*this` is empty.
     * @returns A reference to the mapped type.
     */
    ReferenceType operator*() noexcept
    {
        CARB_ASSERT(get());
        return *get();
    }

    /**
     * Dereferences and returns a const reference to the mapped type.
     * @warning Undefined behavior if `*this` is empty.
     * @returns A const reference to the mapped type.
     */
    ReferenceType operator*() const noexcept
    {
        CARB_ASSERT(get());
        return *get();
    }

    /**
     * Returns a pointer to the mapped type, or `nullptr` if empty.
     * @returns A pointer to the mapped type or `nullptr` if empty.
     */
    PointerType get() noexcept
    {
        return this->m_mapped;
    }

    /**
     * Returns a const pointer to the mapped type, or `nullptr` if empty.
     * @returns A const pointer to the mapped type or `nullptr` if empty.
     */
    PointerType get() const noexcept
    {
        return this->m_mapped;
    }

    /**
     * Swaps state with another HandleRef.
     */
    void swap(HandleRef& rhs)
    {
        BaseType::swap(rhs);
    }

private:
    constexpr HandleRef(Database* db, Handle h, Mapped* m) noexcept : BaseType(db, h, m)
    {
    }
};

/**
 * @a Deprecated: Use HandleRef instead.
 */
template <class Mapped, class Handle, class Allocator = std::allocator<Mapped>, size_t IndexBits = 32, size_t LifecycleBits = 32>
using ScopedHandleRef = HandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>;

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline constexpr HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::HandleDatabase() noexcept
{
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::~HandleDatabase()
{
    // Make sure everything is removed from the free list before we destroy it
    m_emo.m_free.popAll();

    size_t leaks = 0;
    for (uint32_t i = 0; i < CARB_COUNTOF32(m_bucket); i++)
    {
        HandleData* handleData = m_bucket[i].exchange(nullptr, std::memory_order_relaxed);
        if (!handleData)
            break;

        // Go through each entry and destruct any outstanding ones with a non-zero refcount
        uint32_t const kBucketSize = getBucketSize(i);
        for (size_t j = 0; j != kBucketSize; ++j)
        {
            Metadata meta = handleData[j].metadata.load(std::memory_order_relaxed);
            if ((meta.refCount & kRefMask) != 0)
            {
                handleData[j].val.~Mapped();
                ++leaks;
            }
            AllocatorTraits::destroy(m_emo, handleData + j);
        }

        AllocatorTraits::deallocate(m_emo, handleData, kBucketSize);
    }

    if (leaks != 0)
    {
        // We don't notify m_destructNotifier here because destructors are inherently non-threadsafe. No other threads
        // should be in any HandleDatabase functions with *this, and if they are then UB will result.

        // If we *did* notify here, then a thread in awaitFinalRelease() will attempt unsafe memory accesses, therefore
        // this is specifically disallowed.

        CARB_LOG_WARN("%s: had %zu outstanding handle(s) at shutdown", CARB_PRETTY_FUNCTION, leaks);
    }
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline auto HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::getHandleData(uint32_t index) const
    -> HandleData*
{
    auto [bucketIndex, offsetInBucket] = indexToBucketAndOffset(index);

    CARB_UNLIKELY_IF(bucketIndex >= CARB_COUNTOF(m_bucket))
    {
        return nullptr;
    }

    auto bucket = getDbIndex(bucketIndex, std::memory_order_acquire);
    return bucket ? bucket + offsetInBucket : nullptr;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline auto HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::getHandleData(const Mapped* mapped) const
    -> HandleData*
{
    // HandleData must have val as the first member. This would prevent us from casting
    // mapped to HandleData without using ugly pointer math otherwise.
    // static assert using offsetof() is not possible due to HandleData having a non-standard-layout type.
    auto pHandleData = reinterpret_cast<HandleData*>(const_cast<Mapped*>(mapped));
    CARB_ASSERT(reinterpret_cast<intptr_t>(&pHandleData->val) - reinterpret_cast<intptr_t>(pHandleData) == 0);
    return pHandleData;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline void HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::destroyMapped(HandleData* hd,
                                                                                               uint32_t index)
{
    // Destroy the mapped type and add it to the free list.
    hd->val.~Mapped();
    hd->index = index;
    m_emo.m_free.push(hd);

    // Just need atomicity, so used relaxed
    m_destructNotifier.fetch_add(1, std::memory_order_relaxed);
    m_destructNotifier.notify_all();
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline auto HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::getDbIndex(size_t index,
                                                                                            std::memory_order order) const
    -> HandleData*
{
    static HandleData* const kLocked = reinterpret_cast<HandleData*>(size_t(-1));
    CARB_ASSERT(index < kBuckets);

    // Spin briefly if the entry is locked
    HandleData* bucket = m_bucket[index].load(order);
    while (CARB_UNLIKELY(bucket == kLocked))
    {
        CARB_HARDWARE_PAUSE();
        bucket = m_bucket[index].load(order);
    }
    return bucket;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::handleWasValid(Handle handle) const
{
    auto [index, lifecycle] = handleComponents(handle);
    HandleData* pHandleData = getHandleData(index);

    if (pHandleData == nullptr)
    {
        return false;
    }

    Metadata meta = pHandleData->metadata.load(std::memory_order_acquire);

    // The zero lifecycle count isn't used
    if (lifecycle == 0 || meta.lifecycle == 0)
    {
        return false;
    }

    // The kRolloverFlag value is always unset in hu, but possibly present in meta.lifecycle. However, this is still a
    // valid comparison because if the kRolloverFlag is set in meta.lifecycle, it means that every possible value has
    // been a valid handle at one point and the expression will always result in `true`.
    return lifecycle <= meta.lifecycle;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::handleIsValid(Handle handle) const
{
    auto [index, lifecycle] = handleComponents(handle);
    HandleData* pHandleData = getHandleData(index);

    if (pHandleData == nullptr)
    {
        return false;
    }

    // Fence-atomic synchronization since we're not doing any atomic modification, just loading. This fence allows use
    // of the relaxed load though.
    carb::this_thread::atomic_fence_seq_cst();
    Metadata meta = pHandleData->metadata.load(std::memory_order_relaxed);

    // We return true if there is a non-zero refcount on the handle data and the lifecycle matches current.
    return ((meta.refCount & kRefMask) != 0 && (meta.lifecycle & kLifecycleMask) == lifecycle);
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
template <class... Args>
inline std::pair<Handle, Mapped*> HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::createHandle(
    Args&&... args)
{
    HandleData* handleData = m_emo.m_free.pop();
    if (!handleData)
        handleData = expandDatabase();

    CARB_ASSERT(handleData);

    Metadata meta = handleData->metadata.load(std::memory_order_relaxed);
    CARB_ASSERT(((void*)std::addressof(handleData->metadata) == (void*)std::addressof(handleData->refCount)) &&
                offsetof(Metadata, refCount) == 0);

    meta.refCount = 1;

    // Don't allow the 0 lifecycle.
    meta.lifecycle++;
    if ((meta.lifecycle & kLifecycleMask) == 0)
    {
        meta.lifecycle = 1 | kRolloverFlag;
    }

    uint32_t indexToAllocateFrom = handleData->index;
    Mapped* p = new (std::addressof(handleData->val)) Mapped(std::forward<Args>(args)...);
    handleData->metadata.store(meta, std::memory_order_release);

    return std::make_pair(makeHandle(indexToAllocateFrom, meta.lifecycle), p);
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline Mapped* HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::tryAddRef(Handle handle,
                                                                                              size_t* outRefCount)
{
    auto [index, lifecycle] = handleComponents(handle);

    HandleData* pHandleData = getHandleData(index);

    if (pHandleData == nullptr)
    {
        return nullptr;
    }

    Metadata meta = pHandleData->metadata.load(std::memory_order_acquire);
    for (;;)
    {
        if ((meta.refCount & kRefMask) == 0 || (meta.lifecycle & kLifecycleMask) != lifecycle)
        {
            return nullptr;
        }

        Metadata desired = meta;
        desired.refCount |= kSharedFlag;
        desired.refCount++;
        if (pHandleData->metadata.compare_exchange_weak(
                meta, desired, std::memory_order_release, std::memory_order_relaxed))
        {
            if (outRefCount)
                *outRefCount = desired.refCount & kRefMask;
            return std::addressof(pHandleData->val);
        }
    }
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline size_t HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::addRef(Handle handle)
{
    size_t out;
    Mapped* mapped = tryAddRef(handle, &out);
    CARB_FATAL_UNLESS(mapped != nullptr, "Attempt to addRef released handle");
    return out;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline size_t HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::addRef(Mapped* mapped)
{
    HandleData* pHandleData = getHandleData(mapped);

    // We're working with the Mapped type here, so if it's not valid we're in UB.
    uint32_t count = pHandleData->refCount.fetch_add(1, std::memory_order_relaxed) + 1;
    CARB_CHECK(count > 1); // no resurrection and no rollover
    return count;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::release(Handle handle)
{
    auto [index, lifecycle] = handleComponents(handle);

    HandleData* pHandleData = getHandleData(index);
    CARB_ASSERT(pHandleData);

    if (pHandleData == nullptr)
    {
        return false;
    }

    Metadata meta = pHandleData->metadata.load(std::memory_order_relaxed);

    for (;;)
    {
        if ((meta.refCount & kRefMask) == 0 || (meta.lifecycle & kLifecycleMask) != lifecycle)
        {
            return false;
        }
        Metadata desired = meta;
        bool released = (--desired.refCount & kRefMask) == 0;
        if (CARB_LIKELY(pHandleData->metadata.compare_exchange_weak(
                meta, desired, std::memory_order_release, std::memory_order_relaxed)))
        {
            if (released)
            {
                std::atomic_thread_fence(std::memory_order_acquire);
                destroyMapped(pHandleData, index);
            }
            return released;
        }
    }
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::release(Mapped* mapped)
{
    HandleData* pHandleData = getHandleData(mapped);

    // We're working with the Mapped type here, so if it's not valid we're in UB.
    uint32_t prev = pHandleData->refCount.fetch_sub(1, std::memory_order_release);
    CARB_CHECK((prev & kRefMask) >= 1); // No underflow
    if ((prev & kRefMask) == 1)
    {
        // Released
        std::atomic_thread_fence(std::memory_order_acquire);
        destroyMapped(pHandleData, handleComponents(getHandleFromValue(mapped)).first);
        return true;
    }
    return false;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::releaseIfLastRef(Handle handle)
{
    auto [index, lifecycle] = handleComponents(handle);
    HandleData* pHandleData = getHandleData(index);
    CARB_ASSERT(pHandleData);

    if (pHandleData == nullptr)
    {
        return false;
    }

    // Since we're making decisions based solely on a load, ensure full fence
    this_thread::atomic_fence_seq_cst();
    Metadata meta = pHandleData->metadata.load(std::memory_order_relaxed);

    for (;;)
    {
        if ((meta.refCount & kRefMask) == 0 || (meta.lifecycle & kLifecycleMask) != lifecycle)
        {
            return false;
        }
        if ((meta.refCount & kRefMask) > 1)
        {
            return false;
        }
        Metadata desired = meta;
        desired.refCount &= ~kRefMask;
        if (CARB_LIKELY(pHandleData->metadata.compare_exchange_weak(
                meta, desired, std::memory_order_release, std::memory_order_relaxed)))
        {
            std::atomic_thread_fence(std::memory_order_acquire);
            destroyMapped(pHandleData, index);
            return true;
        }
    }
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::releaseIfLastRef(Mapped* mapped)
{
    // We're working with the Mapped type here, so if it's not valid we're in UB.
    HandleData* pHandleData = getHandleData(mapped);

    // Since we're making decisions based solely on a load, ensure full fence
    this_thread::atomic_fence_seq_cst();
    uint32_t refCount = pHandleData->refCount.load(std::memory_order_relaxed);
    for (;;)
    {
        CARB_CHECK((refCount & kRefMask) != 0);
        if ((refCount & kRefMask) > 1)
        {
            return false;
        }
        if (CARB_LIKELY(pHandleData->refCount.compare_exchange_weak(
                refCount, refCount & ~kRefMask, std::memory_order_relaxed, std::memory_order_relaxed)))
        {
            std::atomic_thread_fence(std::memory_order_acquire);
            destroyMapped(pHandleData, handleComponents(getHandleFromValue(mapped)).first);
            return true;
        }
    }
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline Mapped* HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::getValueFromHandle(Handle handle) const
{
    auto [index, lifecycle] = handleComponents(handle);

    HandleData* pHandleData = getHandleData(index);
    if (pHandleData == nullptr)
    {
        return nullptr;
    }

    Metadata meta = pHandleData->metadata.load(std::memory_order_acquire);
    if ((meta.lifecycle & kLifecycleMask) != lifecycle || (meta.refCount & kRefMask) == 0)
        return nullptr;
    return std::addressof(pHandleData->val);
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline Handle HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::getHandleFromValue(const Mapped* mapped) const
{
    // Resolve mapped to the handle data
    // We're working with the Mapped type here, so if it's not valid we're in UB.
    HandleData* pHandleData = getHandleData(mapped);

    // Start setting up the handle, but we don't know the index yet.
    uint32_t lifecycle = pHandleData->metadata.load(std::memory_order_acquire).lifecycle;

    // Find the index by searching all of the buckets.
    for (uint32_t i = 0; i < kBuckets; ++i)
    {
        HandleData* p = getDbIndex(i, std::memory_order_acquire);
        if (!p)
            break;

        size_t offset = size_t(pHandleData - p);
        if (offset < getBucketSize(i))
        {
            return makeHandle(getBucketOffset(i) + uint32_t(offset), lifecycle);
        }
    }

    // Given mapped doesn't exist in this HandleDatabase
    CARB_CHECK(0);
    return Handle{};
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline std::pair<uint32_t, uint32_t> HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::indexToBucketAndOffset(
    uint32_t index) noexcept
{
    auto const zeros = uint32_t(cpp::countl_zero(index));

    uint32_t const bucket = (32u - _kFirstBucketBits) - carb_min(zeros, 32u - _kFirstBucketBits);
    return { bucket, index - ((bucket != 0) * (1u << (bucket + _kFirstBucketBits - 1))) };
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline auto HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::expandDatabase() -> HandleData*
{
    static HandleData* const kLocked = reinterpret_cast<HandleData*>(size_t(-1));

    // Scan (right now O(n), but this is rare and n is small) for the first empty database.
    uint32_t bucketToAllocateFrom;
    for (bucketToAllocateFrom = 0; bucketToAllocateFrom != CARB_COUNTOF32(m_bucket); bucketToAllocateFrom++)
    {
        HandleData* mem = m_bucket[bucketToAllocateFrom].load(std::memory_order_acquire);
        for (;;)
        {
            while (mem == kLocked)
            {
                // Another thread is trying to allocate this. Try to pull from the free list until it stabilizes.
                mem = m_emo.m_free.pop();
                if (mem)
                    return mem;

                mem = m_bucket[bucketToAllocateFrom].load(std::memory_order_acquire);
            }
            if (!mem)
            {
                // Try to lock it
                if (m_bucket[bucketToAllocateFrom].compare_exchange_strong(
                        mem, kLocked, std::memory_order_release, std::memory_order_relaxed))
                {
                    // Successfully locked
                    break;
                }

                // Continue if another thread has locked it
                if (mem == kLocked)
                    continue;

                // Failed to lock, but it's not locked anymore, so see if there's a free entry now
                HandleData* hd = m_emo.m_free.pop();
                if (hd)
                    return hd;
            }

            CARB_ASSERT(mem != kLocked);
            break;
        }

        if (!mem)
            break;
    }
    CARB_FATAL_UNLESS(bucketToAllocateFrom < CARB_COUNTOF(m_bucket), "Out of handles!");

    uint32_t const allocateCount = getBucketSize(bucketToAllocateFrom);
    uint32_t const offset = getBucketOffset(bucketToAllocateFrom);

    HandleData* handleData = AllocatorTraits::allocate(m_emo, allocateCount);

    // Set the indexes
    for (uint32_t i = 0; i < allocateCount; ++i)
    {
        AllocatorTraits::construct(m_emo, handleData + i, offset + i);
    }

    // Add entries (after the first) to the free list
    m_emo.m_free.push(handleData + 1, handleData + allocateCount);

    // Overwrite the lock with the actual pointer now
#if CARB_ASSERT_ENABLED
    HandleData* expect = m_bucket[bucketToAllocateFrom].exchange(handleData, std::memory_order_release);
    CARB_ASSERT(expect == kLocked);
#else
    m_bucket[bucketToAllocateFrom].store(handleData, std::memory_order_release);
#endif

    // Return the first entry that we reserved for the caller
    return handleData;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline size_t HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::clear()
{
    size_t count = 0;

    for (uint32_t i = 0; i != kBuckets; ++i)
    {
        HandleData* data = getDbIndex(i, std::memory_order_acquire);
        if (!data)
            break;

        uint32_t const kBucketSize = getBucketSize(i);
        uint32_t const kBucketOffset = getBucketOffset(i);
        for (uint32_t j = 0; j != kBucketSize; ++j)
        {
            if ((data[j].refCount.exchange(0, std::memory_order_release) & kRefMask) != 0)
            {
                // Successfully set the refcount to 0. Destroy and add to the free list
                std::atomic_thread_fence(std::memory_order_acquire);
                ++count;
                auto hd = &data[j];
                hd->val.~Mapped();
                hd->index = kBucketOffset + j;
                m_emo.m_free.push(hd);
            }
        }
    }

    // Notify once at the end
    if (count)
    {
        // Just need atomicity, so use relaxed semantics.
        m_destructNotifier.fetch_add(1, std::memory_order_relaxed);
        m_destructNotifier.notify_all();
    }

    return count;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline void HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::awaitFinalRelease(Handle h) const
{
    // handleIsValid() performs seq-cst ordering, so we can use relaxed semantics here.
    auto val = m_destructNotifier.load(std::memory_order_relaxed);
    while (handleIsValid(h))
    {
        m_destructNotifier.wait(val, std::memory_order_relaxed);
        val = m_destructNotifier.load(std::memory_order_relaxed);
    }
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline cpp::optional<size_t> HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::debugGetRefCount(
    Handle h) const noexcept
{
    auto [index, lifecycle] = handleComponents(h);

    auto data = getHandleData(index);

    if (!data)
        return cpp::nullopt;

    Metadata meta = data->metadata.load(std::memory_order_acquire);
    if ((meta.refCount & kRefMask) == 0 || (meta.lifecycle & kLifecycleMask) != lifecycle)
        return cpp::nullopt;

    return meta.refCount & kRefMask;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline size_t HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::debugGetRefCount(
    const Mapped* mapped) const noexcept
{
    auto data = getHandleData(mapped);

    auto refs = data->refCount.load(std::memory_order_acquire) & kRefMask;
    CARB_ASSERT(refs != 0);
    return refs;
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::markShared(Handle h,
                                                                                            bool* previouslyShared) noexcept
{
    auto [index, lifecycle] = handleComponents(h);

    auto data = getHandleData(index);

    if (!data)
        return false;

    Metadata meta = data->metadata.load(std::memory_order_acquire);
    for (;;)
    {
        if ((meta.refCount & kRefMask) == 0 || (meta.lifecycle & kLifecycleMask) != lifecycle)
            return false;

        if (meta.refCount & kSharedFlag)
        {
            if (previouslyShared)
                *previouslyShared = true;
            return true;
        }

        Metadata desired = meta;
        desired.refCount |= kSharedFlag;
        if (data->metadata.compare_exchange_weak(meta, desired, std::memory_order_release, std::memory_order_relaxed))
        {
            if (previouslyShared)
                *previouslyShared = false;
            return true;
        }
    }
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline void HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::markShared(Mapped* mapped,
                                                                                            bool* previouslyShared) noexcept
{
    auto data = getHandleData(mapped);

    auto prev = data->refCount.fetch_or(kSharedFlag, std::memory_order_release);
    CARB_ASSERT((prev & kRefMask) != 0);
    if (previouslyShared)
        *previouslyShared = !!(prev & kSharedFlag);
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline cpp::optional<SharedState> HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::getSharedState(
    Handle h) const noexcept
{
    auto [index, lifecycle] = handleComponents(h);

    auto data = getHandleData(index);

    if (!data)
        return cpp::nullopt;

    Metadata meta = data->metadata.load(std::memory_order_acquire);
    if ((meta.refCount & kRefMask) == 0 || (meta.lifecycle & kLifecycleMask) != lifecycle)
        return cpp::nullopt;

    return (SharedState)(((meta.refCount & kRefMask) > 1 ? eReferenced : eNotShared) |
                         (!(meta.refCount & kSharedFlag) ? eNotShared : eMarkedShared));
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline SharedState HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::getSharedState(
    const Mapped* mapped) const noexcept
{
    auto data = getHandleData(mapped);

    auto refs = data->refCount.load(std::memory_order_acquire);
    CARB_ASSERT((refs & kRefMask) != 0);

    return (SharedState)(((refs & kRefMask) > 1 ? eReferenced : eNotShared) |
                         (!(refs & kSharedFlag) ? eNotShared : eMarkedShared));
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline auto HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::makeScopedRef(Handle handle)
    -> HandleRefType
{
    return HandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>(*this, handle);
}

template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline auto HandleDatabase<Mapped, Handle, Allocator, IndexBits, LifecycleBits>::makeScopedRef(Handle handle) const
    -> ConstHandleRefType
{
    return ConstHandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>(
        const_cast<HandleDatabase&>(*this), handle);
}

// Global operators.
/**
 * Tests equality between HandleRef and `nullptr`.
 * @param ref The HandleRef to test.
 * @returns `true` if @p ref is empty; `false` otherwise.
 */
template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool operator==(const HandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>& ref, std::nullptr_t)
{
    return ref.get() == nullptr;
}

/**
 * Tests equality between HandleRef and `nullptr`.
 * @param ref The HandleRef to test.
 * @returns `true` if @p ref is empty; `false` otherwise.
 */
template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool operator==(std::nullptr_t, const HandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>& ref)
{
    return ref.get() == nullptr;
}

/**
 * Tests inequality between HandleRef and `nullptr`.
 * @param ref The HandleRef to test.
 * @returns `true` if @p ref is not empty; `false` otherwise.
 */
template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool operator!=(const HandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>& ref, std::nullptr_t)
{
    return ref.get() != nullptr;
}

/**
 * Tests inequality between HandleRef and `nullptr`.
 * @param ref The HandleRef to test.
 * @returns `true` if @p ref is not empty; `false` otherwise.
 */
template <class Mapped, class Handle, class Allocator, size_t IndexBits, size_t LifecycleBits>
inline bool operator!=(std::nullptr_t, const HandleRef<Mapped, Handle, Allocator, IndexBits, LifecycleBits>& ref)
{
    return ref.get() != nullptr;
}

} // namespace extras
} // namespace carb

CARB_IGNOREWARNING_MSC_POP
