// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/extras/Hash.h>

#include <omni/core/IObject.h>
#include <omni/fabric/SimStageWithHistory.h>
#include <omni/utils/HashTypes.h>
#include <usdrt/gf/matrix.h>
#include <usdrt/gf/quat.h>
#include <usdrt/gf/range.h>
#include <usdrt/gf/vec.h>
#include <usdrt/scenegraph/interface/Common.h>
#include <usdrt/scenegraph/usd/usd/timeCode.h>

namespace usdrt
{
namespace population
{

struct SceneStatistics
{
    size_t numUsdMeshes = 0;
    size_t numUsdMaterials = 0;
    size_t numUsdCubes = 0;
    size_t numUsdCylinders = 0;
    size_t numUsdCapsules = 0;
    size_t numUsdInstances = 0;
    size_t numUsdSpheres = 0;
    size_t numUsdCones = 0;
    size_t numUsdCameras = 0;
    size_t numGeoInstanceProxies = 0;
    size_t numUniqueMaterials = 0;
    double usdTraversalTime = 0.;
    double fabricPopulationTime = 0.;
    double ujitsoProcessingTime = 0.;
    double resolverTime = 0.;
    double totalPopulationTime = 0.;
};

struct PrimvarAttributeDescription
{
    omni::fabric::TokenC name;
    omni::fabric::TokenC indicesName;
    omni::fabric::TokenC interpolationName;
    omni::fabric::TypeC type;
    bool isIndexed;
};

class IDerivedDataLookup;

OMNI_DECLARE_INTERFACE(IUtils);

class IUtils_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.population.IUtils")>
{
protected:
    // deprecated
    virtual void setXformValues_abi(const omni::fabric::StageReaderWriterId stageId,
                                    omni::fabric::PathC fcPath,
                                    OMNI_ATTR("in") const usdrt::GfVec3d* translation,
                                    OMNI_ATTR("in") const usdrt::GfQuatf* rotation,
                                    OMNI_ATTR("in") const usdrt::GfVec3f* scale,
                                    omni::fabric::TokenC visibility,
                                    bool worldVisibility) noexcept = 0;

    virtual void addCube_abi(const omni::fabric::StageReaderWriterId stageId,
                             omni::fabric::PathC fcPath,
                             OMNI_ATTR("in") const usdrt::GfVec3f* displayColor,
                             double size,
                             bool hasAnimatedXform,
                             OMNI_ATTR("in, count=numappliedSchemas") const omni::fabric::TokenC* appliedSchemas,
                             size_t numappliedSchemas,
                             omni::fabric::PathC materialId,
                             int refinementLevel,
                             int protoIndex,
                             OMNI_ATTR("in") const omni::fabric::PathC* instancerPath,
                             size_t numPrimvars,
                             OMNI_ATTR("in, count=numPrimvars") const PrimvarAttributeDescription* primvars) noexcept = 0;

    virtual void addSphere_abi(const omni::fabric::StageReaderWriterId stageId,
                               omni::fabric::PathC fcPath,
                               OMNI_ATTR("in") const usdrt::GfVec3f* displayColor,
                               double radius,
                               bool hasAnimatedXform,
                               OMNI_ATTR("in, count=numappliedSchemas") const omni::fabric::TokenC* appliedSchemas,
                               size_t numappliedSchemas,
                               omni::fabric::PathC materialId,
                               int refinementLevel,
                               int protoIndex,
                               OMNI_ATTR("in") const omni::fabric::PathC* instancerPath,
                               size_t numPrimvars,
                               OMNI_ATTR("in, count=numPrimvars") const PrimvarAttributeDescription* primvars) noexcept = 0;

    virtual void addCone_abi(const omni::fabric::StageReaderWriterId stageId,
                             omni::fabric::PathC fcPath,
                             OMNI_ATTR("in") const usdrt::GfVec3f* displayColor,
                             omni::fabric::TokenC fcAxis,
                             double height,
                             double radius,
                             bool hasAnimatedXform,
                             OMNI_ATTR("in, count=numappliedSchemas") const omni::fabric::TokenC* appliedSchemas,
                             size_t numappliedSchemas,
                             omni::fabric::PathC materialId,
                             int refinementLevel,
                             int protoIndex,
                             OMNI_ATTR("in") const omni::fabric::PathC* instancerPath,
                             size_t numPrimvars,
                             OMNI_ATTR("in, count=numPrimvars") const PrimvarAttributeDescription* primvars) noexcept = 0;

