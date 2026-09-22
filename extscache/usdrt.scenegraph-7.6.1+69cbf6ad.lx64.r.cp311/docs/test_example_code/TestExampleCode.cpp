// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// clang-format off
#include "UsdPCH.h"
#include "../common/TestHelpers.h"
// clang-format on

#include "TestScenegraphCommon.h"

#include <cuda/include/cuda_runtime_api.h>
#include <omni/core/Omni.h>
#include <omni/core/OmniInit.h>
#include <omni/fabric/FabricUSD.h>
#include <omni/fabric/IFabric.h>
#include <omni/fabric/SimStageWithHistory.h>
#include <usdrt/scenegraph/base/gf/vec3f.h>
#include <usdrt/scenegraph/usd/sdf/types.h>
#include <usdrt/scenegraph/usd/usd/prim.h>
#include <usdrt/scenegraph/usd/usd/stage.h>
#include <usdrt/scenegraph/usd/usdGeom/tokens.h>
#include <usdrt/scenegraph/usd/usdShade/tokens.h>

//-----------------------------------------------------------------------------
// Get one prim examples
//-----------------------------------------------------------------------------
TEST_CASE("Example: Get one property with USDRT",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    usdrt::UsdStageRefPtr stage = usdrt::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));

    // Begin example one property RT

    using namespace usdrt;

    SdfPath path("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back");
    UsdPrim prim = stage->GetPrimAtPath(path);
    TfToken attrName = UsdGeomTokens->primvarsDisplayColor;
    UsdAttribute attr = prim.GetAttribute(attrName);

    // Get the value of displayColor on White_Wall_Back,
    // which is mid-gray on this stage
    VtArray<GfVec3f> result;
    attr.Get(&result);
    CHECK(result.size() == 1);
    CHECK(result[0] == GfVec3f(0.5, 0.5, 0.5));

    // Set the value of displayColor to red,
    // and verify the change by getting the value
    VtArray<GfVec3f> red = { GfVec3f(1, 0, 0) };
    attr.Set(red);
    attr.Get(&result);
    CHECK(result[0] == GfVec3f(1, 0, 0));

    // End example one property RT
}

TEST_CASE("Example: Get one property with USD",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    PXR_NS::UsdStageRefPtr stage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));

    // Begin example one property USD

    PXR_NAMESPACE_USING_DIRECTIVE;

    SdfPath path("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back");
    UsdPrim prim = stage->GetPrimAtPath(path);
    TfToken attrName = UsdGeomTokens->primvarsDisplayColor;
    UsdAttribute attr = prim.GetAttribute(attrName);

    // Get the value of displayColor on White_Wall_Back,
    // which is mid-gray on this stage
    VtArray<GfVec3f> result;
    attr.Get(&result);
    CHECK(result.size() == 1);
    CHECK(result[0] == GfVec3f(0.5, 0.5, 0.5));

    // Set the value of displayColor to red,
    // and verify the change by getting the value
    VtArray<GfVec3f> red = { GfVec3f(1, 0, 0) };
    attr.Set(red);
    attr.Get(&result);
    CHECK(result[0] == GfVec3f(1, 0, 0));

    // End example one property USD

    // purge the stage cache here
    // so the modified USD stage isn't picked up by subsequent tests
    UsdUtilsStageCache::Get().Clear();
}

