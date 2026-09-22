// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Container.h"
#include "Model.h"

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <type_traits>
#include <vector>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Widget that spawns different widgets depending on the underlying model leaf node type.
 */
class OMNI_KIT_UI_CLASS_API ViewNode : public ModelWidget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ViewNode);

    OMNI_KIT_UI_API ViewNode();

    OMNI_KIT_UI_API ~ViewNode();

    WidgetType getType() override
    {
        return kType;
    }

    OMNI_KIT_UI_API std::shared_ptr<Widget> getWidget() const;

private:
    void _onModelNodeChange() override;

    template <class T>
    std::shared_ptr<Widget> _createWidget();
    std::shared_ptr<Widget> _tryCreateWidgetFromMeta();
    std::shared_ptr<Widget> _createWidgetFromValueType();
};


/**
 * Widget to view Model Array nodes..
 */
class OMNI_KIT_UI_CLASS_API ViewArray : public ModelWidget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ViewArray);

    OMNI_KIT_UI_API ViewArray();

    OMNI_KIT_UI_API ~ViewArray();

    WidgetType getType() override
    {
        return kType;
    }

private:
    void _onModelNodeChange() override;
    void _createWidgetsFromArray();
};


/**
 * Takes section of a model and represent it as a list of widgets.
 * Supports filtering.
 */
class OMNI_KIT_UI_CLASS_API ViewFlat : public ModelWidget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ViewFlat);

    OMNI_KIT_UI_API ViewFlat(bool sort);

    OMNI_KIT_UI_API ~ViewFlat();

    WidgetType getType() override
    {
        return kType;
    }

    OMNI_KIT_UI_API size_t setFilter(const char* filter);

protected:
    bool m_sort;

private:
    std::shared_ptr<Container> _createLayout();
    void _createWidgetsFromModel();
    void _createLeafWidgetPair(std::shared_ptr<Widget> labelWidget,
                               const std::string& modelRootPath,
                               std::shared_ptr<Container>& layout);
    void _onModelNodeChange() override;
};

/**
 * Takes topmost sections of a model and spawns CollapsingFrame+ViewFlat for each.
 * Supports filtering.
 */
class OMNI_KIT_UI_CLASS_API ViewCollapsing : public ModelWidget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ViewCollapsing);

    OMNI_KIT_UI_API ViewCollapsing(bool defaultOpen, bool sort);

    OMNI_KIT_UI_API ~ViewCollapsing();

    WidgetType getType() override
    {
        return kType;
    }

    OMNI_KIT_UI_API void setFilter(const char* filter);

    void setUseFrameBackgroundColor(bool useFrameBackgroundColor)
    {
        m_useFrameBackgroundColor = useFrameBackgroundColor;
    }
    bool getUseFrameBackgroundColor() const
    {
        return m_useFrameBackgroundColor;
    }

protected:
    bool m_defaultOpen;
    bool m_sort;
    bool m_useFrameBackgroundColor;

private:
    void _createWidgetsFromModel();
    void _onModelNodeChange() override;
};

enum class DelegateAction
{
    eCreateDefaultWidget = 0,
    eSkipKey,
    eUseCustomWidget
};
struct DelegateResult
{
    DelegateAction action;
    std::shared_ptr<Widget> customWidget;
};

class OMNI_KIT_UI_CLASS_API ViewTreeGrid : public ModelWidget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ViewTreeGrid);

    OMNI_KIT_UI_API ViewTreeGrid(bool defaultOpen, bool sort, uint32_t columnCount);
    OMNI_KIT_UI_API ~ViewTreeGrid();

    WidgetType getType() override
    {
        return kType;
    }

    void draw(float elapsedTime) override;

    OMNI_KIT_UI_API bool getDrawTableHeader() const;
    OMNI_KIT_UI_API void setDrawTableHeader(bool drawTableHeader);

    using OnBuildCellFn = DelegateResult (*)(std::shared_ptr<Model> model,
                                             const char* modelPath,
                                             uint32_t columnIdx,
                                             uint32_t columnCount);
    using OnBuildCellStdFn = std::function<std::remove_pointer_t<OnBuildCellFn>>;
    OMNI_KIT_UI_API void setOnBuildCellFn(const OnBuildCellStdFn& onBuildCellStdFn);

    OMNI_KIT_UI_API void setHeaderCellWidget(uint32_t columnIdx, std::shared_ptr<Widget> widget);
    OMNI_KIT_UI_API std::shared_ptr<Widget> getHeaderCellWidget(uint32_t columnIdx);

    OMNI_KIT_UI_API void setHeaderCellText(uint32_t columnIdx, const char* text);

    OMNI_KIT_UI_API void setIsRoot(bool isRoot);
    OMNI_KIT_UI_API bool getIsRoot() const;

    OMNI_KIT_UI_API void setText(const char* text);
    OMNI_KIT_UI_API const char* getText() const;

protected:
    bool m_defaultOpen;
    bool m_sort;
    std::string m_text;
    uint32_t m_columnCount;

    bool m_isRoot = true;
    bool m_drawTableHeader = false;
    std::vector<std::shared_ptr<Widget>> m_headerWidgets;
    std::vector<float> m_columnOffsets;

    OnBuildCellStdFn m_onBuildCellStdFn;

    bool m_widgetsValid = false;
    bool m_isNodeOpen = false;

    void setSibling(uint32_t columnIdx, std::shared_ptr<Widget> sibling);
    std::shared_ptr<Widget> getSibling(uint32_t columnIdx);

    std::vector<std::shared_ptr<Widget>> m_siblingCells;

    std::shared_ptr<Widget> _buildDefaultLeafWidget(const char* sectionName, const char* sectionPath);
    void _createWidgetsFromModel();

    void _onModelNodeChange() override;
    void _drawTableHeader(float elapsedTime);
    const uint32_t kNoTreeNode = (uint32_t)-1;
    uint32_t _findTreeNodeColumnIndexInRow(uint32_t rowIndex);
    void _drawCommonChildrenTreeNodeRow(uint32_t rowIndex, uint32_t treeNodeColumnIndex, float elapsedTime);
    void _drawCommonChildrenRegularRow(uint32_t rowIndex, float elapsedTime);
    void _drawCommonChildrenGrid(float elapsedTime);
    void _drawAsRoot(float elapsedTime);
    void _drawAsChildHeader(float elapsedTime);
    void _drawAsChildBody(float elapsedTime);
};

}
}
}
