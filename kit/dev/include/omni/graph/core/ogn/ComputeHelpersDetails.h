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
/** ========================= Compute utils=========================== */
// Solves array VS single value args/result

// Small helper structure to broacast operation on tuple component when asked for (TUPLE_SIZE != 1)
// In that case, computation will be broadcasted to actual tuple elements
template <size_t TUPLE_SIZE, typename T>
struct TupleHelper
{
    static inline auto& get(T& val, size_t /*tupleIdx*/, size_t idx) {
        return (&val)[idx];
    }
    static inline auto& getConst(T const& val, size_t /*tupleIdx*/, size_t idx) {
        return (&val)[idx];
    }
};

template <size_t TUPLE_SIZE, typename T>
struct TupleHelper <TUPLE_SIZE, T[TUPLE_SIZE]>
{
    static inline auto& get(T* val, size_t tupleIdx, size_t idx) {
        return val[idx * TUPLE_SIZE + tupleIdx];
    }
    static inline auto& getConst(T const* val, size_t tupleIdx, size_t idx) {
        return val[idx * TUPLE_SIZE + tupleIdx];
    }
};

template <typename T>
struct TupleHelper<1, T>
{
    static inline auto& get(T& val, size_t /*tupleIdx*/, size_t idx) {
        return (&val)[idx];
    }
    static inline auto& getConst(T const& val, size_t /*tupleIdx*/, size_t idx) {
        return (&val)[idx];
    }
};

template <typename T>
struct TupleHelper<1, T[1]>
{
    template<typename U>
    static inline auto& get(U& val, size_t tupleIdx, size_t idx) {
        return (&val[tupleIdx])[idx];
    }
    template <typename U>
    static inline auto& getConst(U const& val, size_t tupleIdx, size_t idx) {
        return (&val[tupleIdx])[idx];
    }
};

constexpr size_t kNotAnArray{ size_t(-1) };

//Small helper structure to differentiate array attributes from regular attribute,
// and allows to make the proper operation depending of it
template <size_t TUPLE_SIZE, typename T, bool IsArray = is_array<typename remove_const_ref<T>::type>::value>
struct ArrayHelper
{
    static inline auto& accessArg(T& val, size_t /*index*/, size_t tupleIdx, size_t idx){
        return TupleHelper<TUPLE_SIZE, T>::get(val, tupleIdx, idx);
    }
    static inline auto const& accessArgConst(T const& val, size_t /*index*/, size_t tupleIdx, size_t idx){
        return TupleHelper<TUPLE_SIZE, T>::getConst(val, tupleIdx, idx);
    }

    template<typename... ARGS>
    static constexpr size_t setResultLen(size_t, T&, const ARGS&...) {
        return 1;
    }
    static constexpr size_t getArgsLengthAndAdjustHandle(T const&, size_t) {
        return kNotAnArray;
    }
};

template <size_t TUPLE_SIZE, typename T_>
struct ArrayHelper<TUPLE_SIZE, T_, true>
{
    using T = typename remove_const_ref<T_>::type;
    using InnerType = typename T::iterator::value_type;
    static inline auto& accessArg(T& val, size_t index, size_t tupleIdx, size_t /*instance*/) {
        return TupleHelper<TUPLE_SIZE, InnerType>::get(val[index], tupleIdx, 0);
    }
    static inline auto const& accessArgConst(T const& val, size_t index, size_t tupleIdx, size_t /*instance*/){
        return TupleHelper<TUPLE_SIZE, InnerType>::getConst(val[index], tupleIdx, 0);
    }
    template <typename... ARGS>
    static size_t const setResultLen(size_t instance, T& res, const ARGS&... args)
    {
        auto comp = [](size_t ret, size_t others)
        {
            if (ret != kNotAnArray)
            {
                if (others != kNotAnArray)
                {
                    if (ret != others)
                    {
                        throw InputError("Unable to broadcast arrays of differing lengths: " + std::to_string(ret) +
                                         " != " + std::to_string(others));
                    }
                    return std::max(ret, others);
                }
                return ret;
            }
            return others;
        };
        size_t size = fold(comp, ArrayHelper<1, decltype(args)>::getArgsLengthAndAdjustHandle(args, instance)...);
        if (size == kNotAnArray)
            size = 1;

        //The array is already pointing to the first instance
        // offset it by 1 instance on every other calls
        if (instance)
            res.adjustHandle(1);

        res.resize(size);
        return size;
    }
    static size_t const getArgsLengthAndAdjustHandle(T const& arg, size_t instance)
    {
        // The array is already pointing to the first instance
        //  offset it by 1 instance on every other calls
        if (instance)
            const_cast<T&>(arg).adjustHandle(1);
        return arg.size();
    }
};

