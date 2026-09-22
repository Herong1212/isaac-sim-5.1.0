// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,...) inline ReturnType WrapperName::FuncName(__VA_ARGS__)
#define FABRIC_BIND_DEFN(FuncName,...) { CARB_ASSERT(capi); const auto call = [&]() { return capi->FuncName(__VA_ARGS__); }; CARB_UNUSED(call);
#define FABRIC_BIND_CALL() return call(); }

#define FABRIC_BIND_0_W_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName,fabricId)
#define FABRIC_BIND_1_W_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName,fabricId,a1)
#define FABRIC_BIND_2_W_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName,fabricId,a1,a2)
#define FABRIC_BIND_3_W_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName,fabricId,a1,a2,a3)
#define FABRIC_BIND_4_W_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName,fabricId,a1,a2,a3,a4)

#define FABRIC_BIND_0_NO_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName)
#define FABRIC_BIND_1_NO_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName,a1)
#define FABRIC_BIND_2_NO_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName,a1,a2)
#define FABRIC_BIND_3_NO_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName,a1,a2,a3)
#define FABRIC_BIND_4_NO_FID(WrapperName,ReturnType,FuncName,...) FABRIC_BIND_DECL(WrapperName,ReturnType,FuncName,##__VA_ARGS__) FABRIC_BIND_DEFN(FuncName,a1,a2,a3,a4)

#define FABRIC_ASSERT_OR_RETURN(cond,retvalue) do { const bool b = !!(cond); CARB_ASSERT(b); if(!b) return (retvalue); } while(0)

#include "IConnectivity.h"

#include <omni/fabric/stage/StageReaderWriter.h>

