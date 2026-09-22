// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include <omni/fabric/FabricUSD.h>


namespace omni
{
namespace fabric
{

inline TokenC StageReaderWriterUsd::registerToken(const StageReaderWriter& stage, const PXR_NS::TfToken& token)
{
    TokenC tokenC = asInt(token);
    stage.m_interface->registerTfTokens(stage.getId(), { &tokenC, 1 });
    return tokenC;
}

inline void StageReaderWriterUsd::registerTokens(const StageReaderWriter& stage,
                                                 const gsl::span<const PXR_NS::TfToken>& tfTokens)
{
    std::vector<TokenC> tokenCs(tfTokens.size());
    std::transform(
        tfTokens.begin(), tfTokens.end(), tokenCs.begin(), [](const PXR_NS::TfToken& token) { return asInt(token); });
    stage.m_interface->registerTfTokens(stage.getId(), { tokenCs.data(), tokenCs.size() });
}

inline PathC StageReaderWriterUsd::registerPath(const StageReaderWriter& stage, const PXR_NS::SdfPath& path)
{
    PathC pathC = asInt(path);
    stage.m_interface->registerSdfPaths(stage.getId(), { &pathC, 1 });
    return pathC;
}

inline void StageReaderWriterUsd::registerPaths(const StageReaderWriter& stage,
                                                const gsl::span<const PXR_NS::SdfPath>& sdfPaths)
{
    std::vector<PathC> pathCs(sdfPaths.size());
    std::transform(
        sdfPaths.begin(), sdfPaths.end(), pathCs.begin(), [](const PXR_NS::SdfPath& path) { return asInt(path); });
    stage.m_interface->registerSdfPaths(stage.getId(), { pathCs.data(), pathCs.size() });
}

} // namespace fabric
} // namespace omni
