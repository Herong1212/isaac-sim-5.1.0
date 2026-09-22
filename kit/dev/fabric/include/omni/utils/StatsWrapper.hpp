// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <regex>
#include <optional>

#include <carb/logging/Log.h>
#include <carb/stats/Stats.h>
#include <carb/metrics/IMetrics.h>
#include <carb/profiler/Profile.h>


namespace omni
{

// Convenience wrappers for create stats (uint64_t/Double values) that can get exported
// to diffent systems (carb::stats, carb::profiler, otel metrics)

// Config for carb::profiler exporting of stats
struct StatsCarbProfilerExport
{
    const carb::profiler::Channel& channel;
};
// Config for otel metricsexporting of stats
struct StatsOtelMetricsExport
{
    // TODO: add telemetry channel?
};
struct StatsScopeOptions
{
    std::optional<StatsCarbProfilerExport> profilerExport = std::nullopt;
    std::optional<StatsOtelMetricsExport> otelExport = StatsOtelMetricsExport{};
};

// StatScopeWrapper:
//  - Wrapper for a stat scope under which stats are groups
class StatScopeWrapper
{
public:
    StatScopeWrapper(const char* name, const char* description, const StatsScopeOptions& options)
        : m_profilerChannel(options.profilerExport.has_value() ? &options.profilerExport.value().channel : nullptr)
        , m_name(name)
    { 
        m_stats = carb::getFramework()->tryAcquireInterface<carb::stats::IStats>();
        if (!m_stats)
        {
            CARB_LOG_INFO("StatScopeWrapper: IStats is not available when creating stats scope: '%s'", name);
            return;
        }
        carb::stats::ScopeDesc scopeDesc = { name, description };
        m_scopeId = m_stats->getOrCreateScope(scopeDesc);

        if (options.otelExport.has_value())
        {
            m_metrics = carb::getCachedInterface<carb::metrics::IMetrics>();
            if (!m_metrics)
            {
                CARB_LOG_INFO("StatScopeWrapper: IMetrics is not available when creating metrics scope: '%s'", name);
            }
            else
            {
                CARB_LOG_VERBOSE("StatWrapper:creating metric scope %s", name);
                m_metricScopeId = m_metrics->getOrCreateScope(name);
            }
        }
    }

    // Simple case of only doing legacy carb::profiler exports
    StatScopeWrapper(const char* name, const char* description, const carb::profiler::Channel& profilerChannel)
        : StatScopeWrapper(name, description, StatsScopeOptions{ StatsCarbProfilerExport{profilerChannel}, std::nullopt })
    {}

    inline carb::profiler::StaticStringType registerProfilerStaticString(const char* str)
    {
        auto prof = carb::profiler::getProfiler();
        return (prof && m_profilerChannel) ? prof->registerStaticString(str) : carb::profiler::kInvalidStaticString;
    }
    template <typename T>
    inline void setProfilerStatValue(const T& value, carb::profiler::StaticStringType valueName)
    {
        auto prof = carb::profiler::getProfiler();
        if (m_profilerChannel && m_profilerChannel->isEnabled() && prof && (valueName != carb::profiler::kInvalidStaticString))
        {
            prof->valueStatic(m_profilerChannel->getMask(), value, valueName);
        }
    }

