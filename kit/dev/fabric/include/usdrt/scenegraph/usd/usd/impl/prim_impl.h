// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "usd_decl.h"

namespace usdrt
{

inline bool UsdPrim::HasAttribute(const TfToken& name) const
{
    if (!m_prim)
    {
        return false;
    }

    return m_prim->hasAttribute(static_cast<TokenC>(name));
}

inline UsdAttribute UsdPrim::GetAttribute(const TfToken& name) const
{
    if (!m_prim)
    {
        return UsdAttribute{ nullptr };
    }

    return UsdAttribute{ m_prim->getAttribute(static_cast<TokenC>(name)) };
}

inline std::vector<UsdAttribute> UsdPrim::GetAttributes() const
{
    std::vector<UsdAttribute> result;

    if (!m_prim)
    {
        return result;
    }

    std::vector<omni::core::ObjectPtr<usdrt::IRtAttribute>> attrList = m_prim->getAttributes();
    result.reserve(attrList.size());
    for (const auto& attrPtr : attrList)
    {
        result.push_back(UsdAttribute{ attrPtr });
    }

    return result;
}

inline std::vector<UsdAttribute> UsdPrim::GetAuthoredAttributes() const
{
    std::vector<UsdAttribute> result;

    if (!m_prim)
    {
        return result;
    }

    std::vector<omni::core::ObjectPtr<usdrt::IRtAttribute>> attrList = m_prim->getAuthoredAttributes();
    result.reserve(attrList.size());
    for (const auto& attrPtr : attrList)
    {
        result.push_back(UsdAttribute{ attrPtr });
    }

    return result;
}

inline UsdAttribute UsdPrim::CreateAttribute(const TfToken& name, const SdfValueTypeName& typeName, bool custom) const
{
    if (!m_prim)
    {
        return UsdAttribute{ nullptr };
    }

    return UsdAttribute{ m_prim->createAttribute(
        static_cast<TokenC>(name), typeName, custom, usdrt::Variability::eVarying) };
}


inline bool UsdPrim::HasRelationship(const TfToken& name) const
{
    if (!m_prim)
    {
        return false;
    }

    return m_prim->hasRelationship(static_cast<TokenC>(name));
}

inline UsdRelationship UsdPrim::GetRelationship(const TfToken& name) const
{
    if (!m_prim)
    {
        return UsdRelationship{ nullptr };
    }

    return UsdRelationship{ m_prim->getRelationship(static_cast<TokenC>(name)) };
}

inline std::vector<UsdRelationship> UsdPrim::GetRelationships() const
{
    std::vector<UsdRelationship> result;

    if (!m_prim)
    {
        return result;
    }

    std::vector<omni::core::ObjectPtr<usdrt::IRtRelationship>> attrList = m_prim->getRelationships();
    result.reserve(attrList.size());
    for (const auto& attrPtr : attrList)
    {
        result.push_back(UsdRelationship{ attrPtr });
    }

    return result;
}

inline std::vector<UsdRelationship> UsdPrim::GetAuthoredRelationships() const
{
    std::vector<UsdRelationship> result;

    if (!m_prim)
    {
        return result;
    }

    std::vector<omni::core::ObjectPtr<usdrt::IRtRelationship>> attrList = m_prim->getAuthoredRelationships();
    result.reserve(attrList.size());
    for (const auto& attrPtr : attrList)
    {
        result.push_back(UsdRelationship{ attrPtr });
    }

    return result;
}

inline UsdRelationship UsdPrim::CreateRelationship(const TfToken& relName, bool custom) const
{
    if (!m_prim)
    {
        return UsdRelationship{ nullptr };
    }

    return UsdRelationship{ m_prim->createRelationship(static_cast<TokenC>(relName), custom) };
}

inline bool UsdPrim::RemoveProperty(const TfToken& name) const
{
    if (!m_prim)
    {
        return false;
    }

    return m_prim->removeProperty(static_cast<TokenC>(name));
}

inline TfTokenVector UsdPrim::GetPropertyNames() const
{
    std::vector<TfToken> props;

    std::vector<UsdRelationship> rels = GetRelationships();
    for (auto rel : rels)
    {
        props.push_back(rel.GetName());
    }

    std::vector<UsdAttribute> attrs = GetAttributes();
    for (auto attr : attrs)
    {
        props.push_back(attr.GetName());
    }

    return props;
}


inline TfTokenVector UsdPrim::GetAuthoredPropertyNames() const
{
    return GetPropertyNames();
}

inline bool UsdPrim::HasProperty(const TfToken& name) const
{
    return HasRelationship(name) || HasAttribute(name);
}

inline bool UsdPrim::IsValid() const
{
    if (!m_prim)
    {
        return false;
    }

    return m_prim->isValid();
}

inline UsdStageRefPtr UsdPrim::GetStage() const
{
    if (!m_prim)
    {
        return UsdStageRefPtr(nullptr);
    }

    UsdStageRefPtr stage(new UsdStage{ m_prim->getStage() });
    return stage;
}

inline UsdPrim UsdPrim::GetPrim() const
{
    if (!m_prim)
    {
        return UsdPrim{ nullptr };
    }

    return UsdPrim{ m_prim->getPrim() };
}

inline const TfToken UsdPrim::GetName() const
{
    if (!m_prim)
    {
        return TfToken();
    }

    return TfToken(m_prim->getName());
}

inline SdfPath UsdPrim::GetPath() const
{
    if (!m_prim)
    {
        return SdfPath();
    }

    return SdfPath(m_prim->getPath());
}

inline const SdfPath UsdPrim::GetPrimPath() const
{
    if (!m_prim)
    {
        return SdfPath();
    }

    return SdfPath(m_prim->getPrimPath());
}

inline UsdPrim::operator bool() const
{
    return IsValid();
}

inline UsdPrim UsdPrim::GetChild(const TfToken& name, bool prefetchFromUsd) const
{
    auto prim107 = omni::core::cast<IRtPrim107>(m_prim.get());

    if (!prim107)
    {
        return UsdPrim{ nullptr };
    }

    return UsdPrim{ prim107->getChild107(static_cast<TokenC>(name), prefetchFromUsd) };
}

inline std::vector<UsdPrim> UsdPrim::GetChildren(bool prefetchFromUsd) const
{
    auto prim107 = omni::core::cast<IRtPrim107>(m_prim.get());

    std::vector<UsdPrim> result;

    if (!prim107)
    {
        return result;
    }

    std::vector<omni::core::ObjectPtr<usdrt::IRtPrim>> primList = prim107->getChildren107(prefetchFromUsd);
    result.reserve(primList.size());
    for (const auto& primPtr : primList)
    {
        result.push_back(UsdPrim{ primPtr });
    }

    return result;
}

inline TfTokenVector UsdPrim::GetChildrenNames(bool prefetchFromUsd) const
{
    std::vector<UsdPrim> children = GetChildren(prefetchFromUsd);
    TfTokenVector names;
    std::transform(
        children.begin(), children.end(), std::back_inserter(names), [](const UsdPrim prim) { return prim.GetName(); });
    return names;
}


inline std::vector<UsdPrim> UsdPrim::GetAllChildren(bool prefetchFromUsd) const
{
    return GetChildren(prefetchFromUsd);
}

inline TfTokenVector UsdPrim::GetAllChildrenNames(bool prefetchFromUsd) const
{
    return GetChildrenNames(prefetchFromUsd);
}

inline UsdPrim UsdPrim::GetParent(bool prefetchFromUsd) const
{
    auto prim107 = omni::core::cast<IRtPrim107>(m_prim.get());

    if (!prim107)
    {
        return UsdPrim{ nullptr };
    }

    return UsdPrim{ prim107->getParent107(prefetchFromUsd) };
}


inline UsdPrim UsdPrim::GetNextSibling(bool prefetchFromUsd) const
{
    auto prim107 = omni::core::cast<IRtPrim107>(m_prim.get());

    if (!prim107)
    {
        return UsdPrim{ nullptr };
    }

    return UsdPrim{ prim107->getNextSibling107(prefetchFromUsd) };
}

inline TfToken UsdPrim::GetTypeName() const
{
    if (!m_prim)
    {
        return TfToken();
    }

    return TfToken(omni::fabric::Token(m_prim->getTypeName()));
}

inline bool UsdPrim::SetTypeName(const TfToken& typeName) const
{
    if (!m_prim)
    {
        return false;
    }

    return m_prim->setTypeName(static_cast<TokenC>(typeName));
}

inline bool UsdPrim::ClearTypeName() const
{
    if (!m_prim)
    {
        return false;
    }

    return m_prim->clearTypeName();
}

inline bool UsdPrim::HasAuthoredTypeName() const
{
    if (!m_prim)
    {
        return false;
    }

    return m_prim->hasAuthoredTypeName();
}

inline bool UsdPrim::_IsA(const TfToken& schemaType, bool validateSchemaType) const
{
    auto schemaRegistry = UsdSchemaRegistry::GetInstance();
    if (validateSchemaType)
    {
        if (schemaRegistry.IsUnknown(schemaType))
        {
            // Error, invalid query type
            return false;
        }
    }
    return schemaRegistry.IsA(GetTypeName(), schemaType);
}

inline bool UsdPrim::IsA(const TfToken& schemaType) const
{
    return _IsA(schemaType, true);
}

// API schemas
inline bool UsdPrim::AddAppliedSchema(const TfToken& appliedSchemaName) const
{
    if (!m_prim)
    {
        return false;
    }
    return CreateAttribute(appliedSchemaName, SdfValueTypeNames->AppliedSchemaTypeTag, true).IsValid();
}

inline bool UsdPrim::RemoveAppliedSchema(const TfToken& appliedSchemaName) const
{
    if (!m_prim)
    {
        return false;
    }

    UsdAttribute attr = GetAttribute(appliedSchemaName);
    if (!(attr.IsValid() && attr.GetTypeName() == SdfValueTypeNames->AppliedSchemaTypeTag))
    {
        return true;
    }
    return RemoveProperty(appliedSchemaName);
}

inline bool UsdPrim::HasAPI(const TfToken& schemaIdentifier, const TfToken& instanceName) const
{
    if (!m_prim)
    {
        return false;
    }

    auto registry = UsdSchemaRegistry::GetInstance();
    if (registry.IsUnknown(schemaIdentifier) || registry.IsTyped(schemaIdentifier) ||
        !registry.IsAppliedAPISchema(schemaIdentifier) || !registry.IsA(schemaIdentifier, "UsdAPISchemaBase"))
    {
        // invalid query type
        return false;
    }

    bool isMultipleApply = registry.IsMultipleApplyAPISchema(schemaIdentifier);
    if (!isMultipleApply && !instanceName.IsEmpty())
    {
        // invalid: single apply must not contain instance name
        return false;
    }

    TfToken alias = UsdSchemaRegistry::GetInstance().GetAliasFromName(schemaIdentifier);

    // otherwise, look for the attribute directly
    TfToken apiName = TfToken(SdfPath::JoinIdentifier(alias, instanceName));
    UsdAttribute attr = GetAttribute(apiName);
    if (!attr.IsValid())
    {
        return false;
    }

    return attr.GetTypeName() == SdfValueTypeNames->AppliedSchemaTypeTag;
}

inline bool UsdPrim::ApplyAPI(const TfToken& schemaIdentifier, const TfToken& instanceName) const
{
    if (!m_prim)
    {
        return false;
    }

    if (!UsdSchemaRegistry::GetInstance().IsAppliedAPISchema(schemaIdentifier))
    {
        if (!instanceName.IsEmpty())
        {
            // Single apply schemas cannot have an instance name
            return false;
        }

        // Must be an applied API schema. Error, do nothing.
        return false;
    }
    bool isMultiApply = UsdSchemaRegistry::GetInstance().IsMultipleApplyAPISchema(schemaIdentifier);
    if (isMultiApply && instanceName.IsEmpty())
    {
        // Multiple apply api schemas must have an instance name
        return false;
    }

    TfToken alias = UsdSchemaRegistry::GetInstance().GetAliasFromName(schemaIdentifier);
    TfToken apiName = TfToken(SdfPath::JoinIdentifier(alias, instanceName));

    bool result = AddAppliedSchema(apiName);
    if (isMultiApply)
    {
        result &= AddAppliedSchema(alias);
    }
    return result;
}

inline bool UsdPrim::RemoveAPI(const TfToken& schemaIdentifier, const TfToken& instanceName) const
{
    if (!m_prim)
    {
        return false;
    }


    if (!UsdSchemaRegistry::GetInstance().IsAppliedAPISchema(schemaIdentifier))
    {
        if (!instanceName.IsEmpty())
        {
            // Single apply schemas cannot have an instance name
            return false;
        }
        // Must be an applied API schema.
        return false;
    }

    bool isMultiApply = UsdSchemaRegistry::GetInstance().IsMultipleApplyAPISchema(schemaIdentifier);
    if (isMultiApply && instanceName.IsEmpty())
    {
        // Multiple apply api schemas must have an instance name
        return false;
    }

    TfToken alias = UsdSchemaRegistry::GetInstance().GetAliasFromName(schemaIdentifier);
    TfToken apiName = TfToken(SdfPath::JoinIdentifier(alias, instanceName));
    bool result = RemoveAppliedSchema(apiName);
    if (isMultiApply)
    {
        // search the list of applied schemas to see if any start with the schemaIdentifier alias
        auto appliedSchemas = GetAppliedSchemas();
        bool found =
            std::any_of(appliedSchemas.begin(), appliedSchemas.end(),
                        [&alias](const TfToken& appliedSchema)
                        // this was TfStringStartsWith
                        { return appliedSchema.GetString().find(alias.GetString() + ":") != std::string::npos; });
        if (!found)
        {
            result &= RemoveAppliedSchema(alias);
        }
    }
    return result;
}

inline TfTokenVector UsdPrim::GetAppliedSchemas() const
{
    if (!m_prim)
    {
        return TfTokenVector();
    }

    auto prim105 = omni::core::cast<IRtPrim105>(m_prim.get());

    omni::fabric::TypeC apiSchemaType = SdfValueTypeNames->AppliedSchemaTypeTag.GetAsTypeC();

    uint32_t numApis = prim105->getAttributesWithTypeCount(apiSchemaType);

    if (numApis == 0)
    {
        return TfTokenVector();
    }

    std::vector<usdrt::IRtAttribute*> vec;
    vec.resize(numApis);
    std::vector<omni::core::ObjectPtr<usdrt::IRtAttribute>> counted;
    counted.reserve(numApis);

    const bool ok = prim105->getAttributesWithType(apiSchemaType, vec.data(), numApis);

    if (!ok)
    {
        return TfTokenVector();
    }

    for (size_t i = 0; i < numApis; ++i)
    {
        counted.emplace_back(vec[i], omni::core::kSteal);
    }

    TfTokenVector result;
    result.reserve(numApis);
    for (const auto& attr : counted)
    {
        result.push_back(TfToken(omni::fabric::Token(attr->getName())));
    }

    return result;
}

static_assert(std::is_standard_layout<UsdPrim>::value, "UsdPrim must be standard layout");

} // namespace usdrt
