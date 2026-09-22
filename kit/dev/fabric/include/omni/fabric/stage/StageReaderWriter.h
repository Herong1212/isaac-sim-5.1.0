// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/Interface.h>
#include <carb/logging/Log.h>

#include <omni/fabric/core/AttrNameAndType.h>

#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/core/interface/IPath.h>
#include <omni/fabric/core/interface/IToken.h>

#include <omni/fabric/stage/Column.h>
#include <omni/fabric/stage/PrimBucketList.h>
#include <omni/fabric/stage/PrimChanges.h>
#include <omni/fabric/stage/SimStageWithHistory.h>

#include <gsl/span>
#include <stdint.h>

namespace omni
{
namespace fabric
{

class StageReaderWriterUsd;

class StageReaderWriter
{
    StageReaderWriterId m_stageReaderWriter;
    IStageReaderWriter* m_interface;
    friend class StageReaderWriterUsd;

public:
    StageReaderWriter();
    StageReaderWriter(StageReaderWriterId stageId);
    StageReaderWriter(FabricId fabricId);
    
    StageReaderWriter(const StageReaderWriter& other);
    StageReaderWriter& operator=(const StageReaderWriter& other);

    StageReaderWriter(StageReaderWriter&& other);
    StageReaderWriter& operator=(StageReaderWriter&& other);
    
    ~StageReaderWriter();

    /** @brief Get the FabricId for the StageReaderWriter.  This can be used
     * with the IFabric/IFabricUsd interfaces.
     *
     * @return the id of the working fabric space.
     */
    FabricId getFabricId() const;

    StageReaderWriterId getId() const;

    // TODO: replace with an iterator for iterating over bucket names
    void printBucketNames() const;

    //-------------------------------Prims/Attributes-------------------------------
    /**
     * @brief Check whether a prim exists at a given path
     * @param[in] the path
     * @return true if a prim exists at the path
     */
    bool primExists(const Path& path);

    // Returns which mirrored array is valid: CPU, GPU, etc.
    ValidMirrors getAttributeValidBits(const Path& path, const Token& attrName) const;

    // getAttribute returns a read/write pointer to a non-array attribute
    // If it returns nullptr then the attribute doesn't exist in the stage
    template <typename T>
    T* getAttribute(const Path& path, const Token& attrName);

    // getAttribute returns a read-only pointer to a non-array attribute
    // If it returns nullptr then the attribute doesn't exist in the stage
    template <typename T>
    const T* getAttributeRd(const Path& path, const Token& attrName);

    // getAttribute returns a write-only pointer to a non-array attribute
    // If it returns nullptr then the attribute doesn't exist in the stage
    template <typename T>
    T* getAttributeWr(const Path& path, const Token& attrName);

    // getAttribute returns a read/write pointer to a non-array attribute
    // If it returns nullptr then the attribute doesn't exist in the stage
    template <typename T>
    T* getAttributeGpu(const Path& path, const Token& attrName, int deviceId = 0);

    // getAttribute returns a read-only pointer to a non-array attribute
    // If it returns nullptr then the attribute doesn't exist in the stage
    template <typename T>
    const T* getAttributeRdGpu(const Path& path, const Token& attrName, int deviceId = 0);

    // getAttribute returns a write-only pointer to a non-array attribute
    // If it returns nullptr then the attribute doesn't exist in the stage
    template <typename T>
    T* getAttributeWrGpu(const Path& path, const Token& attrName, int deviceId = 0);

    // getOrCreateAttributeWr returns a write-only pointer to a non-array
    // attribute. If the attribute doesn't exist, then it will create it.
    template <typename T>
    T* getOrCreateAttributeWr(const Path& path, const Token& attrName, Type type);

    // getAttribute returns a read/write span of an array attribute
    // The span allows the array size to be read, but not written
    // To set the array size, use setArrayAttributeSize
    template <typename T>
    gsl::span<T> getArrayAttribute(const Path& path, const Token& attrName);

    // getAttributeRd returns a read-only span of an array attribute
    // The array size is also read only
    template <typename T>
    gsl::span<const T> getArrayAttributeRd(const Path& path, const Token& attrName);

