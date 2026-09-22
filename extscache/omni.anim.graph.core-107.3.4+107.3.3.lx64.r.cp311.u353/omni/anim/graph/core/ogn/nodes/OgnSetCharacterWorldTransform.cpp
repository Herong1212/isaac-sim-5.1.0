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

#include <OgnSetCharacterWorldTransformDatabase.h>
#include <omni/timeline/ITimeline.h>
#include <ICharacter.h>
#include "PrimCommon.h"

namespace omni
{
namespace anim
{
namespace graph
{

class OgnSetCharacterWorldTransform
{
public:
    static bool compute(OgnSetCharacterWorldTransformDatabase& db)
    {
        auto timeline = omni::timeline::getTimeline();  // TODO: from context?
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

                // ExtractRotationQuat expects the matrix to be orthonormal.
                GfMatrix4d gf_m = db.inputs.transform();
                gf_m.Orthonormalize();

                auto gf_q = GfQuatf(gf_m.ExtractRotationQuat());
                auto gf_i = gf_q.GetImaginary();
                auto q = carb::Float4{ gf_i[0], gf_i[1], gf_i[2], gf_q.GetReal() };

                auto gf_t = GfVec3f(gf_m.ExtractTranslation());
                auto t = carb::Float3{ gf_t[0], gf_t[1], gf_t[2] };

                ag->setWorldTransform(character, t, q);
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
