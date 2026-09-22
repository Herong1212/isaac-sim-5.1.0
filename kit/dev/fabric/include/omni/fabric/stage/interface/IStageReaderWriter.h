// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>

#include <omni/fabric/core/API.h>
#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/Enums.h>
#include <omni/fabric/FabricTypes.h>
#include <omni/fabric/IdTypes.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/Ordered_Set.h>
#include <omni/fabric/FabricTime.h>
//#include <omni/fabric/stage/ChangeTracking.h>
#include <stdint.h>

namespace omni
{
namespace fabric
{

// Holds the result of a stage in progress exclusive lock operation
struct SimStageWithHistoryLockSnapshot
{
    UsdStageId usdStageId;
    int64_t simFrameNumber = -1;
    int64_t writeSlot = -1;
};

class FineGrainedChangeTracker;

// Note when extending the interface please add to the end so
// that dependencies don't break as easily before they are rebuilt
//
struct IStageReaderWriter
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IStageReaderWriter", 0, 14);

    StageReaderWriterId(CARB_ABI* create)(UsdStageId usdStageId, size_t simFrameNumber);
    StageReaderWriterId(CARB_ABI* get)(UsdStageId usdStageId);
    void(CARB_ABI* flushToRingBuffer)(UsdStageId usdStageId);
    size_t(CARB_ABI* getFrameNumber)(StageReaderWriterId stageId);

    // Prefetch prim from USD stage
    // This guarantees that subsequent gets of the prim from the cache will succeed
    void(CARB_ABI* prefetchPrim)(UsdStageId usdStageId, PathC path);