//Perform a broadcasted computation, expanding any provided scalar for each array entry
// All provided arrays must have the same length
template <size_t TUPLE_SIZE, typename Result, typename Functor, typename... Args>
void compute(size_t const count, Result& result, Functor const& functor, const Args&... args)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        size_t const len = ArrayHelper<TUPLE_SIZE, Result>::setResultLen(idx, result, args...);
        for (size_t i = 0; i < len; ++i)
            for (size_t j = 0; j < TUPLE_SIZE; ++j)
                functor(ArrayHelper<TUPLE_SIZE, Args>::accessArgConst(args, i, j, idx)...,
                        ArrayHelper<TUPLE_SIZE, Result>::accessArg(result, i, j, idx));
    }
}


/** ========================= TryCompute utilities =========================== */
// Solves RuntimeAttribute compatibility VS Regular attribute

//Helper class to test the validity and access the data of RuntimeAttribute,
// or just return the data for regular attribute
template <typename T, bool RTData = is_runtime_data<typename remove_const_ref<T>::type>::value>
struct TryComputeHelper
{
    using base_type = typename remove_const_ref<T>::type;

    static bool testValid(base_type const& val) {
        return (bool)val;
    }
    static auto& accessData(base_type& val) {
        return *val;
    }
    static const auto& accessData(base_type const& val) {
        return *val;
    }
};

template <typename T>
struct TryComputeHelper<T, false>
{
    using base_type = typename remove_const_ref<T>::type;

    static bool testValid(base_type const& val) {
        return true;
    }
    static base_type& accessData(base_type& val) {
        return val;
    }
    static const base_type& accessData(base_type const& val) {
        return val;
    }
};

// This functions test validity of its runtime attributes, and if all valid,
// forward the call to do the broadcasted computation
template <size_t TUPLE_SIZE, typename Result, typename Functor, typename... Args>
bool tryCompute(size_t count, Result&& result, Functor const& functor, Args&&... args)
{
    if (!TryComputeHelper<Result>::testValid(result) ||
        !(fold(std::logical_and<>(), TryComputeHelper<decltype(args)>::testValid(args)...)))
        return false;

    compute<TUPLE_SIZE>(count, TryComputeHelper<Result>::accessData(std::forward<Result&&>(result)), functor,
            TryComputeHelper<Args>::accessData(std::forward<Args&&>(args))...);

    return true;
}


/** ========================= TryComputeArray utilities =========================== */

// Some/All args are Runtime, and might be array or simple value: this block of functionalities select the proper combination
//  of array/not array for runtime attribs

//Small helper struct that separates RuntimeAttribute from regular attribute,
// and allows to retrieve the asked accessors for those Runtime attributes
template <size_t TUPLE_SIZE, typename T>
struct RuntimeAttribHelper
{
    using T_ = typename remove_const_ref<T>::type;

    // the templated type is only use with RT attribute to retrieve the value
    template <typename Useless> static T_& accessData(T_& val) {
        return val;
    }
    template <typename Useless> static T_ const& accessData(T_ const& val) {
        return val;
    }

    static bool isArray(T const&) {
        return false;
    }
    static bool isTuple(T const& val) {
        return false;
    }
};

template <size_t TUPLE_SIZE, eAttributeType AttributeType, eMemoryType MemoryType>
struct RuntimeAttribHelper<TUPLE_SIZE, ogn::RuntimeAttribute<AttributeType, MemoryType>>
{
    using RTAttr = ogn::RuntimeAttribute<AttributeType, MemoryType>;

    template <typename T>
    static auto accessData(RTAttr const& val) {
        return val.template get<T>();
    }
    static bool isArray(RTAttr const& val) {
        return val.type().arrayDepth != 0;
    }
    static bool isTuple(RTAttr const& val) {
        return TUPLE_SIZE != 1 && val.type().componentCount == TUPLE_SIZE;
    }
};