    // getAttributeRd returns a write-only span of an array attribute
    // The array size is read only, to resize use setArrayAttributeSize
    template <typename T>
    gsl::span<T> getArrayAttributeWr(const Path& path, const Token& attrName);

    // Get the size of an array attribute. When writing CPU code, it isn'tF
    // normally necessary to use this method, as getArrayAttribute returns a
    // span containing the data pointer and the size.
    // However, when writing mixed CPU/GPU code it is wasteful to copy the
    // array data from GPU to CPU when just the size is required, so use this
    // method in that case.
    size_t getArrayAttributeSize(const Path& path, const Token& attrName);

    size_t* getArrayAttributeSizePtr(const Path& path, const Token& attrName);
    const size_t* getArrayAttributeSizeRdPtr(const Path& path, const Token& attrName);
    size_t* getArrayAttributeSizeWrPtr(const Path& path, const Token& attrName);
    const size_t* getArrayAttributeSizeRdGpuPtr(const Path& path, const Token& attrName);

    // Set the size of an array attribute
    void setArrayAttributeSize(const Path& path, const Token& attrName, size_t elemCount);

    // Get an attribute's type
    Type getType(const Path& path, const Token& attrName);

    // Get prim's attribute count
    size_t getAttributeCount(const Path& path);

    /** @brief Get the names and tyes associated with a given prim
     *
     * @path[in] the path of the prim to check
     *
     * returns a vector of the attribute name and types;
     */
    std::vector<AttrNameAndType> getAttrNamesAndTypes(const Path& path);

    // createPrim, destroyPrim, createAttribute and destroyAttribute do what
    // you'd expect
    void createPrim(const Path& path);
    void createPrims(const Span<const PathC>& paths, const Span<AttrNameAndType>& attributes, CreatePrimOptions createPrimOptions);
    void destroyPrim(const Path& path);
    void destroyPrims(Span<PathC const> paths);
    void movePrim(const Path& oldPath, const Path& newPath);

    void createAttribute(const Path& path, const Token& attrName, Type type);
    template <size_t n>
    void createAttributes(const Path& path, std::array<AttrNameAndType, n> attributes);
    void createAttributes(const Path& path, std::vector<AttrNameAndType> attributes);
    bool attributeExists(const Path& path, const Token& attrName) const;
    bool attributeExistsWithType(const Path& path, const Token& attrName, Type type) const;

    // Deprecated: type argument is not used.
    void destroyAttribute(const Path& path, const Token& attrName, Type type);
    void destroyAttribute(const Path& path, const Token& attrName);
    template <size_t n>
    void destroyAttributes(const Path& path, const std::array<Token, n>& attributes);
    void destroyAttributes(const Path& path, const std::vector<Token>& attributes);

    void setPrimTypeName(const Path& path, const Token& typeName);
    /** @brief Get the USD type name of a prim
     *
     * @path[in] The path of the prim
     *
     * @return The USD type name of the prim
     */
    Token getPrimTypeName(const Path& path);

    /** @brief Get the names and types of a prim's attributes
     *
     * @path[in] The path of the prim
     *
     * @return The names and types
     */
    std::pair<std::vector<Token>, std::vector<Type>> getAttributeNamesAndTypes(const Path& path);


    /**
     * @brief Copy all attributes from the source prim to the destination prim
     * Will create attributes if they do not exist on the destination prim
     * If an attribute exists on both prims they must have compatible types to copy.
     *
     * @param[in] srcPath the source prim
     * @param[in] dstPath the destination prim
     */
    void copyAttributes(const Path& srcPath, const Path& dstPath);

    /**
     * @brief Copy the specified attributes from the source prim to the destination prim
     * Will create attributes if they do not exist on the destination prim
     * If an attribute exists on both prims they must have compatible types to copy.
     *
     * @param[in] srcPath the source prim
     * @param[in] srcAttrs a span of attributes to be copied.
     * @param[in] dstPath the destination prim
     */
    void copyAttributes(const Path& srcPath, const gsl::span<Token>& srcAttrs, const Path& dstPath);

