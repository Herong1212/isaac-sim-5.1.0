// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "OgnRpResourceExampleDeformerDatabase.h"

#include <carb/graphics/GraphicsTypes.h>
#include <carb/logging/Log.h>

#include <cuda/include/cuda_runtime_api.h>

#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/NodeTypeRegistrar.h>

#include <rtx/utils/GraphicsDescUtils.h>
#include <rtx/resourcemanager/ResourceManager.h>

#include <omni/kit/KitUtils.h>
#include <omni/kit/renderer/IRenderer.h>
#include <gpu/foundation/FoundationTypes.h>

#include <omni/math/linalg/vec.h>

#include <stdlib.h>
#include <iostream>

using omni::math::linalg::vec3f;

namespace omni
{
namespace graph
{
namespace core
{
namespace examples
{

extern "C" void modifyPositionsSinusoidal(const float3* pointsRest,
                                          float3* pointsDeformed,
                                          size_t numPoints,
                                          float time,
                                          float positionScale,
                                          float timeScale,
                                          float deformScale,
                                          bool verbose,
                                          cudaStream_t stream);

class OgnRpResourceExampleDeformer
{
public:
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        // std::cout << "OgnRpResourceExampleDeformer::initialize" << std::endl;
    }

    static void release(const NodeObj& nodeObj)
    {
        // std::cout << "OgnRpResourceExampleDeformer::release" << std::endl;
    }

    static bool compute(OgnRpResourceExampleDeformerDatabase& db)
    {
        CARB_PROFILE_ZONE(1, "OgnRpResourceExampleDeformer::compute");

        rtx::resourcemanager::Context* resourceManagerContext = nullptr;
        rtx::resourcemanager::ResourceManager* resourceManager = nullptr;

        const bool verbose = db.inputs.verbose();

        if (auto renderer = carb::getCachedInterface<omni::kit::renderer::IRenderer>())
        {
            if (auto gpuFoundation = renderer->getGpuFoundation())
            {
                resourceManager = gpuFoundation->getResourceManager();
                resourceManagerContext = gpuFoundation->getResourceManagerContext();
            }
        }

        cudaStream_t stream = (cudaStream_t)db.inputs.stream();

        if (verbose)
        {
            std::cout << "OgnRpResourceExampleDeformer::compute -- cudaStream: " << stream << std::endl;
        }

        if (!stream)
        {
            db.outputs.resourcePointerCollection().resize(0);
            db.outputs.pointCountCollection().resize(0);
            db.outputs.primPathCollection().resize(0);
            return false;
        }

        if (resourceManager == nullptr || resourceManagerContext == nullptr)
        {
            db.outputs.resourcePointerCollection().resize(0);
            db.outputs.pointCountCollection().resize(0);
            db.outputs.primPathCollection().resize(0);
            return false;
        }

        auto& resourcePointerCollection = db.inputs.resourcePointerCollection();
        auto& pointCountCollection = db.inputs.pointCountCollection();
        auto& primPathCollection = db.inputs.primPathCollection();

        const size_t primCount = primPathCollection.size();

        if (primCount == 0 || pointCountCollection.size() != primPathCollection.size() ||
            2 * pointCountCollection.size() != resourcePointerCollection.size())
        {
            db.outputs.resourcePointerCollection().resize(0);
            db.outputs.pointCountCollection().resize(0);
            db.outputs.primPathCollection().resize(0);
            return false;
        }

        auto& sequenceCounter = db.state.sequenceCounter();
        if (db.inputs.simTime() != 0)
        {
            sequenceCounter = db.inputs.simTime();
        }

        const uint32_t deviceIndex = 0;

        rtx::resourcemanager::RpResource** rpResources =
            (rtx::resourcemanager::RpResource**)resourcePointerCollection.data();
        const uint64_t* pointCounts = pointCountCollection.data();
        // const NameToken* primPaths = primPathCollection.data();

        for (size_t primIndex = 0; primIndex < primCount; primIndex++)
        {
            rtx::resourcemanager::RpResource* rpResourceRest = rpResources[2 * primIndex];
            rtx::resourcemanager::RpResource* rpResourceDeformed = rpResources[2 * primIndex + 1];
            const uint64_t& pointsCount = pointCounts[primIndex];
            // const NameToken& path = primPaths[primIndex];

            // run some simple kernel
            if (verbose)
            {
                std::cout << "OgnRpResourceExampleDeformer: Modifying " << pointsCount
                          << " positions at sequence point " << sequenceCounter << std::endl;
            }

            if (db.inputs.runDeformerKernel())
            {
                void* cudaPtrRest = resourceManager->getCudaDevicePointer(*rpResourceRest, deviceIndex);
                void* cudaPtrDeformed = resourceManager->getCudaDevicePointer(*rpResourceDeformed, deviceIndex);
                {
                    CARB_PROFILE_ZONE(1, "OgnRpResourceExampleDeformer::modifyPositions kernel");

                    modifyPositionsSinusoidal((float3*)cudaPtrRest, (float3*)cudaPtrDeformed, pointsCount,
                                              (float)sequenceCounter, db.inputs.positionScale(), db.inputs.timeScale(),
                                              db.inputs.deformScale(), verbose, stream);
                }
            }
        }
        if (db.inputs.runDeformerKernel() && db.inputs.simTime() == 0)
        {
            sequenceCounter += 1.0;
        }

        db.outputs.resourcePointerCollection.resize(resourcePointerCollection.size());
        memcpy(db.outputs.resourcePointerCollection().data(), resourcePointerCollection.data(),
               resourcePointerCollection.size() * sizeof(uint64_t));
        db.outputs.pointCountCollection.resize(pointCountCollection.size());
        memcpy(db.outputs.pointCountCollection().data(), pointCountCollection.data(),
               pointCountCollection.size() * sizeof(uint64_t));
        db.outputs.primPathCollection.resize(primPathCollection.size());
        memcpy(db.outputs.primPathCollection().data(), primPathCollection.data(),
               primPathCollection.size() * sizeof(NameToken));
        db.outputs.stream() = (uint64_t)stream;

        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
}
