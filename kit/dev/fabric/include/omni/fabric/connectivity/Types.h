// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once


namespace omni
{
namespace fabric
{
namespace connectivity
{

using EdgeType = uint8_t;

constexpr const EdgeType kInvalidEdgeType { 0 };
constexpr const EdgeType kParentEdgeType { 1 };
constexpr const EdgeType kChildEdgeType { 2 };
constexpr const EdgeType kParentDualEdgeType = kChildEdgeType;
constexpr const EdgeType kChildDualEdgeType = kParentEdgeType;
constexpr const EdgeType kFirstCustomEdgeType { 3 };
constexpr const uint64_t kDefaultEdgeMask = 0xffull;
constexpr const uint64_t kCounterGreaterThanZeroValue = ~0ull;
constexpr const uint64_t kCounterUndefinedValue = ~1ull;

struct EdgeId
{
    constexpr EdgeId() : id(~0ull){};
    constexpr EdgeId(uint64_t _id) : id(_id){};
    uint64_t id;
    constexpr bool operator==(const EdgeId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const EdgeId& other) const
    {
        return id != other.id;
    }
};

static_assert(std::is_standard_layout<EdgeId>::value, "Struct must be standard layout as it is used in C-ABI interfaces");
const EdgeId kInvalidEdgeId;

struct BakeId
{
    constexpr BakeId() : id(0){};
    constexpr BakeId(uint64_t _id) : id(_id){};
    uint64_t id;
    constexpr bool operator==(const BakeId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const BakeId& other) const
    {
        return id != other.id;
    }
};

static_assert(std::is_standard_layout<BakeId>::value, "Struct must be standard layout as it is used in C-ABI interfaces");
const BakeId kInvalidBakeId;

struct SelectionId
{
    constexpr SelectionId() : id(0){};
    constexpr SelectionId(uint64_t _id) : id(_id){};
    uint64_t id;
    constexpr bool operator==(const SelectionId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const SelectionId& other) const
    {
        return id != other.id;
    }
};

static_assert(std::is_standard_layout<SelectionId>::value, "Struct must be standard layout as it is used in C-ABI interfaces");
const SelectionId kInvalidSelectionId;

//! @struct Filter
//! @brief A filtering data-structure. Components matching all the following criteria will be selected.
//! @param attributes_rd List of attribute types to read only. If not empty, a component has to match one attribute definition in this list to be selected.
//! @param attributes_wr List of attribute types to write only. If not empty, a component has to match one attribute definition in this list to be selected.
//! @param attributes_rw List of attribute types to read and write. If not empty, a component has to match one attribute definition in this list to be selected.
//! @param paths List of paths. If not empty, a component has to match one path in this list to be selected.
//! @param tags List of tag-names: If not empty, a component has to match one tag in this list to be selected.
//! @param edgdes If not empty, a component has to match one edge in this list to be selected.
//! @param connections If not empty, a component has to match one connection type in this list to be selected.

struct Filter
{
    Span<const AttrNameAndType> attributes_rd;
    Span<const AttrNameAndType> attributes_wr;
    Span<const AttrNameAndType> attributes_rw;
    Span<const Path> paths;
    Span<const Token> tags;
    Span<const Token> connections;
    Span<const EdgeId> egdes;
    Span<const BucketId> bucketIds;
};

static_assert(std::is_standard_layout<Filter>::value, "Struct must be standard layout as it is used in C-ABI interfaces");

enum struct Algorithm
{
    DFS = 0,
    BFS = 1,
    Default = DFS,

    DirectMapping = 10,
    RecursiveMapping = 11,
    ComposedMapping = 12,
    DefaultMapping = DirectMapping,
};

struct Navigator
{
    void* getUserData();
    size_t getVisitId();
    EdgeId getEdgeId();
    uint64_t getEdgeValue();
    void pruneChildren();
    void pruneSiblings();
    void deleteSrcPrim(); // delete the src prim
    void deleteDstPrim(); // delete the dst prim
    void updateSrcPrim(); // update all the writable attributes of the current src prim
    void updateDstPrim(); // update all the writable attributes of the current dst prim
    void terminate();
};

static_assert(std::is_standard_layout<Navigator>::value, "Struct must be standard layout as it is used in C-ABI interfaces");

template <typename NavigatorFunction>
struct NavigatorParameters
{
    Algorithm algorithm = Algorithm::Default;
    SelectionId sid = kInvalidSelectionId;
    PathC fromPath = 0;
    NavigatorFunction* pre = nullptr;
    NavigatorFunction* post = nullptr;
    void* userData = nullptr;
};

enum TransformVisit
{
    Start,
    Descendant,
};

enum ExtentVisit
{
    First,
    Next,
};

using VisitorFunctionPath_t = void(const PathC* firstPath, const PathC* lastPath, void* userData);

using VisitorFunctionRd_t = void(const void** dstAttributes, const void** srcAttributes, size_t dstIndex, size_t srcIndex, void* userData);
using VisitorFunctionWr_t = void(void** dstAttributes, void** srcAttributes, size_t dstIndex, size_t srcIndex, void* userData);

using TransformFunctionWr_t = void(void** dstAttributes, void** srcAttributes, size_t dstIndex, size_t srcIndex, void* userData, TransformVisit what);
using ExtentFunctionWr_t = void(const void** dstAttributes, const void** srcAttributes, size_t dstIndex, size_t srcIndex, void* userData, ExtentVisit what);

using NavigatorFunctionRd_t = void(const void** dstAttributes, const void** srcAttributes, size_t dstIndex, size_t srcIndex, Navigator& nav);
using NavigatorFunctionWr_t = void(void** dstAttributes, void** srcAttributes, size_t dstIndex, size_t srcIndex, Navigator& nav);

using NavigatorParametersRd_t = NavigatorParameters<NavigatorFunctionRd_t>;
using NavigatorParametersWr_t = NavigatorParameters<NavigatorFunctionWr_t>;

template <typename T>
inline const T* argRd(const void** base, size_t rowIdx, size_t attrIdx, size_t attrDim = 1)
{
    return base[attrIdx] ? reinterpret_cast<const T*>(base[attrIdx]) + rowIdx * attrDim : nullptr;
}

template <typename T>
inline T* argWr(void** base, size_t rowIdx, size_t attrIdx, size_t attrDim = 1)
{
    return base[attrIdx] ? reinterpret_cast<T*>(base[attrIdx]) + rowIdx * attrDim : nullptr;
}

struct PerformanceCounters
{
    size_t queryCreateCnt = 0;
    size_t queryCacheHitCnt = 0;
    size_t queryCacheInsertCnt = 0;
    size_t queryCacheReplaceCnt = 0;
    size_t visitedPrimCnt = 0;          // Amount of prims visited
    size_t visitedAttributeCnt = 0;     // Amount of attributes visited
    size_t visitedBytesCnt = 0;         // Amount of bytes visited
    size_t visitedWritableCnt = 0;      // Amount of writable attributes visited
    size_t modifiedWritableCnt = 0;     // Amount of writable attributes effectively modified in memory
};

} // namespace connectivity
} // namespace fabric
} // namespace omni
