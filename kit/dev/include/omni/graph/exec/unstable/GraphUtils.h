// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file GraphUtils.h
//!
//! @brief Defines utilities for graph visualization.
#pragma once

#include <carb/Format.h>

#include <omni/graph/exec/unstable/IGraph.h>
#include <omni/graph/exec/unstable/Traversal.h>

#include <map>
#include <ostream>
#include <string>
#include <unordered_map>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Debugging utility to write out the graph topology in a graphviz format
//!
//! @param  inGraph                    Graph to dump.
//! @param  out                        Output stream to receive the produced graphviz text output.
//! @param  deterministicAndSimplified Optional flag to create a simplified graph dump that is also
//!                                    guaranteed to remain exactly the same each time it is generated.
//!                                    This is done by omitting node topology indices and name hashes
//!                                    from all labels, and using the same color for the entire graph.
//!                                    This setting is mostly used for creating graph dumps that are
//!                                    later used in automated unit tests.
//!
inline void writeFlattenedAsGraphviz(omni::core::ObjectParam<IGraph> inGraph,
                                     std::ostream& out,
                                     const bool deterministicAndSimplified = false);

namespace detail
{

#ifndef DOXYGEN_BUILD

constexpr const char* colorScheme()
{
    return "paired10";
}

constexpr unsigned colorSchemeSize()
{
    return 10;
}

struct GraphState
{
    std::unordered_map<size_t, unsigned> colorMapping;
    unsigned nextColorIndex{ 0 };

