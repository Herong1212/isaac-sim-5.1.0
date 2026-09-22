// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

namespace Private
{

template <size_t TUPLE_SIZE, typename ComputeType, typename InputType>
inline bool validateInputsAndOutput(gsl::span<InputType const> const inputs,
                                    ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu> result)
{
    if (TUPLE_SIZE == 1)
    {
        if (result.type().arrayDepth == 0)
        {
            // handle single values

            auto resultValue = result.template get<ComputeType>();

            if (!TryComputeHelper<decltype(resultValue)>::testValid(resultValue))
                return false;

            for (auto const& input : inputs)
            {
                auto const inputValue = input.template get<ComputeType>();
                if (!TryComputeHelper<decltype(inputValue)>::testValid(inputValue))
                    return false;
            }
        }
        else
        {
            // handle arrays

            auto resultValue = result.template get<ComputeType[]>();
            if (!TryComputeHelper<decltype(resultValue)>::testValid(resultValue))
                return false;

            for (auto const& input : inputs)
            {
                if (RuntimeAttribHelper<TUPLE_SIZE, typename remove_const_ref<decltype(input)>::type>::isArray(input))
                {
                    auto const inputValue = input.template get<ComputeType[]>();
                    if (!TryComputeHelper<decltype(inputValue)>::testValid(inputValue))
                        return false;
                }
                else
                {
                    auto const inputValue = input.template get<ComputeType>();
                    if (!TryComputeHelper<decltype(inputValue)>::testValid(inputValue))
                        return false;
                }
            }
        }
    }
    else
    {
        using ComputeTypeTuple = ComputeType[TUPLE_SIZE];

        if (result.type().componentCount != TUPLE_SIZE)
            return false;

        if (result.type().arrayDepth == 0)
        {
            // handle tuple values

            auto resultValue = result.get<ComputeTypeTuple>();

            if (!TryComputeHelper<decltype(resultValue)>::testValid(resultValue))
                return false;

            for (auto const& input : inputs)
            {
                if (RuntimeAttribHelper<TUPLE_SIZE, typename remove_const_ref<decltype(input)>::type>::isTuple(input))
                {
                    auto const inputValue = input.template get<ComputeTypeTuple>();
                    if (!TryComputeHelper<decltype(inputValue)>::testValid(inputValue))
                        return false;
                }
                else
                {
                    auto const inputValue = input.template get<ComputeType>();
                    if (!TryComputeHelper<decltype(inputValue)>::testValid(inputValue))
                        return false;
                }
            }
        }
        else
        {
            // handle arrays of tuples

            auto resultValue = result.get<ComputeTypeTuple[]>();
            if (!TryComputeHelper<decltype(resultValue)>::testValid(resultValue))
                return false;

            for (auto const& input : inputs)
            {
                if (RuntimeAttribHelper<TUPLE_SIZE, typename remove_const_ref<decltype(input)>::type>::isArray(input))
                {
                    if (RuntimeAttribHelper<TUPLE_SIZE, typename remove_const_ref<decltype(input)>::type>::isTuple(input))
                    {
                        auto const inputValue = input.template get<ComputeTypeTuple[]>();
                        if (!TryComputeHelper<decltype(inputValue)>::testValid(inputValue))
                            return false;
                    }
                    else
                    {
                        auto const inputValue = input.template get<ComputeType[]>();
                        if (!TryComputeHelper<decltype(inputValue)>::testValid(inputValue))
                            return false;
                    }
                }
                else
                {
                    if (RuntimeAttribHelper<TUPLE_SIZE, typename remove_const_ref<decltype(input)>::type>::isTuple(input))
                    {
                        auto const inputValue = input.template get<ComputeTypeTuple>();
                        if (!TryComputeHelper<decltype(inputValue)>::testValid(inputValue))
                            return false;
                    }
                    else
                    {
                        auto const inputValue = input.template get<ComputeType>();
                        if (!TryComputeHelper<decltype(inputValue)>::testValid(inputValue))
                            return false;
                    }
                }
            }
        }
    }

    return true;
}


template <typename ComputeType, typename InputType, typename Functor>
inline bool tryComputeInputsWithArrayBroadcasting(gsl::span<InputType const> const inputs,
                                                  ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu> result,
                                                  Functor functor,
                                                  size_t count)
{
    if (!validateInputsAndOutput<1, ComputeType, InputType>(inputs, result))
        return false;

    if (result.type().arrayDepth == 0)
    {
        // the output is not an array
        auto resultValue = result.get<ComputeType>();
        using TResultValue = typename remove_const_ref<decltype(*resultValue)>::type;

        auto inputIt = inputs.begin();
        // initialize the result
        {
            auto const inputValue = inputIt->template get<ComputeType>();
            using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
            for (size_t instance = 0; instance < count; ++instance)
            {
                auto const& inputData = ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, 0, 0, instance);
                auto& resultData = ArrayHelper<1, TResultValue>::accessArg(*resultValue, 0, 0, instance);

                resultData = inputData;
            }
        }
        // accumulate the result by iterating over the remaining inputs
        ++inputIt;
        for (; inputIt != inputs.end(); ++inputIt)
        {
            auto const inputValue = inputIt->template get<ComputeType>();
            using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
            for (size_t instance = 0; instance < count; ++instance)
            {
                functor(ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, 0, 0, instance),
                        ArrayHelper<1, TResultValue>::accessArg(*resultValue, 0, 0, instance));
            }
        }
        return true;
    }
    else
    {
        // cache for the array data, to avoid having to get it from fabric multiple times
        // (once for getting the size, a second time for computing the result)
        std::vector<ArrayDataReadOnly<ComputeType[], ogn::kCpu>> arrayDataCache;
        arrayDataCache.reserve(inputs.size());

        // the output is an array of single values

        // result.get<ComputeType[]>() returns a temporary value, so it has to be cached.
        auto arrayObj = result.template get<ComputeType[]>();
        auto& resultArray = *arrayObj;
        using TResultValue = typename remove_const_ref<decltype(resultArray)>::type;

        for (size_t instance = 0; instance < count; ++instance)
        {
            // find the output length
            size_t len = 0;
            for (const auto& input : inputs)
            {
                using TInput = typename remove_const_ref<decltype(input)>::type;
                if (RuntimeAttribHelper<1, TInput>::isArray(input))
                {
                    arrayDataCache.emplace_back(input.template get<ComputeType[]>());
                    auto const& array = *arrayDataCache.back();
                    auto s = ArrayHelper<1, decltype(array)>::getArgsLengthAndAdjustHandle(array, instance);
                    if (s != len && len > 0)
                        throw InputError("Unable to broadcast arrays of differing lengths: " + std::to_string(s) +
                                         " != " + std::to_string(len));
                    len = std::max(len, s);
                }
            }

            if (instance)
                resultArray.adjustHandle(1);

            resultArray.resize(len);

            auto arrayDataCacheIt = arrayDataCache.cbegin();

            auto inputIt = inputs.begin();
            using TInput = typename remove_const_ref<decltype(*inputIt)>::type;
            if (RuntimeAttribHelper<1, TInput>::isArray(*inputIt))
            {
                const auto& inputValue = *arrayDataCacheIt++;
                using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                for (size_t idx = 0; idx < len; ++idx)
                {
                    auto const& inputData = ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, idx, 0, instance);
                    auto& resultData = ArrayHelper<1, TResultValue>::accessArg(resultArray, idx, 0, instance);
                    resultData = inputData;
                }
            }
            else
            {
                auto const inputValue = inputIt->template get<ComputeType>();
                using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                auto const& inputData = ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, 0, 0, instance);
                for (size_t idx = 0; idx < len; ++idx)
                {
                    auto& resultData = ArrayHelper<1, TResultValue>::accessArg(resultArray, idx, 0, instance);
                    resultData = inputData;
                }
            }
            ++inputIt;
            for (; inputIt != inputs.end(); ++inputIt)
            {
                using TInput = typename remove_const_ref<decltype(*inputIt)>::type;
                if (RuntimeAttribHelper<1, TInput>::isArray(*inputIt))
                {
                    auto const& inputValue = *arrayDataCacheIt++;
                    using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                    for (size_t idx = 0; idx < len; ++idx)
                    {
                        auto const& inputData =
                            ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, idx, 0, instance);
                        auto& resultData = ArrayHelper<1, TResultValue>::accessArg(resultArray, idx, 0, instance);
                        functor(inputData, resultData);
                    }
                }
                else
                {
                    auto const inputValue = inputIt->template get<ComputeType>();
                    using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                    auto const& inputData = ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, 0, 0, instance);
                    for (size_t idx = 0; idx < len; ++idx)
                    {
                        auto& resultData = ArrayHelper<1, TResultValue>::accessArg(resultArray, idx, 0, instance);
                        functor(inputData, resultData);
                    }
                }
            }
        }

        return true;
    }

    return false;
}

