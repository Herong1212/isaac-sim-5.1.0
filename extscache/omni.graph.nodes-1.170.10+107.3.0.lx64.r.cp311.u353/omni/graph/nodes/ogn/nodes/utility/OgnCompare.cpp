// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnCompareDatabase.h>
#include <functional>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/string.h>
#include <omni/graph/core/ogn/Types.h>
#include <carb/logging/Log.h>

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T>
std::function<bool(const T&, const T&)> getOperation(OgnCompareDatabase& db, NameToken operation)
{
    // Find the desired comparison
    std::function<bool(const T&, const T&)> fn;
    if (operation == db.tokens.gt)
        fn = [](const T& a, const T& b) { return a > b; };
    else if (operation == db.tokens.lt)
        fn = [](const T& a, const T& b) { return a < b; };
    else if (operation == db.tokens.ge)
        fn = [](const T& a, const T& b) { return a >= b; };
    else if (operation == db.tokens.le)
        fn = [](const T& a, const T& b) { return a <= b; };
    else if (operation == db.tokens.eq)
        fn = [](const T& a, const T& b) { return a == b; };
    else if (operation == db.tokens.ne)
        fn = [](const T& a, const T& b) { return a != b; };
    else
    {
        throw ogn::compute::InputError("Failed to resolve token " + std::string(db.tokenToString(operation)) +
                                       ", expected one of (>,<,>=,<=,==,!=)");
    }
    return fn;
}

template <>
std::function<bool(const OgnToken&, const OgnToken&)> getOperation(OgnCompareDatabase& db, NameToken operation)
{
    std::function<bool(const OgnToken&, const OgnToken&)> fn;

    if (operation == db.tokens.eq)
        fn = [](const OgnToken& a, const OgnToken& b) { return a == b; };
    else if (operation == db.tokens.ne)
        fn = [](const OgnToken& a, const OgnToken& b) { return a != b; };
    else if (operation == db.tokens.gt || operation == db.tokens.lt || operation == db.tokens.ge ||
             operation == db.tokens.le)
        throw ogn::compute::InputError("Operation " + std::string(db.tokenToString(operation)) +
                                       " not supported for Tokens, expected one of (==,!=)");
    else
        throw ogn::compute::InputError("Failed to resolve token " + std::string(db.tokenToString(operation)) +
                                       ", expected one of (>,<,>=,<=,==,!=)");

    return fn;
}

template <typename T>
bool tryComputeAssumingType(OgnCompareDatabase& db, NameToken operation, size_t count)
{
    auto op = getOperation<T>(db, operation);
    auto functor = [&](auto const& a, auto const& b, auto& result) { result = op(a, b); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, T, bool>(
        db.inputs.a(), db.inputs.b(), db.outputs.result(), functor, count);
}

template <typename T, size_t N>
bool tryComputeAssumingType(OgnCompareDatabase& db, NameToken operation, size_t count)
{
    auto op = getOperation<T>(db, operation);
    auto functor = [&](auto const& a, auto const& b, auto& result)
    {
        // Lexicographical comparison of tuples
        result = true;
        for (size_t i = 0; i < N; i++)
        {
            if (i < (N - 1) && (a[i] == b[i]))
                continue;
            else if (op(a[i], b[i]))
            {
                result = true;
                break;
            }
            else
            {
                result = false;
                break;
            }
        }
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T[N], bool>(
        db.inputs.a(), db.inputs.b(), db.outputs.result(), functor, count);
}

bool tryComputeAssumingString(OgnCompareDatabase& db, NameToken operation, size_t count)
{
    auto op = getOperation<ogn::const_string>(db, operation);
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto stringA = db.inputs.a(idx).get<const char[]>();
        auto stringB = db.inputs.b(idx).get<const char[]>();
        *(db.outputs.result(idx).get<bool>()) = op(stringA(), stringB());
    }
    return true;
}
} // namespace