// This struct is a helper that will scan a list of input arguments to determine whether or not each of them is an array.
// This information is collected by recursively calling "callCorrectCompute", and acumulating the resolved types in the class
// template arguments "ResolvedTypes".
// Once the recursive call ends (when all the inputs have been scanned), a specialized version of "callCorrectCompute"
// unpack the tuple to forward the call to tryCompute (through "makeCall"), with all the appropriate accessors for runtime attribute resolved
template <typename... ResolvedTypes>
struct ArgumentTypeSelector
{
    template <size_t TUPLE_SIZE, typename... ComputeTypes, typename Ret, typename Functor, typename Args>
    static bool callCorrectCompute( bool const allowArrays,
                                    size_t count,
                                    Ret&& ret,
                                    Functor const& f,
                                    Args&& args,
                                    typename std::enable_if<sizeof...(ResolvedTypes) != sizeof...(ComputeTypes)>::type* _cond = 0)
    {
        using ComputeType = typename std::tuple_element<sizeof...(ResolvedTypes), std::tuple<ComputeTypes...>>::type;
        using ComputeTypeTuple = ComputeType[TUPLE_SIZE];
        auto const& arg = std::get<sizeof...(ResolvedTypes)>(args);
        using RTAH = RuntimeAttribHelper<TUPLE_SIZE, typename remove_const_ref<decltype(arg)>::type>;
        if (RTAH::isArray(arg))
        {
            if (allowArrays == false)
                return false;
            if (RTAH::isTuple(arg))
                return ArgumentTypeSelector<ResolvedTypes..., ComputeTypeTuple[]>::template callCorrectCompute<TUPLE_SIZE, ComputeTypes...>(allowArrays, count, ret, f, args);
            return ArgumentTypeSelector<ResolvedTypes..., ComputeType[]>::template callCorrectCompute<TUPLE_SIZE, ComputeTypes...>(allowArrays, count, ret, f, args);
        }
        if (RTAH::isTuple(arg))
            return ArgumentTypeSelector<ResolvedTypes..., ComputeTypeTuple>::template callCorrectCompute<TUPLE_SIZE, ComputeTypes...>(allowArrays, count, ret, f, args);
        return ArgumentTypeSelector<ResolvedTypes..., ComputeType>::template callCorrectCompute<TUPLE_SIZE, ComputeTypes...>(allowArrays, count, ret, f, args);
    }

    template <size_t TUPLE_SIZE, typename... ComputeTypes, typename Ret, typename Functor, typename Args>
    static bool callCorrectCompute( bool const /*allowArrays*/,
                                    size_t count,
                                    Ret&& ret,
                                    Functor const& f,
                                    Args&& args,
                                    typename std::enable_if<sizeof...(ResolvedTypes) == sizeof...(ComputeTypes)>::type* _cond = 0)
    {
        return makeCall<TUPLE_SIZE>(count, ret, f, args, std::make_index_sequence<sizeof...(ComputeTypes)>());
    }

    template <size_t TUPLE_SIZE, size_t... Indices, typename Ret, typename Functor, typename Args>
    static bool makeCall(size_t count, Ret&& ret, Functor const& f, Args&& args, std::index_sequence<Indices...>)
    {
        using Args_ = typename remove_const_ref<Args>::type;
        return tryCompute<TUPLE_SIZE>( count, ret, f,
            RuntimeAttribHelper<TUPLE_SIZE, typename remove_const_ref<typename std::tuple_element<Indices, Args_>::type>::type>
                ::template accessData<ResolvedTypes>(std::get<Indices>(args))...);
    }
};

// Main entry point for broadcasting the provided functor to each element of arrays (if arrays are provided)
// In the case of the output not being an array, it is assumed that inputs are not either,
//  and this call is just forwarded to the compute function which will check that that inputs have compatible types
// If the output is an array, the call is forwarded to the "ArgumentTypeSelector" helper class, that will scan each input argument
//  to determine whether or not is an array, and perform the final broadcasting call.
//  The parameter pack is passed as a std::tuple so it is workable
template <size_t TUPLE_SIZE, typename RetType, typename... ComputeTypes, typename Functor, typename... Args>
bool tryComputeWithArrayBroadcasting(size_t count,
                                     ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu>& result,
                                     Functor const& functor,
                                     const Args&... args)
{
    using RetTypeTuple = RetType[TUPLE_SIZE];

    if (result.type().arrayDepth == 0)
    {
        if (TUPLE_SIZE != 1)
        {
            if (result.type().componentCount != TUPLE_SIZE)
                return false;
            return ArgumentTypeSelector<>::callCorrectCompute<TUPLE_SIZE, ComputeTypes...>(
                false, count, result.get<RetTypeTuple>(), functor, std::forward_as_tuple(args...));
        }
        return ArgumentTypeSelector<>::callCorrectCompute<TUPLE_SIZE, ComputeTypes...>(
            false, count, result.get<RetType>(), functor, std::forward_as_tuple(args...));
    }


    if (TUPLE_SIZE != 1)
    {
        if (result.type().componentCount != TUPLE_SIZE)
            return false;
        return ArgumentTypeSelector<>::callCorrectCompute<TUPLE_SIZE, ComputeTypes...>(
            true, count, result.get<RetTypeTuple[]>(), functor, std::forward_as_tuple(args...));
    }
    return ArgumentTypeSelector<>::callCorrectCompute<TUPLE_SIZE, ComputeTypes...>(
        true, count, result.get<RetType[]>(), functor, std::forward_as_tuple(args...));
}

