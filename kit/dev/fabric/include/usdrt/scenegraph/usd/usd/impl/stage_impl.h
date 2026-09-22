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

#include <usdrt/scenegraph/usd/rt/defines.h>
#include <usdrt/scenegraph/usd/rt/primSelection.h>

namespace usdrt
{

inline UsdStage::~UsdStage(void)
{
    if (!m_stage)
    {
        return;
    }

    m_stage->done();
}

inline UsdStageRefPtr UsdStage::CreateNew(const std::string& identifier, InitialLoadSet load)
{
    auto iStage = omni::core::createType<usdrt::IRtStage>();
    if (!iStage)
    {
        return UsdStageRefPtr(new UsdStage{ nullptr });
    }
    UsdStageRefPtr newStage(new UsdStage{ iStage->createNew(identifier.c_str()) });

    return newStage;
}

inline UsdStageRefPtr UsdStage::Open(const std::string& filePath, InitialLoadSet load)
{
    auto iStage = omni::core::createType<usdrt::IRtStage>();
    if (!iStage)
    {
        return UsdStageRefPtr(new UsdStage{ nullptr });
    }
    UsdStageRefPtr newStage(new UsdStage{ iStage->open(filePath.c_str()) });

    return newStage;
}

inline UsdStageRefPtr UsdStage::CreateInMemory(const std::string& identifier, InitialLoadSet load)
{
    auto iStage = omni::core::createType<usdrt::IRtStage>();
    if (!iStage)
    {
        return UsdStageRefPtr(new UsdStage{ nullptr });
    }
    UsdStageRefPtr newStage(new UsdStage{ iStage->createInMemory(identifier.c_str()) });

    return newStage;
}

inline UsdStageRefPtr UsdStage::CreateOnlyInFabric()
{
    auto iStage = omni::core::createType<usdrt::IRtStage107>();
    if (!iStage)
    {
        return UsdStageRefPtr(new UsdStage{ nullptr });
    }
    UsdStageRefPtr newStage(new UsdStage{ iStage->createOnlyInFabric() });

    return newStage;
}

inline UsdStageRefPtr UsdStage::Attach(omni::fabric::UsdStageId stageId,
                                       omni::fabric::StageReaderWriterId stageReaderWriterId)
{
    UsdStageRefPtr stage;
    auto iStage = omni::core::createType<usdrt::IRtStage>();
    if (!iStage)
    {
        stage.reset(new UsdStage{ nullptr });
    }
    else if (stageReaderWriterId.id == 0)
    {
        stage.reset(new UsdStage{ iStage->attachUnknown(stageId) });
    }
    else
    {
        stage.reset(new UsdStage{ iStage->attach(stageId, stageReaderWriterId) });
    }

    return stage;
}

inline UsdStageRefPtr UsdStage::Attach(const omni::fabric::FabricId fabricId)
{
    UsdStageRefPtr stage;
    auto iStage107 = omni::core::createType<usdrt::IRtStage107>();
    if (!iStage107)
    {
        stage.reset(new UsdStage{ nullptr });
    }
    else
    {
        stage.reset(new UsdStage{ iStage107->attachByFabricId(fabricId) });
    }

    return stage;
}

inline UsdPrim UsdStage::GetPrimAtPath(const SdfPath& path, bool prefetchFromUsd) const
{
    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());
    
    if (!stage107)
    {
        return UsdPrim{ nullptr };
    }

    return UsdPrim{ stage107->getPrimAtPath107(static_cast<PathC>(path), prefetchFromUsd) };
}

inline UsdPrim UsdStage::GetDefaultPrim(bool prefetchFromUsd) const
{
    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());

    if (!stage107)
    {
        return UsdPrim{ nullptr };
    }

    return UsdPrim{ stage107->getDefaultPrim107(prefetchFromUsd) };
}

inline bool UsdStage::RemovePrim(const SdfPath& path) const
{
    if (!m_stage)
    {
        return false;
    }

    return m_stage->removePrim(static_cast<PathC>(path));
}

inline UsdPrim UsdStage::GetPseudoRoot() const
{
    if (!m_stage)
    {
        return UsdPrim{ nullptr };
    }

    return GetPrimAtPath("/");
}

inline UsdPrim UsdStage::DefinePrim(const SdfPath& path, const TfToken& typeName)
{
    if (!m_stage)
    {
        return UsdPrim{ nullptr };
    }

    return UsdPrim{ m_stage->definePrim(static_cast<PathC>(path), static_cast<TokenC>(typeName)) };
}

