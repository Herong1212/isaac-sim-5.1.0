// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file usdrt/scenegraph/usd/rt/changeTracker.h
//!
//! @brief Provides RtChangeTracker class, for tracking changes in Fabric

#include <gsl/span>
#include <omni/fabric/SimStageWithHistory.h>
#include <omni/fabric/stage/interface/IChangeTrackingConfig.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/usd/usd/prim.h>

namespace usdrt
{

//! The RtChangeTracker class provides an interface for tracking changes to Fabric data.
//! Unlike TfNotice (USD's built in notification system), RtChangeTracker and Fabric
//! handle change notifications in a non-blocking manner.
//!
//! RTChangeTracker leverages Fabric's change tracking capabilities, while abstracting out
//! the underlying bucket-based details. It also adds helper methods for querying changes
//! in the data by prim and attribute.
//!
class RtChangeTracker
{
public:
    //! Construct an RtChangeTracker instance from a USD stage reference
    //!
    //! @param stage The stage you want to track changes in
    RtChangeTracker(UsdStageRefPtr stage);

    //! Destructor
    ~RtChangeTracker();

    //! Start tracking an attribute
    //!
    //! @param attrName The name of the attribute to track
    void TrackAttribute(TfToken attrName);

    //! Stop tracking an attribute
    //!
    //! @param attrName The name of the attribute to stop tracking
    void StopTrackingAttribute(TfToken attrName);

    //! Pauses change tracking
    void PauseTracking();

    //! Resumes paused change tracking
    void ResumeTracking();

    //! Check if change tracking is paused
    //!
    //! @returns true if change tracking is paused
    bool IsChangeTrackingPaused();

    //! Check if there are any tracked changes
    //!
    //! @returns true if there are tracked changes
    bool HasChanges();

    //! Clear out any tracked changes
    void ClearChanges();

    //! Enable tracking added prims
    void EnablePrimCreateTracking();

    //! Get list of all prims with changes
    //!
    //! @returns list of SdfPaths of all prims with changes
    std::vector<SdfPath> GetAllChangedPrims();

    //! Get list of all newly-created prims in fabric.
    //!
    //! @returns a list of SdfPaths of all newly-added prims.
    std::vector<SdfPath> GetAddedPrims();

    //! Get list of all prim & attribute combos that have changed
    //!
    //! @returns list of full SdfPaths of all attributes with changes
    std::vector<SdfPath> GetAllChangedAttributes();

    //! Check for changes on a given prim
    //!
    //! @param prim prim to check for changes
    //! @returns true if prim has tracked changes
    bool PrimChanged(UsdPrim prim);

    //! Check for changes on a given prim
    //!
    //! @param primPath path to prim to check for changes
    //! @returns true if prim has tracked changes
    bool PrimChanged(SdfPath primPath);

    //! Check for changes on a specific attribute of a prim
    //!
    //! @param attr prim attribute to check for changes
    //! @returns true if attribute has tracked changes
    bool AttributeChanged(UsdAttribute attr);

    //! Check for changes on a specific attribute of a prim
    //!
    //! @param attrPath path to attribute on a prim to check for changes
    //! @returns true if attribute has tracked changes
    bool AttributeChanged(SdfPath attrPath);

    //! Get list of attributes that have changed for given prim
    //!
    //! @param prim prim to check for changes
    //! @returns list of attributes with changes
    std::vector<TfToken> GetChangedAttributes(UsdPrim prim);

    //! Get list of attributes that have changed for a given prim
    //!
    //! @param primPath path to prim to check for changes
    //! @returns list of attributes with changes
    std::vector<TfToken> GetChangedAttributes(SdfPath primPath);

    //! Check if an attribute is being tracked
    //!
    //! @param attrName name of the attribute to check
    //! @returns true if attribute is being tracked
    bool IsTrackingAttribute(TfToken attrName);

    //! Get list of all currently tracked attributes
    //!
    //! @returns list of tracked attribute names
    std::vector<TfToken> GetTrackedAttributes();


private:
    omni::fabric::ListenerId m_listener;
    omni::fabric::StageReaderWriter m_stage;
    UsdStageRefPtr m_usdStageRef;