    /**
     * @brief Copy the specified attributes from the source prim to the the specified
     * attributes on the destination prim
     * Will create attributes if they do not exist on the destination prim
     * If an attribute exists on both prims they must have compatible types to copy.
     * Note: The srcAttrs and dstAttrs must be the same size as the function assumes
     * that the copy is 1 to 1 in terms of name alignment
     *
     * @param[in] srcPath the source prim
     * @param[in] srcAttrs a span of attributes to be copied.
     * @param[in] dstPath the destination prim
     * @param[in] dstAttrs a span of attributes to be copied.
     */
    void copyAttributes(const Path& srcPath,
                        const gsl::span<Token>& srcAttrs,
                        const Path& dstPath,
                        const gsl::span<Token>& dstAttrs);

    // wrappers for tags
    void createTag(const Path& path, const Token& attrName);
    void destroyTag(const Path& path, const Token& attrName);
    bool tagExists(const Path& path, const Token& attrName) const;

    //-----------------PrimBucketList Operations-----------------------------------

    // Returns every prim in the fabric cache.
    // The attributes of the resulting prims can be accessed as piecewise
    // contiguous arrays, using getAttributeArray() below, which is typically
    // faster than calling getAttribute for each prim.
    PrimBucketList allPrims();

    // findPrims() finds prims that have all the attributes in "all", and any
    // of the attributes in "any", and none of the attributes in "none".
    // The attributes of the resulting prims can be accessed as piecewise
    // contiguous arrays, using getAttributeArray() below, which is typically
    // faster than calling getAttribute for each prim.
    PrimBucketList findPrims(const omni::fabric::set<AttrNameAndType>& all,
                             const omni::fabric::set<AttrNameAndType>& any = {},
                             const omni::fabric::set<AttrNameAndType>& none = {});

    /** @brief Get the USD type of the prims in a bucket
     *
     * @stageId[in] The stage containing the prim
     * @primBucketList[in] The primBucketList
     * @primBucketListIndex[in] The index of the bucket within the primBucketList
     *
     * @return The USD type name of the prims in the bucket
     */
    Token getBucketPrimTypeName(PrimBucketListId primBucketList, size_t primBucketListIndex);

    ArrayPointersAndSizesWithTypeC getArrayAttributeArrayWithSizesGpu(PrimBucketListId primBucketList,
                                                              size_t primBucketListIndex,
                                                              const Token& attrName);

    ConstArrayPointersAndSizesWithTypeC getArrayAttributeArrayWithSizesRdGpu(PrimBucketListId primBucketList,
                                                                     size_t primBucketListIndex,
                                                                     const Token& attrName);

    ArrayPointersAndSizesWithTypeC getArrayAttributeArrayWithSizesWrGpu(PrimBucketListId primBucketList,
                                                                size_t primBucketListIndex,
                                                                const Token& attrName);

    template <typename T>
    gsl::span<T> setArrayAttributeSizeAndGet(const PrimBucketList& primBucketList,
                                             size_t primBucketListIndex,
                                             size_t indexInBucket,
                                             const Token& attrName,
                                             size_t newElemCount);

    // getAttributeArray(primBucketList, index, attrName) returns a read/write
    // contiguous array of the values of attribute "attrName" for each prim of
    // bucket "index" of "primBucketList".
    // "index" must be in the range [0..primBucketList.getBucketCount())
    template <typename T>
    gsl::span<T> getAttributeArray(const PrimBucketList& primBucketList, size_t primBucketListIndex, const Token& attrName);

    template <typename T>
    Column<T> getAttributeColumn(const PrimBucketList& primBucketList, size_t primBucketListIndex, const Token& attrName);

    template <typename T>
    gsl::span<const T> getAttributeArrayRd(const PrimBucketList& primBucketList,
                                           size_t primBucketListIndex,
                                           const Token& attrName) const;

    template <typename T>
    gsl::span<const T> getAttributeColumnRd(const PrimBucketList& primBucketList,
                                            size_t primBucketListIndex,
                                            const Token& attrName) const;

