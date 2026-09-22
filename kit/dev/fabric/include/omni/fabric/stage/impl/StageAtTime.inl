// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

namespace omni
{
namespace fabric
{
/**
 * @brief Linear interpolation for carb types Double3, Float3, Float4 (color)
 *        See InterpolationUsd.h for extended type support
 *
 * @details This is intended to be used internally by StageAtTime read methods in order
 *          to calculate values that were not written by StageReaderWriter directly.
 *
 *          Enables the decoupling of the sim and render threads by allowing them access
 *          to ringbuffer values at various frequencies.
 */
template <typename T>
const T interpolate(const T& a, const T& b, float theta)
{
    T result = T(a * (1.0f - theta)) + T(b * theta);
    return result;
    // T result = std::lerp(a, b, theta);
}

template <>
inline const carb::Double3 interpolate(const carb::Double3& a, const carb::Double3& b, float theta)
{
    if (theta < 0.0 || theta > 1.0)
    {
        CARB_LOG_WARN_ONCE("WrapperImpl interpolate(): theta %f outside range [0.0, 1.0]", theta);
    }

    carb::Double3 result;
    double tmp = 1.0 - theta;
    result.x = (a.x * tmp) + (b.x * theta);
    result.y = (a.y * tmp) + (b.y * theta);
    result.z = (a.z * tmp) + (b.z * theta);
    return result;
}


template <>
inline const carb::Float3 interpolate(const carb::Float3& a, const carb::Float3& b, float theta)
{
    if (theta < 0.0f || theta > 1.0f)
    {
        CARB_LOG_WARN_ONCE("WrapperImpl interpolate(): theta %f outside range [0.0, 1.0]", theta);
    }

    carb::Float3 result;
    float tmp = 1.0f - theta;
    result.x = (a.x * tmp) + (b.x * theta);
    result.y = (a.y * tmp) + (b.y * theta);
    result.z = (a.z * tmp) + (b.z * theta);
    return result;
}

template <>
inline const carb::Float4 interpolate(const carb::Float4& a, const carb::Float4& b, float theta)
{
    if (theta < 0.0f || theta > 1.0f)
    {
        CARB_LOG_WARN_ONCE("WrapperImpl interpolate(): theta %f outside range [0.0, 1.0]", theta);
    }

    carb::Float4 result;
    float tmp = 1.0f - theta;
    result.x = (a.x * tmp) + (b.x * theta);
    result.y = (a.y * tmp) + (b.y * theta);
    result.z = (a.z * tmp) + (b.z * theta);
    result.w = (a.w * tmp) + (b.w * theta);
    return result;
}

template <>
inline const omni::fabric::TokenC interpolate(const omni::fabric::TokenC& a, const omni::fabric::TokenC& b, float theta)
{
    if (theta < 0.0f || theta > 1.0f)
    {
        CARB_LOG_WARN_ONCE("WrapperImpl interpolate(): theta %f outside range [0.0, 1.0]", theta);
    }

    return theta < 0.5f ? a : b;
}

// Auxiliary function used when handling data that is not going to be interpolated (bool, string, int, uint)
// Returns pair of values from first and second sampled frame, or the value found and nullptr if data is only available
// in one frame
template <typename T>
inline optional<std::pair<optional<T>, optional<T>>> StageAtTime::getNonInterpolatableAttributeRd(const Path& path,
                                                                                                  const Token& attrName) const
{
    auto rawSamples = m_historyWindow.getAttributeRd<T>(path, attrName);
    std::vector<FabricTime> sampleTimes = m_historyWindow.getTimestamps();

    if (rawSamples.size() != sampleTimes.size())
    {
        return carb::cpp::nullopt;
    }

    // checking that if the rawSamples are not empty, we have something valid in rawSamples[0]
    CARB_ASSERT(rawSamples.empty() || rawSamples[0]);

    // Communicate zero samples found
    if (rawSamples.empty() || !rawSamples[0])
    {
        return carb::cpp::nullopt;
    }

    if (rawSamples.size() == 1)
    {
        std::pair<carb::cpp::optional<T>, carb::cpp::optional<T>> result(*rawSamples[0], carb::cpp::nullopt);
        return result;
    }
    else if ((rawSamples.size() >= 2) && rawSamples[m_maxSampleIdx])
    {
        std::pair<carb::cpp::optional<T>, carb::cpp::optional<T>> result(*rawSamples[m_minSampleIdx], *rawSamples[m_maxSampleIdx]);
        return result;
    }
    return carb::cpp::nullopt;
}


// StageAtTime implementation starts here
// This is defined here rather than in Carbonite plugin to allow use of templates and inlining

inline ValidMirrors StageAtTime::getAttributeValidBits(const PathC& path, const TokenC& attrName) const
{
    return m_historyWindow.getAttributeValidBits(path, attrName);
}
// The method reports interpolatable data types, and is specialized as optional<pair<optional<T>,optional<T>
// in order to report non-interpolatable data types as encountered in either or both samples
template <typename T>
inline optional<T> StageAtTime::getAttributeRd(const Path& path, const Token& attrName) const
{
    auto rawSamples = m_historyWindow.getAttributeRd<T>(path, attrName);

    // Communicate zero samples found
    if (rawSamples.size() == 0)
    {
        return carb::cpp::nullopt;
    }

    if (rawSamples.size() == 1)
    {
        CARB_ASSERT(rawSamples[0]);

        return *rawSamples[0];
    }
    else if (rawSamples.size() >= 2)
    {
        CARB_ASSERT(rawSamples[m_minSampleIdx]);
        CARB_ASSERT(rawSamples[m_maxSampleIdx]);

        // Calculate linear approximation of f(time)
        T a_f = *rawSamples[m_minSampleIdx];
        T b_f = *rawSamples[m_maxSampleIdx];

        return interpolate(a_f, b_f, (float)m_theta);
    }

    return carb::cpp::nullopt;
}

// The following functions are marked for deletion since the specified types cannot be interpolated
// StageAtTime reports the non-interpolatable types read from Fabric as a pair<optional<T>, optional<T>>
template <>
inline optional<bool> StageAtTime::getAttributeRd(const Path& path, const Token& attrName) const = delete;

template <>
inline optional<int> StageAtTime::getAttributeRd(const Path& path, const Token& attrName) const = delete;

template <>
inline optional<unsigned int> StageAtTime::getAttributeRd(const Path& path, const Token& attrName) const = delete;

template <>
inline optional<unsigned char> StageAtTime::getAttributeRd(const Path& path, const Token& attrName) const = delete;

template <>
inline optional<int64_t> StageAtTime::getAttributeRd(const Path& path, const Token& attrName) const = delete;

template <>
inline optional<uint64_t> StageAtTime::getAttributeRd(const Path& path, const Token& attrName) const = delete;

template <>
inline optional<omni::fabric::Token> StageAtTime::getAttributeRd(const Path& path, const Token& attrName) const = delete;

// Specialize StageAtTime::getAttributeRd for non-interpolatable types: bool, int, uint
// In these cases the returned type will be a pair of values from the samples found, or nullopt otherwise
template <>
inline optional<std::pair<optional<bool>, optional<bool>>> StageAtTime::getAttributeRd(const Path& path,
                                                                                       const Token& attrName) const
{
    auto result = getNonInterpolatableAttributeRd<bool>(path, attrName);
    return result;
}

template <>
inline optional<std::pair<optional<int>, optional<int>>> StageAtTime::getAttributeRd(const Path& path,
                                                                                     const Token& attrName) const
{
    return getNonInterpolatableAttributeRd<int>(path, attrName);
}

template <>
inline optional<std::pair<optional<unsigned int>, optional<unsigned int>>> StageAtTime::getAttributeRd(
    const Path& path, const Token& attrName) const
{
    return getNonInterpolatableAttributeRd<unsigned int>(path, attrName);
}

template <>
inline optional<std::pair<optional<unsigned char>, optional<unsigned char>>> StageAtTime::getAttributeRd(
    const Path& path, const Token& attrName) const
{
    return getNonInterpolatableAttributeRd<unsigned char>(path, attrName);
}

template <>
inline optional<std::pair<optional<int64_t>, optional<int64_t>>> StageAtTime::getAttributeRd(const Path& path,
                                                                                             const Token& attrName) const
{
    return getNonInterpolatableAttributeRd<int64_t>(path, attrName);
}

template <>
inline optional<std::pair<optional<uint64_t>, optional<uint64_t>>> StageAtTime::getAttributeRd(const Path& path,
                                                                                               const Token& attrName) const
{
    return getNonInterpolatableAttributeRd<uint64_t>(path, attrName);
}

template <>
inline optional<std::pair<optional<TokenC>, optional<TokenC>>> StageAtTime::getAttributeRd(
    const Path& path, const Token& attrName) const
{
    return getNonInterpolatableAttributeRd<TokenC>(path, attrName);
}

template <typename T>
const T* StageAtTime::getAttributeRdGpu(const Path& path, const Token& attrName) const
{
    auto rawSamples = m_historyWindow.getAttributeRdGpu<T>(path, attrName);
    std::vector<FabricTime> sampleTimes = m_historyWindow.getTimestamps();

    CARB_ASSERT(rawSamples.size() == sampleTimes.size());

    // This API doesn't have a way to communicate zero samples found
    CARB_ASSERT(rawSamples.size() != 0);

    if (rawSamples.size() == 1)
    {
        CARB_ASSERT(rawSamples[0]);
        return rawSamples[0];
    }
    else if (rawSamples.size() >= 2)
    {
        // For GPU types there is no support for interpolation yet
        // Return first sample value instead for now
        CARB_LOG_WARN_ONCE(
            "Support for interpolation of array attributes is not supported yet, returning first time sample instead!");
        CARB_ASSERT(rawSamples[m_minSampleIdx]);
        return rawSamples[m_minSampleIdx];
    }
    return nullptr;
}

inline size_t StageAtTime::getArrayAttributeSize(const Path& path, const Token& attrName) const
{
    auto rawSamples = m_historyWindow.getArrayAttributeSize(path, attrName);
    std::vector<FabricTime> sampleTimes = m_historyWindow.getTimestamps();

    CARB_ASSERT(rawSamples.size() == sampleTimes.size());

    // This API doesn't have a way to communicate zero samples found
    CARB_ASSERT(rawSamples.size() != 0);

    if (rawSamples.size() == 1)
    {
        return rawSamples[0];
    }
    else if (rawSamples.size() >= 2)
    {
        // For GPU types there is no support for interpolation yet
        // Return first sample value instead for now
        return rawSamples[m_minSampleIdx];
    }
    return 0;
}

template <typename T>
inline gsl::span<const T> StageAtTime::getArrayAttributeRd(const Path& path, const Token& attrName) const
{
    std::vector<gsl::span<const T>> rawSamples = m_historyWindow.getArrayAttributeRd<T>(path, attrName);
    std::vector<FabricTime> sampleTimes = m_historyWindow.getTimestamps();

    CARB_ASSERT(rawSamples.size() == sampleTimes.size());

    // This API doesn't have a way to communicate zero samples found
    CARB_ASSERT(rawSamples.size() != 0);

    if (rawSamples.size() == 1)
    {
        return rawSamples[0];
    }
    else if (rawSamples.size() >= 2)
    {
        // For array types there is no support for interpolation yet
        // Return first sample value instead for now
        CARB_LOG_WARN_ONCE(
            "Support for interpolation of array attributes is not supported yet, returning first time sample instead!");
        return rawSamples[m_minSampleIdx];
    }
    return gsl::span<const T>();
}


/**
 * @brief Auxiliary function used by AttributeArrayResult<T> and AttributeArrayResult<std::vector<T>>
 *
 * @details Used to assess if a prim is present in both of the sampled frames
 */
inline bool checkPathCorrespondence(std::vector<gsl::span<const omni::fabric::Path>> paths,
                                    size_t index,
                                    size_t& pos_f0,
                                    size_t& pos_f1)
{
    if (paths.size() > 1)
    {
        // in the common case, the prim exists in both frames
        if ((index < paths[1].size()) && (paths[0][index] == paths[1][index]))
        {
            pos_f0 = pos_f1 = index;
            return true;
        }

        auto pathIt = std::find(paths[1].begin(), paths[1].end(), paths[0][index]);
        if (pathIt != paths[1].end())
        {
            pos_f0 = index; // TODO: this isn't needed, can infer it
            pos_f1 = std::distance(paths[1].begin(), pathIt);

            return true;
        }
    }

    return false;
}


/**
 * @brief Returned by StageAtTime.getAttributeArrayRd
 *
 * @details Holds at most two samples (one from frame n, and one from frame n+1)
 *          checkPathCorrespondence verifies if the path in frame n exists in frame n+1
 *          If no corresponding path exists, the value will be returned and not interpolated
 */
template <typename T>
class AttributeArrayResult
{
public:
    size_t size() const
    {
        return m_samples[0].size();
    }

