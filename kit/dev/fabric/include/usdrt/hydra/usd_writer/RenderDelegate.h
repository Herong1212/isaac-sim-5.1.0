// Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "api.h"

#include <pxr/base/tf/staticTokens.h>
#include <pxr/base/vt/array.h>
#include <pxr/imaging/hd/renderDelegate.h>
#include <pxr/imaging/hd/resourceRegistry.h>
#include <pxr/pxr.h>
#include <pxr/usd/usd/stage.h>

#include <unordered_map>

namespace usdrt
{
namespace hydra
{

PXR_NAMESPACE_USING_DIRECTIVE

class HdTestBasisCurves;
class HdTestInstancer;
class HdTestLight;
class HdTestMaterial;
class HdTestMesh;
class HdTestOpenvdbAsset;
class HdTestPoints;
class HdTestOmniSensor;
class HdTestVolume;
class HdTestCamera;
class HdTestOmniSound;
class HdTestNuRecVolume;
class HdTestNuRecFieldAsset;

CARB_IGNOREWARNING_MSC_PUSH
CARB_IGNOREWARNING_MSC(4275) // base class not dll-exported
CARB_IGNOREWARNING_MSC(4251) // statics of types not dll-exported

///
/// \class HdTestRenderDelegate
///
/// Render delegates provide renderer-specific functionality to the render
/// index, the main hydra state management structure. The render index uses
/// the render delegate to create and delete scene primitives, which include
/// geometry and also non-drawable objects. The render delegate is also
/// responsible for creating renderpasses, which know how to draw this
/// renderer's scene primitives.
///
class RENDERDELEGATE_API HdTestRenderDelegate final : public HdRenderDelegate
{
public:
    /// Render delegate constructor.
    HdTestRenderDelegate();
    /// Render delegate constructor.
    HdTestRenderDelegate(HdRenderSettingsMap const& settingsMap);
    /// Render delegate destructor.
    virtual ~HdTestRenderDelegate();

    /// Supported types
    const TfTokenVector& GetSupportedRprimTypes() const override;
    const TfTokenVector& GetSupportedSprimTypes() const override;
    const TfTokenVector& GetSupportedBprimTypes() const override;

    // Basic value to return from the RD
    HdResourceRegistrySharedPtr GetResourceRegistry() const override;

    // Prims
    HdRenderPassSharedPtr CreateRenderPass(HdRenderIndex* index, HdRprimCollection const& collection) override;

    HdInstancer* CreateInstancer(HdSceneDelegate* delegate, SdfPath const& id) override;

    void DestroyInstancer(HdInstancer* instancer) override;

    HdRprim* CreateRprim(TfToken const& typeId, SdfPath const& rprimId) override;

    void DestroyRprim(HdRprim* rPrim) override;

    HdSprim* CreateSprim(TfToken const& typeId, SdfPath const& sprimId) override;
    HdSprim* CreateFallbackSprim(TfToken const& typeId) override;
    void DestroySprim(HdSprim* sprim) override;

    HdBprim* CreateBprim(TfToken const& typeId, SdfPath const& bprimId) override;
    HdBprim* CreateFallbackBprim(TfToken const& typeId) override;
    void DestroyBprim(HdBprim* bprim) override;

    void CommitResources(HdChangeTracker* tracker) override;

    HdRenderParam* GetRenderParam() const override;

    /// Writes the hydra primitives to a USD file.
    ///
    ///   \param filename Path to the USD file.
    ///   \param override Whether or not to use overrides when writing the file.
    ///   \return True if writing was successful, false otherwise.
    bool SerializeToUsd(const std::string& filename);

    /// Saves all the stages
    void SaveAll();

    template <typename T>
    using PrimMap = std::unordered_map<SdfPath, T*, SdfPath::Hash>;

    void SetMaterialBindingPurpose(const TfToken& materialBindingPurpose);

    void SetMaterialRenderContexts(const TfTokenVector& materialRenderContexts);

    void SetShaderSourceTypes(const TfTokenVector& shaderSourceTypes);

    TfToken GetMaterialBindingPurpose() const override;

    TfTokenVector GetMaterialRenderContexts() const override;

    TfTokenVector GetShaderSourceTypes() const override;

    void SetWriteExtent(bool writeExtent);

private:
    static const TfTokenVector SUPPORTED_RPRIM_TYPES;
    static const TfTokenVector SUPPORTED_SPRIM_TYPES;
    static const TfTokenVector SUPPORTED_BPRIM_TYPES;

    void _Initialize();

    HdResourceRegistrySharedPtr _resourceRegistry;

    PrimMap<HdTestCamera> _cameras;
    PrimMap<HdTestBasisCurves> _curves;
    PrimMap<HdTestInstancer> _instancers;
    PrimMap<HdTestLight> _lights;
    PrimMap<HdTestMaterial> _materials;
    PrimMap<HdTestMesh> _meshes;
    PrimMap<HdTestOpenvdbAsset> _openvdbAssets;
    PrimMap<HdTestPoints> _points;
    PrimMap<HdTestOmniSensor> _sensors;
    PrimMap<HdTestVolume> _volumes;
    PrimMap<HdTestOmniSound> _omniSounds;
    PrimMap<HdTestNuRecVolume> _nuRecVolumes;
    PrimMap<HdTestNuRecFieldAsset> _nuRecFieldAssets;

    // This get cleared during SerializeToUsd
    std::unordered_set<SdfPath, SdfPath::Hash> _createdPaths;
    std::unordered_set<SdfPath, SdfPath::Hash> _destroyedPaths;

    std::vector<UsdStageRefPtr> _stages;

    TfToken _materialBindingPurpose;
    TfTokenVector _materialRenderContexts;
    TfTokenVector _shaderSourceTypes;

    bool _writeExtent = false;

    // This class does not support copying.
    HdTestRenderDelegate(const HdTestRenderDelegate&) = delete;

    HdTestRenderDelegate& operator=(const HdTestRenderDelegate&) = delete;
};

CARB_IGNOREWARNING_MSC_POP

}
}
