// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/Types.h>

#include <memory>
#include <vector>


namespace omni
{
namespace anim
{
namespace navigation
{
/**
 * Holds an array of 32-bit integers.
 */
class Int32Array
{
public:
    Int32Array(size_t size = 0, int value = 0);
    Int32Array(size_t size, const int* data);
    Int32Array(const Int32Array& other);

    ~Int32Array();

    size_t size() const;
    int* data();
    bool empty() const;

    void clear();
    void resize(size_t size, int value = 0);
    void copy(size_t size, const int* data);

    int& operator[](size_t index);
    const int& operator[](size_t index) const;

    /*! \cond PRIVATE */
protected:
    class Int32ArrayImpl
    {
    public:
        Int32ArrayImpl(size_t size, int value) : m_data(size, value){};

        Int32ArrayImpl(size_t size, const int* data) : m_data(data, data + size){};

        size_t size() const
        {
            return m_data.size();
        }

        int* data()
        {
            return m_data.data();
        }

        bool empty() const
        {
            return m_data.empty();
        }

        void clear()
        {
            m_data.clear();
        }

        void resize(size_t size, int value)
        {
            m_data.resize(size, value);
        }

        void copy(size_t size, const int* data)
        {
            m_data.assign(data, data + size);
        }

        int& operator[](size_t index)
        {
            return m_data[index];
        }

        const int& operator[](size_t index) const
        {
            return m_data[index];
        }

    private:
        std::vector<int> m_data;
    };
    Int32Array(const Int32ArrayImpl&);
    std::unique_ptr<Int32ArrayImpl> m_impl;
    /*! \endcond */
};

/**
 * Holds an array of 32-bit floating point numbers.
 */
class Float32Array
{
public:
    Float32Array(size_t size = 0, float value = 0.0f);
    Float32Array(size_t size, const float* data);
    Float32Array(const Float32Array& other);

    ~Float32Array();

    size_t size() const;
    float* data();
    bool empty() const;

    void clear();
    void resize(size_t size, float value = 0.0f);
    void copy(size_t size, const float* data);

    float& operator[](size_t index);
    const float& operator[](size_t index) const;

protected:
    class Float32ArrayImpl
    {
    public:
        Float32ArrayImpl(size_t size, float value) : m_data(size, value){};

        Float32ArrayImpl(size_t size, const float* data) : m_data(data, data + size){};

        Float32ArrayImpl(const std::vector<float>& data) : m_data(data){};

        size_t size() const
        {
            return m_data.size();
        }

        float* data()
        {
            return m_data.data();
        }

        bool empty() const
        {
            return m_data.empty();
        }

        void clear()
        {
            m_data.clear();
        }

        void resize(size_t size, float value)
        {
            m_data.resize(size, value);
        }

        void copy(size_t size, const float* data)
        {
            m_data.assign(data, data + size);
        }


        float& operator[](size_t index)
        {
            return m_data[index];
        }

        const float& operator[](size_t index) const
        {
            return m_data[index];
        }

    private:
        std::vector<float> m_data;
    };

    Float32Array(const Float32ArrayImpl&);
    std::unique_ptr<Float32ArrayImpl> m_impl;
};

/**
 * Holds an array of carb::Float3 values.
 */
class Vec3Array
{
public:
    Vec3Array(size_t size = 0, const carb::Float3& value = { 0, 0, 0 });
    Vec3Array(size_t size, const carb::Float3* data);
    Vec3Array(const Vec3Array& other);

    ~Vec3Array();

    size_t size() const;
    carb::Float3* data();
    bool empty() const;

    void clear();
    void resize(size_t size, const carb::Float3& value = { 0, 0, 0 });
    void copy(size_t size, const carb::Float3* data);

    carb::Float3& operator[](size_t index);
    const carb::Float3& operator[](size_t index) const;

protected:
    class Vec3ArrayImpl
    {
    public:
        Vec3ArrayImpl(size_t size, const carb::Float3& value) : m_data(size, value){};

        Vec3ArrayImpl(size_t size, const carb::Float3* data) : m_data(data, data + size){};

        Vec3ArrayImpl(const std::vector<carb::Float3>& data) : m_data(data){};

        size_t size() const
        {
            return m_data.size();
        }

        carb::Float3* data()
        {
            return m_data.data();
        }

        bool empty() const
        {
            return m_data.empty();
        }

