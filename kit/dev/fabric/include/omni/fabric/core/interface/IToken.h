// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>
#ifndef __CUDACC__
// InterfaceUtils.h provides carb::getCachedInterface and is not CUDA-compatible
#    include <carb/InterfaceUtils.h>
#endif // __CUDACC__

// Set to empty macro when IToken::iToken static member is removed
#define FABRIC_ITOKEN_INIT const omni::fabric::IToken* omni::fabric::iToken = nullptr;

#include <string>

namespace omni
{
namespace fabric
{

// TokenC are integer keys that identify paths to C-ABI interfaces
struct TokenC
{
    constexpr TokenC() : token(0){};
    constexpr TokenC(uint64_t _token) : token(_token){};
    uint64_t token;

    // Note that in the name comparisons below we mask off USD's lifetime bit.
    // For example, tokens created from the same string are considered equal even
    // if one was created with finite lifetime and the other infinite lifetime.

    constexpr bool operator<(const TokenC& other) const
    {
        return (token & ~1) < (other.token & ~1);
    }
    constexpr bool operator==(const TokenC& other) const
    {
        return (token & ~1) == (other.token & ~1);
    }
    constexpr bool operator!=(const TokenC& other) const
    {
        return (token & ~1) != (other.token & ~1);
    }
};

static_assert(std::is_standard_layout<TokenC>::value, "Struct must be standard layout as it is used in C-ABI interfaces");

// We don't reference count the uninitialized (or empty) token, and we use
// this fact to avoid unnecessary dll calls to addRef()/removeRef(), for
// example during std::vector resize. To do this we need to check whether a
// token is uninitialized without the dll call getEmptyToken(), so we store
// its value here in a constant.
// We run automated test "IToken::getEmptyToken() dll call can be replaced with
// constant, kUninitializedToken" to ensure that this constant never
// changes.
static constexpr TokenC kUninitializedToken{ (uint64_t)0 };

// C-ABI interface to pxr::TfToken
struct IToken
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IToken", 0, 1);

    TokenC (*getHandle)(const char* name);
    const char* (*getText)(TokenC handle);
    void (*addRef)(TokenC handle);
    void (*removeRef)(TokenC handle);
    TokenC (*getEmptyToken)();
    uint64_t (*size)(TokenC handle);
};

// C++ wrapper for IToken
class Token
{
    static omni::fabric::IToken& sIToken();

public:
    // DEPRECATED: keeping for binary compatibility
    // Will be removed in October 2021 - @TODO set FABRIC_ITOKEN_INIT to empty macro when removed!
    // Still safe to use if initialized in a given dll
    static const omni::fabric::IToken* iToken;

    Token() : mHandle(kUninitializedToken)
    {
    }

    Token(const char* string)
    {
        mHandle = sIToken().getHandle(string);
    }

    // Needs to be noexcept for std::vector::resize() to move instead of copy
    ~Token() noexcept
    {
#ifndef __CUDACC__
        if (mHandle != kUninitializedToken)
        {
            if (!carb::isFrameworkValid())
            {
                return;
            }
            // IToken can be nullptr durin exit process
            if (auto iToken = carb::getCachedInterface<omni::fabric::IToken>())
            {
                iToken->removeRef(mHandle);
            }
        }
#endif // __CUDACC__
    }

    // Copy constructor
    Token(const Token& other) : mHandle(other.mHandle)
    {
        if (mHandle != kUninitializedToken)
        {
            sIToken().addRef(mHandle);
        }
    }

    // Copy construct from integer
    Token(TokenC token) : mHandle(token)
    {
        if (mHandle != kUninitializedToken)
        {
            sIToken().addRef(mHandle);
        }
    }

    // Move constructor
    // Needs to be noexcept for std::vector::resize() to move instead of copy
    Token(Token&& other) noexcept
    {
        // We are moving the src handle so don't need to change its refcount
        mHandle = other.mHandle;

        // Make source invalid
        other.mHandle = kUninitializedToken;
    }

    // Copy assignment
    Token& operator=(const Token& other)
    {
        if (this != &other)
        {
            if (mHandle != kUninitializedToken)
            {
                sIToken().removeRef(mHandle);
            }

            mHandle = other.mHandle;

            if (other.mHandle != kUninitializedToken)
            {
                sIToken().addRef(mHandle);
            }
        }

        return *this;
    }

