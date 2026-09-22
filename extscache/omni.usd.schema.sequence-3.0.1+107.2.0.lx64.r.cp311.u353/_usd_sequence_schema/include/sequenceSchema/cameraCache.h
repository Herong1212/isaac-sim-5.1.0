#ifndef PXR_USD_SEQUENCE_CAMERA_CACHE_BAKER_H
#define PXR_USD_SEQUENCE_CAMERA_CACHE_BAKER_H

#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/camera.h>
#include <pxr/usd/usd/notice.h>
#include <pxr/usdImaging/usdImaging/resolvedAttributeCache.h>

#include "api.h"

PXR_NAMESPACE_OPEN_SCOPE

class UsdSequenceCameraCache: public TfWeakBase
{
public:
	USDSEQUENCE_API explicit UsdSequenceCameraCache(UsdStageWeakPtr stage);
	USDSEQUENCE_API UsdGeomCamera GetCurrentCamera(UsdTimeCode time);
	USDSEQUENCE_API UsdStageWeakPtr GetStage()const;

protected:
	void HandleNotice(const UsdNotice::ObjectsChanged& notice, const UsdStageWeakPtr& stage);
	void HandleStageChange(const std::vector<SdfPath>& changedPaths);

	struct ShotClipData
	{
		SdfPath cameraPath;
		UsdImaging_VisCache shotVisCache;
		UsdAttributeQuery startQuery, endQuery;
	};

	struct CompareClip
	{
		bool operator()(const SdfPath& left, const SdfPath& right)const;
		UsdStageWeakPtr stage;
	};

	TfNotice::Key noticeKey;
	UsdStageWeakPtr stage;
	std::map<SdfPath, ShotClipData, CompareClip> shotClips;
};

PXR_NAMESPACE_CLOSE_SCOPE
#endif