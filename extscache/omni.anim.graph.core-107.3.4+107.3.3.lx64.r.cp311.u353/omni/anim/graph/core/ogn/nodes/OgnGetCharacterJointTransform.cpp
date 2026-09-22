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

#include <OgnGetCharacterJointTransformDatabase.h>
#include <omni/timeline/ITimeline.h>
#include <ICharacter.h>
#include "PrimCommon.h"

namespace omni
{
namespace anim
{
namespace graph
{

class OgnGetCharacterJointTransform
{
public:
    static bool compute(OgnGetCharacterJointTransformDatabase& db)
    {
        auto timeline = omni::timeline::getTimeline(); // TODO: from context?
        if (!timeline->isPlaying())
        {
            return state::NotPlaying;
        }

        const char* skelRootPath = getSkeletonRootPath(db);
        if (!skelRootPath || strlen(skelRootPath) == 0)
        {
            return state::InvalidInput;
        }

        const char* jointToken = db.tokenToString(db.inputs.joint());
        if (!jointToken || strlen(jointToken) == 0)
        {
            return state::InvalidInput;
        }

        auto ag = carb::getCachedInterface<omni::anim::graph::ICharacter>();
        auto character = ag->getCharacter(skelRootPath);

        if (character == Invalid)
        {
            db.logWarning("Invalid character: '%s'", skelRootPath);
            return state::InvalidInput;
        }

        carb::Float3 jointTranslation;
        carb::Float4 jointRotation;

        bool result = ag->getJointTransform(character, jointToken, jointTranslation, jointRotation);
        if (!result)
        {
            db.logError("Unable to get character joint (%s) transform for '%s'.", jointToken, skelRootPath);
            return state::InvalidInput;
        }

        db.outputs.transform().SetTransform(GfQuatd(jointRotation.w, jointRotation.x, jointRotation.y, jointRotation.z),
                                            GfVec3d(jointTranslation.x, jointTranslation.y, jointTranslation.z));

        return true;
    }
};

REGISTER_OGN_NODE()
}
}
}