    virtual void addCylinder_abi(const omni::fabric::StageReaderWriterId stageId,
                                 omni::fabric::PathC fcPath,
                                 OMNI_ATTR("in") const usdrt::GfVec3f* displayColor,
                                 omni::fabric::TokenC fcAxis,
                                 double height,
                                 double radius,
                                 bool hasAnimatedXform,
                                 OMNI_ATTR("in, count=numappliedSchemas") const omni::fabric::TokenC* appliedSchemas,
                                 size_t numappliedSchemas,
                                 omni::fabric::PathC materialId,
                                 int refinementLevel,
                                 int protoIndex,
                                 OMNI_ATTR("in") const omni::fabric::PathC* instancerPath,
                                 size_t numPrimvars,
                                 OMNI_ATTR("in, count=numPrimvars") const PrimvarAttributeDescription* primvars) noexcept = 0;

    virtual void addCapsule_abi(const omni::fabric::StageReaderWriterId stageId,
                                omni::fabric::PathC fcPath,
                                OMNI_ATTR("in") const usdrt::GfVec3f* displayColor,
                                omni::fabric::TokenC fcAxis,
                                double height,
                                double radius,
                                bool hasAnimatedXform,
                                OMNI_ATTR("in, count=numappliedSchemas") const omni::fabric::TokenC* appliedSchemas,
                                size_t numappliedSchemas,
                                omni::fabric::PathC materialId,
                                int refinementLevel,
                                int protoIndex,
                                OMNI_ATTR("in") const omni::fabric::PathC* instancerPath,
                                size_t numPrimvars,
                                OMNI_ATTR("in, count=numPrimvars") const PrimvarAttributeDescription* primvars) noexcept = 0;

    virtual void addGeomInstance_abi(const omni::fabric::StageReaderWriterId stageId,
                                     omni::fabric::PathC fcPath,
                                     omni::fabric::TokenC primType,
                                     omni::fabric::PathC protoPath,
                                     int protoIndex,
                                     bool hasAnimatedXform,
                                     omni::fabric::PathC materialId,
                                     bool isInstanceRoot) noexcept = 0;

    virtual void addInstancer_abi(omni::fabric::StageReaderWriterId stageId,
                                  omni::fabric::PathC fcPath,
                                  bool hasAnimatedXform,
                                  OMNI_ATTR("in, count=numPrototypes") const omni::fabric::PathC* prototypes,
                                  size_t numPrototypes,
                                  OMNI_ATTR("in, count=numProtoIndices") const int* protoIndices,
                                  size_t numProtoIndices,
                                  OMNI_ATTR("in, count=numTranslations") const usdrt::GfVec3f* translations,
                                  size_t numTranslations,
                                  OMNI_ATTR("in, count=numOrientations") const usdrt::GfQuath* orientations,
                                  size_t numOrientations,
                                  OMNI_ATTR("in, count=numScales") const usdrt::GfVec3f* scales,
                                  size_t numScales,
                                  OMNI_ATTR("in, count=numappliedSchemas") const omni::fabric::TokenC* appliedSchemas,
                                  size_t numappliedSchemas,
                                  omni::fabric::PathC instancerPath,
                                  int protoIndex,
                                  size_t numPrimvars,
                                  OMNI_ATTR("in, count=numPrimvars") const PrimvarAttributeDescription* primvars) noexcept = 0;

    virtual void defineMeshWithSizes_abi(omni::fabric::StageReaderWriterId stageId,
                                         omni::fabric::PathC fcPath,
                                         size_t points,
                                         size_t faceVertexCounts,
                                         size_t faceVertexIndices,
                                         size_t subsets,
                                         size_t subsetIndices,
                                         bool isPrototype,
                                         size_t numPrimvars,
                                         OMNI_ATTR("in, count=numPrimvars")
                                            const PrimvarAttributeDescription* primvars,
                                         size_t timeVaryingAttributes,
                                         omni::fabric::TokenC subdivisionScheme,
                                         omni::fabric::TokenC interpolateBoundary,
                                         omni::fabric::TokenC faceVaryingLinearInterpolation,
                                         omni::fabric::TokenC triangleSubdivisionRule,
                                         size_t creaseIndices,
                                         size_t creaseLengths,
                                         size_t creaseSharpnesses,
                                         size_t cornerIndices,
                                         size_t cornerSharpnesses,
                                         bool hasAnimatedXform,
                                         OMNI_ATTR("in, count=numappliedSchemas")
                                             const omni::fabric::TokenC* appliedSchemas,
                                         size_t numappliedSchemas,
                                         bool hasMaterial,
                                         size_t holeIndices) noexcept = 0;

