// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Handle.h"
#include <carb/Interface.h>

namespace omni
{
namespace graph
{
namespace core
{

/**
 * Interface to the underlying data access for OmniGraph
 */
struct IDataModel
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IDataModel", 1, 1);

    // This shouldn't exist...all data model changes should be implemented via data model interface
    // until this is done, we expose a way to protect edits to data model...like ones in PrimCommon

    /**
     * @return Allocate and return new scoped lock for read or write.
     */
    void* (CARB_ABI* enterEditScope)(bool writer);

    /**
     * @param[in] scope Free scoped lock
     */
    void (CARB_ABI* exitEditScope)(void* scope);
};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IDataModel, exitEditScope, 1)

//! Scoping object to enter and exist editing mode for the DataModel
class DataModelEditScope
{
public:
    //! Constructor to enter the edit scope, optionally with write mode enabled
    DataModelEditScope(bool write)
    {
        static const IDataModel& iDataModel = *carb::getCachedInterface<IDataModel>();
        m_scope = iDataModel.enterEditScope(write);
    }

    //! Destructor that exits the DataModel edit scope
    ~DataModelEditScope()
    {
        static const IDataModel& iDataModel = *carb::getCachedInterface<IDataModel>();
        iDataModel.exitEditScope(m_scope);
    }
private:
    void* m_scope{nullptr};
};

}
}
}
