// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/core/IObject.h>
#include <omni/fabric/IdTypes.h>
#include <omni/fabric/SimStageWithHistory.h>
#include <usdrt/population/IUtils.h>


// Only pixar header that should be included!
#include "../ISceneDelegate.h"

#include <usdrt/gf/matrix.h>
#include <usdrt/gf/range.h>
#include <usdrt/gf/rect.h>
#include <usdrt/gf/vec.h>

#include <float.h>

namespace usdrt
{

namespace hydra
{

// Matching the PXR_NS::CameraUtilConformWindowPolicy.
enum class OMNI_ATTR("prefix=e") CameraConformWindowPolicy : int32_t
{
    eMatchVertically,
    eMatchHorizontally,
    eUtilFit,
    eUtilCrop,
    eUtilDontConform,
};

struct SimpleLight
{
    usdrt::GfMatrix4d transform = usdrt::GfMatrix4d(1.0);
    usdrt::GfVec4f ambient = { 0.7f, 0.7f, 0.7f, 1.0f };
    usdrt::GfVec4f diffuse = { 1.0f, 1.0f, 1.0f, 1.0f };
    usdrt::GfVec4f specular = { 0.2f, 0.2f, 0.2f, 1.0f };
    usdrt::GfVec4f position = { 0.0f, 0.0f, 0.0f, 0.0f };
    usdrt::GfVec3f spotDirection = { 0.0f, 0.0f, -1.0f };
    usdrt::GfVec3f attenuation = { 1.0f, 0.0f, 0.0f };
    float spotCutoff = 180.0f;
    float spotFalloff = 0.0f;
    float shadowBias = 0.0f;
    float shadowBlur = 0.0f;
    int shadowResolution = 512;
    int shadowIndexStart = 0;
    int shadowIndexEnd = 0;
    bool isCameraSpaceLight = false;
    bool hasShadow = false;
    bool isDomeLight = false;
};

struct SimpleMaterial
{
    usdrt::GfVec4f ambient = { 0.4f, 0.4f, 0.4f, 1.0f };
    usdrt::GfVec4f diffuse = { 0.8f, 0.8f, 0.8f, 1.0f };
    usdrt::GfVec4f specular = { 0.5f, 0.5f, 0.5f, 1.0f };
    usdrt::GfVec4f emission = { 0.0f, 0.0f, 0.0f, 1.0f };
    double shininess = 32.0f;
};

enum class OMNI_ATTR("prefix=e") DrawMode : int32_t
{
    ePoints,
    eWireframe,
    eWireframeOnSurface,
    eShadedFlat,
    eShadedSmooth,
    eGeomOnly,
    eGeomFlat,
    eGeomSmooth
};

enum class OMNI_ATTR("prefix=e") CullStyle : int32_t
{
    eNoOpinion,
    eNothing,
    eBack,
    eFront,
    eBackUnlessDoubleSided
};

struct RenderParams
{
    usdrt::GfVec4f overrideColor = { 0.0f, 0.0f, 0.0f, 0.0f };
    usdrt::GfVec4f wireframeColor = { 0.0f, 0.0f, 0.0f, 0.0f };
    usdrt::GfVec4f clearColor = { 0.0f, 0.0f, 0.0f, 1.0f };
    // TODO: Safe way to pass strings around?
    const char* colorCorrectionMode = nullptr;
    double frame = 0.0; // UsdTimeCode is using std::numeric_limits<double>::quiet_NaN()
    float complexity = 1.0f;
    float alphaThreshold = -1.0f;
    DrawMode drawMode = DrawMode::eShadedSmooth;
    CullStyle cullStyle = CullStyle::eNothing;
    int lut3dSizeOCIO = 65;
    bool showGuides = false;
    bool showProxy = true;
    bool showRender = false;
    bool forceRefresh = false;
    bool flipFrontFacing = false;
    bool enableIdRender = false;
    bool enableLighting = true;
    bool enableSampleAlphaToCoverage = false;
    bool applyRenderState = true;
    bool gammaCorrectColors = true;
    bool highlight = false;
    bool enableSceneMaterials = true;
    bool enableUsdDrawModes = true;
};

// TODO: Convert GfRange3d into a more generic implementation and add GfRect2i.
struct CameraFraming
{
    usdrt::GfRange2f displayWindow = { usdrt::GfVec2f{ FLT_MAX, FLT_MAX }, usdrt::GfVec2f{ -FLT_MAX, -FLT_MAX } };
    usdrt::GfRect2i dataWindow = { usdrt::GfVec2i{ 0, 0 }, usdrt::GfVec2i{ -1, -1 } };
    float pixelAspectRatio = 1.0f;
};

#define ISIMPLE_ENGINE_TYPE_ID "usdrt.hydra.ISimpleEngine"

OMNI_DECLARE_INTERFACE(ISimpleEngine);

class ISimpleEngine_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID(ISIMPLE_ENGINE_TYPE_ID)>
{
protected:
    virtual void create_abi(bool useUsdImaging,
                            OMNI_ATTR("out, not_null") usdrt::population::SceneStatistics* sceneStats) noexcept = 0;

    virtual OMNI_ATTR("not_prop") void setWindowPolicy_abi(CameraConformWindowPolicy policy) noexcept = 0;

    virtual void setCameraState_abi(OMNI_ATTR("in, not_null") const usdrt::GfMatrix4d* viewMatrix,
                                    OMNI_ATTR("in, not_null") const usdrt::GfMatrix4d* projectionMatrix) noexcept = 0;

