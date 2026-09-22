// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnConstructArrayDatabase.h>
#include <carb/logging/Log.h>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/StringUtils.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include "CoverageUtils.h"

#include <array>
#include <unordered_map>
#include <vector>

namespace omni
{
namespace graph
{
namespace nodes
{
// unnamed namespace to avoid multiple declaration when linking
namespace
{
static constexpr size_t kMaxAttrNameLen{ 32 };

void formatAttrName(size_t n, std::array<char, kMaxAttrNameLen>& outName)
{
    snprintf(outName.data(), kMaxAttrNameLen, "inputs:input%zu", n);
}

template <typename BaseType>
size_t tryComputeAssumingType(OgnConstructArrayDatabase& db, size_t count)
{
    NodeObj nodeObj = db.abi_node();
    auto iNode = nodeObj.iNode;
    GraphObj graphObj = iNode->getGraph(nodeObj);
    GraphContextObj context = graphObj.iGraph->getDefaultGraphContext(graphObj);

    for (size_t idx = 0; idx < count; ++idx)
    {
        auto outputArray = db.outputs.array(idx).template get<BaseType[]>();
        if (outputArray)
        {
            auto const arraySize = static_cast<size_t>(std::max(0, db.inputs.arraySize(idx)));
            (*outputArray).resize(arraySize);
            memset(outputArray->data(), 0, sizeof(BaseType) * arraySize);

            // read dynamic inputs
            size_t i = 0;
            std::array<char, kMaxAttrNameLen> outName;
            formatAttrName(i, outName);
            while (iNode->getAttributeExists(nodeObj, outName.data()) && i < arraySize)
            {
                auto inAttrib = iNode->getAttribute(nodeObj, outName.data());
                auto inputAttribType = inAttrib.iAttribute->getResolvedType(inAttrib);
                if (inputAttribType.baseType != BaseDataType::eUnknown)
                {
                    ConstAttributeDataHandle handle =
                        inAttrib.iAttribute->getConstAttributeDataHandle(inAttrib, db.getInstanceIndex() + idx);
                    auto const dataPtr = getDataR<BaseType>(context, handle);
                    if (dataPtr)
                        (*outputArray)[i] = *dataPtr;
                }
                ++i;
                formatAttrName(i, outName);
            }

            // fill the rest of the array using the last input value if necessary
            if (0 < i && i < arraySize)
            {
                for (size_t j = i; j < arraySize; ++j)
                {
                    (*outputArray)[j] = (*outputArray)[i - 1];
                }
            }
        }
    }
    return count;
}

template <typename BaseType, size_t TupleSize>
size_t tryComputeAssumingType(OgnConstructArrayDatabase& db, size_t count)
{
    NodeObj nodeObj = db.abi_node();
    auto iNode = nodeObj.iNode;
    GraphObj graphObj = iNode->getGraph(nodeObj);
    GraphContextObj context = graphObj.iGraph->getDefaultGraphContext(graphObj);

    for (size_t idx = 0; idx < count; ++idx)
    {
        auto outputArray = db.outputs.array(idx).template get<BaseType[][TupleSize]>();
        if (outputArray)
        {
            auto const arraySize = static_cast<size_t>(std::max(0, db.inputs.arraySize(idx)));
            (*outputArray).resize(arraySize);
            memset(outputArray->data(), 0, sizeof(BaseType) * arraySize * TupleSize);

            // read dynamic inputs
            size_t i = 0;
            std::array<char, kMaxAttrNameLen> outName;
            formatAttrName(i, outName);
            while (iNode->getAttributeExists(nodeObj, outName.data()) && i < arraySize)
            {
                auto inAttrib = iNode->getAttribute(nodeObj, outName.data());
                auto inputAttribType = inAttrib.iAttribute->getResolvedType(inAttrib);
                if (inputAttribType.baseType != BaseDataType::eUnknown)
                {
                    ConstAttributeDataHandle handle =
                        inAttrib.iAttribute->getConstAttributeDataHandle(inAttrib, db.getInstanceIndex() + idx);
                    auto const dataPtr = getDataR<BaseType[TupleSize]>(context, handle);
                    if (dataPtr)
                        memcpy(&((*outputArray)[i]), dataPtr, sizeof(BaseType) * TupleSize);
                }
                ++i;
                formatAttrName(i, outName);
            }

            // fill the rest of the array using the last input value if necessary
            if (0 < i && i < arraySize)
            {
                for (size_t j = i; j < arraySize; ++j)
                {
                    memcpy(&((*outputArray)[j]), &((*outputArray)[i - 1]), sizeof(BaseType) * TupleSize);
                }
            }
        }
    }
    return count;
}
} // namespace

class OgnConstructArray
{
    static void tryResolveAttribute(omni::graph::core::NodeObj const& nodeObj,
                                    omni::graph::core::AttributeObj attrib,
                                    omni::graph::core::Type attribType)
    {
        Type valueType{ attrib.iAttribute->getResolvedType(attrib) };
        bool attribIsValid = (attribType.baseType != BaseDataType::eUnknown);

        if (valueType.baseType != BaseDataType::eUnknown)
        {
            // Resolved
            // Case 1: We didn't find a valid source attribute => unresolve
            // Case 2: We found an attribute but it is not compatible with our current resolution => unresolve
            // Else: All good
            if (!attribIsValid or (attribType != valueType))
            {
                // Not compatible! Request that the attribute be un-resolved. Note that this could fail if there are
                // connections that result in a contradiction during type propagation
                attrib.iAttribute->setResolvedType(attrib, Type(BaseDataType::eUnknown));
            }
        }

        // If it's unresolved (and we have a valid attribute) we can request a resolution
        if (attribIsValid and (attrib.iAttribute->getResolvedType(attrib).baseType == BaseDataType::eUnknown))
        {
            attrib.iAttribute->setResolvedType(attrib, attribType);
        }
    }

