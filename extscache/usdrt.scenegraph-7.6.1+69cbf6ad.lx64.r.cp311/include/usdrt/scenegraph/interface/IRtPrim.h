// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtAttribute.h"
#include "IRtObject.h"
#include "IRtRelationship.h"

#include <omni/core/IObject.h>
#include <omni/extras/OutArrayUtils.h>
#include <omni/fabric/IToken.h>
#include <omni/str/IReadOnlyCString.h>

#include <vector>

namespace usdrt
{

enum class OMNI_ATTR("prefix=e") Variability : uint32_t
{
    eVarying,
    eUniform
};

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtPrim);

// *********************************************************************************************************************
// *********************************************************************************************************************
// *********************************************************************************************************************
//
//     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION
//
// The interfaces within these obnoxious comment blocks are now locked for long-term support.
// Any changes you wish to make should be added in a new interface.
//
// Please do not break our precious ABIs!
//
//     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION
//
// *********************************************************************************************************************
// *********************************************************************************************************************
// *********************************************************************************************************************

class IRtPrim_abi : public omni::core::Inherits<usdrt::IRtObject, OMNI_TYPE_ID("usdrt.IRtPrim")>
{
protected: // all ABI functions must always be 'protected'.
    // ---- attributes
    virtual bool hasAttribute_abi(omni::fabric::TokenC attrName) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtAttribute* getAttribute_abi(omni::fabric::TokenC attrName) noexcept = 0;
    virtual IRtAttribute* createAttribute_abi(omni::fabric::TokenC name,
                                              omni::fabric::TypeC typeName,
                                              bool custom,
                                              Variability varying) noexcept = 0;
    virtual OMNI_ATTR("no_api") omni::core::Result getAttributes_abi( // disable omni.bind until OM-21202
        OMNI_ATTR("out, count=*outCount, *not_null") IRtAttribute** out,
        OMNI_ATTR("out, not_null") uint32_t* outCount) noexcept = 0;
    virtual OMNI_ATTR("no_api") omni::core::Result getAuthoredAttributes_abi( // disable omni.bind until OM-21202
        OMNI_ATTR("out, count=*outCount, *not_null") IRtAttribute** out,
        OMNI_ATTR("out, not_null") uint32_t* outCount) noexcept = 0;

    // ---- relationships
    virtual bool hasRelationship_abi(omni::fabric::TokenC relName) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtRelationship* getRelationship_abi(omni::fabric::TokenC relName) noexcept = 0;
    virtual IRtRelationship* createRelationship_abi(omni::fabric::TokenC relName, bool custom) noexcept = 0;
    virtual OMNI_ATTR("no_api") omni::core::Result getRelationships_abi( // disable omni.bind until OM-21202
        OMNI_ATTR("out, count=*outCount, *not_null") IRtRelationship** out,
        OMNI_ATTR("out, not_null") uint32_t* outCount) noexcept = 0;
    virtual OMNI_ATTR("no_api") omni::core::Result getAuthoredRelationships_abi( // disable omni.bind until OM-21202
        OMNI_ATTR("out, count=*outCount, *not_null") IRtRelationship** out,
        OMNI_ATTR("out, not_null") uint32_t* outCount) noexcept = 0;

    // ---- properties
    virtual bool removeProperty_abi(omni::fabric::TokenC propName) noexcept = 0;

    // ---- hierarchy
    virtual OMNI_ATTR("not_prop") IRtPrim* getChild_abi(omni::fabric::TokenC name) noexcept = 0;
    virtual OMNI_ATTR("no_api") omni::core::Result getChildren_abi( // disable omni.bind until OM-21202
        OMNI_ATTR("out, count=*outCount, *not_null") IRtPrim** out,
        OMNI_ATTR("out, not_null") uint32_t* outCount) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtPrim* getParent_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtPrim* getNextSibling_abi() noexcept = 0;

    // ---- types
    virtual OMNI_ATTR("not_prop") omni::fabric::TokenC getTypeName_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") bool setTypeName_abi(omni::fabric::TokenC typeName) noexcept = 0;
    virtual bool hasAuthoredTypeName_abi() noexcept = 0;
    virtual bool clearTypeName_abi() noexcept = 0;
};

// *********************************************************************************************************************
// *********************************************************************************************************************
// *********************************************************************************************************************
//
//     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION
//
// End of locked interfaces. Enjoy the rest of your day.
//
//     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION
//
// *********************************************************************************************************************
// *********************************************************************************************************************
// *********************************************************************************************************************


} // namespace usdrt


#include "IRtPrim.gen.h"