        void clear()
        {
            m_data.clear();
        }

        void resize(size_t size, const carb::Float3& value)
        {
            m_data.resize(size, value);
        }

        void copy(size_t size, const carb::Float3* data)
        {
            m_data.assign(data, data + size);
        }

        carb::Float3& operator[](size_t index)
        {
            return m_data[index];
        }

        const carb::Float3& operator[](size_t index) const
        {
            return m_data[index];
        }

    private:
        std::vector<carb::Float3> m_data;
    };
    Vec3Array(const Vec3ArrayImpl&);
    std::unique_ptr<Vec3ArrayImpl> m_impl;
};


enum class DebugLineType
{
    None,
    TerrainBoundaryBorder,
    TerrainBoundaryFeature,
    Normal,
    Cut,
    Polygon,
    Vertex,
    CreaseVertex,
    FixedVertex,
    BorderDistanceFieldVertex,
    AreaDistanceFieldVertex,
    ObstacleDistanceFieldVertex,
    ClearanceFieldVertex,
    CreaseEdge,
    ObstacleBounds,
    ObstructedEdgeByObstacle,
    ObstructedEdgeByAgent,
    ObstructedEdgeByArea,
    VisibilityLine,
    Agent,
    AgentGoal,
    AgentPath,
    AStarSearch,
    AstarPath,

    NumLineTypes
};


struct DebugLines
{
    void clear()
    {
        vertexPairs.clear();
        lineTypes.clear();
        objectIds.clear();
        firstLineOfType.clear();
    }

    void sort()
    {
        int numLines = (int)vertexPairs.size() / 2;
        int numTypes = (int)DebugLineType::NumLineTypes;

        std::vector<int> numLinesOfType(numTypes, 0);

        for (int i = 0; i < numLines; i++)
        {
            int lineType = (int)lineTypes[i];
            if (lineType >= 0 && lineType < numTypes)
            {
                numLinesOfType[lineType]++;
            }
        }

        firstLineOfType.clear();
        firstLineOfType.resize(numTypes + 1, 0);

        int sumLines = 0;
        for (int i = 0; i < numTypes; i++)
        {
            firstLineOfType[i] = sumLines;
            sumLines += numLinesOfType[i];
        }
        firstLineOfType[numTypes] = numLines;

        // copy the data to the upper half of the arrays for sorting
        vertexPairs.resize(4 * numLines);
        lineTypes.resize(2 * numLines);
        objectIds.resize(2 * numLines);

        for (int i = 0; i < numLines; i++)
        {
            vertexPairs[2 * (numLines + i)] = vertexPairs[2 * i];
            vertexPairs[2 * (numLines + i) + 1] = vertexPairs[2 * i + 1];
            lineTypes[numLines + i] = lineTypes[i];
            objectIds[numLines + i] = objectIds[i];
        }

        int numSortedLines = 0;

        for (int i = 0; i < numLines; i++)
        {
            int lineType = (int)lineTypes[numLines + i];
            if (lineType >= 0 && lineType < numTypes)
            {
                int& pos = firstLineOfType[lineType];

                vertexPairs[2 * pos] = vertexPairs[2 * (numLines + i)];
                vertexPairs[2 * pos + 1] = vertexPairs[2 * (numLines + i) + 1];
                lineTypes[pos] = lineTypes[numLines + i];
                objectIds[pos] = objectIds[numLines + i];
                pos++;
                numSortedLines++;
            }
        }
        vertexPairs.resize(2 * numSortedLines);
        lineTypes.resize(numSortedLines);
        objectIds.resize(numSortedLines);
        // fix the first line of each type
        for (int i = 0; i < numTypes; i++)
        {
            firstLineOfType[i] -= numLinesOfType[i];
        }
    }

    /**
     * The debug lines as segments defined by pairs of vertices. The size is equal to the number of lines times two.
     */
    Vec3Array vertexPairs;
    /**
     * One value of type DebugLineType for each line. The size is equal to the number of lines.
     */
    Int32Array lineTypes;
    /**
     * One id for each line. The object the line belongs to. The size is equal to the number of lines.
     */
    Int32Array objectIds;
    /**
     * The first line of each type. The size is equal to the number of types plus one.
     * This array is only valid after calling sort().
     */
    Int32Array firstLineOfType;
};

}
}
}

#include "Types.inl"