    static void tryResolveArrayAttributes(omni::graph::core::NodeObj const& nodeObj, bool reconnectInputs)
    {
        auto& state = OgnConstructArrayDatabase::sSharedState<OgnConstructArray>(nodeObj);

        // Get the input attributes
        std::vector<AttributeObj> inputAttributes;
        size_t i = 0;
        std::array<char, kMaxAttrNameLen> outName;
        formatAttrName(i, outName);
        while (nodeObj.iNode->getAttributeExists(nodeObj, outName.data()))
        {
            inputAttributes.push_back(nodeObj.iNode->getAttribute(nodeObj, outName.data()));
            ++i;
            formatAttrName(i, outName);
        }

        // Determine the output array type from the specified array type and connected inputs
        Type outputType = state.m_inputArrayType; // Initialize to the specified array type ('eUnknown' if unspecified,
                                                  // i.e. 'inputs:arrayType' is set to 'auto')
        for (auto const& inAttrib : inputAttributes)
        {
            // Skip unconnected inputs
            size_t upstreamConnectionCount = inAttrib.iAttribute->getUpstreamConnectionCount(inAttrib);
            if (upstreamConnectionCount != 1)
                continue;

            // Get the type of the current input from the upstream connection
            ConnectionInfo upstreamConnection;
            inAttrib.iAttribute->getUpstreamConnectionsInfo(inAttrib, &upstreamConnection, 1);
            Type const upstreamType = upstreamConnection.attrObj.iAttribute->getResolvedType(upstreamConnection.attrObj);

            // The array type is not specified, so infer from the first connected and resolved input
            if (upstreamType.baseType != BaseDataType::eUnknown)
            {
                if (outputType.baseType == BaseDataType::eUnknown)
                {
                    outputType = upstreamType;
                }
                else
                {
                    // Check if the specified or inferred array type matches the type of the current input
                    if (!outputType.compatibleRawData(upstreamType))
                    {
                        OgnConstructArrayDatabase::logError(
                            nodeObj, "Mismatched array element type on input attribute '%s': expected '%s', got '%s'",
                            inAttrib.iAttribute->getName(inAttrib), getOgnTypeName(outputType).c_str(),
                            getOgnTypeName(upstreamType).c_str());
                        outputType = Type(BaseDataType::eUnknown);
                        break;
                    }
                }
            }
        }

        // Resolve inputs
        for (auto& inAttrib : inputAttributes)
        {
            size_t upstreamConnectionCount = inAttrib.iAttribute->getUpstreamConnectionCount(inAttrib);
            if (upstreamConnectionCount == 0)
            {
                // Resolve unconnected inputs to the specified array type, or the inferred array type if the array type
                // is unspecified
                if (state.m_inputArrayType.baseType != BaseDataType::eUnknown)
                {
                    if (inAttrib.iAttribute->getResolvedType(inAttrib) != state.m_inputArrayType)
                    {
                        // Case: The current input is disconnected and the array type is specified
                        // Action: Resolve the current input to the specified array type
                        tryResolveAttribute(nodeObj, inAttrib, state.m_inputArrayType);
                    }
                }
                else
                {
                    if (inAttrib.iAttribute->getResolvedType(inAttrib) != outputType)
                    {
                        // Case: The current input is disconnected and the array type is unspecified (auto)
                        // Action: Resolve the current input to the inferred array type if any input is connected.
                        //         If no inputs are connected, then outputType will be 'eUnknown', unresolving the
                        //         current input.
                        tryResolveAttribute(nodeObj, inAttrib, outputType);
                    }
                }
            }
            else if (upstreamConnectionCount == 1 && reconnectInputs) // reconnectInputs avoids an infinite loop
            {
                // Resolve connected inputs to the specified array type, or their upstream types if the array type is
                // unspecified
                if (state.m_inputArrayType.baseType != BaseDataType::eUnknown)
                {
                    // Check if already resolved to the specified array type
                    if (inAttrib.iAttribute->getResolvedType(inAttrib) != state.m_inputArrayType)
                    {
                        // Disconnect before re-resolving
                        ConnectionInfo upstreamConnection;
                        inAttrib.iAttribute->getUpstreamConnectionsInfo(inAttrib, &upstreamConnection, 1);
                        inAttrib.iAttribute->disconnectAttrs(upstreamConnection.attrObj, inAttrib, true);

                        // Case: The current input is connected and the array type is specified
                        // Action: Resolve the current input to the specified array type
                        tryResolveAttribute(nodeObj, inAttrib, state.m_inputArrayType);

                        // Reconnect
                        ConnectionInfo destConnection{ inAttrib, upstreamConnection.connectionType };
                        inAttrib.iAttribute->connectAttrsEx(upstreamConnection.attrObj, destConnection, true);
                    }
                }
                else
                {
                    ConnectionInfo upstreamConnection;
                    inAttrib.iAttribute->getUpstreamConnectionsInfo(inAttrib, &upstreamConnection, 1);
                    Type const upstreamType =
                        upstreamConnection.attrObj.iAttribute->getResolvedType(upstreamConnection.attrObj);
                    // Check if already resolved to the upstream type
                    if (inAttrib.iAttribute->getResolvedType(inAttrib) != upstreamType)
                    {
                        // Disconnect before re-resolving
                        inAttrib.iAttribute->disconnectAttrs(upstreamConnection.attrObj, inAttrib, true);

                        // Case: The current input is connected and the array type is unspecified (auto)
                        // Action: Resolve the current input to its upstream type (not the inferred array type
                        // 'outputType',
                        //         which could be a different but compatible type or 'eUnknown')
                        tryResolveAttribute(nodeObj, inAttrib, Type(BaseDataType::eUnknown)); // Must be resolved to
                                                                                              // 'eUnknown', not
                                                                                              // 'upstreamType'

                        // Reconnect
                        ConnectionInfo destConnection{ inAttrib, upstreamConnection.connectionType };
                        inAttrib.iAttribute->connectAttrsEx(upstreamConnection.attrObj, destConnection, true);
                    }
                }
            }
        }

        // Resolve the output
        // If there is a type mismatch (regardless of whether the array type was specified), then 'outputType' gets set
        // to 'eUnknown', so 'outputs:array' gets unresolved. If the array type is unspecified (auto) and no inputs are
        // connected (i.e. no type is inferred), then 'outputType' gets set to 'eUnknown' as well (but the node does not
        // error). Otherwise, 'outputs:array' gets resolved to the specified or inferred array type 'outputType'.
        outputType.arrayDepth = 1;
        auto outputArrayAttrib = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::array.token());
        tryResolveAttribute(nodeObj, outputArrayAttrib, outputType);
    }

    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        NodeObj nodeObj{ attrObj.iAttribute->getNode(attrObj) };
        FIREWALL_RETURN(nodeObj.nodeHandle == kInvalidNodeHandle); // LCOV_EXCL_LINE

        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        FIREWALL_RETURN(graphObj.graphHandle == kInvalidGraphHandle); // LCOV_EXCL_LINE

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        FIREWALL_RETURN(context.contextHandle == kInvalidGraphContextHandle); // LCOV_EXCL_LINE