inline UsdAttribute UsdStage::GetAttributeAtPath(const SdfPath& path, bool prefetchFromUsd) const
{
    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());

    if (!stage107)
    {
        return UsdAttribute{ nullptr };
    }

    return UsdAttribute{ stage107->getAttributeAtPath107(
        static_cast<PathC>(path.GetPrimPath()), static_cast<TokenC>(path.GetNameToken()), prefetchFromUsd) };
}

inline UsdRelationship UsdStage::GetRelationshipAtPath(const SdfPath& path, bool prefetchFromUsd) const
{
    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());

    if (!stage107)
    {
        return UsdRelationship{ nullptr };
    }

    return UsdRelationship{ stage107->getRelationshipAtPath107(
        static_cast<PathC>(path.GetPrimPath()), static_cast<TokenC>(path.GetNameToken()), prefetchFromUsd) };
}

inline UsdPrimRange UsdStage::Traverse()
{
    return UsdPrimRange(GetPrimAtPath("/"));
}

inline omni::fabric::UsdStageId UsdStage::GetStageId() const
{
    if (!m_stage)
    {
        return omni::fabric::kUninitializedStage;
    }

    return m_stage->getStageId();
}

inline omni::fabric::StageReaderWriterId UsdStage::GetStageReaderWriterId() const
{
    if (!m_stage)
    {
        return { 0 };
    }

    return m_stage->getStageReaderWriterId();
}

inline omni::fabric::StageReaderWriterId UsdStage::GetStageInProgressId() const
{
    return GetStageReaderWriterId();
}

inline omni::fabric::FabricId UsdStage::GetFabricId() const
{
    if (!m_stage)
    {
        return omni::fabric::kInvalidFabricId;
    }

    auto stage105 = omni::core::cast<IRtStage105>(m_stage.get());

    return stage105->getFabricId();
}

inline bool UsdStage::IsFabricOnlyStage() const
{
    if (!m_stage)
    {
        return false;
    }

    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());

    return stage107->isFabricOnlyStage();
}

inline bool UsdStage::SimStageWithHistoryExists(omni::fabric::UsdStageId stageId)
{
    auto iStageWithHistory = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();

    if (iStageWithHistory)
    {
        return iStageWithHistory->exists(stageId);
    }

    return false;
}

inline bool UsdStage::StageWithHistoryExists(omni::fabric::UsdStageId stageId)
{
    return SimStageWithHistoryExists(stageId);
}

inline void UsdStage::WriteToStage(bool includePrivateFabricProperties, bool convertFabricXforms) const
{
    if (!m_stage)
    {
        return;
    }

    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());
    if (stage107->isFabricOnlyStage())
    {
        CARB_LOG_WARN("usdrt::UsdStage::WriteToStage - Fabric only stage. Cannot write to a non-existent USD stage.");
        return;
    }

    stage107->writeWithOptions(nullptr, includePrivateFabricProperties, convertFabricXforms);
}

inline void UsdStage::WriteToLayer(const std::string& filePath,
                                   bool includePrivateFabricProperties,
                                   bool convertFabricXforms) const
{
    if (!m_stage)
    {
        return;
    }

    auto stage106 = omni::core::cast<IRtStage106>(m_stage.get());

    stage106->writeWithOptions(filePath.c_str(), includePrivateFabricProperties, convertFabricXforms);
}

inline bool UsdStage::HasPrimAtPath(const SdfPath& path, bool excludeTags) const
{
    if (!m_stage)
    {
        return false;
    }

    auto stage105 = omni::core::cast<IRtStage105>(m_stage.get());

    return stage105->hasPrimAtPath105(static_cast<PathC>(path), excludeTags);
}

inline std::vector<SdfPath> UsdStage::GetPrimsWithTypeName(const TfToken& typeName) const
{
    if (!m_stage)
    {
        return std::vector<SdfPath>();
    }

    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());

    std::vector<SdfPath> result;
    omni::vector<omni::fabric::PathC> resultC;

    const bool ok = stage107->find107(omni::fabric::TokenC(typeName), nullptr, 0, resultC);

    if (ok)
    {
        result.reserve(resultC.size());
        for (const auto pathC : resultC)
        {
            result.push_back(SdfPath(pathC));
        }
    }

    return result;
}

