// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// This file contains the definition of the INodeTypeForwarding ONI class
// This ABI is unstable and subject to change
/*  _    _  _____ ______         _______  __     ______  _    _ _____     ______          ___   _   _____  _____  _____ _  __ */
/* | |  | |/ ____|  ____|     /\|__   __| \ \   / / __ \| |  | |  __ \   / __ \ \        / / \ | | |  __ \|_   _|/ ____| |/ / */
/* | |  | | (___ | |__       /  \  | |     \ \_/ / |  | | |  | | |__) | | |  | \ \  /\  / /|  \| | | |__) | | | | (___ | ' /  */
/* | |  | |\___ \|  __|     / /\ \ | |      \   /| |  | | |  | |  _  /  | |  | |\ \/  \/ / | . ` | |  _  /  | |  \___ \|  <   */
/* | |__| |____) | |____   / ____ \| |       | | | |__| | |__| | | \ \  | |__| | \  /\  /  | |\  | | | \ \ _| |_ ____) | . \  */
/*  \____/|_____/|______| /_/    \_\_|       |_|  \____/ \____/|_|  \_\  \____/   \/  \/   |_| \_| |_|  \_\_____|_____/|_|\_| */

#include <omni/core/Omni.h>
#include <omni/core/IObject.h>
#ifndef INODE_TYPE_FORWARDING_STABLE
#pragma message("INodeTypeForwarding is out of date. Use omni/graph/core/INodeTypeForwarding2.h instead.")
#endif

namespace omni {
namespace graph {
namespace core {
namespace unstable {

OMNI_DECLARE_INTERFACE(INodeTypeForwarding);

/**
 * @brief Interface that creates a forward on a request for a node type to a different node type
 *
 * There are a couple of different common use cases for needing a forward:
 * - Node type gets renamed
 * - Node type moves from one extension to another
 *
 * The node type forward specifies the unique node type name so if extension omni.my.extension has a node whose type
 * is specified as "MyNode" then the forward must be from "omni.my.extension.MyNode".
 *
 * The forwarding is version-based as well, where the version is a minimum number required for forwarding, the usual
 * node version update mechanism not withstanding. For example, if you set up a forward from "omni.nodes.MyNode" version
 * 2 to "omni.my_nodes.MyNode" version 3 then any larger version number is forwarded to the same location:
 * - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
 * - omni.nodes.MyNode(3) -> omni.my_nodes.MyNode(3)
 * - omni.nodes.MyNode(4) -> omni.my_nodes.MyNode(3)
 *
 * The forwards can also have multiple versions forwarding to different locations, so if on top of the above forward
 * you also add a forward from "omni.nodes.MyNode" version 3 to "omni.new_nodes.MyNode" version 4 then these become
 * the example forward locations:
 * - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
 * - omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
 * - omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4)
 *
 * Version numbers lower than the first forward are left as-is
 * - omni.nodes.MyNode(1) -> omni.nodes.MyNode(1)
 *
 * @note The usual mechanism of calling updateVersionNumber on a node is only applied after a forward so in the above
 *       cases requesting omni.nodes.MyNode(2) does not call updateVersionNumber(1,2) on your omni.nodes.MyNode
 *       implementation.
 *
 * Node type forwards are associative, so if A forwards to B and B forwards to C then when you request A you get C.
 * Adding a new forward from omni.my_nodes.MyNode(3) to omni.new_nodes.MyNode(2) above yields this forwarding:
 * - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3) -> omni.new_nodes.MyNode(2)
 * - omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
 * - omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4)
 */
class INodeTypeForwarding_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.core.INodeTypeForwarding")>
{
protected:
    /**
     * @returns Number of currently defined forwards
     */
    virtual size_t getForwardCount_abi() noexcept = 0;

    /**
     * @brief Get the list of available forwards and their redirections.
     * Note that there is no guarantee that the replacement names are legitimate node type names, only that they
     * have been registered as replacements.
     *
     * The caller is responsible for allocating and destroying buffers large enough to hold "bufferSize" results.
     * If bufferSize > getForwardCount() then the entries at the ends of the buffers will be filled with nullptr.
     *
     * @param[out] forwardNameBuffer List of forward names to be replaced
     * @param[out] forwardVersionBuffer List of the first version of each forward name to be replaced
     * @param[out] replacementNameBuffer List of node type names that replace the forwarded names
     * @param[out] replacementVersionBuffer List of node type versions that replace the forwarded names
     * @param[out] extensionIdBuffer List of extension IDs corresponding to the replacement node type names.
     * @param[in] bufferSize Number of entries to fill in the buffers
     * @return true if the buffers were successfully filled and the bufferSize matched the forward count
     */
    OMNI_ATTR("no_py")
    virtual bool getForwards_abi(
        OMNI_ATTR("*c_str, out, not_null, count=bufferSize") char const** forwardNameBuffer,
        OMNI_ATTR("out, not_null, count=bufferSize") int* forwardVersionBuffer,
        OMNI_ATTR("*c_str, out, not_null, count=bufferSize") char const** replacementNameBuffer,
        OMNI_ATTR("out, not_null, count=bufferSize") int* replacementVersionBuffer,
        OMNI_ATTR("*c_str, out, not_null, count=bufferSize") char const** extensionIdBuffer,
        size_t bufferSize
    ) noexcept = 0;

