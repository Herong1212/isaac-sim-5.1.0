// Copyright (c) 2019-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once


#include <omni/fabric/core/Defines.h>

#include <cstdint>
#include <cstdlib>
#include <cstddef>

#if USING(WINDOWS_BUILD)
#   include <carb/CarbWindows.h>
#   include <intrin.h>
#   define __MM_SSE4
#elif USING(LINUX_BUILD)
#   define __MM_SSE4
#elif USING(MACOS_BUILD)
#   define __MM_SSE4
#else
#   error "Unsupported platform"
#endif

namespace omni
{
namespace fabric
{

inline uint32_t clz32(const uint32_t x)
{
#if USING(WINDOWS_BUILD)
    DWORD z;
    return _BitScanReverse(&z, x) ? 31 - z : 32;
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD) // #if USING( WINDOWS_BUILD )
    return x ? __builtin_clz(x) : 32;
#else // #if USING( WINDOWS_BUILD )
#    error "Unsupported platform"
#endif // #if USING( WINDOWS_BUILD )
}


inline uint32_t clz64(const uint64_t x)
{
#if USING(WINDOWS_BUILD)
    DWORD z;
    return _BitScanReverse64(&z, x) ? 63 - z : 64;
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD) // #if USING( WINDOWS_BUILD )
    return x ? __builtin_clzll(x) : 64;
#else // #if USING( WINDOWS_BUILD )
#    error "Unsupported platform"
#endif // #if USING( WINDOWS_BUILD )
}


inline uint32_t ctz32(const uint32_t x)
{
#if USING(WINDOWS_BUILD)
    DWORD z;
    return _BitScanForward(&z, x) ? z : 32;
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD) // #if USING( WINDOWS_BUILD )
    return x ? __builtin_ctz(x) : 32;
#else // #if USING( WINDOWS_BUILD )
#    error "Unsupported platform"
#endif // #if USING( WINDOWS_BUILD )
}


inline uint32_t ctz64(const uint64_t x)
{
#if USING(WINDOWS_BUILD)
    DWORD z;
    return _BitScanForward64(&z, x) ? z : 64;
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD) // #if USING( WINDOWS_BUILD )
    return x ? __builtin_ctzll(x) : 64;
#else // #if USING( WINDOWS_BUILD )
#    error "Unsupported platform"
#endif // #if USING( WINDOWS_BUILD )
}


inline uint64_t bswap64(const uint64_t x)
{
#if USING(WINDOWS_BUILD)
    return _byteswap_uint64(x);
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD) // #if USING( WINDOWS_BUILD )
    return __builtin_bswap64(x);
#else // #if USING( WINDOWS_BUILD )
#    error "Unsupported platform"
#endif // #if USING( WINDOWS_BUILD )
}


inline uint64_t rotr64(const uint64_t value, const int shift)
{
#if USING(WINDOWS_BUILD)
    return _rotr64(value, shift);
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD) // #if USING( WINDOWS_BUILD )
    return (value >> shift) | (value << (64 - shift));
#else // #if USING( WINDOWS_BUILD )
#    error "Unsupported platform"
#endif // #if USING( WINDOWS_BUILD )
}


inline uint64_t rotl64(const uint64_t value, const int shift)
{
#if USING(WINDOWS_BUILD)
    return _rotl64(value, shift);
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD) // #if USING( WINDOWS_BUILD )
    return (value << shift) | (value >> (64 - shift));
#else // #if USING( WINDOWS_BUILD )
#    error "Unsupported platform"
#endif // #if USING( WINDOWS_BUILD )
}


// lock_xchg
// { tmp = *_Destination; if(tmp == _Expected) *ptr = _Desired; return tmp; }
inline uint64_t lock_xchg(uint64_t volatile* _Destination, uint64_t _Expected, uint64_t _Desired)
{
#if USING(WINDOWS_BUILD)
    return _InterlockedCompareExchange64((int64_t volatile *)_Destination, _Desired, _Expected);
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD)
    uint64_t expected = _Expected;
    __atomic_compare_exchange_n(_Destination, &expected, _Desired, false, __ATOMIC_RELEASE, __ATOMIC_ACQUIRE);
    return expected;
#else
#   error "Unsupported platform"
#endif
}


