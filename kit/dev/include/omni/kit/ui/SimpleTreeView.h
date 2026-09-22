// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Widget.h"

#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a SimpleTreeView.
 */
class OMNI_KIT_UI_CLASS_API SimpleTreeView : public Widget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::SimpleTreeView);

    /**
     * Constructor.
     *
     * @param treeData  A list of strings to construct the data of the TreeView
     * @param separator
     */
    OMNI_KIT_UI_API explicit SimpleTreeView(const std::vector<std::string>& treeData, char separator = '/');

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API ~SimpleTreeView() override;

    /**
     * Gets the text of the treeNode.
     *
     * @return The text of the treeNode.
     */
    OMNI_KIT_UI_API const std::string getSelectedItemName() const;

    /**
     * Clears the currently selected tree node
     */
    OMNI_KIT_UI_API void clearSelection();

    /**
     * Sets the text of the tree nodes.
     *
     * @param text The text of the tree nodes.
     */
    OMNI_KIT_UI_API void setTreeData(const std::vector<std::string>& treeData);

    /**
     * Sets the callback function when any tree node is clicked.
     *
     * fn The callback function when any tree node is clicked.
     */
    OMNI_KIT_UI_API void setClickedFn(const std::function<void(WidgetRef)>& fn);

    /**
     * @see Widget::getType
     */
    OMNI_KIT_UI_API WidgetType getType() override;

    /**
     * @see Widget::draw
     */
    void draw(float elapsedTime) override;

protected:
    // Clicked Function callback
    std::function<void(WidgetRef)> m_clickedFn;

protected:
    struct TreeDataNode;

    using TreeDataNodePtr = std::shared_ptr<TreeDataNode>;
    // An internal structure to accomodate the Hierachical tree data
    struct TreeDataNode : public std::enable_shared_from_this<TreeDataNode>
    {

        // The text of the current node
        std::string m_text;

        // Pointer to the parent node
        std::weak_ptr<TreeDataNode> m_parentNode;

        // List of child nodes
        std::vector<TreeDataNodePtr> m_children;

        // Single Node's constructor/destructor
        explicit TreeDataNode(const std::string& data);
        ~TreeDataNode();

        // Helper functions

        // Add a child
        TreeDataNodePtr& addChild(TreeDataNodePtr& node);

        // Recursively delete all childrens(decendents)
        void deleteChildren();

        // Stack up the node text to construct the full path from root to the current node
        const std::string getFullPath(const char& separator) const;
    };

    // The root node of the entire tree
    TreeDataNodePtr m_rootNode;

    // Pointer to the currently selected Node, for the rendering purpose
    std::weak_ptr<TreeDataNode> m_selectedNode;

    // A customized separator, default as '/'
    char m_separator;

protected:
    // Helper function to build the entire data tree, return false if build fail
    bool buildDataTree(const std::vector<std::string>& inputStrings);

    // Helper function to split the string into a list of string tokens
    //      example, "root/parent/child" ==> ["root","parent","child"]
    std::vector<std::string> split(const std::string& s, char seperator);

    // A core function to hierachically, node as the root, visualize the tree data using into the SimpleTreeView
    void drawTreeNode(carb::imgui::ImGui* imgui, const std::shared_ptr<SimpleTreeView::TreeDataNode>& node);
};
}
}
}