TEST_CASE("Example: Get one property with Fabric",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    PXR_NS::UsdStageRefPtr stage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));
    PXR_NS::UsdStageCache& cache = PXR_NS::UsdUtilsStageCache::Get();
    cache.Insert(stage);

    // Use interface directly here and in other static methods
    // so that SWH may optionally persist after Stage object is destroyed
    auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    auto iSimStageWithHistory = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    omni::fabric::UsdStageId stageId = { static_cast<uint64_t>(cache.GetId(stage).ToLongInt()) };
    iSimStageWithHistory->getOrCreate(stageId, 1, { 1, 30 }, omni::fabric::GpuComputeType::eNone);
    omni::fabric::StageReaderWriterId stageReaderWriterId = iStageReaderWriter->create(stageId, 0);

    omni::fabric::StageReaderWriter stageReaderWriter(stageReaderWriterId);
    omni::fabric::Path primPathPrefetch("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back");
    iStageReaderWriter->prefetchPrim(stageId, primPathPrefetch);

    // Begin example one property Fabric

    using namespace omni::fabric;
    using namespace usdrt;

    const Path primPath("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back");
    const Token attrName("primvars:displayColor");

    // Get the value of displayColor on White_Wall_Back,
    // which is mid-gray on this stage
    // Note - the "Rd" API (getArrayAttributeRd) returns a span
    // of const items, which is therefor read-only
    // and Fabric does not track that a change was potentially made here
    gsl::span<const GfVec3f> displayColor = stageReaderWriter.getArrayAttributeRd<GfVec3f>(primPath, attrName);
    CHECK(displayColor.size() == 1);
    CHECK(displayColor[0] == GfVec3f(0.5, 0.5, 0.5));

    // Set the value of displayColor to red
    // Note - the "Wr" API (getArrayAttributeWr) returns a span
    // with non-const items, and this can be used to write
    // new values directly to Fabric. Using the "Wr" APIs
    // indicates to Fabric that a change may have been made to this
    // attribute, which Fabric will track
    gsl::span<GfVec3f> displayColorWr = stageReaderWriter.getArrayAttributeWr<GfVec3f>(primPath, attrName);
    displayColorWr[0] = GfVec3f(1, 0, 0);

    // Validate that displayColor was updated to red
    // using the previous read-only query
    CHECK(displayColor[0] == GfVec3f(1, 0, 0));

    // End example one property Fabric

    iSimStageWithHistory->release(stageId);
}

//-----------------------------------------------------------------------------
// Get many prims examples
//-----------------------------------------------------------------------------

TEST_CASE("Example: Get many prims with USDRT",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    usdrt::UsdStageRefPtr stage = usdrt::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));

    // Begin example many prims RT

    using namespace usdrt;

    std::vector<SdfPath> gPrimPaths = stage->GetPrimsWithTypeName(TfToken("UsdGeomGprim"));

    std::vector<SdfPath> sidedPrims;

    for (SdfPath gPrimPath : gPrimPaths)
    {
        UsdPrim prim = stage->GetPrimAtPath(gPrimPath);
        if (prim.HasAttribute(UsdGeomTokens->doubleSided))
        {
            sidedPrims.push_back(prim.GetPath());
        }
    }

    // End example many prims RT
}

TEST_CASE("Example: Get many prims with USD",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    PXR_NS::UsdStageRefPtr stage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));

    // Begin example many prims USD

    PXR_NAMESPACE_USING_DIRECTIVE;

    std::vector<SdfPath> sidedPrims;

    for (UsdPrim prim : stage->Traverse())
    {
        if (prim.HasAttribute(UsdGeomTokens->doubleSided))
        {
            sidedPrims.push_back(prim.GetPath());
        }
    }

    // End example many prims USD

    // purge the stage cache here
    // so the modified USD stage isn't picked up by subsequent tests
    UsdUtilsStageCache::Get().Clear();
}