    virtual void populateXformAttributes_abi(omni::fabric::StageReaderWriterId stageId,
                                             omni::fabric::PathC fcPath,
                                             OMNI_ATTR("in") const usdrt::GfVec3d* translation,
                                             OMNI_ATTR("in") const usdrt::GfQuatf* rotation,
                                             OMNI_ATTR("in") const usdrt::GfVec3f* scale,
                                             OMNI_ATTR("in") const usdrt::GfRange3d* worldExtent,
                                             OMNI_ATTR("in, count=numappliedSchemas")
                                                 const omni::fabric::TokenC* appliedSchemas,
                                             size_t numappliedSchemas) noexcept = 0;

    virtual void populateFromUsd_abi(omni::fabric::StageReaderWriterId stageReaderWriterId,
                                     omni::fabric::UsdStageId usdStageId,
                                     omni::fabric::PathC primPathC,
                                     OMNI_ATTR("out") SceneStatistics* statistics,
                                     double time) noexcept = 0;

    virtual void populateFromUsd_abi(omni::fabric::StageReaderWriterId stageReaderWriterId,
                                     omni::fabric::UsdStageId usdStageId,
                                     OMNI_ATTR("in, count=numPrimPathCs") const omni::fabric::PathC* primPathCs,
                                     size_t numPrimPathCs,
                                     OMNI_ATTR("out") SceneStatistics* statistics,
                                     double time,
                                     bool diffMode = false) noexcept = 0;

    virtual void OMNI_ATTR("no_py")
        populateFromUsd_abi(omni::fabric::StageReaderWriterId stageReaderWriterId,
                            omni::fabric::UsdStageId usdStageId,
                            bool enableNotice,
                            OMNI_ATTR("in, count=numPrimPathCs") const omni::fabric::PathC* primPathCs,
                            size_t numPrimPathCs,
                            OMNI_ATTR("out") SceneStatistics* statistics,
                            double time,
                            bool diffMode = false,
                            bool sparseOnly = true) noexcept = 0;

    virtual bool getEnableUsdNoticeHandling_abi(omni::fabric::UsdStageId usdStageId) noexcept = 0;

    virtual void setEnableUsdNoticeHandling_abi(omni::fabric::UsdStageId usdStageId, omni::fabric::FabricId fabricId, const bool value) noexcept = 0;

    virtual void applyPendingUsdUpdates_abi(omni::fabric::UsdStageId usdStageId,
                                            omni::fabric::StageReaderWriterId stageReaderWriterId,
                                            double time) noexcept = 0;

    virtual void setExtent_abi(omni::fabric::StageReaderWriterId stageReaderWriterId,
                               omni::fabric::PathC fcPath,
                               OMNI_ATTR("in") const usdrt::GfRange3d* localExtent,
                               OMNI_ATTR("in") const usdrt::GfRange3d* worldExtent) noexcept = 0;

    virtual void setMaterialPurpose_abi(omni::fabric::FabricId fabricId,
                                        omni::fabric::TokenC materialPurposeC) noexcept = 0;

    virtual void setWorldXform_abi(const omni::fabric::StageReaderWriterId stageId,
                                   omni::fabric::PathC fcPath,
                                   OMNI_ATTR("in") const usdrt::GfMatrix4d* xform,
                                   omni::fabric::TokenC visibility,
                                   bool worldVisibility) noexcept = 0;

    virtual bool isPopulated_abi(omni::fabric::StageReaderWriterId stageReaderWriterId) noexcept = 0;

    virtual void detachMaterial_abi(omni::fabric::StageReaderWriterId stageReaderWriterId,
                                    omni::fabric::PathC primPathC) noexcept = 0;

    virtual omni::fabric::PathC acquireOrCreateRtPopulator_abi(
        const std::string& populatorIdentifier, omni::fabric::StageReaderWriterId stageReaderWriterId,
        omni::fabric::UsdStageId derivedDataStageId) noexcept = 0;

    virtual void releaseRtPopulator_abi(omni::fabric::PathC populatorPathC) noexcept = 0;

    virtual omni::fabric::PathC getRenderSettingsPrimPath_abi(omni::fabric::StageReaderWriterId stageReaderWriterId) noexcept = 0;

    virtual void OMNI_ATTR("no_py") getPopulationHash_abi(OMNI_ATTR("out") omni::hash128_t* outHash) noexcept = 0;

    virtual void synchronizeToFabric_abi(omni::fabric::UsdStageId usdStageId,
                                            omni::fabric::StageReaderWriterId stageReaderWriterId,
                                            usdrt::TimeChange timeChange,
                                            usdrt::UsdTimeCode time) noexcept = 0;
};

} // namespace population
} // namespace usdrt

#include "IUtils.gen.h"