// Meta function that selects a given element in a tuple, or, in the case of a single-element tuple
//   returns this unique element regardless of the index
// @input TUPLE: the tuple on which to operate
// @input IDX: the index at which the element must be extracted
// @private COUNT: private argument that allows to specialize for single-element TUPLE input
template <typename TUPLE, size_t IDX, size_t COUNT = std::tuple_size<TUPLE>::value>
struct AccessComputeTypes
{
    using type = typename std::tuple_element<IDX, TUPLE>::type;
};
template <typename TUPLE, size_t IDX>
struct AccessComputeTypes<TUPLE, IDX, 1>
{
    using type = typename std::tuple_element<0, TUPLE>::type;
};

//This functions is a pass-through adapter that has 2 purposes:
//#1/ We allow to provide all the compute types that will be used to access the inputs/output data,
//   but also a unique one, that will be applied to each input/output. This is the purpose of AccessComputeTypes:
//    Selectively expand a unique type to a parameter pack duplicating this type the right amount of time,
//    or use the parameter pack as provided. The pack provided (containing 1 or n elements) is converted to std::tuple
//    in order to be workable.
//#2/ Changes the order of arguments, moving the output and the functor as first arguments,
//    allowing to move a random number of inputs as a parameter pack at the end of the function
template <size_t TUPLE_SIZE, typename... ComputeTypes, typename TUPLE, size_t... Inputs>
inline bool tryComputeWithArrayBroadcasting_ReverseHelper(TUPLE&& tuple,
                                                          std::index_sequence<Inputs...>,
                                                          size_t count)
{
    using CTTuple = std::tuple<ComputeTypes...>;
    return tryComputeWithArrayBroadcasting< TUPLE_SIZE,
                                            typename AccessComputeTypes<CTTuple, sizeof...(Inputs)>::type,
                                            typename AccessComputeTypes<CTTuple, Inputs>::type...>(
                                                                count,
                                                                std::get<sizeof...(Inputs)>(tuple),
                                                                std::get<sizeof...(Inputs) + 1>(tuple),
                                                                std::get<Inputs>(tuple)...);
}



// This functions is a pass-through adapter that forward the arguments as a tuple, and creates a corresponding index_sequence
// This will allow the ReverseHelper to do its job of modifying the parameter order (see purpose #2  above)
template <typename TUPLE, size_t... Inputs>
inline bool tryCompute_ReverseHelper(TUPLE&& tuple, std::index_sequence<Inputs...>, size_t count)
{
    using RetType = typename std::tuple_element<sizeof...(Inputs), TUPLE>::type;
    return tryCompute<1>(
        count,
        std::forward<RetType&&>(std::get<sizeof...(Inputs)>(tuple)),
        std::get<sizeof...(Inputs) + 1>(tuple),
        std::get<Inputs>(tuple)...);
}


// Small helper to detect whether a vectorized compute has been asked or not
template <typename... Arguments>
struct VectorizationHelper
{
    using Tuple = std::tuple<Arguments...>;
    using LastType = typename std::tuple_element<sizeof...(Arguments) - 1, Tuple>::type;
    static constexpr bool isVectorized = std::is_integral<typename remove_const_ref<LastType>::type>::value;
    static constexpr int Offset = isVectorized ? 1 : 0;

    static size_t count(Tuple&& args)
    {
        return count_helper(std::forward<Tuple>(args), std::integral_constant<bool,isVectorized>());
    }

private:
    static size_t count_helper(Tuple&& args, std::false_type /*isVectorized*/) {
        return 1;
    }
    static size_t count_helper(Tuple&& args, std::true_type  /*isVectorized*/) {
        return std::get<sizeof...(Arguments) - 1>(args);
    }
};


}//namespace private