TEST_CASE("Example: Get many prims with Fabric",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    PXR_NS::UsdStageRefPtr stage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));
    PXR_NS::UsdStageCache& cache = PXR_NS::UsdUtilsStageCache::Get();
    cache.Insert(stage);

    // Use interface directly here and in other static methods
    // so that SWH may optionally persist after Stage object is destroyed
    auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    auto iSimStageWithHistory = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    omni::fabric::UsdStageId stageId = { static_cast<uint64_t>(cache.GetId(stage).ToLongInt()) };
    iSimStageWithHistory->getOrCreate(stageId, 1, { 1, 30 }, omni::fabric::GpuComputeType::eNone);
    omni::fabric::StageReaderWriterId stageReaderWriterId = iStageReaderWriter->create(stageId, 0);

    omni::fabric::StageReaderWriter stageReaderWriter(stageReaderWriterId);

    omni::fabric::Path primPathPrefetch("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back");
    iStageReaderWriter->prefetchPrim(stageId, primPathPrefetch);

    // Begin example many prims Fabric

    using namespace omni::fabric;

    std::vector<Path> sidedPrims;

    AttrNameAndType doubleSided(Type(BaseDataType::eBool), Token("doubleSided"));
    PrimBucketList buckets = stageReaderWriter.findPrims({ doubleSided });

    for (size_t bucketId = 0; bucketId < buckets.bucketCount(); bucketId++)
    {
        auto pathArray = stageReaderWriter.getPathArray(buckets, bucketId);
        sidedPrims.insert(sidedPrims.end(), pathArray.begin(), pathArray.end());
    }

    // End example many prims Fabric

    iSimStageWithHistory->release(stageId);
}

//-----------------------------------------------------------------------------
// Update every Mesh examples
//-----------------------------------------------------------------------------
TEST_CASE("Example: Update every Mesh with USDRT",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    usdrt::UsdStageRefPtr stage = usdrt::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));

    // Begin example many prims and types RT

    using namespace usdrt;

    const TfToken mesh("Mesh");
    const TfToken attrName = UsdGeomTokens->primvarsDisplayColor;
    const VtArray<GfVec3f> red = { GfVec3f(1, 0, 0) };

    const SdfPathVector meshPaths = stage->GetPrimsWithTypeName(mesh);
    for (SdfPath meshPath : meshPaths)
    {
        UsdPrim prim = stage->GetPrimAtPath(meshPath);
        if (prim.HasAttribute(attrName))
        {
            prim.GetAttribute(attrName).Set(red);
        }
    }

    // End example many prims and types RT
}

TEST_CASE("Example: Update every Mesh with USD",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    PXR_NS::UsdStageRefPtr stage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));

    // Begin example many prims and types USD

    PXR_NAMESPACE_USING_DIRECTIVE;

    const TfToken mesh("Mesh");
    const TfToken attrName = UsdGeomTokens->primvarsDisplayColor;
    const VtArray<GfVec3f> red = { GfVec3f(1, 0, 0) };

    for (UsdPrim prim : stage->Traverse())
    {
        if (prim.GetTypeName() == mesh)
        {
            prim.GetAttribute(attrName).Set(red);
        }
    }

    // End example many prims and types USD

    // purge the stage cache here
    // so the modified USD stage isn't picked up by subsequent tests
    UsdUtilsStageCache::Get().Clear();
}