    template <typename T>
    gsl::span<T> getAttributeArrayWr(const PrimBucketList& primBucketList,
                                     size_t primBucketListIndex,
                                     const Token& attrName);

    template <typename T>
    Column<T> getAttributeColumnWr(const PrimBucketList& primBucketList,
                                   size_t primBucketListIndex,
                                   const Token& attrName);

    template <typename T>
    gsl::span<T> getAttributeArrayGpu(const PrimBucketList& primBucketList,
                                      size_t primBucketListIndex,
                                      const Token& attrName,
                                      int deviceId = 0);

    template <typename T>
    gsl::span<const T> getAttributeArrayRdGpu(const PrimBucketList& primBucketList,
                                              size_t primBucketListIndex,
                                              const Token& attrName,
                                              int deviceId = 0) const;

    template <typename T>
    gsl::span<T> getAttributeArrayWrGpu(const PrimBucketList& primBucketList,
                                        size_t primBucketListIndex,
                                        const Token& attrName,
                                        int deviceId = 0);

    template <typename T>
    gsl::span<T> getOrCreateAttributeArrayWr(const PrimBucketList& primBucketList,
                                             size_t primBucketListIndex,
                                             const Token& attrName,
                                             Type type);

    // getAttributeArray(primBucketList, index, attrName) returns a vector of
    // array-valued attributes "attrName" for the prims of bucket "index" of
    // "primBucketList". "index" must be in the range [0..primBucketList.getBucketCount())
    // It gives read/write access to the values of each prim's array
    template <typename T>
    std::vector<gsl::span<T>> getArrayAttributeArray(const PrimBucketList& primBucketList,
                                                     size_t primBucketListIndex,
                                                     const Token& attrName) const;

    template <typename T>
    Column<gsl::span<T>> getArrayAttributeColumn(const PrimBucketList& primBucketList,
                                                 size_t primBucketListIndex,
                                                 const Token& attrName);

    // getAttributeArray(primBucketList, index, attrName) returns a vector of
    // array-valued attributes "attrName" for the prims of bucket "index" of
    // "primBucketList". "index" must be in the range [0..primBucketList.getBucketCount())
    // It gives read-only access to the values of each prim's array
    template <typename T>
    std::vector<gsl::span<const T>> getArrayAttributeArrayRd(const PrimBucketList& primBucketList,
                                                             size_t primBucketListIndex,
                                                             const Token& attrName) const;

    template <typename T>
    std::vector<gsl::span<const T>> getArrayAttributeColumnRd(const PrimBucketList& primBucketList,
                                                              size_t primBucketListIndex,
                                                              const Token& attrName) const;

    // getAttributeArray(primBucketList, index, attrName) returns a vector of
    // array-valued attributes "attrName" for the prims of bucket "index" of
    // "primBucketList". "index" must be in the range [0..primBucketList.getBucketCount())
    // It gives read-only access to the values of each prim's array when they are present and not sparsely populated
    //   or
    // It returns a content hash for a sparsely populated attribute and {nullptr,0} as the span for that attribute value
    template <typename T>
    std::vector<std::pair<gsl::span<const T>, ContentHashType>> getArrayAttributeArrayOrHashRd(
        const PrimBucketList& primBucketList,
        size_t primBucketListIndex,
        const Token& attrName) const;

    std::vector<ContentHashType> getArrayAttributeHashRd(const PrimBucketList& primBucketList,
                                                         size_t primBucketListIndex,
                                                         const Token& attrName) const;

    // getAttributeArray(primBucketList, index, attrName) returns a vector of
    // array-valued attributes "attrName" for the prims of bucket "index" of
    // "primBucketList". "index" must be in the range [0..primBucketList.getBucketCount())
    // It gives write-only access to the values of each prim's array
    template <typename T>
    std::vector<gsl::span<T>> getArrayAttributeArrayWr(const PrimBucketList& primBucketList,
                                                       size_t primBucketListIndex,
                                                       const Token& attrName) const;

    template <typename T>
    Column<gsl::span<T>> getArrayAttributeColumnWr(const PrimBucketList& primBucketList,
        size_t primBucketListIndex,
        const Token& attrName);