// clang-format off
OMNI_DEFINE_INTERFACE_API(usdrt::IRtPrim)
{
public:

    std::vector<omni::core::ObjectPtr<usdrt::IRtAttribute>> getAttributes() noexcept
    {
        std::vector<omni::core::ObjectPtr<usdrt::IRtAttribute>> vec;
        auto result = omni::extras::getOutArray<usdrt::IRtAttribute*>(
            [this](usdrt::IRtAttribute** out, uint32_t* outCount) // get func
            {
                std::memset(out, 0, sizeof(usdrt::IRtAttribute*) * *outCount); // incoming ptrs must be nullptr
                return this->getAttributes_abi(out, outCount);
            },
            [&vec](usdrt::IRtAttribute** in, uint32_t inCount) // fill func
            {
                vec.reserve(inCount);
                for (uint32_t i = 0; i < inCount; ++i)
                {
                    vec.emplace_back(in[i], omni::core::kSteal);
                }
            }
        );

        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("Unable to get attributes: 0x%08X", result);
        }

        return vec;
    }

    std::vector<omni::core::ObjectPtr<usdrt::IRtAttribute>> getAuthoredAttributes() noexcept
    {
        std::vector<omni::core::ObjectPtr<usdrt::IRtAttribute>> vec;
        auto result = omni::extras::getOutArray<usdrt::IRtAttribute*>(
            [this](usdrt::IRtAttribute** out, uint32_t* outCount) // get func
            {
                std::memset(out, 0, sizeof(usdrt::IRtAttribute*) * *outCount); // incoming ptrs must be nullptr
                return this->getAuthoredAttributes_abi(out, outCount);
            },
            [&vec](usdrt::IRtAttribute** in, uint32_t inCount) // fill func
            {
                vec.reserve(inCount);
                for (uint32_t i = 0; i < inCount; ++i)
                {
                    vec.emplace_back(in[i], omni::core::kSteal);
                }
            });

        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("Unable to get authored attributes: 0x%08X", result);
        }

        return vec;
    }

    std::vector<omni::core::ObjectPtr<usdrt::IRtRelationship>> getRelationships() noexcept
    {
        std::vector<omni::core::ObjectPtr<usdrt::IRtRelationship>> vec;
        auto result = omni::extras::getOutArray<usdrt::IRtRelationship*>(
            [this](usdrt::IRtRelationship** out, uint32_t* outCount) // get func
        {
            std::memset(out, 0, sizeof(usdrt::IRtRelationship*) * *outCount); // incoming ptrs must be nullptr
            return this->getRelationships_abi(out, outCount);
        },
            [&vec](usdrt::IRtRelationship** in, uint32_t inCount) // fill func
        {
            vec.reserve(inCount);
            for (uint32_t i = 0; i < inCount; ++i)
            {
                vec.emplace_back(in[i], omni::core::kSteal);
            }
        }
        );

        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("Unable to get relationships: 0x%08X", result);
        }

        return vec;
    }

    std::vector<omni::core::ObjectPtr<usdrt::IRtRelationship>> getAuthoredRelationships() noexcept
    {
        std::vector<omni::core::ObjectPtr<usdrt::IRtRelationship>> vec;
        auto result = omni::extras::getOutArray<usdrt::IRtRelationship*>(
            [this](usdrt::IRtRelationship** out, uint32_t* outCount) // get func
        {
            std::memset(out, 0, sizeof(usdrt::IRtRelationship*) * *outCount); // incoming ptrs must be nullptr
            return this->getAuthoredRelationships_abi(out, outCount);
        },
            [&vec](usdrt::IRtRelationship** in, uint32_t inCount) // fill func
        {
            vec.reserve(inCount);
            for (uint32_t i = 0; i < inCount; ++i)
            {
                vec.emplace_back(in[i], omni::core::kSteal);
            }
        });
        
        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("Unable to get authored relationships: 0x%08X", result);
        }

        return vec;
    }

    std::vector<omni::core::ObjectPtr<usdrt::IRtPrim>> getChildren() noexcept
    {
        std::vector<omni::core::ObjectPtr<usdrt::IRtPrim>> vec;
        auto result = omni::extras::getOutArray<usdrt::IRtPrim*>(
            [this](usdrt::IRtPrim** out, uint32_t* outCount) // get func
        {
            std::memset(out, 0, sizeof(usdrt::IRtPrim*) * *outCount); // incoming ptrs must be nullptr
            return this->getChildren_abi(out, outCount);
        },
            [&vec](usdrt::IRtPrim** in, uint32_t inCount) // fill func
        {
            vec.reserve(inCount);
            for (uint32_t i = 0; i < inCount; ++i)
            {
                vec.emplace_back(in[i], omni::core::kSteal);
            }
        }
        );

        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("Unable to get children: 0x%08X", result);
        }

        return vec;
    }

};
// clang-format on
