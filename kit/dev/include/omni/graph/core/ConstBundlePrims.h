// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

// ====================================================================================================
/*   _____          _   _       _     _    _
    |  __ \        | \ | |     | |   | |  | |
    | |  | | ___   |  \| | ___ | |_  | |  | |___  ___
    | |  | |/ _ \  | . ` |/ _ \| __| | |  | / __|/ _ \
    | |__| | (_) | | |\  | (_) | |_  | |__| \__ \  __/
    |_____/ \___/  |_| \_|\___/ \__|  \____/|___/\___|

This is a temporary interface that can change at any time.
*/
// ====================================================================================================

#include "BundleAttrib.h"

#include <omni/graph/core/IBundleFactory.h>

#include <unordered_map>
#include <memory>
#include <vector>

namespace omni
{
namespace graph
{
namespace core
{

class ConstBundlePrims;
class ConstBundlePrimIterator;
class ConstBundlePrimAttrIterator;

/**
 * Index used to identify primitives in a bundle.
 */
using BundlePrimIndex = size_t;
constexpr BundlePrimIndex kInvalidBundlePrimIndex = ~BundlePrimIndex(0);

/**
 * Collection of read-only attributes in a primitive.
 *
 * Const Bundle Primitive is not movable, not copyable. It lifespan is managed by Const Bundle Primitives.
 */
class ConstBundlePrim
{
public:
    using BundleAttributeMap = std::unordered_map<NameToken, std::unique_ptr<BundleAttrib>>;
    using AttrMapIteratorType = BundleAttributeMap::const_iterator;

    ConstBundlePrim(ConstBundlePrim const&) = delete;
    ConstBundlePrim(ConstBundlePrim&&) = delete;

    ConstBundlePrim& operator=(ConstBundlePrim const& that) = delete;
    ConstBundlePrim& operator=(ConstBundlePrim&&) = delete;

    /**
     * @return Bundle handle of this primitive.
     */
    ConstBundleHandle getConstHandle() noexcept;

    /**
     * @return Parent bundle prims of this primitive.
     */
    ConstBundlePrims* getConstBundlePrims() noexcept;

    /**
     * @return Number of attributes in this primitive. Does not include internal attributes.
     */
    size_t attrCount() noexcept;

    /**
     * @return PrimAttribute if attribute with given name is found, nullptr otherwise.
     */
    BundleAttrib const* getConstAttr(NameToken attrName) noexcept;

    /**
     * @return Index of this primitive in parent bundle.
     */
    BundlePrimIndex primIndex() noexcept;

    /**
     * @return Path of this primitive.
     */
    NameToken path() noexcept;

    /**
     * @return Type of this primitive.
     */
    NameToken type() noexcept;

    [[deprecated("Dirty ID management has been moved to core. Use IBundleChanges.")]]
    DirtyIDType dirtyID() noexcept;

    /**
     * @return Attribute iterator pointing to the first attribute in this bundle.
     */
    ConstBundlePrimAttrIterator begin() noexcept;

    /**
     * @return Attribute iterator pointing to the last attribute in this bundle.
     */
    ConstBundlePrimAttrIterator end() noexcept;

    /***********************************************************************************************
     *
     * TODO: Following methods might be deprecated in the future.
     *       In the next iteration when real interface starts to emerge, we can retire those methods.
     *
     ***********************************************************************************************/

    /**
     * @deprecated Do not use!. Use getConstAttr().
     */
    [[deprecated("Use non const instead.")]]
    BundleAttrib const* getAttr(NameToken attrName) const noexcept;

    /**
     * @deprecated Do not use!. Use non-const variant of path().
     */
    [[deprecated("Use non const instead.")]]
    NameToken path() const noexcept;

    /**
     * @deprecated Do not use!. Use non-const variant of type().
     */
    [[deprecated("Use non const instead.")]]
    NameToken type() const noexcept;

    [[deprecated("Dirty ID management has been moved to core. Use IBundleChanges.")]]
    DirtyIDType dirtyID() const noexcept;

    /**
     * @deprecated Do not use!. Use non-const variant of begin().
     */
    [[deprecated("Use non const instead.")]]
    ConstBundlePrimAttrIterator begin() const noexcept;