    // Triggers change tracking for all elements of the given attribute in the
    // range [beginElem, endElem)
    void dirtyAttribute(const PrimBucketList& primBucketList,
        size_t primBucketListIndex,
        const Token& attrName,
        size_t beginElem, size_t endElem) const;

    // getPathArray(primBucketList, index) returns a read-only contiguous array
    // of the paths of the prims of bucket "index" of "primBucketList".
    // "index" must be in the range [0..primBucketList.getBucketCount())
    gsl::span<const Path> getPathArray(const PrimBucketList& primBucketList, size_t primBucketListIndex) const;

    omni::fabric::set<AttrNameAndType> getAttributeNamesAndTypes(const PrimBucketList& primBucketList,
                                                                 size_t primBucketListIndex) const;

    /** @brief Get the USD type name of the prims in a bucket
     *
     * @primBucketList[in] The primBucketList
     * @primBucketListIndex[in] The index of the bucket within the primBucketList
     *
     * @return The USD type name of the prims in the bucket
     */
    Token getPrimTypeName(const PrimBucketList& primBucketList, size_t primBucketListIndex) const;

    size_t getBucketPrimCount(PrimBucketListId primBucketList, size_t primBucketListIndex, const Token& attrName);

    size_t getBucketAttributeCount(PrimBucketListId primBucketList, size_t primBucketListIndex);

    std::vector<AttrNameAndType> getBucketAttributeNamesAndTypes(PrimBucketListId primBucketList,
                                                                 size_t primBucketListIndex);

    // Get the number of attributes for a given bucket.
    size_t getAttributeCount(const PrimBucketList& primBucketList, size_t primBucketListIndex) const;


    // ------------------------------Change Tracking -------------------------------

    /**
     * Tell a listener to log changes for an attribute.
     * Attaches listener to stage if not already attached
     *
     * @param[in] attrName The attribute's name
     * @param[in] listenerId The listener
     */
    void attributeEnableChangeTracking(const Token& attrName, ListenerId listenerId);

    /**
     * Tell a listener to stop logging changes for an attribute.
     * Attaches listener to stage if not already attached
     *
     * @param[in] attrName The attribute's name
     * @param[in] listenerId The listener
     */
    void attributeDisableChangeTracking(const Token& attrName, ListenerId listenerId);

    /**
     * Tell a listener to log prim creates
     * Attaches listener to stage if not already attached
     *
     * @param[in] attrName The attribute's name
     * @param[in] listenerId The listener
     */
    void enablePrimCreateTracking(ListenerId listenerId);

    /**
     * Pause change tracking.
     *
     * @param[in] listenerId The listener to pause
     */
    void pauseChangeTracking(ListenerId listenerId);

    /**
     * Resume change tracking.
     *
     * @param[in] listenerId The listener to resume
     */
    void resumeChangeTracking(ListenerId listenerId);

    /**
     * Is change tracking paused?
     *
     * @param[in] listenerId The listener
     * @return Whether the listener is paused
     */
    bool isChangeTrackingPaused(ListenerId listenerId);

    /**
     * Get changes
     *
     * @param[in] listenerId The listener
     * @return The changes that occured since the last time the listener was popped
     */
    ChangedPrimBucketList getChanges(ListenerId listenerId);

    /**
     * Clear the list of changes
     *
     * @param[in] listenerId The listener
     */
    void popChanges(ListenerId listenerId);

    /**
     * Get the number of listeners
     *
     * @return The number of listeners listening to this stage
     */
    size_t getListenerCount();

    /**
     * Is the listener attached to this stage
     *
     * @return Whether the listener is attached to this stage
     */
    bool isListenerAttached(ListenerId listenerId);

    /**
     * Detach the listener from the stage. Future changes will not be logged for this listener.
     *
     * @param[in] listenerId The listener
     * @return Whether the listener is attached to this stage
     */
    void detachListener(ListenerId listenerId);

    // Record that the attribute at path.attrName has been modified. Right now this is
    // done explicitly to give a high degree of control over which attributes get
    // passed to the notice.
    void logAttributeWriteForNotice(const Path& path, const Token& attrName);