    carb::stats::IStats* m_stats = nullptr;
    carb::metrics::IMetrics* m_metrics = nullptr;
    carb::stats::ScopeId m_scopeId = 0x0;
    carb::metrics::ScopeId m_metricScopeId = 0x0;
    const carb::profiler::Channel* m_profilerChannel = nullptr;
    const std::string m_name;
};

inline std::string otelifyStatName(const std::string& stat_name)
{
    static const std::regex carb_stats_name_cleaner_pattern("[# :()]"); // remove #, space, colon
    std::string metric_name_clean = std::regex_replace(stat_name, carb_stats_name_cleaner_pattern, "");
    std::transform(metric_name_clean.begin(), metric_name_clean.end(), metric_name_clean.begin(),
                    [](unsigned char c) { return std::tolower(c); });
    return metric_name_clean;
}

// helper to validate metric types
inline bool isValidMetric(carb::metrics::MetricType metric, const std::initializer_list<carb::metrics::MetricType>& validMetrics) 
{
    for (carb::metrics::MetricType m : validMetrics) 
    {
        if (m == metric) 
        {
            return true;
        }
    }
    return false;
}

enum class StatFlags : uint32_t
{
    None = 0x0,
    UseHistogram = 0x1, // use an histogram backend for the exporters that support it
};
inline StatFlags operator|(StatFlags lhs, StatFlags rhs)
{
    return static_cast<StatFlags>(static_cast<std::underlying_type_t<StatFlags>>(lhs) |
                                    static_cast<std::underlying_type_t<StatFlags>>(rhs));
}
inline StatFlags& operator|=(StatFlags& lhs, StatFlags rhs)
{
    lhs = lhs | rhs;
    return lhs;
}
inline StatFlags operator&(StatFlags lhs, StatFlags rhs)
{
    return static_cast<StatFlags>(static_cast<std::underlying_type_t<StatFlags>>(lhs) &
                                    static_cast<std::underlying_type_t<StatFlags>>(rhs));
}
inline StatFlags& operator&=(StatFlags& lhs, StatFlags rhs)
{
    lhs = lhs & rhs;
    return lhs;
}
inline StatFlags operator~(StatFlags val)
{
    return static_cast<StatFlags>(~static_cast<std::underlying_type_t<StatFlags>>(val));
}
inline bool operator!(StatFlags val)
{
    return static_cast<std::underlying_type_t<StatFlags>>(val) == 0;
}
inline bool isFlagSet(StatFlags lhs, StatFlags rhs)
{
    return (lhs & rhs) == rhs;
}

struct StatOptions
{
    const StatFlags flags = StatFlags::None;
    std::optional<carb::metrics::HistogramBucketParams> histogramParams = std::nullopt;
};

// StatWrapper:
// Use to wrap a stat value that gets exported to both carb::stats, carb::profiler and carb::metrics
class StatWrapper
{
public:
    StatWrapper(StatScopeWrapper& scope,
                const char* name,
                const char* description,
                const char* unit,
                carb::stats::StatType type = carb::stats::StatType::eUint64,
                const std::optional<StatOptions>& options = std::nullopt
               )
     : m_scope(scope), m_type(type)
    {
        if (!m_scope.m_stats)
        {
            CARB_LOG_INFO("StatScopeWrapper: IStats is not available when creating stat: '%s'", name);
            return;
        }

        // carb stat
        carb::stats::StatDesc statDesc = { name, description, scope.m_scopeId, type };
        m_statId = m_scope.m_stats->getOrCreateStat(statDesc);

        // carb profiler stas
        m_profilerStat = m_scope.registerProfilerStaticString(name);

        // otel metric
        if (m_scope.m_metrics && m_scope.m_metricScopeId)
        {
            using namespace carb::metrics;
            std::string fullname = otelifyStatName(m_scope.m_name + "." +  std::string(name));

            //Todo: eventually work out some heuristic for units, or add to the StatDesc
            const carb::metrics::MetricType metricType = getMetricType(type, options.has_value() ? options.value().flags : StatFlags::None);
            carb::metrics::MetricDesc metricDesc(fullname.c_str(), description, unit, m_scope.m_metricScopeId, metricType,
                                                 options.has_value() ? options.value().histogramParams : std::nullopt);
            m_metricEntry = m_scope.m_metrics->getOrCreateMetric(metricDesc);
            CARB_LOG_VERBOSE("StatWrapper:created metrics %s id %" PRIu64 "", fullname.c_str(), uint64_t(m_metricEntry.metricId));
        }
    }

    template <typename T>
    inline void setProfilerStatValue(const T& value)
    {
        m_scope.setProfilerStatValue(value, m_profilerStat);
    }

    static carb::metrics::MetricType getMetricType(carb::stats::StatType type, const StatFlags flags)
    {
        using MetricType = carb::metrics::MetricType;
        switch(type)
        {
            // If not using histograms, we have to make them UpDownCounters, as we can't know if the value will increase or decrease
            case carb::stats::StatType::eUint64:
                return isFlagSet(flags, StatFlags::UseHistogram) ? MetricType::IntHistogramMetric : MetricType::IntUpDownCounterMetric;
            case carb::stats::StatType::eDouble:
                return isFlagSet(flags, StatFlags::UseHistogram) ? MetricType::DoubleHistogramMetric : MetricType::DoubleUpDownCounterMetric;
        }
        CARB_CHECK(false);
        return MetricType::IntHistogramMetric;
    }

