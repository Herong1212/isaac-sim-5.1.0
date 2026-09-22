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

#include <OgnGetCharacterWorldTransformDatabase.h>
#include <omni/timeline/ITimeline.h>
#include <ICharacter.h>
#include "PrimCommon.h"

namespace omni
{
namespace anim
{
namespace graph
{

class OgnGetCharacterWorldTransform
{
public:
    static bool compute(OgnGetCharacterWorldTransformDatabase& db)
    {
        auto timeline = omni::timeline::getTimeline(); // TODO: from context?
        if (timeline->isPlaying())
        {
            const char* skelRootPath = getSkeletonRootPath(db);
            if (skelRootPath && strlen(skelRootPath) > 0)
            {
                auto ag = carb::getCachedInterface<omni::anim::graph::ICharacter>();
                auto character = ag->getCharacter(skelRootPath);

                if (character == Invalid)
                {
                    db.logWarning("Invalid character: '%s'", skelRootPath);
                    return state::InvalidInput;
                }

                carb::Float3 translation;
                carb::Float4 rotation;

                bool result = ag->getWorldTransform(character, translation, rotation);
                if (result)
                {
                    db.outputs.transform().SetTransform(GfQuatd(rotation.w, rotation.x, rotation.y, rotation.z),
                                                        GfVec3d(translation.x, translation.y, translation.z));
                }
                else
                {
                    db.logError("Unable to get character world transform for '%s'.", skelRootPath);
                    return state::InvalidInput;
                }
            }
        }
        return true;
    }
};

REGISTER_OGN_NODE()
}
}
}