namespace omni
{
namespace fabric
{

inline Connectivity::Connectivity(FabricId fabricId_, IConnectivity* capi_) : fabricId(fabricId_)
{
    CARB_ASSERT(fabricId_ != kInvalidFabricId);
    capi = capi_ ? capi_ : carb::getCachedInterface<IConnectivity>();
    CARB_ASSERT(capi != nullptr);
}

inline bool Connectivity::pushConnectionType(uint64_t value_, uint64_t dualValue_, uint64_t mask_)
{
    FABRIC_ASSERT_OR_RETURN(value_ != connectivity::kInvalidEdgeType, false);
    FABRIC_ASSERT_OR_RETURN(dualValue_ != connectivity::kInvalidEdgeType, false);
    FABRIC_ASSERT_OR_RETURN(value_ != dualValue_, false);
    FABRIC_ASSERT_OR_RETURN(mask_ >= connectivity::kDefaultEdgeMask, false);

    const size_t capacity = std::size(value);
    FABRIC_ASSERT_OR_RETURN(top+1 < capacity, false);

    top += 1;
    value[top] = value_;
    dualValue[top] = dualValue_;
    mask[top] = mask_;
    return true;
}

inline bool Connectivity::pushConnectionType(const EdgeType type, const EdgeType dualType)
{
    FABRIC_ASSERT_OR_RETURN(type != connectivity::kInvalidEdgeType, false);
    FABRIC_ASSERT_OR_RETURN(dualType != connectivity::kInvalidEdgeType, false);
    FABRIC_ASSERT_OR_RETURN(type != dualType, false);
    return pushConnectionType(type, dualType, connectivity::kDefaultEdgeMask);
}

inline bool Connectivity::pushConnectionType(const Token& typeName, const Token& dualTypeName)
{
    FABRIC_ASSERT_OR_RETURN(typeName != kUninitializedToken, false);
    FABRIC_ASSERT_OR_RETURN(dualTypeName != kUninitializedToken, false);
    FABRIC_ASSERT_OR_RETURN(typeName != dualTypeName, false);
    const EdgeType t = setType(typeName);
    const EdgeType dt = setType(dualTypeName);
    return pushConnectionType(t, dt);
}

inline void Connectivity::popConnectionType(unsigned n)
{
    CARB_ASSERT(n <= top);
    if(n >= top)
        top = 0;
    else
        top -= n;
}

inline void Connectivity::swapConnectionType()
{
    std::swap(value[top], dualValue[top]);
}

inline void Connectivity::resetConnectionType()
{
    top = 0;
    value[0] = kDefaultValue;
    dualValue[0] = kDefaultDualValue;
    mask[0] = kDefaultMask;
}

inline uint64_t Connectivity::currentConnectionTypeValue() const
{
    CARB_ASSERT(top < std::size(value));
    return value[top];
}

inline uint64_t Connectivity::currentConnectionTypeDualValue() const
{
    CARB_ASSERT(top < std::size(dualValue));
    return dualValue[top];
}

inline uint64_t Connectivity::currentConnectionTypeMask() const
{
    CARB_ASSERT(top < std::size(mask));
    return mask[top];
}

FABRIC_BIND_1_W_FID(Connectivity, Connectivity::EdgeType, setType, const Token& a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_W_FID(Connectivity, TokenC, getTypeName, EdgeType a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_DECL(Connectivity, Connectivity::EdgeId, connect, const Path& a1, const Path& a2)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    return capi->connect(fabricId, a1, a2, value[top], dualValue[top]);
}

FABRIC_BIND_DECL(Connectivity, Connectivity::EdgeId, connectIfNot, const Path& a1, const Path& a2, bool* outAlreadyConnected)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    return capi->connectIfNot(fabricId, a1, a2, value[top], dualValue[top], outAlreadyConnected);
}

FABRIC_BIND_DECL(Connectivity, bool, disconnect, const Path& a1, const Path& a2)
{
    CARB_ASSERT(value[top]);
    return capi->disconnect(fabricId, a1, a2, value[top]);
}

FABRIC_BIND_DECL(Connectivity, bool, disconnectSource, const Path& a1)
{
    CARB_ASSERT(value[top]);
    return capi->disconnectSource(fabricId, a1, value[top]);
}

FABRIC_BIND_1_W_FID(Connectivity, bool, disconnectEdge, EdgeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, bool, disconnectEdges, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_W_FID(Connectivity, size_t, sumDegree, const Path& a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_DECL(Connectivity, size_t, countDegree, const Path& a1)
{
    CARB_ASSERT(value[top]);
    return capi->countDegree(fabricId, a1, value[top]);
}

FABRIC_BIND_1_W_FID(Connectivity, Connectivity::EdgeId, getFirstEdge, const Path& a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_DECL(Connectivity, Connectivity::EdgeId, findFirstEdge, const Path& a1)
{
    CARB_ASSERT(value[top]);
    return capi->findFirstEdge(fabricId, a1, value[top]);
}

FABRIC_BIND_DECL(Connectivity, Connectivity::EdgeId, findEdge, const Path& a1, const Path& a2)
{
    CARB_ASSERT(value[top]);
    return capi->findEdge(fabricId, a1, a2, value[top]);
}

FABRIC_BIND_1_W_FID(Connectivity, bool, isValid, EdgeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_W_FID(Connectivity, PathC, getSource, EdgeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_W_FID(Connectivity, PathC, getTarget, EdgeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_W_FID(Connectivity, Connectivity::EdgeId, getDual, EdgeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_W_FID(Connectivity, Connectivity::EdgeId, getNext, EdgeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_W_FID(Connectivity, uint64_t, getEdgeValue, EdgeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_W_FID(Connectivity, void, setEdgeValue, EdgeId a1, uint64_t a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_W_FID(Connectivity, Connectivity::EdgeId, getNextAtSource, EdgeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_W_FID(Connectivity, Connectivity::EdgeId, getNextAtTarget, EdgeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_W_FID(Connectivity, Connectivity::EdgeId, getNextAtSourceWithin, EdgeId a1, SelectionId a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_W_FID(Connectivity, Connectivity::EdgeId, getNextAtTargetWithin, EdgeId a1, SelectionId a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_DECL(Connectivity, Connectivity::EdgeId, findNextAtSource, EdgeId a1)
{
    CARB_ASSERT(value[top]);
    return capi->findNextAtSource(fabricId, a1, value[top]);
}

FABRIC_BIND_DECL(Connectivity, Connectivity::EdgeId, findNextAtTarget, EdgeId a1)
{
    CARB_ASSERT(value[top]);
    return capi->findNextAtTarget(fabricId, a1, value[top]);
}

FABRIC_BIND_DECL(Connectivity, Connectivity::EdgeId, findNextAtSourceWithin, EdgeId a1, const SelectionId a2)
{
    CARB_ASSERT(value[top]);
    return capi->findNextAtSourceWithin(fabricId, a1, value[top], a2);
}

FABRIC_BIND_DECL(Connectivity, Connectivity::EdgeId, findNextAtTargetWithin, EdgeId a1, const SelectionId a2)
{
    CARB_ASSERT(value[top]);
    return capi->findNextAtTargetWithin(fabricId, a1, value[top], a2);
}

FABRIC_BIND_0_W_FID(Connectivity, Connectivity::BakeId, bakeBegin)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_NO_FID(Connectivity, Connectivity::SelectionId, bakeSelectAttributes, BakeId a1, const Filter& a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_4_NO_FID(Connectivity, Connectivity::SelectionId, bakeSelectPrims, BakeId a1, const Filter& a2, const Filter& a3, const Filter& a4)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_4_NO_FID(Connectivity, Connectivity::SelectionId, bakeSelectBuckets, BakeId a1, const Filter& a2, const Filter& a3, const Filter& a4)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_4_NO_FID(Connectivity, Connectivity::SelectionId, bakeSelectEdges, BakeId a1, const Filter& a2, const Filter& a3, const Filter& a4)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_4_NO_FID(Connectivity, Connectivity::SelectionId, bakeSelectNetwork, BakeId a1, const Filter& a2, const Filter& a3, const Filter& a4)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_NO_FID(Connectivity, Connectivity::SelectionId, bakeUnion, SelectionId a1, SelectionId a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_NO_FID(Connectivity, Connectivity::SelectionId, bakeDifference, SelectionId a1, SelectionId a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_NO_FID(Connectivity, Connectivity::SelectionId, bakeIntersection, SelectionId a1, SelectionId a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_NO_FID(Connectivity, Connectivity::SelectionId, bakeDisjunction, SelectionId a1, SelectionId a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, void, bakePack, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, void, bakeExport, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, void, bakeEnd, BakeId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, size_t, retain, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, size_t, release, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, bool, isUndefined, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, void, invalidate, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_DECL(Connectivity, void, invalidateAll)
{
    capi->invalidateAll(fabricId);
}

FABRIC_BIND_1_NO_FID(Connectivity, size_t, getMemUsage, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_NO_FID(Connectivity, bool, pathExistsIn, SelectionId a1, const Path& a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_NO_FID(Connectivity, bool, edgeExistsIn, SelectionId a1, EdgeId a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_NO_FID(Connectivity, void, includeEdge, SelectionId a1, EdgeId a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_2_NO_FID(Connectivity, void, excludeEdge, SelectionId a1, EdgeId a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, size_t, countPrims, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, size_t, countAttributes, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, size_t, countBuckets, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_1_NO_FID(Connectivity, size_t, countEdges, SelectionId a1)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_DECL(Connectivity, size_t, findEdgesToRoot, Span<EdgeId> a1, const Path& a2)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->findEdgesToRoot(fabricId, a1, a2.asPathC(), value[top], mask[top]);
}

FABRIC_BIND_DECL(Connectivity, size_t, findPrimsToRoot, Span<PathC> a1, const Path& a2)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->findPrimsToRoot(fabricId, a1, a2.asPathC(), value[top], mask[top]);
}

FABRIC_BIND_DECL(Connectivity, PathC, findRoot, const Path& a1)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->findRoot(fabricId, a1.asPathC(), value[top], mask[top]);
}

FABRIC_BIND_DECL(Connectivity, size_t, removeDescendants, Span<PathC> a1, Span<const Path> a2)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->removeDescendants(fabricId, a1, convertSpan<const PathC>(a2), value[top], mask[top]);
}

FABRIC_BIND_DECL(Connectivity, size_t, reduceChangeList, Span<PathC> a1, ListenerId a2, Span<const PathC> a3, Span<const PathC> a4)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->reduceChangeList(fabricId, a1, a2, a3, a4, value[top], mask[top]);
}

FABRIC_BIND_2_W_FID(Connectivity, size_t, visitPaths, VisitorFunctionPath_t a1, void* a2)
{
    FABRIC_BIND_CALL()
}

FABRIC_BIND_DECL(Connectivity, size_t, visitRd, SelectionId a1, const Path& a2, VisitorFunctionRd_t a3, void* a4)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitRd(a1, a2, value[top], dualValue[top], mask[top], a3, a4);
}

FABRIC_BIND_DECL(Connectivity, size_t, visitWr, SelectionId a1, const Path& a2, VisitorFunctionWr_t a3, void* a4)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitWr(a1, a2, value[top], dualValue[top], mask[top], a3, a4);
}

FABRIC_BIND_DECL(Connectivity, size_t, visitParallelRd, SelectionId a1, const Path& a2, VisitorFunctionRd_t a3, void* a4)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitParallelRd(a1, a2, value[top], dualValue[top], mask[top], a3, a4);
}

FABRIC_BIND_DECL(Connectivity, size_t, visitParallelWr, SelectionId a1, const Path& a2, VisitorFunctionWr_t a3, void* a4)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitParallelWr(a1, a2, value[top], dualValue[top], mask[top], a3, a4);
}

FABRIC_BIND_DECL(Connectivity, size_t, visitFromRd, SelectionId a1, const Path& a2, const Path& a3, VisitorFunctionRd_t a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitFromRd(a1, a2, a3, value[top], dualValue[top], mask[top], a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, visitFromWr, SelectionId a1, const Path& a2, const Path& a3, VisitorFunctionWr_t a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitFromWr(a1, a2, a3, value[top], dualValue[top], mask[top], a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, rvisitFromRd, SelectionId a1, const Path& a2, const Path& a3, VisitorFunctionRd_t a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->rvisitFromRd(a1, a2, a3, value[top], dualValue[top], mask[top], a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, rvisitFromWr, SelectionId a1, const Path& a2, const Path& a3, VisitorFunctionWr_t a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->rvisitFromWr(a1, a2, a3, value[top], dualValue[top], mask[top], a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, visitParallelFromRd, SelectionId a1, const Path& a2, const Path& a3, VisitorFunctionRd_t a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitParallelFromRd(a1, a2, a3, value[top], dualValue[top], mask[top], a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, visitParallelFromWr, SelectionId a1, const Path& a2, const Path& a3, VisitorFunctionWr_t a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitParallelFromWr(a1, a2, a3, value[top], dualValue[top], mask[top], a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, transformFromWr, SelectionId a1, const Path& a2, const Span<const Path> a3, TransformFunctionWr_t a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    const auto a3_span = makeSpan((PathC*)a3.data(), a3.size());
    return capi->transformFromWr(a1, a2, a3_span, value[top], dualValue[top], mask[top], a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, extentFromWr, SelectionId a1, const Path& a2, const Span<const Path> a3, ExtentFunctionWr_t a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    const auto a3_span = makeSpan((PathC*)a3.data(), a3.size());
    return capi->extentFromWr(a1, a2, a3_span, value[top], dualValue[top], mask[top], a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, visitMappingRd, SelectionId a1, SelectionId a2, VisitorFunctionRd_t a3, Algorithm a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitMappingRd(a1, a2, value[top], dualValue[top], mask[top], a3, a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, visitMappingWr, SelectionId a1, SelectionId a2, VisitorFunctionWr_t a3, Algorithm a4, void* a5)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->visitMappingWr(a1, a2, value[top], dualValue[top], mask[top], a3, a4, a5);
}

FABRIC_BIND_DECL(Connectivity, size_t, navigateRd, const NavigatorParametersRd_t& a1)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->navigateRd(a1, value[top], dualValue[top], mask[top]);
}

FABRIC_BIND_DECL(Connectivity, size_t, navigateWr, const NavigatorParametersWr_t& a1)
{
    CARB_ASSERT(value[top]);
    CARB_ASSERT(dualValue[top]);
    CARB_ASSERT(mask[top]);
    return capi->navigateWr(a1, value[top], dualValue[top], mask[top]);
}

FABRIC_BIND_0_W_FID(Connectivity, Connectivity::PerformanceCounters*, runtimePerfCounters)
{
    FABRIC_BIND_CALL();
}

FABRIC_BIND_0_W_FID(Connectivity, void, runtimeClearQueryCache)
{
    FABRIC_BIND_CALL();
}

FABRIC_BIND_1_W_FID(Connectivity, size_t, runtimeReserveQueryCache, size_t a1)
{
    FABRIC_BIND_CALL();
}

FABRIC_BIND_0_W_FID(Connectivity, size_t, getDataRevision)
{
    FABRIC_BIND_CALL();
}

FABRIC_BIND_0_W_FID(Connectivity, size_t, getDataId)
{
    FABRIC_BIND_CALL();
}

//
// USD Hierarchy

inline USDHierarchy::USDHierarchy(FabricId fabricId_, IConnectivity* capi_) : fabricId(fabricId_)
{
    CARB_ASSERT(fabricId_ != kInvalidFabricId);
    capi = capi_ ? capi_ : carb::getCachedInterface<IConnectivity>();
    CARB_ASSERT(capi != nullptr);
}

FABRIC_BIND_DECL(USDHierarchy, USDHierarchy::EdgeId, connectToParent, const Path& a1, const Path& a2)
{
    const uint64_t parentTypeValue = safeConvert<uint64_t>(connectivity::kParentEdgeType);
    const uint64_t childTypeValue = safeConvert<uint64_t>(connectivity::kChildEdgeType);
    return capi->connectIfNot(fabricId, a1, a2, parentTypeValue, childTypeValue, nullptr);
}

FABRIC_BIND_DECL(USDHierarchy, USDHierarchy::EdgeId, connectToCanonicalParent, const Path& a1)
{
    auto const& parent = a1.getParent();
    return connectToParent(a1, parent);
}

FABRIC_BIND_DECL(USDHierarchy, bool, disconnectFromParent, const Path& a1)
{
    const uint64_t parentTypeValue = safeConvert<uint64_t>(connectivity::kParentEdgeType);
    return capi->disconnectSource(fabricId, a1, parentTypeValue);
}

FABRIC_BIND_DECL(USDHierarchy, PathC, getParent, const Path& a1)
{
    const uint64_t parentTypeValue = safeConvert<uint64_t>(connectivity::kParentEdgeType);
    const EdgeId eid = capi->findFirstEdge(fabricId, a1, parentTypeValue);
    if(eid == connectivity::kInvalidEdgeId)
        return kUninitializedPath;
    return capi->getTarget(fabricId, eid);
}

FABRIC_BIND_DECL(USDHierarchy, PathC, getTopParent, const Path& a1)
{
    const uint64_t parentTypeValue = safeConvert<uint64_t>(connectivity::kParentEdgeType);
    return capi->findRoot(fabricId, a1.asPathC(), parentTypeValue, connectivity::kDefaultEdgeMask);
}

FABRIC_BIND_DECL(USDHierarchy, PathC, getFirstChild, const Path& a1)
{
    const uint64_t childTypeValue = safeConvert<uint64_t>(connectivity::kChildEdgeType);
    const EdgeId eid = capi->findFirstEdge(fabricId, a1, childTypeValue);
    if(eid == connectivity::kInvalidEdgeId)
        return kUninitializedPath;
    return capi->getTarget(fabricId, eid);
}

FABRIC_BIND_DECL(USDHierarchy, PathC, getNextSibling, const Path& a1)
{
    const uint64_t parentTypeValue = safeConvert<uint64_t>(connectivity::kParentEdgeType);
    const uint64_t childTypeValue = safeConvert<uint64_t>(connectivity::kChildEdgeType);
    const EdgeId peid = capi->findFirstEdge(fabricId, a1, parentTypeValue);
    if(peid == connectivity::kInvalidEdgeId)
        return a1;
    const EdgeId deid = capi->getDual(fabricId, peid);
    const EdgeId ceid = capi->findNextAtSource(fabricId, deid, childTypeValue);
    return capi->getTarget(fabricId, ceid);
}

FABRIC_BIND_DECL(USDHierarchy, FabricId, getFabricId)
{
    return fabricId;
}

FABRIC_BIND_DECL(USDHierarchy, void, connectAllToCanonicalParent, size_t* outAmountVisited, size_t* outAmountConnected)
{
    size_t n_connected = 0;

    struct UD
    {
        IConnectivity* capi;
        IPath* papi;
        FabricId fabricId;
        size_t* n_connected_ptr;
        uint64_t value;
        uint64_t dualValue;
    } ud;

    ud.capi = capi;
    ud.papi = carb::getCachedInterface<IPath>();
    ud.fabricId = fabricId;
    ud.n_connected_ptr = &n_connected;
    ud.value = safeConvert<uint64_t>(connectivity::kParentEdgeType);;
    ud.dualValue = safeConvert<uint64_t>(connectivity::kParentDualEdgeType);;

    const auto visitor = [](const PathC* firstPath, const PathC* lastPath, void* userData) {
        UD* ud = (UD*) userData;
        CARB_ASSERT(firstPath <= lastPath);
        auto pc = firstPath;
        for( ; pc <= lastPath ; pc++)
        {
#if CARB_ASSERT_ENABLED
            const char* pcstr = ud->papi->getText(*pc);
            CARB_UNUSED(pcstr);
#endif
            PathC pp = ud->papi->getParent(*pc);
            if(pp != kUninitializedPath)
            {
#if CARB_ASSERT_ENABLED
                const char* ppstr = ud->papi->getText(pp);
                CARB_UNUSED(ppstr);
#endif
                bool alreadyConnected;
                const auto eid = ud->capi->connectIfNot(ud->fabricId, *pc, pp, ud->value, ud->dualValue, &alreadyConnected);
                if(eid != connectivity::kInvalidEdgeId)
                {
                    if(!alreadyConnected)
                    {
                        (*ud->n_connected_ptr)++;
                    }
                }
            }
        }
    };

    const size_t n_visited = capi->visitPaths(fabricId, visitor, &ud);

    if(outAmountVisited)
        *outAmountVisited = n_visited;

    if(outAmountConnected)
        *outAmountConnected = n_connected;
}

FABRIC_BIND_DECL(USDHierarchy, void, connectAllToCanonicalParent, ChangedPrimBucketList& changedList, size_t* outAmountVisited, size_t* outAmountConnected)
{
    size_t n_connected = 0;
    size_t n_visited = 0;

    const uint64_t parentTypeValue = safeConvert<uint64_t>(connectivity::kParentEdgeType);
    const uint64_t childTypeValue = safeConvert<uint64_t>(connectivity::kChildEdgeType);

    for (size_t i = 0; i != changedList.size(); i++)
    {
        AddedPrimIndices addedPrimIndices = changedList.getAddedPrims(i);
        if (addedPrimIndices.size() > 0)
        {
            const BucketChanges changes = changedList.getChanges(i);
            const gsl::span<const Path>& paths = changes.pathArray;
            for (size_t index : addedPrimIndices)
            {
                const auto& pi = paths[index];
                const auto pp = pi.getParent();

#if CARB_ASSERT_ENABLED
                const char* pi_str = pi.getText();
                const char* pp_str = pp.getText();
                CARB_UNUSED(pi_str);
                CARB_UNUSED(pp_str);
#endif
                bool alreadyConnected;
                const auto eid = capi->connectIfNot(fabricId, pi, pp, parentTypeValue, childTypeValue, &alreadyConnected);
                if(eid != connectivity::kInvalidEdgeId)
                {
                    if(!alreadyConnected)
                    {
                        n_connected++;
                    }
                }

                n_visited++;
            }
        }
    }

    if(outAmountVisited)
        *outAmountVisited = n_visited;

    if(outAmountConnected)
        *outAmountConnected = n_connected;
}

//
// UsdHierarychyRange

inline USDHierarchyRange::USDHierarchyRange(USDHierarchy& hier, const PathC& startPath) : m_hier(hier)
{
    omni::fabric::StageReaderWriter stageReaderWriter(m_hier.getFabricId());
    if(stageReaderWriter.primExists(startPath))
    {
        m_beginPath = startPath;
        m_endPath = getNextPrim(omni::fabric::Path(startPath));
    }
    else
    {
        m_beginPath = kUninitializedPath;
        m_endPath = kUninitializedPath;
    }
}

FABRIC_BIND_DECL(USDHierarchyRange, PathC, getNextPrim, const Path& path)
{
    // traverse up until we find another sibling or reach the end
    PathC node = path.asPathC();
    while (node != kUninitializedPath)
    {

        PathC nextSibling = m_hier.getNextSibling(node);
        PathC parent = m_hier.getParent(node);
        PathC firstChild = (parent == kUninitializedPath) ? kUninitializedPath : m_hier.getFirstChild(parent);
        // make sure next sibling is not first child, end, or itself
        if (nextSibling != kUninitializedPath && nextSibling != firstChild && nextSibling != node)
        {
            return nextSibling;
        }
        node = m_hier.getParent(node);
    }
    return kUninitializedPath;
}

FABRIC_BIND_DECL(USDHierarchyRange, USDHierarchyRange::iterator, begin)
{
    return USDHierarchyRange::iterator(*this, m_hier, m_beginPath);
}

FABRIC_BIND_DECL(USDHierarchyRange, USDHierarchyRange::iterator, end)
{
    return USDHierarchyRange::iterator(*this, m_hier, m_endPath);
}

//
// USDHierarchyRange::iterator

FABRIC_BIND_DECL(USDHierarchyRange::iterator, void, PruneChildren)
{
    CARB_ASSERT(m_primPath != m_hierRange.m_endPath);
    m_pruneChildrenFlag = true;
}

FABRIC_BIND_DECL(USDHierarchyRange::iterator, PathC, operator*)
{
    return m_primPath;
}

FABRIC_BIND_DECL(USDHierarchyRange::iterator, PathC, operator->)
{
    return m_primPath;
}

FABRIC_BIND_DECL(USDHierarchyRange::iterator, USDHierarchyRange::iterator&, operator++)
{
    increment();
    return *this;
}

FABRIC_BIND_DECL(USDHierarchyRange::iterator, USDHierarchyRange::iterator, operator++, int)
{
    iterator tmp = *this;
    increment();
    return tmp;
}

inline bool operator==(const USDHierarchyRange::iterator& a, const USDHierarchyRange::iterator& b)
{
    return a.m_primPath == b.m_primPath;
}

inline bool operator!=(const USDHierarchyRange::iterator& a, const USDHierarchyRange::iterator& b)
{
    return a.m_primPath != b.m_primPath;
}

FABRIC_BIND_DECL(USDHierarchyRange::iterator, void, increment)
{
    // if we arent pruning children, move to child if it exists
    if (!m_pruneChildrenFlag && moveToChild())
    {
        m_depth++;
    }
    else
    {
        // traverse up to parents until we find a sibling or reach the end
        while (moveToNextSiblingOrParent())
        {
            if (m_depth)
            {
                m_depth--;
            }
        }
    }
    m_pruneChildrenFlag = false;
}

FABRIC_BIND_DECL(USDHierarchyRange::iterator, bool, moveToChild)
{
    PathC firstChild = m_hier.getFirstChild(m_primPath);
    if (firstChild != kUninitializedPath)
    {
        m_primPath = firstChild;
        return true;
    }
    return false;
}

FABRIC_BIND_DECL(USDHierarchyRange::iterator, bool, moveToNextSiblingOrParent)
{
    PathC end = m_hierRange.m_endPath;
    PathC next = (m_primPath == kUninitializedPath) ? kUninitializedPath : m_hier.getNextSibling(m_primPath);

    // make sure next sibling is not first child, end, or itself
    if (next != kUninitializedPath && next != m_primPath && next != m_hier.getFirstChild(m_hier.getParent(next)))
    {
        m_primPath = next;
    }
    else if (next != end)
    {
        PathC parent = m_hier.getParent(m_primPath);
        m_primPath = parent;
        return true;
    }
    return false;
}

} // namespace fabric
} // namespace omni

#undef FABRIC_ASSERT_OR_RETURN

#undef FABRIC_BIND_0_W_FID
#undef FABRIC_BIND_1_W_FID
#undef FABRIC_BIND_2_W_FID
#undef FABRIC_BIND_3_W_FID
#undef FABRIC_BIND_4_W_FID

#undef FABRIC_BIND_0_NO_FID
#undef FABRIC_BIND_1_NO_FID
#undef FABRIC_BIND_2_NO_FID
#undef FABRIC_BIND_3_NO_FID
#undef FABRIC_BIND_4_NO_FID

#undef FABRIC_BIND_CALL
#undef FABRIC_BIND_DECL
#undef FABRIC_BIND_DEFN