        ConstAttributeDataHandle handle =
            attrObj.iAttribute->getConstAttributeDataHandle(attrObj, kAccordingToContextIndex);
        auto const dataPtr = getDataR<NameToken>(context, handle);
        if (dataPtr)
        {
            auto& state = OgnConstructArrayDatabase::sSharedState<OgnConstructArray>(nodeObj);
            state.m_inputArrayType = state.m_arrayTypes[*dataPtr];
        }

        tryResolveArrayAttributes(nodeObj, true);
    }

    static void onConnected(AttributeObj const& otherAttrib, AttributeObj const& inAttrib, void* userData)
    {
        NodeObj nodeObj{ inAttrib.iAttribute->getNode(inAttrib) };
        if (nodeObj.nodeHandle == kInvalidNodeHandle)
            return;

        NodeObj* thisNodeObj = reinterpret_cast<NodeObj*>(userData);
        if (nodeObj.nodeHandle != thisNodeObj->nodeHandle)
            return;

        auto& state = OgnConstructArrayDatabase::sSharedState<OgnConstructArray>(nodeObj);

        // Deregister onConnected callback to avoid infinite loop
        struct ConnectionCallback connectedCallback = { onConnected, &state.m_nodeObj };
        nodeObj.iNode->deregisterConnectedCallback(nodeObj, connectedCallback);

        tryResolveArrayAttributes(nodeObj, true);

        // Re-register onConnected callback
        nodeObj.iNode->registerConnectedCallback(nodeObj, connectedCallback);
    }

public:
    omni::graph::core::NodeObj m_nodeObj;

