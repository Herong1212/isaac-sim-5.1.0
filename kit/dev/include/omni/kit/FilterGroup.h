// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/logging/Log.h>

#include <omni/kit/EventSubscribers.h>

#include <functional>
#include <map>
#include <regex>

namespace omni
{
namespace kit
{

/**
 * Defines the filter group class

 * @param ItemT Type of the item to be filtered.
 * @param FilterT Type of the filter used to test item.
 * @param Pred Predicate to test if an item is accepted by a filter.
 */
template <typename ItemT, typename FilterT, typename Pred>
class FilterGroup
{
public:
    using SubscriptionId = uint64_t;
    using OnFilterChangedFn = std::function<void()>;

    /**
     * Tests an item against all enabled filters.
     *
     * @param item The item to be tested.
     * @return True if the item matches any enabled filter.
     */
    bool match(const ItemT& item) const
    {
        if (m_enabledCount == 0 || m_groupEnabled == false)
        {
            return true;
        }

        bool accepted = false;
        for (auto&& filter : m_filters)
        {
            if (!filter.second.enabled)
            {
                continue;
            }

            accepted |= m_pred(item, filter.second.filter);
            if (accepted)
            {
                break;
            }
        }
        return accepted;
    }

    /**
     * Adds a filter to the FilterGroup.
     *
     * @param name The name of the filter.
     * @param filter The filter to be added.
     * @param enabled True to enable the filter on add.
     * @return True if filter is added successfully.
     */
    bool addFilter(const std::string& name, const FilterT& filter, bool enabled)
    {
        auto filterEntry = m_filters.find(name);
        if (filterEntry == m_filters.end())
        {
            m_filters.emplace(name, FilterData{ filter, enabled });
            m_enabledCount += enabled ? 1 : 0;

            // Turn on filterGroup if not already enabled
            m_groupEnabled |= enabled;
            m_filterChangeSubscribers.send();
            return true;
        }
        else
        {
            CARB_LOG_WARN("Failed to add filter %s. Already existed", name.c_str());
        }
        return false;
    }

    /**
     * Gets names of all filters in the FilterGroup.
     *
     * @param filterNames The vector to store all filter names to.
     */
    void getFilterNames(std::vector<std::string>& filterNames) const
    {
        filterNames.reserve(m_filters.size());
        for (auto&& filter : m_filters)
        {
            filterNames.push_back(filter.first);
        }
    }

    /**
     * Checks if a filter is enabled by its name.
     *
     * @param name The name of the filter to be checked.
     * @return True if the filter is enabled. False if filter is disabled or not exists.
     */
    bool isFilterEnabled(const std::string& name) const
    {
        auto filterEntry = m_filters.find(name);
        if (filterEntry != m_filters.end())
        {
            return filterEntry->second.enabled;
        }
        return false;
    }

    /**
     * Enable or disable a filter by its name.
     * If the filter is the first one to be enabled in the FilterGroup, the FilterGroup will be enabled.
     * If the filter is the last one to be disabled in the FilterGroup, the FilterGroup will be disabled.
     *
     * @param name The name of the filter.
     * @param enabled True to enable the filter. False to disable the filter.
     */
    void setFilterEnabled(const std::string& name, bool enabled)
    {
        auto filterEntry = m_filters.find(name);
        if (filterEntry != m_filters.end())
        {
            if (filterEntry->second.enabled != enabled)
            {
                m_enabledCount += enabled ? 1 : -1;
                filterEntry->second.enabled = enabled;

                if (m_groupEnabled && m_enabledCount == 0)
                {
                    m_groupEnabled = false;
                }
                else if (!m_groupEnabled && enabled)
                {
                    m_groupEnabled |= true;
                }
                m_filterChangeSubscribers.send();
            }
        }
    }

    /**
     * Checks if the FilterGroup is enabled.
     * If a FilterGroup is disabled, none of its enabled filter will filter any item.
     *
     * @return True if FilterGroup is enabled.
     */
    bool isFilterGroupEnabled() const
    {
        return m_groupEnabled;
    }

    /**
     * Enabled or disable the FilterGroup
     *
     * @param enabled True to enable the FilterGroup. False to disable the FilterGroup.
     */
    void setFilterGroupEnabled(bool enabled)
    {
        if (m_groupEnabled != enabled)
        {
            m_groupEnabled = enabled;
            m_filterChangeSubscribers.send();
        }
    }

    /**
     * Checks if any of the filter in the FilterGroup is enabled.
     *
     * @return True if at least one filter in the FilterGroup is enabled.
     */
    bool isAnyFilterEnabled() const
    {
        return m_enabledCount > 0;
    }

    /**
     * Remove all filters in the group.
     */
    void clear()
    {
        m_filters.clear();
        m_enabledCount = 0;
        m_groupEnabled = false;
        m_filterChangeSubscribers.send();
    }

    /**
     * Subscribes to filter change event.
     *
     * @param onFilterEvent The function to be called when filter has changed.
     * @return SubscriptionId to be used when unsubscribe from filter event.
     */
    SubscriptionId subscribeForFilterEvent(const OnFilterChangedFn& onFilterEvent)
    {
        // Since we're using std::function, userData is not needed anymore.
        return m_filterChangeSubscribers.subscribe([onFilterEvent](void*) { onFilterEvent(); }, nullptr);
    }

    /**
     * Unsubscribe from filter change event.
     *
     * @param subId the SubscriptionId obtain when calling @ref subscribeForFilterEvent.
     */
    void unsubscribeFromFilterEvent(SubscriptionId subId)
    {
        m_filterChangeSubscribers.unsubscribe(subId);
    }

private:
    using OnFilterChangedInternalFn = std::function<void(void*)>;

    struct FilterData
    {
        FilterT filter;
        bool enabled;
    };

    bool m_groupEnabled = false;
    Pred m_pred;
    std::map<std::string, FilterData> m_filters;
    size_t m_enabledCount = 0;
    carb::EventSubscribers<OnFilterChangedInternalFn, SubscriptionId> m_filterChangeSubscribers;
};

/**
 * Defines a FilterGroup that tests string against regular expression.
 */
struct RegexPred
{
    bool operator()(const std::string& str, const std::regex& regex) const
    {
        return std::regex_search(str, regex);
    }
};
using RegexFilterGroup = FilterGroup<std::string, std::regex, RegexPred>;
}
}