    // Move assignment
    Token& operator=(Token&& other) noexcept
    {
        if (&other == this)
            return *this;

        // We are about to overwrite the dest handle, so decrease its refcount
        if (mHandle != kUninitializedToken)
        {
            sIToken().removeRef(mHandle);
        }
        // We are moving the src handle so don't need to change its refcount

        mHandle = other.mHandle;
        other.mHandle = kUninitializedToken;

        return *this;
    }

    const char* getText() const
    {
        return sIToken().getText(mHandle);
    }

    uint64_t size() const
    {
        return sIToken().size(mHandle);
    }

    std::string getString() const
    {
        return std::string(sIToken().getText(mHandle), sIToken().size(mHandle));
    }

    // Note that in the name comparisons below TokenC masks off USD's lifetime bit.
    // In other words, tokens created from the same string are considered equal even
    // if one was created with finite lifetime and the other infinite lifetime.

    constexpr bool operator<(const Token& other) const
    {
        return mHandle < other.mHandle;
    }
    constexpr bool operator!=(const Token& other) const
    {
        return mHandle != other.mHandle;
    }
    constexpr bool operator==(const Token& other) const
    {
        return mHandle == other.mHandle;
    }

    constexpr bool operator<(const TokenC& other) const
    {
        return mHandle < other;
    }
    constexpr bool operator!=(const TokenC& other) const
    {
        return mHandle != other;
    }
    constexpr bool operator==(const TokenC& other) const
    {
        return mHandle == other;
    }

    constexpr operator TokenC() const
    {
        return mHandle;
    }

    constexpr const TokenC& asTokenC() const
    {
        return mHandle;
    }

private:
    TokenC mHandle;
};

static_assert(std::is_standard_layout<Token>::value, "Token must be standard layout as it is used in C-ABI interfaces");

#ifndef __CUDACC__
inline omni::fabric::IToken& Token::sIToken()
{
    // Acquire carbonite interface on first use
    omni::fabric::IToken* iToken = carb::getCachedInterface<omni::fabric::IToken>();
    CARB_ASSERT(iToken);
    return *iToken;
}
#endif // __CUDACC__

inline uint64_t swapByteOrder(uint64_t val)
{
#if !CARB_COMPILER_MSC
    // Compilers other than MSVC tend to turn the following into a single instruction like bswap
    val = ((val & 0xFF00000000000000u) >> 56u) | ((val & 0x00FF000000000000u) >> 40u) |
          ((val & 0x0000FF0000000000u) >> 24u) | ((val & 0x000000FF00000000u) >> 8u) |
          ((val & 0x00000000FF000000u) << 8u) | ((val & 0x0000000000FF0000u) << 24u) |
          ((val & 0x000000000000FF00u) << 40u) | ((val & 0x00000000000000FFu) << 56u);
#else
    // MSVC does not currently optimize the above code, so we have to use an intrinsic to get bswap
    val = _byteswap_uint64(val);
#endif
    return val;
}

inline size_t hash(TokenC token)
{
    size_t tokenWithoutMortalityBit = token.token & ~1;

    // The following Hash function was chosen to match the one in pxr\base\tf\hash.h

    // This is based on Knuth's multiplicative hash for integers.  The
    // constant is the closest prime to the binary expansion of the inverse
    // golden ratio.  The best way to produce a hash table bucket index from
    // the result is to shift the result right, since the higher order bits
    // have the most entropy.  But since we can't know the number of buckets
    // in a table that's using this, we just reverse the byte order instead,
    // to get the highest entropy bits into the low-order bytes.
    return swapByteOrder(tokenWithoutMortalityBit * 11400714819323198549ULL);
}

inline size_t hash(Token const& token)
{
    return hash(TokenC(token));
}

} // namespace fabric
} // namespace omni

namespace std
{
template <>
struct hash<omni::fabric::Token>
{
    std::size_t operator()(const omni::fabric::Token& key) const
    {
        return omni::fabric::hash(key);
    }
};
template <>
class hash<omni::fabric::TokenC>
{
public:
    size_t operator()(const omni::fabric::TokenC& key) const
    {
        return omni::fabric::hash(key);
    }
};
} // namespace std