TEST_CASE("Example: Update every Mesh with Fabric vectorized",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    PXR_NS::UsdStageRefPtr stage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));
    PXR_NS::UsdStageCache& cache = PXR_NS::UsdUtilsStageCache::Get();
    cache.Insert(stage);

    // Use interface directly here and in other static methods
    // so that SWH may optionally persist after Stage object is destroyed
    auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    auto iSimStageWithHistory = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    omni::fabric::UsdStageId stageId = { static_cast<uint64_t>(cache.GetId(stage).ToLongInt()) };
    iSimStageWithHistory->getOrCreate(stageId, 1, { 1, 30 }, omni::fabric::GpuComputeType::eNone);
    omni::fabric::StageReaderWriterId stageReaderWriterId = iStageReaderWriter->create(stageId, 0);
    omni::fabric::StageReaderWriter stageReaderWriter(stageReaderWriterId);

    // Is there a better way to prefetch an entire stage?
    for (auto prim : stage->Traverse())
    {
        omni::fabric::Path primPathPrefetch(prim.GetPath().GetText());
        iStageReaderWriter->prefetchPrim(stageId, primPathPrefetch);
    }


    // Begin example many prims and types Fabric vectorized

    using namespace omni::fabric;
    using namespace usdrt;

    // Get every Mesh prim with a displayColor attribute in Fabric
    const Token displayColorName("primvars:displayColor");
    const GfVec3f red(1, 0, 0);
    AttrNameAndType displayColor(Type(BaseDataType::eBool), displayColorName);
    AttrNameAndType mesh(Type(BaseDataType::eTag, 1, 0, AttributeRole::ePrimTypeName), Token("Mesh"));
    PrimBucketList buckets = stageReaderWriter.findPrims({ displayColor, mesh });

    // Iterate over the buckets that match the query
    for (size_t bucketId = 0; bucketId < buckets.bucketCount(); bucketId++)
    {
        // Get the array of displayColor attributes from the bucket
        auto dcArray = stageReaderWriter.getArrayAttributeArrayWr<GfVec3f>(buckets, bucketId, displayColorName);
        for (gsl::span<GfVec3f> color : dcArray)
        {
            // Update the attribute to red
            color[0] = red;
        }
    }

    // End example many prims and types Fabric vectorized

    iSimStageWithHistory->release(stageId);
}

TEST_CASE("Example: Update every Mesh with Fabric",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    PXR_NS::UsdStageRefPtr stage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));
    PXR_NS::UsdStageCache& cache = PXR_NS::UsdUtilsStageCache::Get();
    cache.Insert(stage);

    // Use interface directly here and in other static methods
    // so that SWH may optionally persist after Stage object is destroyed
    auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    auto iSimStageWithHistory = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    omni::fabric::UsdStageId stageId = { static_cast<uint64_t>(cache.GetId(stage).ToLongInt()) };
    iSimStageWithHistory->getOrCreate(stageId, 1, { 1, 30 }, omni::fabric::GpuComputeType::eNone);
    omni::fabric::StageReaderWriterId stageReaderWriterId = iStageReaderWriter->create(stageId, 0);
    omni::fabric::StageReaderWriter stageReaderWriter(stageReaderWriterId);

    // Is there a better way to prefetch an entire stage?
    for (auto prim : stage->Traverse())
    {
        omni::fabric::Path primPathPrefetch(prim.GetPath().GetText());
        iStageReaderWriter->prefetchPrim(stageId, primPathPrefetch);
    }


    // Begin example many prims and types Fabric not vectorized

    using namespace omni::fabric;
    using namespace usdrt;

    // Get every Mesh prim with a displayColor attribute in Fabric
    const Token displayColorName("primvars:displayColor");
    const GfVec3f red(1, 0, 0);
    AttrNameAndType displayColor(Type(BaseDataType::eBool), displayColorName);
    AttrNameAndType mesh(Type(BaseDataType::eTag, 1, 0, AttributeRole::ePrimTypeName), Token("Mesh"));
    PrimBucketList buckets = stageReaderWriter.findPrims({ displayColor, mesh });

    // Iterate over the buckets that match the query
    for (size_t bucketId = 0; bucketId < buckets.bucketCount(); bucketId++)
    {
        auto primPaths = stageReaderWriter.getPathArray(buckets, bucketId);

        for (Path primPath : primPaths)
        {
            gsl::span<GfVec3f> displayColorWr =
                stageReaderWriter.getArrayAttributeWr<GfVec3f>(primPath, displayColorName);
            displayColorWr[0] = red;
        }
    }

    // End example many prims and types Fabric not vectorized

    iSimStageWithHistory->release(stageId);
}

