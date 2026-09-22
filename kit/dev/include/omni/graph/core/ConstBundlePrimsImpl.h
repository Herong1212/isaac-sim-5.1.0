// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "ConstBundlePrims.h"

#include <omni/graph/core/CppWrappers.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/ComputeGraph.h>

#include <algorithm>

namespace omni
{
namespace graph
{
namespace core
{

// ====================================================================================================
//
//                                      Const Bundle Primitive
//
// ====================================================================================================

inline ConstBundlePrim::ConstBundlePrim(ConstBundlePrims& bundlePrims, omni::core::ObjectPtr<IConstBundle2> bundle)
    : m_bundlePrims{ &bundlePrims }, m_bundle{ std::move(bundle) }
{
    // Read and cache all non internal attributes.
    readAndCacheAttributes();

    const detail::AttrDefinition& primIndexDef = detail::getPrimIndexDefinition();
    m_primIndexAttr = getConstBundlePtr()->getConstBundleMetadataByName(primIndexDef.token);
}

inline ConstBundleHandle ConstBundlePrim::getConstHandle() noexcept
{
    return m_bundle->getConstHandle();
}

inline void ConstBundlePrim::readAndCacheAttributes() noexcept
{
    IConstBundle2* bundle = getConstBundlePtr();
    GraphContextObj const& context = getConstBundlePrims()->context();

    std::vector<ConstAttributeDataHandle> attrHandles(bundle->getAttributeCount());
    bundle->getConstAttributes(attrHandles.data(), attrHandles.size());

    auto& attrs = getAttributes();
    for(ConstAttributeDataHandle& attrHandle : attrHandles)
    {
        if(!attrHandle.isValid())
            continue;

        NameToken attrName = context.iAttributeData->getName(context, attrHandle);
        attrs.insert(std::make_pair(attrName, std::make_unique<BundleAttrib>(*this, attrName)));
    }
}

inline BundleAttrib const* ConstBundlePrim::getConstAttr(core::NameToken attrName) noexcept
{
    // Try to find cached attributes
    auto& attrMap = getAttributes();
    auto it = attrMap.find(attrName);
    if (it != attrMap.end())
    {
        return it->second.get();
    }

    // Try to find attribute in this bundle.
    IConstBundle2* bundle = getConstBundlePtr();
    ConstAttributeDataHandle attributeHandle = bundle->getConstAttributeByName(attrName);
    if (!attributeHandle.isValid())
    {
        // attribute is not found, ensure entry is removed from the cache.
        auto it = attrMap.find(attrName);
        if (it != attrMap.end())
        {
            attrMap.erase(it);
        }

        return nullptr;
    }

    // Check if attribute in the bundle is stale
    auto newPrimAttribute = new BundleAttrib{ *this, attrName};
    std::unique_ptr<BundleAttrib> primAttributePtr{ newPrimAttribute };
    attrMap.emplace(attrName, std::move(primAttributePtr));
    return newPrimAttribute;
}

inline BundleAttrib const* ConstBundlePrim::getAttr(NameToken attrName) const noexcept
{
    return const_cast<ConstBundlePrim*>(this)->getConstAttr(attrName);
}

inline size_t ConstBundlePrim::attrCount() noexcept
{
    return getAttributes().size();
}

inline BundlePrimIndex ConstBundlePrim::primIndex() noexcept
{
    if (m_primIndexAttr.isValid())
    {
        ConstBundlePrims* bundlePrims = getConstBundlePrims();
        return *getDataR<BundlePrimIndex>(bundlePrims->context(), m_primIndexAttr);
    }
    return kInvalidBundlePrimIndex;
}

inline NameToken ConstBundlePrim::path() noexcept
{
    if (!m_pathAttr.isValid())
    {
        const detail::AttrDefinition& attrDef = detail::getPrimPathDefinition();
        m_pathAttr = getConstBundlePtr()->getConstAttributeByName(attrDef.token);
    }

    NameToken result = omni::fabric::kUninitializedToken;

    if (m_pathAttr.isValid())
    {
        ConstBundlePrims* bundlePrims = getConstBundlePrims();
        result = *getDataR<NameToken>(bundlePrims->context(), m_pathAttr);
    }

    return result;
}

inline NameToken ConstBundlePrim::path() const noexcept
{
    return const_cast<ConstBundlePrim*>(this)->path();
}

inline NameToken ConstBundlePrim::type() noexcept
{
    if (!m_typeAttr.isValid())
    {
        const detail::AttrDefinition& attrDef = detail::getPrimTypeDefinition();
        m_typeAttr = getConstBundlePtr()->getConstAttributeByName(attrDef.token);
    }

    NameToken result = omni::fabric::kUninitializedToken;

    if (m_typeAttr.isValid())
    {
        ConstBundlePrims* bundlePrims = getConstBundlePrims();
        result = *getDataR<NameToken>(bundlePrims->context(), m_typeAttr);
    }

    return result;
}

inline NameToken ConstBundlePrim::type() const noexcept
{
    return const_cast<ConstBundlePrim*>(this)->type();
}

inline DirtyIDType ConstBundlePrim::dirtyID() noexcept
{
    auto id = carb::getCachedInterface<ComputeGraph>()->getDirtyIDInterfacePtr(m_bundle->getContext());
    return id->getForBundle(m_bundle->getConstHandle());
}

inline DirtyIDType ConstBundlePrim::dirtyID() const noexcept
{
    CARB_IGNOREWARNING_MSC_WITH_PUSH(4996)
    CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wdeprecated-declarations")
    return const_cast<ConstBundlePrim*>(this)->dirtyID();
    CARB_IGNOREWARNING_GNUC_POP
    CARB_IGNOREWARNING_MSC_POP
}

inline ConstBundlePrims* ConstBundlePrim::getConstBundlePrims() noexcept
{
    return m_bundlePrims;
}

inline ConstBundlePrimAttrIterator ConstBundlePrim::begin() noexcept
{
    return ConstBundlePrimAttrIterator(*this, getAttributes().begin());
}

inline ConstBundlePrimAttrIterator ConstBundlePrim::end() noexcept
{
    return ConstBundlePrimAttrIterator(*this, getAttributes().end());
}

inline ConstBundlePrimAttrIterator ConstBundlePrim::begin() const noexcept
{
    ConstBundlePrim& thisPrim = const_cast<ConstBundlePrim&>(*this);
    return ConstBundlePrimAttrIterator(thisPrim, thisPrim.getAttributes().begin());
}

inline ConstBundlePrimAttrIterator ConstBundlePrim::end() const noexcept
{
    ConstBundlePrim& thisPrim = const_cast<ConstBundlePrim&>(*this);
    return ConstBundlePrimAttrIterator(thisPrim, thisPrim.getAttributes().end());
}

inline IConstBundle2* ConstBundlePrim::getConstBundlePtr() noexcept
{
    return m_bundle.get();
}

inline ConstBundlePrim::BundleAttributeMap& ConstBundlePrim::getAttributes() noexcept
{
    return m_attributes;
}

// ====================================================================================================
//
//                                      Const Bundle Primitives
//
// ====================================================================================================

inline ConstBundlePrims::ConstBundlePrims()
{
}

inline ConstBundlePrims::ConstBundlePrims(GraphContextObj const& context,
                                          ConstBundleHandle const& bundle)
    : ConstBundlePrims()
{
    attach(context, bundle);
}

inline void ConstBundlePrims::detach() noexcept
{
    m_primitives.clear();
    m_commonAttributes.reset();
    m_context = GraphContextObj{};
    m_bundle.release();
    m_factory.release();
}

inline ConstBundlePrims::BundlePrimArray& ConstBundlePrims::getPrimitives() noexcept
{
    return m_primitives;
}

inline ConstBundleHandle ConstBundlePrims::getConstHandle() noexcept
{
    return m_bundle->getConstHandle();
}

template <typename FUNC>
ConstBundlePrim* ConstBundlePrims::getConstPrim(BundlePrimIndex primIndex, FUNC createSortedBundlePrims) noexcept
{
    // Return invalid const bundle prim if out of bounds.
    size_t const bundlePrimCount = getPrimCount();
    if (primIndex >= bundlePrimCount)
    {
        return nullptr;
    }

    auto& prims = getPrimitives();

    // HDC_TODO: we need a clear signal to be sure when creation and resorting is required.
    if (prims.size() != bundlePrimCount)
    {
        prims = std::move(createSortedBundlePrims());

        CARB_ASSERT(bundlePrimCount == (size_t)std::count_if(prims.cbegin(), prims.cend(), [](const auto& p) { return p.get(); }));
    }

    return prims[primIndex].get();
}

inline ConstBundlePrim* ConstBundlePrims::getPrim(BundlePrimIndex primIndex) noexcept
{
    return getConstPrim(primIndex);
}

inline ConstBundlePrim* ConstBundlePrims::getConstPrim(BundlePrimIndex primIndex) noexcept
{
    auto createSortedBundlePrims = [this, &bundlePrims = *this]() -> BundlePrimArray
    {
        const size_t childBundleCount = getConstBundlePtr()->getChildBundleCount();
        std::vector<ConstBundleHandle> handles(childBundleCount);
        getConstBundlePtr()->getConstChildBundles(handles.data(), handles.size());

        const GraphContextObj& graphContext = context();

        BundlePrimArray prims(childBundleCount);
        BundlePrimArray nonIndexedPrims;

        for (ConstBundleHandle& handle : handles)
        {
            auto childBundle = getBundleFactoryPtr()->getConstBundle(graphContext, handle);
            ConstBundlePrim* prim = new ConstBundlePrim(bundlePrims, childBundle);
            BundlePrimIndex index = prim->primIndex();
            CARB_ASSERT(index < childBundleCount || index == kInvalidBundlePrimIndex);
            if (index < childBundleCount)
            {
                prims[index].reset(prim);
            }
            else
            {
                nonIndexedPrims.emplace_back(prim);
            }
        }

        // Merge non-indexed prims into the sorted array.
        if (!nonIndexedPrims.empty())
        {
            BundlePrimIndex index = 0;

            for (ConstBundlePrimPtr& nonIndexedPrim : nonIndexedPrims)
            {
                while (index < childBundleCount)
                {
                    ConstBundlePrimPtr& prim = prims[index++];
                    if (!prim)
                    {
                        prim = std::move(nonIndexedPrim);
                        break;
                    }
                }
            }
        }

        return prims;
    };

    return getConstPrim(primIndex, createSortedBundlePrims);
}

inline DirtyIDType ConstBundlePrims::getBundleDirtyID() noexcept
{
    CARB_IGNOREWARNING_MSC_WITH_PUSH(4996)
    CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wdeprecated-declarations")
    return getCommonAttrs().dirtyID();
    CARB_IGNOREWARNING_GNUC_POP
    CARB_IGNOREWARNING_MSC_POP
}

inline ConstBundlePrim& ConstBundlePrims::getConstCommonAttrs() noexcept
{
    return *m_commonAttributes;
}

inline GraphContextObj const& ConstBundlePrims::context() noexcept
{
    if (m_bundle)
    {
        m_context = m_bundle->getContext();
    }
    else
    {
        m_context = GraphContextObj{};
    }
    return m_context;
}

inline void ConstBundlePrims::attach(GraphContextObj const& context,
                                     ConstBundleHandle const& bundleHandle) noexcept
{
    ComputeGraph* computeGraph = carb::getCachedInterface<ComputeGraph>();
    omni::core::ObjectPtr<IBundleFactory> factory = computeGraph->getBundleFactoryInterfacePtr();
    omni::core::ObjectPtr<IConstBundle2> bundle = factory->getConstBundle(context, bundleHandle);
    attach(std::move(factory), std::move(bundle));
}

inline void ConstBundlePrims::attach(omni::core::ObjectPtr<IBundleFactory>&& factoryPtr,
                                     omni::core::ObjectPtr<IConstBundle2>&& bundlePtr) noexcept
{
    // Initialize members
    m_factory = std::move(factoryPtr);
    m_bundle = std::move(bundlePtr);

    // Initialize common attributes to provide access to ConstBundlePrims attributes.
    m_commonAttributes.reset(new ConstBundlePrim(*this, m_bundle));

    if (!m_bundle->isValid())
    {
        return;
    }

    // TODO: Following code is necessary for backward compatibility.
    [[maybe_unused]] IConstBundle2* bundle = getConstBundlePtr();
    [[maybe_unused]] GraphContextObj const& context = this->context();
}

inline IBundleFactory* ConstBundlePrims::getBundleFactoryPtr() noexcept
{
    return m_factory.get();
}

inline IConstBundle2* ConstBundlePrims::getConstBundlePtr() noexcept
{
    return m_bundle.get();
}

inline size_t ConstBundlePrims::getPrimCount() noexcept
{
    if (IConstBundle2* bundle = getConstBundlePtr())
    {
        return bundle->getChildBundleCount();
    }
    return 0;
}

inline ConstBundlePrimIterator ConstBundlePrims::begin() noexcept
{
    return ConstBundlePrimIterator(*this);
}

inline ConstBundlePrimIterator ConstBundlePrims::end() noexcept
{
    return ConstBundlePrimIterator(*this, getPrimCount());
}

/***********************************************************************************************
 *
 * TODO: Following methods might be deprecated in the future, but are kept for backward compatibility.
 *       In the next iteration when real interface starts to emerge, we can retire those methods.
 *
 ***********************************************************************************************/

inline ConstBundlePrim& ConstBundlePrims::getCommonAttrs() noexcept
{
    return getConstCommonAttrs();
}

inline ConstBundleHandle ConstBundlePrims::handle() noexcept
{
    return m_bundle->getConstHandle();
}

inline void ConstBundlePrims::separateAttrs() noexcept
{
    // There is nothing to separate. This function is deprecated.
}

inline void ConstBundlePrims::ensurePrimAttrsCached(BundlePrimIndex primIndex) noexcept
{
    // Responsibility of caching attributes was moved to Bundle Prim.
}

// ====================================================================================================
//
//                                      Const Bundle Primitive Iterator
//
// ====================================================================================================

inline ConstBundlePrimIterator::ConstBundlePrimIterator(ConstBundlePrims& bundlePrims, BundlePrimIndex primIndex) noexcept
    : m_bundlePrims(&bundlePrims), m_primIndex(primIndex)
{
}

inline bool ConstBundlePrimIterator::operator==(ConstBundlePrimIterator const& that) const noexcept
{
    return m_bundlePrims == that.m_bundlePrims && m_primIndex == that.m_primIndex;
}

inline bool ConstBundlePrimIterator::operator!=(ConstBundlePrimIterator const& that) const noexcept
{
    return !(*this == that);
}

inline ConstBundlePrim& ConstBundlePrimIterator::operator*() noexcept
{
    return *(m_bundlePrims->getConstPrim(m_primIndex));
}

inline ConstBundlePrim* ConstBundlePrimIterator::operator->() noexcept
{
    return m_bundlePrims->getConstPrim(m_primIndex);
}

inline ConstBundlePrimIterator& ConstBundlePrimIterator::operator++() noexcept
{
    ++m_primIndex;
    return *this;
}

// ====================================================================================================
//
//                                      Const Bundle Primitive Attribute Iterator
//
// ====================================================================================================

inline ConstBundlePrimAttrIterator::ConstBundlePrimAttrIterator(ConstBundlePrim& bundlePrim, ConstBundlePrim::AttrMapIteratorType attrIter) noexcept
    : m_bundlePrim(&bundlePrim), m_attrIter(attrIter)
{
}

inline bool ConstBundlePrimAttrIterator::operator==(ConstBundlePrimAttrIterator const& that) const noexcept
{
    return m_bundlePrim == that.m_bundlePrim && m_attrIter == that.m_attrIter;
}

inline bool ConstBundlePrimAttrIterator::operator!=(ConstBundlePrimAttrIterator const& that) const noexcept
{
    return !(*this == that);
}

inline BundleAttrib const& ConstBundlePrimAttrIterator::operator*() const noexcept
{
    CARB_ASSERT(m_attrIter->second);
    return *(m_attrIter->second);
}

inline BundleAttrib const*ConstBundlePrimAttrIterator:: operator->() const noexcept
{
    CARB_ASSERT(m_attrIter->second);
    return m_attrIter->second.get();
}

inline ConstBundlePrimAttrIterator& ConstBundlePrimAttrIterator::operator++() noexcept
{
    ++m_attrIter;
    return *this;
}

} // namespace core
} // namespace graph
} // namespace omni