    std::unordered_map<NameToken, omni::graph::core::Type> m_arrayTypes;

    omni::graph::core::Type m_inputArrayType;

    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        auto& state = OgnConstructArrayDatabase::sSharedState<OgnConstructArray>(nodeObj);

        state.m_nodeObj = nodeObj;

        state.m_arrayTypes = {
            { OgnConstructArrayDatabase::tokens.Bool, Type(BaseDataType::eBool) },
            { OgnConstructArrayDatabase::tokens.Double, Type(BaseDataType::eDouble) },
            { OgnConstructArrayDatabase::tokens.Float, Type(BaseDataType::eFloat) },
            { OgnConstructArrayDatabase::tokens.Half, Type(BaseDataType::eHalf) },
            { OgnConstructArrayDatabase::tokens.Int, Type(BaseDataType::eInt) },
            { OgnConstructArrayDatabase::tokens.Int64, Type(BaseDataType::eInt64) },
            { OgnConstructArrayDatabase::tokens.Token, Type(BaseDataType::eToken) },
            { OgnConstructArrayDatabase::tokens.UChar, Type(BaseDataType::eUChar) },
            { OgnConstructArrayDatabase::tokens.UInt, Type(BaseDataType::eUInt) },
            { OgnConstructArrayDatabase::tokens.UInt64, Type(BaseDataType::eUInt64) },
            { OgnConstructArrayDatabase::tokens.Double_2, Type(BaseDataType::eDouble, 2) },
            { OgnConstructArrayDatabase::tokens.Double_3, Type(BaseDataType::eDouble, 3) },
            { OgnConstructArrayDatabase::tokens.Double_4, Type(BaseDataType::eDouble, 4) },
            { OgnConstructArrayDatabase::tokens.Matrix_2, Type(BaseDataType::eDouble, 4, 0, AttributeRole::eMatrix) },
            { OgnConstructArrayDatabase::tokens.Double_9, Type(BaseDataType::eDouble, 9, 0, AttributeRole::eMatrix) },
            { OgnConstructArrayDatabase::tokens.Double_16, Type(BaseDataType::eDouble, 16, 0, AttributeRole::eMatrix) },
            { OgnConstructArrayDatabase::tokens.Float_2, Type(BaseDataType::eFloat, 2) },
            { OgnConstructArrayDatabase::tokens.Float_3, Type(BaseDataType::eFloat, 3) },
            { OgnConstructArrayDatabase::tokens.Float_4, Type(BaseDataType::eFloat, 4) },
            { OgnConstructArrayDatabase::tokens.Half_2, Type(BaseDataType::eHalf, 2) },
            { OgnConstructArrayDatabase::tokens.Half_3, Type(BaseDataType::eHalf, 3) },
            { OgnConstructArrayDatabase::tokens.Half_4, Type(BaseDataType::eHalf, 4) },
            { OgnConstructArrayDatabase::tokens.Int_2, Type(BaseDataType::eInt, 2) },
            { OgnConstructArrayDatabase::tokens.Int_3, Type(BaseDataType::eInt, 3) },
            { OgnConstructArrayDatabase::tokens.Int_4, Type(BaseDataType::eInt, 4) },
            { OgnConstructArrayDatabase::tokens.Timecode, Type(BaseDataType::eDouble, 1, 0, AttributeRole::eTimeCode) },
            { OgnConstructArrayDatabase::tokens.Frame, Type(BaseDataType::eDouble, 16, 0, AttributeRole::eFrame) },
            { OgnConstructArrayDatabase::tokens.Colord_3, Type(BaseDataType::eDouble, 3, 0, AttributeRole::eColor) },
            { OgnConstructArrayDatabase::tokens.Colord_4, Type(BaseDataType::eDouble, 4, 0, AttributeRole::eColor) },
            { OgnConstructArrayDatabase::tokens.Colorf_3, Type(BaseDataType::eFloat, 3, 0, AttributeRole::eColor) },
            { OgnConstructArrayDatabase::tokens.Colorf_4, Type(BaseDataType::eFloat, 4, 0, AttributeRole::eColor) },
            { OgnConstructArrayDatabase::tokens.Colorh_3, Type(BaseDataType::eHalf, 3, 0, AttributeRole::eColor) },
            { OgnConstructArrayDatabase::tokens.Colorh_4, Type(BaseDataType::eHalf, 4, 0, AttributeRole::eColor) },
            { OgnConstructArrayDatabase::tokens.Normald, Type(BaseDataType::eDouble, 3, 0, AttributeRole::eNormal) },
            { OgnConstructArrayDatabase::tokens.Normalf, Type(BaseDataType::eFloat, 3, 0, AttributeRole::eNormal) },
            { OgnConstructArrayDatabase::tokens.Normalh, Type(BaseDataType::eHalf, 3, 0, AttributeRole::eNormal) },
            { OgnConstructArrayDatabase::tokens.Pointd, Type(BaseDataType::eDouble, 3, 0, AttributeRole::ePosition) },
            { OgnConstructArrayDatabase::tokens.Pointf, Type(BaseDataType::eFloat, 3, 0, AttributeRole::ePosition) },
            { OgnConstructArrayDatabase::tokens.Pointh, Type(BaseDataType::eHalf, 3, 0, AttributeRole::ePosition) },
            { OgnConstructArrayDatabase::tokens.Quatd, Type(BaseDataType::eDouble, 4, 0, AttributeRole::eQuaternion) },
            { OgnConstructArrayDatabase::tokens.Quatf, Type(BaseDataType::eFloat, 4, 0, AttributeRole::eQuaternion) },
            { OgnConstructArrayDatabase::tokens.Quath, Type(BaseDataType::eHalf, 4, 0, AttributeRole::eQuaternion) },
            { OgnConstructArrayDatabase::tokens.TexCoordd_2, Type(BaseDataType::eDouble, 2, 0, AttributeRole::eTexCoord) },
            { OgnConstructArrayDatabase::tokens.TexCoordd_3, Type(BaseDataType::eDouble, 3, 0, AttributeRole::eTexCoord) },
            { OgnConstructArrayDatabase::tokens.TexCoordf_2, Type(BaseDataType::eFloat, 2, 0, AttributeRole::eTexCoord) },
            { OgnConstructArrayDatabase::tokens.TexCoordf_3, Type(BaseDataType::eFloat, 3, 0, AttributeRole::eTexCoord) },
            { OgnConstructArrayDatabase::tokens.TexCoordh_2, Type(BaseDataType::eHalf, 2, 0, AttributeRole::eTexCoord) },
            { OgnConstructArrayDatabase::tokens.TexCoordh_3, Type(BaseDataType::eHalf, 3, 0, AttributeRole::eTexCoord) },
            { OgnConstructArrayDatabase::tokens.Vectord, Type(BaseDataType::eDouble, 3, 0, AttributeRole::eVector) },
            { OgnConstructArrayDatabase::tokens.Vectorf, Type(BaseDataType::eFloat, 3, 0, AttributeRole::eVector) },
            { OgnConstructArrayDatabase::tokens.Vectorh, Type(BaseDataType::eHalf, 3, 0, AttributeRole::eVector) }
        };

