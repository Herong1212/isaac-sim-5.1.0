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

#include <OgnUpdateCharacterDatabase.h>
#include <omni/timeline/ITimeline.h>
#include <ICharacter.h>
#include "PrimCommon.h"

#include "CharacterManager.h"
#include "CharacterInstance.h"
#include <anim_core/math/transform.h>

extern uint32_t g_currentFrame;

namespace
{
    inline GfVec3f ConvertVector3(const SimdFloat4 v)
    {
        ::Float3 r(v);
        return GfVec3f{ r.x, r.y, r.z };
    }

    inline static GfQuatf ConvertQuaternion(const SimdFloat4 q)
    {
        ::Float4 r(q);
        return GfQuatf(r.w, r.x, r.y, r.z);
    }
}

namespace omni
{
namespace anim
{
namespace graph
{

class OgnUpdateCharacter
{
public:
    static bool compute(OgnUpdateCharacterDatabase& db)
    {
        auto timeline = omni::timeline::getTimeline();  // TODO: from context?
        if (!timeline->isPlaying())
        {
            return state::NotPlaying;
        }

        const char* skelRootPath = getSkeletonRootPath(db);
        if (!skelRootPath || strlen(skelRootPath) == 0)
        {
            return state::InvalidInput;
        }

        auto ag = carb::getCachedInterface<omni::anim::graph::ICharacter>();
        const auto characterHandle = ag->getCharacter(skelRootPath);

        const CharacterInstancePtr& character = CharacterManager::GetInstance()->GetCharacter(characterHandle);
        if (!character)
        {
            db.logWarning("Invalid character: '%s'", skelRootPath);
            return state::InvalidInput;
        }

        float deltaTime = db.inputs.deltaTime();
        const SimdTransform previousWorldTransform = character->GetWorldRootTransform();

        if (character->GetUpdateFrame() == g_currentFrame)
        {
            character->Update(deltaTime);
            character->MarkOGUpdate();
        }

        //const IGraphContext* const iContext = db.abi_context().iContext;
        const INode* const iNode = db.abi_node().iNode;
        auto& nodeObj = db.abi_node();
        omni::graph::core::AttributeObj outputPoseBundleAttr = iNode->getAttribute(nodeObj, "outputs_pose");
        bool writeToOutputPose = outputPoseBundleAttr.iAttribute->getDownstreamConnectionCount(outputPoseBundleAttr) > 0;

        if (writeToOutputPose)
        {
            auto& outputPoseBundle = db.outputs.pose();
            auto rootTranslationAttr =
                outputPoseBundle.addAttribute(
                    db.tokens.rootTranslation,
                        Type(BaseDataType::eFloat, 3, 0, AttributeRole::ePosition) );
            auto rootRotationAttr =
                outputPoseBundle.addAttribute(
                    db.tokens.rootRotation,
                        Type(BaseDataType::eFloat, 4, 0, AttributeRole::eQuaternion) );
            auto skeletonDeltaTranslationAttr =
                outputPoseBundle.addAttribute(
                    db.tokens.skeletonDeltaTranslation,
                        Type(BaseDataType::eFloat, 3, 0, AttributeRole::ePosition) );
            auto skeletonDeltaRotationAttr =
                outputPoseBundle.addAttribute(
                    db.tokens.skeletonDeltaRotation,
                        Type(BaseDataType::eFloat, 4, 0, AttributeRole::eQuaternion) );
              auto jointTranslationsAttr =
                outputPoseBundle.addAttribute(
                    db.tokens.jointTranslations,
                        Type(BaseDataType::eFloat, 3, 1, AttributeRole::ePosition) );
            auto jointRotationsAttr =
                outputPoseBundle.addAttribute(
                    db.tokens.jointRotations,
                        Type(BaseDataType::eFloat, 4, 1, AttributeRole::eQuaternion) );

            const CharacterInstance::transform_buffer* buffer = character->GetJointsTransformBuffer();
            if(buffer == nullptr)
                return state::InvalidInput;


            const SimdTransform& transform = character->GetWorldRootTransform();
            //rootTranslation
            {
                PXR_NS::GfVec3f* rootTranslation = reinterpret_cast<PXR_NS::GfVec3f*>(*rootTranslationAttr.get<float[3]>());
                *rootTranslation = ConvertVector3(transform.t);
            }
            //rootRotation
            {
                PXR_NS::GfQuatf* rootRotation = reinterpret_cast<PXR_NS::GfQuatf*>(*rootRotationAttr.get<float[4]>());
                *rootRotation = ConvertQuaternion(transform.q);
            }
            //skeletonDeltaTranslation
            {
                PXR_NS::GfVec3f deltaTranslation = ConvertVector3(transform::inverse_transform(previousWorldTransform, transform.t));

                PXR_NS::GfVec3f* skeletonDeltaTraslation = reinterpret_cast<PXR_NS::GfVec3f*>(*skeletonDeltaTranslationAttr.get<float[3]>());
                *skeletonDeltaTraslation = deltaTranslation;
            }
            //skeletonDeltaRotation
            {
                PXR_NS::GfQuatf deltaRotation = ConvertQuaternion(previousWorldTransform.q).GetConjugate() * ConvertQuaternion(transform.q);
                PXR_NS::GfQuatf* skeletonDeltaRotation = reinterpret_cast<PXR_NS::GfQuatf*>(*skeletonDeltaRotationAttr.get<float[4]>());
                *skeletonDeltaRotation = deltaRotation;
            }

            uint32_t jointsCount = buffer->size();
            if (jointsCount >= 0)
            {
                //jointTranslations
                {
                    auto jointTranslationsBuffer = jointTranslationsAttr.get<float[][3]>();
                    if (jointTranslationsAttr.size() != jointsCount)
                    {
                        jointTranslationsBuffer->resize(jointsCount);
                    }

                    PXR_NS::GfVec3f* jointTranslations = reinterpret_cast<PXR_NS::GfVec3f*>(jointTranslationsBuffer->data());
                    for (uint32_t i = 0; i < jointsCount; ++i)
                    {
                        (jointTranslations)[i] = ConvertVector3(buffer->get_position(i));
                    }
                }

                //jointRotations
                {
                    auto jointRotationsBuffer = jointRotationsAttr.get<float[][4]>();
                    if (jointRotationsAttr.size() != jointsCount)
                    {
                        jointRotationsBuffer.resize(jointsCount);
                    }

                    PXR_NS::GfQuatf* jointRotations = reinterpret_cast<PXR_NS::GfQuatf*>(jointRotationsBuffer->data());
                    for (uint32_t i = 0; i < jointsCount; ++i)
                    {
                        jointRotations[i] = ConvertQuaternion(buffer->get_rotation(i));
                    }
                }
            }
        }

        if(!writeToOutputPose || db.state.forceOutputToInherentSkelAnimation())
        {
            if (character->IsOGUpdate())
            {
                character->PushResults();
            }
        }

        db.outputs.execOut() = kExecutionAttributeStateEnabled;
        return true;

    }
};

REGISTER_OGN_NODE()
}
}
}