//-----------------------------------------------------------------------------
// Relationship examples
//-----------------------------------------------------------------------------
TEST_CASE("Example: Get one relationship with USDRT",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    usdrt::UsdStageRefPtr stage = usdrt::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));

    // Begin example relationship RT

    using namespace usdrt;

    SdfPath path("/Cornell_Box/Root/Cornell_Box1_LP/Green_Wall/Green1SG");
    UsdPrim prim = stage->GetPrimAtPath(path);
    TfToken relName = UsdShadeTokens->materialBinding;
    UsdRelationship rel = prim.GetRelationship(relName);

    // The currently bound Material prim, and a new
    // Material prim to bind
    const SdfPath oldMtl("/Cornell_Box/Root/Looks/Green1SG");
    const SdfPath newMtl("/Cornell_Box/Root/Looks/Red1SG");

    // Get the first target
    CHECK(rel.HasAuthoredTargets());
    SdfPathVector targets;
    rel.GetTargets(&targets);
    CHECK(targets[0] == oldMtl);

    // Update the relationship to target
    // a different material
    SdfPathVector newTargets = { newMtl };
    rel.SetTargets(newTargets);
    SdfPathVector updatedTargets;
    rel.GetTargets(&updatedTargets);
    CHECK(updatedTargets[0] == newMtl);

    // End example relationship RT
}

TEST_CASE("Example: Get one relationship with USD",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    PXR_NS::UsdStageRefPtr stage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));

    // Begin example relationship USD

    PXR_NAMESPACE_USING_DIRECTIVE;

    SdfPath path("/Cornell_Box/Root/Cornell_Box1_LP/Green_Wall/Green1SG");
    UsdPrim prim = stage->GetPrimAtPath(path);
    TfToken relName = UsdShadeTokens->materialBinding;
    UsdRelationship rel = prim.GetRelationship(relName);

    // The currently bound Material prim, and a new
    // Material prim to bind
    const SdfPath oldMtl("/Cornell_Box/Root/Looks/Green1SG");
    const SdfPath newMtl("/Cornell_Box/Root/Looks/Red1SG");

    // Get the first target
    CHECK(rel.HasAuthoredTargets());
    SdfPathVector targets;
    rel.GetTargets(&targets);
    CHECK(targets[0] == oldMtl);

    // Update the relationship to target
    // a different material
    SdfPathVector newTargets = { newMtl };
    rel.SetTargets(newTargets);
    SdfPathVector updatedTargets;
    rel.GetTargets(&updatedTargets);
    CHECK(updatedTargets[0] == newMtl);

    // End example relationship USD

    // purge the stage cache here
    // so the modified USD stage isn't picked up by subsequent tests
    UsdUtilsStageCache::Get().Clear();
}

TEST_CASE("Example: Get one relationship with Fabric",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    PXR_NS::UsdStageRefPtr stage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    CHECK(bool(stage));
    PXR_NS::UsdStageCache& cache = PXR_NS::UsdUtilsStageCache::Get();
    cache.Insert(stage);

    // Use interface directly here and in other static methods
    // so that SWH may optionally persist after Stage object is destroyed
    auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    auto iSimStageWithHistory = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    omni::fabric::UsdStageId stageId = { static_cast<uint64_t>(cache.GetId(stage).ToLongInt()) };
    iSimStageWithHistory->getOrCreate(stageId, 1, { 1, 30 }, omni::fabric::GpuComputeType::eNone);
    omni::fabric::StageReaderWriterId stageReaderWriterId = iStageReaderWriter->create(stageId, 0);
    omni::fabric::StageReaderWriter stageReaderWriter(stageReaderWriterId);

    omni::fabric::Path primPathPrefetch("/Cornell_Box/Root/Cornell_Box1_LP/Green_Wall/Green1SG");
    iStageReaderWriter->prefetchPrim(stageId, primPathPrefetch);

    // Begin example relationship Fabric

    using namespace omni::fabric;
    using namespace usdrt;

    const Path primPath("/Cornell_Box/Root/Cornell_Box1_LP/Green_Wall/Green1SG");
    const Token relName("material:binding");

    const Path oldMtl("/Cornell_Box/Root/Looks/Green1SG");
    const Path newMtl("/Cornell_Box/Root/Looks/Red1SG");

    // Get the first target of material:binding
    // Note: getAttribute methods have a specialization for relationships
    // that will return the first target directly
    const Path* target = stageReaderWriter.getAttributeRd<Path>(primPath, relName);
    CHECK(*target == oldMtl);

    // Update the relationship to target
    // a different material
    Path* newTarget = stageReaderWriter.getAttributeWr<Path>(primPath, relName);
    *newTarget = newMtl;

    // Validate that target was updated
    CHECK(*target == newMtl);

    // End example relationship Fabric

    iSimStageWithHistory->release(stageId);
}

