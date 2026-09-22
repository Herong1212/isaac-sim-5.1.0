// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// This node implements the noise() function from Warp. Once Warp has been released
// it will be reimplemented using Warp.
//
// If you're interested in how to use the output from this node to drive a procedural
// noise texture, take a look at the core_definitions::perlin_noise_texture from the material library,
// documented here:
//
// https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_material-graph/nodes/Texturing_High_Level/perlin-noise.html
//
// Its MDL implementation can be found in the omni-core-materials repo, in mdl/nvidia/core_definitions.mdl
// That in turn calls base::perlin_noise_texture() which is implemented in the MDL-SDK repo, in
// src/shaders/mdl/base/base.mdl
//
#include <OgnNoiseDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>

#include "warp_noise.h"

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{

template <typename T, typename PXRTYPE>
bool getNoiseValues(uint32_t& rng_state,
                    const OgnNoiseAttributes::inputs::position_t& position,
                    ogn::array<float>& resultArray)
{
    if (auto positionArray = position.get<T>())
    {
        resultArray.resize(positionArray.size());

        size_t i = 0;
        for (auto pos : *positionArray)
        {
            resultArray[i++] = noise(rng_state, *(const PXRTYPE*)pos);
        }
        return true;
    }
    return false;
}

// Specialization for non-tuple type.
template <>
bool getNoiseValues<float[], float>(uint32_t& rng_state,
                                    const OgnNoiseAttributes::inputs::position_t& position,
                                    ogn::array<float>& resultArray)
{
    if (auto positionArray = position.get<float[]>())
    {
        resultArray.resize(positionArray.size());

        size_t i = 0;
        for (auto pos : *positionArray)
        {
            resultArray[i++] = noise(rng_state, pos);
        }
        return true;
    }
    return false;
}

}


class OgnNoise
{
public:
    static bool compute(OgnNoiseDatabase& db)
    {
        const auto& position = db.inputs.position();

        // If we don't have any positions to sample then there's nothing to do.
        if (!position.resolved())
            return true;

        auto& result = db.outputs.result();
        const auto& seed = db.inputs.seed();
        uint32_t rng_state = rand_init(seed);

        try
        {
            if (position.type().arrayDepth == 0)
            {
                if (auto resultScalar = result.get<float>())
                {
                    switch (position.type().componentCount)
                    {
                    case 1:
                    {
                        *resultScalar = noise(rng_state, *position.get<float>());
                        return true;
                    }

                    case 2:
                    {
                        *resultScalar = noise(rng_state, *(GfVec2f*)(*position.get<float[2]>()));
                        return true;
                    }

                    case 3:
                    {
                        *resultScalar = noise(rng_state, *(GfVec3f*)(*position.get<float[3]>()));
                        return true;
                    }
                    case 4:
                    {
                        *resultScalar = noise(rng_state, *(GfVec4f*)(*position.get<float[4]>()));
                        return true;
                    }

                    default:
                        db.logError("'position' has invalid tuple size of %i.", position.type().componentCount);
                    }
                }
                else
                {
                    throw ogn::compute::InputError("'result' is an array but 'position' is not");
                }
            }
            else if (auto resultArray = result.get<float[]>())
            {
                switch (position.type().componentCount)
                {
                case 1:
                {
                    if (getNoiseValues<float[], float>(rng_state, position, *resultArray))
                        return true;
                    throw ogn::compute::InputError("could not resolve 'position' to float[]");
                }

                case 2:
                {
                    if (getNoiseValues<float[][2], GfVec2f>(rng_state, position, *resultArray))
                        return true;
                    throw ogn::compute::InputError("could not resolve 'position' to float[2][]");
                }

                case 3:
                {
                    if (getNoiseValues<float[][3], GfVec3f>(rng_state, position, *resultArray))
                        return true;
                    throw ogn::compute::InputError("could not resolve 'position' to float[3][]");
                }
                case 4:
                {
                    if (getNoiseValues<float[][4], GfVec4f>(rng_state, position, *resultArray))
                        return true;
                    throw ogn::compute::InputError("could not resolve 'position' to float[4][]");
                }

                default:
                    db.logError("'position' has invalid tuple size of %i.", position.type().componentCount);
                }
            }
            else
            {
                throw ogn::compute::InputError("'position' is an array but 'result' is not");
            }
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return false;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto position = node.iNode->getAttributeByToken(node, inputs::position.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto positionType = position.iAttribute->getResolvedType(position);

        if (positionType.baseType != BaseDataType::eUnknown)
        {
            // 'result' is always float but has the same array depth as 'position'.
            Type type(BaseDataType::eFloat, 1, positionType.arrayDepth, AttributeRole::eNone);
            result.iAttribute->setResolvedType(result, type);
        }
        else
            result.iAttribute->setResolvedType(result, Type(BaseDataType::eUnknown));
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
// end-compute-helpers
