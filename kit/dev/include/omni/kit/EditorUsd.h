// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>

namespace omni
{
namespace kit
{
/**
 * Defines a Kit specific usd metadata set.
 * The python counterpart is at source/extensions/omni.usd/bindings/python/omni.usd/impl/editor.py
 */
class EditorUsd
{
public:
    /**
     * Sets if to hide the prim in Stage Window.
     *
     * @param prim The prim to set metadata value to.
     * @param hide true to hide prim in Stage Window, false to show in Stage Window.
     */
    static void setHideInStageWindow(const pxr::UsdPrim& prim, bool hide)
    {
        static const pxr::TfToken kHideInStageWindow("hide_in_stage_window");
        setMetadata(prim, kHideInStageWindow, hide);
    }

    /**
     * Gets whether the prim should be hidden in Stage Window.
     *
     * @param prim The prim to get metadata value from.
     * @return true if prim is hidden, false otherwise.
     */
    static bool isHideInStageWindow(const pxr::UsdPrim& prim)
    {
        static const pxr::TfToken kHideInStageWindow("hide_in_stage_window");
        return getMetadata(prim, kHideInStageWindow, false);
    }

    /**
     * Sets if to disallow deletion of a prim.
     *
     * @param prim The prim to set metadata value to.
     * @param noDelete true to disallow deletion, false to allow deletion.
     */
    static void setNoDelete(const pxr::UsdPrim& prim, bool noDelete)
    {
        static const pxr::TfToken kNoDelete("no_delete");
        setMetadata(prim, kNoDelete, noDelete);
    }

    /**
     * Gets whether deletion on the prim is disallowed.
     *
     * @param prim The prim to get metadata value from.
     * @return true if prim cannot be disabled, false otherwise.
     */
    static bool isNoDelete(const pxr::UsdPrim& prim)
    {
        static const pxr::TfToken kNoDelete("no_delete");
        return getMetadata(prim, kNoDelete, false);
    }

    /**
     * Sets if to override the picking preference of a prim.
     *
     * @param prim The prim to set metadata value to.
     * @param pickModel true to always pick the enclosing model regardless of editor preferences, false to follow editor
     * preferences.
     */
    static void setAlwaysPickModel(const pxr::UsdPrim& prim, bool pickModel)
    {
        static const pxr::TfToken kAlwaysPickModel("always_pick_model");
        setMetadata(prim, kAlwaysPickModel, pickModel);
    }

    /**
     * Gets whether prim overrides the picking mode to always pick model.
     *
     * @param prim The prim to get metadata value from.
     * @return true if pick on the prim always select its enclosing model, false otherwise.
     */
    static bool isAlwaysPickModel(const pxr::UsdPrim& prim)
    {
        static const pxr::TfToken kAlwaysPickModel("always_pick_model");
        return getMetadata(prim, kAlwaysPickModel, false);
    }

    /**
     * Sets if a prim should ignore material updates.
     *
     * @param prim The material prim to set metadata value to.
     * @param ignore true if prim has set to ignore material updates.
     */
    static void setIgnoreMaterialUpdates(const pxr::UsdPrim& prim, bool ignore)
    {
        static const pxr::TfToken kIgnoreMaterialUpdates("ignore_material_updates");
        setMetadata(prim, kIgnoreMaterialUpdates, ignore);
    }

    /**
     * Gets whether the prim should ignore material updates.
     *
     * @param prim The prim to get metadata value from.
     * @return true if prim has set to ignore material updates
     */
    static bool hasIgnoreMaterialUpdates(const pxr::UsdPrim& prim)
    {
        static const pxr::TfToken kIgnoreMaterialUpdates("ignore_material_updates");
        return getMetadata(prim, kIgnoreMaterialUpdates, false);
    }

    /**
     * Sets if a prim should show a selection outline
     *
     * @param prim The material prim to set metadata value to.
     * @param ignore true if prim has set to not show a selection outline
     */
    static void setNoSelectionOutline(const pxr::UsdPrim& prim, bool ignore)
    {
        static const pxr::TfToken kNoSelectionOutline("no_selection_outline");
        setMetadata(prim, kNoSelectionOutline, ignore);
    }

    /**
     * Gets whether the prim should show a selection outline
     *
     * @param prim The prim to get metadata value from.
     * @return true if prim has set to not show a selection outline
     */
    static bool hasNoSelectionOutline(const pxr::UsdPrim& prim)
    {
        static const pxr::TfToken kNoSelectionOutline("no_selection_outline");
        return getMetadata(prim, kNoSelectionOutline, false);
    }

private:
    template <typename T>
    static void setMetadata(const pxr::UsdPrim& prim, const pxr::TfToken& token, T value)
    {
        pxr::UsdEditContext context(prim.GetStage(), prim.GetStage()->GetSessionLayer());
        bool ret = prim.SetMetadata(token, value);
        CARB_ASSERT(ret);
    }

    template <typename T>
    static T getMetadata(const pxr::UsdPrim& prim, const pxr::TfToken& token, T defaultVal)
    {
        T val = defaultVal;
        prim.GetMetadata(token, &val);
        return val;
    }
};
}
}
