// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnOnVariableChangeDatabase.h>
#include <omni/graph/action/IActionGraph.h>
#include <omni/graph/core/ogn/string.h>
#include "ActionNodeCommon.h"

namespace omni
{
namespace graph
{
namespace action
{

using namespace omni::graph::core;
using omni::graph::core::ogn::VariableAttribute;

// unnamed namespace to avoid multiple declaration when linking
namespace
{

bool compareAndCacheVariables(VariableAttribute& var, std::vector<uint8_t>& cachedVariable, Type& cachedType)
{
    if (!var.isValid())
        return true;

    RawPtr varValuePtr{ nullptr };
    size_t size{ 0 };
    if (cachedType.arrayDepth > 0)
    {
        // for arrays, raw data returns the pointer to the base address of the array and the size of the pointer
        var.rawData(varValuePtr, size);
        if (varValuePtr)
        {
            // var.size() is the number of elements.
            size = var.size() * var.type().baseTypeSize();
            varValuePtr = *reinterpret_cast<RawPtr*>(varValuePtr);
        }
    }
    else
    {
        var.rawData(varValuePtr, size);
    }

    if (!varValuePtr)
        size = 0;

    if ((cachedType != var.type()) || (size != cachedVariable.size()) ||
        (memcmp(cachedVariable.data(), varValuePtr, size) != 0))
    {
        cachedType = var.type();
        cachedVariable.resize(size);
        memcpy(cachedVariable.data(), varValuePtr, size);
        return false;
    }

    return true;
}
} // namespace


class OgnOnVariableChange
{
    std::vector<uint8_t> m_cachedVariable{};
    Type m_cachedType{};
    VariableAttribute var;

public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        AttributeObj attrObj = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::variableName.m_token);
        attrObj.iAttribute->registerValueChangedCallback(attrObj, onValueChanged, true);
    }

    // ----------------------------------------------------------------------------
    // Called by OG when the value of the variableName changes
    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        // Even if the graph is not instantiated (instCount == 0), we still have the "default" instance.
        // Using do-while to make sure at least the default instance is updated
        OgnOnVariableChangeDatabase db(attrObj.iAttribute->getNode(attrObj));
        int64_t instCount = (signed)db.getGraphTotalInstanceCount();
        do
        {
            auto& state = db.perInstanceState<OgnOnVariableChange>();
            state.m_cachedVariable.clear();
            state.m_cachedType = Type();
            state.var = VariableAttribute();
            db.moveToNextInstance();
        } while (--instCount > 0);
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnOnVariableChangeDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        auto& state = db.perInstanceState<OgnOnVariableChange>();
        if (!state.var.isValid())
            state.var = db.getVariable(db.inputs.variableName());

        auto& cachedVariable = state.m_cachedVariable;
        auto& cachedType = state.m_cachedType;

        bool isClean = (cachedVariable.size() != 0);
        bool isSame = compareAndCacheVariables(state.var, cachedVariable, cachedType);
        if (isClean && !isSame)
        {
            auto iActionGraph = getInterface();
            iActionGraph->setExecutionEnabled(outputs::changed.token(), db.getInstanceIndex());
        }

        return true;
    }
};


REGISTER_OGN_NODE()
} // action
} // graph
} // omni
