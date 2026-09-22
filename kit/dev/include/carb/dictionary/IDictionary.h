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
//! @brief carb.dictionary interface definition file.
#pragma once

#include "../Defines.h"
#include "../Interface.h"
#include "../Types.h"
#include "../extras/Hash.h"
#include "../cpp/StringView.h"
#include "../../omni/String.h"

#include <cstdint>

namespace carb
{
namespace dictionary
{

/**
 * Supported item types.
 */
enum class ItemType
{
    /** Boolean value type.  Values of this type will be `true` or `false`.  These values may be
     *  converted from numerical values where a 0 value is treated as `false` and any other value
     *  is treated as `true`.  These may similarly be converted from string values that either
     *  are the strings `true` or `false`, or a numerical string.
     */
    eBool,

    /** 64-bit integer value type.  Values of this type can be any signed 64-bit integer.  These
     *  values may be converted from other numerical types with a simple cast.  Note however that
     *  converting from a floating point value that is out of range of a 64-bit integer will
     *  result in `INT64_MIN` being returned on x86_64 platforms.  Integer items may be converted
     *  from a boolean value to get either 0 or 1.  These may be converted from a string
     *  that contains only a numerical value.  Other strings will convert to the value 0.
     */
    eInt,

    /** 64-bit floating point value type.  Values of this type can be any signed 64-bit floating
     *  point value.  These values may be converted from other numerical types with a simple cast.
     *  These may be converted from a boolean value to get either 0 or 1.  These may be converted
     *  from a string that contains only a numerical value.  Other strings will convert to the
     *  value 0.
     */
    eFloat,

    /** String value type.  Values of this type can contain any string data, including
     *  multi-strings (ie: a string with internal null characters) or binary byte data.
     *  These values may be converted to numerical or boolean types if they contain the
     *  appropriate data and no extra characters (ie: "0.001purple" will not convert to
     *  a floating point value).
     */
    eString,

    /** Dictionary item type.  A dictionary is one that has zero or more children and no local
     *  item value.  This type of item cannot be implicitly converted to any other data type
     *  and all value `get` operations on it will fail.  This item type can also be treated as
     *  an array if it has one or more children whose names are consecutive non-negative integers
     *  starting at zero.  An array item may still have other children with non-integer or
     *  non-consecutive names, but they will not be seen as being part of the array.
     */
    eDictionary,

    /** The total number of item types.  This is not considered a valid item type but will be
     *  used as a return value from some @ref IDictionary functions to indicate a failure or
     *  error condition.
     */
    eCount
};

//! Structure used in opaque pointers to each dictionary node
struct Item DOXYGEN_EMPTY_CLASS;

//! Actions that may be returned by @ref carb::dictionary::OnUpdateItemFn.
//! @see IDictionary::update() and @ref OnUpdateItemFn for more information.
enum class UpdateAction
{
    /** The target item should be overwritten by the source item.  This will include all of the
     *  children of the target item as well if one of the items is _not_ a dictionary.  The
     *  children of the overwritten item will not be enumerated or considered after this.
     */
    eOverwrite,

    /** The target item should be retained, ignoring the source item.  The children of the target
     *  item will still be enumerated after this.
     */
    eKeep,

    /** The entire subtree should be replaced (dictionary source item only).  This action only
     *  differs from @ref eOverwrite when both the target and source items are dictionaries.
     *  If neither or only one item is a dictionary, this action behaves identically to
     *  @ref eOverwrite.  The subtree of this item may still be enumerated for the update
     *  operation after this action is returned.
     */
    eReplaceSubtree,
};

//! Item flags that can be specified by the user.
//! @see IDictionary::getItemFlag(), IDictionary::setItemFlag(), IDictionary::copyItemFlags().
enum class ItemFlag
{
    /** Flag to indicate that a given item is intended to have a subtree even if it might not
     *  currently have any children.  This allows for better array handling during dictionary
     *  update operations with IDictionary::update() so that @ref UpdateAction::eOverwrite
     *  versus @ref UpdateAction::eReplaceSubtree can be chosen more accurately in the update
     *  callback function.  This handling is already present in the provided update callback
     *  function overwriteOriginalWithArrayHandling().  For uses that need their own update
     *  callback function implementations, this flag can be used to provide similar functionality.
     */
    eUnitSubtree,
};

/**
 * Callback function that will tell whether and how the merger in IDictionary::update() operations
 * should overwrite the destination item with the source item.  This callback is called once for
 * each proposed merge operation that occurs during the update.  Note that this callback will be
 * performed for both leaf and intermediate items in the existing dictionary (ie: the dictionary
 * being merged into).  If the existing dictionary contains an item that is not also present in
 * the source dictionary (ie: the one being merged into the existing dictionary), this callback
 * will not be performed and the walk of the dictionary will continue.
 *
 * @param[in] dstItem       The target item in the existing dictionary that is being updated.
 *                          This may be `nullptr` if no matching item exists in the existing
 *                          dictionary.
 * @param[in] dstItemType   The item type for @p dstItem.  This will be @ref ItemType::eCount
 *                          if @p dstItem is `nullptr`.  This can be used to make merging
 *                          decisions based on the source and destination item types.  This is
 *                          also provided as a convenience so that the type of each item doesn't
 *                          need to be explicitly retrieved for each call.
 * @param[in] srcItem       The source item from the dictionary being merged into the existing
 *                          dictionary.  This is potentially a new item to be added or one that
 *                          exists in both dictionaries under the same name or path.  It is the
 *                          responsibility of this callback to decide if and how to merge this
 *                          item into the existing dictionary by returning the appropriate update
 *                          action.  This will not be `nullptr`.
 * @param[in] srcItemType   The item type for @p srcItem.  This can be used to make merging
 *                          decisions based on the source and destination item types.  This is
 *                          also provided as a convenience so that the type of each item doesn't
 *                          need to be explicitly retrieved for each call.
 * @param[in] userData      An opaque user data pointer that is provided in the original call to
 *                          IDictionary::update().  The callback implementation must know how to
 *                          properly interpret this data.
 * @returns The action that the dictionary update merger should take to handle the merging of
 *          this particular pair of items.
 */
typedef UpdateAction (*OnUpdateItemFn)(
    const Item* dstItem, ItemType dstItemType, const Item* srcItem, ItemType srcItemType, void* userData);

/**
 * Note that this function does not properly handle overwriting of arrays due to
 * overwriting array being shorter, potentially leaving part of the older array in-place
 * after the merge
 * Use \ref overwriteOriginalWithArrayHandling() if dictionaries are expected to contain array data.
 * @see IDictionary::update()
 */
inline UpdateAction overwriteOriginal(
    const Item* dstItem, ItemType dstItemType, const Item* srcItem, ItemType srcItemType, void* userData)
{
    CARB_UNUSED(dstItem, dstItemType, srcItem, srcItemType, userData);
    return UpdateAction::eOverwrite;
}

/**
 * Function that indicates that the merger should retain the existing destination item.
 * @see IDictionary::update()
 */
inline UpdateAction keepOriginal(
    const Item* dstItem, ItemType dstItemType, const Item* srcItem, ItemType srcItemType, void* userData)
{
    CARB_UNUSED(dstItemType, srcItem, srcItemType, userData);
    if (!dstItem)
    {
        // If the destination item doesn't exist - allow to create a new one
        return UpdateAction::eOverwrite;
    }
    return UpdateAction::eKeep;
}

//! Alias for \ref overwriteOriginal().
constexpr OnUpdateItemFn kUpdateItemOverwriteOriginal = overwriteOriginal;
//! Alias for \ref keepOriginal().
constexpr OnUpdateItemFn kUpdateItemKeepOriginal = keepOriginal;

//! Opaque value representing a subscription.
//! @see IDictionary::subscribeToNodeChangeEvents() IDictionary::subscribeToTreeChangeEvents()
struct SubscriptionId DOXYGEN_EMPTY_CLASS;

//! Type of a change passed to a subscription callback.
//!
//! A change callback can be queued for a lot of different dictionary operations, basically
//! anything that is not a 'get' type operation.  Multiple callbacks can be queued for what
//! seems like a single operation on a dictionary as well.  For example, creating and setting
//! an item's value in an @c IDictionary::make*AtPath() can both create an item and modify its
//! value.  Operations such as IDictionary::update() can also trigger a lot of change
//! notifications since it can create, modify, and delete items a lot of items in a dictionary.
//! @see IDictionary::subscribeToNodeChangeEvents(), IDictionary::subscribeToTreeChangeEvents(), OnNodeChangeEventFn,
//! OnTreeChangeEventFn.
enum class ChangeEventType
{
    /** A new item was created under the dictionary.  This may also be accompanied by an
     *  @ref eChanged event if an initial value is also set for the new item through an
     *  operation such as IDictionary::makeIntAtPath().  This type of callback will be
     *  performed after the new item is created.
     */
    eCreated,

    /** The value or type of an existing item in the dictionary has changed.  This can be
     *  triggered by operations such as @c IDictionary::set*() that can modify both the item's
     *  type and value, or by operations such as IDictionary::createItem() which can potentially
     *  change an item's type if one already exists at the given path.  This type of callback
     *  will be performed after the new value has been set in the item.
     */
    eChanged,

    /** An item was destroyed in the dictionary.  This can be triggered by explicit calls to
     *  IDictionary::destroyItem() or by operations that could implicitly delete an item's
     *  subtree such as IDictionary::update() or @c IDictionary::set*().  This type of callback
     *  will be performed just before the given item is destroyed.
     */
    eDestroyed,
};

/**
 * A callback that, once registered with IDictionary::subscribeToNodeChangeEvents(), receives
 * notifications when an item at a specific path changes state or value.  This can include being
 * created or destroyed, or its value being changed.
 *
 * @note The callbacks happen in the context of the thread performing the change.  It is safe to
 *       call back into the IDictionary interface and unsubscribe or otherwise make changes from
 *       the callback function itself.  For @ref ChangeEventType::eCreated and
 *       @ref ChangeEventType::eChanged types, no internal locks are held during the callback.
 *       For @ref ChangeEventType::eDestroyed types, internal locks are held which can cause
 *       thread-synchronization issues with locking order.
 *
 * @param changedItem   The item being changed.  This will never be `nullptr`.  The item's value
 *                      should not be changed inside the callback since that could result in an
 *                      endless callback loop.  Its value, type, or flag may be safely queried
 *                      though.
 * @param eventType     The type of event that is occurring on @p changedItem.
 * @param userData      An opaque user data object.  This value is stored at the time the change
 *                      subscription is created with IDictionary::subscribeToNodeChangeEvents()
 *                      but is never accessed or interpreted internally.  It is the callback
 *                      implementation's responsibility to know how to correctly interpret this
 *                      value.
 */
using OnNodeChangeEventFn = void (*)(const Item* changedItem, ChangeEventType eventType, void* userData);

/**
 * A callback that, once registered with IDictionary::subscribeToTreeChangeEvents(), receives
 * notifications when Items in a given tree change state or value.  This can include being
 * created or destroyed, or the value of an item in the watched tree changes.
 *
 * @note The callbacks happen in the context of the thread performing the change.  It is safe to
 *       call back into the IDictionary interface and unsubscribe or otherwise make changes from
 *       the callback itself.  For @ref ChangeEventType::eCreated and
 *       @ref ChangeEventType::eChanged types, no internal locks are held during the callback.
 *       For @ref ChangeEventType::eDestroyed, internal locks are held which can cause
 *       thread-synchronization issues with locking order.
 *
 * @param treeItem      The root of the tree given to the tree being watched for changes.  This
 *                      is passed to @ref IDictionary::subscribeToTreeChangeEvents() when the
 *                      callback is originally registered.  The item @p changedItem will be a
 *                      descendent of this item.
 * @param changedItem   The item that is being changed.  This will never be `nullptr`.  This may
 *                      be either @p treeItem or one of its descendants.
 * @param eventType     The type of event that is occurring on @p changedItem.
 * @param userData      An opaque user data object.  This value is stored at the time the change
 *                      subscription is created with IDictionary::subscribeToNodeChangeEvents()
 *                      but is never accessed or interpreted internally.  It is the callback
 *                      implementation's responsibility to know how to correctly interpret this
 *                      value.
 */
using OnTreeChangeEventFn = void (*)(const Item* treeItem,
                                     const Item* changedItem,
                                     ChangeEventType eventType,
                                     void* userData);

/**
 * DOM-style dictionary (keeps the whole structure in-memory).
 *
 * In most functions, item is specified using the relative root index and path from
 * the relative root. Path can be nullptr, meaning that baseItem will be considered
 * a specified item.
 *
 * @thread_safety
 * IDictionary functions are thread-safe unless otherwise indicated. Where possible, a shared ("read") lock is held so
 * that multiple threads may query data from a \ref carb::dictionary::Item without blocking each other. Functions that
 * contain `Mutable` in the name, and functions that exchange non-const \ref carb::dictionary::Item pointers will hold
 * an exclusive ("write") lock, which will block any other threads attempting to perform read/write operations on the
 * \ref carb::dictionary::Item. These locks are held at the true-root level of the Item hierarchy which ensures safety
 * across that root Item's hierarchy (see \ref IDictionary::createItem).
 *
 * In some cases, a read or write lock must be held across multiple function calls. An example of this would be a call
 * to \ref getItemChildCount() followed by one or more calls to \ref getItemChildByIndex(). Since you would not want
 * another thread to change the dictionary between the two calls, you must use a lock to keep the state consistent. In
 * this case \ref ScopedWrite and \ref ScopedRead exist to maintain a lock across multiple calls.
 *
 * @par Ordering
 * Dictionary items of type \ref ItemType::eDictionary can function as either an array type (sequential integer keys
 * starting with `0`), or a map type. For map types, dictionary attempts to order child items in the order that they
 * were created, provided that the items were created by \ref createItem(), \ref update(), or \ref duplicateItem() (the
 * "creation functions"). This order is reflected when retrieving child items via \ref getItemChildByIndex(). Performing
 * one of the creation functions on a key that already exists will move it to the end of the order, but merely setting a
 * value on an existing item will not change its order.
 *
 * @par Subscriptions
 * Dictionary \ref Item objects may have subscriptions for notification of changes, either for an individual \ref Item
 * (\ref subscribeToNodeChangeEvents), or a sub-tree (\ref subscribeToTreeChangeEvents). Subscriptions are called in the
 * context of the thread that triggered the change, and only once that thread has fully released the lock for the
 * dictionary hierarchy that contains the changed \ref Item (since looks are at the true-root level). Subscription
 * callbacks also follow the principles of Basic Callback Hygiene:
 * 1. \ref unsubscribeToChangeEvents may be called from within the callback to unregister the called subscription or any
 *    other subscription.
 * 2. Unregistering the subscription ensures that it will never be called again, and any calls in process on another
 *    thread will complete before \ref unsubscribeToChangeEvents returns.
 * 3. The true-root level lock is not held while the callback is called, but may be temporarily taken for API calls
 *    within the callback.
 */
struct IDictionary
{
    // Version 1.0: Initial
    // Version 1.1: Ordering guarantees for createItem(), update(), duplicateItem().
    CARB_PLUGIN_INTERFACE("carb::dictionary::IDictionary", 1, 1)