    CARB_DEPRECATED("Use getAttribute(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttribute_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    CARB_DEPRECATED("Use getAttributeRd(), which returns a ConstSpanWithTypeC instead.")
    ConstSpanC(CARB_ABI* getAttributeRd_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    CARB_DEPRECATED("Use getAttributeWr(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttributeWr_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    CARB_DEPRECATED("Use getOrCreateAttributeWr(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getOrCreateAttributeWr_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName, TypeC typeC);

    size_t(CARB_ABI* getArrayAttributeSize)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    size_t*(CARB_ABI* getArrayAttributeSizePtr)(StageReaderWriterId stageId, PathC path, TokenC attrName);
    const size_t*(CARB_ABI* getArrayAttributeSizeRdPtr)(StageReaderWriterId stageId, PathC path, TokenC attrName);
    size_t*(CARB_ABI* getArrayAttributeSizeWrPtr)(StageReaderWriterId stageId, PathC path, TokenC attrName);
    const size_t*(CARB_ABI* getArrayAttributeSizeRdGpuPtr)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    void(CARB_ABI* setArrayAttributeSize)(StageReaderWriterId stageId, PathC path, TokenC attrName, size_t elemCount);

    CARB_DEPRECATED("Use setArrayAttributeSizeAndGet(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* setArrayAttributeSizeAndGet_DEPRECATED)(StageReaderWriterId stageId,
                                                      PrimBucketListId primBucketList,
                                                      size_t primBucketListIndex,
                                                      size_t indexInBucket,
                                                      TokenC attrName,
                                                      size_t newElemCount);

    // Get an attribute's type
    Type(CARB_ABI* getType)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get prim's attribute count
    size_t(CARB_ABI* getAttributeCount)(StageReaderWriterId stageId, PathC path);

    // Get the names of a prim's attributes
    void(CARB_ABI* getAttributeNamesAndTypes)(
        Token* outNames, Type* outTypes, size_t outCount, StageReaderWriterId stageId, PathC path);

    /** @brief Get the names and tyes associated with a given prim
     *
     * @out[out] a buffer to hold the requested information. it must be sized appropriately.
     * @outCount[out] the size of the out parameter
     * @stageId[in] the stage id
     * @path[in] the path of the prim to check
     *
     */
    void(CARB_ABI* getAttrNamesAndTypes)(AttrNameAndType* out, size_t outCount, StageReaderWriterId stageID, PathC path);

    // Attribute/prim create/destroy
    void(CARB_ABI* createPrim)(StageReaderWriterId stageId, PathC path);
    void(CARB_ABI* destroyPrim)(StageReaderWriterId stageId, PathC path);    
    void(CARB_ABI* movePrim)(StageReaderWriterId stageId, PathC oldPath, PathC newPath);
    void(CARB_ABI* createAttribute)(StageReaderWriterId stageId, PathC path, TokenC attrName, TypeC type);
    void(CARB_ABI* createAttributes)(
        StageReaderWriterId stageId, PathC path, TokenC* attrNames, TypeC* types, uint32_t attrNameAndTypeCount);

    // Deprecated as type attribute is not required!
    void(CARB_ABI* destroyAttribute)(StageReaderWriterId stageId, PathC path, TokenC attrName, TypeC type);
    // see new destroyAttribute and destroyAttributes functions at end of IFabric

    // Attribute SOA accessors
    PrimBucketListId(CARB_ABI* findPrims)(StageReaderWriterId stageId,
                                          const omni::fabric::set<AttrNameAndType>& all,
                                          const omni::fabric::set<AttrNameAndType>& any,
                                          const omni::fabric::set<AttrNameAndType>& none);

    CARB_DEPRECATED("Use getAttributeArray(), which returns a SpanWithTypeC instead.")
    void(CARB_ABI* getAttributeArray_DEPRECATED)(SpanC* out,
                                           StageReaderWriterId stageId,
                                           PrimBucketListId primBucketList,
                                           size_t primBucketListIndex,
                                           TokenC attrName);

    CARB_DEPRECATED("Use getAttributeArrayRd(), which returns a ConstSpanWithTypeC instead.")
    void(CARB_ABI* getAttributeArrayRd_DEPRECATED)(ConstSpanC* out,
                                             StageReaderWriterId stageId,
                                             PrimBucketListId primBucketList,
                                             size_t primBucketListIndex,
                                             TokenC attrName);

    CARB_DEPRECATED("Use getAttributeArrayWr(), which returns a SpanWithTypeC instead.")
    void(CARB_ABI* getAttributeArrayWr_DEPRECATED)(SpanC* out,
                                             StageReaderWriterId stageId,
                                             PrimBucketListId primBucketList,
                                             size_t primBucketListIndex,
                                             TokenC attrName);

    CARB_DEPRECATED("Use getOrCreateAttributeArrayWr(), which uses Type instead of TypeC and returns a SpanWithTypeC instead.")
    void(CARB_ABI* getOrCreateAttributeArrayWr_DEPRECATED)(SpanC* out,
                                                     StageReaderWriterId stageId,
                                                     PrimBucketListId primBucketList,
                                                     size_t primBucketListIndex,
                                                     TokenC attrName,
                                                     TypeC typeC);

    size_t(CARB_ABI* getBucketPrimCount)(StageReaderWriterId stageId,
                                         PrimBucketListId primBucketList,
                                         size_t primBucketListIndex,
                                         TokenC attrName);

    size_t(CARB_ABI* getBucketAttributeCount)(StageReaderWriterId stageId,
                                              PrimBucketListId primBucketList,
                                              size_t primBucketListIndex);

    void(CARB_ABI* getBucketAttributeNamesAndTypes)(AttrNameAndType* out,
                                                    size_t outCount,
                                                    StageReaderWriterId stageId,
                                                    PrimBucketListId primBucketList,
                                                    size_t primBucketListIndex);

    ConstSpanSizeC(CARB_ABI* getArrayAttributeSizeArrayRd)(StageReaderWriterId stageId,
                                                           PrimBucketListId primBucketList,
                                                           size_t primBucketListIndex,
                                                           TokenC attrName);

    CARB_DEPRECATED("Use getArrayAttributeArrayWithSizes(), which returns a span with type instead.")
    ArrayPointersAndSizesC(CARB_ABI* getArrayAttributeArrayWithSizes_DEPRECATED)(StageReaderWriterId stageId,
                                                                      PrimBucketListId primBucketList,
                                                                      size_t primBucketListIndex,
                                                                      TokenC attrName);

    CARB_DEPRECATED("Use getArrayAttributeArrayWithSizesRd(), which returns a span with type instead.")
    ConstArrayPointersAndSizesC(CARB_ABI* getArrayAttributeArrayWithSizesRd_DEPRECATED)(StageReaderWriterId stageId,
                                                                             PrimBucketListId primBucketList,
                                                                             size_t primBucketListIndex,
                                                                             TokenC attrName);

    CARB_DEPRECATED("Use getArrayAttributeArrayWithSizesWr(), which returns a span with type instead.")
    ArrayPointersAndSizesC(CARB_ABI* getArrayAttributeArrayWithSizesWr_DEPRECATED)(StageReaderWriterId stageId,
                                                                        PrimBucketListId primBucketList,
                                                                        size_t primBucketListIndex,
                                                                        TokenC attrName);

    void(CARB_ABI* getPathArray)(ConstPathCSpan* out,
                                 StageReaderWriterId stageId,
                                 PrimBucketListId primBucketList,
                                 size_t primBucketListIndex);
    void(CARB_ABI* printBucketNames)(StageReaderWriterId stageId);

    void(CARB_ABI* createForAllStages)(int64_t simFrameNumber);
    void(CARB_ABI* flushAllStagesToRingBuffer)();


    void(CARB_ABI* logAttributeWriteForNotice)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Broadcast a USD TfNotice to all registered listeners containing paths of
    // all attributes passed to logAttributeWriteForNotice since this StageReaderWriter was constructed.
    // This is used, for example, to send changes to PhysX.
    void(CARB_ABI* broadcastTfNoticeForAttributesChanged)(StageReaderWriterId stageId);

    PrimBucketListId(CARB_ABI* getChanges)(StageReaderWriterId stageId, ListenerId listenerId);
    void(CARB_ABI* popChanges)(StageReaderWriterId stageId, ListenerId listenerId);

    FabricTime(CARB_ABI* getFrameTime)(StageReaderWriterId stageId);

    CARB_DEPRECATED("Use getArrayAttribute(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getArrayAttribute_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    CARB_DEPRECATED("Use getArrayAttributeRd(), which returns a ConstSpanWithTypeC instead.")
    ConstSpanC(CARB_ABI* getArrayAttributeRd_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    CARB_DEPRECATED("Use getArrayAttributeWr(), which returns a ConstSpanWithTypeC instead.")
    SpanC(CARB_ABI* getArrayAttributeWr_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    /** @brief Destroy attribute with matching name
     *
     * Overloads and superseeds destroyAttribute which takes a unnecessary attribute type.
     *
     * @stageId[in] Id for the stage to look in
     * @path[in] Path to the prim holding the attribute
     * @attrNames[in] Attribute name
     *
     */
    void(CARB_ABI* destroyAttribute2)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    /** @brief Destroy all attributes with matching names
     *
     * @stageId[in] Id for the stage to look in
     * @path[in] Path to the prim holding the attribute
     * @attrNames[in] Attribute name array
     * @attrNames[in] Attribute name array count
     *
     */
    void(CARB_ABI* destroyAttributes)(StageReaderWriterId stageId, PathC path, TokenC* attrNames, uint32_t attrNameCount);

    // Begin: Backwards compatible single GPU functions whose implementations call their *MGpu* counterparts with device
    // Id = 0
    CARB_DEPRECATED("Use getAttributeArrayGpu(), which returns a SpanWithTypeC instead.")
    void(CARB_ABI* getAttributeArrayGpu_DEPRECATED)(SpanC* out,
                                              StageReaderWriterId stageId,
                                              PrimBucketListId primBucketList,
                                              size_t primBucketListIndex,
                                              TokenC attrName);

    CARB_DEPRECATED("Use getAttributeArrayRdGpu(), which returns a SpanWithTypeC instead.")
    void(CARB_ABI* getAttributeArrayRdGpu_DEPRECATED)(ConstSpanC* out,
                                           StageReaderWriterId stageId,
                                           PrimBucketListId primBucketList,
                                           size_t primBucketListIndex,
                                           TokenC attrName);

    CARB_DEPRECATED("Use getAttributeArrayWrGpu(), which returns a SpanWithTypeC instead.")
    void(CARB_ABI* getAttributeArrayWrGpu_DEPRECATED)(SpanC* out,
                                           StageReaderWriterId stageId,
                                           PrimBucketListId primBucketList,
                                           size_t primBucketListIndex,
                                           TokenC attrName);

    // Get GPU attribute for read/write access
    CARB_DEPRECATED("Use getAttributeGpu(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttributeGpu_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get GPU attribute for read only access
    CARB_DEPRECATED("Use getAttributeRdGpu(), which returns a ConstSpanWithTypeC instead.")
    ConstSpanC(CARB_ABI* getAttributeRdGpu_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get GPU attribute for write only access
    CARB_DEPRECATED("Use getAttributeWrGpu(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttributeWrGpu_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get GPU attribute for read/write access
    CARB_DEPRECATED("Use getAttributeGpuMemType(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttributeGpuMemType_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName, PtrToPtrKind wherePtr);

    // Get GPU attribute for read only access
    CARB_DEPRECATED("Use getAttributeRdGpuMemType(), which returns a ConstSpanWithTypeC instead.")
    ConstSpanC(CARB_ABI* getAttributeRdGpuMemType_DEPRECATED)(StageReaderWriterId stageId,
                                                        PathC path,
                                                        TokenC attrName,
                                                        PtrToPtrKind wherePtr);

    // Get GPU attribute for write only access
    CARB_DEPRECATED("Use getAttributeWrGpuMemType(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttributeWrGpuMemType_DEPRECATED)(StageReaderWriterId stageId,
                                                   PathC path,
                                                   TokenC attrName,
                                                   PtrToPtrKind wherePtr);
    // End: Backwards compatible single GPU functions whose implementations call their *MGpu* counterparts with device
    // Id = 0

    /** @brief Returns which mirrors of the array are valid: CPU, GPU, etc.
     *
     * @stageId[in] The stage to query validity from
     * @path[in] The prim path
     * @attrName[in] The attribute name
     *
     * @return ValidMirrors struct
     *
     */
    ValidMirrors(CARB_ABI* getAttributeValidBits)(StageReaderWriterId stageId, const PathC& path, const TokenC& attrName);

    // Connection API
    /**
     * @brief Create a connection on a prim
     *
     * @param[in] stageId the stage to work on
     * @param[in] path the prim to create the connection on
     * @param[in] connectionName the name of the connection attribute
     * @param[in] connection the target prim and attribute for the connection
     */
    void(CARB_ABI* createConnection)(StageReaderWriterId stageId, PathC path, TokenC connectionName, Connection connection);

    /**
     * @brief Create multiple connections on a prim
     *
     * @param[in] stageId the stage to work on
     * @param[in] path the prim to create the connection on
     * @param[in] connectionNames the name of the connection attributes to create
     * @param[in] connection the target prim and attribute for the connections
     * @param[in] connectionCount the number of connections to be created.
     */
    void(CARB_ABI* createConnections)(StageReaderWriterId stageId,
                                      PathC path,
                                      const TokenC* connectionNames,
                                      const Connection* connections,
                                      size_t connectionCount);

    /**
     * @brief remove a connection on a prim
     *
     * @param[in] stageId the stage to work on
     * @param[in] path the prim to remove the connection from
     * @param[in] connectionName the name of the connection attribute
     */
    void(CARB_ABI* destroyConnection)(StageReaderWriterId stageId, PathC path, TokenC connectionName);

    /**
     * @brief Remove multiple connections from a prim
     *
     * @param[in] stageId the stage to work on
     * @param[in] path the prim to remove the connections from
     * @param[in] connectionNames the name of the connection attributes to be removed
     * @param[in] connectionCount the number of connections to be removed.
     */
    void(CARB_ABI* destroyConnections)(StageReaderWriterId stageId,
                                       PathC path,
                                       const TokenC* connectionNames,
                                       size_t connectionCount);

    /**
     * @brief  Retrieves a connection attribute from a prim
     *
     * @param[in] stageId the stage to work on
     * @param[in] path the prim to fetch the connection from
     * @param[in] connectionName the name of the connection attribute to fetch
     * @return a read/write pointer to the connection
     */
    Connection*(CARB_ABI* getConnection)(StageReaderWriterId stageId, PathC path, TokenC connectionName);

    /**
     * @brief  Retrieves a connection attribute from a prim
     *
     * @param[in] stageId the stage to work on
     * @param[in] path the prim to fetch the connection from
     * @param[in] connectionName the name of the connection attribute to fetch
     * @return a read only pointer to the connection
     */
    const Connection*(CARB_ABI* getConnectionRd)(StageReaderWriterId stageId, PathC path, TokenC connectionName);

    /**
     * @brief  Retrieves a connection attribute from a prim
     *
     * @param[in] stageId the stage to work on
     * @param[in] path the prim to fetch the connection from
     * @param[in] connectionName the name of the connection attribute to fetch
     * @return a write only pointer to the connection
     */
    Connection*(CARB_ABI* getConnectionWr)(StageReaderWriterId stageId, PathC path, TokenC connectionName);

    /**
     * @brief Copy all attributes from the source prim to the destination prim
     * Will create attributes if they do not exist on the destination prim
     * If an attribute exists on both prims they must have compatible types to copy.
     *
     * @param[in] stageId the stage id to use for copying
     * @param[in] srcPath the source prim
     * @param[in] dstPath the destination prim
     */
    void(CARB_ABI* copyAllAttributes)(StageReaderWriterId stageId, PathC srcPath, PathC dstPath);

    /**
     * @brief Copy the specified attributes from the source prim to the the specified
     * attributes on the destination prim
     * Will create attributes if they do not exist on the destination prim
     * If an attribute exists on both prims they must have compatible types to copy.
     * Note: The srcAttrs and dstAttrs must be the same size as the function assumes
     * that the copy is 1 to 1 in terms of name alignment
     *
     * @param[in] stageId the stage id to use for copying
     * @param[in] srcPath the source prim
     * @param[in] srcAttrs a vector of attributes to be copied.
     * @param[in] dstPath the destination prim
     * @param[in] dstAttrs a vector of attributes to be copied.
     * @param[in] count the number of attributes to copy
     */
    void(CARB_ABI* copySpecifiedAttributes)(StageReaderWriterId stageId,
                                            PathC srcPath,
                                            const TokenC* srcAttrs,
                                            PathC dstPath,
                                            const TokenC* dstAttrs,
                                            size_t count);

    /** @brief Get the FabricId for the StageReaderWriter.  This can be used
     * with the IFabric/IFabricUsd interfaces.
     *
     * @param[in] stageId the stage id whose fabricId is desired.
     * @return the id of the working fabric space.
     */
    FabricId(CARB_ABI* getFabricId)(StageReaderWriterId stageId);

    /** @brief Create or get a StageReaderWriter that is based on the given FabricId
     *
     * @param[in] fabricId the fabric to use to create the stagereaderwriter
     * @return the associated StageReaderWriterId.
     */
    StageReaderWriterId(CARB_ABI* createOrGetFromFabricId)(FabricId fabricId);

    /** @brief checks if a prim exists in Fabric
     *
     * @param[in] stageId the stage id to check
     * @param[in] path the prim
     * @return true if the prim exists in fabric
     */
    bool(CARB_ABI* primExists)(StageReaderWriterId stageId, PathC path);

    /** @brief checks if a prim with the given attribute exists in Fabric
     *
     * @param[in] stageId the stage id to check
     * @param[in] path the prim
     * @param[in] attrName the encoded name of the attribute
     * @return true if the prim with attribute exists in fabric
     */
    bool(CARB_ABI* attributeExists)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    /** @brief checks if a prim has an attribute of a given name and type
     *
     * @param[in] stageId the stage id to check
     * @param[in] path the prim
     * @param[in] attrName the encoded name
     * @param[in] typeC the encoded type of the attribute
     * @return true if the attribute exists in the prim with the given type
     */
    bool(CARB_ABI* attributeExistsWithType)(StageReaderWriterId stageId, PathC path, TokenC attrName, TypeC attrTypeC);

    FABRIC_ABI_DUMMY(1)
    FABRIC_ABI_DUMMY(2)
    FABRIC_ABI_DUMMY(3)
    FABRIC_ABI_DUMMY(4)
    FABRIC_ABI_DUMMY(5)
    FABRIC_ABI_DUMMY(6)
    FABRIC_ABI_DUMMY(7)

    /** @brief Set the USD type of a prim
     *
     * @stageId[in] The stage containing the prim
     * @path[in] The path of the prim
     * @typeName[in] The desired type of the prim
     */
    void(CARB_ABI* setPrimTypeName)(StageReaderWriterId stageId, PathC path, TokenC typeName);

    /** @brief Get the USD type of a prim
     *
     * @stageId[in] The stage containing the prim
     * @path[in] The path of the prim
     *
     * @return The USD type name of the prim
     */
    TokenC(CARB_ABI* getPrimTypeName)(StageReaderWriterId stageId, PathC path);

    /** @brief Get the USD type of the prims in a bucket
     *
     * @stageId[in] The stage containing the prim
     * @primBucketList[in] The primBucketList
     * @primBucketListIndex[in] The index of the bucket within the primBucketList
     *
     * @return The USD type name of the prims in the bucket
     */
    TokenC(CARB_ABI* getBucketPrimTypeName)(StageReaderWriterId stageId,
                                            PrimBucketListId primBucketList,
                                            size_t primBucketListIndex);

    FABRIC_ABI_DUMMY(8)
    FABRIC_ABI_DUMMY(9)

    // MGPU versions of existing GPU functions that support specifying a particular device id on which the
    // attribute/array should be made available
    CARB_DEPRECATED("Use getAttributeArrayMGpu(), which returns a SpanWithTypeC instead.")
    void(CARB_ABI* getAttributeArrayMGpu_DEPRECATED)(SpanC* out,
                                               StageReaderWriterId stageId,
                                               PrimBucketListId primBucketList,
                                               size_t primBucketListIndex,
                                               TokenC attrName,
                                               int deviceId);

    CARB_DEPRECATED("Use getAttributeArrayRdMGpu(), which returns a ConstSpanWithTypeC instead.")
    void(CARB_ABI* getAttributeArrayRdMGpu_DEPRECATED)(ConstSpanC* out,
                                                 StageReaderWriterId stageId,
                                                 PrimBucketListId primBucketList,
                                                 size_t primBucketListIndex,
                                                 TokenC attrName,
                                                 int deviceId);

    CARB_DEPRECATED("Use getAttributeArrayWrMGpu(), which returns a SpanWithTypeC instead.")
    void(CARB_ABI* getAttributeArrayWrMGpu_DEPRECATED)(SpanC* out,
                                                 StageReaderWriterId stageId,
                                                 PrimBucketListId primBucketList,
                                                 size_t primBucketListIndex,
                                                 TokenC attrName,
                                                 int deviceId);

    // Get GPU attribute for read/write access
    CARB_DEPRECATED("Use getAttributeMGpu(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttributeMGpu_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName, int deviceId);

    // Get GPU attribute for read only access
    CARB_DEPRECATED("Use getAttributeRdMGpu(), which returns a ConstSpanWithTypeC instead.")
    ConstSpanC(CARB_ABI* getAttributeRdMGpu_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName, int deviceId);

    // Get GPU attribute for write only access
    CARB_DEPRECATED("Use getAttributeWrMGpu(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttributeWrMGpu_DEPRECATED)(StageReaderWriterId stageId, PathC path, TokenC attrName, int deviceId);

    // Get GPU attribute for read/write access
    CARB_DEPRECATED("Use getAttributeMGpuMemType(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttributeMGpuMemType_DEPRECATED)(
        StageReaderWriterId stageId, PathC path, TokenC attrName, PtrToPtrKind wherePtr, int deviceId);

    // Get GPU attribute for read only access
    CARB_DEPRECATED("Use getAttributeRdMGpuMemType(), which returns a ConstSpanWithTypeC instead.")
    ConstSpanC(CARB_ABI* getAttributeRdMGpuMemType_DEPRECATED)(
        StageReaderWriterId stageId, PathC path, TokenC attrName, PtrToPtrKind wherePtr, int deviceId);

    // Get GPU attribute for write only access
    CARB_DEPRECATED("Use getAttributeWrMGpuMemType(), which returns a SpanWithTypeC instead.")
    SpanC(CARB_ABI* getAttributeWrMGpuMemType_DEPRECATED)(
        StageReaderWriterId stageId, PathC path, TokenC attrName, PtrToPtrKind wherePtr, int deviceId);

    /**
     * @brief Obtains the current simulation frame and ring buffer slot that will be used when flushing to ring buffer
     *
     * @param[in] stageId the stage id to use for copying
     * @param[out] simFrameNumber the simulation frame number we are writting the data for
     * @param[out] writeSlot the simStageWithHistory ring buffer slot we will be writing to
     */
    void(CARB_ABI* getWriteParameters)(UsdStageId usdStageId, int64_t& simFrameNumber, int64_t& writeSlot);

    /**
     * @brief Acquires write locks to the ring buffer slot relating to the current simulation frame
     *
     * @param[in] stageId the stage id to use for copying
     * @param[out] lockedSnapshot the snapshot of the paramaters relating to the simStageWithHistory ring buffer slot we
     * locked
     */
    void(CARB_ABI* exclusiveAcquireAndInitRingBufferSlotForCurrentSimStage)(
        UsdStageId usdStageId, SimStageWithHistoryLockSnapshot& lockedSnapshot);

    /**
     * @brief Same as @see flushToRingBuffer, but instead keeps the exclusive write lock on the ring buffer slot
     * relating to the current simulation
     *
     * @param[in] stageId the stage id to use for copying
     */
    void(CARB_ABI* flushToRingBufferAlreadyLocked)(UsdStageId usdStageId);

    /**
     * @brief unlock previous locked ring buffer slots relating to the current simulation frame
     *
     * @param[in] lockedSnapshot the previously aquired snapshot
     */
    void(CARB_ABI* unlock)(SimStageWithHistoryLockSnapshot& lockedSnapshot);

    CARB_DEPRECATED("Use getArrayAttributeArrayWithSizesGpu(), which returns a span with type instead.")
    ArrayPointersAndSizesC(CARB_ABI* getArrayAttributeArrayWithSizesGpu_DEPRECATED)(StageReaderWriterId stageId,
                                                                         PrimBucketListId primBucketList,
                                                                         size_t primBucketListIndex,
                                                                         TokenC attrName);

    CARB_DEPRECATED("Use getArrayAttributeArrayWithSizesRdGpu(), which returns a span with type instead.")
    ConstArrayPointersAndSizesC(CARB_ABI* getArrayAttributeArrayWithSizesRdGpu_DEPRECATED)(StageReaderWriterId stageId,
                                                                                PrimBucketListId primBucketList,
                                                                                size_t primBucketListIndex,
                                                                                TokenC attrName);

    CARB_DEPRECATED("Use getArrayAttributeArrayWithSizesWrGpu(), which returns a span with type instead.")
    ArrayPointersAndSizesC(CARB_ABI* getArrayAttributeArrayWithSizesWrGpu_DEPRECATED)(StageReaderWriterId stageId,
                                                                           PrimBucketListId primBucketList,
                                                                           size_t primBucketListIndex,
                                                                           TokenC attrName);

    PrimBucketListId(CARB_ABI* allPrims)(StageReaderWriterId stageId);

    // Get attribute for read/write access
    SpanWithTypeC(CARB_ABI* getAttribute)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get attribute for read only access
    ConstSpanWithTypeC(CARB_ABI* getAttributeRd)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get attribute for write only access
    SpanWithTypeC(CARB_ABI* getAttributeWr)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    /** @brief Get a Span with a pointer to the head of the relevant array of data
     *         with elementCount, elementSize, and elementType reflecting the underlying data
     *
     * @stageId[in] Id for the stage to look in
     * @path[in] Path to the prim holding the attribute
     * @name[in] Name of the array attribute
     *
     * @return If a valid prim/attribute that hold an array returns a valid span, otherwise
     *         returns an empty span.
     *
     */
    SpanWithTypeC(CARB_ABI* getArrayAttribute)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    /** @brief Get a const Span with a pointer to the head of the relevant array of data
     *         with elementCount, elementSize, and elementType reflecting the underlying data
     *
     * @stageId[in] Id for the stage to look in
     * @path[in] Path to the prim holding the attribute
     * @name[in] Name of the array attribute
     *
     * @return If a valid prim/attribute that hold an array returns a valid span, otherwise
     *         returns an empty span.
     *
     */
    ConstSpanWithTypeC(CARB_ABI* getArrayAttributeRd)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    /** @brief Get a Span with a pointer to the head of the relevant array of data
     *         with elementCount, elementSize, and elementType reflecting the underlying data
     *
     * @stageId[in] Id for the stage to look in
     * @path[in] Path to the prim holding the attribute
     * @name[in] Name of the array attribute
     *
     * @return If a valid prim/attribute that hold an array returns a valid span, otherwise
     *         returns an empty span.
     *
     */
    SpanWithTypeC(CARB_ABI* getArrayAttributeWr)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get attribute for write only access, creating it if necessary
    SpanWithTypeC(CARB_ABI* getOrCreateAttributeWr)(StageReaderWriterId stageId, PathC path, TokenC attrName, TypeC typeC);

    SpanWithTypeC(CARB_ABI* setArrayAttributeSizeAndGet)(StageReaderWriterId stageId,
                                                         PrimBucketListId primBucketList,
                                                         size_t primBucketListIndex,
                                                         size_t indexInBucket,
                                                         TokenC attrName,
                                                         size_t newElemCount);

    void(CARB_ABI* getAttributeArray)(SpanWithTypeC* out,
                                      StageReaderWriterId stageId,
                                      PrimBucketListId primBucketList,
                                      size_t primBucketListIndex,
                                      TokenC attrName);

    void(CARB_ABI* getAttributeArrayRd)(ConstSpanWithTypeC* out,
                                        StageReaderWriterId stageId,
                                        PrimBucketListId primBucketList,
                                        size_t primBucketListIndex,
                                        TokenC attrName);

    void(CARB_ABI* getAttributeArrayWr)(SpanWithTypeC* out,
                                        StageReaderWriterId stageId,
                                        PrimBucketListId primBucketList,
                                        size_t primBucketListIndex,
                                        TokenC attrName);

    void(CARB_ABI* getOrCreateAttributeArrayWr)(SpanWithTypeC* out,
                                                StageReaderWriterId stageId,
                                                PrimBucketListId primBucketList,
                                                size_t primBucketListIndex,
                                                TokenC attrName,
                                                Type type);

    // Begin: Backwards compatible single GPU functions whose implementations call their *MGpu* counterparts with device
    // Id = 0
    void(CARB_ABI* getAttributeArrayGpu)(SpanWithTypeC* out,
                                         StageReaderWriterId stageId,
                                         PrimBucketListId primBucketList,
                                         size_t primBucketListIndex,
                                         TokenC attrName);

    void(CARB_ABI* getAttributeArrayRdGpu)(ConstSpanWithTypeC* out,
                                           StageReaderWriterId stageId,
                                           PrimBucketListId primBucketList,
                                           size_t primBucketListIndex,
                                           TokenC attrName);
    
    void(CARB_ABI* getAttributeArrayWrGpu)(SpanWithTypeC* out,
                                           StageReaderWriterId stageId,
                                           PrimBucketListId primBucketList,
                                           size_t primBucketListIndex,
                                           TokenC attrName);
    //  Get GPU attribute for read/write access
    SpanWithTypeC(CARB_ABI* getAttributeGpu)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get GPU attribute for read only access
    ConstSpanWithTypeC(CARB_ABI* getAttributeRdGpu)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get GPU attribute for write only access
    SpanWithTypeC(CARB_ABI* getAttributeWrGpu)(StageReaderWriterId stageId, PathC path, TokenC attrName);

    // Get GPU attribute for read/write access
    SpanWithTypeC(CARB_ABI* getAttributeGpuMemType)(StageReaderWriterId stageId,
                                                    PathC path,
                                                    TokenC attrName,
                                                    PtrToPtrKind wherePtr);

    // Get GPU attribute for read only access
    ConstSpanWithTypeC(CARB_ABI* getAttributeRdGpuMemType)(StageReaderWriterId stageId,
                                                           PathC path,
                                                           TokenC attrName,
                                                           PtrToPtrKind wherePtr);

    // Get GPU attribute for write only access
    SpanWithTypeC(CARB_ABI* getAttributeWrGpuMemType)(StageReaderWriterId stageId,
                                                      PathC path,
                                                      TokenC attrName,
                                                      PtrToPtrKind wherePtr);
    // End: Backwards compatible single GPU functions whose implementations call their *MGpu* counterparts with device
    // Id = 0

    void(CARB_ABI* getAttributeArrayMGpu)(SpanWithTypeC* out,
                                          StageReaderWriterId stageId,
                                          PrimBucketListId primBucketList,
                                          size_t primBucketListIndex,
                                          TokenC attrName,
                                          int deviceId);

    void(CARB_ABI* getAttributeArrayRdMGpu)(ConstSpanWithTypeC* out,
                                            StageReaderWriterId stageId,
                                            PrimBucketListId primBucketList,
                                            size_t primBucketListIndex,
                                            TokenC attrName,
                                            int deviceId);
    
    void(CARB_ABI* getAttributeArrayWrMGpu)(SpanWithTypeC* out,
                                            StageReaderWriterId stageId,
                                            PrimBucketListId primBucketList,
                                            size_t primBucketListIndex,
                                            TokenC attrName,
                                            int deviceId);
    
    // Get GPU attribute for read/write access
    SpanWithTypeC(CARB_ABI* getAttributeMGpu)(StageReaderWriterId stageId, PathC path, TokenC attrName, int deviceId);
    
    // Get GPU attribute for read only access
    ConstSpanWithTypeC(CARB_ABI* getAttributeRdMGpu)(StageReaderWriterId stageId, PathC path, TokenC attrName, int deviceId);

    // Get GPU attribute for write only access
    SpanWithTypeC(CARB_ABI* getAttributeWrMGpu)(StageReaderWriterId stageId, PathC path, TokenC attrName, int deviceId);

    // Get GPU attribute for read/write access
    SpanWithTypeC(CARB_ABI* getAttributeMGpuMemType)(
        StageReaderWriterId stageId, PathC path, TokenC attrName, PtrToPtrKind wherePtr, int deviceId);

    // Get GPU attribute for read only access
    ConstSpanWithTypeC(CARB_ABI* getAttributeRdMGpuMemType)(
        StageReaderWriterId stageId, PathC path, TokenC attrName, PtrToPtrKind wherePtr, int deviceId);

    // Get GPU attribute for write only access
    SpanWithTypeC(CARB_ABI* getAttributeWrMGpuMemType)(
        StageReaderWriterId stageId, PathC path, TokenC attrName, PtrToPtrKind wherePtr, int deviceId);

    ArrayPointersAndSizesWithTypeC(CARB_ABI* getArrayAttributeArrayWithSizes)(StageReaderWriterId stageId,
                                                                      PrimBucketListId primBucketList,
                                                                      size_t primBucketListIndex,
                                                                      TokenC attrName);

    ConstArrayPointersAndSizesWithTypeC(CARB_ABI* getArrayAttributeArrayWithSizesRd)(StageReaderWriterId stageId,
                                                                             PrimBucketListId primBucketList,
                                                                             size_t primBucketListIndex,
                                                                             TokenC attrName);

    ArrayPointersAndSizesWithTypeC(CARB_ABI* getArrayAttributeArrayWithSizesWr)(StageReaderWriterId stageId,
                                                                        PrimBucketListId primBucketList,
                                                                        size_t primBucketListIndex,
                                                                        TokenC attrName);

    ArrayPointersAndSizesWithTypeC(CARB_ABI* getArrayAttributeArrayWithSizesGpu)(StageReaderWriterId stageId,
                                                                         PrimBucketListId primBucketList,
                                                                         size_t primBucketListIndex,
                                                                         TokenC attrName);

    ConstArrayPointersAndSizesWithTypeC(CARB_ABI* getArrayAttributeArrayWithSizesRdGpu)(StageReaderWriterId stageId,
                                                                                PrimBucketListId primBucketList,
                                                                                size_t primBucketListIndex,
                                                                                TokenC attrName);

    ArrayPointersAndSizesWithTypeC(CARB_ABI* getArrayAttributeArrayWithSizesWrGpu)(StageReaderWriterId stageId,
                                                                           PrimBucketListId primBucketList,
                                                                           size_t primBucketListIndex,
                                                                           TokenC attrName);
                                                                           
    ArrayPointersAndSizesWithTypeC(CARB_ABI* getArrayAttributeColumn)(StageReaderWriterId stageId,
                                                                      Span<FineGrainedChangeTracker> _fineGrainedChangeTrackers,
                                                                      PrimBucketListId primBucketList,
                                                                      size_t primBucketListIndex,
                                                                      TokenC attrName,
                                                                      WriteType accessType);

    // This method implements both getAttributeColumn() and getAttributeColumnWr()
    // Use accessType parameter to specify which one
    SpanWithTypeC(CARB_ABI* getAttributeColumn)(StageReaderWriterId stageId,
                                                Span<FineGrainedChangeTracker> _fineGrainedChangeTrackers,
                                                PrimBucketListId primBucketList,
                                                size_t primBucketListIndex,
                                                TokenC attrName,
                                                WriteType accessType);

    // Sets sparsely populated values to array attributes. This moves the bucket to cpu and overwrites the current array data
    // for the given paths and attribute with a "breadcrumb" to populate the actual data on demand.
    // Array values for sparsely populated values are not stored in fabric initially, but can be fully populated
    // and stored in fabric on access. Transparent to a consumer of fabric data, sparsely populated
    // array data is populated on demand through a populator (see IPopulator interface).
    // This helps reducing memory consumption for data that will only be accessed rarely or sparsely.
    void (CARB_ABI* setSparseArrayAttributes)(StageReaderWriterId stageReaderWriterId,
        const Span<const PathC>& paths,
        const AttrNameAndType& attribute,
        const PathC& populatorId,
        const Span<const SparseAttributeContext>& sparseAttributeContextPerPath);

    // Access array attribute metadata
    void (CARB_ABI* getArrayAttributeContentHash)(StageReaderWriterId stageReaderWriterId,
        const Span<const PathC>& paths,
        const AttrName& attribute,
        const Span<ContentHashType>& attributeContentHashPerPath);

    // Retrieve the span of content hashes for a given bucket
    // The following results are valid:
    //  * An empty span indicating that there is no such array attribute or it has no content hashes
    //  * A shorter span than elements in the bucket indicating that only some attributes have hashes
    //  * Hashes that are {} indicating that an element has no valid content hash
    Span<const ContentHashType> (CARB_ABI* getArrayAttributeContentHashes)(StageReaderWriterId stageId,
        PrimBucketListId primBucketList,
        size_t primBucketListIndex,
        TokenC attrName);

    // Same as getArrayAttributeArrayWithSizesRd, but doesn't trigger population of sparse data
    ConstArrayPointersAndSizesWithTypeC(CARB_ABI* getSparseArrayAttributeArrayWithSizesRd)(StageReaderWriterId stageId,
        PrimBucketListId primBucketList,
        size_t primBucketListIndex,
        TokenC attrName);

    // Advise the cache to populate sparse array attributes
    // if all sparse array attributes had been successfully populated within the timeout it returns true, otherwise false
    // this is no guarantee that all attributes will be populated when accessed after this call returns as another thread could call
    // adviseDepopulateSparseArrayAttribute in the meantime
    bool(CARB_ABI* advisePopulateSparseArrayAttribute)(StageReaderWriterId stageReaderWriterId,
        const Span<const PathC>& paths,
        const Span<const AttrName>& attributes,
        TimeSpanUS timeOut);

    // Advise the cache to depopulate sparse array attributes
    // This is no guarantee that sparse attributes are depopulated after this call returns as other
    // threads could access attributes or call advisePopulateSparseArrayAttribute
    void(CARB_ABI* adviseDepopulateSparseArrayAttribute)(StageReaderWriterId stageReaderWriterId,
        const Span<const PathC>& paths,
        const Span<const AttrName>& attributes);

    // triggers change tracking on elements between beginElem and endElem without changing the attributes
    void(CARB_ABI* dirtyAttribute)(StageReaderWriterId stageId,
        PrimBucketListId primBucketList,
        size_t primBucketListIndex,
        TokenC attrName, size_t beginElem, size_t endElem);

    // Internally every Fabric buffer is copy-on-write. Since queries for pointers to this memory are provided to the caller,
    // we can't know when those writes are complete. Since we cannot know when they are complete Fabric has to assume they could 
    // still be written to at any moment, and therefore not be cheaply copied by reference.
    // It must make a deep copy every time a copy is desired. 
    // This function tells fabric that all writes are complete across all memory in the Fabric, which allows for all memory to be cheaply copied by reference."
    void(CARB_ABI* commit)(StageReaderWriterId stageId);

    // tally the mutable internal structures in the given stage (which should be 0 after a close() operation)
    size_t(CARB_ABI* getMutableEntityCount)(StageReaderWriterId stageId);

    void(CARB_ABI* registerTokens)(StageReaderWriterId stageId, const Span<const Token>& tokens,
        const Span<size_t>& indexes);

    void(CARB_ABI* registerPaths)(StageReaderWriterId stageId, const Span<const Path>& paths,
        const Span<size_t>& indexes);

    void(CARB_ABI* createPrims)(StageReaderWriterId stageId,
                                const Span<const PathC>& paths,
                                const Span<AttrNameAndType>& attributes,
                                CreatePrimOptions createPrimOptions);

    // returns true if the specified bucket passes the filter defined by all, any, none in the same way as for findPrims()
    bool(CARB_ABI* acceptBucket)(StageReaderWriterId stageId, PrimBucketListId primBucketList,
        size_t primBucketListIndex, const omni::fabric::set<AttrNameAndType>& all,
        const omni::fabric::set<AttrNameAndType>& any,
        const omni::fabric::set<AttrNameAndType>& none);

    // this might seem odd, but the optional second span is for actual TokenC+PathC, which could be attribute memory
    void(CARB_ABI* registerTfTokens)(StageReaderWriterId stageId, const Span<const TokenC>& tfTokens);
    void(CARB_ABI* registerSdfPaths)(StageReaderWriterId stageId, const Span<const PathC>& sdfPaths);

    // Destroy many prims at once - more efficient than calling detroyPrim in a loop
    void(CARB_ABI* destroyPrims)(StageReaderWriterId stageId, PathC const* paths, size_t count);
};

// LEGACY SUPPORT FUNCTIONS TO USE AS WE TRANSITION TO HIDE FABRIC IMPL DETAILS

// DO NOT USE IN NEW CODE UNLESS ABSOLUTELY NECESARRY
// ALMOST ALL OF THIS WILL GO AWAY IN FAVOR OF THE UPCOMING QUERY INTERFACES

// DO NOT WRITE C++ WRAPPERS FOR THESE CALLS
struct IStageReaderWriterLegacy
{
    CARB_PLUGIN_INTERFACE("omni::fabric::IStageReaderWriterLegacy", 0, 5);

    FABRIC_ABI_DUMMY(1)

    BucketIdAndIndex(CARB_ABI* getBucketIdAndIndex)(StageReaderWriterId stageId, PathC path);
    size_t(CARB_ABI* findBucketIds)(BucketId* out,
                                    size_t outCount,
                                    StageReaderWriterId stageId,
                                    const AttrNameAndType* required,
                                    size_t requiredCount,
                                    const AttrNameAndType* any,
                                    size_t anyCount,
                                    const AttrNameAndType* none,
                                    size_t noneCount);
    void(CARB_ABI* getPathArrayFromBucketId)(ConstPathCSpan* out, StageReaderWriterId stageId, BucketId bucketId);
    size_t(CARB_ABI* getPrimCountFromBucketId)(StageReaderWriterId stageId, BucketId bucketId);
    size_t(CARB_ABI* getAttrNamesAndTypesFromBucketId)(AttrNameAndType* out,
                                                       size_t outCount,
                                                       StageReaderWriterId stageId,
                                                       BucketId bucketId);

    void(CARB_ABI* getAttributeArrayFromBucketId)(SpanC* out,
                                                  StageReaderWriterId stageId,
                                                  BucketId bucketId,
                                                  TokenC attrName);

    void(CARB_ABI* getAttributeArrayRdFromBucketId)(ConstSpanC* out,
                                                    StageReaderWriterId stageId,
                                                    BucketId bucketId,
                                                    TokenC attrName);

    void(CARB_ABI* getAttributeArrayWrFromBucketId)(SpanC* out,
                                                    StageReaderWriterId stageId,
                                                    BucketId bucketId,
                                                    TokenC attrName);

    void(CARB_ABI* getAttributeArrayGpuFromBucketId)(SpanC* out,
                                                     StageReaderWriterId stageId,
                                                     BucketId bucketId,
                                                     TokenC attrName);

    void(CARB_ABI* getAttributeArrayRdGpuFromBucketId)(ConstSpanC* out,
                                                       StageReaderWriterId stageId,
                                                       BucketId bucketId,
                                                       TokenC attrName);

    void(CARB_ABI* getAttributeArrayWrGpuFromBucketId)(SpanC* out,
                                                       StageReaderWriterId stageId,
                                                       BucketId bucketId,
                                                       TokenC attrName);

    void(CARB_ABI* getArrayAttributeSizesFromBucketId)(SpanSizeC* out,
                                                       StageReaderWriterId stageId,
                                                       BucketId bucketId,
                                                       TokenC attrName);
    void(CARB_ABI* getArrayAttributeSizesRdFromBucketId)(ConstSpanSizeC* out,
                                                         StageReaderWriterId stageId,
                                                         BucketId bucketId,
                                                         TokenC attrName);
    void(CARB_ABI* getArrayAttributeSizesWrFromBucketId)(SpanSizeC* out,
                                                         StageReaderWriterId stageId,
                                                         BucketId bucketId,
                                                         TokenC attrName);
    void(CARB_ABI* getArrayAttributeSizesRdGpuFromBucketId)(ConstSpanSizeC* out,
                                                            StageReaderWriterId stageId,
                                                            BucketId bucketId,
                                                            TokenC attrName);

    BucketId(CARB_ABI* addBucket)(StageReaderWriterId stageId, void* bucket);
    void(CARB_ABI* addPathToBucket)(StageReaderWriterId stageId, PathC path, void* bucket);
    BucketId(CARB_ABI* getBucketIdFromBucket)(StageReaderWriterId stageId, void* bucket);
    void(CARB_ABI* removeAttributeFromBucket)(StageReaderWriterId stageId, BucketId bucketId, TokenC attrName);
    SpanC(CARB_ABI* setArrayAttributeSizeAndGetByBucketId)(
        StageReaderWriterId stageId, BucketId bucketId, size_t elementIndex, TokenC attrName, size_t newSize);
    void(CARB_ABI* removeAttributesFromBucket)(StageReaderWriterId stageId,
                                               BucketId bucketId,
                                               TokenC const* attrNames,
                                               uint32_t attribCount);
    // Note that we also have addAttributesToBucket() for adding multiple
    // attributes, but it was added later so you'll need to scroll down to see
    // it.
    void(CARB_ABI* addAttributeToBucket)(StageReaderWriterId stageId,
                                         BucketId bucketId,
                                         TokenC attrName,
                                         Type attrType,
                                         void const* value,
                                         NameSuffix suffix);

    /** @brief Serialize all the data from a prim into a buffer to be passed to another cache
     *
     * @stageReaderWriterId[in] The stageReaderWriter with the Fabric to serialize
     * @prim[in] The prim that needs to be pulled out
     * @dest[in/out] Pointer to buffer to be written to, will start writing to head
     *       of pointer. dest will be left pointing to the point after the last write
     * @destSize Size of buffer that was allocated for the data (in bytes)
     *
     * @return Number of bytes written success is determined by (return <= @destSize)
     *          if return == 0 then prim did not exist
     *
     *
     * @invariant It is safe to write to any memory within[dest, dest+size] for the
     *            duration of the function call.
     *
     * @note If the cache will not fit into the size of memory allocated in
     *       @dest then it will stop writing, but continue to run the serialize
     *       algorithm to calculate the actual amount of data that needs to be
     *       written
     *
     */
    uint64_t(CARB_ABI* serializeFabricPrim)(StageReaderWriterId stageReaderWriterId,
                                            PathC pathc,
                                            uint8_t* dest,
                                            size_t destSize);

    /** @brief Given a buffer that has the serialized version of a prim written
     *         using the serializePrim function, this function attempt to add that prim to
     *         the cache
     *
     * @stageReaderWriterId[in] stageReaderWriter with the Fabric to be populated
     * @input[in] Pointer to buffer of data containing serialized cache
     * @inputSize[in] Size of data in the buffer
     *
     * @return True if buffer was successfully de-serialized
     */
    bool(CARB_ABI* deserializeFabricPrim)(StageReaderWriterId stageReaderWriterId,
                                          const uint8_t* input,
                                          const size_t inputSize);

    /** @brief Add multiple attributes to all prims in a bucket
     *
     * @stageId[in] The stage containing the bucket
     * @bucketId[in] The bucket to add the attributes to
     * @attrCreateSpecs[in] For each attribute to be created a spec containing
     *                      its name, type, (optional) initial value etc.
     */
    void(CARB_ABI* addAttributesToBucket)(StageReaderWriterId stageId,
                                          BucketId bucketId,
                                          const AttrCreateSpec* attrCreateSpecs,
                                          size_t attrCount);

    // MGPU versions of existing GPU functions that support specifying a particular device id on which the
    // attribute/array should be made available
    void(CARB_ABI* getAttributeArrayMGpuFromBucketId)(
        SpanC* out, StageReaderWriterId stageId, BucketId bucketId, TokenC attrName, int deviceId);

    void(CARB_ABI* getAttributeArrayRdMGpuFromBucketId)(
        ConstSpanC* out, StageReaderWriterId stageId, BucketId bucketId, TokenC attrName, int deviceId);

    void(CARB_ABI* getAttributeArrayWrMGpuFromBucketId)(
        SpanC* out, StageReaderWriterId stageId, BucketId bucketId, TokenC attrName, int deviceId);

    void(CARB_ABI* batchClone)(FabricId fabricId, const PathC sourceRootPath, Span<const PathC> destRootPaths);
};


} // namespace fabric
} // namespace omni