    virtual OMNI_ATTR("not_prop") void setRenderViewport_abi(OMNI_ATTR("in, not_null")
                                                                 const usdrt::GfVec4d* viewport) noexcept = 0;

    virtual void setLightingState_abi(OMNI_ATTR("in, not_null, count=numLights") const SimpleLight* lights,
                                      uint32_t numLights,
                                      OMNI_ATTR("in, not_null") const SimpleMaterial* material,
                                      OMNI_ATTR("in, not_null") const usdrt::GfVec4f* sceneAmbient) noexcept = 0;

    virtual void render_abi(omni::fabric::UsdStageId usdStageId,
                            omni::fabric::PathC rootPathC,
                            OMNI_ATTR("in, not_null") const RenderParams* params,
                            OMNI_ATTR("in, not_null, count=numClipPlanes") const usdrt::GfVec4d* clipPlanes,
                            uint64_t numClipPlanes) noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool isConverged_abi() noexcept = 0;

    virtual void pauseRenderer_abi() noexcept = 0;

    virtual void resumeRenderer_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool isPauseRendererSupported_abi() noexcept = 0;

    virtual void stopRenderer_abi() noexcept = 0;

    virtual void restartRenderer_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool isStopRendererSupported_abi() noexcept = 0;

    virtual void clearSelected_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") void setSelectionColor_abi(OMNI_ATTR("in, not_null")
                                                                 const usdrt::GfVec4f* color) noexcept = 0;

    virtual OMNI_ATTR("not_prop") omni::core::ObjectPtr<usdrt::hydra::ISceneDelegate> getUsdrtDelegate_abi() noexcept = 0;

    virtual omni::fabric::PathC convertSdfPath_abi(OMNI_ATTR("c_str, not_null") const char* path) noexcept = 0;

    virtual OMNI_ATTR("c_str, not_null, not_prop") const char* getCurrentRendererId_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool setRendererPlugin_abi(OMNI_ATTR("c_str, not_null") const char* id) noexcept = 0;

    virtual OMNI_ATTR("not_prop") void setCameraPath_abi(omni::fabric::PathC cameraPathC) noexcept = 0;

    virtual void addSelected_abi(omni::fabric::PathC selectedPathC, int instanceIndex) noexcept = 0;

    virtual OMNI_ATTR("not_prop") void setRendererAov_abi(OMNI_ATTR("c_str, not_null") const char* aov) noexcept = 0;

    virtual void renderSimple_abi(omni::fabric::UsdStageId usdStageId, omni::fabric::PathC rootPathC) noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool isColorCorrectionCapable_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool isHydraEnabled_abi() noexcept = 0;

    virtual OMNI_ATTR("c_str, not_null, not_prop") const
        char* getRendererDisplayName_abi(OMNI_ATTR("c_str, not_null") const char* id) noexcept = 0;

    virtual OMNI_ATTR("not_prop, c_str, not_null") const char* getRendererPlugin_abi(uint32_t i) noexcept = 0;

    virtual OMNI_ATTR("not_prop") uint32_t getRendererPluginCount_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop, c_str, not_null") const char* getRendererAov_abi(uint32_t i) noexcept = 0;

    virtual OMNI_ATTR("not_prop") uint32_t getRendererAovCount_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") void setRenderBufferSize_abi(OMNI_ATTR("in, not_null")
                                                                   const usdrt::GfVec2i* size) noexcept = 0;

    virtual void OMNI_ATTR("not_prop")
        setFraming_abi(OMNI_ATTR("in, not_null") const CameraFraming* framing) noexcept = 0;

    virtual OMNI_ATTR("not_prop") void setOverrideWindowPolicy_abi(bool set,
                                                                   CameraConformWindowPolicy policy) noexcept = 0;

    virtual bool testIntersection_abi(OMNI_ATTR("in, not_null") const usdrt::GfMatrix4d* viewMatrix,
                                      OMNI_ATTR("in, not_null") const usdrt::GfMatrix4d* projectionMatrix,
                                      omni::fabric::UsdStageId usdStageId,
                                      omni::fabric::PathC rootPathC,
                                      OMNI_ATTR("in, not_null") const RenderParams* params,
                                      OMNI_ATTR("out, not_null") usdrt::GfVec3d* hitPoint,
                                      OMNI_ATTR("out, not_null") usdrt::GfVec3d* hitNormal,
                                      OMNI_ATTR("out, not_null") omni::fabric::PathC* hitPrimPath,
                                      OMNI_ATTR("out, not_null") omni::fabric::PathC* hitInstancerPath,
                                      OMNI_ATTR("out, not_null") int32_t* hitInstanceIndex,
                                      OMNI_ATTR("out, not_null") omni::fabric::PathC* topLevelPath,
                                      OMNI_ATTR("out, not_null") int32_t* topLevelInstanceIndex) noexcept = 0;

    virtual OMNI_ATTR("not_prop") void setSelected_abi(OMNI_ATTR("in, not_null, count=numSelected")
                                                           const omni::fabric::PathC* selected,
                                                       uint64_t numSelected) noexcept = 0;

    virtual OMNI_ATTR("c_str, not_null") const char* convertPathC_abi(omni::fabric::PathC pathC) noexcept = 0;

    virtual OMNI_ATTR("not_prop") int32_t getPxrVersion_abi() noexcept = 0;
};

} // namespace hydra
} // namespace usdrt

#include "ISimpleEngine.gen.h"