TEST_CASE("Example: USD / USDRT Interop",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=disabled]")
{
    ScenegraphTestFramework framework;

    // Begin example interop

    PXR_NS::UsdStageRefPtr usdStage = PXR_NS::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    // Get USD stage Id from global stage cache in UsdUtils
    PXR_NS::UsdStageCache::Id usdStageId = PXR_NS::UsdUtilsStageCache::Get().Insert(usdStage);

    // Get Fabric stage Id from USD stage Id
    omni::fabric::UsdStageId stageId(usdStageId.ToLongInt());

    // Create USDRT stage pointer using Attach w/ Fabric stage Id
    usdrt::UsdStageRefPtr stage = usdrt::UsdStage::Attach(stageId);

    usdrt::SdfPathVector meshPaths = stage->GetPrimsWithTypeName(usdrt::TfToken("Mesh"));

    for (const usdrt::SdfPath meshPath : meshPaths)
    {
        // Convert usdrt SdfPath to USD SdfPath
        const PXR_NS::SdfPath& usdMeshPath = omni::fabric::toSdfPath(omni::fabric::PathC(meshPath));

        // Now you can query the USD stage
        PXR_NS::UsdPrim usdPrim = usdStage->GetPrimAtPath(usdMeshPath);

        // ...and use APIs that are not represented in USDRT
        if (usdPrim.HasVariantSets())
        {
            std::cout << "Found Mesh with variantSet: " << usdMeshPath.GetString() << std::endl;
        }
    }

    // End example interop
}

//-----------------------------------------------------------------------------
// Fabric GPU example
//-----------------------------------------------------------------------------

TEST_CASE("Example: GPU Fabric",
          "[usdrt]"
          "[component=scenegraph][owner=ablevins][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    // Begin example GPU Fabric

    using namespace omni::fabric;
    using namespace usdrt;

    UsdStageRefPtr stage = UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));

    const Path primPath("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back");
    const Token attrName("points");

    // Get the points attribute value from USDRT
    VtArray<GfVec3f> usdrtPoints;
    UsdPrim mesh = stage->GetPrimAtPath(SdfPath(primPath));
    UsdAttribute attr = mesh.GetAttribute(TfToken(attrName));
    attr.Get(&usdrtPoints);

    // Nobody has accessed the GPU mirror for the points
    // attribute yet, so VtArray reports that there is no
    // Fabric GPU data available
    CHECK(!usdrtPoints.HasFabricGpuData());

    std::vector<GfVec3f> newPoints = { { 0, 0, 0 }, { 0, 1, 0 }, { 1, 1, 0 }, { 1, 0, 0 } };

    // Update the points on the GPU with Fabric APIs
    // Note - USDRT itself does not yet directly support
    // moving data to and from GPU, but this will be added
    // in a forthcoming release
    StageReaderWriter stageReaderWriter(stage->GetStageReaderWriterId());
    GfVec3f** points = stageReaderWriter.getAttributeWrGpu<GfVec3f*>(primPath, attrName);
    REQUIRE(points);
    REQUIRE(*points);
    cudaError_t err = cudaMemcpy(*points, newPoints.data(), newPoints.size() * sizeof(GfVec3f), cudaMemcpyHostToDevice);
    REQUIRE(err == cudaSuccess);

    // USDRT can query the attribute value again.
    // This time, HasFabricGpuData returns true, indicating
    // a GPU mirror for the attribute in Fabric
    attr.Get(&usdrtPoints);
    CHECK(usdrtPoints.HasFabricGpuData());

    // We can use cudaMemcpy to copy GPU data from Fabric
    // into memory on the host, in this case, a new vector,
    // using the GetGpuData method on VtArray
    std::vector<GfVec3f> verifyPoints(4);
    REQUIRE(usdrtPoints.GetGpuData());
    err = cudaMemcpy(
        verifyPoints.data(), usdrtPoints.GetGpuData(), verifyPoints.size() * sizeof(GfVec3f), cudaMemcpyDeviceToHost);
    REQUIRE(err == cudaSuccess);

    CHECK(verifyPoints[0] == GfVec3f(0, 0, 0));
    CHECK(verifyPoints[1] == GfVec3f(0, 1, 0));
    CHECK(verifyPoints[2] == GfVec3f(1, 1, 0));
    CHECK(verifyPoints[3] == GfVec3f(1, 0, 0));

    // End example GPU Fabric
}


