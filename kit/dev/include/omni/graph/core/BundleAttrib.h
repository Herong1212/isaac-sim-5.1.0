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

#include "IDirtyID.h"

#include <omni/graph/core/IBundle.h>

namespace omni
{
namespace graph
{
namespace core
{

class BundlePrim;
class ConstBundlePrim;

using BundleAttribSourceType = uint8_t;
/**
 * BundleAttributeSource is used to differentiate between UsdAttributes
 * and UsdRelationships.
 *
 * TODO: Investigate why we can't use eRelationship for this purpose.
 */
enum class BundleAttribSource : BundleAttribSourceType
{
    Attribute,
    Relationship,
};

/**
 * Attribute in bundle primitive.
 *
 * In contrast to (Const)BundlePrim and (Const)BundlePrims, PrimAttribute uses
 * const qualifier to express constness of the attribute.
 *
 * TODO: Review if const qualifier is appropriate.
 */
class BundleAttrib
{
public:
    /**
     * Backward compatibility alias.
     */
    using SourceType = BundleAttribSourceType;
    using Source = BundleAttribSource;

    BundleAttrib() = default;

    /**
     * Read initialization.
     */
    BundleAttrib(ConstBundlePrim& prim, omni::graph::core::NameToken name) noexcept;

    /**
     * Read-Write initialization.
     */
    BundleAttrib(BundlePrim& prim,
                 omni::graph::core::NameToken name,
                 omni::graph::core::Type type,
                 size_t arrayElementCount,
                 BundleAttribSource source) noexcept;

    BundleAttrib(BundleAttrib const&) = delete;
    BundleAttrib(BundleAttrib&&) noexcept = delete;

    BundleAttrib& operator=(BundleAttrib const&) = delete;
    BundleAttrib& operator=(BundleAttrib&&) noexcept = delete;

    /**
     * @return Bundle Primitive where this attribute belongs to.
     */
    ConstBundlePrim* getBundlePrim() const noexcept;

    /**
     * @return Bundle Primitive where this attribute belongs to.
     */
    BundlePrim* getBundlePrim() noexcept;

    /**
     * @return Non const attribute handle of this attribute.
     */
    omni::graph::core::AttributeDataHandle handle() noexcept;

    /**
     * @return Const attribute handle of this attribute.
     */
    omni::graph::core::ConstAttributeDataHandle handle() const noexcept;

    /**
     * @return Name of this attribute.
     */
    omni::graph::core::NameToken name() const noexcept;

    /**
     * @return Type of this attribute.
     */
    omni::graph::core::Type type() const noexcept;

    /**
     * @return Interpolation of this attribute.
     */
    omni::graph::core::NameToken interpolation() const noexcept;

    /**
     * Set interpolation for this attribute.
     *
     * @return True if operation successful, false otherwise.
     */
    bool setInterpolation(omni::graph::core::NameToken interpolation) noexcept;

    /**
     * Clean interpolation information for this attribute.
     */
    void clearInterpolation() noexcept;

    [[deprecated("Dirty ID management has been moved to core. Use IBundleChanges.")]]
    DirtyIDType dirtyID() const noexcept;

    [[deprecated("Setting DirtyID has no effect, Dirty ID management has been moved to core. Use IBundleChanges.")]]
    bool setDirtyID(DirtyIDType dirtyID) noexcept
    {
        return false;
    }

    [[deprecated("Bumping DirtyID has no effect, Dirty ID management has been moved to core. Use IBundleChanges.")]]
    bool bumpDirtyID() noexcept
    {
        return false;
    }

    /**
     * Set source for this attribute.
     *
     * @return True if successful, false otherwise.
     */
    bool setSource(Source source) noexcept;

    /**
     * Reset source to default value for this attribute.
     */
    void clearSource() noexcept;

    /**
     * @return True if this attribute is an array attribute.
     */
    bool isArray() const noexcept;

    /**
     * @return Size of this attribute. If attribute is not an array, then size is 1.
     */
    size_t size() const noexcept;

    /**
     * Changes size of this attribute.
     */
    void resize(size_t arrayElementCount) noexcept;

    /**
     * Copy attribute contents from another attribute.
     * Destination name is preserved.
     */
    void copyContentsFrom(BundleAttrib const& sourceAttr) noexcept;

    /**
     * @return Internal data as void pointer.
     */
    void* getDataInternal() noexcept;

    /**
     * @return Internal data as void pointer.
     */
    void const* getDataInternal() const noexcept;

    template <typename T>
    T get() const noexcept;

    // NOTE: If this is not an array type attribute, this pointer may not be valid once any prim,
    //       even if it's not the prim containing this attribute, has an attribute added or removed,
    //       due to how attribute data is stored.
    template <typename T>
    T* getData() noexcept;

    template <typename T>
    T const* getData() const noexcept;

    template <typename T>
    T const* getConstData() const noexcept;

    template <typename T>
    void set(T const& value) noexcept;

    template <typename T>
    void set(T const* values, size_t elementCount) noexcept;

    /***********************************************************************************************
     *
     * TODO: Following methods might be deprecated in the future.
     *       In the next iteration when real interface starts to emerge, we can retire those methods.
     *
     ***********************************************************************************************/

    /**
     * @todo First iteration of MPiB didn't use 'eRelationship' type to describe relationships.
     *       Thus, strange approach was created to treat attribute, that is a relationship as a "source".
     */
    Source source() const noexcept;

    /**
     * @return true if this attribute is data.
     */
    bool isAttributeData() const noexcept;

    /**
     * @return true if this attribute is relationship.
     */
    bool isRelationshipData() const noexcept;

    /**
     * @deprecated IBundle2 interface does not require prefixing, use getName().
     */
    omni::graph::core::NameToken prefixedName() const noexcept;

private:
    /**
     * Remove attribute and its internal data.
     */
    void clearContents() noexcept;

    omni::graph::core::IConstBundle2* getConstBundlePtr() const noexcept;
    omni::graph::core::IBundle2* getBundlePtr() noexcept;

    ConstBundlePrim* m_bundlePrim{ nullptr };

    // Attribute Definition:
    omni::graph::core::NameToken m_name = omni::fabric::kUninitializedToken;
    omni::fabric::TypeC m_type;

    // Attribute Property Cached Values:
    omni::graph::core::NameToken m_interpolation = omni::fabric::kUninitializedToken;
    Source m_source { BundleAttribSource::Attribute };

    friend class ConstBundlePrims;
    friend class BundlePrim;
};

/**
 * Do not use! Backward compatibility alias.
 */
using BundleAttributeInfo = BundleAttrib;

} // namespace core
} // namespace graph
} // namespace omni

#include "BundleAttribImpl.h"