        AttributeObj arrayTypeAttrib = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::arrayType.m_token);
        arrayTypeAttrib.iAttribute->registerValueChangedCallback(arrayTypeAttrib, onValueChanged, true);

        struct ConnectionCallback connectedCallback = { onConnected, &state.m_nodeObj };
        nodeObj.iNode->registerConnectedCallback(nodeObj, connectedCallback);

        onValueChanged(arrayTypeAttrib, nullptr);
    }

    static size_t computeVectorized(OgnConstructArrayDatabase& db, size_t count)
    {
        try
        {
            auto const outputArrayType = db.outputs.array().type();
            switch (outputArrayType.baseType)
            {
            case BaseDataType::eBool:
                return tryComputeAssumingType<bool>(db, count);
            case BaseDataType::eDouble:
                switch (outputArrayType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<double>(db, count);
                case 2:
                    return tryComputeAssumingType<double, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<double, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<double, 4>(db, count);
                case 9:
                    return tryComputeAssumingType<double, 9>(db, count);
                case 16:
                    return tryComputeAssumingType<double, 16>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eFloat:
                switch (outputArrayType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<float>(db, count);
                case 2:
                    return tryComputeAssumingType<float, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<float, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<float, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (outputArrayType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<pxr::GfHalf>(db, count);
                case 2:
                    return tryComputeAssumingType<pxr::GfHalf, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<pxr::GfHalf, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<pxr::GfHalf, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt:
                switch (outputArrayType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<int32_t>(db, count);
                case 2:
                    return tryComputeAssumingType<int32_t, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<int32_t, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<int32_t, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t>(db, count);
            case BaseDataType::eToken:
                return tryComputeAssumingType<OgnToken>(db, count);
            case BaseDataType::eUChar:
                return tryComputeAssumingType<uint8_t>(db, count);
            case BaseDataType::eUInt:
                return tryComputeAssumingType<uint32_t>(db, count);
            case BaseDataType::eUInt64:
                return tryComputeAssumingType<uint64_t>(db, count);
            // LCOV_EXCL_START
            default:
                throw ogn::compute::InputError("Failed to resolve input types");
                // LCOV_EXCL_STOP
            }
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }

    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        tryResolveArrayAttributes(nodeObj, false);
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
