// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnEventUpdateTickDatabase.h"

namespace omni
{
namespace graph
{
namespace core
{

class OgnEventUpdateTick
{
public:
    static bool compute(OgnEventUpdateTickDatabase& db)
    {
        // FIXME: temporary incomplete implementation.  Always output event id of 0 for now.
        // This is not useful of course, but does allow the event connection to trigger.
        // In time this should become a bundle, to incorporate information about the event
        // received.
        db.outputs.event() = 0;
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