    /**
     * @deprecated Do not use!. Use non-const variant of end().
     */
    [[deprecated("Use non const instead.")]]
    ConstBundlePrimAttrIterator end() const noexcept;

protected:
    /**
     * Direct initialization with IConstBundle interface.
     *
     * ConstBundlePrim and BundlePrim take advantage of polymorphic relationship
     * between IConstBundle and IBundle interfaces.
     * In order to modify bundles, BundlePrim makes attempt to down cast IConstBundle
     * to IBundle interface. When this process is successful then, bundle can be modified.
     *
     * Only ConstBundlePrims is allowed to create instances of ConstBundlePrim.
     */
    ConstBundlePrim(ConstBundlePrims& bundlePrims, omni::core::ObjectPtr<IConstBundle2> bundle);

    /**
     * @return IConstBundle interface for this bundle primitive.
     */
    IConstBundle2* getConstBundlePtr() noexcept;

    /**
     * @return Get attribute used by ConstBundlePrims and BundlePrims.
     */
    BundleAttributeMap& getAttributes() noexcept;

    /**
     * Reads public attributes from the bundle and caches them as BundleAttribs.
     */
    void readAndCacheAttributes() noexcept;

private:
    ConstBundlePrims* m_bundlePrims{ nullptr }; // Parent of this bundle prim.
    omni::core::ObjectPtr<IConstBundle2> m_bundle;

    ConstAttributeDataHandle m_primIndexAttr{ ConstAttributeDataHandle::invalidValue() };
    ConstAttributeDataHandle m_pathAttr{ ConstAttributeDataHandle::invalidValue() };
    ConstAttributeDataHandle m_typeAttr{ ConstAttributeDataHandle::invalidValue() };

    BundleAttributeMap m_attributes; // Cached public attributes that belong to this primitive.

    friend class BundleAttrib;      // Required to access IConstBundle interface.
    friend class BundlePrim;        // Required to access primitive type.
    friend class BundlePrims;       // Required to update internal indices.
    friend class ConstBundlePrims;  // Required to call constructor.
};

/**
 * Collection of read-only primitives in a bundle.
 *
 * Const Bundle Primitives is not movable, not copyable. It lifespan is managed by the user.
 */
class ConstBundlePrims
{
public:
    ConstBundlePrims();
    ConstBundlePrims(GraphContextObj const& context,
                     ConstBundleHandle const& bundle);

    ConstBundlePrims(ConstBundlePrims const&) = delete;
    ConstBundlePrims(ConstBundlePrims&&) = delete;

    ConstBundlePrims& operator=(ConstBundlePrims const&) = delete;
    ConstBundlePrims& operator=(ConstBundlePrims&&) = delete;

    /**
     * @return Bundle handle of this primitive.
     */
    ConstBundleHandle getConstHandle() noexcept;

    /**
     * @return Number of primitives in this bundle of primitives.
     */
    size_t getPrimCount() noexcept;

    /**
     * @return Get read only primitive under specified index.
     */
    ConstBundlePrim* getConstPrim(BundlePrimIndex primIndex) noexcept;

    [[deprecated("Dirty ID management has been moved to core. Use IBundleChanges.")]]
    DirtyIDType getBundleDirtyID() noexcept;

    /**
     * Common Attributes are attributes that are shared for entire bundle.
     * An example of a common attribute is "transform" attribute.
     *
     * @return ConstBundlePrims as ConstBundlePrim to access attributes.
     */
    ConstBundlePrim& getConstCommonAttrs() noexcept;

    /**
     * @return Context where bundle primitives belongs to.
     */
    GraphContextObj const& context() noexcept;

    /**
     * @return Primitive iterator pointing to the first primitive in this bundle.
     */
    ConstBundlePrimIterator begin() noexcept;

    /**
     * @return Primitive iterator pointing to the last primitive in this bundle.
     */
    ConstBundlePrimIterator end() noexcept;

    /***********************************************************************************************
     *
     * TODO: Following methods might be deprecated in the future.
     *       In the next iteration when real interface starts to emerge, we can retire those methods.
     *
     ***********************************************************************************************/

    /**
     * @deprecated Do not use! Use getConstPrim().
     */
    ConstBundlePrim* getPrim(BundlePrimIndex primIndex) noexcept;

    [[deprecated("Getting next DirtyID has no effect, Dirty ID management has been moved to core. Use IBundleChanges.")]]
    DirtyIDType getNextDirtyID() noexcept
    {
        return carb::getCachedInterface<IDirtyID>()->getNextDirtyID();
    }

    /**
     * @deprecated Use appropriate constructor and heap allocate ConstBundlePrims.
     *
     * @todo: There is no benefit of using this method. Cache has to be rebuild from scratch
     *        whenever ConstBundlePrims is attached/detached.
     *        It would be better to remove default constructor and enforce cache construction
     *        through constructor with arguments.
     */
    void attach(GraphContextObj const& context,
                ConstBundleHandle const& bundle) noexcept;