// lock_xchg_kvp
// { tmpkey = *_Key; if(tmpkey == _ExpectedKey) { *_Key = _DesiredKey; *_Value = _DesiredValue, return tmpkey; }
inline uint64_t lock_xchg_kvp(uint64_t volatile* _Key, uint64_t volatile* _Value, uint64_t _ExpectedKey, uint64_t _DesiredKey, uint64_t _DesiredValue)
{
    const uint64_t tmpKey = lock_xchg(_Key, _ExpectedKey, _DesiredKey);
    if(tmpKey == _ExpectedKey)
        *_Value = _DesiredValue;
#if USING(WINDOWS_BUILD)
    _mm_mfence();
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD)
     __sync_synchronize();
#else
#    error "Unsupported platform"
#endif
    return tmpKey;
}

inline uint64_t lock_xchg_kvp(uint64_t volatile* _Key, uint64_t volatile* _Value, uint64_t _ExpectedKey, uint64_t _DesiredKey, uint64_t (*_DesiredValue)(void*), void* ud)
{
    const uint64_t tmpKey = lock_xchg(_Key, _ExpectedKey, _DesiredKey);
    if(tmpKey == _ExpectedKey)
        *_Value = _DesiredValue(ud);
#if USING(WINDOWS_BUILD)
    _mm_mfence();
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD)
     __sync_synchronize();
#else
#    error "Unsupported platform"
#endif
    return tmpKey;
}


// lock_add
// { tmp = *ptr; *ptr += val; return tmp; }
inline uint32_t lock_add(uint32_t volatile * _Addend, uint32_t _Value)
{
#if USING(WINDOWS_BUILD)
    static_assert(sizeof(long) == sizeof(uint32_t), "sizeof(long) == sizeof(uint32_t)");
    return _InterlockedExchangeAdd((long volatile *)_Addend, _Value);
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD)
    return __atomic_fetch_add(_Addend, _Value, __ATOMIC_RELEASE);
#else
#    error "Unsupported platform"
#endif
}

inline uint64_t lock_add(uint64_t volatile * _Addend, uint64_t _Value)
{
#if USING(WINDOWS_BUILD)
    return _InterlockedExchangeAdd64((int64_t volatile *)_Addend, _Value);
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD)
    return __atomic_fetch_add(_Addend, _Value, __ATOMIC_RELEASE);
#else
#    error "Unsupported platform"
#endif
}


// lock_inc
// { *ptr += 1; return *ptr; }
inline uint32_t lock_inc(uint32_t volatile * _Addend)
{
#if USING(WINDOWS_BUILD)
    static_assert(sizeof(long) == sizeof(uint32_t), "sizeof(long) == sizeof(uint32_t)");
    return _InterlockedIncrement((long volatile *)_Addend);
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD)
    return __atomic_add_fetch(_Addend, 1, __ATOMIC_RELEASE);
#else
#    error "Unsupported platform"
#endif
}

inline uint64_t lock_inc(uint64_t volatile * _Addend)
{
#if USING(WINDOWS_BUILD)
    return _InterlockedIncrement64((int64_t volatile *)_Addend);
#elif USING(LINUX_BUILD) || USING(MACOS_BUILD)
    return __atomic_add_fetch(_Addend, 1, __ATOMIC_RELEASE);
#else
#    error "Unsupported platform"
#endif
}


// interleave8_mem
// { u32* a32=addr; u32 hi=a32[0]; u32 lo=a32[1];
//      return concat( hi[31:24] lo[31:24] hi[23:16] lo[23:16] hi[15:8] lo[15:8] hi[7:0] lo[7:0] );
// }
__MM_SSE4 inline  uint64_t interleave8_mem(uint64_t* addr)
{
    CARB_ASSERT(addr);
#if CARB_X86_64 && USING(WINDOWS_BUILD)
    __m128i u = _mm_loadl_epi64((const __m128i*)addr);
    __m128i r = _mm_shuffle_epi8(u, _mm_set_epi64x(0,0x0307020601050004ull));
    return _mm_cvtsi128_si64(r);
#else
#define _u_byte(i) ((u>>(i*8))&0xff)
#define _sl(v,i)   ((v)<<(i*8))
    const uint64_t u = addr[0];
    return  _sl(_u_byte(3), 7)
        |   _sl(_u_byte(7), 6)
        |   _sl(_u_byte(2), 5)
        |   _sl(_u_byte(6), 4)
        |   _sl(_u_byte(1), 3)
        |   _sl(_u_byte(5), 2)
        |   _sl(_u_byte(0), 1)
        |   _sl(_u_byte(4), 0);
#undef _u_byte
#undef _sl
#endif
}

} // namespace fabric
} // namespace omni
