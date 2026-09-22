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

#include "ConstBundlePrims.h"

namespace omni
{
namespace graph
{
namespace core
{

class BundlePrims;
class BundlePrimIterator;
class BundlePrimAttrIterator;

/**
 * Collection of read-write attributes in a primitive.
 */
class BundlePrim : public ConstBundlePrim
{
public:
    using AttrMapIteratorType = BundleAttributeMap::iterator;

    /**
     * @return Parent of this bundle prim.
     */
    BundlePrims* getBundlePrims() noexcept;

    /**
     * @return Bundle handle of this primitive.
     */
    BundleHandle handle() noexcept;

    /**
     * Sets path of the primitive.
     */
    void setPath(NameToken path) noexcept;

    /**
     * Sets type of the primitive.
     */
    void setType(NameToken type) noexcept;

    /**
     * @return Cached instance of BundleAttrib if attribute is found successfully, nullptr otherwise.
     */
    BundleAttrib* getAttr(NameToken attrName) noexcept;

    /**
     * @return BundleAttrib if attribute is added successfully, nullptr otherwise.
     */
    BundleAttrib* addAttr(NameToken attrName,
                          Type type,
                          size_t arrayElementCount = 0,
                          BundleAttrib::Source source = BundleAttrib::Source::Attribute) noexcept;

    /**
     * Convenience structure for adding attributes.
     */
    struct AddAttrInfo
    {
        NameToken attrName;
        Type type;
        size_t arrayElementCount;
        BundleAttrib::Source source;
    };

    /**
     * Adds a list of attributes to this bundle prim.
     *
     * @param[in] attrList Vector of all the new attributes to be added to this prim
     * @returns True if all (new) attributes were added successfully
     *
     * @todo Weakness of this interface is that it forces usage of std::vector.
     */
    bool addAttrs(std::vector<AddAttrInfo> const& attrList) noexcept;

    /**
     * Remove attribute with a given name from this primitive.
     */
    void removeAttr(NameToken attrName) noexcept;

    /**
     * Recursively remove all attributes from this primitive.
     */
    void clearContents() noexcept;

    /**
     * Copy contents from another bundle prim.
     */
    void copyContentsFrom(ConstBundlePrim& source, bool removeAttrsNotInSource = true) noexcept;

    [[deprecated("Bumping DirtyID has no effect, Dirty ID management has been moved to core. Use IBundleChanges.")]]
    void bumpDirtyID() noexcept {}

    [[deprecated("Setting DirtyID has no effect, Dirty ID management has been moved to core. Use IBundleChanges.")]]
    void setDirtyID(DirtyIDType dirtyID) noexcept {}

    /**
     * @return Attribute iterator pointing to the first attribute in this bundle.
     */
    BundlePrimAttrIterator begin() noexcept;

    /**
     * @return Attribute iterator pointing to the last attribute in this bundle.
     */
    BundlePrimAttrIterator end() noexcept;

    /**
     * @return Attribute iterator pointing to the first attribute in this bundle.
     */
    ConstBundlePrimAttrIterator cbegin() noexcept;

    /**
     * @return Attribute iterator pointing to the last attribute in this bundle.
     */
    ConstBundlePrimAttrIterator cend() noexcept;

    /***********************************************************************************************
     *
     * TODO: Following methods might be deprecated in the future.
     *       In the next iteration when real interface starts to emerge, we can retire those methods.
     *
     ***********************************************************************************************/

    /**
     * Create an attribute that is a relationship type.
     */
    BundleAttrib* addRelationship(NameToken name, size_t targetCount) noexcept;

    /**
     * @deprecated Use getBundlePrims.
     */
    BundlePrims* bundlePrims() noexcept;

    /**
     * @deprecated Do not use!
     */
    void copyContentsFrom(ConstBundlePrim const& source, bool removeAttrsNotInSource = true) noexcept;

private:
    /**
     * Direct initialization with IBundle interface.
     *
     * ConstBundlePrim and BundlePrim take advantage of polymorphic relationship
     * between IConstBundle and IBundle interfaces.
     * In order to modify bundles, BundlePrim makes an attempt to cast IConstBundle
     * to IBundle interface. When this process is successful then, bundle can be modified.
     *
     * Only BundlePrims is allowed to create instances of BundlePrim.
     */
    BundlePrim(BundlePrims& bundlePrims, omni::core::ObjectPtr<IBundle2> bundle);

    /**
     * Clear contents of IBundle.
     */
    void recursiveClearContents(GraphContextObj const& context,
                                IBundleFactory* factory,
                                IBundle2* bundle) noexcept;

    /**
     * @return Make an attempt to cast IConstBundle interface to IBundle. Returns nullptr if operation failed.
     */
    IBundle2* getBundlePtr(IConstBundle2* constBundle) noexcept;

    /**
     * @return Make an attempt to cast IConstBundle interface to IBundle. Returns nullptr if operation failed.
     */
    IBundle2* getBundlePtr() noexcept;

    /**
     * @return True if primitive is an instance of common attributes.
     */
    bool isCommonAttrs() const noexcept
    {
        BundlePrimIndex primIndex = static_cast<ConstBundlePrim*>(const_cast<BundlePrim*>(this))->primIndex();
        return primIndex == kInvalidBundlePrimIndex;
    }

    friend class BundlePrimIterator;
    friend class BundlePrims;
    friend class BundleAttrib;
};

/**
 * Collection of read-write primitives in a bundle.
 *
 * Bundle Primitives is not movable, not copyable. It lifespan is managed by the user.
 */
class BundlePrims : public ConstBundlePrims
{
public:
    /**
     * Acquire access to a bundle primitives under given handle.
     */
    BundlePrims(GraphContextObj const& context, BundleHandle const& bundle);

