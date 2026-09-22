// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "BundlePrims.h"

namespace omni
{
namespace graph
{
namespace core
{

// ====================================================================================================
//
//                                      Bundle Attribute
//
// Because entire Bundle Prims is inlined, we have to put definition of those functions
// after declaration of ConstBundlePrim and ConstBundlePrims.
// ====================================================================================================

inline BundleAttrib::BundleAttrib(ConstBundlePrim& prim, omni::graph::core::NameToken name) noexcept
{
    using namespace omni::graph::core;

    // Get attribute handle and attribute properties
    IConstBundle2* bundle = prim.getConstBundlePtr();
    ConstAttributeDataHandle attributeHandle = bundle->getConstAttributeByName(name);
    if(!attributeHandle.isValid())
    {
        return;
    }

    GraphContextObj const& context = prim.getConstBundlePrims()->context();

    m_bundlePrim = &prim;
    m_name = name;
    m_type = omni::fabric::TypeC(context.iAttributeData->getType(context, attributeHandle));

    // Read attribute properties.
    ConstAttributeDataHandle propertyAttributeHandle;
    propertyAttributeHandle =
        bundle->getConstAttributeMetadataByName(name, detail::getAttrInterpolationDefinition().token);
    if(propertyAttributeHandle.isValid())
    {
        m_interpolation = *getDataR<NameToken>(context, propertyAttributeHandle);
    }

    propertyAttributeHandle =
        bundle->getConstAttributeMetadataByName(name, detail::getAttrSourceDefinition().token);
    if(propertyAttributeHandle.isValid())
    {
        m_source = static_cast<Source>(*getDataR<SourceType>(context, propertyAttributeHandle));
    }
}

inline BundleAttrib::BundleAttrib(BundlePrim& prim, omni::graph::core::NameToken name, omni::graph::core::Type type, size_t arrayElementCount, Source source) noexcept
    : BundleAttrib{ prim, name }
{
    using namespace omni::graph::core;

    // Attribute exists!
    if (m_bundlePrim)
    {
        return;
    }

    // Attribute does not exist.
    IBundle2* bundle = prim.getBundlePtr();
    GraphContextObj const& context = prim.getConstBundlePrims()->context();

    auto handle = bundle->createAttribute(name, type, arrayElementCount);
    omni::graph::core::getDataW<void*>(context, handle); // remove after OM-50059 is merged.

    m_bundlePrim = &prim;
    m_name = name;
    m_type = omni::fabric::TypeC(type);

    // Interpolation is optional.

    // Source of the attribute identifies "data" or "relationship"
    setSource(source);
}

inline BundlePrim* BundleAttrib::getBundlePrim() noexcept
{
    IConstBundle2* constBundle = getConstBundlePtr();
    if(auto bundle = omni::cast<IBundle2>(constBundle))
    {
        return static_cast<BundlePrim*>(m_bundlePrim);
    }
    return nullptr;
}

inline omni::graph::core::IConstBundle2* BundleAttrib::getConstBundlePtr() const noexcept
{
    ConstBundlePrim* bundlePrim = getBundlePrim();
    return bundlePrim->getConstBundlePtr();
}

inline omni::graph::core::IBundle2* BundleAttrib::getBundlePtr() noexcept
{
    BundlePrim* bundlePrim = getBundlePrim();
    return bundlePrim->getBundlePtr();
}

inline DirtyIDType BundleAttrib::dirtyID() const noexcept
{
    auto const context = getConstBundlePtr()->getContext();
    auto id = carb::getCachedInterface<omni::graph::core::ComputeGraph>()->getDirtyIDInterfacePtr(context);
    return id->getForAttribute(this->handle());
}

// ====================================================================================================
//
//                                      Bundle Primitive
//
// ====================================================================================================

inline BundlePrim::BundlePrim(BundlePrims& bundlePrims, omni::core::ObjectPtr<IBundle2> bundle)
    : ConstBundlePrim{ bundlePrims, std::move(bundle) }
{
}

inline void BundlePrim::setPath(NameToken path) noexcept
{
    const detail::AttrDefinition& attrDef = detail::getPrimPathDefinition();
    AttributeDataHandle pathAttr = getBundlePtr()->getAttributeByName(attrDef.token);
    if (!pathAttr.isValid())
    {
        pathAttr = getBundlePtr()->createAttribute(attrDef.token, attrDef.type);
    }

    BundlePrims* bundlePrims = getBundlePrims();
    *getDataW<NameToken>(bundlePrims->context(), pathAttr) = path;
}

inline void BundlePrim::setType(NameToken type) noexcept
{
    const detail::AttrDefinition& attrDef = detail::getPrimTypeDefinition();
    AttributeDataHandle typeAttr = getBundlePtr()->getAttributeByName(attrDef.token);
    if (!typeAttr.isValid())
    {
        typeAttr = getBundlePtr()->createAttribute(attrDef.token, attrDef.type);
    }

    BundlePrims* bundlePrims = getBundlePrims();
    *getDataW<NameToken>(bundlePrims->context(), typeAttr) = type;
}


inline BundleAttrib* BundlePrim::addAttr(omni::graph::core::NameToken attrName,
                                         omni::graph::core::Type type,
                                         size_t arrayElementCount,
                                         BundleAttribSource source) noexcept
{
    using namespace omni::graph::core;

    auto& attrs = getAttributes();

    // Erase existing attribute.
    auto it = attrs.find(attrName);
    if (it != attrs.end())
    {
        it->second->clearContents();
        attrs.erase(it);
    }

    auto attr = new BundleAttrib{ *this, attrName, type, arrayElementCount, source };
    attrs.emplace(attrName, attr);
    return attr;
}

inline BundleAttrib* BundlePrim::addRelationship(omni::graph::core::NameToken name, size_t targetCount) noexcept
{
    BundleAttrib* bundleAttrib = addAttr(name, detail::s_relationshipType, 0, BundleAttribSource::Relationship);
    IBundle2* bundle = this->getBundlePtr();
    omni::graph::core::AttributeDataHandle handle = bundle->getAttributeByName(name);

    auto const iAttributeData = carb::getCachedInterface<IAttributeData>();

    iAttributeData->setElementCount(bundle->getContext(), handle, targetCount);

    return bundleAttrib;
}

inline bool BundlePrim::addAttrs(std::vector<BundlePrim::AddAttrInfo> const& attrList) noexcept
{
    using namespace omni::graph::core;

    auto& attrs = getAttributes();

    // Remove attributes that exists but properties are different.
    std::vector<BundlePrim::AddAttrInfo> attrToCreate;
    attrToCreate.reserve(attrList.size());

    for (auto const& newAttr : attrList) {
        auto it = attrs.find(newAttr.attrName);
        if (it == attrs.end())
        {
            attrToCreate.push_back(newAttr);
            continue;
        }

        BundleAttrib const* attr = it->second.get();
        if (attr->type() != newAttr.type ||
            attr->size() != newAttr.arrayElementCount ||
            attr->source() != newAttr.source)
        {
            it->second->clearContents();
            attrs.erase(it);
            attrToCreate.push_back(newAttr);
        }

        // attribute is the same nothing to do.
    }

    // Create attributes that require instantiation.
    for (auto const& tmp : attrToCreate)
    {
        auto attr = new BundleAttrib{ *this, tmp.attrName, tmp.type, tmp.arrayElementCount, tmp.source };
        attrs.emplace(tmp.attrName, attr);
    }

    return true;
}

inline void BundlePrim::removeAttr(omni::graph::core::NameToken attrName) noexcept
{
    using namespace omni::graph::core;

    // Remove attribute from internal member.
    auto& attrs = getAttributes();
    auto it = attrs.find(attrName);
    if (it != attrs.end())
    {
        it->second->clearContents();
        attrs.erase(it);
    }
}

inline void BundlePrim::clearContents() noexcept
{

    auto& attrs = getAttributes();
    for (auto& attr : attrs)
    {
        attr.second->clearContents();
    }
    getAttributes().clear();
}

inline void BundlePrim::copyContentsFrom(ConstBundlePrim const& source, bool removeAttrsNotInSource /* = true*/) noexcept
{
    return copyContentsFrom(const_cast<ConstBundlePrim&>(source), removeAttrsNotInSource);
}

inline void BundlePrim::copyContentsFrom(ConstBundlePrim& source, bool removeAttrsNotInSource /* = true*/) noexcept
{
    CARB_IGNOREWARNING_MSC_WITH_PUSH(4996)
    CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wdeprecated-declarations")
    // Nothing to do if they're already equal.
    if (dirtyID() == source.dirtyID())
        return;

    // Add/set any attributes from source, if the dirty IDs are different, being sure to copy the dirty IDs.
    // first we batch add them, then we copy the contents
    std::vector<BundlePrim::AddAttrInfo> attrsToAdd;
    attrsToAdd.reserve(source.attrCount());
    for (auto const& sourceAttr : source)
    {
        NameToken name = sourceAttr.name();
        // NOTE: Request a const attribute, to avoid bumping its dirty ID.
        BundleAttrib const* constDestAttr = getConstAttr(name);
        if (constDestAttr != nullptr && constDestAttr->dirtyID() == sourceAttr.dirtyID())
        {
            continue;
        }

        if (constDestAttr == nullptr)
        {
            attrsToAdd.push_back(
                { sourceAttr.m_name, Type(sourceAttr.m_type), 0, sourceAttr.m_source });
        }
    }

    // add the attributes
    addAttrs(attrsToAdd);

    // copy the data
    for (auto const& sourceAttr : source)
    {
        NameToken name = sourceAttr.name();
        // NOTE: Request a const attribute, to avoid bumping its dirty ID.
        BundleAttrib const* constDestAttr = getConstAttr(name);
        CARB_ASSERT(constDestAttr != nullptr);
        if (constDestAttr == nullptr || constDestAttr->dirtyID() == sourceAttr.dirtyID())
        {
            continue;
        }
        const_cast<BundleAttrib*>(constDestAttr)->copyContentsFrom(sourceAttr);
    }

    CARB_ASSERT(attrCount() >= source.attrCount());

    // If there are more attributes in this than in source, remove any that aren't in source.
    auto& attrMap = getAttributes();
    if (attrCount() > source.attrCount() && removeAttrsNotInSource)
    {
        std::vector<NameToken> attrsToRemove;
        for (auto it = attrMap.begin(); it != attrMap.end();)
        {
            if (source.getConstAttr(it->second->name()) == nullptr)
            {
                it->second->clearContents();
                it = attrMap.erase(it);
            }
            else
            {
                ++it;
            }
        }
    }
    CARB_IGNOREWARNING_GNUC_POP
    CARB_IGNOREWARNING_MSC_POP
}

inline BundleAttrib* BundlePrim::getAttr(omni::graph::core::NameToken attrName) noexcept
{
    auto& attrs = getAttributes();
    auto it = attrs.find(attrName);
    if (it == attrs.end())
    {
        return nullptr;
    }

    BundleAttrib* attr = it->second.get();
    return attr;
}

inline omni::graph::core::BundleHandle BundlePrim::handle() noexcept
{
    return getBundlePtr()->getHandle();
}

inline BundlePrims* BundlePrim::getBundlePrims() noexcept
{
    omni::graph::core::IBundle2* bundle = getBundlePtr();
    if (bundle)
    {
        ConstBundlePrims* bundlePrims = ConstBundlePrim::getConstBundlePrims();
        return static_cast<BundlePrims*>(bundlePrims);
    }

    return nullptr;
}

inline BundlePrims* BundlePrim::bundlePrims() noexcept
{
    return getBundlePrims();
}

inline BundlePrimAttrIterator BundlePrim::begin() noexcept
{
    return BundlePrimAttrIterator(*this, getAttributes().begin());
}

inline BundlePrimAttrIterator BundlePrim::end() noexcept
{
    return BundlePrimAttrIterator(*this, getAttributes().end());
}

inline ConstBundlePrimAttrIterator BundlePrim::cbegin() noexcept
{
    return ConstBundlePrim::begin();
}

inline ConstBundlePrimAttrIterator BundlePrim::cend() noexcept
{
    return ConstBundlePrim::end();
}

inline omni::graph::core::IBundle2* BundlePrim::getBundlePtr(omni::graph::core::IConstBundle2* constBundle) noexcept
{
    auto bundle = omni::cast<omni::graph::core::IBundle2>(constBundle);
    return bundle.get();
}

inline omni::graph::core::IBundle2* BundlePrim::getBundlePtr() noexcept
{
    using namespace omni::graph::core;

    IConstBundle2* constBundle = getConstBundlePtr();
    IBundle2* bundle = getBundlePtr(constBundle);
    return bundle;
}

// ====================================================================================================
//
//                                      Bundle Primitives
//
// ====================================================================================================

inline BundlePrims::~BundlePrims() noexcept
{
    detach();
}

inline omni::graph::core::BundleHandle BundlePrims::handle() noexcept
{
    using namespace omni::graph::core;

    if (IBundle2* bundle = getBundlePtr())
    {
        return bundle->getHandle();
    }

    return BundleHandle{ BundleHandle::invalidValue() };
}

inline void BundlePrims::ensurePrimAttrsCached(BundlePrimIndex primIndex) noexcept
{
}

inline BundlePrims::BundlePrims()
    : ConstBundlePrims()
{
}

inline BundlePrims::BundlePrims(omni::graph::core::GraphContextObj const& context,
                                omni::graph::core::BundleHandle const& bundle)
    : BundlePrims()
{
    attach(context, bundle);
}

inline void BundlePrims::attach(omni::graph::core::GraphContextObj const& context,
                                omni::graph::core::BundleHandle const& bundleHandle) noexcept
{
    using namespace omni::graph::core;

    ComputeGraph* computeGraph = carb::getCachedInterface<ComputeGraph>();
    omni::core::ObjectPtr<IBundleFactory> factoryPtr = computeGraph->getBundleFactoryInterfacePtr();
    omni::core::ObjectPtr<IBundle2> bundlePtr = factoryPtr->getBundle(context, bundleHandle);
    ConstBundlePrims::attach(std::move(factoryPtr), std::move(bundlePtr));

    IBundle2* bundle = getBundlePtr();
    auto& bundlePrimIndexOffsetDef = detail::getBundlePrimIndexOffsetDefinition();
    m_bundlePrimIndexOffsetAttr = bundle->getBundleMetadataByName(bundlePrimIndexOffsetDef.token);
}

inline void BundlePrims::detach() noexcept
{
    using omni::graph::core::AttributeDataHandle;

    //
    // Bundle Level Attributes
    //
    m_bundlePrimIndexOffsetAttr = AttributeDataHandle{ AttributeDataHandle::invalidValue() };

    ConstBundlePrims::detach();
}

inline BundlePrim* BundlePrims::getPrim(BundlePrimIndex primIndex) noexcept
{
    using namespace omni::graph::core;

    auto createSortedBundlePrims = [this, &bundlePrims = *this]() -> BundlePrimArray
    {
        const size_t childBundleCount = getBundlePtr()->getChildBundleCount();
        std::vector<BundleHandle> handles(childBundleCount);
        getBundlePtr()->getChildBundles(handles.data(), handles.size());

        const GraphContextObj& graphContext = context();

        BundlePrimArray prims(childBundleCount);
        BundlePrimArray nonIndexedPrims;

        for (BundleHandle& handle : handles)
        {
            auto childBundle = getBundleFactoryPtr()->getBundle(graphContext, handle);
            BundlePrim* prim = new BundlePrim(bundlePrims, childBundle);
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

    // Since we acquire BundlePrim instance through BundlePrims interface,
    // we are required to bump dirty id of this prim because intention is to modify it.
    auto bundlePrim = static_cast<BundlePrim*>(ConstBundlePrims::getConstPrim(primIndex, createSortedBundlePrims));
    return bundlePrim;
}

inline BundlePrim* BundlePrims::getClearedPrim(BundlePrimIndex primIndex) noexcept
{
    BundlePrim* bundlePrim = getPrim(primIndex);
    if(!bundlePrim)
    {
        return nullptr;
    }

    bundlePrim->clearContents();
    return bundlePrim;
}

inline BundlePrim& BundlePrims::getCommonAttrs() noexcept
{
    ConstBundlePrim& commonAttributes = ConstBundlePrims::getConstCommonAttrs();
    return static_cast<BundlePrim&>(commonAttributes);
}

inline omni::graph::core::IBundle2* BundlePrims::getBundlePtr() noexcept
{
    using namespace omni::graph::core;

    auto constBundle = getConstBundlePtr();
    auto bundle = omni::cast<IBundle2>(constBundle);
    return bundle.get();
}

inline void BundlePrims::clearContents() noexcept
{
    for (BundlePrimIndex primIndex = getPrimCount(); primIndex != 0;)
    {
        --primIndex;
        removePrim(primIndex);
    }

    // Delete all attributes from this bundle.
    BundlePrim& thisBundle = getCommonAttrs();
    thisBundle.clearContents();

    // remove internal data
    IBundle2* bundle = getBundlePtr();

    if (m_bundlePrimIndexOffsetAttr.isValid())
    {
        const detail::AttrDefinition& attrDef = detail::getBundlePrimIndexOffsetDefinition();
        bundle->removeBundleMetadata(attrDef.token);
        m_bundlePrimIndexOffsetAttr = AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    // Clearing bundle prims internal attributes such as bundleDirtyID and others causes downstream problems.
    // Initial implementation never cleared those attributes.
    #if 0
    auto bundlePrimsInternalAttributes = {
        std::ref(m_bundleDirtyIDAttr),  //
        std::ref(m_primIndexAttr),      //
    };

    for (auto& internalAttribute : bundlePrimsInternalAttributes)
    {
        if (internalAttribute.get().isValid())
        {
            bundle->removeAttribute(internalAttribute.get());
        }
        internalAttribute.get() = AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }
    #endif
}

inline bool BundlePrims::removePrim(ConstBundlePrim* prim) noexcept
{
    return removePrim(prim->primIndex());
}

inline bool BundlePrims::removePrim(BundlePrimIndex primIndex) noexcept
{
    using namespace omni::graph::core;

    IBundle2* bundle = getBundlePtr();
    auto& context = this->context();
    auto& prims = getPrimitives();

    // remove children and attributes
    BundlePrim* childBundlePrim = getPrim(primIndex);
    if (!childBundlePrim)
    {
        return false;
    }

    // clear contents and remove bundle from a map
    childBundlePrim->clearContents();
    bundle->removeChildBundle(childBundlePrim->handle());

    // If removed primitive is not the last one,
    // swap last one with removed one and update index.
    size_t const newPrimCount = prims.size() - 1;
    if (primIndex != newPrimCount)
    {
        prims[primIndex] = std::move(prims[newPrimCount]);

        childBundlePrim = getPrim(primIndex);
        IBundle2* childBundle = childBundlePrim->getBundlePtr();
        CARB_ASSERT(childBundle);
        if (childBundle)
        {
            const detail::AttrDefinition& attrDef = detail::getPrimIndexDefinition();
            AttributeDataHandle primIndexAttr = childBundle->getBundleMetadataByName(attrDef.token);
            CARB_ASSERT(primIndexAttr.isValid());
            if (primIndexAttr.isValid())
            {
                *getDataW<uint64_t>(context, primIndexAttr) = primIndex;
            }
        }
    }

    prims.resize(newPrimCount);

    return true;
}

inline size_t BundlePrims::addPrims(size_t primCountToAdd) noexcept
{
    using namespace omni::graph::core;

    size_t oldPrimCount = getConstBundlePtr()->getChildBundleCount();
    if (primCountToAdd == 0)
    {
        return oldPrimCount;
    }

    size_t const newPrimCount = oldPrimCount + primCountToAdd;
    CARB_ASSERT(newPrimCount > oldPrimCount);

    IBundle2* bundle = getBundlePtr();
    IBundleFactory* factory = getBundleFactoryPtr();
    auto& context = this->context();

    if (!m_bundlePrimIndexOffsetAttr.isValid())
    {
        auto& attrDef = detail::getBundlePrimIndexOffsetDefinition();
        m_bundlePrimIndexOffsetAttr = bundle->getBundleMetadataByName(attrDef.token);
        if (!m_bundlePrimIndexOffsetAttr.isValid())
        {
            m_bundlePrimIndexOffsetAttr = bundle->createBundleMetadata(attrDef.token, attrDef.type);
            *getDataW<uint64_t>(context, m_bundlePrimIndexOffsetAttr) = 0;
        }
    }

    uint64_t* bundlePrimIndexOffsetData = getDataW<uint64_t>(context, m_bundlePrimIndexOffsetAttr);

    auto& primIndexDef = detail::getPrimIndexDefinition();

    // Create new child bundles.
    // All children are called 'prim' + primIndex, because IBundle2 interface does not allow sparse hierarchy.
    // Then child paths are stored as an attribute.
    BundlePrimArray& prims = getPrimitives();
    prims.resize(newPrimCount);

    std::string primPathStr;
    for (BundlePrimIndex primIndex = oldPrimCount; primIndex < newPrimCount; ++primIndex)
    {
        primPathStr = "prim" + std::to_string(*bundlePrimIndexOffsetData + primIndex - oldPrimCount);
        NameToken primName = context.iToken->getHandle(primPathStr.data());

        BundleHandle childHandle = bundle->createChildBundle(primName);
        auto childBundle = factory->getBundle(context, childHandle);
        CARB_ASSERT(childBundle);

        // A metadata attribute is created for each child bundle to store its prim index, so that each BundlePrims or
        // ConstBundlePrims instance attached to this bundle can have consistent prim indices.
        if (childBundle)
        {
            AttributeDataHandle primIndexAttr = childBundle->createBundleMetadata(primIndexDef.token, primIndexDef.type);
            *getDataW<uint64_t>(context, primIndexAttr) = primIndex;
        }

        auto newPrim = new BundlePrim(*this, std::move(childBundle));
        prims[primIndex].reset(newPrim);
    }

    *bundlePrimIndexOffsetData += primCountToAdd; // Update prim index offset.
    return oldPrimCount;
}

inline BundlePrimIterator BundlePrims::begin() noexcept
{
    return BundlePrimIterator(*this);
}

inline BundlePrimIterator BundlePrims::end() noexcept
{
    return BundlePrimIterator(*this, getPrimCount());
}

inline ConstBundlePrimIterator BundlePrims::cbegin() noexcept
{
    return ConstBundlePrims::begin();
}

inline ConstBundlePrimIterator BundlePrims::cend() noexcept
{
    return ConstBundlePrims::end();
}

// ====================================================================================================
//
//                                      Bundle Primitive Iterator
//
// ====================================================================================================

inline BundlePrimIterator::BundlePrimIterator(BundlePrims& bundlePrims, BundlePrimIndex primIndex) noexcept
    : m_bundlePrims(&bundlePrims), m_primIndex(primIndex)
{
}

inline bool BundlePrimIterator::operator==(BundlePrimIterator const& that) const noexcept
{
    return m_bundlePrims == that.m_bundlePrims && m_primIndex == that.m_primIndex;
}

inline bool BundlePrimIterator::operator!=(BundlePrimIterator const& that) const noexcept
{
    return !(*this == that);
}

inline BundlePrim& BundlePrimIterator::operator*() noexcept
{
    return *(m_bundlePrims->getPrim(m_primIndex));
}

inline BundlePrim* BundlePrimIterator::operator->() noexcept
{
    return m_bundlePrims->getPrim(m_primIndex);
}

inline BundlePrimIterator& BundlePrimIterator::operator++() noexcept
{
    ++m_primIndex;
    return *this;
}

// ====================================================================================================
//
//                                      Bundle Primitive Attribute Iterator
//
// ====================================================================================================

inline BundlePrimAttrIterator::BundlePrimAttrIterator(BundlePrim& bundlePrim, BundlePrim::AttrMapIteratorType attrIter) noexcept
    : m_bundlePrim(&bundlePrim), m_attrIter(attrIter)
{
}

inline bool BundlePrimAttrIterator::operator==(BundlePrimAttrIterator const& that) const noexcept
{
    return m_bundlePrim == that.m_bundlePrim && m_attrIter == that.m_attrIter;
}

inline bool BundlePrimAttrIterator::operator!=(BundlePrimAttrIterator const& that) const noexcept
{
    return !(*this == that);
}

inline BundleAttrib const* BundlePrimAttrIterator::getConst() noexcept
{
    CARB_ASSERT(m_bundlePrim != nullptr);
    CARB_ASSERT(m_attrIter->second);
    BundleAttrib* attr = m_attrIter->second.get();
    return attr;
}

inline BundleAttrib& BundlePrimAttrIterator::operator*() noexcept
{
    CARB_ASSERT(m_bundlePrim != nullptr);
    CARB_ASSERT(m_attrIter->second);
    BundleAttrib* attr = m_attrIter->second.get();
    return *attr;
}

inline BundleAttrib* BundlePrimAttrIterator::operator->() noexcept
{
    CARB_ASSERT(m_bundlePrim != nullptr);
    CARB_ASSERT(m_attrIter->second);
    BundleAttrib* attr = m_attrIter->second.get();
    return attr;
}

inline BundlePrimAttrIterator& BundlePrimAttrIterator::operator++() noexcept
{
    ++m_attrIter;
    return *this;
}

} // namespace core
} // namespace graph
} // namespace omni
