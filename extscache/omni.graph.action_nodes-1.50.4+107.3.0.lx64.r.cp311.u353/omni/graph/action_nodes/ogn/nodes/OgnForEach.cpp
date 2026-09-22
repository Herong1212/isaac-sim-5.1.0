// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnForEachDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnForEach
{
public:
    size_t m_arrayIndex{ 0 };

    static bool compute(OgnForEachDatabase& db)
    {
        auto iActionGraph = getInterface();
        auto const& arrayIn = db.inputs.arrayIn();
        size_t const arrayLen = arrayIn.size();

        auto& state = db.perInstanceState<OgnForEach>();

        if (iActionGraph->getExecutionEnabled(inputs::execIn.token(), db.getInstanceIndex()))
            state.m_arrayIndex = 0;

        if (state.m_arrayIndex >= arrayLen)
        {
            iActionGraph->setExecutionEnabled(outputs::finished.token(), db.getInstanceIndex());
            state.m_arrayIndex = 0;
            return true;
        }

        size_t currentIndex = state.m_arrayIndex++;

        iActionGraph->setExecutionEnabledAndPushed(outputs::loopBody.token(), db.getInstanceIndex());
        db.outputs.arrayIndex() = static_cast<int>(currentIndex);

        ConstRawPtr arrayAttribPtr{ nullptr };
        size_t arraySize{ 0 };
        arrayIn.rawData(arrayAttribPtr, arraySize);

        // arrayAttribPtr is a pointer to the attribute data, the data being an array of something,
        // so we need to deref that pointer to get the pointer to the actual data.
        ConstRawPtr arrayData = *(ConstRawPtr*)arrayAttribPtr;

        auto& element = db.outputs.element();

        // Ensure output attribute is writable
        void* out{ nullptr };
        void** outPtr = (void**)(&out);
        auto hdl = element.abi_handle();
        db.abi_context().iAttributeData->getDataW(outPtr, db.abi_context(), &hdl, 1);
        if (!out)
        {
            db.logError("Could not make writable output");
            return false;
        }

        // Determine the size of the element to copy
        const IAttributeType& iAttributeType = *carb::getCachedInterface<IAttributeType>();
        Type const type = element.type();
        size_t strideBytes = iAttributeType.baseDataSize(type) * type.componentCount;
        size_t offsetBytes = currentIndex * strideBytes;
        memcpy(out, arrayData + offsetBytes, strideBytes);

        return true;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto const arrayIn = node.iNode->getAttributeByToken(node, inputs::arrayIn.token());
        auto const element = node.iNode->getAttributeByToken(node, outputs::element.token());

        auto const arrayInType = arrayIn.iAttribute->getResolvedType(arrayIn);
        auto const elementType = element.iAttribute->getResolvedType(element);

        if (elementType.baseType == BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ arrayIn, element };

            std::array<uint8_t, 2> tupleCounts{ arrayInType.componentCount, arrayInType.componentCount };
            // value type can not be an array because we don't support arrays-of-arrays
            std::array<uint8_t, 2> arrayDepths{ 1, 0 };
            std::array<AttributeRole, 2> rolesBuf{ arrayInType.role,
                                                   // Copy the attribute role from the array type to the value type
                                                   AttributeRole::eUnknown };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace action
} // namespace graph
} // namespace omni
