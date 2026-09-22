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

#include <OgnWriteVariableDatabase.h>
#include <carb/events/EventsUtils.h>
#include "PrimCommon.h"
#include "CoverageUtils.h"

namespace omni
{
namespace graph
{
namespace core
{

class OgnWriteVariable
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
        FIREWALL_RETURN(graphObj.graphHandle == kInvalidGraphHandle); // LCOV_EXCL_LINE

        OgnWriteVariableDatabase::sSharedState<OgnWriteVariable>(nodeObj).m_EventSubscription =
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
    // Called by OG to resolve the input type
    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        onValueChanged(nodeObj.iNode->getAttributeByToken(nodeObj, inputs::variableName.m_token), nullptr);
    }

    // ----------------------------------------------------------------------------
    // Called by OG when the value of the variableName changes
    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        auto nodeObj = attrObj.iAttribute->getNode(attrObj);
        FIREWALL_RETURN(nodeObj.nodeHandle == kInvalidNodeHandle); // LCOV_EXCL_LINE

        auto graphObj = nodeObj.iNode->getGraph(nodeObj);
        FIREWALL_RETURN(graphObj.graphHandle == kInvalidGraphHandle); // LCOV_EXCL_LINE

        auto context = graphObj.iGraph->getDefaultGraphContext(graphObj);
        FIREWALL_RETURN(context.contextHandle == kInvalidGraphContextHandle); // LCOV_EXCL_LINE

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

        omni::graph::nodes::tryResolveInputAttribute(nodeObj, inputs::value.m_token, type);
        omni::graph::nodes::tryResolveOutputAttribute(nodeObj, outputs::value.m_token, type);
    }

    static bool computeVectorized(OgnWriteVariableDatabase& db, size_t count)
    {
        auto variable = db.getVariable(db.inputs.variableName());
        FIREWALL_RETURN(!variable.isValid(), false); // LCOV_EXCL_LINE

        auto& node = db.abi_node();

        // FIREWALL - resolution should catch this beforehand
        if (!variable.type().compatibleRawData(db.outputs.value().type()))
        {
            /* LCOV_EXCL_START */
            db.logError("Variable %s with type %s is not compatible with type '%s', please disconnect",
                        db.tokenToString(db.inputs.variableName()), variable.type().getTypeName().c_str(),
                        db.outputs.value().typeName().c_str());

            return false;
            /* LCOV_EXCL_STOP */
        }
        if (variable.type().role != db.outputs.value().type().role)
        {
            if (variable.type().role != AttributeRole ::eNone && db.outputs.value().type().role != AttributeRole::eNone)
            {
                db.logWarning("Roles between variable %s (%s) and output (%s) differs",
                              db.tokenToString(db.inputs.variableName()),
                              getAttributeRoleName(variable.type().role).c_str(),
                              getAttributeRoleName(db.outputs.value().type().role).c_str());
            }
        }

        if (variable.type() != db.inputs.value().type())
        {
            auto attribute = db.abi_node().iNode->getAttributeByToken(node, inputs::value.m_token);
            attribute.iAttribute->setResolvedType(attribute, variable.type());
            return 0;
        }

        // and going through the ABI is mandatory on a per instance basis
        auto varNameAttrib = node.iNode->getAttributeByToken(node, inputs::variableName.m_token);
        bool const isVarNameConstant = varNameAttrib.iAttribute->isRuntimeConstant(varNameAttrib);
        if (variable.type().arrayDepth || !isVarNameConstant || !db.inputs.value.canVectorize())
        {
            auto varName = db.inputs.variableName();
            for (size_t i = 0; i < count; ++i)
            {
                variable = db.getVariable(varName, { i });
                variable.copyData(db.inputs.value(i));

                // forces an access to trigger CoW and have a real copy
                if (variable.type().arrayDepth)
                {
                    RawPtr ptr;
                    size_t s;
                    variable.rawData(ptr, s);
                }

                // copy from the input, so it's not an alias to the variable
                db.outputs.value(i).copyData(db.inputs.value(i));
            }
        }
        else
        {
            uint8_t* dst = nullptr;
            size_t sd;
            variable.rawData(dst, sd);

            uint8_t const* src = nullptr;
            size_t ss;
            db.inputs.value().rawData(src, ss);

            if (ss != sd)
                return 0;

            memcpy(dst, src, ss * count);

            db.outputs.value().rawData(dst, sd);
            if (ss != sd)
                return 0;

            memcpy(dst, src, ss * count);
        }

        auto execOut = db.outputs.execOut.vectorized(count);
        std::fill(execOut.begin(), execOut.end(), kExecutionAttributeStateEnabled);

        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace examples
} // namespace graph
} // namespace omni