    /**
     * @brief Define a new node type forward.
     * It is allowed to have the same forwardName to be defined more than once, however the "forwardVersion" must be
     * different from any existing ones. Later "forwardVersion" numbers will supersede earlier ones in this case.
     * For example if you have these two forwards set up:
     * - OldNode,1 -> BetterNode,1,omni.better.extension
     * - OldNode,2 -> MuchBetterNode,1,omni.much_better.extension
     *
     * then when version 1 of "OldNode" is requested it will treat it as if you requested "BetterNode", but when
     * versions 2 or later are requested it will instead treat it as if you requested "MuchBetterNode". These can be
     * chained together:
     * - OldNode,1 -> BetterNode,1,omni.better.extension
     * - BetterNode,1 -> MuchBetterNode,1,omni.much_better.extension
     *
     * @param[in] forwardName Name to be replaced
     * @param[in] forwardVersion The first version of the forward name to be replaced
     * @param[in] replacementName Node type name that replaces the forwarded name
     * @param[in] replacementVersion Version of the node type that replaces the forwarded name
     * @param[in] extensionId Extension ID in which the replacement node type can be found
     * @return false if there was already an forward with the given name and initial version number
     */
    virtual bool defineForward_abi(
        OMNI_ATTR("c_str, in, not_null") char const* forwardName,
        int forwardVersion,
        OMNI_ATTR("c_str, in, not_null") char const* replacementName,
        int replacementVersion,
        OMNI_ATTR("c_str, in, not_null") char const* replacementExtensionId
    ) noexcept = 0;

    /**
     * @brief Remove an existing node type forward.
     * Since an forwardName + forwardVersion combination is unique there is no need to pass in the replacement information.
     * Only the forward with the matching version is removed. Any others with the same name remain untouched.
     *
     * @param[in] forwardName Forward to be removed
     * @param[in] forwardVersion The version at which the forward is to be removed
     * @return false if there was already an forward with the given name and initial version number
     */
    virtual bool removeForward_abi(
        OMNI_ATTR("c_str, in, not_null") char const* forwardName,
        int forwardVersion
    ) noexcept = 0;

    /**
     * @brief Remove forwards referencing a given node type name.
     *
     * @param[in] referencedName Forward to be removed
     * @param[in] referencedVersion The version at which the forward is to be removed
     * @return number of forwards to the given type that were removed
     */
    virtual size_t removeForwardedType_abi(
        OMNI_ATTR("c_str, in, not_null") char const* referencedName,
        int referencedVersion
    ) noexcept = 0;

    /**
     * @brief Find a node type name replacement corresponding to the given node type forward name and version
     *
     * @param[in] forwardName Name of the node type forward to look up
     * @param[in] forwardVersion Version number of the node type forward being looked up
     * @param[out] nodeTypeName Pointer to the name of the actual node type name corresponding to the forward,
     *                          or nullptr if there is no equivalent. This string is a constant and managed
     *                          by the node type forward system so it should not be stored on a long-term basis.
     * @param[out] nodeTypeVersion Pointer to the version of the actual node type name corresponding to the forward
     * @param[out] nodeTypeExtension Pointer to the name of the extension owning nodeTypeName
     * @return true if the forwardName/forwardVersion found a valid mapping, with the result placed in the return parameters
     */
    OMNI_ATTR("no_py")
    virtual bool findForward_abi(
        OMNI_ATTR("c_str, in, not_null") char const* forwardName,
        int forwardVersion,
        OMNI_ATTR("*c_str, out, not_null, count=1") char const** nodeTypeName,
        OMNI_ATTR("out, count=1") int* nodeTypeVersion,
        OMNI_ATTR("*c_str, out, not_null, count=1") char const** nodeTypeExtension
    ) noexcept = 0;
};

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni

#include "INodeTypeForwarding.gen.h"
