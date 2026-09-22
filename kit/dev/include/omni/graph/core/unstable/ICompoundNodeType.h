// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
//
// This ABI is unstable and subject to change
/*  _    _  _____ ______         _______  __     ______  _    _ _____     ______          ___   _   _____  _____  _____ _  __
   | |  | |/ ____|  ____|     /\|__   __| \ \   / / __ \| |  | |  __ \   / __ \ \        / / \ | | |  __ \|_   _|/ ____| |/ /
   | |  | | (___ | |__       /  \  | |     \ \_/ / |  | | |  | | |__) | | |  | \ \  /\  / /|  \| | | |__) | | | | (___ | ' /
   | |  | |\___ \|  __|     / /\ \ | |      \   /| |  | | |  | |  _  /  | |  | |\ \/  \/ / | . ` | |  _  /  | |  \___ \|  <
   | |__| |____) | |____   / ____ \| |       | | | |__| | |__| | | \ \  | |__| | \  /\  /  | |\  | | | \ \ _| |_ ____) | . \
    \____/|_____/|______| /_/    \_\_|       |_|  \____/ \____/|_|  \_\  \____/   \/  \/   |_| \_| |_|  \_\_____|_____/|_|\_|
*/

#pragma once

#include <omni/graph/core/unstable/IAttributeTemplate.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

struct ICompoundNodeType;
class CompoundNodeTypeHandle : public HandleBase<NodeTypeHandle, CompoundNodeTypeHandle>
{
public:
    using HandleBase<NodeTypeHandle, CompoundNodeTypeHandle>::HandleBase;

    static constexpr NodeTypeHandle invalidValue()
    {
        return kInvalidNodeTypeHandle;
    }
};

struct CompoundNodeTypeObj
{
    const ICompoundNodeType* iNodeType; //!< interface to functionality on the compound node type
    CompoundNodeTypeHandle nodeTypeHandle; //!< opaque handle to actual underlying node type - managed by OmniGraph

    bool isValid() const
    {
        return nodeTypeHandle.isValid();
    }
};

/**
 * Carb interface for manipulating compound node type objects
 *
 */
struct ICompoundNodeType
{
    CARB_PLUGIN_INTERFACE("omni::graph::core::unstable::ICompoundNodeType", 0, 2);


    /**
     * Given an existing node type object, casts it to a compound node type object
     *
     * @param[in] Node Type object to convert
     * @returns   A CompoundNodeTypeObj representing the same Node Type. If the Node Type
     *            is not a Compound Node Type, the returned object will not be valid.
     */
    CompoundNodeTypeObj(CARB_ABI* getCompoundNodeType)(const NodeTypeObj& nodeType);


    /**
     * Finds a compound node type by its USD SdfPath
     *
     * @param[in] An SdfPath to the location of the correspond UsdPrim representing the Compound Node Type
     * @returns An object representing the compound node type, or an invalid object
     *          if no compound node type exists at the given path
     */
    CompoundNodeTypeObj(CARB_ABI* findCompoundNodeTypeByPath)(const char* path);


    /**
     * Create a Compound Node Type object at the given path.
     *
     * @param[in] compoundName The name of the compound to be created. This will be the name of the
     *                         compound USD object, and the default name in registration. Cannot be null
     *                         and must comform to USD naming standards.
     * @param[in] graphDefinitionName The name of Omnigraph definition created defining the function of the
     *                                compound. Cannot be null and must conform to USD naming standards.
     * @param[in] nameSpace The namespace of the compound when registered in the node library. Can be
     *                      null, which indicates a default of "local.nodes".
     * @param[in] compoundFolder Sdf style Path the compound folder to store the compound in. Can be null,
     *                           which indicates to use the default folder, which is a scope named "Compounds"
     *                           parented to the default prim of the stage. If the folder does not exist,
     *                           it will be created.
     * @param[in] evaluatorType The type of the evaluator to associate with the graph
     * @returns A CompoundNodeType object.
     */
    CompoundNodeTypeObj(CARB_ABI* createCompoundNodeType)(const char* compoundName,
                                                          const char* graphDefinitionName,
                                                          const char* nameSpace,
                                                          const char* compoundFolder,
                                                          const char* evaluatorType);