template <size_t N, typename InputIterator>
inline bool isTuple(InputIterator it)
{
    return N != 1 && it->type().componentCount == N;
}

template <typename InputIterator>
inline bool isArray(InputIterator it)
{
    return it->type().arrayDepth != 0;
}

template <size_t N, typename ComputeType, typename InputType, typename Functor>
inline bool tryComputeInputsWithTupleBroadcasting(gsl::span<InputType const> const inputs,
                                                  ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu> result,
                                                  Functor functor,
                                                  size_t count)
{
    if (!validateInputsAndOutput<N, ComputeType, InputType>(inputs, result))
        return false;

    using ComputeTypeTuple = ComputeType[N];

    if (result.type().arrayDepth == 0)
    {
        // the output is not an array

        auto resultValue = result.get<ComputeTypeTuple>();
        using TResultValue = typename remove_const_ref<decltype(*resultValue)>::type;

        auto inputIt = inputs.begin();

        // initialize the result
        using TInput = typename remove_const_ref<decltype(*inputIt)>::type;
        if (RuntimeAttribHelper<N, TInput>::isTuple(*inputIt))
        {
            auto const inputValue = inputIt->template get<ComputeTypeTuple>();
            using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
            for (size_t instance = 0; instance < count; ++instance)
            {
                for (uint8_t t = 0; t < N; ++t)
                {
                    auto const& inputData = ArrayHelper<N, TInputValue>::accessArgConst(*inputValue, 0, t, instance);
                    auto& resultData = ArrayHelper<N, TResultValue>::accessArg(*resultValue, 0, t, instance);
                    resultData = inputData;
                }
            }
        }
        else
        {
            auto const inputValue = inputIt->template get<ComputeType>();
            using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
            for (size_t instance = 0; instance < count; ++instance)
            {
                auto const& inputData = ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, 0, 0, instance);
                for (uint8_t t = 0; t < N; ++t)
                {
                    auto& resultData = ArrayHelper<N, TResultValue>::accessArg(*resultValue, 0, t, instance);
                    resultData = inputData;
                }
            }
        }
        ++inputIt;
        for (; inputIt != inputs.end(); ++inputIt)
        {
            using TInput = typename remove_const_ref<decltype(*inputIt)>::type;
            if (RuntimeAttribHelper<N, TInput>::isTuple(*inputIt))
            {
                auto const inputValue = inputIt->template get<ComputeTypeTuple>();
                using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                for (size_t instance = 0; instance < count; ++instance)
                {
                    for (uint8_t t = 0; t < N; ++t)
                    {
                        auto const& inputData = ArrayHelper<N, TInputValue>::accessArgConst(*inputValue, 0, t, instance);
                        auto& resultData = ArrayHelper<N, TResultValue>::accessArg(*resultValue, 0, t, instance);
                        functor(inputData, resultData);
                    }
                }
            }
            else
            {
                auto const& inputValue = inputIt->template get<ComputeType>();
                using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                for (size_t instance = 0; instance < count; ++instance)
                {
                    auto const& inputData = ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, 0, 0, instance);
                    for (uint8_t t = 0; t < N; ++t)
                    {
                        auto& resultData = ArrayHelper<N, TResultValue>::accessArg(*resultValue, 0, t, instance);
                        functor(inputData, resultData);
                    }
                }
            }
        }
        return true;
    }
    else // result.type().arrayDepth > 0
    {
        // cache for the array data, to avoid having to get it from fabric multiple times
        // (once for getting the size, a second time for computing the result)
        // Note: we need different caches for tuple and non tuple arrays
        std::vector<ArrayDataReadOnly<ComputeType[], ogn::kCpu>> arrayDataCache;
        arrayDataCache.reserve(inputs.size());
        std::vector<TupleArrayDataReadOnly<ComputeTypeTuple[], ogn::kCpu>> tupleArrayDataCache;
        tupleArrayDataCache.reserve(inputs.size());

        // result.get<ComputeTypeTuple[]>() returns a temporary value, so it has to be cached.
        auto arrayObj = result.template get<ComputeTypeTuple[]>();
        auto& resultArray = *arrayObj;
        using TResultValue = typename remove_const_ref<decltype(resultArray)>::type;

        for (size_t instance = 0; instance < count; ++instance)
        {
            size_t len = 0;
            for (auto const& input : inputs)
            {
                using TInput = typename remove_const_ref<decltype(input)>::type;
                if (RuntimeAttribHelper<N, TInput>::isArray(input))
                {
                    tupleArrayDataCache.emplace_back(input.template get<ComputeTypeTuple[]>());
                    auto const& array = *tupleArrayDataCache.back();
                    auto s = ArrayHelper<N, decltype(array)>::getArgsLengthAndAdjustHandle(array, instance);
                    if (s != len && len > 0)
                        throw InputError("Unable to broadcast arrays of differing lengths: " + std::to_string(s) +
                                         " != " + std::to_string(len));
                    len = std::max(len, s);
                }
                else if (RuntimeAttribHelper<1, TInput>::isArray(input))
                {
                    arrayDataCache.emplace_back(input.template get<ComputeType[]>());
                    auto const& array = *arrayDataCache.back();
                    auto s = ArrayHelper<1, decltype(array)>::getArgsLengthAndAdjustHandle(array, instance);
                    if (s != len && len > 0)
                        throw InputError("Unable to broadcast arrays of differing lengths: " + std::to_string(s) +
                                         " != " + std::to_string(len));
                    len = std::max(len, s);
                }
            }

            if (instance)
                resultArray.adjustHandle(1);
            resultArray.resize(len);

            auto arrayDataCacheIt = arrayDataCache.cbegin();
            auto tupleArrayDataCacheIt = tupleArrayDataCache.cbegin();

            auto inputIt = inputs.begin();
            if (!isArray(inputIt))
            {
                if (isTuple<N>(inputIt))
                {
                    auto const inputValue = inputIt->template get<ComputeTypeTuple>();
                    using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                    for (size_t idx = 0; idx < len; ++idx)
                    {
                        for (uint8_t t = 0; t < N; ++t)
                        {
                            auto const& inputData =
                                ArrayHelper<N, TInputValue>::accessArgConst(*inputValue, 0, t, instance);
                            auto& resultData = ArrayHelper<N, TResultValue>::accessArg(resultArray, idx, t, instance);
                            resultData = inputData;
                        }
                    }
                }
                else
                {
                    auto const inputValue = inputIt->template get<ComputeType>();
                    using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                    auto const& inputData = ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, 0, 0, instance);
                    for (size_t idx = 0; idx < len; ++idx)
                    {
                        for (uint8_t t = 0; t < N; ++t)
                        {
                            auto& resultData = ArrayHelper<N, TResultValue>::accessArg(resultArray, idx, t, instance);
                            resultData = inputData;
                        }
                    }
                }
            }
            else
            {
                if (isTuple<N>(inputIt))
                {
                    auto const& inputValue = *tupleArrayDataCacheIt++;
                    using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                    for (size_t idx = 0; idx < len; ++idx)
                    {
                        for (uint8_t t = 0; t < N; ++t)
                        {
                            auto const& inputData =
                                ArrayHelper<N, TInputValue>::accessArgConst(*inputValue, idx, t, instance);
                            auto& resultData = ArrayHelper<N, TResultValue>::accessArg(resultArray, idx, t, instance);
                            resultData = inputData;
                        }
                    }
                }
                else
                {
                    const auto& inputValue = *arrayDataCacheIt++;
                    using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                    for (size_t idx = 0; idx < len; ++idx)
                    {
                        auto const& inputData =
                            ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, idx, 0, instance);
                        for (uint8_t t = 0; t < N; ++t)
                        {
                            auto& resultData = ArrayHelper<N, TResultValue>::accessArg(resultArray, idx, t, instance);
                            resultData = inputData;
                        }
                    }
                }
            }
            ++inputIt;
            for (; inputIt != inputs.end(); ++inputIt)
            {
                if (!isArray(inputIt))
                {
                    if (isTuple<N>(inputIt))
                    {
                        auto const inputValue = inputIt->template get<ComputeTypeTuple>();
                        using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                        for (size_t idx = 0; idx < len; ++idx)
                        {
                            for (uint8_t t = 0; t < N; ++t)
                            {
                                auto const& inputData =
                                    ArrayHelper<N, TInputValue>::accessArgConst(*inputValue, 0, t, instance);
                                auto& resultData = ArrayHelper<N, TResultValue>::accessArg(resultArray, idx, t, instance);
                                functor(inputData, resultData);
                            }
                        }
                    }
                    else
                    {
                        auto const inputValue = inputIt->template get<ComputeType>();
                        using TInputValue = typename remove_const_ref<decltype(*inputValue)>::type;
                        auto const& inputData = ArrayHelper<1, TInputValue>::accessArgConst(*inputValue, 0, 0, instance);
                        for (size_t idx = 0; idx < len; ++idx)
                        {
                            for (uint8_t t = 0; t < N; ++t)
                            {
                                auto& resultData = ArrayHelper<N, TResultValue>::accessArg(resultArray, idx, t, instance);
                                functor(inputData, resultData);
                            }
                        }
                    }
                }
                else
                {
                    if (isTuple<N>(inputIt))
                    {
                        auto const& inputValueArray = *tupleArrayDataCacheIt++;
                        using TInputValue = typename remove_const_ref<decltype(*inputValueArray)>::type;
                        for (size_t idx = 0; idx < len; ++idx)
                        {
                            for (uint8_t t = 0; t < N; ++t)
                            {
                                auto const& inputData =
                                    ArrayHelper<N, TInputValue>::accessArgConst(*inputValueArray, idx, t, instance);
                                auto& resultData = ArrayHelper<N, TResultValue>::accessArg(resultArray, idx, t, instance);
                                functor(inputData, resultData);
                            }
                        }
                    }
                    else
                    {
                        auto const& inputValueArray = *arrayDataCacheIt++;
                        using TInputValue = typename remove_const_ref<decltype(*inputValueArray)>::type;
                        for (size_t idx = 0; idx < len; ++idx)
                        {
                            auto const& inputData =
                                ArrayHelper<1, TInputValue>::accessArgConst(*inputValueArray, idx, 0, instance);
                            for (uint8_t t = 0; t < N; ++t)
                            {
                                auto& resultData = ArrayHelper<N, TResultValue>::accessArg(resultArray, idx, t, instance);
                                functor(inputData, resultData);
                            }
                        }
                    }
                }
            }
        }

        return true;
    }

    return false;
}


} // namespace private