    bool empty() const
    {
        return (size() == 0);
    }

    std::vector<gsl::span<const T>> const* data() const
    {
        return &m_samples;
    }

    std::vector<gsl::span<const T>>* data()
    {
        return &m_samples;
    }

    T operator[](const size_t valueIndex) const
    {
        {
            if (valueIndex >= m_samples[0].size() || m_samples[0].empty())
            {
                CARB_LOG_WARN_ONCE("AttributeArrayResult[] out of bounds");
                return T();
            }

            if (m_samples.size() == 1)
            {
                return m_samples[0][valueIndex];
            }
            else if (m_samples.size() >= 2)
            {
                size_t pos0, pos1;
                if (checkPathCorrespondence(m_paths, valueIndex, pos0, pos1))
                {
                    T a = (m_samples[m_minSampleIdx][pos0]);
                    T b = (m_samples[m_maxSampleIdx][pos1]);

                    T result = interpolate<T>(a, b, m_theta);

                    return result;
                }

                return m_samples[0][valueIndex];
            }
        }

        return T();
    };

    std::vector<gsl::span<const omni::fabric::Path>> m_paths;
    std::vector<gsl::span<const T>> m_samples;
    float m_theta;
    size_t m_minSampleIdx;
    size_t m_maxSampleIdx;
};

/**
 * @brief Returned by StageAtTime.getArrayAttributeArrayRd
 *
 * @details Enables access to a vector of readily interpolated attribute values
 */
template <typename T>
class AttributeArrayResult<std::vector<T>>
{
public:
    size_t size() const
    {
        return m_samples[0].size();
    }

