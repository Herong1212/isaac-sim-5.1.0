#ifndef PXR_USD_SEQUENCE_VALUE_CLIP_BAKER_H
#define PXR_USD_SEQUENCE_VALUE_CLIP_BAKER_H

#include "pxr/usd/usd/stage.h"
#include "pxr/usd/usd/notice.h"
#include "pxr/usd/usd/attributeQuery.h"
#include "pxr/usd/usdSkel/animation.h"
#include "pxr/usdImaging/usdImaging/resolvedAttributeCache.h"

#include "api.h"
#include "sequence.h"

PXR_NAMESPACE_OPEN_SCOPE

class UsdSequenceAssetClipBase;

class UsdSequenceValueClipBaker: public TfWeakBase
{
public:
	struct AssetClipData
	{
		double startTime = 0;
		double endTime = 0;
		float playRate = 1;
		bool loop = false;
		GfVec3d animTime = {};	// Start, end, play offset
		SdfPath clipAnim;
		SdfPath animPrim;
		std::vector<TfToken> rels;
		std::unordered_set<UsdRelationship, TfHash> clipAnimBindingRels;
		UsdImaging_VisCache visCache;
		std::vector<SdfPath> updatedPaths;
	};

	enum class UpdateType
	{
		Initialize,
		Update,
		Clear,
	};

	typedef std::vector<SdfPath> (*UpdateCallback)(UpdateType updateType, const SdfPath& clip, const AssetClipData& clipData, const UsdTimeCode& time, const SdfPath& assetPrim, UsdStage& stage);


	USDSEQUENCE_API explicit UsdSequenceValueClipBaker(UsdStageWeakPtr stage);

	USDSEQUENCE_API ~UsdSequenceValueClipBaker();

	USDSEQUENCE_API UsdStageWeakPtr GetStage()const;

	USDSEQUENCE_API SdfLayerHandle CacheAnimation(const UsdPrim& prim);

	USDSEQUENCE_API void Update(UsdTimeCode timeCode);

	USDSEQUENCE_API static void SetUpdateCallback(UpdateCallback);

protected:

	struct PrimOrder
	{
		bool operator()(const SdfPath& left, const SdfPath& right)const;

		UsdStageWeakPtr stage;
	};

	struct AssetPrimData
	{
		std::map<SdfPath, AssetClipData, PrimOrder> clipPrims;
		std::unordered_set<UsdAttribute, TfHash> timeCodeAttrs;
		std::unordered_set<UsdAttribute, TfHash> visAttrs;
		SdfLayerRefPtr clipsManifest;
	};

	void ProcessObjectsChanged();
	void UpdateAnim(const UsdTimeCode& time);
	void HandleNotice(const UsdNotice::ObjectsChanged& notice,const UsdStageWeakPtr& stage);
	SdfLayerRefPtr PrepareValueClipLayer(const SdfPath & animPrimPath);
	void InvalidateAssetPrims(const std::set<SdfPath>& assetPrims, std::vector<SdfPath>& changedPaths);
	void RemoveInert(const SdfPath& path)const;

	static void ProcessVisChanged(const UsdPrim& assetPrim, AssetPrimData& assetPrimData);
    static bool ShouldCreateClipAnim(const UsdPrim& assetPrim, const UsdPrim& animPrim);
	static SdfLayerRefPtr CreateValueClipLayer(UsdPrim animPrim);
	static void AppendClipsTimes(VtVec2dArray& times, GfVec2d segment, GfVec2d clip, GfVec3d anim, SdfLayerOffset offset, bool loop, float playRate);
	static GfVec3d GetAnimTime(const UsdSequenceAssetClipBase& clip, SdfLayer & valueClipLayer);
	static void RaiseRelationships(UsdPrim animPrim, UsdPrim clipAnim);

	static UpdateCallback updateCallback;

	UsdStageWeakPtr stage;
	TfNotice::Key noticeKey;
	std::map<SdfPath, AssetPrimData> assetPrims;
	std::map<SdfPath, SdfLayerRefPtr> valueClipLayers;
	std::map<SdfPath, SdfLayerRefPtr> cachedValueClipLayers;
	std::set<SdfPath> changedPaths = {SdfPath::AbsoluteRootPath()};
	bool subLayersChanged = false;
	unsigned clipAnimPostfix = 0;
};

PXR_NAMESPACE_CLOSE_SCOPE
#endif