    /**
     * Returns opaque pointer to read-only item.
     *
     * @param baseItem  Base item to apply path from.  This may not be `nullptr`.
     * @param path      Child path, separated with forward slash ('/').  If provided, the path
     *                  should not start with a forward slash.  This can be `nullptr` or an
     *                  empty string to simply return @p baseItem.
     * @return Opaque item pointer if the item is valid and present, or `nullptr` otherwise.
     */
    const Item*(CARB_ABI* getItem)(const Item* baseItem, const char* path);

    /**
     * Returns opaque pointer to mutable item.
     *
     * @param baseItem  Base item to apply path from (required).
     * @param path      Child path, separated with forward slash ('/'), can be nullptr.  If
     *                  provided, the path should not start with a forward slash.
     * @return Opaque item pointer if the item is valid and present, or `nullptr` otherwise.
     */
    Item*(CARB_ABI* getItemMutable)(Item* baseItem, const char* path);

    /**
     * Returns the number of children that belong to the specified item if it
     * is a dictionary.  Returns 0 if the item is not a dictionary or doesn't exist.
     *
     * @param  item     Item to query the number of children from.  This may not be `nullptr`.
     * @return The number of children if applicable, 0 otherwise.
     */
    size_t(CARB_ABI* getItemChildCount)(const Item* item);

    /**
     * Returns an opaque pointer to a read-only child item by its index in the given base item.
     * This is mostly intended for dynamic dictionary processing.  This function is different
     * from the getItemAt() function in a sense that this function doesn't work with the array
     * view of the supplied item - for example if the item has children named "A", "B", "0", this
     * function will return all of them in an undefined succession.  Meanwhile the getItemAt()
     * function works only with items which have array-like names (e.g. "0", "1", "2", etc.).
     *
     * @param item          Item to query child from.  This may not be `nullptr`.
     * @param childIndex    The 0-based index of the item to retrieve.
     * @return Opaque const item pointer if the item and index are valid, or `nullptr` otherwise.
     */
    const Item*(CARB_ABI* getItemChildByIndex)(const Item* item, size_t childIndex);

    /**
     * Returns an opaque pointer to a mutable child item by its index. Mostly for dynamic
     * dictionary processing.  This function is different from the getItemAtMutable() function
     * in the sense that this function doesn't work with the array view of the supplied item -
     * for example if the item has children named "A", "B", "0", this function will return all
     * of them in an undefined succession.  Meanwhile getItemAt() functions work only with
     * items which has array-like names (e.g. "0", "1", "2", etc.).
     *
     * @param item          Item to query child from.  This may not be `nullptr`.
     * @param childIndex    The 0-based index of the item to retrieve.
     * @return Opaque item pointer if the item and index are valid, or `nullptr` otherwise.
     */
    Item*(CARB_ABI* getItemChildByIndexMutable)(Item* item, size_t childIndex);

    /**
     * Returns the read-only parent item, or `nullptr` if the supplied item is the root item.
     *
     * @param item  Item to get parent for.  This may not be `nullptr`.
     * @return Opaque item pointer if the item is valid and has a parent, or `nullptr` otherwise.
     */
    const Item*(CARB_ABI* getItemParent)(const Item* item);

    /**
     * Returns an opaque pointer to a mutable parent item, or `nullptr` if the supplied item
     * is the root item.
     *
     * @param item  Item to get parent for.  This may not be `nullptr`.
     * @return Opaque item pointer if the item is valid and has a parent, or `nullptr` otherwise.
     */
    Item*(CARB_ABI* getItemParentMutable)(Item* item);

    /**
     * Returns an item's type.  If the item is not a valid item, returns @ref ItemType::eCount.
     *
     * @param item  The item to retrieve the type for.  This may not be `nullptr`.
     * @return The item's type if the item is valid or @ref ItemType::eCount otherwise.
     */
    ItemType(CARB_ABI* getItemType)(const Item* item);

    /**
     * Creates and returns a string buffer filled with the item name.  The string buffer will be
     * allocated in a thread safe manner.
     *
     * @param item  The item to retrieve the name for.  This may not be `nullptr`.
     * @return A newly allocated buffer containing the item's name if the item is valid.  This
     *         buffer must be destroyed using destroyStringBuffer() when it is no longer needed.
     *         Returns `nullptr` if the item is invalid.
     */
    const char*(CARB_ABI* createStringBufferFromItemName)(const Item* item);

    /**
     * Returns a pointer to an item's name if the item is valid.  Note that the returned buffer
     * will be the internal name buffer for the item and will not be in a newly allocated buffer.
     * This should only be used when the caller can guarantee safety around the access.
     *
     * @param item  The item to retrieve the name for.  This may not be `nullptr`.
     * @return Pointer to an internal item name string if the item is valid or `nullptr` otherwise.
     */
    const char*(CARB_ABI* getItemName)(const Item* item);

    /**
     * Creates a new item and all the required items along the given path if necessary.  If the
     * @p baseItem item supplied is `nullptr`, the created item is created as a root dictionary
     * (ie: the returned item does not have a parent item).
     *
     * @param baseItem  Base @ref Item to create the new item(s) under.  Passing `nullptr` means
     *                  that the created item will be a true root (ie: has no parent @ref Item).
     * @param path      Path to the new item relative to the base item @p baseItem.  This may not
     *                  be `nullptr`.
     * @param itemType  The type of the new item to be created at the given path.  This may not be
     *                  @ref ItemType::eCount.
     * @return An opaque @ref Item pointer if it was successfully created or `nullptr` otherwise.
     *         The returned item only needs to be explicitly destroyed if it is created as a root
     *         item or if the created item needs to be removed from the root dictionary.  The
     *         item can be destroyed with destroyItem().
     */
    Item*(CARB_ABI* createItem)(Item* baseItem, const char* path, ItemType itemType);


    /**
     * Checks if the item could be accessible as the provided type, either directly or via a cast.
     *
     * Generally this means for a given @ref ItemType to return `true` for @p item:
     * * @ref ItemType::eDictionary -- @p item must be of type @ref ItemType::eDictionary.
     * * @ref ItemType::eString -- @p item must be of any type except @ref ItemType::eDictionary.
     * * @ref ItemType::eInt -- @p item must be of type @ref ItemType::eInt, @ref ItemType::eFloat,
     *   or @ref ItemType::eBool.  It may also be @ref ItemType::eString if it contains only a
     *   string representation of an integer (in in decimal, hex or octal, as convertible by
     *   `strtoll()`) or a floating-point number (as convertible by `strtod()`).
     * * @ref ItemType::eFloat -- @p item must be of type @ref ItemType::eFloat, @ref ItemType::eInt
     *   or @ref ItemType::eBool.  It may also be @ref ItemType::eString if it contains only a
     *   string representation of a floating point number (as convertible by `strtod()`).
     * * @ref ItemType::eBool -- @p item must be of type @ref ItemType::eBool, @ref ItemType::eInt,
     *   or @ref ItemType::eFloat, or @ref ItemType::eString that either contains only
     *   case-insensitive versions of `"true"` or `"false"` or only a string representation of a
     *   floating point number (as convertible by `strtod()`).
     *
     * @param itemType  The item type to check whether @p item is accessible as.  This may not be
     *                  @ref ItemType::eCount.
     * @param item      The item to check the type accessibility for.  This may not be `nullptr`.
     * @return `true` if accessible as the requested type (see above) or `false` otherwise.
     */
    bool(CARB_ABI* isAccessibleAs)(ItemType itemType, const Item* item);


    /**
     * Attempts to get the supplied item as a 64-bit integer, either directly or via a cast.
     *
     * @param[in] item  The item to retrieve the integer value from.  This may not be `nullptr`.
     * @return The 64 bit integer value of @p item.  This will be converted from the existing
     *         type if this @p item is not a 64-bit integer type.  For an @ref Item of type
     *         `int32_t`, `float` or `double`, this conversion will be a direct cast.
     *         Note that overly large `double` values will convert to `INT64_MIN` on x86_64.
     *         For an @ref Item of string type, the string data will be interpreted as a number.
     *         If the string is not a valid number, 0 will be returned.  If the string is a
     *         valid number, but exceeds the range of an `int64_t`, it will be parsed as a
     *         `double` and converted to an `int64_t` (with the same potential limits as noted
     *         above).
     *
     * @note `carb.dictionary.serializer-toml.plugin` cannot handle integers that
     *       exceed `INT64_MAX`.
     *
     * @note When `carb.dictionary.serializer-json.plugin` reads integers exceeding `UINT64_MAX`,
     *       it will store the result as a double so you may get an unexpected 64-bit integer
     *       value when retrieved.  Unsigned 64-bit values are still retrievable with full
     *       precision though; they will just be wrapped around when returned from this function.
     */
    int64_t(CARB_ABI* getAsInt64)(const Item* item);

    /**
     * Sets the integer value for the supplied item.  If an item was already present, changes its
     * original type to @ref ItemType::eInt.  If the item is an @ref ItemType::eDictionary item,
     * this will destroy all of its children.
     *
     * @param item  The item to set the integer value for.  This may not be `nullptr`.
     * @param value The integer value that will be set to the supplied item.
     */
    void(CARB_ABI* setInt64)(Item* item, int64_t value);

    /**
     * Attempts to get the supplied item's value as 32-bit integer, either directly or via a cast.
     *
     * @warning The value is truncated by casting to 32-bits.  In debug builds, an assert occurs
     *          if the value read from the item would be truncated.
     * @param[in] item  The item to retrieve the integer value from.  This may not be `nullptr`.
     * @return The 32-bit integer value of @p item.  This will be converted from the existing
     *         type if this @ref Item is not a 32-bit integer.  The conversion semantics are the
     *         same as for getAsInt64().  Note that the string conversion behavior has the same
     *         clamping limits as getAsInt64(), which may result in unexpected wraparound
     *         behavior; you should use getAsInt64() instead if you may be reading string values.
     */
    int32_t getAsInt(const Item* item);

    /**
     * Sets the 32-bit integer value for the supplied item.  If a value was already present in
     * the item, the item's type will be changed to @ref ItemType::eInt.  If the present item
     * is a @ref ItemType::eDictionary item, all of its children will be destroyed before setting
     * the new value and changing the type.
     *
     * @param item  The item to set an integer value for.  This may not be `nullptr`.
     * @param value The new integer value that will be set in the supplied item.
     */
    void setInt(Item* item, int32_t value);

    /**
     * Helper function that sets the value of an item at a given path to a 64-bit integer.  The
     * item at the requested path and all items leading up to it will be created if they do not
     * exist.
     *
     * @param baseItem  Base item to apply path from.  This may be `nullptr` to create a new
     *                  dictionary containing the new value at the requested path.
     * @param path      The path to the item to create or modify.  If an item already exists
     *                  at this path, its type will be changed to @ref ItemType::eInt.  If the
     *                  original item was an @ref ItemType::eDictionary, all of its children
     *                  will be destroyed before setting the new integer value.  If no item
     *                  exists at the given path, a new one will be created containing the new
     *                  value.
     * @param value     The new integer value that will be set to the supplied item.
     * @returns The created or modified item if the new value is successfully set or `nullptr`
     *          otherwise.  The returned item only needs to be explicitly destroyed if it is
     *          created as a new root (ie: no parent items) or if it needs to be removed from
     *          the dictionary.  The item can be destroyed with destroyItem().
     */
    Item* makeInt64AtPath(Item* baseItem, const char* path, int64_t value);

    /**
     * Helper function that sets the value of an item at a given path to a 32-bit integer.  The
     * item at the requested path and all items leading up to it will be created if they do not
     * exist.
     *
     * @param baseItem  Base item to apply path from.  This may be `nullptr` to create a new
     *                  dictionary containing the new value at the requested path.
     * @param path      The path to the item to create or modify.  If an item already exists
     *                  at this path, its type will be changed to @ref ItemType::eInt.  If the
     *                  original item was an @ref ItemType::eDictionary, all of its children
     *                  will be destroyed before setting the new integer value.  If no item
     *                  exists at the given path, a new one will be created containing the new
     *                  value.
     * @param value     The new integer value that will be set to the supplied item.
     * @returns The created or modified item if the new value is successfully set or `nullptr`
     *          otherwise.  The returned item only needs to be explicitly destroyed if it is
     *          created as a new root (ie: no parent items) or if it needs to be removed from
     *          the dictionary.  The item can be destroyed with destroyItem().
     */
    Item* makeIntAtPath(Item* baseItem, const char* path, int32_t value);

    /**
     * Attempts to get the supplied item as a float, either directly or via a cast.
     *
     * @param[in] item  The item to retrieve the floating point value from.  This may not be
     *                  `nullptr`.
     * @return The 64-bit floating point value of @p item.  This will be converted from the
     *         existing type if this @ref Item is not a `double`.  For an @ref Item of type
     *         `int32_t`, `int64_t` or `float`, this conversion will be a direct cast.  For an
     *         @ref Item of string type, the string data will be interpreted as a number.
     *         If the string is not a valid number, 0 will be returned.  If the string is a
     *         valid number, but exceeds the range of a `double`, `INFINITY` or `-INFINITY`
     *         will be returned.  Some precision may be lost on overly precise strings.
     */
    double(CARB_ABI* getAsFloat64)(const Item* item);

    /**
     * Sets the floating point value for the supplied item.  If a value was already present,
     * it will be changed to @ref ItemType::eFloat.  If the present item is of type
     * @ref ItemType::eDictionary item, all of its children will be destroyed before setting
     * the new value.
     *
     * @param item  The item to set the new 64-bit floating point value for.  This may not
     *              be `nullptr`.
     * @param value The new floating point value that will be set to the supplied item.  The
     *              item's data type will be changed to @ref ItemType::eFloat if it already
     *              exists.
     */
    void(CARB_ABI* setFloat64)(Item* item, double value);

    /**
     * Attempts to get the supplied item as 32-bit float, either directly or via a cast.
     *
     * @param[in] item  The item to retrieve the 32-bit floating point value from.  This may
     *                  not be `nullptr`.
     * @return The 32-bit floating point value of @p item.  This will be converted from the
     *         existing type if this @ref Item is not a `float`.  The conversion semantics are
     *         the same as with getAsFloat64().
     */
    float getAsFloat(const Item* item);

    /**
     * Sets the 32-bit floating point value for the supplied item.  If a value was already
     * present, it will be changed to @ref ItemType::eFloat.  If the present item is a
     * @ref ItemType::eDictionary item, all of its children will be destroyed before settings
     * the new value.
     *
     * @param item  The item to set the new 32-bit floating point value for.  This may not be
     *              `nullptr`.
     * @param value The new 32-bit floating point value that will be set to the supplied item.
     */
    void setFloat(Item* item, float value);