    /**
     * @deprecated Use getDefaultFolderPath instead.
     */
    CARB_DEPRECATED("Deprecated - use getDefaultFolderPath instead.")
    omni::fabric::PathC(CARB_ABI* getDefaultFolder)();

    /**
     * Finds the input with the given name. The 'inputs:' prefix is optional.
     *
     * @param nodeType. The compound node type to search
     * @param inputName. The name to search for.
     *
     * @returns An AttributeTemplateObj representing the input. If the input is not found, the
     * returned objects isValid() method will return false.
     */
    AttributeTemplateObj(CARB_ABI* findInput)(const CompoundNodeTypeObj& nodeType, const char* inputName);

    /**
     * Finds the output with the given name. The 'outputs:' prefix is optional.
     *
     * @param nodeType. The compound node type to search
     * @param outputName. The name to search for.
     *
     * @returns An AttributeTemplateObj representing the output. If the output is not found, the
     * returned objects isValid() method will return false.
     */
    AttributeTemplateObj(CARB_ABI* findOutput)(const CompoundNodeTypeObj& nodeType, const char* outputName);


    /**
     * Removes an input with the given name. The 'inputs:' prefix is optional.
     *
     * @param nodeType. The compound node type to remove an input from.
     * @param inputName. The name of the input to remove.
     *
     * @returns True if the input was removed, false otherwise.
     */
    bool(CARB_ABI* removeInputByName)(const CompoundNodeTypeObj& nodeType, const char* inputName);


    /**
     * Removes an output with the given name. The 'outputs:' prefix is optional.
     *
     * @param nodeType. The compound node type to remove an output from.
     * @param outputName. The name of the output to remove.
     *
     * @returns True if the output was removed, false otherwise.
     */
    bool(CARB_ABI* removeOutputByName)(const CompoundNodeTypeObj& nodeType, const char* outputName);


    /**
     * Downcasts a CompoundNodeTypeObj to a regular NodeTypeObj.
     *
     * @param nodeType. The compound node type to downcast.
     * @returns  NodeType object also representing the compound node. If the ComoundNodeType object is not
     * valid, an invalid NodeType object will be returned.
     */
    NodeTypeObj(CARB_ABI* asNodeType)(const CompoundNodeTypeObj& nodeType);

    /**
     * Get the number of input attribute templates on this node type
     *
     * @param nodeType. The compound node type to fetch inputs from.
     * @returns The number of input attributes on the compound node type.
     */
    size_t(CARB_ABI* getInputCount)(const CompoundNodeTypeObj& nodeType);

    /**
     * Retrieves the input attributes from a compound node type.
     *
     * @param nodeType. The compound node type to retreive inputs from.
     * @param templateBuffer. Buffer to hold the returned objects
     * @param bufferElementCount. The number of objects the buffer can hold.
     *
     * @returns The number of items copied to bufferElementCount.
     */
    size_t(CARB_ABI* getInputs)(const CompoundNodeTypeObj& nodeType, AttributeTemplateObj* templateBuffer, size_t bufferElementCount);

    /**
     * Get the number of output attribute templates on this node type.
     *
     * @param nodeType. The compound node type to fetch outputs from.
     * @returns The number of output attributes on the compound node type.
     */
    size_t(CARB_ABI* getOutputCount)(const CompoundNodeTypeObj& nodeType);

    /**
     * Retrieves the output attributes from a compound node type.
     *
     * @param nodeType. The compound node type to retreive outputs from.
     * @param templateBuffer. Buffer to hold the returned objects
     * @param bufferElementCount. The number of objects the buffer can hold.
     *
     * @returns The number of items copied to bufferElementCount.
     */
     size_t(CARB_ABI* getOutputs)(const CompoundNodeTypeObj& nodeType, AttributeTemplateObj* templateBuffer, size_t bufferElementCount);

    /**
      * Retrieves the default folder path where compound node types are placed on the stage.
      * This is typically a Usd::Scope under the default prim. e.g. "/World/Compounds".
      *
      * @param[out] outPath A pointer to a Path object to store the default compound folder path on stage.
      */
     void(CARB_ABI* getDefaultFolderPath)(omni::fabric::Path* outPath);
};

// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(ICompoundNodeType, getDefaultFolderPath, 13);

}
}
}
}