inline std::vector<SdfPath> UsdStage::GetPrimsWithAppliedAPIName(const TfToken& apiName) const
{
    if (!m_stage)
    {
        return std::vector<SdfPath>();
    }

    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());

    std::vector<SdfPath> result;
    omni::vector<omni::fabric::PathC> resultC;

    const omni::fabric::TokenC apiNameC = omni::fabric::TokenC(apiName);
    const bool ok = stage107->find107(omni::fabric::kUninitializedToken, &apiNameC, 1, resultC);

    if (ok)
    {
        result.reserve(resultC.size());
        for (const auto pathC : resultC)
        {
            result.push_back(SdfPath(pathC));
        }
    }

    return result;
}

inline std::vector<SdfPath> UsdStage::GetPrimsWithTypeAndAppliedAPIName(const TfToken& typeName,
                                                                        const std::vector<TfToken>& apiNames) const
{
    if (!m_stage)
    {
        return std::vector<SdfPath>();
    }

    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());

    std::vector<SdfPath> result;
    omni::vector<omni::fabric::PathC> resultC;

    const bool ok = stage107->find107(omni::fabric::TokenC(typeName),
                                      reinterpret_cast<const omni::fabric::TokenC*>(apiNames.data()),
                                      (uint32_t)apiNames.size(), resultC);

    if (ok)
    {
        result.reserve(resultC.size());
        for (const auto pathC : resultC)
        {
            result.push_back(SdfPath(pathC));
        }
    }

    return result;
}

inline GfRange3d UsdStage::GetStageExtent() const
{
    if (!m_stage)
    {
        return GfRange3d();
    }

    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());

    if (stage107->isFabricOnlyStage())
    {
        CARB_LOG_WARN("usdrt::UsdStage::GetStageExtent - Cannot compute. Fabric only stage.");
        return GfRange3d();
    }

    GfRange3d result;

    stage107->computeWorldBound(&result);

    return result;
}

inline RtPrimSelection UsdStage::SelectPrims(std::vector<TfToken> requireAppliedSchemas,
                                             std::vector<AttrSpec> requireAttrs,
                                             std::optional<TfToken> requirePrimTypeName,
                                             uint32_t device,
                                             bool wantPaths)
{
    auto stage106_4 = omni::core::cast<IRtStage106_4>(m_stage.get());

    std::vector<omni::fabric::TokenC> requireAppliedSchemasC(requireAppliedSchemas.size());
    for (size_t i = 0; i != requireAppliedSchemas.size(); i++)
    {
        requireAppliedSchemasC[i] = static_cast<omni::fabric::TokenC>(requireAppliedSchemas[i]);
    }

    std::vector<AttrSpecC> requireAttrsC(requireAttrs.size());
    for (size_t i = 0; i != requireAttrs.size(); i++)
    {
        requireAttrsC[i].type = omni::fabric::Type(omni::fabric::TypeC(requireAttrs[i].type));
        requireAttrsC[i].name = static_cast<omni::fabric::TokenC>(requireAttrs[i].name);
        requireAttrsC[i].accessType = requireAttrs[i].accessType;
    }

    // Convert carb::optional into a C-ABI friendly pointer
    omni::fabric::TokenC primTypeNameC;
    omni::fabric::TokenC* primTypeNameCptr = nullptr;
    if (requirePrimTypeName)
    {
        primTypeNameC = static_cast<omni::fabric::TokenC>(requirePrimTypeName.value());
        primTypeNameCptr = &primTypeNameC;
    }

    RtPrimSelection selection = RtPrimSelection{ stage106_4->selectPrims1064(
        requireAppliedSchemasC.data(), requireAppliedSchemasC.size(), requireAttrsC.data(), requireAttrsC.size(),
        primTypeNameCptr, device, wantPaths) };

    return selection;
}

inline void UsdStage::SynchronizeToFabric(TimeChange timeChange, const usdrt::UsdTimeCode& time)
{
    if (!m_stage)
    {
        return;
    }

    auto stage107 = omni::core::cast<IRtStage107>(m_stage.get());
    if (stage107)
    {
        if (stage107->isFabricOnlyStage())
        {
            CARB_LOG_WARN("usdrt::UsdStage::SynchronizeToFabric - Fabric only stage. Cannot sync with USD.");
            return;
        }

        stage107->synchronizeToFabric(timeChange, time);
    }
}


static_assert(std::is_standard_layout<UsdStage>::value, "UsdStage must be standard layout");

} // namespace usdrt