    /**
     * Helper function that sets the value of an item at a given path to a 64-bit floating point
     * value.  The item at the requested path and all items leading up to it will be created if
     * they do not exist.
     *
     * @param baseItem  Base item to apply path from.  This may be `nullptr` to create a new
     *                  dictionary containing the new value at the requested path.
     * @param path      The path to the item to create or modify.  If an item already exists
     *                  at this path, its type will be changed to @ref ItemType::eFloat.  If the
     *                  original item was an @ref ItemType::eDictionary, all of its children
     *                  will be destroyed before setting the new floating point value.  If no item
     *                  exists at the given path, a new one will be created containing the new
     *                  value.
     * @param value     The new floating point value that will be set to the supplied item.
     * @returns The created or modified item if the new value is successfully set or `nullptr`
     *          otherwise.  The returned item only needs to be explicitly destroyed if it is
     *          created as a new root (ie: no parent items) or if it needs to be removed from
     *          the dictionary.  The item can be destroyed with destroyItem().
     */
    Item* makeFloat64AtPath(Item* baseItem, const char* path, double value);

    /**
     * Helper function that sets the value of an item at a given path to a 32-bit floating point
     * value.  The item at the requested path and all items leading up to it will be created if
     * they do not exist.
     *
     * @param baseItem  Base item to apply path from.  This may be `nullptr` to create a new
     *                  dictionary containing the new value at the requested path.
     * @param path      The path to the item to create or modify.  If an item already exists
     *                  at this path, its type will be changed to @ref ItemType::eFloat.  If the
     *                  original item was an @ref ItemType::eDictionary, all of its children
     *                  will be destroyed before setting the new floating point value.  If no item
     *                  exists at the given path, a new one will be created containing the new
     *                  value.
     * @param value     The new floating point value that will be set to the supplied item.
     * @returns The created or modified item if the new value is successfully set or `nullptr`
     *          otherwise.  The returned item only needs to be explicitly destroyed if it is
     *          created as a new root (ie: no parent items) or if it needs to be removed from
     *          the dictionary.  The item can be destroyed with destroyItem().
     */
    Item* makeFloatAtPath(Item* baseItem, const char* path, float value);

    /**
     * Attempts to get the supplied item as a boolean value, either directly or via a cast.
     *
     * @param item  The item to retrieve the boolean value from.  If the item's type is not
     *              @ref ItemType::eBool, the value will attempt to be cast from other non
     *              dictionary types.  For numeric item types, a zero value is considered
     *              to be `false` and any other value is considered to be `true`.  For string
     *              item types, the value will first be checked if it is a numeric string,
     *              then it will check for values like `true` and `false` (case insensitive).
     *              If a numeric string is found, the value would be converted just as if it
     *              were an integer value.  If the item is a dictionary type, `false` will
     *              always be assumed.
     * @return A boolean value, either directly from the item's value or cast from the item's
     *         type as explained above.  If the item has the type @ref ItemType::eDictionary
     *         or @ref ItemType::eCount (ie: value not set yet on a newly created item), `false`
     *         is always returned.
     */
    bool(CARB_ABI* getAsBool)(const Item* item);

    /**
     * Sets a boolean value for the supplied item.  If an item was already present, its type
     * is changed to @ref ItemType::eBool.  If the present item has the type
     * @ref ItemType::eDictionary, all of the item's children will be destroyed before setting
     * the new value.
     *
     * @param item  The item to set a new boolean value for.  This may not be `nullptr`.
     * @param value The new boolean value that will be set to the supplied item.
     */
    void(CARB_ABI* setBool)(Item* item, bool value);

    /**
     * Helper function that sets the value of an item at a given path to a boolean value.
     * The item at the requested path and all items leading up to it will be created if they
     * do not exist.
     *
     * @param baseItem  Base item to apply path from.  This may be `nullptr` to create a new
     *                  dictionary containing the new value at the requested path.
     * @param path      The path to the item to create or modify.  If an item already exists
     *                  at this path, its type will be changed to @ref ItemType::eBool.  If the
     *                  original item was an @ref ItemType::eDictionary, all of its children
     *                  will be destroyed before setting the new boolean value.  If no item
     *                  exists at the given path, a new one will be created containing the new
     *                  value.
     * @param value     The new boolean value that will be set to the supplied item.
     * @returns The created or modified item if the new value is successfully set or `nullptr`
     *          otherwise.  The returned item only needs to be explicitly destroyed if it is
     *          created as a new root (ie: no parent items) or if it needs to be removed from
     *          the dictionary.  The item can be destroyed with destroyItem().
     */
    Item* makeBoolAtPath(Item* baseItem, const char* path, bool value);

    //! @private
    const char*(CARB_ABI* internalCreateStringBufferFromItemValue)(const Item* item, size_t* pStringLen);

    /**
     * Attempts to create a new string buffer with a value, either the real string value or a
     * string resulting from converting the item value to a string.
     *
     * @param item              The item to retrieve the value as a string from.  This may not be
     *                          `nullptr`.
     * @param[out] pStringLen   Receives the length of the string.  This can be useful if the
     *                          string contains null characters or just to be able to trivially
     *                          know the string's length after it has been retrieved.  This may
     *                          be `nullptr` if the length of the string is not needed.  This
     *                          parameter defaults to `nullptr`.
     * @return A pointer to the created string buffer if if is successfully created, or `nullptr`
     *         otherwise.  When this buffer is no longer needed, it must be destroyed using
     *         @ref destroyStringBuffer().
     */
    const char* createStringBufferFromItemValue(const Item* item, size_t* pStringLen = nullptr) const
    {
        return internalCreateStringBufferFromItemValue(item, pStringLen);
    }

    //! @private
    const char*(CARB_ABI* internalGetStringBuffer)(const Item* item, size_t* pStringLen);

    /**
     * Returns the internal raw data pointer to the string value of an item.  No conversion will
     * be performed on the value before returning.  If the item's type is not a string, `nullptr`
     * will be returned.
     *
     * @warning This function returns the internal string buffer.  Another thread may change the
     *          item's value at any point which can cause the string buffer to be destroyed or
     *          overwritten unexpectedly.  It is recommended to take a @ref ScopedRead lock around
     *          calling this function and using the return value.
     *
     * @param item              The item to retrieve the string buffer pointer for.  This may not
     *                          be `nullptr`.
     * @param[out] pStringLen   Receives the length of the string.  This can be useful if the
     *                          string contains null characters (i.e. byte data) or just to be
     *                          able to trivially know the string's length after its pointer has
     *                          been retrieved.  This may be `nullptr` if the length of the string
     *                          is not needed.  This parameter is optional and defaults to
     *                          `nullptr`.
     * @return The raw pointer to the internal string value if the item has a string value, or
     *         `nullptr` otherwise.
     */
    const char* getStringBuffer(const Item* item, size_t* pStringLen = nullptr)
    {
        return internalGetStringBuffer(item, pStringLen);
    }

    //! @private
    void(CARB_ABI* internalSetString)(Item* item, const char* value, size_t stringLen);

    /**
     * Sets a string value for the supplied item.  If the item @p item is not of type
     * @ref ItemType::eString it is changed to be @ref ItemType::eString.  If the item
     * currently has the type @ref ItemType::eDictionary, all of its children will be
     * destroyed before setting the new string value.  Change notifications for subscriptions
     * are queued to be executed after the value (or type) change is complete.  If @p value
     * is `nullptr`, an empty string will be stored in the item.
     *
     * @param item      The item to set a new string value in.  This may not be `nullptr`.
     * @param value     The new string value that will be set in the supplied item.  This may
     *                  be `nullptr` to store an empty string in the item.
     * @param stringLen The maximum number of characters in the string to copy.  This can be
     *                  useful if only a portion of the string should be copied, or if @p value
     *                  contains null characters (i.e. byte data).  If this value is larger than
     *                  the number of characters in @p value, it is assumed that the caller knows
     *                  that the length to copy.  The copied bytes in that case will include any
     *                  null characters that are encountered.  If this value is set to
     *                  `size_t(-1)`, it is assumed that the string is null terminated and it is
     *                  safe to access its full contents.  This defaults to `size_t(-1)`.
     */
    void setString(Item* item, const char* value, size_t stringLen = size_t(-1)) const
    {
        internalSetString(item, value, stringLen);
    }

    /**
     * Helper function that sets the value of an item at a given path to a string value.  The
     * item at the requested path and all items leading up to it will be created if they do not
     * exist.
     *
     * @param baseItem  Base item to apply path from.  This may be `nullptr` to create a new
     *                  dictionary containing the new value at the requested path.
     * @param path      The path to the item to create or modify.  If an item already exists
     *                  at this path, its type will be changed to @ref ItemType::eString.  If the
     *                  original item was an @ref ItemType::eDictionary, all of its children
     *                  will be destroyed before setting the new string value.  If no item
     *                  exists at the given path, a new one will be created containing the new
     *                  value.
     * @param value     The new string value that will be set to the supplied item.  This string
     *                  will be copied into the item.
     * @param stringLen The maximum number of characters in the string to copy.  This can be
     *                  useful if only a portion of the string should be copied, or if @p value
     *                  contains null characters (i.e. byte data).  If this value is larger than
     *                  the number of characters in @p value, it is assumed that the caller knows
     *                  that the length to copy.  The copied bytes in that case will include any
     *                  null characters that are encountered.  If this value is set to
     *                  `size_t(-1)`, it is assumed that the string is null terminated and it is
     *                  safe to access its full contents.  This defaults to `size_t(-1)`.
     * @returns The created or modified item if the new value is successfully set or `nullptr`
     *          otherwise.  The returned item only needs to be explicitly destroyed if it is
     *          created as a new root (ie: no parent items) or if it needs to be removed from
     *          the dictionary.  The item can be destroyed with destroyItem().
     */
    Item* makeStringAtPath(Item* baseItem, const char* path, const char* value, size_t stringLen = size_t(-1));

    /**
     * Helper function that ensures the item at a given path is a dictionary.  If the item at the
     * given path or any item leading up to its path does not exist, they will be created as
     * needed.
     *
     * @param parentItem    The base item to use the path @p path relative to.  This may be
     *                      `nullptr` to create a new dictionary root with the given path.
     * @param path          The path to the item to create or modify.  If an item already at this
     *                      path, its type will be changed to @ref ItemType::eDictionary if it is
     *                      not already that.  If the item at this path is already a dictionary
     *                      type, it will not be modified.  No specific value will be added to
     *                      the dictionary if it is created.
     * @returns The created or modified item if the new value is successfully set or `nullptr`
     *          otherwise.  The returned item only needs to be explicitly destroyed if it is
     *          created as a new root (ie: no parent items) or if it needs to be removed from
     *          the dictionary.  The item can be destroyed with destroyItem().
     */
    Item* makeDictionaryAtPath(Item* parentItem, const char* path);

    /**
     * Reads the value from an item, converting it if necessary.
     *
     * @tparam T    The type of the value to retrieve the value as from the given item.  This must
     *              be one of the supported dictionary types.  The supported types are `int32_t`,
     *              `int64_t`, `bool`, `float`, `double`, and `const char* `.  Array dictionary
     *              values may also be retrieved with `Int{2|3|4}`, `Uint{2|3|4}`, `Float{2|3|4}`,
     *              or `Double{2|3|4}`.  Unsigned numeric types are not supported and should be
     *              retrieved using their signed conterparts instead.
     * @param item  The item to retrieve the value from.  This may not be `nullptr`.
     * @returns The value of the given item converted to the requested data type.  Note that if a
     *          `const char*` value is returned, it is equivalent to calling getStringBuffer() and
     *          has the same safety warnings.
     */
    template <typename T>
    T get(const dictionary::Item* item);

    /**
     * Reads the value from a path relative to a base item, converting if necessary.
     *
     * @tparam T        The type of the value to retrieve the value as from the given item.  This
     *                  must be one of the supported dictionary types.  The supported types are
     *                  `int32_t`, `int64_t`, `bool`, `float`, `double`, and `const char* `.
     *                  Array dictionary values may also be retrieved with `Int{2|3|4}`,
     *                  `Uint{2|3|4}`, `Float{2|3|4}`, or `Double{2|3|4}`.  Unsigned numeric types
     *                  are not supported and should be retrieved using their signed conterparts
     *                  instead.
     * @param baseItem  The base item that @p path is taken to be relative to.  This may not be
     *                  `nullptr`.
     * @param path      The path to the item relative to @p baseItem to retrieve the value from.
     *                  This can be `nullptr` or an empty string to indicate that the value from
     *                  @p baseItem should be retrieved instead.
     * @returns The value of the given item converted to the requested data type.  Note that if a
     *          `const char*` value is returned, it is equivalent to calling getStringBuffer() and
     *          has the same safety warnings.
     */
    template <typename T>
    T get(const dictionary::Item* baseItem, const char* path);

    /**
     * Helper function that sets the value of an item at a given path to a given value.  The
     * item at the requested path and all items leading up to it will be created if they do not
     * exist.
     *
     * @tparam T        The type of the value to set in the given item path.  This must be one
     *                  of the supported dictionary types.  The supported types are `int32_t`,
     *                  `int64_t`, `bool`, `float`, `double`, `const char* `, `std::string`,
     *                  `carb::cpp::string_view`, and `omni::string`.  Array dictionary values
     *                  may also be set with `Int{2|3|4}`, `Uint{2|3|4}`, `Float{2|3|4}`, or
     *                  `Double{2|3|4}`.  Unsigned numeric types in @p value must either be cast
     *                  to their signed equivalents or an explicit template parameter must be
     *                  provided to allow for an implicit cast.
     * @param baseItem  Base item to apply path from.  This may be `nullptr` to create a new
     *                  dictionary containing the new value at the requested path.
     * @param path      The path to the item to create or modify.  If an item already exists
     *                  at this path, its type will be changed to the @ref ItemType that most
     *                  most closely corresponds to the template parameter type.  If the
     *                  original item was an @ref ItemType::eDictionary, all of its children
     *                  will be destroyed before setting the new value.  If no item exists at
     *                  the given path, a new one will be created containing the new value.
     * @param value     The new value that will be set to the supplied item.  If a string
     *                  value is provided, the string will always be assumed to either be
     *                  wrapped in an object such as `std::string`, `omni::string`, or
     *                  `carb::cpp::string_view`, or that it will be null terminated.  The
     *                  string will be copied into the item's value in full.
     * @returns The created or modified item if the new value is successfully set or `nullptr`
     *          otherwise.  The returned item only needs to be explicitly destroyed if it is
     *          created as a new root (ie: no parent items) or if it needs to be removed from
     *          the dictionary.  The item can be destroyed with destroyItem().
     */
    template <typename T>
    void makeAtPath(dictionary::Item* baseItem, const char* path, T value);

