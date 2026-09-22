

// This code contains NVIDIA Confidential Information and is disclosed to you
// under a form of NVIDIA software license agreement provided separately to you.
//
// Notice
// NVIDIA Corporation and its licensors retain all intellectual property and
// proprietary rights in and to this software and related documentation and
// any modifications thereto. Any use, reproduction, disclosure, or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA Corporation is strictly prohibited.
//
// ALL NVIDIA DESIGN SPECIFICATIONS, CODE ARE PROVIDED "AS IS.". NVIDIA MAKES
// NO WARRANTIES, EXPRESSED, IMPLIED, STATUTORY, OR OTHERWISE WITH RESPECT TO
// THE MATERIALS, AND EXPRESSLY DISCLAIMS ALL IMPLIED WARRANTIES OF NONINFRINGEMENT,
// MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.
//
// Information and code furnished is believed to be accurate and reliable.
// However, NVIDIA Corporation assumes no responsibility for the consequences of use of such
// information or for any infringement of patents or other rights of third parties that may
// result from its use. No license is granted by implication or otherwise under any patent
// or patent rights of NVIDIA Corporation. Details are subject to change without notice.
// This code supersedes and replaces all information previously supplied.
// NVIDIA Corporation products are not authorized for use as critical
// components in life support devices or systems without express written approval of
// NVIDIA Corporation.
//
// Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include "../plugins/SceneQueryShared.h"
#include <string>
using namespace omni::physx;
using namespace omni::physx::graph;
using namespace omni::graph::core;

template <typename SceneQueryNodeType, typename SceneQueryDatabaseType>
class OgnPhysXSceneQuery
{
public:

    struct DeprecatedAttribute
    {   
        const NameToken attrName;
        const std::string strWarning;
        bool bConnected = false;
        DeprecatedAttribute(const NameToken& attrName, const std::string& strWarning) : attrName(attrName), strWarning(std::string(strWarning)) { };
    };

    std::vector<DeprecatedAttribute> deprecatedAttributes;

    static bool GetIsDeprecatedAttributeConnected(SceneQueryDatabaseType db, const NameToken& attrName)
    {
        auto& state = db.template sharedState<SceneQueryNodeType>();
        for(const DeprecatedAttribute& deprAttrib : state.deprecatedAttributes)
        {
            if(attrName == deprAttrib.attrName)
            {
                return deprAttrib.bConnected;
            }
        }
        return false;
    }

    static void SetAttributeDeprecated(const NodeObj& nodeObj, const NameToken& attrName, const char* strWarning)
    {
        SceneQueryDatabaseType db(nodeObj);
        auto& state = db.template sharedState<SceneQueryNodeType>();
        state.deprecatedAttributes.emplace_back(DeprecatedAttribute(attrName, strWarning));
    }

    static void onConnectionChanged(AttributeObj const& srcAttr, AttributeObj const& dstAttr, void* userData, bool bConnected)
    {
        NodeHandle nodeHandle = reinterpret_cast<NodeHandle>(userData);
        NodeObj nodeObj = srcAttr.iAttribute->getNode(srcAttr);

        // Check that this node is the connection source.
        if (nodeObj.nodeHandle != nodeHandle)
        {
            return;
        }

        SceneQueryDatabaseType db(nodeObj);
        auto& state = db.template sharedState<SceneQueryNodeType>();
        for(DeprecatedAttribute& deprecated : state.deprecatedAttributes)
        {
            const AttributeObj& attribute = nodeObj.iNode->getAttributeByToken(nodeObj, deprecated.attrName);
            if(attribute.attributeHandle == srcAttr.attributeHandle)
            {
                deprecated.bConnected = bConnected;
                if(bConnected) db.logWarning(deprecated.strWarning.c_str());
            }
        }
    }

    static void onConnected(AttributeObj const& srcAttr, AttributeObj const& dstAttr, void* userData)
    {
        onConnectionChanged(srcAttr, dstAttr, userData, true );
    }

    static void onDisconnected(AttributeObj const& srcAttr, AttributeObj const& dstAttr, void* userData)
    {
        onConnectionChanged(srcAttr, dstAttr, userData, false );
    }

    static void SetConnectionCallbacks(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        struct ConnectionCallback connectedCallback = {onConnected, (void*) nodeObj.nodeHandle};
        nodeObj.iNode->registerConnectedCallback(nodeObj, connectedCallback);
        struct ConnectionCallback disconnectedCallback = {onDisconnected, (void*) nodeObj.nodeHandle};
        nodeObj.iNode->registerDisconnectedCallback(nodeObj, disconnectedCallback);
    }

};