//-----------------------------------------------------------------------------
// Prim selection examples
//-----------------------------------------------------------------------------

TEST_CASE("Example: Make prim selection by prim type",
          "[usdrt]"
          "[component=scenegraph][owner=rtonge][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    // Begin populate cornell.usda for examples
    // Load a USD stage and populate Fabric with it
    using namespace usdrt;
    UsdStageRefPtr stage = UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));

    for (UsdPrim prim : stage->Traverse())
    {
    } // Populate Fabric
    // End populate cornell.usda for examples

    // Begin example making a prim selection by prim type
    using namespace usdrt;
    RtPrimSelection selection = stage->SelectPrims({}, {}, TfToken("Mesh"), kDeviceCpu);
    std::cout << "Found " << selection.GetCount() << "meshes\n";
    // End example making a prim selection by prim type
}

TEST_CASE("Example: Make prim selection by prim type and applied schema",
          "[usdrt]"
          "[component=scenegraph][owner=rtonge][priority=mandatory]")
{
    ScenegraphTestFramework framework;

    // Load a USD stage and populate Fabric with it
    using namespace usdrt;
    UsdStageRefPtr stage = UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));

    for (UsdPrim prim : stage->Traverse())
    {
    } // Populate Fabric

    // Begin example making a prim selection by prim type and applied schema
    using namespace usdrt;
    std::vector<TfToken> requireAppliedSchemas = { "PhysicsRigidBodyAPI" };
    RtPrimSelection selection = stage->SelectPrims(requireAppliedSchemas, {}, TfToken("Mesh"), kDeviceCpu);
    std::cout << "Found " << selection.GetCount() << "physics meshes\n";
    // End example making a prim selection by prim type and applied schema
}

TEST_CASE("Example: Make a prim selection by prim type and attributes",
          "[usdrt]"
          "[component=scenegraph][owner=rtonge][priority=mandatory]")
{
    ScenegraphTestFramework framework;
    using namespace usdrt;

    // Load a USD stage and populate Fabric with it
    usdrt::UsdStageRefPtr stage = usdrt::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    for (usdrt::UsdPrim prim : stage->Traverse())
    {
    }

    // Begin example making a prim selection by prim type and attributes
    TfToken requireType = TfToken("Mesh");
    std::vector<AttrSpec> requireAttrs = { AttrSpec{ usdrt::SdfValueTypeNames->Color3fArray,
                                                     UsdGeomTokens->primvarsDisplayColor, AccessType::eReadWrite } };
    RtPrimSelection selection = stage->SelectPrims({}, requireAttrs, requireType, kDeviceCpu);
    std::cout << "Found " << selection.GetCount() << "meshes with displayColor\n";
    // End example making a prim selection by prim type and attributes
}

