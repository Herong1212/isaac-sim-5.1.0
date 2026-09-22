// Copyright (c) 2019-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// Improved #define preprocessor directives that support compile-time checking for mispelled or missing
// directives. Basically, the same as #define MY_FEATURE 0/1, but with a bit more compile-time safety,
// and ease of use around mixing or combining boolean logic.
//
// #if USING( X )..
// .. with X = IN_USE is #if (1 && 1)
// .. with X = NOT_IN_USE is #if (1 &&! 1)
// .. with X undefined is (1 X 1) where the compiler fails at substitution for X, and produces a compile-time error
//
// Example usage:
// #define MY_FEATURE_A IN_USE
// #define MY_FEATURE_B NOT_IN_USE
// #define MY_FEATURE_C USE_IF( USING( MY_FEATURE_A ) && USING( MY_FEATURE_B ) )
// ...
// void doStuff()
// {
// #if USING( MY_FEATURE_C )
//     doStuff_C();
// #else // #if USING( MY_FEATURE_C )
//     doStuff_NotC();
// #endif // #if USING( MY_FEATURE_C )
// }

#define IN_USE &&
#define NOT_IN_USE &&!
#define USE_IF(X) &&((X) ? 1 : 0)&&
#define USING(X) (1 X 1)
#define NOT_USING(X) !(1 X 1)


#ifndef NDEBUG
#    define DEVELOPMENT_BUILD IN_USE
#else // #ifndef NDEBUG
#    define DEVELOPMENT_BUILD NOT_IN_USE
#endif // #ifndef NDEBUG

#ifdef _WIN32
#    define WINDOWS_BUILD IN_USE
#    define LINUX_BUILD NOT_IN_USE
#    define MACOS_BUILD NOT_IN_USE
#elif defined(__linux__) // #ifdef _WIN32
#    define WINDOWS_BUILD NOT_IN_USE
#    define LINUX_BUILD IN_USE
#    define MACOS_BUILD NOT_IN_USE
#elif defined(__APPLE__) // #elif defined(__linux__) // #ifdef _WIN32
#    define WINDOWS_BUILD NOT_IN_USE
#    define LINUX_BUILD NOT_IN_USE
#    define MACOS_BUILD IN_USE
#else // #elif defined(__APPLE__) // #elif defined(__linux__) // #ifdef _WIN32
#    error "Unsupported platform"
#endif

#define ASSERTS USE_IF(USING(DEVELOPMENT_BUILD))

#define ARRAY_COUNT(X) ((sizeof(X) / sizeof(0 [X])) / ((size_t)(!(sizeof(X) % sizeof(0 [X])))))
#define COMPILE_ASSERT(X) static_assert((X), #X)
#define COMPILE_ASSERT_MSG(X,M) static_assert((X), M)

#if USING( WINDOWS_BUILD )
	#define COMPILER_SUPPRESS_WARN_BEGIN 				_Pragma("warning(push)")
	#define COMPILER_SUPPRESS_WARN_END 					_Pragma("warning(pop)")
	#define COMPILER_SUPPRESS_WARN_MISSING_SWITCH_CASE 	_Pragma("warning(error: 4061)") \
														_Pragma("warning(error: 4062)")
#elif USING(LINUX_BUILD)
	#define COMPILER_SUPPRESS_WARN_BEGIN 				_Pragma("GCC diagnostic push")
	#define COMPILER_SUPPRESS_WARN_END 					_Pragma("GCC diagnostic pop")
	#define COMPILER_SUPPRESS_WARN_MISSING_SWITCH_CASE 	_Pragma("GCC diagnostic ignored \"-Wswitch-enum\"")
#endif

#define RETURN_IF(_cond) do { const bool b = !!(_cond); if(b) return; } while(0)
#define RETURN_VALUE_IF(_cond, _value) do { const bool b = !!(_cond); if(b) return (_value); } while(0)
#define RETURN_FALSE_IF(_cond) RETURN_VALUE_IF(_cond,false)
#define RETURN_TRUE_IF(_cond) RETURN_VALUE_IF(_cond,true)
#define RETURN_NULL_IF(_cond) RETURN_VALUE_IF(_cond,nullptr)
//
#define RETURN_IF_NOT_A_CACHE(_fabricId) RETURN_IF((_fabricId == kInvalidFabricId))
#define RETURN_IF_NOT_A_PATH(_path) RETURN_IF((_path == kUninitializedPath))
#define RETURN_IF_NOT_A_TOKEN(_token) RETURN_IF((_token == kUninitializedToken))
#define RETURN_VALUE_IF_NOT_A_PATH(_path, _value) RETURN_VALUE_IF((_path == kUninitializedPath),_value)
#define RETURN_VALUE_IF_NOT_A_TOKEN(_token, _value) RETURN_VALUE_IF((_token == kUninitializedToken),_value)
#define RETURN_VALUE_IF_NOT_A_CACHE(_fabricId, _value) RETURN_VALUE_IF((_fabricId == kInvalidFabricId),_value)
#define RETURN_FALSE_IF_NOT_A_PATH(_path) RETURN_VALUE_IF_NOT_A_PATH(_path,false)
#define RETURN_NULLPTR_IF_NOT_A_PATH(_path) RETURN_VALUE_IF_NOT_A_PATH(_path,nullptr)
//
#define FAIL_AND_RETURN_IF(_cond) do { const bool b = !!(_cond); CARB_ASSERT(!b, #_cond); if(b) return; } while(0)
#define FAIL_AND_RETURN_VALUE_IF(_cond, _value) do { const bool b = !!(_cond); CARB_ASSERT(!b, #_cond); if(b) return (_value); } while(0)
#define FAIL_AND_RETURN_FALSE_IF(_cond) FAIL_AND_RETURN_VALUE_IF(_cond,false)
#define FAIL_AND_RETURN_TRUE_IF(_cond) FAIL_AND_RETURN_VALUE_IF(_cond,true)
#define FAIL_AND_RETURN_NULL_IF(_cond) FAIL_AND_RETURN_VALUE_IF(_cond,nullptr)
//
#define LOG_FAIL_AND_RETURN_IF(_cond, _value, fmt, ...) do { const bool b = !!(_cond); CARB_ASSERT(!b, #_cond); if(b) { CARB_LOG(carb::logging::kLevelError, fmt, ##__VA_ARGS__); return; } ; } while(0)
#define LOG_FAIL_AND_RETURN_VALUE_IF(_cond, _value, fmt, ...) do { const bool b = !!(_cond); CARB_ASSERT(!b, #_cond); if(b) { CARB_LOG(carb::logging::kLevelError, fmt, ##__VA_ARGS__); return _value; } ; } while(0)