    // The list of tracked attributes isn't exposed in Fabric, so keeping track of them here (for now)
    // This could also be further optimized into a std::set, but would require implementing < & > on TfToken
    std::vector<TfToken> m_trackedAttrs;
};

inline RtChangeTracker::RtChangeTracker(UsdStageRefPtr stage) : m_usdStageRef(stage)
{
    auto iSimStageWithHistory = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    auto iChangeTracker = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();

    m_stage = omni::fabric::StageReaderWriter(stage->GetStageReaderWriterId());
    m_listener = iChangeTracker->createListener();
}

inline RtChangeTracker::~RtChangeTracker()
{
    m_stage.detachListener(m_listener);
}

inline void RtChangeTracker::TrackAttribute(TfToken attrName)
{
    m_stage.attributeEnableChangeTracking(omni::fabric::TokenC(attrName), m_listener);
    if (!IsTrackingAttribute(attrName))
        m_trackedAttrs.push_back(attrName);
}

inline void RtChangeTracker::StopTrackingAttribute(TfToken attrName)
{
    m_stage.attributeDisableChangeTracking(omni::fabric::TokenC(attrName), m_listener);

    // Safely remove attrName from m_trackedAttrs
    for (auto i = m_trackedAttrs.begin(); i != m_trackedAttrs.end();)
    {
        if (*i == attrName)
            i = m_trackedAttrs.erase(i);
        else
            ++i;
    }
}

inline void RtChangeTracker::PauseTracking()
{
    m_stage.pauseChangeTracking(m_listener);
}

inline void RtChangeTracker::ResumeTracking()
{
    m_stage.resumeChangeTracking(m_listener);
}

inline bool RtChangeTracker::IsChangeTrackingPaused()
{
    return m_stage.isChangeTrackingPaused(m_listener);
}

inline bool RtChangeTracker::HasChanges()
{
    return (m_stage.getChanges(m_listener).size() > 0);
}

inline void RtChangeTracker::ClearChanges()
{
    m_stage.popChanges(m_listener);
}

inline void RtChangeTracker::EnablePrimCreateTracking()
{
    m_stage.enablePrimCreateTracking(m_listener);
}

inline std::vector<SdfPath> RtChangeTracker::GetAllChangedPrims()
{
    std::vector<SdfPath> result;
    ChangedPrimBucketList changeBuckets = m_stage.getChanges(m_listener);

    // Return empty vector if there are no buckets with changes
    if (changeBuckets.size() == 0)
        return result;

    // Iterate through buckets with changes and pull prims into result
    for (size_t i = 0; i < changeBuckets.size(); i++)
    {
        BucketChanges changes = changeBuckets.getChanges(i);

        // For each prim in the bucket, keep track of how many attrs on it have changed
        std::vector<int> perPrimChanges(changes.pathArray.size());
        for (size_t j = 0; j != changes.pathArray.size(); j++)
            perPrimChanges[j] = 0;

        // Iterate through attributes with changes in bucket
        for (auto changeInfo : changes.attrChangedIndices)
        {
            // First check if all prims in bucket have changed (to avoid checking individually)
            if (changeInfo.allIndicesChanged)
            {
                for (size_t k = 0; k != changes.pathArray.size(); k++)
                    perPrimChanges[k]++;
                continue;
            }

            // Then iterate through which indices (prims) in current bucket have change for that attribute
            for (auto index : changeInfo.changedIndices)
                perPrimChanges[index]++;
        }

        // Collect all prims with changes into overall result
        for (size_t k = 0; k != changes.pathArray.size(); k++)
        {
            if (perPrimChanges[k] > 0)
                result.push_back(SdfPath(changes.pathArray[k]));
        }
    }
    return result;
}

inline std::vector<SdfPath> RtChangeTracker::GetAddedPrims()
{
    std::vector<SdfPath> result;
    ChangedPrimBucketList changeBuckets = m_stage.getChanges(m_listener);

    // Return empty vector if there are no buckets with changes
    if (changeBuckets.size() == 0)
        return result;

    // Iterate through buckets with changes and pull prims into result
    for (size_t i = 0; i < changeBuckets.size(); i++)
    {
        AddedPrimIndices addedPrimIndices = changeBuckets.getAddedPrims(i);
        if (addedPrimIndices.size() > 0)
        {
            const BucketChanges changes = changeBuckets.getChanges(i);
            const gsl::span<const Path>& paths = changes.pathArray;
            for (size_t index : addedPrimIndices)
            {
                const auto& pi = paths[index];
                result.push_back(SdfPath(pi));
            }
        }
    }
    return result;
}

inline std::vector<SdfPath> RtChangeTracker::GetAllChangedAttributes()
{
    std::vector<SdfPath> result;
    ChangedPrimBucketList changeBuckets = m_stage.getChanges(m_listener);

    // Return empty vector if there are no buckets with changes
    if (changeBuckets.size() == 0)
        return result;

    // Iterate through buckets with changes and pull prims+attrs into result
    for (size_t i = 0; i < changeBuckets.size(); i++)
    {
        BucketChanges changes = changeBuckets.getChanges(i);

        // Iterate through attributes with changes in bucket
        for (auto changeInfo : changes.attrChangedIndices)
        {
            // First check if all prims in bucket have changed (to avoid checking individually)
            if (changeInfo.allIndicesChanged)
            {
                for (auto path : changes.pathArray)
                {
                    std::string fullPath = path.getText();
                    fullPath += ".";
                    fullPath += changeInfo.attr.name.getText();
                    result.push_back(SdfPath(fullPath));
                }
                continue;
            }

            // Then iterate through which indices (prims) in current bucket have change for that attribute
            for (auto i : changeInfo.changedIndices)
            {
                std::string fullPath = changes.pathArray[i].getText();
                fullPath += ".";
                fullPath += changeInfo.attr.name.getText();
                result.push_back(SdfPath(fullPath));
            }
        }
    }
    return result;
}

inline bool RtChangeTracker::PrimChanged(UsdPrim prim)
{
    return PrimChanged(prim.GetPath());
}

// Developer note: This function is not efficient (looks through all changes to see if a prim has changed) as is.
//                 In theory we should be able to modify fabric's change tracking to make this faster.
inline bool RtChangeTracker::PrimChanged(SdfPath primPath)
{
    ChangedPrimBucketList changeBuckets = m_stage.getChanges(m_listener);

    // The prim did not change if there are no buckets with changes
    if (changeBuckets.size() == 0)
        return false;

    // Iterate through buckets with changes, stop when you find primPath
    for (size_t i = 0; i < changeBuckets.size(); i++)
    {
        BucketChanges changes = changeBuckets.getChanges(i);
        size_t primIndex;
        bool foundPrim = false;

        // Look for prim in current bucket, and note its index if found. This avoids comparing SdfPaths later.
        for (size_t j = 0; j != changes.pathArray.size(); j++)
        {
            if (PathC(primPath) == changes.pathArray[j])
            {
                primIndex = j;
                foundPrim = true;
                break;
            }
        }

        if (foundPrim)
        {
            // Iterate through each attribute with changes in that bucket
            for (auto changeInfo : changes.attrChangedIndices)
            {
                // First check if all prims in bucket have changed for that attr (to avoid checking individually)
                if (changeInfo.allIndicesChanged)
                    return true;

                // Then check for primIndex in list of indices with changes
                bool hasPrimChanged = std::any_of(changeInfo.changedIndices.begin(), changeInfo.changedIndices.end(),
                                                  [&primIndex](const size_t i) { return primIndex == i; });
                if (hasPrimChanged)
                    return true;
            }
            // None of the attributes in the bucket changed for given prim
            return false;
        }
    }
    // Never found prim in buckets
    return false;
}

inline bool RtChangeTracker::AttributeChanged(UsdAttribute attr)
{
    return AttributeChanged(attr.GetPath());
}

inline bool RtChangeTracker::AttributeChanged(SdfPath attrPath)
{
    std::vector<SdfPath> changedAttrs = GetAllChangedAttributes();

    // std::any_of will return true if range given is empty, so check for that case first
    if (changedAttrs.empty())
        return false;

    bool result = std::any_of(
        changedAttrs.begin(), changedAttrs.end(), [&attrPath](const SdfPath& path) { return attrPath == path; });
    return result;
}

inline std::vector<TfToken> RtChangeTracker::GetChangedAttributes(UsdPrim prim)
{
    std::vector<TfToken> result;
    // We can reserve space for result ahead of time bc we know max size (# of attrs on prim)
    result.reserve(prim.GetAttributes().size());

    ChangedPrimBucketList changeBuckets = m_stage.getChanges(m_listener);

    // Return empty vector if there are no buckets with changes
    if (changeBuckets.size() == 0)
        return result;

    // Iterate through buckets until we find one with prim we want
    for (size_t i = 0; i < changeBuckets.size(); i++)
    {
        BucketChanges changes = changeBuckets.getChanges(i);

        // When we find the bucket, collect changed attr information for that prim
        bool primInBucket = std::any_of(changes.pathArray.begin(), changes.pathArray.end(),
                                        [&prim](const omni::fabric::Path& p) { return prim.GetPath() == SdfPath(p); });
        if (primInBucket)
        {
            for (auto changeInfo : changes.attrChangedIndices)
            {
                // First check if all prims in bucket have changed for attribute (to avoid checking individually)
                if (changeInfo.allIndicesChanged)
                {
                    result.push_back(TfToken(changeInfo.attr.name.getString()));
                    continue;
                }
                // Otherwise check for the prim individually
                for (auto changedIndex : changeInfo.changedIndices)
                {
                    if (SdfPath(changes.pathArray[changedIndex]) == prim.GetPath())
                    {
                        result.push_back(TfToken(changeInfo.attr.name));
                        continue;
                    }
                }
            }
        }
    }
    return result;
}

inline std::vector<TfToken> RtChangeTracker::GetChangedAttributes(SdfPath primPath)
{
    return GetChangedAttributes(m_usdStageRef->GetPrimAtPath(primPath));
}

inline bool RtChangeTracker::IsTrackingAttribute(TfToken attrName)
{
    bool result = std::any_of(
        m_trackedAttrs.begin(), m_trackedAttrs.end(), [&attrName](const TfToken& name) { return attrName == name; });
    return result;
}

inline std::vector<TfToken> RtChangeTracker::GetTrackedAttributes()
{
    return m_trackedAttrs;
}

} // namespace usdrt