class OgnCompare
{
public:
    static bool computeVectorized(OgnCompareDatabase& db, size_t count)
    {
        try
        {
            auto& aType = db.inputs.a().type();
            auto& bType = db.inputs.b().type();
            if (aType.baseType != bType.baseType)
                throw ogn::compute::InputError("Mismatched base types: " + getBaseTypeName(aType.baseType) + " and " +
                                               getBaseTypeName(bType.baseType));

            if (aType.componentCount != bType.componentCount)
                throw ogn::compute::InputError("Mismatched input types: " + std::to_string(aType.componentCount) +
                                               " and " + std::to_string(bType.componentCount));

            const auto& operation = db.inputs.operation();
            if ((operation != db.tokens.gt) && (operation != db.tokens.lt) && (operation != db.tokens.ge) &&
                (operation != db.tokens.le) && (operation != db.tokens.eq) && (operation != db.tokens.ne))
            {
                std::string op{ "Unknown" };
                char const* opStr = db.tokenToString(operation);
                if (opStr)
                    op = opStr;
                throw ogn::compute::InputError("Unrecognized operation '" + op + std::string("'"));
            }

            auto node = db.abi_node();
            auto opAttrib = node.iNode->getAttributeByToken(node, inputs::operation.m_token);
            bool isOpConstant = opAttrib.iAttribute->isRuntimeConstant(opAttrib);

            using FUNC_SIG = bool (*)(OgnCompareDatabase& db, NameToken operation, size_t count);

            auto repeatWork = [&](FUNC_SIG const& func)
            {
                if (isOpConstant)
                {
                    return func(db, operation, count);
                }
                bool ret = true;
                while (count)
                {
                    ret = func(db, operation, 1) && ret;
                    db.moveToNextInstance();
                    --count;
                }
                return ret;
            };

            switch (aType.baseType)
            {
            case BaseDataType::eBool:
                return repeatWork(tryComputeAssumingType<bool>);
            case BaseDataType::eDouble:
                switch (aType.componentCount)
                {
                case 1:
                    return repeatWork(tryComputeAssumingType<double>);
                case 2:
                    return repeatWork(tryComputeAssumingType<double, 2>);
                case 3:
                    return repeatWork(tryComputeAssumingType<double, 3>);
                case 4:
                    return repeatWork(tryComputeAssumingType<double, 4>);
                case 9:
                    return repeatWork(tryComputeAssumingType<double, 9>);
                case 16:
                    return repeatWork(tryComputeAssumingType<double, 16>);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eFloat:
                switch (aType.componentCount)
                {
                case 1:
                    return repeatWork(tryComputeAssumingType<float>);
                case 2:
                    return repeatWork(tryComputeAssumingType<float, 2>);
                case 3:
                    return repeatWork(tryComputeAssumingType<float, 3>);
                case 4:
                    return repeatWork(tryComputeAssumingType<float, 4>);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (aType.componentCount)
                {
                case 1:
                    return repeatWork(tryComputeAssumingType<pxr::GfHalf>);
                case 2:
                    return repeatWork(tryComputeAssumingType<pxr::GfHalf, 2>);
                case 3:
                    return repeatWork(tryComputeAssumingType<pxr::GfHalf, 3>);
                case 4:
                    return repeatWork(tryComputeAssumingType<pxr::GfHalf, 4>);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt:
                switch (aType.componentCount)
                {
                case 1:
                    return repeatWork(tryComputeAssumingType<int32_t>);
                case 2:
                    return repeatWork(tryComputeAssumingType<int32_t, 2>);
                case 3:
                    return repeatWork(tryComputeAssumingType<int32_t, 3>);
                case 4:
                    return repeatWork(tryComputeAssumingType<int32_t, 4>);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt64:
                return repeatWork(tryComputeAssumingType<int64_t>);
            case BaseDataType::eToken:
                return repeatWork(tryComputeAssumingType<OgnToken>);
            case BaseDataType::eUChar:
                if ((aType.role == AttributeRole::eText || aType.role == AttributeRole::ePath) &&
                    (bType.role == AttributeRole::eText || bType.role == AttributeRole::ePath) && aType.arrayDepth == 1 &&
                    bType.arrayDepth == 1 && aType.componentCount == 1 && bType.componentCount == 1)
                {
                    return repeatWork(tryComputeAssumingString);
                }
                return repeatWork(tryComputeAssumingType<unsigned char>);
            case BaseDataType::eUInt:
                return repeatWork(tryComputeAssumingType<uint32_t>);
            case BaseDataType::eUInt64:
                return repeatWork(tryComputeAssumingType<uint64_t>);
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

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto a = node.iNode->getAttributeByToken(node, inputs::a.token());
        auto b = node.iNode->getAttributeByToken(node, inputs::b.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto aType = a.iAttribute->getResolvedType(a);
        auto bType = b.iAttribute->getResolvedType(b);

        // Require inputs to be resolved before determining result's type
        if (aType.baseType != BaseDataType::eUnknown && bType.baseType != BaseDataType::eUnknown)
        {
            const bool isStringInput =
                (aType.baseType == BaseDataType::eUChar && bType.baseType == BaseDataType::eUChar &&
                 (aType.role == AttributeRole::eText || aType.role == AttributeRole::ePath) &&
                 (bType.role == AttributeRole::eText || bType.role == AttributeRole::ePath) && aType.arrayDepth == 1 &&
                 bType.arrayDepth == 1 && aType.componentCount == 1 && bType.componentCount == 1);
            const uint8_t resultArrayDepth = isStringInput ? 0 : std::max(aType.arrayDepth, bType.arrayDepth);
            Type resultType(BaseDataType::eBool, 1, resultArrayDepth);
            result.iAttribute->setResolvedType(result, resultType);
        }
        else
            result.iAttribute->setResolvedType(result, Type(BaseDataType::eUnknown));
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