    /**
     * Checks if the given item could be accessible as an array.
     *
     * @param item  The item to check if it can be treated as an array dicitonary.  An array
     *              dictionary has one or more children whose names are contiguous non-negative
     *              integers starting at zero.  The dictionary could also have other children
     *              with non-integer or non-contiguous names as well, but those children will
     *              not be treated as part of the array.
     * @return `true` if the item is accessible as an array and `false` otherwise.  If @p item
     *         has no children (ie: an empty dictionary) it is also considered to not be an array
     *         and `false` will be returned here.
     */
    bool(CARB_ABI* isAccessibleAsArray)(const Item* item);

    /**
     * Checks if the given item could be accessible as the array of items of provided type,
     * either directly or via a cast of all elements.  For this function to return `true`,
     * @ref isAccessibleAsArray() must be satisfied, as well as each child item must satisfy
     * @ref isAccessibleAs() for the given @p itemType.  Empty dictionaries and non-dictionary
     * items will always return `false`.
     *
     * @param itemType  Item type to check for.  This may not be @ref ItemType::eCount.
     * @param item      The item to check whether it can be treated as an array of the requested
     *                  type @p itemType.  This may not be `nullptr`.
     * @return `true` if the given item is a valid array where all child items are accessible as
     *         the requested type.  Returns `false` otherwise.
     */
    bool(CARB_ABI* isAccessibleAsArrayOf)(ItemType itemType, const Item* item);

    /**
     * Checks if the all the children of the item have array-style indices.  This means that all
     * of the names of all child items are consecutive integers starting with 0 or the item has
     * been explicitly flagged as an array internally (ie: the various IDictionary::setArray()
     * functions were used to create it).  If yes, returns the number of children the item has
     * (ie: array elements).
     *
     * @param item  The item to test whether it is being treated purely as an array item.  This
     *              may not be `nullptr`.
     * @return Non-zero number of array elements if the item can be treated as an array (implies
     *         isAccessibleAsArray() also succeeds), or 0 otherwise.
     */
    size_t(CARB_ABI* getArrayLength)(const Item* item);

    /**
     * Runs through all elements of an array and infers a type that is most suitable for the
     * array.  Individual elements in the array may have different item types, but this tries
     * to determine if there is one type that is either most common or can be converted to for
     * each item.
     *
     * The rules for determining the preferred type are thus:
     * - Strings attempt to convert to float or bool if possible (see isAccessibleAs() for
     *   possibilities).
     * - The converted type of the first element is the initial type.  This will be either
     *   @ref ItemType::eBool, @ref ItemType::eFloat, or @ref ItemType::eString.
     * - If the initial type is a @ref ItemType::eBool and later elements can be converted
     *   to @ref ItemType::eBool without losing precision, @ref ItemType::eBool is kept.
     *   The conversion requires that the string value be either "true"/"false" (case
     *   insensitive), or numerical values exactly equal to 0/1.
     * - Elements of type @ref ItemType::eFloat can convert to @ref ItemType::eInt if they
     *   don't lose precision.
     *
     * @param item  The array item to try to determine the preferred type for.  This may not be
     *              `nullptr`.  This item must be a @ref ItemType::eDictionary item.
     * @return The item type that is most suitable for the array, or @ref ItemType::eCount if
     *         a consistent preferred type could not be determined (ie: the item was not a
     *         dictionary or has no children).
     */
    ItemType(CARB_ABI* getPreferredArrayType)(const Item* item);

    /**
     * Attempts to read an array item as a 64-bit integer.
     *
     * Attempts to get the child item as an integer, either directly or via a cast.  This
     * considers the item at the given path to be an array and uses the supplied index to access
     * its child.
     *
     * @param item  The array item to retrieve a value from.  This may not be `nullptr`.
     * @param index The 0-based index of the element in array.  If this index is out of bounds of
     *              the array, 0 will be returned.
     * @return The integer value of the given array element, either directly or cast from the
     *         real item type.  Zero is returned on conversion failure or if the index is out
     *         of bounds of the array's size.
     */
    int64_t(CARB_ABI* getAsInt64At)(const Item* item, size_t index);

    /**
     * Set a 64-bit integer value in an array item.
     *
     * Sets the integer value for the supplied item.  If @p item is not an
     * @ref ItemType::eDictionary type, @p item is changed to an that type and item change
     * notifications are queued.  @p index is used as the name of the child item.  If the child
     * item already exists and is of the type @ref ItemType::eInt, it is updated with the new
     * value.  Otherwise, that array element item and any of its children are destroyed and a
     * new child item is created of type @ref ItemType::eInt.  Finally the new value is set into
     * this new child item.  Change notifications are queued for every change that occurs.
     * Subscriptions are notified of changes when the calling thread no longer holds any locks
     * on the true root of @p item.
     *
     * @param item  The array item to set a new 64-bit integer value in.  This may not be
     *              `nullptr`.  It does not need to already be of type @ref ItemType::eDictionary
     *              or need to already be treated as an array in order for this call to succeed.
     *              However, note that if it is not already seen as an array item (ie: the
     *              isAccessibleAsArray() function succeeds on it), its existing children (if
     *              any) will be destroyed and replaced with the new array item.
     * @param index The 0-based index of the element in array to be set.  Note that new array
     *              items should be created starting with index 0 and filling in consecutively
     *              numbered entries after that.  If later entries are added first, the item
     *              may not be seen as an array by other functions until all other elements
     *              starting from index 0 are added.
     * @param value The new 64-bit integer value that will be set to the given index in the
     *              supplied array item.
     */
    void(CARB_ABI* setInt64At)(Item* item, size_t index, int64_t value);

    /**
     * Attempts to read an array item as a 32-bit integer.
     *
     * Attempts to get the child item as an integer, either directly or via a cast.  This
     * considers the item at the given path to be an array and uses the supplied index to
     * access its child.
     *
     * @param item  The array item to retrieve a value from.  This may not be `nullptr`.
     * @param index The 0-based index of the element in array.  If this index is out of bounds of
     *              the array, 0 will be returned.
     * @return The integer value of the given array element, either value directly or cast from
     *         the real item type.  Zero is returned on conversion failure or if the index is out
     *         of bounds of the array's size.
     */
    int32_t getAsIntAt(const Item* item, size_t index);

    /**
     * Set a 32-bit integer value in an array item.
     *
     * Sets the integer value for the supplied item.  If @p item is not an
     * @ref ItemType::eDictionary type, @p item is changed to an that type and item change
     * notifications are queued.  @p index is used as the name of the child item.  If the child
     * item already exists and is of the type @ref ItemType::eInt, it is updated with the new
     * value.  Otherwise, that array element item and any of its children are destroyed and a
     * new child item is created of type @ref ItemType::eInt.  Finally the new value is set into
     * this new child item.  Change notifications are queued for every change that occurs.
     * Subscriptions are notified of changes when the calling thread no longer holds any locks
     * on the true root of @p item.
     *
     * @param item  The array item to set a new 64-bit integer value in.  This may not be
     *              `nullptr`.  This must be of type @ref ItemType::eDictionary.  It does not
     *              need to already be treated as an array in order for this call to succeed.
     *              However, note that if it is not already seen as an array item (ie: the
     *              isAccessibleAsArray() function succeeds on it), its existing children (if
     *              any) will be destroyed and replaced with the new array item.
     * @param index The 0-based index of the element in array to be set.  Note that new array
     *              items should be created starting with index 0 and filling in consecutively
     *              numbered entries after that.  If later entries are added first, the item
     *              may not be seen as an array by other functions until all other elements
     *              starting from index 0 are added.
     * @param value The new 32-bit integer value that will be set to the given index in the
     *              supplied array item.
     */
    void setIntAt(Item* item, size_t index, int32_t value);

    /**
     * Fills the given buffer with the array values from the given array item.
     *
     * If the provided @p item is not an array item, @p arrayOut is not modified.  If the array
     * item contains more items than @p arrayBufferLength, a warning message is logged and items
     * past the end are ignored.
     *
     * @warning Dictionary items that are not arrays will only have child items with names that
     *          are convertible to array indices (ie: 0-based consecutive integers) written to
     *          @p arrayOut.  For example, if @p item is a dictionary item with keys '5' and '10',
     *          only those items will be written into @p arrayOut.  The other indices will not be
     *          modified.
     *
     * @note It is highly recommended to take a @ref ScopedRead lock around calling this function.
     *       It should also only be called if isAccessibleAsArray() or isAccessibleAsArrayOf()
     *       return `true`.
     *
     * @param item              The array item to retrieve the 64-bit integer values from.  This
     *                          may not be `nullptr`.
     * @param[out] arrayOut     Receives the values read from the array item.  Note that only the
     *                          entries in the array that correspond to the valid indices of the
     *                          array item will be modified in this array.  It is recommended to
     *                          both verify the size of the array item and ensure it has a set of
     *                          contiguous indices before attempting to parse the results.
     * @param arrayBufferLength The maximum number of values that can fit in @p arrayOut.  If the
     *                          array item contains more values than this, only the first
     *                          @p arrayBufferLength values will be retrieved.
     */
    void(CARB_ABI* getAsInt64Array)(const Item* item, int64_t* arrayOut, size_t arrayBufferLength);

    /**
     * Modifies or updates an item to be a 64-bit integer array.
     *
     * The given @p item is changed to have the type @ref ItemType::eDictionary if it is not
     * already.  Any previous value in that item is lost.  If it was already a dictionary,
     * All of the item's existing children will be destroyed (and any applicable change
     * notifications will be queued for affected child items).  New child items will be created
     * for all elements of the given input @p array.
     *
     * @param item          The item to convert to an array and update the given values in.
     *                      This may not be `nullptr`.  This item does not need to already be
     *                      a dictionary or array.  However, if it was all previous children
     *                      will be lost and replaced with the new array of values.  The new
     *                      child items will be given integer names starting from "0" up to
     *                      one less than @p arrayLength.
     * @param array         An array of new 64-bit integer values to use for the contents of
     *                      the new array.  Only the first @p arrayLength entries of this
     *                      array will be used to fill in the new array item's values.
     * @param arrayLength   The total number of valid values in @p array that should be set
     *                      in the given item as array elements.
     */
    void(CARB_ABI* setInt64Array)(Item* item, const int64_t* array, size_t arrayLength);

    /**
     * Fills the given buffer with the array values from the given array item.
     *
     * If the provided @p item is not an array item, @p arrayOut is not modified.  If the array
     * item contains more items than @p arrayBufferLength, a warning message is logged and items
     * past the end are ignored.
     *
     * @warning Dictionary items that are not arrays will only have child items with names that
     *          are convertible to array indices (ie: 0-based consecutive integers) written to
     *          @p arrayOut.  For example, if @p item is a dictionary item with keys '5' and '10',
     *          only those items will be written into @p arrayOut.  The other indices will not be
     *          modified.
     *
     * @note It is highly recommended to take a @ref ScopedRead lock around calling this function.
     *       It should also only be called if isAccessibleAsArray() or isAccessibleAsArrayOf()
     *       return `true`.
     *
     * @param item              The array item to retrieve the 32-bit integer values from.  This
     *                          may not be `nullptr`.
     * @param[out] arrayOut     Receives the values read from the array item.  Note that only the
     *                          entries in the array that correspond to the valid indices of the
     *                          array item will be modified in this array.  It is recommended to
     *                          both verify the size of the array item and ensure it has a set of
     *                          contiguous indices before attempting to parse the results.
     * @param arrayBufferLength The maximum number of values that can fit in @p arrayOut.  If the
     *                          array item contains more values than this, only the first
     *                          @p arrayBufferLength values will be retrieved.
     */
    void(CARB_ABI* getAsIntArray)(const Item* item, int32_t* arrayOut, size_t arrayBufferLength);

    /**
     * Modifies or updates an item to be a 32-bit integer array.
     *
     * The given @p item is changed to have the type @ref ItemType::eDictionary if it is not
     * already.  Any previous value in that item is lost.  If it was already a dictionary,
     * All of the item's existing children will be destroyed (and any applicable change
     * notifications will be queued for affected child items).  New child items will be created
     * for all elements of the given input @p array.
     *
     * @param item          The item to convert to an array and update the given values in.
     *                      This may not be `nullptr`.  This item does not need to already be
     *                      a dictionary or array.  However, if it was all previous children
     *                      will be lost and replaced with the new array of values.  The new
     *                      child items will be given integer names starting from "0" up to
     *                      one less than @p arrayLength.
     * @param array         An array of new 32-bit integer values to use for the contents of
     *                      the new array.  Only the first @p arrayLength entries of this
     *                      array will be used to fill in the new array item's values.
     * @param arrayLength   The total number of valid values in @p array that should be set
     *                      in the given item as array elements.
     */
    void(CARB_ABI* setIntArray)(Item* item, const int32_t* array, size_t arrayLength);

    /**
     * Attempts to read an array item as a 64-bit floating point number.
     *
     * Attempts to get the child item as a 64-bit floating point number, either directly or via
     * a cast.  This considers the item at the given path to be an array and uses the supplied
     * index to access its child.
     *
     * @param item  The array item to retrieve a value from.  This may not be `nullptr`.
     * @param index The 0-based index of the element in array.  If this index is out of bounds of
     *              the array, 0 will be returned.
     * @return The 64-bit floating point value of the given array element, either directly or cast from
     *         the real item type.  Zero is returned on conversion failure or if the index is out
     *         of bounds of the array's size.
     */
    double(CARB_ABI* getAsFloat64At)(const Item* item, size_t index);

    /**
     * Set a 64-bit floating point value in an array item.
     *
     * Sets the floating point value for the supplied item.  If @p item is not an
     * @ref ItemType::eDictionary type, @p item is changed to an that type and item change
     * notifications are queued.  @p index is used as the name of the child item.  If the child
     * item already exists and is of the type @ref ItemType::eFloat, it is updated with the new
     * value.  Otherwise, that array element item and any of its children are destroyed and a
     * new child item is created of type @ref ItemType::eFloat.  Finally the new value is set into
     * this new child item.  Change notifications are queued for every change that occurs.
     * Subscriptions are notified of changes when the calling thread no longer holds any locks
     * on the true root of @p item.
     *
     * @param item  The array item to set a new 64-bit floating point value in.  This may not be
     *              `nullptr`.  It does not need to already be of type @ref ItemType::eDictionary
     *              or need to already be treated as an array in order for this call to succeed.
     *              However, note that if it is not already seen as an array item (ie: the
     *              isAccessibleAsArray() function succeeds on it), its existing children (if
     *              any) will be destroyed and replaced with the new array item.
     * @param index The 0-based index of the element in array to be set.  Note that new array
     *              items should be created starting with index 0 and filling in consecutively
     *              numbered entries after that.  If later entries are added first, the item
     *              may not be seen as an array by other functions until all other elements
     *              starting from index 0 are added.
     * @param value The new 64-bit floating point value that will be set to the given index in the
     *              supplied array item.
     */
    void(CARB_ABI* setFloat64At)(Item* item, size_t index, double value);