    bool empty() const
    {
        return (size() == 0);
    }

    std::vector<std::vector<gsl::span<const T>>> const* data() const
    {
        return m_samples;
    }

    std::vector<std::vector<gsl::span<const T>>>* data()
    {
        return m_samples;
    }

    std::vector<T> operator[](const size_t primIndex)
    {
        std::vector<T> interpolatedAttributeValues;

        if (m_samples.size() == 1)
        {
            interpolatedAttributeValues.resize(m_samples[0][primIndex].size());
            std::copy(
                m_samples[0][primIndex].begin(), m_samples[0][primIndex].end(), interpolatedAttributeValues.begin());

            return interpolatedAttributeValues;
        }
        else if (m_samples.size() >= 2)
        {
            size_t pos0, pos1;
            if (checkPathCorrespondence(m_paths, primIndex, pos0, pos1))
            {
                auto values_f0 = m_samples[m_minSampleIdx][primIndex];
                auto values_f1 = m_samples[m_maxSampleIdx][primIndex];

                interpolatedAttributeValues.reserve(values_f0.size());

                // interpolate attrib values for the requested {prim index : attrib val index}
                for (size_t valueIndex = 0; valueIndex < values_f0.size(); ++valueIndex)
                {
                    T a = (values_f0[valueIndex]);
                    T b = (values_f1[valueIndex]);
                    T result = interpolate<T>(a, b, m_theta);
                    interpolatedAttributeValues.emplace_back(result);
                }

                return interpolatedAttributeValues;
            }

            interpolatedAttributeValues.resize(m_samples[0][primIndex].size());
            std::copy(
                m_samples[0][primIndex].begin(), m_samples[0][primIndex].end(), interpolatedAttributeValues.begin());

            return interpolatedAttributeValues;
        }
        return std::vector<T>();
    }

