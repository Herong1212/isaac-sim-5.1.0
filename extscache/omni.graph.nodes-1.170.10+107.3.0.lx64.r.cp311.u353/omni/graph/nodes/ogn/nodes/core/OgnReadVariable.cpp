// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <OgnReadVariableDatabase.h>
#include <carb/events/EventsUtils.h>
#include "PrimCommon.h"
namespace omni
{
namespace graph
{
namespace core
{

class OgnReadVariable
{
public:
    carb::events::ISubscriptionPtr m_EventSubscription;

    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        AttributeObj attribObj = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::variableName.m_token);
        attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, true);
        onConnectionTypeResolve(nodeObj);
        GraphObj graphObj{ context.iContext->getGraph(context) };
        if (graphObj.graphHandle == kInvalidGraphHandle)
            return;


        OgnReadVariableDatabase::sSharedState<OgnReadVariable>(nodeObj).m_EventSubscription =
            carb::events::createSubscriptionToPop(graphObj.iGraph->getEventStream(graphObj).get(),
                                                  [nodeObj](carb::events::IEvent* e)
                                                  {
                                                      switch (static_cast<IGraphEvent>(e->type))
                                                      {
                                                      case IGraphEvent::eCreateVariable:
                                                      case IGraphEvent::eRemoveVariable:
                                                      case IGraphEvent::eVariableTypeChange:
                                                          onConnectionTypeResolve(nodeObj);
                                                          break;
                                                      default:
                                                          break;
                                                      }
                                                  });
    }

    // ----------------------------------------------------------------------------
    // Called by OG to resolve the output type
    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        onValueChanged(nodeObj.iNode->getAttributeByToken(nodeObj, inputs::variableName.m_token), nullptr);
    }

    // ----------------------------------------------------------------------------
    // Called by OG when the value of the variableName changes
    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        auto nodeObj = attrObj.iAttribute->getNode(attrObj);
        if (nodeObj.nodeHandle == kInvalidNodeHandle)
            return;

        auto graphObj = nodeObj.iNode->getGraph(nodeObj);
        if (graphObj.graphHandle == kInvalidGraphHandle)
            return;

        auto context = graphObj.iGraph->getDefaultGraphContext(graphObj);
        if (context.contextHandle == kInvalidGraphContextHandle)
            return;

        Type type(BaseDataType::eUnknown);
        const auto token = getDataR<NameToken>(
            context, attrObj.iAttribute->getConstAttributeDataHandle(attrObj, kAccordingToContextIndex));
        if (token)
        {
            auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
            auto variable = graphObj.iGraph->findVariable(graphObj, tokenInterface->getText(*token));
            if (variable)
            {
                type = variable->getType();
            }
        }
        omni::graph::nodes::tryResolveOutputAttribute(nodeObj, outputs::value.m_token, type);
    }

    static size_t computeVectorized(OgnReadVariableDatabase& db, size_t count)
    {
        auto variable = db.getVariable(db.inputs.variableName());
        if (!variable.isValid())
            return 0;

        auto& node = db.abi_node();

        // make sure the types match
        if (variable.type() != db.outputs.value().type())
        {
            auto attribute = node.iNode->getAttributeByToken(node, outputs::value.m_token);
            attribute.iAttribute->setResolvedType(attribute, variable.type());

            // if it failed to resolve properly, just return
            if (variable.type() != db.outputs.value().type())
                return 0;
        }

        // if the variable name is not a constant (ie. each instance may point to a different variable)
        // or the type is an array type (may have/trigger CoW or data stealing), we cannot do a vectorized compute,
        // and going through the ABI is mandatory on a per instance basis
        auto varNameAttrib = node.iNode->getAttributeByToken(node, inputs::variableName.m_token);
        bool const isVarNameConstant = varNameAttrib.iAttribute->isRuntimeConstant(varNameAttrib);
        if (variable.type().isArray() || !isVarNameConstant)
        {
            auto varName = db.inputs.variableName();
            for (size_t i = 0; i < count; ++i)
            {
                db.outputs.value().copyData(db.getVariable(varName));
                db.moveToNextInstance();
            }
        }
        else
        {
            uint8_t* dst = nullptr;
            size_t sd;
            db.outputs.value().rawData(dst, sd);

            uint8_t* src = nullptr;
            size_t ss;
            variable.rawData(src, ss);

            if (ss != sd)
                return 0;

            memcpy(dst, src, ss * count);
        }
        return count;
    }
};

REGISTER_OGN_NODE()

} // namespace examples
} // namespace graph
} // namespace omni