    /**
     * Attempts to read an array item as a 32-bit floating point number.
     *
     * Attempts to get the child item as a 32-bit floating point number, either directly or via
     * a cast.  This considers the item at the given path to be an array and uses the supplied
     * index to access its child.
     *
     * @param item  The array item to retrieve a value from.  This may not be `nullptr`.
     * @param index The 0-based index of the element in array.  If this index is out of bounds of
     *              the array, 0 will be returned.
     * @return The 32-bit floating point value of the given array element, either directly or cast from
     *         the real item type.  Zero is returned on conversion failure or if the index is out
     *         of bounds of the array's size.
     */
    float getAsFloatAt(const Item* item, size_t index);

    /**
     * Set a 32-bit floating point value in an array item.
     *
     * Sets the floating point value for the supplied item.  If @p item is not an
     * @ref ItemType::eDictionary type, @p item is changed to an that type and item change
     * notifications are queued.  @p index is used as the name of the child item.  If the child
     * item already exists and is of the type @ref ItemType::eFloat, it is updated with the new
     * value.  Otherwise, that array element item and any of its children are destroyed and a
     * new child item is created of type @ref ItemType::eFloat.  Finally the new value is set into
     * this new child item.  Change notifications are queued for every change that occurs.
     * Subscriptions are notified of changes when the calling thread no longer holds any locks
     * on the true root of @p item.
     *
     * @param item  The array item to set a new 64-bit floating point value in.  This may not be
     *              `nullptr`.  It does not need to already be of type @ref ItemType::eDictionary
     *              or need to already be treated as an array in order for this call to succeed.
     *              However, note that if it is not already seen as an array item (ie: the
     *              isAccessibleAsArray() function succeeds on it), its existing children (if
     *              any) will be destroyed and replaced with the new array item.
     * @param index The 0-based index of the element in array to be set.  Note that new array
     *              items should be created starting with index 0 and filling in consecutively
     *              numbered entries after that.  If later entries are added first, the item
     *              may not be seen as an array by other functions until all other elements
     *              starting from index 0 are added.
     * @param value The new 32-bit floating point value that will be set to the given index in the
     *              supplied array item.
     */
    void setFloatAt(Item* item, size_t index, float value);

    /**
     * Fills the given buffer with the array values from the given array item.
     *
     * If the provided @p item is not an array item, @p arrayOut is not modified.  If the array
     * item contains more items than @p arrayBufferLength, a warning message is logged and items
     * past the end are ignored.
     *
     * @warning Dictionary items that are not arrays will only have child items with names that
     *          are convertible to array indices (ie: 0-based consecutive integers) written to
     *          @p arrayOut.  For example, if @p item is a dictionary item with keys '5' and '10',
     *          only those items will be written into @p arrayOut.  The other indices will not be
     *          modified.
     *
     * @note It is highly recommended to take a @ref ScopedRead lock around calling this function.
     *       It should also only be called if isAccessibleAsArray() or isAccessibleAsArrayOf()
     *       return `true`.
     *
     * @param item              The array item to retrieve the 64-bit floating point values from.
     *                          This may not be `nullptr`.
     * @param[out] arrayOut     Receives the values read from the array item.  Note that only the
     *                          entries in the array that correspond to the valid indices of the
     *                          array item will be modified in this array.  It is recommended to
     *                          both verify the size of the array item and ensure it has a set of
     *                          contiguous indices before attempting to parse the results.
     * @param arrayBufferLength The maximum number of values that can fit in @p arrayOut.  If the
     *                          array item contains more values than this, only the first
     *                          @p arrayBufferLength values will be retrieved.
     */
    void(CARB_ABI* getAsFloat64Array)(const Item* item, double* arrayOut, size_t arrayBufferLength);

    /**
     * Modifies or updates an item to be a 64-bit floating point array.
     *
     * The given @p item is changed to have the type @ref ItemType::eDictionary if it is not
     * already.  Any previous value in that item is lost.  If it was already a dictionary,
     * All of the item's existing children will be destroyed (and any applicable change
     * notifications will be queued for affected child items).  New child items will be created
     * for all elements of the given input @p array.
     *
     * @param item          The item to convert to an array and update the given values in.
     *                      This may not be `nullptr`.  This item does not need to already be
     *                      a dictionary or array.  However, if it was all previous children
     *                      will be lost and replaced with the new array of values.  The new
     *                      child items will be given integer names starting from "0" up to
     *                      one less than @p arrayLength.
     * @param array         An array of new 64-bit floating point values to use for the contents
     *                      of the new array.  Only the first @p arrayLength entries of this
     *                      array will be used to fill in the new array item's values.
     * @param arrayLength   The total number of valid values in @p array that should be set
     *                      in the given item as array elements.
     */
    void(CARB_ABI* setFloat64Array)(Item* item, const double* array, size_t arrayLength);

    /**
     * Fills the given buffer with the array values from the given array item.
     *
     * If the provided @p item is not an array item, @p arrayOut is not modified.  If the array
     * item contains more items than @p arrayBufferLength, a warning message is logged and items
     * past the end are ignored.
     *
     * @warning Dictionary items that are not arrays will only have child items with names that
     *          are convertible to array indices (ie: 0-based consecutive integers) written to
     *          @p arrayOut.  For example, if @p item is a dictionary item with keys '5' and '10',
     *          only those items will be written into @p arrayOut.  The other indices will not be
     *          modified.
     *
     * @note It is highly recommended to take a @ref ScopedRead lock around calling this function.
     *       It should also only be called if isAccessibleAsArray() or isAccessibleAsArrayOf()
     *       return `true`.
     *
     * @param item              The array item to retrieve the 32-bit floating point values from.
     *                          This may not be `nullptr`.
     * @param[out] arrayOut     Receives the values read from the array item.  Note that only the
     *                          entries in the array that correspond to the valid indices of the
     *                          array item will be modified in this array.  It is recommended to
     *                          both verify the size of the array item and ensure it has a set of
     *                          contiguous indices before attempting to parse the results.
     * @param arrayBufferLength The maximum number of values that can fit in @p arrayOut.  If the
     *                          array item contains more values than this, only the first
     *                          @p arrayBufferLength values will be retrieved.
     */
    void(CARB_ABI* getAsFloatArray)(const Item* item, float* arrayOut, size_t arrayBufferLength);

    /**
     * Modifies or updates an item to be a 32-bit floating point array.
     *
     * The given @p item is changed to have the type @ref ItemType::eDictionary if it is not
     * already.  Any previous value in that item is lost.  If it was already a dictionary,
     * All of the item's existing children will be destroyed (and any applicable change
     * notifications will be queued for affected child items).  New child items will be created
     * for all elements of the given input @p array.
     *
     * @param item          The item to convert to an array and update the given values in.
     *                      This may not be `nullptr`.  This item does not need to already be
     *                      a dictionary or array.  However, if it was all previous children
     *                      will be lost and replaced with the new array of values.  The new
     *                      child items will be given integer names starting from "0" up to
     *                      one less than @p arrayLength.
     * @param array         An array of new 32-bit floating point values to use for the contents
     *                      of the new array.  Only the first @p arrayLength entries of this
     *                      array will be used to fill in the new array item's values.
     * @param arrayLength   The total number of valid values in @p array that should be set
     *                      in the given item as array elements.
     */
    void(CARB_ABI* setFloatArray)(Item* item, const float* array, size_t arrayLength);

    /**
     * Attempts to read an array item as a boolean value.
     *
     * Attempts to get the child item as a boolean value, either directly or via a cast.  This
     * considers the item at the given path to be an array and uses the supplied index to access
     * its child.
     *
     * @param item  The array item to retrieve a value from.  This may not be `nullptr`.
     * @param index The 0-based index of the element in array.  If this index is out of bounds of
     *              the array, `false` will be returned.
     * @return The boolean value of the given array element, either value directly or cast from
     *         the real item type.  `false` is returned on conversion failure or if the index is
     *         out of bounds of the array's size.
     */
    bool(CARB_ABI* getAsBoolAt)(const Item* item, size_t index);

    /**
     * Set a boolean value in an array item.
     *
     * Sets the boolean value for the supplied item.  If @p item is not an
     * @ref ItemType::eDictionary type, @p item is changed to an that type and item change
     * notifications are queued.  @p index is used as the name of the child item.  If the child
     * item already exists and is of the type @ref ItemType::eBool, it is updated with the new
     * value.  Otherwise, that array element item and any of its children are destroyed and a
     * new child item is created of type @ref ItemType::eBool.  Finally the new value is set into
     * this new child item.  Change notifications are queued for every change that occurs.
     * Subscriptions are notified of changes when the calling thread no longer holds any locks
     * on the true root of @p item.
     *
     * @param item  The array item to set a new boolean value in.  This may not be `nullptr`.
     *              This must be of type @ref ItemType::eDictionary.  It does not need to already
     *              be treated as an array in order for this call to succeed.  However, note that
     *              if it is not already seen as an array item (ie: the isAccessibleAsArray()
     *              function succeeds on it), its existing children (if any) will be destroyed and
     *              replaced with the new array item.
     * @param index The 0-based index of the element in array to be set.  Note that new array
     *              items should be created starting with index 0 and filling in consecutively
     *              numbered entries after that.  If later entries are added first, the item
     *              may not be seen as an array by other functions until all other elements
     *              starting from index 0 are added.
     * @param value The new boolean value that will be set to the given index in the supplied
     *              array item.
     */
    void(CARB_ABI* setBoolAt)(Item* item, size_t index, bool value);

    /**
     * Fills the given buffer with the array values from the given array item.
     *
     * If the provided @p item is not an array item, @p arrayOut is not modified.  If the array
     * item contains more items than @p arrayBufferLength, a warning message is logged and items
     * past the end are ignored.
     *
     * @warning Dictionary items that are not arrays will only have child items with names that
     *          are convertible to array indices (ie: 0-based consecutive integers) written to
     *          @p arrayOut.  For example, if @p item is a dictionary item with keys '5' and '10',
     *          only those items will be written into @p arrayOut.  The other indices will not be
     *          modified.
     *
     * @note It is highly recommended to take a @ref ScopedRead lock around calling this function.
     *       It should also only be called if isAccessibleAsArray() or isAccessibleAsArrayOf()
     *       return `true`.
     *
     * @param item              The array item to retrieve the boolean values from.  This may not
     *                          be `nullptr`.
     * @param[out] arrayOut     Receives the values read from the array item.  Note that only the
     *                          entries in the array that correspond to the valid indices of the
     *                          array item will be modified in this array.  It is recommended to
     *                          both verify the size of the array item and ensure it has a set of
     *                          contiguous indices before attempting to parse the results.
     * @param arrayBufferLength The maximum number of values that can fit in @p arrayOut.  If the
     *                          array item contains more values than this, only the first
     *                          @p arrayBufferLength values will be retrieved.
     */
    void(CARB_ABI* getAsBoolArray)(const Item* item, bool* arrayOut, size_t arrayBufferLength);

    /**
     * Modifies or updates an item to be a boolean array.
     *
     * The given @p item is changed to have the type @ref ItemType::eDictionary if it is not
     * already.  Any previous value in that item is lost.  If it was already a dictionary,
     * All of the item's existing children will be destroyed (and any applicable change
     * notifications will be queued for affected child items).  New child items will be created
     * for all elements of the given input @p array.
     *
     * @param item          The item to convert to an array and update the given values in.
     *                      This may not be `nullptr`.  This item does not need to already be
     *                      a dictionary or array.  However, if it was all previous children
     *                      will be lost and replaced with the new array of values.  The new
     *                      child items will be given integer names starting from "0" up to
     *                      one less than @p arrayLength.
     * @param array         An array of new boolean values to use for the contents of the new
     *                      array.  Only the first @p arrayLength entries of this array will be
     *                      used to fill in the new array item's values.
     * @param arrayLength   The total number of valid values in @p array that should be set
     *                      in the given item as array elements.
     */
    void(CARB_ABI* setBoolArray)(Item* item, const bool* array, size_t arrayLength);

    //! @private
    const char*(CARB_ABI* internalCreateStringBufferFromItemValueAt)(const Item* item, size_t index, size_t* pStringLen);

    /**
     * Attempts to create new string buffer with a value, either the real string value or a string
     * resulting from converting the item value to a string.  This considers the item to be an
     * array using the supplied index to access the child in question.
     *
     * @param item              The array item to retrieve one of the values from as a string.
     *                          The value of one of its numbered children will be retrieved if the
     *                          given index is in range of the array's size.  This item is assumed
     *                          to be an @ref ItemType::eDictionary type item.  This may not be
     *                          `nullptr`.
     * @param index             The 0-based index of the element in array to copy the value from.
     *                          This must be in the range of the current size of the array.
     * @param[out] pStringLen   Receives the length of the string in characters.  This can be
     *                          useful if the string contains null characters (i.e. byte data).
     *                          This value will be undefined if this function returns `nullptr`.
     *                          This may be `nullptr` if the length of the string is not needed.
     * @return A pointer to the created string buffer if successful.  Once this buffer is no
     *         longer needed, it must be cleaned up using destroyStringBuffer().  Returns
     *         `nullptr` if an error occurred.  Errors can include the index being out of range
     *         of the array or failing to allocate memory.
     */
    const char* createStringBufferFromItemValueAt(const Item* item, size_t index, size_t* pStringLen = nullptr) const
    {
        return internalCreateStringBufferFromItemValueAt(item, index, pStringLen);
    }

    //! @private
    const char*(CARB_ABI* internalGetStringBufferAt)(const Item* item, size_t index, size_t* pStringLen);

    /**
     * Returns the internal raw data pointer to the string value of an item.  No conversion is
     * performed on the item's value.  If the given item does not have an @ref ItemType::eString
     * value, `nullptr` will be returned.  This considers the given item to be an array using the
     * supplied index to access the requested child item.
     *
     * @warning This function is dangerous to use since it can only guarantee safety of the data
     *          when dictionary is not changing.  Since any other thread can change the item at
     *          any other point, it is suggested that a @ref ScopedRead or @ref ScopedWrite lock
     *          be used around any access to the string buffer and its use.
     *
     * @param item              The array item to access an indexed value from.  The value of one
     *                          of its numbered children will be retrieved if the given index is
     *                          in range of the array's size.  This item is assumed to be an
     *                          @ref ItemType::eDictionary type item.  This may not be `nullptr`.
     * @param index             The 0-based index of the element in the array to return the
     *                          internal string buffer for.  This must be in the range of the
     *                          current sizez of the array.
     * @param[out] pStringLen   Receives the length of the string in characters.  This can be
     *                          useful if the string contains null characters (i.e. byte data).
     *                          This value will be undefined if this function returns `nullptr`.
     *                          This may be `nullptr` if the length of the string is not needed.
     * @return The raw pointer to the internal string value if the requested indexed item is
     *         found.  This buffer must not be destroyed or freed in any way.  Its contents
     *         should also not be modified.  Returns `nullptr` the requested array item does
     *         not contain a string buffer (ie: not a string value) or if an error occurs.  Errors
     *         can include the index being out of range of the array.
     */
    const char* getStringBufferAt(const Item* item, size_t index, size_t* pStringLen = nullptr) const
    {
        return internalGetStringBufferAt(item, index, pStringLen);
    }