TEST_CASE("Example: Processing prims by iterating over the prim selection on CPU",
          "[usdrt]"
          "[component=scenegraph][owner=rtonge][priority=mandatory]")
{
    ScenegraphTestFramework framework;
    using namespace usdrt;

    // Load a USD stage and populate Fabric with it
    usdrt::UsdStageRefPtr stage = usdrt::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    for (usdrt::UsdPrim prim : stage->Traverse())
    {
    }

    // Begin example processing prims by iterating over the prim selection on CPU
    TfToken requireType = TfToken("Mesh");
    std::vector<AttrSpec> requireAttrs = { AttrSpec{ usdrt::SdfValueTypeNames->Color3fArray,
                                                     UsdGeomTokens->primvarsDisplayColor, AccessType::eReadWrite } };
    RtPrimSelection selection = stage->SelectPrims({}, requireAttrs, requireType, kDeviceCpu);

    AttributeRef colors = selection.GetRef(usdrt::SdfValueTypeNames->Color3fArray, UsdGeomTokens->primvarsDisplayColor);
    batch::ViewIterator iter(selection.GetBatchView());
    while (iter.advance())
    {
        iter.getArrayAttributeWr<GfVec3f>(colors).elements[0] = { 1.0f, 0.0f, 0.0f };
    }
    // End example processing prims by iterating over the prim selection on CPU

    // Check that it worked
    for (UsdPrim prim : stage->Traverse())
    {
        if (prim.GetTypeName() == TfToken("Mesh"))
        {
            TfToken attrName = UsdGeomTokens->primvarsDisplayColor;
            UsdAttribute attr = prim.GetAttribute(attrName);
            VtArray<GfVec3f> result;
            attr.Get(&result);
            REQUIRE(result.size() != 0);
            CHECK(result[0] == GfVec3f(1, 0, 0));
        }
    }
}

void changeColors(const usdrt::RtPrimSelection selection, omni::fabric::batch::AttributeRef positions);

TEST_CASE("Example: Processing prims by iterating over the prim selection on GPU",
          "[usdrt]"
          "[component=scenegraph][owner=rtonge][priority=mandatory]")
{
    ScenegraphTestFramework framework;
    using namespace usdrt;

    // Load a USD stage and populate Fabric with it
    usdrt::UsdStageRefPtr stage = usdrt::UsdStage::Open(framework.getUsdrtTestAssetPath("cornell.usda"));
    for (usdrt::UsdPrim prim : stage->Traverse())
    {
    }

    // Begin example processing prims by iterating over the prim selection on GPU
    TfToken requireType = TfToken("Mesh");
    std::vector<AttrSpec> requireAttrs = { AttrSpec{ usdrt::SdfValueTypeNames->Color3fArray,
                                                     UsdGeomTokens->primvarsDisplayColor, AccessType::eReadWrite } };
    RtPrimSelection selection = stage->SelectPrims({}, requireAttrs, requireType, kDeviceCuda0);

    AttributeRef colors = selection.GetRef(usdrt::SdfValueTypeNames->Color3fArray, UsdGeomTokens->primvarsDisplayColor);

    // Launch CUDA kernel
    changeColors(selection, colors);

    // End example processing prims by iterating over the prim selection on GPU

    // Check that it worked
    for (UsdPrim prim : stage->Traverse())
    {
        if (prim.GetTypeName() == TfToken("Mesh"))
        {
            TfToken attrName = UsdGeomTokens->primvarsDisplayColor;
            UsdAttribute attr = prim.GetAttribute(attrName);

            // We currently have to sync data to CPU manually, because
            // attr.get() gives us the data on the last device it was valid on,
            // which in this case is the GPU
            attr.SyncDataToCpu();

            VtArray<GfVec3f> result;
            attr.Get(&result);
            REQUIRE(result.size() != 0);
            CHECK(result[0] == GfVec3f(1, 0, 0));
        }
    }
}
