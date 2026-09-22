// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <carb/events/EventsUtils.h>
#include <carb/events/IEvents.h>

#include <omni/graph/core/ogn/UsdTypes.h>

#include <algorithm>
#include <cstring>
#include <map>
#include <memory>
#include <utility>

namespace omni
{
namespace graph
{
namespace ui_nodes
{

/**
 * Checks if the node with `inputs:onlyPlayback` should be disabled, because playback is not happening.
 *
 * @param[in] db The node OGN Database object
 * @return true if the node should be disabled
 */
template <typename NodeDb>
bool checkNodeDisabledForOnlyPlay(NodeDb const& db)
{
    return db.inputs.onlyPlayback() && (not db.abi_context().iContext->getIsPlaying(db.abi_context()));
}

/**
 * Memoizes constant copies of C-strings to reduce heap allocation calls when passing equivalent C-strings between
 * scopes.
 */
class StringMemo
{
public:
    /**
     * Finds or creates a constant copy of the input C-string having the same lifetime as this StringMemo object.
     *
     * @param[in] cstr A null-terminated C-style string
     * @return An equivalent constant C-style string
     */
    char const* lookup(char const* cstr)
    {
        if (!cstr)
            return nullptr;

        auto it = m_map.find(cstr);
        if (it == m_map.end())
        {
            std::unique_ptr<char const, cstr_deleter> cstr_copy{ cstrdup(cstr) };
            char const* cstr_copy_ptr = cstr_copy.get();
            m_map.emplace(cstr_copy_ptr, std::move(cstr_copy));

            return cstr_copy_ptr;
        }

        return it->first;
    }

private:
    static char* cstrdup(const char* cstr)
    {
        std::size_t const len = std::strlen(cstr);
        char* new_copy = static_cast<char*>(std::malloc(len + 1));
        if (!new_copy)
            return nullptr;
        std::memcpy(new_copy, cstr, len + 1);
        return new_copy;
    }

    struct cstr_cmp
    {
        bool operator()(char const* a, char const* b) const
        {
            return std::strcmp(a, b) < 0;
        }
    };

    struct cstr_deleter
    {
        void operator()(char const* p) const
        {
            std::free(const_cast<char*>(p));
        }
    };

    std::map<char const*, std::unique_ptr<char const, cstr_deleter>, cstr_cmp> m_map;
};

}
}
}
