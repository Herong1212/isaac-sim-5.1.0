// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "UsdPCH.h"
// clang-format on

#include <OgnFindPrimsDatabase.h>
#include <omni/fabric/FabricUSD.h>

#include "ReadPrimCommon.h"
#include "PrimCommon.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnFindPrims
{
    struct Listener
    {
        UsdStageChangeListenerRefPtr changeListener; // Lets us know when the USD stage changes
    };

public:
    // ----------------------------------------------------------------------------
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        auto& ls = OgnFindPrimsDatabase::sSharedState<Listener>(nodeObj);
        ls.changeListener = UsdStageChangeListener::New(context, UsdStageChangeListener::ListenMode::eResync);
    }

    // ----------------------------------------------------------------------------
    static void release(const NodeObj& nodeObj)
    {
        auto& ls = OgnFindPrimsDatabase::sSharedState<Listener>(nodeObj);
        ls.changeListener.Reset();
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnFindPrimsDatabase& db)
    {
        auto& ls = db.sharedState<Listener>();

        auto inputType = db.inputs.type();
        auto rootPrimPath = db.inputs.rootPrimPath();
        auto rootPrim = db.inputs.rootPrim();
        auto recursive = db.inputs.recursive();
        auto namePrefix = db.inputs.namePrefix();
        auto requiredAttributesStr = db.inputs.requiredAttributes();
        auto requiredRelationship = db.inputs.requiredRelationship();
        auto requiredRelationshipTargetStr = db.inputs.requiredRelationshipTarget();
        auto requiredTarget = db.inputs.requiredTarget();
        auto pathPattern = db.inputs.pathPattern();
        auto ignoreSystemPrims = db.inputs.ignoreSystemPrims();

        // We can skip compute if our state isn't dirty, and our inputs haven't changed
        if (not ls.changeListener->checkDirty())
        {
            if (db.state.inputType() == inputType && db.state.rootPrim().size() == rootPrim.size() &&
                (db.state.rootPrim().size() == 0 ? db.state.rootPrimPath() == rootPrimPath :
                                                   db.state.rootPrim()[0] == rootPrim[0]) &&
                db.state.recursive() == recursive && db.state.namePrefix() == namePrefix &&
                requiredAttributesStr == db.state.requiredAttributes() &&
                db.state.requiredRelationship() == requiredRelationship &&
                (db.state.requiredTarget.size() == 0 ?
                     requiredRelationshipTargetStr == db.state.requiredRelationshipTarget() :
                     db.state.requiredTarget()[0] == requiredTarget[0]) &&
                pathPattern == db.state.pathPattern() && ignoreSystemPrims == db.state.ignoreSystemPrims())
            {
                // Not dirty and inputs didn't change
                return true;
            }
        }

        db.state.inputType() = inputType;
        db.state.rootPrimPath() = rootPrimPath;
        db.state.rootPrim() = rootPrim;
        db.state.recursive() = recursive;
        db.state.namePrefix() = namePrefix;
        db.state.requiredAttributes() = requiredAttributesStr;
        db.state.requiredRelationship() = requiredRelationship;
        db.state.requiredRelationshipTarget() = requiredRelationshipTargetStr;
        db.state.requiredTarget() = requiredTarget;
        db.state.pathPattern() = pathPattern;
        db.state.ignoreSystemPrims() = ignoreSystemPrims;

        long stageId = db.abi_context().iContext->getStageId(db.abi_context());
        auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
        if (!stage)
        {
            db.logError("Could not find USD stage %ld", stageId);
            return false;
        }

        pxr::UsdPrim startPrim;
        if (rootPrim.size() == 0)
        {

            if (rootPrimPath == omni::fabric::kUninitializedToken)
                startPrim = stage->GetPseudoRoot();
            else
            {
                if (const char* primPathStr = db.tokenToString(rootPrimPath))
                {
                    startPrim = stage->GetPrimAtPath(pxr::SdfPath(primPathStr));
                    if (!startPrim)
                    {
                        db.logError("Could not find rootPrim \"%s\"", primPathStr);
                        return false;
                    }
                }
            }
        }
        else
        {
            if (rootPrim.size() > 1)
                db.logWarning("Only one rootPrim target is supported, the rest will be ignored");

            startPrim = stage->GetPrimAtPath(omni::fabric::toSdfPath(rootPrim[0]));
            if (!startPrim)
            {
                db.logError("Could not find rootPrim \"%s\"", db.pathToString(rootPrim[0]));
                return false;
            }
        }

        // Figure out the required type if any
        pxr::TfToken requiredTypeName;
        if (inputType != omni::fabric::kUninitializedToken)
        {
            if (char const* typeStr = db.tokenToString(inputType))
                requiredTypeName = pxr::TfToken(typeStr);
        }

        char const* requiredNamePrefix{ db.tokenToString(namePrefix) };

        // Figure out require relationship target if any
        pxr::SdfPath requiredRelationshipTarget;
        pxr::TfToken requiredRelName;
        if (requiredRelationship != omni::fabric::kUninitializedToken)
        {
            requiredRelName = pxr::TfToken(db.tokenToString(requiredRelationship));
            if (!requiredRelName.IsEmpty())
            {
                bool validTarget = (requiredTarget.size() == 0 && !requiredRelationshipTargetStr.empty());
                if (requiredTarget.size() == 0)
                {
                    if (!requiredRelationshipTargetStr.empty())
                        requiredRelationshipTarget = pxr::SdfPath{ requiredRelationshipTargetStr };
                }
                else
                {
                    if (requiredTarget.size() > 1)
                        db.logWarning("Only one requiredTarget is supported, the rest will be ignored");

                    requiredRelationshipTarget = omni::fabric::toSdfPath(requiredTarget[0]);
                }

                if (validTarget && !requiredRelationshipTarget.IsPrimPath())
                {
                    db.logError("Required relationship target \"%s\" is not valid", requiredRelationshipTarget.GetText());
                }
            }
        }

        // now find matching prims
        pxr::TfToken requiredAttribs{ std::string{ requiredAttributesStr.data(), requiredAttributesStr.size() } };
        VecOfPath matchedPaths;
        findPrims_findMatching(matchedPaths, startPrim, recursive, requiredNamePrefix, requiredTypeName,
                               requiredAttribs, requiredRelName, requiredRelationshipTarget,
                               omni::fabric::toTfToken(pathPattern), ignoreSystemPrims);

        // output PathC
        auto outputPrims = db.outputs.prims();
        outputPrims.resize(matchedPaths.size());
        std::transform(matchedPaths.begin(), matchedPaths.end(), outputPrims.begin(), [](auto path) { return path; });

        // convert PathC to TokenC
        auto outputPaths = db.outputs.primPaths();
        outputPaths.resize(matchedPaths.size());
        std::transform(matchedPaths.begin(), matchedPaths.end(), outputPaths.begin(),
                       [&db](auto path)
                       {
                           const char* pathStr = omni::fabric::toSdfPath(path).GetText();
                           return db.stringToToken(pathStr);
                       });

        return true;
    }

    static bool updateNodeVersion(GraphContextObj const& context, NodeObj const& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            if (oldVersion < 2)
            {
                // backward compatibility: `inputs:type`
                // Prior to this version `inputs:type` attribute did not support wild cards.
                // The meaning of an empty string was to include all types. With the introduction of the wild cards
                // we need to convert an empty string to "*" in order to include all types.
                static Token const value{ "*" };
                if (nodeObj.iNode->getAttributeExists(nodeObj, OgnFindPrimsAttributes::inputs::type.m_name))
                {
                    AttributeObj attr = nodeObj.iNode->getAttribute(nodeObj, OgnFindPrimsAttributes::inputs::type.m_name);
                    auto roHandle = attr.iAttribute->getAttributeDataHandle(attr, kAccordingToContextIndex);
                    Token const* roValue = getDataR<Token const>(context, roHandle);
                    if (roValue && roValue->getString().empty())
                    {
                        Token* rwValue = getDataW<Token>(
                            context, attr.iAttribute->getAttributeDataHandle(attr, kAccordingToContextIndex));
                        *rwValue = value;
                    }
                }
                else
                {
                    nodeObj.iNode->createAttribute(nodeObj, OgnFindPrimsAttributes::inputs::type.m_name,
                                                   Type(BaseDataType::eToken), &value, nullptr,
                                                   kAttributePortType_Input, kExtendedAttributeType_Regular, nullptr);
                }
                return true;
            }
        }
        return false;
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