    ~BundlePrims() noexcept;

    /**
     * @return Bundle handle of this primitive.
     */
    BundleHandle handle() noexcept;

    /**
     * @return BundlePrim under given index, or nullptr if prim is not found.
     */
    BundlePrim* getPrim(BundlePrimIndex primIndex) noexcept;

    /**
     * @return BundlePrim allowing access to attributes to this bundle primitives.
     */
    BundlePrim& getCommonAttrs() noexcept;

    /**
     * Add new primitives to this bundle.
     *
     * @return Number of successfully added primitives.
     */
    size_t addPrims(size_t primCountToAdd) noexcept;

    /**
     * Remove primitive under given index.
     */
    bool removePrim(BundlePrimIndex primIndex) noexcept;

    /**
     * Cleans up this primitive bundle. Remove all primitives and attributes.
     */
    void clearContents() noexcept;

    [[deprecated("Bumping DirtyID has no effect, Dirty ID management has been moved to core. Use IBundleChanges.")]]
    DirtyIDType bumpBundleDirtyID() noexcept
    {
        return kInvalidDirtyID;
    }

    /**
     * @return Primitive iterator pointing to the first primitive in this bundle.
     */
    BundlePrimIterator begin() noexcept;

    /**
     * @return Primitive iterator pointing to the last primitive in this bundle.
     */
    BundlePrimIterator end() noexcept;

    /**
     * @return Primitive iterator pointing to the first primitive in this bundle.
     */
    ConstBundlePrimIterator cbegin() noexcept;

    /**
     * @return Primitive iterator pointing to the last primitive in this bundle.
     */
    ConstBundlePrimIterator cend() noexcept;

    /***********************************************************************************************
     *
     * TODO: Following methods might be deprecated in the future.
     *       In the next iteration when real interface starts to emerge, we can retire those methods.
     *
     ***********************************************************************************************/

    /**
     * @deprecated Don't use! Read attach() description.
     */
    BundlePrims();

    /**
     * @deprecated Use appropriate constructor and heap allocate BundlePrims.
     *
     * @todo: There is no benefit of using this method. Cache has to be rebuild from scratch
     *        whenever BundlePrims is attached/detached.
     *        It would be better to remove default constructor and enforce cache construction
     *        through constructor with arguments.
     */
    void attach(GraphContextObj const& context, BundleHandle const& bundle) noexcept;

    /**
     * @deprecated Use appropriate constructor and heap allocate ConstBundlePrims.
     */
    void detach() noexcept;

    /**
     * @deprecated Do not use! Use removePrim with index. This override introduces ambiguity where int can
     *             be converted to a pointer.
     *
     * @todo: Weakness of removePrim design is that it introduces two overrides with following arguments:
     *         * pointer
     *         * integer
     *        This leads to ambiguity during override resolution. Override with a pointer should be avoided
     *        and removed in the future.
     */
    bool removePrim(ConstBundlePrim* prim) noexcept;

    /**
     * @deprecated Do not use! There is no need for this function to exist.
     *             Get the primitive and call clearContents().
     */
    BundlePrim* getClearedPrim(BundlePrimIndex primIndex) noexcept;

    /**
     * @deprecated Responsibility to cache primitive's attributes has been moved to BundlePrim.
     */
    void ensurePrimAttrsCached(BundlePrimIndex primIndex) noexcept;

private:

    /**
     * @return Returns nullptr if bundle is read only, or IBundle2 instance otherwise.
     */
    IBundle2* getBundlePtr() noexcept;

    // cached attribute handles
    AttributeDataHandle m_bundlePrimIndexOffsetAttr{ AttributeDataHandle::invalidValue() };

    friend class BundlePrim;
    friend class BundleAttrib;
};

/**
 * Primitives in Bundle iterator.
 */
class BundlePrimIterator
{
public:
    BundlePrimIterator(BundlePrims& bundlePrims, BundlePrimIndex primIndex = 0) noexcept;

    BundlePrimIterator(BundlePrimIterator const& that) noexcept = default;
    BundlePrimIterator& operator=(BundlePrimIterator const& that) noexcept = default;

    bool operator==(BundlePrimIterator const& that) const noexcept;
    bool operator!=(BundlePrimIterator const& that) const noexcept;

    BundlePrim& operator*() noexcept;
    BundlePrim* operator->() noexcept;
    BundlePrimIterator& operator++() noexcept;

private:
    BundlePrims* m_bundlePrims;
    BundlePrimIndex m_primIndex;
};

/**
 * Attributes in Primitive iterator.
 */
class BundlePrimAttrIterator
{
public:
    BundlePrimAttrIterator(BundlePrim& bundlePrim, BundlePrim::AttrMapIteratorType attrIter) noexcept;

    BundlePrimAttrIterator(BundlePrimAttrIterator const& that) noexcept = default;
    BundlePrimAttrIterator& operator=(BundlePrimAttrIterator const& that) noexcept = default;

    bool operator==(BundlePrimAttrIterator const& that) const noexcept;
    bool operator!=(BundlePrimAttrIterator const& that) const noexcept;

    BundleAttrib& operator*() noexcept;
    BundleAttrib* operator->() noexcept;
    BundlePrimAttrIterator& operator++() noexcept;

    BundleAttrib const* getConst() noexcept;

private:
    BundlePrim* m_bundlePrim;
    BundlePrim::AttrMapIteratorType m_attrIter;
};

} // namespace core
} // namespace graph
} // namespace omni

#include "BundlePrimsImpl.h"