    //! @private
    void(CARB_ABI* internalSetStringAt)(Item* item, size_t index, const char* value, size_t stringLen);

    /**
     * Sets a string value in the supplied array item.
     *
     * Sets the string value for the given item.  If @p item is not an @ref ItemType::eDictionary,
     * @p item is changed to an @ref ItemType::eDictionary.  Any applicable notifications are
     * queued.  @p index is used as the integer name of the child item to retrieve the value for.
     * If the child item already existed and matches type @ref ItemType::eString it is updated
     * with the new value, otherwise any previous child item is destroyed (along with any of its
     * children) and a new child item is created of type @ref ItemType::eString.  The new value
     * is set into this child item.  Change notifications are queued for every change that occurs.
     * Subscriptions are notified of changes when the calling thread no longer holds any locks on
     * the true root of @p item.
     *
     * @param item          The array item to set a value in.  The item will either have a child
     *                      modified or added to it depending on whether a value at the given
     *                      index already exists or not.  This item is assumed to be an
     *                      @ref ItemType::eDictionary type item.  This may not be `nullptr`.
     * @param index         The 0-based index of the element in the array to set the new string
     *                      value for.  A new child item will be added to the array if the
     *                      requested index is not already present.  Note though that this will
     *                      not fill in any intermediate values in the array if the index is not
     *                      contiguous with the rest of the array's indices.
     * @param value         The new string value that will be set to the given item.  This may
     *                      be `nullptr` or an empty string to clear out the current value in
     *                      the given array item.
     * @param stringLen     The maximum number of characters of the string at @p value to copy.
     *                      This can be useful if only a portion of the string should be copied
     *                      or if @p value contains null characters (i.e. byte data).  The default
     *                      value of `size_t(-1)` treats @p value as a null-terminated string.
     *                      This value is ignored if @p value is `nullptr`.
     */
    void setStringAt(Item* item, size_t index, const char* value, size_t stringLen = size_t(-1)) const
    {
        internalSetStringAt(item, index, value, stringLen);
    }

    /**
     * Returns internal raw data pointers to the string values of all child items of an array.
     * No conversions are performed on the values, so only children of the array that are of
     * @ref ItemType::eString will return a non-`nullptr` value.
     *
     * @warning This function returns the internal string buffer(s) for several items.  Another
     *          thread may change one of the values in the array which can cause the internal
     *          string buffer for that item to be destroyed.  It is recommended to take a
     *          @ref ScopedRead lock around calling this function and use of the filled items
     *          in @p arrayOut.
     *
     * If the provided @p item is not a dictionary item, @p arrayOut is not modified.  If the
     * array item contains more items than @p arrayBufferLength, a warning message is logged
     * and items past the end are ignored.
     *
     * @warning Dictionary items that are not arrays will only have child keys which are
     *          convertible to array indices written to @p arrayOut.  For example, if @p item
     *          is a dictionary item with keys '5' and '10', only those items will be written
     *          into @p arrayOut.  The other indices will not be written.  It is highly
     *          recommended to take a @ref ScopedRead lock around calling this function, and
     *          call only if isAccessibleAsArray() or isAccessibleAsArrayOf() return `true`.
     *
     * @param item              The array item to retrieve the internal string buffer pointers
     *                          from.  All children that have keys that are convertible to
     *                          array indices will have their values filled in @p arrayOut and
     *                          only if those indices are within the range of zero through one
     *                          one less than @p arrayBufferLength inclusive.  This may not be
     *                          `nullptr`.
     * @param[out] arrayOut     Receives the internal data pointers for all array indexed children
     *                          in the array.  This array will be cleared to all `nullptr` before
     *                          retrieving any values.  Any entry that does not correspond to an
     *                          @ref ItemType::eString item in the array will receive `nullptr`.
     *                          This may not be `nullptr`.
     * @param arrayBufferLength The maximum number of entries that can fit in @p arrayOut.  No
     *                          more than this many items will be written to the output array
     *                          @p arrayOut.
     */
    void(CARB_ABI* getStringBufferArray)(const Item* item, const char** arrayOut, size_t arrayBufferLength);

    /**
     * Creates or updates an item to be a string array.
     *
     * If @p item is already an @ref ItemType::eDictionary type, all of its children will be
     * destroyed and replaced by new items with values from @p array.  Any applicable change
     * notifications will be queued as a result of these operations.  If the item is not already
     * an @ref ItemType::eDictionary, its subtree (if any) is destroyed and the item is converted
     * to an @ref ItemType::eDictionary that is treated as an array.  New child items will be
     * created for all elements of the given @p array.
     *
     * @param item          The array item to set new values for.  The entire subtree of this item
     *                      will be destroyed and replaced with the new array entries.  This item
     *                      will also be converted to an @ref ItemType::eDictionary item.  This may
     *                      not be `nullptr`.
     * @param array         An array of string values to be set in each index of the new array
     *                      item.  This may not be `nullptr` and must contain at least
     *                      @p arrayLength entries.  Individual entries may contain `nullptr` or
     *                      an empty string to indicate that the new value at that index should be
     *                      an empty string.
     * @param arrayLength   The number of entries in @p array.  Exactly this many new child items
     *                      will be created as @ref ItemType::eString items under the array.  All
     *                      new child items will have keys that match their index in @p array.
     */
    void(CARB_ABI* setStringArray)(Item* item, const char* const* array, size_t arrayLength);

    /**
     * Returns a read-only child item by its index in an array item.  This is mostly intended for
     * dynamic dictionary processing purposes.  This function is designed for array view access.
     * If you just want to enumerate all children, use getItemChildCount() and
     * getItemChildByIndex() instead.
     *
     * @param item  The array item to retrieve a child item from.  This may not be `nullptr`.
     * @param index The 0-based index of the child item in the array to rertieve.  This must be
     *              within the range of 0 through one less than the current size of the array.
     * @return A read-only item pointer if the array item and index are valid.  Since other
     *         threads could make changes to the dictionary that could cause the returned item
     *         to be destroyed, it is highly recommended that a @ref ScopedRead lock be taken
     *         while working with the returned item.  Returns `nullptr` if the given item is
     *         not an array or no item at the given index exists.
     */
    const Item*(CARB_ABI* getItemAt)(const Item* item, size_t index);

    /**
     * Returns a writable child item by its index in an array item.  This is mostly intended for
     * dynamic dictionary processing purposes.  This function is designed for array view access.
     * If you just want to enumerate all children, use getItemChildCount() and
     * getItemChildByIndex() instead.
     *
     * @param item  The array item to retrieve a child item from.  This may not be `nullptr`.
     * @param index The 0-based index of the child item in the array to rertieve.  This must be
     *              within the range of 0 through one less than the current size of the array.
     * @return A writable item pointer if the array item and index are valid.  Since other
     *         threads could make changes to the dictionary that could cause the returned item
     *         to be destroyed, it is highly recommended that a @ref ScopedRead or
     *         @ref ScopedWrite lock be taken while working with the returned item.  Returns
     *         `nullptr` if the given item is not an array or no item at the given index exists.
     */
    Item*(CARB_ABI* getItemAtMutable)(Item* item, size_t index);

    /**
     * Attempts to securely fill the supplied @p arrayOut buffer with read-only opaque pointers
     * to the items that are array elements.  No more than @p arrayBufferLength item objects
     * will be retrieved.  This function should not be used for simple dynamic processing
     * purposes.  Use getItemChildCount() and getItemChildByIndex() instead.
     *
     * @param item              The array item to retrieve the child items for.  This is expected
     *                          to be an @ref ItemType::eDictionary type item.
     * @param[out] arrayOut     Array buffer to fill with opaque item pointers.
     * @param arrayBufferLength Size of the supplied array buffer.
     */
    void(CARB_ABI* getItemArray)(const Item* item, const Item** arrayOut, size_t arrayBufferLength);

    /**
     * Updates an item to be an array of the given type with provided values.
     *
     * This is a helper function that will call the appropriate API function based on
     * `ArrayElementType`:
     *  * `bool`: will call through to setBoolArray() for each child item.
     *  * `int32_t`: will call through to setIntArray() for each child item.
     *  * `int64_t`: will call through to setInt64Array() for each child item.
     *  * `float`: will call through to setFloatArray() for each child item.
     *  * `double`: will call through to setFloat64Array() for each child item.
     *  * `const char*`: will call through to setStringArray() for each child item.
     *
     * @note Any existing children in @p item are removed.  Change notifications will be queued
     *       where applicable during this operation.
     *
     * @tparam ArrayElementType The type of elements to fill the array with.  This must be a
     *         supported type listed above.  Any other type must be able to be implicitly
     *         converted to a supported type.  Any unsigned values should use their signed
     *         counterparts for this operation.
     *
     * @param item          The item that will be changed to an array type and have its new
     *                      children created.  If this item is an @ref ItemType::eDictionary,
     *                      all of its existing children will be destroyed and new ones created
     *                      from the given array of values.  If this item is not already an
     *                      @ref ItemType::eDictionary, it will be converted to a dictionary
     *                      item to be filled in.  Any required change notifications will be
     *                      queued as the operation proceeds.  This may not be `nullptr`.
     * @param array         An array of values that will be used to fill the children of the new
     *                      array item.  The values are always copied into the new child items.
     *                      This may not be `nullptr`.
     * @param arrayLength   The total number of entries in @p array.  This is used as the size
     *                      of the new array.
     */
    template <typename ArrayElementType>
    void setArray(Item* item, const ArrayElementType* array, size_t arrayLength);

    /**
     * Merges the source item into a destination item.  If an entry exists in the source tree but
     * not in the destination, new items will be created to fill them in if the callback requests
     * that action.  If an entry exists in the destination tree but not in the source tree, that
     * item in the destination tree will be left unmodified.  If an entry exists for any given
     * path in both trees, a callback will be performed to decide how to proceed with the item
     * merge.
     *
     * @param dstBaseItem       The root item that the item to merge the source item and its
     *                          descendants into is taken to be relative to.  The path @p dstPath
     *                          is taken to be relative to this root item and determines where the
     *                          merge operation starts.  This may not be `nullptr`.  This can be
     *                          any item type and does not have to necessarily be a true root item
     *                          in the dictionary.  Note that depending on how the callback
     *                          directs the merge, the type of the item identified by this plus
     *                          the path @p dstPath may be modified.
     * @param dstPath           The item path relative to @p dstBaseItem where the merge operation
     *                          will begin.  This path may be `nullptr` or an empty string to
     *                          indicate that @p dstBaseItem itself should be used as the start of
     *                          the merge.  If the item at this path does not exist, a new item
     *                          will be created at this path to use as the start of the merge.
     * @param srcBaseItem       The root item of the source dictionary that will be merged into
     *                          the destination.  The real source item for the start of the merge
     *                          operation is identified by both this parameter and the path
     *                          @p srcPath.  This may not be `nullptr`.  This can be any item type
     *                          and does not need to be a true root item in the dictionary.
     * @param srcPath           The item path relative to @p srcBaseItem where the merge operation
     *                          will begin.  This path may be `nullptr` or an empty string to
     *                          indicate that @p srcBaseItem itself should be used as the start of
     *                          the merge.  If the item at this path does not exist, the merge
     *                          operation will simply fail immediately with no changes to the
     *                          destination dictionary.
     * @param onUpdateItemFn    Callback function that will direct how the merge operation occurs.
     *                          This callback will be provided with every pair of items that could
     *                          potentially be used in the merge.  This includes items with paths
     *                          that are present in both the source and destination, and items
     *                          with paths that are only present in the source dictionary.  If an
     *                          item path only exists in the destination dictionary, this callback
     *                          will not be performed as it is assumed that item will remain
     *                          unmodified.  This callback will return an action type that
     *                          instructs the merger how to proceed for each item pair.  This may
     *                          not be `nullptr`. Some common callback implementations have been
     *                          provided that can be used in this call as well:
     *                              * carb::dictionary::keepOriginal(): always keeps the item from
     *                                the destination dictionary.  This will essentially always
     *                                leave the destination dictionary unmodified except for item
     *                                paths that don't already exist in it.
     *                              * carb::dictionary::overwriteOriginal(): always replaces the
     *                                destination dictionary item with the matching source item
     *                                at any given path.  This will always favor the source item.
     *                              * carb::dictionary::overwriteOriginalWithArrayHandling(): same
     *                                as above, but will handle items that have been marked as
     *                                arrays even if they are empty.
     * @param userData          Opaque user data pointer that will be passed into the callback
     *                          function on each call.  This value is not interpreted or accessed
     *                          in any way internally, but simply passed unmodified to the
     *                          callback function.  It is the callback implementation's
     *                          responsibility to know how to properly interpret and access this
     *                          value.
     */
    void(CARB_ABI* update)(Item* dstBaseItem,
                           const char* dstPath,
                           const Item* srcBaseItem,
                           const char* srcPath,
                           OnUpdateItemFn onUpdateItemFn,
                           void* userData);

    /**
     * Destroys the given item and all of its children.  Change notifications are queued for each
     * item that is destroyed.
     *
     * @param item  The item to be destroyed.  Its entire subtree will be destroyed as well.  This
     *              may not be `nullptr`.
     */
    void(CARB_ABI* destroyItem)(Item* item);

    /**
     * Frees a string buffer.  When a buffer returned from createStringBufferFromItemValue() or
     * createStringBufferFromItemValueAt() is no longer needed, it must be explicitly destroyed
     * with this function.  Attempting to clean up these buffers in any other way will result in
     * undefined behavior.
     *
     * @param stringBuffer  The string buffer to destroy.  Undefined behavior results if this is
     *                      not a value returned from one of the functions listed above.
     */
    void(CARB_ABI* destroyStringBuffer)(const char* stringBuffer);

    /**
     * Destroys all children of a specified item.  The item itself will not be destroyed.  Change
     * notifications will be queued for each item that is destroyed.
     *
     * @param item  The item to destroy the subtree of.  This may not be `nullptr`.
     */
    void deleteChildren(Item* item);

    /**
     * Retrieves the value of an item's flag.  Flags control how some item processing is handled.
     * @see ItemFlag for more information on available flags and what behaviors each effects.
     *
     * @param item  The item to check the given flag for.  This may not be `nullptr`.
     * @param flag  The flag to check for in the given item.  Only one flag may be specified at a
     *              time.  Since `ItemFlag` is an enum and not a set of bit flags, combining
     *              multiple flags is not allowed.
     * @returns `true` if the requested flag is enabled for the given item, and `false` otherwise.
     */
    bool(CARB_ABI* getItemFlag)(const Item* item, ItemFlag flag);

