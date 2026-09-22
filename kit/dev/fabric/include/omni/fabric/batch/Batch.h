// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// Supporting structs included for customer convenient, even though this translation unit tecnincally only need forward
// declares.
#include <omni/fabric/batch/interface/IBatch.h>
#include <omni/fabric/batch/AttributeHandle.h>
#include <omni/fabric/batch/BatchFilter.h>
#include <omni/fabric/batch/Lambda.h>
#include <omni/fabric/batch/Types.h>

namespace omni
{
namespace fabric
{
namespace batch
{

// Batch (Batch API) is a canonical way to interact with data hosted by Fabric. It is an entirely optional suite of
// tools to aid with common Fabric data integration patterns. It is a general solution that is optimized for maximum
// throughput and minimal overhead. It is not guaranteed to be more efficient than an entirely bespoke solution, but it
// is intended to reach near-peak performance with much less effort.
//
// For detailed discussion on the API, see the public documentation.
class Batch
{
public:
    // == Common interfaces ==
    // Used for both Immediate and Deferred mode

    // Create a Batch instance
    //
    // NOTE: Calling thread assumes ownership of the Batch instance.
    //       Most methods are only available to the thread owner of the Batch instance.
    //       If ownership transfer is necessary, use changeOwnerToCurrentThread
    inline Batch();

    // copy semantics are not currently allowed to protect thread ownership model
    Batch(const Batch&) = delete;
    Batch& operator=(const Batch&) = delete;

    Batch(Batch&&) = default;
    Batch& operator=(Batch&&) = default;

    inline ~Batch();

    inline BatchId getId() const;

    // Changes Batch instance ownership to the calling thread
    // BEWARE! Batch API makes no guarantees about thread safety in doing this.
    // Callers are responsible for thread safety using this advanced feature, please use caution.
    inline void changeOwnerToCurrentThread();


    // == Immediate Mode interfaces ==

    // Generates a View and returns it immediately.
    // View lifetime is tied to Batch instance lifetime.
    // Caller must be the owner of the Batch instance
    inline const struct View& generateView(const omni::fabric::FabricId& fabricId,
                                           const struct BatchFilter& filter,
                                           const ViewGenerationOptions& options = ViewGenerationOptions());

    // LEGACY ORDERING
    inline const struct View& generateView(const omni::fabric::FabricId& fabricId,
                                           const ViewGenerationOptions& options,
                                           const struct BatchFilter& filter);


    // == Deferred Mode interfaces ==

    // Sets BatchPreferences on the Batch instance.
    // Modifies Batch instance user definition.
    // Has no effect until bake() is called.
    // Caller must be the owner of the Batch instance
    inline void setPreferences(const struct BatchPreferences& preferences);

    // Adds FabricId to be used with the Batch instance.
    // Modifies Batch instance user definition.
    // Has no effect until bake() is called.
    // Caller must be the owner of the Batch instance
    inline void addFabricId(const omni::fabric::FabricId& fabricId);

    // Adds Lambda to be used with the Batch instance.
    // Modifies Batch instance user definition.
    // Has no effect until bake() is called.
    // Caller must be the owner of the Batch instance
    inline size_t addLambda(const struct Lambda& lambda);

    // Clears all user definitions, including: preferences, fabric IDs, and Lambdas
    // Modifies Batch instance user definition.
    // Has no effect until bake() is called.
    // Caller must be the owner of the Batch instance
    inline void clear();

    // Bakes all definitions and configurations. Prepares a Batch to be run().
    // The user should call this once per Batch instance after completing all desired user definitions.
    // Incurs no Fabric data side-effects.
    // Caller must be the owner of the Batch instance
    inline void bake();

    // Returns the cpuConcurrencyWidth set at the time of the last bake() call.
    // Caller must be the owner of the Batch instance
    inline size_t cpuConcurrencyWidth() const;