    /**
     * @deprecated Use appropriate constructor and heap allocate ConstBundlePrims.
     */
    void detach() noexcept;

    /**
     * @deprecated Use getConstHandle.
     */
    ConstBundleHandle handle() noexcept;

    /**
     * @deprecated Use getConstCommonAttrs.
     */
    ConstBundlePrim& getCommonAttrs() noexcept;

    /**
     * @deprecated There is no need to separate attributes. Inherently IBundle2 interface keeps them separated.
     */
    void separateAttrs() noexcept;

    /**
     * @deprecated Caching attributes is not needed. Calling this method doesn't do anything.
     */
    void ensurePrimAttrsCached(BundlePrimIndex primIndex) noexcept;

protected:
    using ConstBundlePrimPtr = std::unique_ptr<ConstBundlePrim>;
    using BundlePrimArray = std::vector<ConstBundlePrimPtr>;

    /**
     * Get bundle primitives in this bundle.
     */
    BundlePrimArray& getPrimitives() noexcept;

    /**
     * IConstBundle2 is a polymorphic base for IBundle2, thus passing bundle argument allows passing
     * version of the interface that allows mutations.
     */
    void attach(omni::core::ObjectPtr<IBundleFactory>&& factory,
                omni::core::ObjectPtr<IConstBundle2>&& bundle) noexcept;

    /**
     * @return Factory to spawn instances of IBundle interface.
     */
    IBundleFactory* getBundleFactoryPtr() noexcept;

    /**
     * @return IBundle instance of this bundle.
     */
    IConstBundle2* getConstBundlePtr() noexcept;

    /**
     * Instances of BundlePrim are instantiated on demand. Argument create allows
     * instantiation mutable or immutable IConstBundle2 interface.
     */
    template<typename FUNC>
    ConstBundlePrim* getConstPrim(BundlePrimIndex primIndex, FUNC create) noexcept;

private:
    omni::core::ObjectPtr<IBundleFactory> m_factory;
    omni::core::ObjectPtr<IConstBundle2> m_bundle;
    GraphContextObj m_context; // Backward compatibility.

    /**
     * ConstBundlePrims is a bundle as well. To access attributes under this bundle we need to acquire
     * an instance of ConstBundlePrim for this bundle. Common attributes, with unfortunate name,
     * gives us ability to access those attributes.
     */
    ConstBundlePrimPtr m_commonAttributes;
    BundlePrimArray m_primitives; // Cached instances of BundlePrim.

    friend class ConstBundlePrim;
    friend class BundlePrim;
    friend class BundleAttrib;
};

/**
 * Primitives in Bundle iterator.
 */
class ConstBundlePrimIterator
{
public:
    ConstBundlePrimIterator(ConstBundlePrims& bundlePrims, BundlePrimIndex primIndex = 0) noexcept;

    ConstBundlePrimIterator(ConstBundlePrimIterator const& that) noexcept = default;
    ConstBundlePrimIterator& operator=(ConstBundlePrimIterator const& that) noexcept = default;

    bool operator==(ConstBundlePrimIterator const& that) const noexcept;
    bool operator!=(ConstBundlePrimIterator const& that) const noexcept;

    ConstBundlePrim& operator*() noexcept;
    ConstBundlePrim* operator->() noexcept;
    ConstBundlePrimIterator& operator++() noexcept;

private:
    ConstBundlePrims* m_bundlePrims;
    BundlePrimIndex m_primIndex;
};

/**
 * Attributes in Primitive iterator.
 */
class ConstBundlePrimAttrIterator
{
public:
    ConstBundlePrimAttrIterator(ConstBundlePrim& bundlePrim, ConstBundlePrim::AttrMapIteratorType attrIter) noexcept;

    ConstBundlePrimAttrIterator(ConstBundlePrimAttrIterator const& that) noexcept = default;
    ConstBundlePrimAttrIterator& operator=(ConstBundlePrimAttrIterator const& that) noexcept = default;

    bool operator==(ConstBundlePrimAttrIterator const& that) const noexcept;
    bool operator!=(ConstBundlePrimAttrIterator const& that) const noexcept;

    BundleAttrib const& operator*() const noexcept;
    BundleAttrib const* operator->() const noexcept;
    ConstBundlePrimAttrIterator& operator++() noexcept;

private:
    ConstBundlePrim* m_bundlePrim;
    ConstBundlePrim::AttrMapIteratorType m_attrIter;
};

} // namespace core
} // namespace graph
} // namespace omni

#include "ConstBundlePrimsImpl.h"