    /**
     * Sets the new state of an item's flag.  Flags control how some item processing is handled.
     * @see ItemFlag for more information on available flags and what behaviors each effects.
     *
     * @param item      The item to modify the flags for.  This may not be `nullptr`.  This may
     *                  be any type of item, but it is the caller's responsibility to ensure the
     *                  flags that do get set make useful sense for the given item's type.  Some
     *                  flags may not have the desired effect if they are not fully handled for
     *                  the given item type (ie: dictionary vs int/float/bool/string value).
     * @param flag      The flag to set the new state for.  Only one flag may be specified at a
     *                  time.  Since `ItemFlag` is an enum and not a set of bit flags, combining
     *                  multiple flags is not allowed.
     * @param flagValue The new value to set for the flag.  `true` indicates that the flag will
     *                  become enabled while `false` indicates disabled.
     */
    void(CARB_ABI* setItemFlag)(Item* item, ItemFlag flag, bool flagValue);

    /**
     * Copies all flags from one item to another.  Upon return, both items will have the same
     * flags.  The flags for the destination item @p dstItem will be overwritten instead of
     * being merged.
     *
     * @param dstItem   The destination item that will receive the new flags.  Any existing flags
     *                  state in this item will be overwritten.  This may not be `nullptr`.
     * @param srcItem   The source item from which flags are copied.  This item's state will be
     *                  left unmodified.  This may not be `nullptr`.
     */
    void copyItemFlags(Item* dstItem, const Item* srcItem);

    /**
     * Subscribes to receive change events about a specific item.  These notifications arrive
     * in the form of a callback function with a specific change event type and item.  Change
     * notifications will only be queued for operations that directly effect the named item,
     * not for any changes to ancestors in the dictionary.  Multiple change notifications could
     * be queued for a single operation.
     *
     * When finished with the subscription, call unsubscribeToChangeEvents().  It is the caller's
     * responsibility to unsubscribe from all of its notifications before its module shuts down.
     *
     * @param baseItem          The base item to watch for changes relative to.  This may not be
     *                          `nullptr`.  This item may be used as the item to watch for changes
     *                          by passing `nullptr` or an empty string for @p path.
     * @param path              The subpath relative to @p baseItem that indicates the item to
     *                          watch.  This may be `nullptr` or an empty string to allow the
     *                          given item @p baseItem to be watched directly for changes.
     * @param onChangeEventFn   The callback function to call when a change event occurs.  This
     *                          callback will provide the item object for reference, the type of
     *                          change that either occurred or will occur (@see ChangeEventType
     *                          for more info on when each type of event is sent relative to the
     *                          operationthat generated the notification), and the user data
     *                          provided in @p userData.  This may not be `nullptr`.
     * @param userData          An opaque data object that will be passed to the callback function
     *                          @p onChangeEventFn any time it is called.  This object will not be
     *                          accessed or interpreted internally.  It is the callback function
     *                          implementation's responsibility to know how to properly and safely
     *                          interpret this value.
     * @return A subscription handle that can be used with unsubscribeToChangeEvents() if the
     *         subscription is successfully registered.  Returns `nullptr` if an error occured.
     */
    SubscriptionId*(CARB_ABI* subscribeToNodeChangeEvents)(Item* baseItem,
                                                           const char* path,
                                                           OnNodeChangeEventFn onChangeEventFn,
                                                           void* userData);
    /**
     * Subscribes to change events for all items in a subtree.  These notifications arrive in the
     * form of a callback function with a specific change event type and item.  Change
     * notifications will be queued for operations that directly affect the named item or for
     * changes to any of its descendants in the dictionary.  Multiple change notifications could
     * be queued for any single operation.
     *
     * When finished with the subscription, call unsubscribeToChangeEvents().  It is the caller's
     * responsibility to unsubscribe from all of its notifications before its module shuts down.
     *
     * @param baseItem          The base item to watch for changes relative to.  This may not be
     *                          `nullptr`.  This item may be used as the root item to watch for
     *                          changes on by passing `nullptr` or an empty string for @p path.
     * @param path              The subpath relative to @p baseItem that indicates the root of the
     *                          subtree to watch.  This may be `nullptr` or an empty string to
     *                          allow the given item @p baseItem to be used as the root of the
     *                          subtree to watch for changes.
     * @param onChangeEventFn   The callback function to call when a change event occurs for
     *                          either the named item or its subtree.  This callback will provide
     *                          the item object for reference, the type of change that either
     *                          occurred or will occur (@see ChangeEventType for more info on when
     *                          each type of event is sent relative to the operationthat generated
     *                          the notification), and the user data provided in @p userData.
     *                          This may not be `nullptr`.
     * @param userData          An opaque data object that will be passed to the callback function
     *                          @p onChangeEventFn any time it is called.  This object will not be
     *                          accessed or interpreted internally.  It is the callback function
     *                          implementation's responsibility to know how to properly and safely
     *                          interpret this value.
     * @return A subscription handle that can be used with unsubscribeToChangeEvents() if the
     *         subscription is successfully registered.  Returns `nullptr` if an error occured.
     */
    SubscriptionId*(CARB_ABI* subscribeToTreeChangeEvents)(Item* baseItem,
                                                           const char* path,
                                                           OnTreeChangeEventFn onChangeEventFn,
                                                           void* userData);

    /**
     * Unsubscribes from change events.  This may be used to clean up the subscription object
     * for both node change subscriptions returned from subscribeToNodeChangeEvents() and tree
     * change subscriptions from subscribeToTreeChangeEvents().  This call may block temporarily
     * if an affected change notification callback is still in progress.  Upon return, it is
     * guaranteed both that no more change notifications will arrive for the given subscription
     * and that any pending change callbacks have finished executing.
     *
     * @param subscriptionId    The subscription handle from subscribeToNodeChangeEvents() or
     *                          subscribeToTreeChangeEvents() to unsubscribe from.  This may
     *                          not be `nullptr`.
     */
    void(CARB_ABI* unsubscribeToChangeEvents)(SubscriptionId* subscriptionId);

    /**
     * Unsubscribes all node change handles for a specific Item.  This may be used to ensure that
     * no more node change notifications will occur for a given item.  Tree change notifications
     * may still occur however if the given item is part of another watched subtree.  This may
     * block temporarily if an affected change notification callback is still in progress.  Upon
     * return, it is guaranteed both that no more node change notifications will arrive for the
     * given item, and that any pending change callbacks have finished executing.
     *
     * @param item  The item to remove any pending node change notification subscriptions from.
     *              Only node subscriptions will be removed and unregistered.  Tree change
     *              notifications could still occur on this item if another tree subscription is
     *              registered on an ancestor.  This may not be `nullptr`.
     */
    void(CARB_ABI* unsubscribeItemFromNodeChangeEvents)(Item* item);

    /**
     * Unsubscribes all subtree change handles for a specific Item.  This may be used to ensure
     * that all tree change notification subscriptions will be removed from the given item and
     * unregistered.  Only tree change subscriptions that were registered directly on the given
     * item will be unregistered.  If this item is in the subtree of another ancestor's tree
     * change subscription, those other higher subscriptions will not be removed.  Upon return,
     * it is guaranteed that both no more tree change notifications will arrive for subscriptsions
     * that were watching the subtree of the given item, and that any pending change callbacks
     * have finished executing.
     *
     * @param item  The item to remove any pending tree change notification subscriptions from.
     *              Only tree subscriptions will be removed and unregistered, and only
     *              subscriptions that were registered directly on the given item will be removed.
     *              Node change notifications could still occur on this item if they were also
     *              registered for it.  This may not be `nullptr`.
     */
    void(CARB_ABI* unsubscribeItemFromTreeChangeEvents)(Item* item);

    /**
     * Locks an Item for reading.
     *
     * Mutex-locks `item` for reading. This is only necessary if you are doing multiple read
     * operations and require thread-safe consistency across the multiple operations. May be
     * called multiple times within a thread, but unlock() must be called for each readLock()
     * call, once the read lock is no longer needed.
     *
     * @warning Do not use readLock() directly; prefer @ref ScopedRead instead.
     * @warning If a read lock is held and the same thread later takes a write lock, all locks
     *          will be released for a brief period of time, in which case another thread may
     *          be able to make changes.
     *
     * @see unlock writeLock ScopedRead ScopedWrite
     *
     * @param item  The item to read-lock. `item`'s entire hierarchy will be read-locked.  This
     *              may not be `nullptr` since it may cause synchronization issues.  `item` must
     *              not be destroyed while the read lock is held.  The same `item` should be
     *              passed to unlock() to unlock this same item at a later point.
     */
    void(CARB_ABI* readLock)(const Item* item);

    /**
     * Locks an Item for writing.
     *
     * Mutex-locks `item` for writing (exclusive access). This is only necessary if you are doing
     * multiple read/write operations and require thread-safe consistency across the multiple
     * operations. May be called multiple times within a thread, but unlock() must be called for
     * each writeLock() call, once the write lock is no longer needed. Calling writeLock() when a
     * readLock() is already held will release the lock and wait until exclusive write lock can be
     * gained.
     *
     * @warning Do not use writeLock() directly; prefer @ref ScopedWrite instead.
     *
     * @see readLock unlock ScopedRead ScopedWrite
     *
     * @param item  The item to write-lock. `item`'s entire hierarchy will be write-locked.  This
     *              may not be `nullptr` since it may cause synchronization issues.  `item` must
     *              not be destroyed while the write lock is held.  The same `item` should be
     *              passed to unlock() to unlock this same item at a later point.
     */
    void(CARB_ABI* writeLock)(Item* item);

    /**
     * Releases a lock from a prior readLock() or writeLock().
     *
     * Releases a held read- or write-lock. Must be called once for each read- or write-lock that
     * is held. Must be called in the same thread that initiated the read- or write-lock.
     *
     * @warning Do not use unlock() directly; prefer using \ref ScopedWrite or \ref ScopedRead
     *          instead.
     *
     * @see readLock writeLock ScopedRead ScopedWrite
     *
     * @param item  The item to unlock. `item`'s entire hierarchy will be unlocked.  Another
     *              thread may only acquire this lock once all locks owned by the calling
     *              thread have been unlocked.  This may not be `nullptr`.
     */
    void(CARB_ABI* unlock)(const Item* item);

    /**
     * Returns a 128-bit hash representing the value.  This hash uses the FNV128 algorithm.  The
     * hash will be invariant of the order of children in each item.  Each item in the tree will
     * use its key name, type, flags, and value (if any) to contribute to the hash.  The hash can
     * be used to compare two dictionaries for equality or to provide a way of including multiple
     * dictionaries in a hash map container.
     *
     * We guarantee that the hashing algorithm will not change unless the version number of the
     * interface changes.  These hashes should not be considered for persistent storage purposes
     * for this reason.
     *
     * @param item  The item to take the hash of.  This may not be `nullptr`.  The item's
     *              information as well as the information of each of its descendants will be
     *              included in the hash calculation.
     * @return The 128-bit hash of the item.  This hash is guaranteed to be invariant for a given
     *         dictionary within the same process and interface version.  The calculation of the
     *         hash may have a different result for a given dictionary in future interface
     *         versions however.
     */
    const extras::hash128_t(CARB_ABI* getHash)(const Item* item);

    /** @private */
    Item*(CARB_ABI* duplicateItemInternal)(const Item* item, Item* newParent, const char* newKey);

    /**
     * Lexicographically compares two Items.
     *
     * The items being compared do not need to be root items. If the items are a key of a parent
     * object, that key is not included in the comparison.
     *
     * The rules match https://en.cppreference.com/w/cpp/algorithm/lexicographical_compare,
     * treating the key and values in the dictionary as an ordered set. The "type" is included in
     * the comparison, however the rules of what types are ordered differently than others may
     * change on a version change of this interface.
     *
     * The function will return a negative, zero, or positive number. The magnitude of the number
     * bears no importance, and shouldn't be assumed to.  A negative number means that
     * itemA < itemB, zero itemA = itemB, and positive itemA > itemB.
     *
     * @param itemA The first item to compare.  This may not be `nullptr`.
     * @param itemB The second item to compare.  This may not be `nullptr`.
     * @returns The result of a lexicographical compare of itemA and itemB.  A negative value
     *          indicates that @p itemA should be ordered before @p itemB.  A positive value
     *          indicates that @p itemA should be ordered after @p itemB.  A zero value
     *          indicates that items @p itemA and @p itemB are equal.
     */
    int(CARB_ABI* lexicographicalCompare)(const Item* itemA, const Item* itemB);

    /**
     * Duplicates a given item as a new dictionary root.  The given item will have its entire
     * subtree duplicated as well.  The new item will not be attached to any other dictionary
     * and can be treated as its own dictionary root.  The caller is responsible for cleaning
     * up the duplicated item when it is no longer needed.
     *
     * @param item  The item to duplicate.  This may not be `nullptr`.  The entire subtree of
     *              this item will also be duplicated.
     * @returns The newly duplicated item if successful.  This new item will be its own dictionary
     *          root and must be explicitly cleaned up with destroyItem() when it is no longer
     *          needed.  Change notifications will not be triggered since the duplicated item will
     *          not have any existing subscriptions copied to it and the original item will not be
     *          modified.  Returns `nullptr` if an error occurs.
     */
    Item* duplicateItem(const Item* item)
    {
        return duplicateItemInternal(item, nullptr, nullptr);
    }

