// Copyright (c) 2021-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <OgnExtractCharacterPoseBundleDatabase.h>
#include "PrimCommon.h"

namespace
{

}

namespace omni
{
namespace anim
{
namespace graph
{

class OgnExtractCharacterPoseBundle
{
public:
    static bool compute(OgnExtractCharacterPoseBundleDatabase& db)
    {
        const auto& inputPoseBundle = db.inputs.pose();
        if(!inputPoseBundle.isValid())
            return false;

        // rootTranslation
        {
            const auto& rootTranslationAttr = inputPoseBundle.attributeByName(db.tokens.rootTranslation);
            const PXR_NS::GfVec3f* rootTranslationPtr = reinterpret_cast<const PXR_NS::GfVec3f*>(&rootTranslationAttr.get<float[3]>()[0]);
            if (rootTranslationPtr != nullptr)
            {
                auto& rootTranslation = db.outputs.rootTranslation();
                rootTranslation = *reinterpret_cast<const PXR_NS::GfVec3f*>(&rootTranslationAttr.get<float[3]>()[0]);
            }
        }

        // rootRotation
        {
            const auto& rootRotationAttr = inputPoseBundle.attributeByName(db.tokens.rootRotation);
            const PXR_NS::GfQuatf* rootRotationPtr = reinterpret_cast<const PXR_NS::GfQuatf*>(&rootRotationAttr.get<float[4]>()[0]);
            if (rootRotationPtr != nullptr)
            {
                auto& rootRotation = db.outputs.rootRotation();
                rootRotation = *reinterpret_cast<const PXR_NS::GfQuatf*>(&rootRotationAttr.get<float[4]>()[0]);
            }
        }

        // skeletonDeltaTranslation
        {
            const auto& skeletonDeltaTranslationAttr = inputPoseBundle.attributeByName(db.tokens.skeletonDeltaTranslation);
            const PXR_NS::GfVec3f* skeletonDeltaTranslationPtr = reinterpret_cast<const PXR_NS::GfVec3f*>(&skeletonDeltaTranslationAttr.get<float[3]>()[0]);
            if (skeletonDeltaTranslationPtr != nullptr)
            {
                auto& skeletonDeltaTranslation = db.outputs.skeletonDeltaTranslation();
                skeletonDeltaTranslation = *reinterpret_cast<const PXR_NS::GfVec3f*>(&skeletonDeltaTranslationAttr.get<float[3]>()[0]);
            }
        }

        // skeletonDeltaRotation
        {
            const auto& skeletonDeltaRotationAttr = inputPoseBundle.attributeByName(db.tokens.skeletonDeltaRotation);
            const PXR_NS::GfQuatf* skeletonDeltaRotationPtr = reinterpret_cast<const PXR_NS::GfQuatf*>(&skeletonDeltaRotationAttr.get<float[4]>()[0]);
            if (skeletonDeltaRotationPtr != nullptr)
            {
                auto& skeletonDeltaRotation = db.outputs.skeletonDeltaRotation();
                skeletonDeltaRotation = *reinterpret_cast<const PXR_NS::GfQuatf*>(&skeletonDeltaRotationAttr.get<float[4]>()[0]);
            }
        }

        // jointTranslations
        {
            const auto& jointTranslationsAttr = inputPoseBundle.attributeByName(db.tokens.jointTranslations);
            auto& jointTranslations = db.outputs.jointTranslations();
            if (jointTranslations.size() != jointTranslationsAttr.size())
            {
                jointTranslations.resize(jointTranslationsAttr.size());
            }
            const PXR_NS::GfVec3f* jointTranslationsPtr = reinterpret_cast<const PXR_NS::GfVec3f*>(&jointTranslationsAttr.get<float[][3]>()->data()[0][0]);
            if (jointTranslationsPtr != nullptr)
            {
                memcpy(jointTranslations.data(), jointTranslationsPtr, sizeof(PXR_NS::GfVec3f) * jointTranslationsAttr.size());
            }
        }

        // jointRotations
        {
            const auto& jointRotationsAttr = inputPoseBundle.attributeByName(db.tokens.jointRotations);
            auto& jointRotations = db.outputs.jointRotations();
            if (jointRotations.size() != jointRotationsAttr.size())
            {
                jointRotations.resize(jointRotationsAttr.size());
            }
            const PXR_NS::GfQuatf* jointRotationsPtr = reinterpret_cast<const PXR_NS::GfQuatf*>(&jointRotationsAttr.get<float[][4]>()->data()[0][0]);
            if (jointRotationsPtr != nullptr)
            {
                memcpy(jointRotations.data(), jointRotationsPtr, sizeof(PXR_NS::GfQuatf) * jointRotationsAttr.size());
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
}
}
}
