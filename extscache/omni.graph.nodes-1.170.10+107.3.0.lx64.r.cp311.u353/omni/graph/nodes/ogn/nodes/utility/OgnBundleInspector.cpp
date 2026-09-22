// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnBundleInspectorDatabase.h>
#include <omni/graph/core/ogn/UsdTypes.h>
#include <fstream>
#include <iomanip>

namespace omni
{
namespace graph
{
namespace nodes
{
template <typename CppType>
std::string valueToString(const CppType& value)
{
    return std::to_string(value);
}
template <>
std::string valueToString(const pxr::GfHalf& value)
{
    return std::to_string((float)value);
}
template <>
std::string valueToString(const bool& value)
{
    return value ? "True" : "False";
}
// TODO: This string conversion code is better suited to the BundledAttribute where it is accessible to all

// Since there are only three matrix dimensions a lookup is faster than a sqrt() call.
const int matrixDimensionMap[17]{ 1, 1, 1, 1, 2, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 4 };

// Helper template to output a convertible simple value as a string. Used when std::to_string works on the type.
template <typename CppType>
bool simpleValueToString(const ogn::RuntimeAttribute<core::ogn::kOgnInput, core::ogn::kCpu>& runtimeInput,
                         std::string& valueToSet)
{
    if (const auto value = runtimeInput.get<CppType>())
    {
        valueToSet = valueToString(*value);
        return true;
    }
    return false;
}
// Helper template to output a convertible simple tuple value as a string.
// The output format is parenthesized "(X, Y, Z)"
template <typename CppType>
bool tupleValueToString(const ogn::RuntimeAttribute<core::ogn::kOgnInput, core::ogn::kCpu>& runtimeInput,
                        std::string& valueToSet)
{
    if (const auto value = runtimeInput.get<CppType>())
    {
        auto inputType = runtimeInput.type();
        valueToSet = "(";
        if (inputType.isMatrixType())
        {
            uint8_t dimension = inputType.dimension();
            uint8_t index{ 0 };
            for (uint8_t row = 0; row < dimension; ++row)
            {
                if (row > 0)
                {
                    valueToSet += ", ";
                }
                valueToSet += "(";
                for (int col = 0; col < dimension; ++col)
                {
                    if (col > 0)
                    {
                        valueToSet += ", ";
                    }
                    valueToSet += valueToString(value[index++]);
                }
                valueToSet += ")";
            }
        }
        else
        {
            for (uint8_t tupleIndex = 0; tupleIndex < value.tupleSize(); ++tupleIndex)
            {
                if (tupleIndex > 0)
                {
                    valueToSet += ", ";
                }
                valueToSet += valueToString(value[tupleIndex]);
            }
        }
        valueToSet += ")";
        return true;
    }
    return false;
}
// Helper template to output a convertible simple array value as a string.
// The output format has square brackets "[X, Y, Z]"
template <typename CppType>
bool arrayValueToString(const ogn::RuntimeAttribute<core::ogn::kOgnInput, core::ogn::kCpu>& runtimeInput,
                        std::string& valueToSet)
{
    if (const auto arrayValue = runtimeInput.get<CppType>())
    {
        auto role = runtimeInput.type().role;
        auto baseType = runtimeInput.type().baseType;
        const bool isString =
            (baseType == BaseDataType::eUChar) && ((role == AttributeRole::eText) || (role == AttributeRole::ePath));

        if (isString)
        {
            std::string rawString(reinterpret_cast<const char*>(arrayValue->data()), arrayValue->size());
            valueToSet = "'";
            valueToSet += rawString;
            valueToSet += "'";
        }
        else
        {
            valueToSet = "[";
            size_t index{ 0 };
            for (const auto& value : *arrayValue)
            {
                if (index++ > 0)
                {
                    valueToSet += ", ";
                }
                valueToSet += valueToString(value);
            }
            valueToSet += "]";
        }
        return true;
    }
    return false;
}

// Helper template to output a convertible tuple array value as a string.
// The output format has square brackets "[(X1, Y1), (X2, Y2), (X3, Y3))]"
template <typename CppType>
bool tupleArrayValueToString(const ogn::RuntimeAttribute<core::ogn::kOgnInput, core::ogn::kCpu>& runtimeInput,
                             std::string& valueToSet)
{
    if (const auto tupleArrayValue = runtimeInput.get<CppType>())
    {
        auto inputType = runtimeInput.type();
        const bool isMatrix = inputType.isMatrixType();
        auto tupleSize = inputType.dimension();
        valueToSet = "[";
        size_t index{ 0 };
        for (const auto& value : *tupleArrayValue)
        {
            if (index++ > 0)
            {
                valueToSet += ", ";
            }
            valueToSet += "(";
            if (isMatrix)
            {
                int tupleIndex{ 0 };
                for (int row = 0; row < tupleSize; ++row)
                {
                    if (row > 0)
                    {
                        valueToSet += ", ";
                    }
                    valueToSet += "(";
                    for (int col = 0; col < tupleSize; ++col)
                    {
                        if (col > 0)
                        {
                            valueToSet += ", ";
                        }
                        valueToSet += valueToString(value[tupleIndex++]);
                    }
                    valueToSet += ")";
                }
            }
            else
            {
                for (int tupleIndex = 0; tupleIndex < tupleSize; ++tupleIndex)
                {
                    if (tupleIndex > 0)
                    {
                        valueToSet += ", ";
                    }
                    valueToSet += valueToString(value[tupleIndex]);
                }
            }
            valueToSet += ")";
        }
        valueToSet += "]";
        return true;
    }
    return false;
}

// Node whose responsibility is to analyze the contents of an input bundle attribute
// and create outputs describing them.
class OgnBundleInspector
{
private:
    static void inspectRecursive(const int currentDepth,
                                 const int inspectDepth,
                                 const bool printContents,
                                 OgnBundleInspectorDatabase& db,
                                 const ogn::BundleContents<ogn::kOgnInput, ogn::kCpu>& inputBundle,
                                 std::ostream& output,
                                 ogn::array<NameToken>& names,
                                 ogn::array<NameToken>& types,
                                 ogn::array<NameToken>& roles,
                                 ogn::array<int>& arrayDepths,
                                 ogn::array<int>& tupleCounts,
                                 ogn::array<NameToken>& values)
    {
        IToken const* iToken = carb::getCachedInterface<omni::fabric::IToken>();

        auto bundleName = inputBundle.abi_bundleInterface()->getName();

        std::string indent{ "    " };
        auto attributeCount = inputBundle.attributeCount();
        auto childCount = inputBundle.childCount();
        output << "Bundle '" << iToken->getText(bundleName) << "' from "
               << db.abi_node().iNode->getPrimPath(db.abi_node()) << " (attributes = " << attributeCount
               << " children = " << childCount << ")" << std::endl;

        // Walk the contents of the input bundle, extracting the attribute information along the way
        size_t index = 0;
        for (const auto& bundledAttribute : inputBundle)
        {
            if (bundledAttribute.isValid())
            {
                // The attribute names and etc apply only to top level bundle passed to the BundleInspector
                if (currentDepth == 0)
                    names[index] = bundledAttribute.name();
                for (int numIndent = 0; numIndent < currentDepth; numIndent++)
                    output << indent;
                output << indent << "[" << index << "] " << db.tokenToString(bundledAttribute.name());

                const Type& attributeType = bundledAttribute.type();
                output << "(" << attributeType << ")";

                if (currentDepth == 0)
                {
                    {
                        std::ostringstream nameStream;
                        nameStream << attributeType.baseType;
                        types[index] = db.stringToToken(nameStream.str().c_str());
                    }
                    {
                        std::ostringstream nameStream;
                        nameStream << getOgnRoleName(attributeType.role);
                        roles[index] = db.stringToToken(nameStream.str().c_str());
                    }
                    arrayDepths[index] = attributeType.arrayDepth;
                    tupleCounts[index] = attributeType.componentCount;
                }

                // Convert the value into a string, using an empty string for unknown types
                std::string valueAsString{ "__unsupported__" };
                bool noOutput = !simpleValueToString<bool>(bundledAttribute, valueAsString) &&
                                !arrayValueToString<bool[]>(bundledAttribute, valueAsString) &&
                                !simpleValueToString<int64_t>(bundledAttribute, valueAsString) &&
                                !arrayValueToString<int64_t[]>(bundledAttribute, valueAsString) &&
                                !simpleValueToString<uint8_t>(bundledAttribute, valueAsString) &&
                                !arrayValueToString<uint8_t[]>(bundledAttribute, valueAsString) &&
                                !simpleValueToString<uint32_t>(bundledAttribute, valueAsString) &&
                                !arrayValueToString<uint32_t[]>(bundledAttribute, valueAsString) &&
                                !simpleValueToString<uint64_t>(bundledAttribute, valueAsString) &&
                                !arrayValueToString<uint64_t[]>(bundledAttribute, valueAsString) &&
                                !simpleValueToString<double>(bundledAttribute, valueAsString) &&
                                !arrayValueToString<double[]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<double[2]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<double[][2]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<double[3]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<double[][3]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<double[4]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<double[][4]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<double[9]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<double[][9]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<double[16]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<double[][16]>(bundledAttribute, valueAsString) &&
                                !simpleValueToString<float>(bundledAttribute, valueAsString) &&
                                !arrayValueToString<float[]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<float[2]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<float[][2]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<float[3]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<float[][3]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<float[4]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<float[][4]>(bundledAttribute, valueAsString) &&
                                !simpleValueToString<int>(bundledAttribute, valueAsString) &&
                                !arrayValueToString<int[]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<int[2]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<int[][2]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<int[3]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<int[][3]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<int[4]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<int[][4]>(bundledAttribute, valueAsString) &&
                                !simpleValueToString<pxr::GfHalf>(bundledAttribute, valueAsString) &&
                                !arrayValueToString<pxr::GfHalf[]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<pxr::GfHalf[2]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<pxr::GfHalf[][2]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<pxr::GfHalf[3]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<pxr::GfHalf[][3]>(bundledAttribute, valueAsString) &&
                                !tupleValueToString<pxr::GfHalf[4]>(bundledAttribute, valueAsString) &&
                                !tupleArrayValueToString<pxr::GfHalf[][4]>(bundledAttribute, valueAsString);
                if (noOutput)
                {
                    if (const auto tokenValue = bundledAttribute.get<OgnToken>())
                    {
                        std::ostringstream tokenValueStream;
                        tokenValueStream << std::quoted(db.tokenToString(*tokenValue));
                        valueAsString = tokenValueStream.str();
                        noOutput = false;
                    }
                }
                if (noOutput)
                {
                    if (const auto tokenArrayValue = bundledAttribute.get<OgnToken[]>())
                    {
                        std::ostringstream tokenArrayValueStream;

                        tokenArrayValueStream << "[";
                        size_t index{ 0 };
                        for (const auto& value : *tokenArrayValue)
                        {
                            if (index++ > 0)
                            {
                                tokenArrayValueStream << ", ";
                            }
                            tokenArrayValueStream << std::quoted(db.tokenToString(value));
                        }
                        tokenArrayValueStream << "]";
                        valueAsString = tokenArrayValueStream.str();
                        noOutput = false;
                    }
                }
                output << " = " << valueAsString << std::endl;
                if (currentDepth == 0)
                    values[index] = db.stringToToken(valueAsString.c_str());

                if (noOutput)
                {
                    std::ostringstream nameStream;
                    nameStream << attributeType;
                    db.logWarning("No value output known for attribute %zu (%s), defaulting to '__unsupported__'",
                                  index, nameStream.str().c_str());
                }
                index++;
            }
            else
            {
                output << indent << "Bundle is invalid" << std::endl;
                db.logWarning("Ignoring invalid bundle member '%s'", db.tokenToString(bundledAttribute.name()));
            }
        }

        // Walk through its children, if any
        if (printContents && childCount && ((currentDepth < inspectDepth) || (inspectDepth <= -1)))
        {
            IConstBundle2* inputBundleIFace = inputBundle.abi_bundleInterface();
            // context is for building the child BundleContents
            const auto context = inputBundleIFace->getContext();

            std::vector<ConstBundleHandle> childBundleHandles(childCount);
            inputBundleIFace->getConstChildBundles(childBundleHandles.data(), childCount);


            for (const auto& childHandle : childBundleHandles)
            {
                if (childHandle.isValid())
                {
                    ogn::BundleContents<ogn::kOgnInput, ogn::kCpu> childBundle(context, childHandle);
                    for (int numIndent = 0; numIndent < currentDepth + 1; numIndent++)
                        output << indent;
                    output << "Has Child "; // No std::endl -> "Has Child Bundle from ..."

                    inspectRecursive(currentDepth + 1, inspectDepth, printContents, db, childBundle, output, names,
                                     types, roles, arrayDepths, tupleCounts, values);
                }
                else
                {
                    for (int numIndent = 0; numIndent < currentDepth; numIndent++)
                        output << indent;
                    output << "One child is invalid." << std::endl;
                }
            }
        }
    }

public:
    static bool compute(OgnBundleInspectorDatabase& db)
    {
        const auto& inputBundle = db.inputs.bundle();
        auto attributeCount = inputBundle.attributeCount();
        auto childCount = inputBundle.childCount();
        db.outputs.bundle() = inputBundle;
        const auto& printContents = db.inputs.print();
        const auto& inspectDepth = db.inputs.inspectDepth();

        // Rather than pollute the file with a bunch of "if (printContents)" setting up a file stream with a
        // bad bit causes the output to be thrown away without parsing.
        std::ofstream ofs;
        ofs.setstate(std::ios_base::badbit);
        auto& output = printContents ? std::cout : ofs;

        db.outputs.count() = attributeCount;
        db.outputs.attributeCount() = attributeCount;
        db.outputs.childCount() = childCount;

        // Extract the output interfaces to nicer names
        auto& names = db.outputs.names();
        auto& types = db.outputs.types();
        auto& roles = db.outputs.roles();
        auto& arrayDepths = db.outputs.arrayDepths();
        auto& tupleCounts = db.outputs.tupleCounts();
        auto& values = db.outputs.values();

        // All outputs except the count are arrays of that size - preallocate them here
        names.resize(attributeCount);
        types.resize(attributeCount);
        roles.resize(attributeCount);
        arrayDepths.resize(attributeCount);
        tupleCounts.resize(attributeCount);
        values.resize(attributeCount);

        inspectRecursive(0, inspectDepth, printContents, db, inputBundle, output, names, types, roles, arrayDepths,
                         tupleCounts, values);

        return true;
    }
};

REGISTER_OGN_NODE();

}
}
}
