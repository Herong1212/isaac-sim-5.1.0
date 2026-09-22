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
namespace batch
{

Batch::Batch() : m_interface(carb::getCachedInterface<IBatch>())
{
    CARB_ASSERT(m_interface);
    m_id = m_interface->createThreadOwnedBatch();
}

Batch::~Batch()
{
    if (m_interface)
    {
        m_interface->destroyBatch(m_id);
    }
}

BatchId Batch::getId() const
{
    return m_id;
}

void Batch::changeOwnerToCurrentThread()
{
    m_interface->changeOwnerToCurrentThread(m_id);
}

const struct View& Batch::generateView(const omni::fabric::FabricId& fabricId,
                                       const struct BatchFilter& filter,
                                       const ViewGenerationOptions& options)
{
    return m_interface->generateView(m_id, fabricId, options, filter);
}

const struct View& Batch::generateView(const omni::fabric::FabricId& fabricId,
                                       const ViewGenerationOptions& options,
                                       const struct BatchFilter& filter)
{
    return generateView(fabricId, filter, options);
}

void Batch::setPreferences(const struct BatchPreferences& preferences)
{
    m_interface->setPreferences(m_id, preferences);
}

void Batch::addFabricId(const omni::fabric::FabricId& fabricId)
{
    m_interface->addFabricId(m_id, fabricId);
}

size_t Batch::addLambda(const struct Lambda& lambda)
{
    return m_interface->addLambda(m_id, lambda);
}

void Batch::clear()
{
    m_interface->clear(m_id);
}

void Batch::bake()
{
    m_interface->bake(m_id);
}

size_t Batch::cpuConcurrencyWidth() const
{
    return m_interface->cpuConcurrencyWidth(m_id);
}

BatchRunContextId Batch::runPrologue()
{
    return m_interface->runPrologue(m_id);
}

void Batch::runEpilogue(const BatchRunContextId& contextId)
{
    m_interface->runEpilogue(m_id, contextId);
}

void Batch::run(const BatchRunContextId& contextId)
{
    m_interface->run(m_id, contextId);
}

void Batch::runWithInitialQueueIndex(const BatchRunContextId& contextId, const size_t desiredQueueIndex)
{
    m_interface->runWithInitialQueueIndex(m_id, contextId, desiredQueueIndex);
}

void Batch::cancel()
{
    m_interface->cancel(m_id);
}

void Batch::print() const
{
    m_interface->print(m_id);
}

void Batch::markViewsValid()
{
    m_interface->markViewsValid(m_id);
}

void Batch::reportStatistics(const size_t iterations) const
{
    m_interface->reportStatistics(m_id, iterations);
}

void Batch::reportRunTime(const size_t iterations) const
{
    m_interface->reportRunTime(m_id, iterations);
}

void Batch::resetStatistics()
{
    m_interface->resetStatistics(m_id);
}

void Batch::setDeveloperSettings(const struct BatchDeveloperSettings& developer)
{
    m_interface->setDeveloperSettings(m_id, developer);
}

carb::cpp::span<const batch::AttributeSpecification> Batch::getAttributeSpecifications(const size_t lambdaIndex)
{
    return m_interface->getAttributeSpecifications(m_id, lambdaIndex);
}
} // namespace batch
} // namespace fabric
} // namespace omni
