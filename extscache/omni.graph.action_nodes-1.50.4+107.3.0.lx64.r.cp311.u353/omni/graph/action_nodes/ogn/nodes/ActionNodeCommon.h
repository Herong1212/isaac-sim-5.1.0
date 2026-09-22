// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

namespace omni
{
namespace graph
{
namespace action
{

/**
 * Checks if the node with `inputs:onlyPlayback` should be disabled, because playback is not happening.
 *
 * @param[in] db The node OGN Database object
 * @return true if the node should be disabled
 */
template <typename NodeDb>
bool checkNodeDisabledForOnlyPlay(NodeDb const& db)
{
    return db.inputs.onlyPlayback() && (not db.abi_context().iContext->getIsPlaying(db.abi_context()));
}

}
}
}