    unsigned getColor(size_t hash)
    {
        /*static const std::vector<const char*> gColors = { "black","aqua","aquamarine","bisque",
            "blue","blueviolet","brown","burlywood","cadetblue","chartreuse","chocolate","coral","cornflowerblue",
            "crimson","cyan","darkblue","darkcyan","darkgoldenrod","darkgray","darkgreen","darkgrey","darkkhaki",
            "darkmagenta","darkolivegreen","darkorange","darkorchid","darkred","darksalmon","darkseagreen","darkslateblue",
            "darkslategray","darkslategrey","darkturquoise","darkviolet","deeppink","deepskyblue","dimgray","dimgrey","dodgerblue",
            "firebrick","floralwhite","forestgreen","fuchsia","gainsboro","gold","goldenrod","gray","grey","green","greenyellow",
            "hotpink","indianred","indigo","khaki","lavender","lavenderblush","lawngreen","lemonchiffon","lightblue","lightcoral",
            "lightcyan","lightgoldenrodyellow","lightgray","lightgreen","lightgrey","lightpink","lightsalmon","lightseagreen",
            "lightskyblue","lightslategray","lightslategrey","lightsteelblue","lightyellow","limegreen","linen","magenta",
            "maroon","mediumaquamarine","mediumblue","mediumorchid","mediumpurple","mediumseagreen","mediumslateblue",
            "mediumspringgreen","mediumturquoise","mediumvioletred","midnightblue","mistyrose","moccasin","navy","oldlace","olive",
            "olivedrab","orange","orangered","orchid","palegoldenrod","palegreen","paleturquoise","palevioletred","papayawhip",
            "peachpuff","peru","pink","plum","powderblue","purple","red","rosybrown","royalblue","saddlebrown","salmon","sandybrown",
            "seagreen","sienna","silver","skyblue","slateblue","slategray","slategrey","springgreen","steelblue","tan","teal",
            "thistle","tomato","turquoise","violet","wheat","whitesmoke","yellow","yellowgreen" };*/

        auto foundIt = colorMapping.find(hash);
        if (foundIt == colorMapping.end())
        {
            auto& color = colorMapping[hash];
            color = nextColorIndex;
            nextColorIndex = (nextColorIndex + 1) % colorSchemeSize();
            return color;
        }
        else
        {
            return foundIt->second;
        }
    }
};

constexpr const char* singleIndent()
{
    return "    ";
}

inline std::string makeQuoted(const std::string& s)
{
    return "\"" + s + "\"";
}

inline std::string makeUniqueNodeName(INode* node, const size_t cnt)
{
    std::string uniqueNodeName = node->getName().toString() + "_";
    if (cnt >= 1 && cnt <= 9)
    {
        uniqueNodeName += "0";
    }
    uniqueNodeName += std::to_string(cnt);
    return uniqueNodeName;
}

inline std::string makeId(const std::string& path, const std::string& nodeName)
{
    return path + "/" + nodeName;
}

inline std::string makeClusterId(const std::string& id)
{
    return "Cluster//" + id;
}

inline void writeNodeProperties(INode* node, const std::string& nodeName, std::ostream& out)
{
    if (node->isRoot())
        out << "["
            << "label=\"\" "
            << "shape=point"
            << "]";
    else
        out << "["
            << "label=" << makeQuoted(nodeName) << "]";
}

inline void writeNode(
    const std::string& indent, const std::string& path, INode* node, const std::string& nodeName, std::ostream& out)
{
    out << indent << makeQuoted(makeId(path, nodeName)) << " ";
    writeNodeProperties(node, nodeName, out);
    out << ";" << std::endl;
}

inline void writeConnection(const std::string& indent,
                            const std::string& path,
                            INode* nodeA,
                            const std::string& nodeAName,
                            INode* nodeB,
                            const std::string& nodeBName,
                            std::ostream& out)
{
    auto graphA = nodeA->getNodeGraphDef();
    auto graphB = nodeB->getNodeGraphDef();

    std::string pathA = makeId(path, nodeAName);
    std::string pathB = makeId(path, nodeBName);

    std::string nodeAId = graphA ? makeId(pathA, graphA->getRoot()->getName().toString()) : pathA;
    std::string nodeBId = graphB ? makeId(pathB, graphB->getRoot()->getName().toString()) : pathB;

    out << indent;
    out << makeQuoted(nodeAId);
    out << " -> ";
    out << makeQuoted(nodeBId);

    if (graphA || graphB)
    {
        out << "[";
        if (graphA)
            out << "ltail=" << makeQuoted(makeClusterId(pathA));
        if (graphB)
            out << "lhead=" << makeQuoted(makeClusterId(pathB));
        out << "]";
    }

    out << ";" << std::endl;
}

inline void writeSubgraphProperties(const std::string& indent,
                                    INode* node,
                                    const std::string nodeName,
                                    INodeGraphDef* graph,
                                    GraphState& state,
                                    std::ostream& out,
                                    const bool deterministicAndSimplified = false)
{
    const auto& nodeGraphDefName = graph->getName();
    std::string nodeGraphDefNameLabel;
    if (deterministicAndSimplified)
    {
        // If we want a simplified graph dump, do not include
        // the nodeGraphDefName's hash in the label.
        nodeGraphDefNameLabel = carb::fmt::format("{}", nodeGraphDefName.getString());
    }
    else
    {
        nodeGraphDefNameLabel = carb::fmt::format("{}({})", nodeGraphDefName.getString(), nodeGraphDefName.getHash());
    }


    // this is nested NodeGraphDef
    if (node)
    {
        std::string nodeNameLabel;
        if (deterministicAndSimplified)
        {
            // If we want a deterministic/simplified graph dump, do not
            // include the node's topology index in its label since that
            // property can change between dumps of the same execution graph.
            nodeNameLabel = carb::fmt::format("{}", nodeName.c_str());
        }
        else
        {
            nodeNameLabel = carb::fmt::format("{}({})", nodeName.c_str(), node->getIndexInTopology());
        }

        out << indent << "label = " << makeQuoted(nodeNameLabel + " | " + nodeGraphDefNameLabel) << std::endl;
    }
    // this is top level NodeGraphDef
    else
    {
        out << indent << "label = " << makeQuoted("EXECUTION GRAPH | " + nodeGraphDefNameLabel) << std::endl;
    }

    unsigned int color;
    if (deterministicAndSimplified)
    {
        // If we want a simplified graph dump, use the same color for everything.
        color = 0;
    }
    else
    {
        color = state.getColor(graph->getName().getHash());
    }
    out << indent << "color = " << color << std::endl;
    out << indent << "node [color = " << color << "]" << std::endl;
    out << indent << "edge [color = " << color << "]" << std::endl;
}

inline void writeGraph(const std::string& indent,
                       const std::string& path,
                       INode* node,
                       const std::string nodeName,
                       INodeGraphDef* graph,
                       GraphState& state,
                       std::ostream& out,
                       const bool deterministicAndSimplified)
{
    std::unordered_map<std::string, size_t> nodeNamesInGraph;
    std::unordered_map<INode*, std::string> nodeToUniqueName;
    std::map<std::string, INode*> uniqueNameToNode;

    out << indent << "subgraph " << makeQuoted(makeClusterId(path)) << " {" << std::endl;

    std::string thisIndent = indent + singleIndent();

    writeSubgraphProperties(thisIndent, node, nodeName, graph, state, out, deterministicAndSimplified);

    // For readability, we first write nodes...
    INode* const graphRoot = graph->getRoot();
    const std::string graphRootName = graphRoot->getName().toString();
    writeNode(thisIndent, path, graphRoot, graphRootName, out);
    nodeNamesInGraph.try_emplace(graphRootName, 0);
    nodeToUniqueName.try_emplace(graphRoot, graphRootName);
    uniqueNameToNode.try_emplace(graphRootName, graphRoot);
    traverseDepthFirst<VisitFirst>(
        graph->getRoot(),
        [&nodeNamesInGraph, &nodeToUniqueName, &uniqueNameToNode](auto info, INode* prev, INode* curr)
        {
            const std::string nodeName = curr->getName().toString();
            if (nodeNamesInGraph.find(nodeName) != nodeNamesInGraph.end())
            {
                std::string uniqueName = makeUniqueNodeName(curr, ++nodeNamesInGraph.at(nodeName));
                nodeToUniqueName.try_emplace(curr, uniqueName);
                uniqueNameToNode.try_emplace(uniqueName, curr);
            }
            else
            {
                nodeNamesInGraph.try_emplace(nodeName, 0);
                nodeToUniqueName.try_emplace(curr, nodeName);
                uniqueNameToNode.try_emplace(nodeName, curr);
            }

            info.continueVisit(curr);
        });

    // ...(note that in the above traversal we first gather a list of all
    // nodes that are present in the current topology, which is sorted
    // according to the unique names that we generated for said nodes along
    // the way; this allows us to produce a graph dump who's subgraphs are
    // always ordered in the same way, so that the only barrier to creating
    // a fully-deterministic dump is whether or not we include the node
    // topology indices in the node labels)...
    for (const auto& pair : uniqueNameToNode)
    {
        const std::string& uniqueName = pair.first;
        INode* const node = pair.second;
        if (INodeGraphDef* const nodeGraphDef = node->getNodeGraphDef())
        {
            writeGraph(thisIndent, makeId(path, uniqueName), node, uniqueName, nodeGraphDef, state, out,
                       deterministicAndSimplified);
        }
        else if (!node->isRoot())
        {
            writeNode(thisIndent, path, node, uniqueName, out);
        }
    }

    // ... and then we write connections. Note that we collect all
    // connections first and then write them out in a sorted manner
    // to guarantee reproducibility.
    std::unordered_map<INode*, std::map<std::string, INode*>> connections;
    traverseDepthFirst<VisitAll>(graph->getRoot(),
                                 [&connections, &nodeToUniqueName](auto info, INode* prev, INode* curr)
                                 {
                                     // Store all connections.
                                     if (connections.find(prev) == connections.end())
                                     {
                                         connections.try_emplace(prev, std::map<std::string, INode*>());
                                     }
                                     connections.at(prev).try_emplace(nodeToUniqueName.at(curr), curr);

                                     // Visit all edges, continue traversal on the first one.
                                     if (info.isFirstVisit())
                                     {
                                         info.continueVisit(curr);
                                     }
                                 });

    for (const auto& prevPair : uniqueNameToNode)
    {
        const std::string& prevNodeName = prevPair.first;
        INode* const prevNode = prevPair.second;

        // Skip if the node has no associated connections.
        if (connections.find(prevNode) == connections.end())
        {
            continue;
        }

        for (const auto& currPair : connections.at(prevNode))
        {
            const std::string& currNodeName = currPair.first;
            INode* currNode = currPair.second;
            writeConnection(thisIndent, path, prevNode, prevNodeName, currNode, currNodeName, out);
        }
    }

    out << indent << "}" << std::endl;
}

inline void writeGraphProperties(const std::string& indent, std::ostream& out)
{
    out << indent << "compound=true" << std::endl;
    out << indent << "colorscheme=" << colorScheme() << std::endl;
    out << indent << "node [shape=circle style=filled fontcolor=white color=black colorscheme=" << colorScheme() << "]"
        << std::endl;
    out << indent << "edge [colorscheme=" << colorScheme() << "]" << std::endl;
    out << indent << "rankdir=LR" << std::endl;
    out << indent << "style=rounded" << std::endl;
}

#endif // DOXYGEN_BUILD

} // namespace detail

inline void writeFlattenedAsGraphviz(omni::core::ObjectParam<IGraph> inGraph,
                                     std::ostream& out,
                                     const bool deterministicAndSimplified)
{
    using namespace detail;

    out << "digraph ExecutionGraph {" << std::endl;
    {
        writeGraphProperties(singleIndent(), out);

        GraphState state;
        writeGraph(singleIndent(), "", nullptr, "", inGraph->getNodeGraphDef(), state, out, deterministicAndSimplified);
    }
    out << "}" << std::endl;
}

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