    // Performs necessary setup steps before run()
    // Should be called once, from a single thread, before run().
    // Caller must be the owner of the Batch instance
    // Allocates and returns a BatchRunContextId, for use with run() and variants.
    // Must be paired with runEpilogue using the same BatchRunContextId to bookend all run() calls.
    inline BatchRunContextId runPrologue();

    // Performs necessary teardown steps after run()
    // Should be called once, from a single thread, after run().
    // Caller must be the owner of the Batch instance
    // Must be provided with the same BatchRunContextId returned from runPrologue
    inline void runEpilogue(const BatchRunContextId& contextId);

    // Runs the batch on the current thread.
    // Control returns once all Lambdas have completed executing.
    // Caller may be any thread! Calling threads will attempt to participate, if any queues are available
    inline void run(const BatchRunContextId& contextId);

    // Runs the batch on the current thread, with a hint as to the desiredQueueIndex to start at.
    // This run() variant that optimizes for applications that can map worker threads to concrete queue indices.
    // Prefer to use this over run() if thread->queue mapping can be determined.
    // Control returns once all Lambdas have completed executing.
    // Caller may be any thread! Calling threads will attempt to participate, if any queues are available
    inline void runWithInitialQueueIndex(const BatchRunContextId& contextId, const size_t desiredQueueIndex);

    // Cancels the Batch instance.
    // Cancel granularity is queue-level:
    //   - A queue that is already owned by a thread will run to completion
    //   - A queue that is not owned by a thread will be skipped
    //   - Queue-level cancellation occurs for ALL Lambdas in the Batch
    //
    // This can leave the Batch in a state where a Lambda has partially executed, since one Lambda may
    // be partitioned among multiple Queues.
    // Caller must be the owner of the Batch instance
    inline void cancel();

    // Prints Batch instance internals to carb::logging using info-level logging
    // Caller must be the owner of the Batch instance
    inline void print() const;

    // Marks all generated views as valid, preventing regeneration.
    // Must be called within a runPrologue/runEpilogue section
    // Caller must be the owner of the Batch instance
    //
    // This is an optimization provided for some subset of users. If it can be promised that no topology changes have
    // been made to Fabric data external to the Batch instance, marking generated views as valid reduces runtime costs
    // by amortizing View Generation step across multiple frames.
    inline void markViewsValid();

    // Reports all statistics accumulated.
    // All accumulators will be averaged over <iterations>.
    // Caller must be the owner of the Batch instance
    inline void reportStatistics(const size_t iterations) const;

    // Reports _just_ the current TimerCategory::Run duration, averaged over <iterations>.
    // Caller must be the owner of the Batch instance
    inline void reportRunTime(const size_t iterations) const;

    // Resets all accumulator values.
    // Caller must be the owner of the Batch instance
    inline void resetStatistics();

    // == Developer interfaces ==

    // Sets BatchPreferences on the Batch instance.
    // Modifies Batch instance user definition.
    // Has no effect until bake() is called.
    // Caller must be the owner of the Batch instance
    //
    // Note: clear() does not reset these! applying these are permanent until setDeveloperSettings()+bake() is called
    // again!
    inline void setDeveloperSettings(const struct BatchDeveloperSettings& developer);

    // Returns the computed list of attributes used for the given Lambda index
    // Requires calling bake() first
    //   - "Immediate Mode": bake() is implicitly performed as part of generateView(), so this can be called after the
    //   view is generated at any time with index = 0
    //   - "Deferred Mode": bake() is explicitly required by the user to schedule. Ensure any calls to
    //   getAttributeSpecs() occurs after bake(), otherwise it may return an empty span.
    inline carb::cpp::span<const batch::AttributeSpecification> getAttributeSpecifications(const size_t lambdaIndex);

private:
    omni::fabric::batch::IBatch* const m_interface;
    BatchId m_id;
};

} // namespace batch
} // namespace fabric
} // namespace omni

#include <omni/fabric/batch/impl/Batch.inl>