    StatScopeWrapper& m_scope;
    carb::stats::StatId m_statId{};
    carb::metrics::MetricEntry m_metricEntry{};
    carb::stats::StatType m_type;
    carb::profiler::StaticStringType m_profilerStat = carb::profiler::kInvalidStaticString;
};

// Uint64StatWrapper:
//  - Uint64_t based stat
//  - Note that carb::profile only gets updated with the uint32_t truncated value
class Uint64StatWrapper : public StatWrapper
{
public:
    Uint64StatWrapper(StatScopeWrapper& scope, const char* name, const char* description, const char* unit,
                      const std::optional<StatOptions>& options = std::nullopt)
        : StatWrapper(scope, name, description, unit, carb::stats::StatType::eUint64, options)
    {}

    Uint64StatWrapper& operator+=(uint64_t value)
    {
        if (m_scope.m_stats)
        {
            uint64_t valueBefore = m_scope.m_stats->addStatUint64(m_statId, value);
            setProfilerStatValue(uint32_t(valueBefore + value));

            if (m_metricEntry)
            {
                CARB_LOG_VERBOSE("StatWrapper:+ setting metric id %" PRIu64 " value %" PRIu64 "", uint64_t(m_metricEntry.metricId), value);
                m_scope.m_metrics->addMetricValueInt(m_metricEntry, value);
            }

        }
        return *this;
    }
    Uint64StatWrapper& operator-=(uint64_t value)
    {
        if (m_scope.m_stats)
        {
            uint64_t valueBefore = m_scope.m_stats->subtractStatUint64(m_statId, value);
            setProfilerStatValue(uint32_t(valueBefore - value));
            if (m_metricEntry)
            {
                CARB_LOG_VERBOSE("StatWrapper:- setting metric id %" PRIu64 " value %" PRIu64 "", uint64_t(m_metricEntry.metricId), value);
                m_scope.m_metrics->addMetricValueInt(m_metricEntry, value);
            }
        }
        return *this;
    }
    Uint64StatWrapper& operator=(uint64_t value)
    {
        if (m_scope.m_stats)
        {
            m_scope.m_stats->setStatUint64(m_statId, value);
            setProfilerStatValue(uint32_t(value));
            if (m_metricEntry)
            {
                CARB_LOG_VERBOSE("StatWrapper:= setting metric id %" PRIu64 " value %" PRIu64 "", uint64_t(m_metricEntry.metricId), value);
                m_scope.m_metrics->addMetricValueInt(m_metricEntry, value);
            }
        }
        return *this;
    }
    uint64_t get()
    {
        if (!m_scope.m_stats)
        {
            return 0;
        }

        // TODO: add a better way of doing this by keeping a copy of the stat?
        return m_scope.m_stats->addStatUint64(m_statId, 0);
    }
};

// DoubleStatWrapper:
//  - Double based stat
//  - Note that carb::profile only gets updated with the value converted to a float
class DoubleStatWrapper : public StatWrapper
{
public:
    DoubleStatWrapper(StatScopeWrapper& scope, const char* name, const char* description, const char* unit,
                      const std::optional<StatOptions>& options = std::nullopt)
        : StatWrapper(scope, name, description, unit, carb::stats::StatType::eDouble, options)
    {}
    DoubleStatWrapper& operator=(double value)
    {
        if (m_scope.m_stats)
        {
            m_scope.m_stats->setStatDouble(m_statId, value);
            setProfilerStatValue(float(value));
            if (m_metricEntry)
            {
                CARB_LOG_VERBOSE("StatWrapper:= setting metric id %" PRIu64 " value %f", uint64_t(m_metricEntry.metricId), value);
                m_scope.m_metrics->addMetricValueDouble(m_metricEntry, value);
            }
        }
        return *this;
    }
};

} // namespace omni