    std::vector<gsl::span<const omni::fabric::Path>> m_paths;
    std::vector<std::vector<gsl::span<const T>>> m_samples;
    float m_theta;
    size_t m_minSampleIdx;
    size_t m_maxSampleIdx;
};

template <typename T>
AttributeArrayResult<T> StageAtTime::getAttributeArrayRd(const PrimBucketList& primBucketList,
                                                         size_t primBucketListIndex,
                                                         const Token& attrName) const
{
    size_t sampleCount = m_historyWindow.getTimeSampleCount();

    if (sampleCount > 0)
    {
        AttributeArrayResult<T> arrAttRes;
        arrAttRes.m_samples = m_historyWindow.getAttributeArrayRd<T>(primBucketList, primBucketListIndex, attrName);
        arrAttRes.m_paths = m_historyWindow.getPathArray(primBucketList, primBucketListIndex);

        arrAttRes.m_theta = (float)m_theta;
        arrAttRes.m_minSampleIdx = m_minSampleIdx;
        arrAttRes.m_maxSampleIdx = m_maxSampleIdx;

        return arrAttRes;
    }
    else
    {
        CARB_LOG_WARN_ONCE(
            "getAttributeArrayRd %s: Data not available at time, possible dropped frame", attrName.getText());
        return AttributeArrayResult<T>();
    }
}

template <typename T>
AttributeArrayResult<T> StageAtTime::getAttributeArrayRdGpu(const PrimBucketList& primBucketList,
                                                            size_t primBucketListIndex,
                                                            const Token& attrName) const
{
    size_t sampleCount = m_historyWindow.getTimeSampleCount();

    if (sampleCount > 0)
    {
        AttributeArrayResult<T> arrAttRes;
        arrAttRes.m_samples = m_historyWindow.getAttributeArrayRdGpu<T>(primBucketList, primBucketListIndex, attrName);
        arrAttRes.m_paths = m_historyWindow.getPathArray(primBucketList, primBucketListIndex);

        arrAttRes.m_theta = (float)m_theta;
        arrAttRes.m_minSampleIdx = m_minSampleIdx;
        arrAttRes.m_maxSampleIdx = m_maxSampleIdx;

        return arrAttRes;
    }
    else
    {
        CARB_LOG_WARN_ONCE(
            "getAttributeArrayRdGpu %s: Data not available at time, possible dropped frame", attrName.getText());
        return AttributeArrayResult<T>();
    }
}

inline std::vector<gsl::span<const char>> StageAtTime::getAttributeArrayRawRd(const PrimBucketList& primBucketList,
                                                                              size_t primBucketListIndex,
                                                                              const Token& attrName) const
{
    return m_historyWindow.getAttributeArrayRawRd(primBucketList, primBucketListIndex, attrName);
}


template <typename T>
AttributeArrayResult<std::vector<T>> StageAtTime::getArrayAttributeArrayRd(const PrimBucketList& primBucketList,
                                                                           size_t primBucketListIndex,
                                                                           const Token& attrName) const
{
    size_t sampleCount = m_historyWindow.getTimeSampleCount();
    AttributeArrayResult<std::vector<T>> result;

    if (sampleCount > 0)
    {
        result.m_samples = m_historyWindow.getArrayAttributeArrayRd<T>(primBucketList, primBucketListIndex, attrName);
        result.m_paths = m_historyWindow.getPathArray(primBucketList, primBucketListIndex);
        result.m_theta = (float)m_theta;
        result.m_minSampleIdx = m_minSampleIdx;
        result.m_maxSampleIdx = m_maxSampleIdx;

        return result;
    }
    else
    {
        CARB_LOG_WARN_ONCE(
            "getAttributeArrayRd %s: Data not available at time, possible dropped frame", attrName.getText());
        return AttributeArrayResult<std::vector<T>>();
    }
}

inline gsl::span<const Path> StageAtTime::getPathArray(const PrimBucketList& primBucketList,
                                                       size_t primBucketListIndex) const
{
    size_t sampleCount = m_historyWindow.getTimeSampleCount();

    if (sampleCount == 1)
    {
        return m_historyWindow.getPathArray(primBucketList, primBucketListIndex)[0];
    }
    else if (sampleCount == 0)
    {
        CARB_LOG_WARN_ONCE("getPathArray: Data not available at time, possible dropped frame");
        return gsl::span<const Path>();
    }
    else if (sampleCount >= 2)
    {
        // TODO: make this correct when prims are being added and deleted
        // To do this we need to make a new array out:
        //    out[i] = in0[i]            , if in0[i] == in1[i]
        //           = kUninitializedPath, otherwise
        return m_historyWindow.getPathArray(primBucketList, primBucketListIndex)[m_minSampleIdx];
#if 0
        gsl::span<const Path> in0 = m_historyWindow.getPathArray(primBucketList, primBucketListIndex)[0];
        gsl::span<const Path> in1 = m_historyWindow.getPathArray(primBucketList, primBucketListIndex)[1];
        std::vector<Path> multiframePaths;

        for (size_t i = 0; i < in0.size(); ++i)
            in0[i] == in1[i] ? multiframePaths.emplace_back(in0[i]) : multiframePaths.emplace_back(fabric::kUninitializedPath);

        return multiframePaths;
#endif
    }

    return gsl::span<const Path>();
}

inline std::vector<const Connection*> StageAtTime::getConnectionRd(const Path& path, const Token& connectionName)
{
    return m_historyWindow.getConnectionRd(path, connectionName);
}

inline void StageAtTime::printBucketNames() const
{
    m_historyWindow.printBucketNames();
}

inline size_t StageAtTime::getAttributeCount(const PrimBucketList& primBucketList, size_t primBucketListIndex) const
{
    std::vector<size_t> counts = m_historyWindow.getAttributeCounts(primBucketList, primBucketListIndex);
    if (counts.size() == 1)
    {
        return counts[0];
    }
    // Perform a set intersection to get a valid count size;
    if (counts.size() >= 2)
    {
        //
        // TODO: The attributes are internally sorted vectors, see omni::fabric::set.
        // Ideally we'd make a C-ABI type that makes it clear that these are sorted,
        // wrap with omni::fabric::set in the C++ wrapper and then use the standard library set intersection.
        //
        auto namesAndTypes = m_historyWindow.getAttributeNamesAndTypes(primBucketList, primBucketListIndex);
        const std::vector<std::vector<Token>>& names = namesAndTypes.first;
        const std::vector<std::vector<Type>>& types = namesAndTypes.second;
        std::vector<Token> intersection;

        // Perform a set intersection but we need to track the types as we intersect
        const std::vector<Token>& workingNames = names[m_minSampleIdx].size() < names[m_maxSampleIdx].size() ? names[m_minSampleIdx] : names[m_maxSampleIdx];
        const std::vector<Type>& workingTypes = names[m_minSampleIdx].size() < names[m_maxSampleIdx].size() ? types[m_minSampleIdx] : types[m_maxSampleIdx];
        const std::vector<Token>& testingNames = names[m_minSampleIdx].size() < names[m_maxSampleIdx].size() ? names[m_maxSampleIdx] : names[m_minSampleIdx];
        const std::vector<Type>& testingTypes = names[m_minSampleIdx].size() < names[m_maxSampleIdx].size() ? types[m_maxSampleIdx] : types[m_minSampleIdx];

        // Since attribute vectors are sorted we can track last spotted locations to be more efficient.
        size_t last = 0;
        for (size_t i = 0; i < workingNames.size(); ++i)
        {
            for (size_t j = last; j < testingNames.size(); ++j)
            {
                if (workingNames[i] == testingNames[j])
                {
                    if (workingTypes[i] == testingTypes[j])
                    {
                        intersection.push_back(workingNames[i]);
                    }
                    // Store hit location to start next search
                    last = j;
                    break;
                }
            }
        }
        return intersection.size();
    }
    return 0;
}

inline std::pair<std::vector<Token>, std::vector<Type>> StageAtTime::getAttributeNamesAndTypes(
    const PrimBucketList& primBucketList, size_t primBucketListIndex) const
{
    std::vector<Token> outNames;
    std::vector<Type> outTypes;

    std::vector<std::vector<Token>> names;
    std::vector<std::vector<Type>> types;

    std::tie(names, types) = m_historyWindow.getAttributeNamesAndTypes(primBucketList, primBucketListIndex);
    if (names.size() == 1)
    {
        outNames = std::move(names[0]);
        outTypes = std::move(types[0]);
    }
    if (names.size() >= 2)
    {
        // Assuming that the invariant that names and types of the same slot are the same count holds.
        outNames.reserve(std::min(names[m_minSampleIdx].size(), names[m_maxSampleIdx].size()));
        outTypes.reserve(std::min(types[m_minSampleIdx].size(), types[m_maxSampleIdx].size()));

        // Perform a set intersection but we need to track the types as we intersect
        std::vector<Token>& workingNames = names[m_minSampleIdx].size() < names[m_maxSampleIdx].size() ? names[m_minSampleIdx] : names[m_maxSampleIdx];
        std::vector<Type>& workingTypes = names[m_minSampleIdx].size() < names[m_maxSampleIdx].size() ? types[m_minSampleIdx] : types[m_maxSampleIdx];
        std::vector<Token>& testingNames = names[m_minSampleIdx].size() < names[m_maxSampleIdx].size() ? names[m_maxSampleIdx] : names[m_minSampleIdx];
        std::vector<Type>& testingTypes = names[m_minSampleIdx].size() < names[m_maxSampleIdx].size() ? types[m_maxSampleIdx] : types[m_minSampleIdx];

        // Since attribute vectors are sorted we can track last spotted locations to be more efficient.
        size_t last = 0;
        for (size_t i = 0; i < workingNames.size(); ++i)
        {
            for (size_t j = last; j < testingNames.size(); ++j)
            {
                if (workingNames[i] == testingNames[j])
                {
                    if (workingTypes[i] == testingTypes[j])
                    {
                        outNames.push_back(workingNames[i]);
                        outTypes.push_back(workingTypes[i]);
                    }
                    // Store hit location to start next search
                    last = j;
                    break;
                }
            }
        }
    }
    return { outNames, outTypes };
}


inline uint64_t StageAtTime::writeCacheToDisk(const char* file, uint8_t* workingBuffer, uint64_t workingBufferSize) const
{
    size_t sampleCount = m_historyWindow.getTimeSampleCount();

    if (sampleCount != 1)
    {
        CARB_LOG_ERROR_ONCE("Can't call StageAtTime::WriteCacheToDisk for interpolated values");
        return 0;
    }

    return m_historyWindow.writeCacheToDisk(file, workingBuffer, workingBufferSize);
}

inline void StageAtTime::addRefCount()
{
    m_historyWindow.addRefCount();
}

inline bool StageAtTime::removeRefCount()
{
    return m_historyWindow.removeRefCount();
}

inline unsigned int StageAtTime::getRefCount()
{
    return m_historyWindow.getRefCount();
}

// Dummy function to force template instatiation at least once to get compiler checking
inline void DONOTCALL_instantiateST(const StageAtTime& st,
                                      const Path& path,
                                      const Token& attrName,
                                      const PrimBucketList& pbl)
{
    optional<std::pair<optional<int>, optional<int>>> out1 = st.getNonInterpolatableAttributeRd<int>(path, attrName);
    CARB_UNUSED(out1);
    optional<float> out2 = st.getAttributeRd<float>(path, attrName);
    CARB_UNUSED(out2);
    const float* out3 = st.getAttributeRdGpu<float>(path, attrName);
    CARB_UNUSED(out3);
    gsl::span<const float> out4 = st.getArrayAttributeRd<float>(path, attrName);
    CARB_UNUSED(out4);
    AttributeArrayResult<float> out5 = st.getAttributeArrayRdGpu<float>(pbl, 0, attrName);
    CARB_UNUSED(out5);
    AttributeArrayResult<std::vector<float>> out6 = st.getArrayAttributeArrayRd<float>(pbl, 0, attrName);
    CARB_UNUSED(out6);
}

} // namespace fabric
} // namespace omni