    // Construct and send a TfNotice with a vector of objects paths
    // that have changed, much like the ObjectsChanged notice from USD
    void broadcastTfNoticeForAttributesChanged() const;

    //------------------------- Connection API ---------------------------------
    /**
     * @brief Create a connection on the target prim
     *
     * @param path the target prim on which to create a connection
     * @param connectionName specifies the connections attribute name on the prim
     * @param connection specifies the target prim and attribute of the connection
     */
    void createConnection(const Path& path, const Token& connectionName, const Connection& connection);

    /**
     * @brief Create an arbitrary number of connections on the target prim
     *
     * @param path the target prim on which to create a connection
     * @param connectionNames a span of attribute names. Must match the size of the connections vector
     * @param connections a span of connections. Must match the size of the connectionNames vector
     */
    void createConnections(const Path& path,
                           const gsl::span<Token>& connectionNames,
                           const gsl::span<Connection>& connections);

    /**
     * @brief removes a connection from a prim
     *
     * @param path the target prim from which to remove a connection
     * @param connectionName the name of the connection to remove
     */
    void destroyConnection(const Path& path, const Token& connectionName);

    /**
     * @brief removes an arbitary number of connections from a prim
     *
     * @param path the target prim from which to remove the connections
     * @param connectionNames the names of the connections to be removed
     */
    void destroyConnections(const Path& path, const gsl::span<Token>& connectionNames);

    /**
     * @brief Get a R/W pointer to a connection on the target prim
     *
     * @param path the target prim
     * @param connectionName the target connection name
     * @return a R/W pointer to the connection
     */
    Connection* getConnection(const Path& path, const Token& connectionName);

    /**
     * @brief Get a read only pointer to a connection on the target prim
     *
     * @param path the target prim
     * @param connectionName the target connection name
     * @return a read only pointer to the connection
     */
    const Connection* getConnectionRd(const Path& path, const Token& connectionName);

    /**
     * @brief Get a write only pointer to a connection on the target prim
     *
     * @param path the target prim
     * @param connectionName the target connection name
     * @return  a write only pointer to the connection
     */
    Connection* getConnectionWr(const Path& path, const Token& connectionName);

    /**
     * @brief tells fabric that all writes are complete across all memory in the Fabric, 
     *        which allows for all memory to be cheaply copied by reference
     */
    void commit();

    /**
     * @brief tally the mutable internal structures in the stage (which should be 0 after a close() operation)
     * @return the number of mutable internal structures in the stage
     */
    size_t getMutableEntityCount() const;

    /**
     * @brief Register a token with the ObjectDirectory, which will store a counted ref which is released at destruction
     * @return the index in the ObjectDirectory that this token occupies. This is stable until the fabric is destroyed
     */
    size_t registerToken(const Token& token);

    /**
     * @brief Register tokens with the ObjectDirectory, which will store a counted ref which is released at destruction
     */
    void registerTokens(const gsl::span<const Token>& tokens, const gsl::span<size_t>& indexes = gsl::span<size_t>());

    /**
     * @brief Register a path with the ObjectDirectory, which will store a counted ref which is released at destruction
     * @return the index in the ObjectDirectory that this token occupies. This is stable until the fabric is destroyed
     */
    size_t registerPath(const Path& path);

    /**
     * @brief Register paths with the ObjectDirectory, which will store a counted ref which is released at destruction
     */
    void registerPaths(const gsl::span<const Path>& paths, const gsl::span<size_t>& indexes = gsl::span<size_t>());

    /**
     * @brief Test a bucket of a PrimBucketList against a findPrims-like filter
     * @return true if the specified bucket passes the filter defined by all, any, none in the same way as for findPrims()
     */
    bool acceptBucket(const PrimBucketList& primBucketList, size_t bucketIndex,
        const omni::fabric::set<AttrNameAndType>& all,
        const omni::fabric::set<AttrNameAndType>& any,
        const omni::fabric::set<AttrNameAndType>& none);
};

} // namespace fabric
} // namespace omni

#include <omni/fabric/stage/impl/StageReaderWriter.inl>