    /**
     * Duplicates an item and places the new copy under a different parent item.  The given
     * item will have its entire subtree duplicated as well.  If the given key already exists
     * on the new parent, it and all its children will be overwritten by the new duplicated
     * item.  Any applicable change events will be queued for the overwritten items.
     *
     * @param item      The item to duplicate.  This may not be `nullptr`.  The entire subtree
     *                  of this item will also be duplicated.
     * @param newParent The new parent item to attach the duplicated item to.  This may be
     *                  `nullptr` to return the duplicated item as its own independent dictionary.
     *                  If this item is returned without attaching it to a new parent, it is the
     *                  caller's responsibility to destroy the item with destroyItem() when it is
     *                  no longer needed.
     * @param newKey    If a new parent item is given in @p newParent, this name specifies the key
     *                  used to store the duplicated item in the parent.  The new key name may not
     *                  contain path separators (ie: '/').  This parameter is ignored if the
     *                  @p newParent parameter is `nullptr`.  This may not be `nullptr` unless
     *                  @p newParent is also `nullptr`.
     * @returns The newly duplicated item if successful.  If @p newParent was `nullptr`, this new
     *          item must be explicitly destroyed with destroyItem() when it is no longer needed.
     *          If @p newParent is not `nullptr`, the duplicated item will be owned by that new
     *          parent and will be automatically destroyed when that parent item is destroyed.
     *          Change notifications will have been triggered for the new item if a new parent was
     *          given or an existing item was overwritten.  Existing subscriptions on any
     *          duplicated items will not be duplicated into the new item(s).  Returns `nullptr` if
     *          an error occurs.
     */
    Item* duplicateItem(const Item* item, Item* newParent, const char* newKey)
    {
        return duplicateItemInternal(item, newParent, newKey);
    }
};

/**
 * A helper class for calling writeLock() and unlock(). Similar to `std::unique_lock`.
 */
class ScopedWrite
{
    const IDictionary* m_pDictionary;
    Item* m_pItem;

public:
    /**
     * RAII constructor. Immediately takes a write lock until *this is destroyed.
     * @note Dictionary locks are recursive.
     * @warning If the current thread already owns a read lock (i.e. via \ref ScopedRead), promotion to a write lock
     *   necessitates *releasing* all locks and then waiting for a write lock. This can cause state to change. Always
     *   re-evaluate state if this is the case.
     * @param dictionary A reference to \ref IDictionary.
     * @param item The item in the subtree to lock. The root of this item is found and the entire subtree from the root
     * is locked. **NOTE:** Undefined behavior occurs if `item` is destroyed before `*this` is destroyed.
     */
    ScopedWrite(const IDictionary& dictionary, Item* item) : m_pDictionary(std::addressof(dictionary)), m_pItem(item)
    {
        m_pDictionary->writeLock(m_pItem);
    }
    //! Destructor. Releases the write lock.
    ~ScopedWrite()
    {
        m_pDictionary->unlock(m_pItem);
    }
    CARB_PREVENT_COPY_AND_MOVE(ScopedWrite);
};

/**
 * A helper class for calling readLock() and unlock(). Similar to `std::shared_lock`.
 */
class ScopedRead
{
    const IDictionary* m_pDictionary;
    const Item* m_pItem;

public:
    /**
     * RAII constructor. Immediately takes a read lock until *this is destroyed.
     *
     * @note Dictionary locks are recursive.
     * @param dictionary A reference to \ref IDictionary.
     * @param item The item in the subtree to lock. The root of this item is found and the entire subtree from the root
     * is locked. **NOTE:** Undefined behavior occurs if `item` is destroyed before `*this` is destroyed.
     */
    ScopedRead(const IDictionary& dictionary, const Item* item)
        : m_pDictionary(std::addressof(dictionary)), m_pItem(item)
    {
        m_pDictionary->readLock(m_pItem);
    }
    //! Destructor. Releases the read lock.
    ~ScopedRead()
    {
        m_pDictionary->unlock(m_pItem);
    }
    CARB_PREVENT_COPY_AND_MOVE(ScopedRead);
};

inline int32_t IDictionary::getAsInt(const Item* item)
{
    auto val = getAsInt64(item);
    CARB_ASSERT(val >= INT_MIN && val <= INT_MAX);
    return int32_t(val);
}
inline void IDictionary::setInt(Item* item, int32_t value)
{
    setInt64(item, static_cast<int64_t>(value));
}
inline Item* IDictionary::makeIntAtPath(Item* baseItem, const char* path, int32_t value)
{
    return makeInt64AtPath(baseItem, path, static_cast<int64_t>(value));
}

inline float IDictionary::getAsFloat(const Item* item)
{
    return static_cast<float>(getAsFloat64(item));
}
inline void IDictionary::setFloat(Item* item, float value)
{
    setFloat64(item, static_cast<double>(value));
}
inline Item* IDictionary::makeFloatAtPath(Item* baseItem, const char* path, float value)
{
    return makeFloat64AtPath(baseItem, path, static_cast<double>(value));
}

inline int32_t IDictionary::getAsIntAt(const Item* item, size_t index)
{
    auto val = getAsInt64At(item, index);
    CARB_ASSERT(val >= INT_MIN && val <= INT_MAX);
    return int32_t(val);
}

inline void IDictionary::setIntAt(Item* item, size_t index, int32_t value)
{
    setInt64At(item, index, static_cast<int64_t>(value));
}

inline float IDictionary::getAsFloatAt(const Item* item, size_t index)
{
    return static_cast<float>(getAsFloat64At(item, index));
}

inline void IDictionary::setFloatAt(Item* item, size_t index, float value)
{
    setFloat64At(item, index, static_cast<double>(value));
}

inline Item* IDictionary::makeInt64AtPath(Item* parentItem, const char* path, int64_t value)
{
    ScopedWrite g(*this, parentItem);
    Item* item = getItemMutable(parentItem, path);
    if (!item)
    {
        item = createItem(parentItem, path, ItemType::eInt);
    }
    setInt64(item, value);
    return item;
}

inline Item* IDictionary::makeFloat64AtPath(Item* parentItem, const char* path, double value)
{
    ScopedWrite g(*this, parentItem);
    Item* item = getItemMutable(parentItem, path);
    if (!item)
    {
        item = createItem(parentItem, path, ItemType::eFloat);
    }
    setFloat64(item, value);
    return item;
}

inline Item* IDictionary::makeBoolAtPath(Item* parentItem, const char* path, bool value)
{
    ScopedWrite g(*this, parentItem);
    Item* item = getItemMutable(parentItem, path);
    if (!item)
    {
        item = createItem(parentItem, path, ItemType::eBool);
    }
    setBool(item, value);
    return item;
}

inline Item* IDictionary::makeStringAtPath(Item* parentItem, const char* path, const char* value, size_t stringLen)
{
    ScopedWrite g(*this, parentItem);
    Item* item = getItemMutable(parentItem, path);
    if (!item)
    {
        item = createItem(parentItem, path, ItemType::eString);
    }
    setString(item, value, stringLen);
    return item;
}

inline Item* IDictionary::makeDictionaryAtPath(Item* parentItem, const char* path)
{
    ScopedWrite g(*this, parentItem);
    Item* item = getItemMutable(parentItem, path);
    if (!item)
    {
        item = createItem(parentItem, path, ItemType::eDictionary);
        return item;
    }
    ItemType itemType = getItemType(item);
    if (itemType != ItemType::eDictionary)
    {
        destroyItem(item);
        item = createItem(parentItem, path, ItemType::eDictionary);
    }
    return item;
}

#ifndef DOXYGEN_BUILD
template <>
inline int32_t IDictionary::get<int32_t>(const dictionary::Item* item)
{
    return getAsInt(item);
}

template <>
inline int64_t IDictionary::get<int64_t>(const dictionary::Item* item)
{
    return getAsInt64(item);
}

template <>
inline float IDictionary::get<float>(const dictionary::Item* item)
{
    return getAsFloat(item);
}

template <>
inline double IDictionary::get<double>(const dictionary::Item* item)
{
    return getAsFloat64(item);
}

template <>
inline bool IDictionary::get<bool>(const dictionary::Item* item)
{
    return getAsBool(item);
}

template <>
inline const char* IDictionary::get<const char*>(const dictionary::Item* item)
{
    return getStringBuffer(item);
}

template <>
inline Int2 IDictionary::get<Int2>(const dictionary::Item* item)
{
    Int2 value;
    getAsIntArray(item, &value.x, 2);
    return value;
}
template <>
inline Int3 IDictionary::get<Int3>(const dictionary::Item* item)
{
    Int3 value;
    getAsIntArray(item, &value.x, 3);
    return value;
}
template <>
inline Int4 IDictionary::get<Int4>(const dictionary::Item* item)
{
    Int4 value;
    getAsIntArray(item, &value.x, 4);
    return value;
}

template <>
inline Uint2 IDictionary::get<Uint2>(const dictionary::Item* item)
{
    int64_t value[2];
    getAsInt64Array(item, value, 2);
    return { static_cast<uint32_t>(value[0]), static_cast<uint32_t>(value[1]) };
}
template <>
inline Uint3 IDictionary::get<Uint3>(const dictionary::Item* item)
{
    int64_t value[3];
    getAsInt64Array(item, value, 3);
    return { static_cast<uint32_t>(value[0]), static_cast<uint32_t>(value[1]), static_cast<uint32_t>(value[2]) };
}
template <>
inline Uint4 IDictionary::get<Uint4>(const dictionary::Item* item)
{
    int64_t value[4];
    getAsInt64Array(item, value, 4);
    return { static_cast<uint32_t>(value[0]), static_cast<uint32_t>(value[1]), static_cast<uint32_t>(value[2]),
             static_cast<uint32_t>(value[3]) };
}

template <>
inline Float2 IDictionary::get<Float2>(const dictionary::Item* item)
{
    Float2 value;
    getAsFloatArray(item, &value.x, 2);
    return value;
}
template <>
inline Float3 IDictionary::get<Float3>(const dictionary::Item* item)
{
    Float3 value;
    getAsFloatArray(item, &value.x, 3);
    return value;
}
template <>
inline Float4 IDictionary::get<Float4>(const dictionary::Item* item)
{
    Float4 value;
    getAsFloatArray(item, &value.x, 4);
    return value;
}

template <>
inline Double2 IDictionary::get<Double2>(const dictionary::Item* item)
{
    Double2 value;
    getAsFloat64Array(item, &value.x, 2);
    return value;
}
template <>
inline Double3 IDictionary::get<Double3>(const dictionary::Item* item)
{
    Double3 value;
    getAsFloat64Array(item, &value.x, 3);
    return value;
}
template <>
inline Double4 IDictionary::get<Double4>(const dictionary::Item* item)
{
    Double4 value;
    getAsFloat64Array(item, &value.x, 4);
    return value;
}


template <class T>
inline T IDictionary::get(const dictionary::Item* baseItem, const char* path)
{
    return get<T>(getItem(baseItem, path));
}

template <>
inline void IDictionary::makeAtPath<int32_t>(dictionary::Item* baseItem, const char* path, int32_t value)
{
    makeIntAtPath(baseItem, path, value);
}

template <>
inline void IDictionary::makeAtPath<int64_t>(dictionary::Item* baseItem, const char* path, int64_t value)
{
    makeInt64AtPath(baseItem, path, value);
}

template <>
inline void IDictionary::makeAtPath<float>(dictionary::Item* baseItem, const char* path, float value)
{
    makeFloatAtPath(baseItem, path, value);
}

template <>
inline void IDictionary::makeAtPath<double>(dictionary::Item* baseItem, const char* path, double value)
{
    makeFloat64AtPath(baseItem, path, value);
}

template <>
inline void IDictionary::makeAtPath<bool>(dictionary::Item* baseItem, const char* path, bool value)
{
    makeBoolAtPath(baseItem, path, value);
}

template <>
inline void IDictionary::makeAtPath<const char*>(dictionary::Item* baseItem, const char* path, const char* value)
{
    makeStringAtPath(baseItem, path, value);
}

template <>
inline void IDictionary::makeAtPath<std::string>(dictionary::Item* baseItem, const char* path, std::string value)
{
    makeStringAtPath(baseItem, path, value.data(), value.size());
}

template <>
inline void IDictionary::makeAtPath<cpp::string_view>(dictionary::Item* baseItem, const char* path, cpp::string_view value)
{
    makeStringAtPath(baseItem, path, value.data(), value.length());
}

template <>
inline void IDictionary::makeAtPath<omni::string>(dictionary::Item* baseItem, const char* path, omni::string value)
{
    makeStringAtPath(baseItem, path, value.data(), value.size());
}

template <>
inline void IDictionary::setArray(Item* baseItem, const bool* array, size_t arrayLength)
{
    setBoolArray(baseItem, array, arrayLength);
}

template <>
inline void IDictionary::setArray(Item* baseItem, const int32_t* array, size_t arrayLength)
{
    setIntArray(baseItem, array, arrayLength);
}

template <>
inline void IDictionary::setArray(Item* baseItem, const int64_t* array, size_t arrayLength)
{
    setInt64Array(baseItem, array, arrayLength);
}

template <>
inline void IDictionary::setArray(Item* baseItem, const float* array, size_t arrayLength)
{
    setFloatArray(baseItem, array, arrayLength);
}

template <>
inline void IDictionary::setArray(Item* baseItem, const double* array, size_t arrayLength)
{
    setFloat64Array(baseItem, array, arrayLength);
}

template <>
inline void IDictionary::setArray(Item* baseItem, const char* const* array, size_t arrayLength)
{
    setStringArray(baseItem, array, arrayLength);
}

template <>
inline void IDictionary::makeAtPath<Int2>(dictionary::Item* baseItem, const char* path, Int2 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }
    setArray<int32_t>(item, &value.x, 2);
}
template <>
inline void IDictionary::makeAtPath<Int3>(dictionary::Item* baseItem, const char* path, Int3 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }
    setArray<int32_t>(item, &value.x, 3);
}
template <>
inline void IDictionary::makeAtPath<Int4>(dictionary::Item* baseItem, const char* path, Int4 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }
    setArray<int32_t>(item, &value.x, 4);
}

template <>
inline void IDictionary::makeAtPath<Uint2>(dictionary::Item* baseItem, const char* path, Uint2 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }

    int64_t values64[] = { value.x, value.y };

    setArray<int64_t>(item, values64, 2);
}
template <>
inline void IDictionary::makeAtPath<Uint3>(dictionary::Item* baseItem, const char* path, Uint3 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }

    int64_t values64[] = { value.x, value.y, value.z };

    setArray<int64_t>(item, values64, 3);
}
template <>
inline void IDictionary::makeAtPath<Uint4>(dictionary::Item* baseItem, const char* path, Uint4 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }

    int64_t values64[] = { value.x, value.y, value.z, value.w };

    setArray<int64_t>(item, values64, 4);
}


template <>
inline void IDictionary::makeAtPath<Float2>(dictionary::Item* baseItem, const char* path, Float2 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }
    setArray<float>(item, &value.x, 2);
}
template <>
inline void IDictionary::makeAtPath<Float3>(dictionary::Item* baseItem, const char* path, Float3 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }
    setArray<float>(item, &value.x, 3);
}
template <>
inline void IDictionary::makeAtPath<Float4>(dictionary::Item* baseItem, const char* path, Float4 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }
    setArray<float>(item, &value.x, 4);
}

template <>
inline void IDictionary::makeAtPath<Double2>(dictionary::Item* baseItem, const char* path, Double2 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }
    setArray<double>(item, &value.x, 2);
}
template <>
inline void IDictionary::makeAtPath<Double3>(dictionary::Item* baseItem, const char* path, Double3 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }
    setArray<double>(item, &value.x, 3);
}
template <>
inline void IDictionary::makeAtPath<Double4>(dictionary::Item* baseItem, const char* path, Double4 value)
{
    dictionary::Item* item = baseItem;
    if (path && path[0] != '\0')
    {
        item = makeDictionaryAtPath(baseItem, path);
    }
    setArray<double>(item, &value.x, 4);
}
#endif

inline void IDictionary::deleteChildren(Item* item)
{
    ScopedWrite g(*this, item);
    size_t childCount = getItemChildCount(item);
    while (childCount != 0)
        destroyItem(getItemChildByIndexMutable(item, --childCount));
}

inline void IDictionary::copyItemFlags(Item* dstItem, const Item* srcItem)
{
    setItemFlag(dstItem, ItemFlag::eUnitSubtree, getItemFlag(srcItem, ItemFlag::eUnitSubtree));
}

} // namespace dictionary
} // namespace carb
