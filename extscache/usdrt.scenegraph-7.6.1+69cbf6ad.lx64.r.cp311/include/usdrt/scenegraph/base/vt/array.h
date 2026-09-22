// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file
//!
//! @brief VtArray

#include <gsl/span>
#include <omni/fabric/IFabric.h>

#include <memory>

namespace usdrt
{

//! @class VtArray
//! Represents an arbitrary dimensional rectangular container class.
//!
//! VtArray can
//! - own its own CPU memory via a std::vector<ElementType>
//! which follows Copy On Write and Copy On Non-Const Access, semantics
//! the same way Pixar's VtArray does
//! - refer to a Fabric CPU/GPU attribute via a stage ID, a path and an attribute
//! - refer to an external CPU python array (numpy) or GPU python array (pytorch/warp)
//!
//! @b Special RT functionality
//! When a VtArray is initialized from Fabric data,
//! generally with UsdAttribute.Get(),
//! its underlying span will point at data directly in
//! Fabric. In this default attached state, the VtArray
//! can be used to modify Fabric arrays directly.
//! The developer may choose to make an instance-local
//! copy of the array data using @ref DetachFromSource, at
//! which point modifications happen on the instance-local
//! array. @ref IsFabricData() will let you know if a VtArray
//! instance is reading/writing Fabric data directly.
//! See
//! - @ref DetachFromSource()
//! - @ref IsFabricData()
//! - @ref IsPythonData()
//! - @ref IsOwnData()
//! - @ref HasFabricCpuData()
//! - @ref HasFabricGpuData()
//! - @ref GetGpuData()
//!
//! @tparam ElementType The type of element contained in this VtArray
template <typename ElementType>
class VtArray
{
public:
    using element_type = ElementType;
    using value_type = std::remove_cv_t<ElementType>;
    using size_type = std::size_t;
    using pointer = element_type*;
    using const_pointer = const element_type*;
    using reference = element_type&;
    using const_reference = const element_type&;
    using difference_type = std::ptrdiff_t;

    //! Create an empty array
    VtArray();
    //! Copy @p other. The new array shares underlying data with @p other.
    VtArray(const VtArray<ElementType>& other);
    //! Move from !p other.  The new array takes ownership of !p other's
    //! underlying data.
    VtArray(VtArray<ElementType>&& other);
    //! Create an array with @p n value-initialized elements.
    VtArray(size_t n);
    //! Create a new array from @p span.
    //!
    //! Make a copy of data from @p span that is unique to this instance.
    VtArray(gsl::span<ElementType> span);
    //! Create a new array from @p vec.
    //!
    //! Make a copy of data from @p vec that is unique to this instance.
    VtArray(const std::vector<ElementType>& vec);
    //! Create a new array from given data.
    //! @param n size of array
    //! @param data Pointer to n elements.
    //! @param gpuData Pointer to GPU data.
    VtArray(size_t n, ElementType* data, void* gpuData);
    //! Create a new array from @p initList.
    //!
    //! Make a copy of data from @p initList that is unique to this instance.
    //! @param initList
    VtArray(std::initializer_list<ElementType> initList);
    //! Create a new array that points to fabric data.
    //! @param stageId stage on which this data exists.
    //! @param path path to the attribute whose value is this array data.
    //! @param attr attribute name whose value is this array data.
    VtArray(omni::fabric::StageReaderWriterId stageId, omni::fabric::PathC path, omni::fabric::TokenC attr);
    //! Destructor
    virtual ~VtArray();

    //! Copy assign from @p other. This array shares underlying data with
    //! @p other.
    virtual VtArray& operator=(const VtArray<ElementType>& other);
    //! Replace current array contents with a copy of those in @p other
    VtArray& operator=(gsl::span<ElementType> other);
    //! Replace current array contents with a copy of those in @p initList
    VtArray& operator=(std::initializer_list<ElementType> initList);
    //! Allows usage of [i].
    //! TODO more detail of gpu & fabric stuff
    ElementType& operator[](size_t index);
    //! Allows usage of [i].
    ElementType const& operator[](size_t index) const;

    //! Return the total number of elements in this array.
    size_t size() const;

    //! Return the capacity of this array.
    size_t capacity() const;

    //! Check if this array is empty.
    //! @returns Return true if empty, false otherwise.
    bool empty() const;

    //! Reset this array to empty.
    //!
    //! Reset the capactiy to 0, delete the contents, an nullify any external data pointers.
    virtual void reset();

    //! Resize this array.
    //!
    //! Localize the data, and resize. Increase the capacity if needed.
    //!
    //! @param newSize New length of this array.
    void resize(size_t newSize);

    //! Reserve memory to increase the length of this array
    //!
    //! Localize the data. If @p num is less than the max capacity
    //! of this array, reserve new localized memory for an array of size @p num.
    //! If this instance already contains local data, copy that to the new span.
    //!
    //! Used by @ref push_back.
    //!
    //! @param num new size of this array.
    void reserve(size_t num);

    //! Append @p element to the back of the array.
    //! @param element New element to add.
    void push_back(const ElementType& element);

    //! Localize the data, and return a pointer to the beginning of the data sequence.
    pointer data()
    {
        detach();
        return span().data();
    }
    //! Return a const pointer to the beginning of the data sequence.
    const_pointer data() const
    {
        return cspan().data();
    }
    //! Return a const pointer to the beginning of the data sequence.
    const_pointer cdata() const
    {
        return cspan().data();
    }

    //! Get the span for this data array.
    //!
    //! @returns Return the span for this data array.
    //!
    //! This can be:
    //! - the localized CPU memory
    //! - the Fabric data
    //! - the external CPU python array (numpy)
    //! - or the GPU python array (pytorch/warp)
    gsl::span<ElementType> span();

    //! Get the const span for this data array.
    //!
    //! @returns Return the const span for this data array.
    //!
    //! This can be:
    //! - the localized CPU memory
    //! - the Fabric data
    //! - the external CPU python array (numpy)
    //! - or the GPU python array (pytorch/warp)
    gsl::span<const ElementType> cspan() const;

    // Special RT functionality...

    //! Make an instance-local copy of the fabric array data, at
    //! which point modifications happen on the instance-local
    //! array.
    void DetachFromSource();
    //! Check if this instance is reading/writing Fabric data directly.
    //! @return true if this instance is reading/writing fabric data directly,
    //! and false if the data has been localized. See @ref DetatchFromSource.
    bool IsFabricData() const;
    //! Check if this instance was created from an external python object (buffer or cuda array interface)
    //! @return Returns true if this instance was created from an external python object.
    virtual bool IsPythonData() const;
    //! Check if this instance contains its own localized data (not external or fabric data)
    //! @return Return true if this data is localized.
    bool IsOwnData() const;

    //! Check if this instance has fabric cpu data. Debug use only.
    //! @return Return true if this instance has fabric CPU data, and false otherwise.
    //! @warning For debug use only.
    bool HasFabricCpuData() const;
    //! Check if this instance has fabric Gpu data. Debug use only.
    //! @return Return true if this instance has fabric GPU data, and false otherwise.
    //! @warning For debug use only.
    bool HasFabricGpuData() const;
    //! Get GPU data. Debugging use only.
    //! @returns Return void* pointer to GPU data.
    //! @warning For debug use only.
    void* GetGpuData() const;

    //! Iterator
    typedef gsl::details::span_iterator<ElementType> iterator;
    //! Const iterator
    typedef gsl::details::span_iterator<const ElementType> const_iterator;
    //! Reverse iterator
    typedef std::reverse_iterator<iterator> reverse_iterator;
    //! Const reverse iterator
    typedef std::reverse_iterator<const_iterator> const_reverse_iterator;

    //! Localizes the data, and returns an iterator to the first element in this array.
    iterator begin()
    {
        detach();
        return span().begin();
    }
    //! Returns an iterator to the element following the last element in this array.
    iterator end()
    {
        return span().end();
    }
    //! Returns a const iterator to the first element in this array.
    const_iterator cbegin()
    {
        return cspan().begin();
    }
    //! Returns a const iterator to the element following the last element in this array.
    const_iterator cend()
    {
        return cspan().end();
    }
    //! Localize the data, and return an iterator to the element following the last element in this array.
    reverse_iterator rbegin()
    {
        detach();
        return reverse_iterator(span().end());
    }
    //! Returns an iterator to the first element in this array.
    reverse_iterator rend()
    {
        return reverse_iterator(span().begin());
    }
    //! Localize the data, and return a const iterator to the element following the last element in this array.
    const_reverse_iterator rbegin() const
    {
        return const_reverse_iterator(cspan().end());
    }
    //! Returns a const iterator to the first element in this array.
    const_reverse_iterator rend() const
    {
        return const_reverse_iterator(cspan().begin());
    }
    //! Localize the data, and return a const iterator to the element following the last element in this array.
    const_reverse_iterator crbegin() const
    {
        return rbegin();
    }
    //! Returns a const iterator to the first element in this array.
    const_reverse_iterator crend() const
    {
        return rend();
    }


private:
    // If the m_data span is pointing at fabric data,
    // or if multiple VtArray instances are pointing
    // at the same underlying data, make a copy
    // of the data that is unique to this instance.
    // This is used to implement Copy On Write
    // and Copy On Non-Const Access, like Pixar's VtArray
    void detach();

    // Make an copy of data from iterable source that
    // is unique to this instance.
    template <typename Source>
    void localize(const Source& other);

    size_t m_size = 0;
    size_t m_capacity = 0;
    ElementType* m_data = nullptr;
    void* m_gpuData = nullptr;

    // Use a shared_ptr for lazy reference counting
    // in order to implement COW/CONCA functionality.
    std::shared_ptr<gsl::span<ElementType>> m_sharedData;

    // When a VtArray points to Fabric data we avoid using pointers which can change
    // without notice, instead we use Path and Attribute.
    omni::fabric::StageReaderWriterId m_stageId{ 0 };
    omni::fabric::PathC m_path{ 0 };
    omni::fabric::TokenC m_attr{ 0 };
};

template <typename ElementType>
inline VtArray<ElementType>::VtArray()
{
    m_sharedData = std::make_shared<gsl::span<ElementType>>();
}

template <typename ElementType>
inline VtArray<ElementType>::VtArray(const VtArray<ElementType>& other)
    : m_size(other.m_size),
      m_capacity(other.m_capacity),
      m_data(other.m_data),
      m_gpuData(other.m_gpuData),
      m_sharedData(other.m_sharedData),
      m_stageId(other.m_stageId),
      m_path(other.m_path),
      m_attr(other.m_attr)
{
}

template <typename ElementType>
inline VtArray<ElementType>::VtArray(VtArray<ElementType>&& other)
    : m_size(other.m_size),
      m_capacity(other.m_capacity),
      m_data(other.m_data),
      m_gpuData(other.m_gpuData),
      m_sharedData(std::move(other.m_sharedData)),
      m_stageId(other.m_stageId),
      m_path(other.m_path),
      m_attr(other.m_attr)
{
    other.m_data = nullptr;
    other.m_size = 0;
    other.m_capacity = 0;
    other.m_gpuData = nullptr;
    other.m_stageId.id = 0;
    other.m_path.path = 0;
    other.m_attr.token = 0;
}

template <typename ElementType>
inline VtArray<ElementType>::VtArray(size_t n) : m_size(n), m_capacity(n)
{
    m_sharedData = std::make_shared<gsl::span<ElementType>>(new ElementType[m_size], m_size);
}

template <typename ElementType>
inline VtArray<ElementType>::VtArray(gsl::span<ElementType> span) : m_size(span.size()), m_capacity(span.size())
{
    localize(span);
}

template <typename ElementType>
inline VtArray<ElementType>::VtArray(size_t n, ElementType* data, void* gpuData)
    : m_size(n), m_capacity(n), m_data(data), m_gpuData(gpuData)
{
}

template <typename ElementType>
inline VtArray<ElementType>::VtArray(omni::fabric::StageReaderWriterId stageId,
                                     omni::fabric::PathC path,
                                     omni::fabric::TokenC attr)
    : m_stageId(stageId), m_path(path), m_attr(attr)
{
}

template <typename ElementType>
inline VtArray<ElementType>::VtArray(std::initializer_list<ElementType> initList)
{
    localize(initList);
}

template <typename ElementType>
inline VtArray<ElementType>::VtArray(const std::vector<ElementType>& vec)
{
    localize(vec);
}

template <typename ElementType>
inline VtArray<ElementType>& VtArray<ElementType>::operator=(const VtArray<ElementType>& other)
{
    m_size = other.m_size;
    m_capacity = other.m_capacity;
    m_data = other.m_data;
    m_gpuData = other.m_gpuData;
    m_sharedData = other.m_sharedData;
    m_stageId = other.m_stageId;
    m_path = other.m_path;
    m_attr = other.m_attr;

    return *this;
}

template <typename ElementType>
inline VtArray<ElementType>& VtArray<ElementType>::operator=(gsl::span<ElementType> other)
{
    localize(other);

    return *this;
}

template <typename ElementType>
inline VtArray<ElementType>& VtArray<ElementType>::operator=(std::initializer_list<ElementType> initList)
{
    localize(initList);

    return *this;
}

template <typename ElementType>
inline ElementType const& VtArray<ElementType>::operator[](size_t index) const
{
    return cspan()[index];
}

template <typename ElementType>
inline ElementType& VtArray<ElementType>::operator[](size_t index)
{
    if (m_stageId.id == 0)
    {
        // Allow writing to Fabric only
        detach();
    }
    return span()[index];
}

template <typename ElementType>
inline VtArray<ElementType>::~VtArray()
{
    reset();
}

template <typename ElementType>
inline void VtArray<ElementType>::reset()
{
    if (m_sharedData.use_count() == 1 && m_sharedData->data())
    {
        delete[] m_sharedData->data();
    }
    m_data = nullptr;
    m_gpuData = nullptr;
    m_size = 0;
    m_capacity = 0;
    m_stageId.id = 0;
    m_path.path = 0;
    m_attr.token = 0;
}

template <typename ElementType>
inline gsl::span<ElementType> VtArray<ElementType>::span()
{
    if (m_sharedData)
    {
        // Note - the m_sharedData span may be larger than m_size
        // if there is reserved capacity, so return a new span
        // that has a size of m_size
        return gsl::span<ElementType>(m_sharedData->data(), m_size);
    }
    if (m_data)
    {
        return gsl::span<ElementType>(m_data, m_size);
    }
    if (m_gpuData)
    {
        return gsl::span<ElementType>((ElementType*)m_gpuData, m_size);
    }
    if (m_stageId.id)
    {
        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        size_t size = iStageReaderWriter->getArrayAttributeSize(m_stageId, m_path, m_attr);
        auto validBits = iStageReaderWriter->getAttributeValidBits(m_stageId, m_path, m_attr);
        if (uint32_t(validBits & omni::fabric::ValidMirrors::eCPU) != 0)
        {
            auto fabSpan = iStageReaderWriter->getArrayAttribute(m_stageId, m_path, m_attr);
            return gsl::span<ElementType>((ElementType*)fabSpan.ptr, size);
        }
        else if (uint32_t(validBits & omni::fabric::ValidMirrors::eCudaGPU) != 0)
        {
            auto fabSpan = iStageReaderWriter->getAttributeGpu(m_stageId, m_path, m_attr);
            return gsl::span<ElementType>((ElementType*)fabSpan.ptr, size);
        }
    }
    return gsl::span<ElementType>();
}

template <typename ElementType>
inline gsl::span<const ElementType> VtArray<ElementType>::cspan() const
{
    if (m_sharedData)
    {
        // Note - the m_sharedData span may be larger than m_size
        // if there is reserved capacity, so return a new span
        // that has a size of m_size
        return gsl::span<const ElementType>(m_sharedData->data(), m_size);
    }
    if (m_data)
    {
        return gsl::span<const ElementType>(m_data, m_size);
    }
    if (m_gpuData)
    {
        return gsl::span<const ElementType>((const ElementType*)m_gpuData, m_size);
    }
    if (m_stageId.id)
    {
        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        size_t size = iStageReaderWriter->getArrayAttributeSize(m_stageId, m_path, m_attr);
        auto validBits = iStageReaderWriter->getAttributeValidBits(m_stageId, m_path, m_attr);
        if (uint32_t(validBits & omni::fabric::ValidMirrors::eCPU) != 0)
        {
            auto fabSpan = iStageReaderWriter->getArrayAttributeRd(m_stageId, m_path, m_attr);
            return gsl::span<const ElementType>((const ElementType*)fabSpan.ptr, size);
        }
        else if (uint32_t(validBits & omni::fabric::ValidMirrors::eCudaGPU) != 0)
        {
            auto fabSpan = iStageReaderWriter->getAttributeRdGpu(m_stageId, m_path, m_attr);
            return gsl::span<const ElementType>((const ElementType*)fabSpan.ptr, size);
        }
    }
    return gsl::span<const ElementType>();
}

template <typename ElementType>
inline size_t VtArray<ElementType>::size() const
{
    return cspan().size();
}


template <typename ElementType>
inline size_t VtArray<ElementType>::capacity() const
{
    if (!IsOwnData())
    {
        return cspan().size();
    }

    return m_capacity;
}

template <typename ElementType>
inline bool VtArray<ElementType>::empty() const
{
    return cspan().empty();
}

template <typename ElementType>
inline bool VtArray<ElementType>::IsFabricData() const
{
    return m_stageId.id != 0;
}

template <typename ElementType>
inline bool VtArray<ElementType>::IsPythonData() const
{
    // Override in python bindings
    return false;
}

template <typename ElementType>
inline bool VtArray<ElementType>::IsOwnData() const
{
    return (bool)m_sharedData;
}

template <typename ElementType>
inline bool VtArray<ElementType>::HasFabricGpuData() const
{
    if (m_stageId.id)
    {
        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        auto validBits = iStageReaderWriter->getAttributeValidBits(m_stageId, m_path, m_attr);
        return uint32_t(validBits & omni::fabric::ValidMirrors::eCudaGPU) != 0;
    }
    return false;
}

template <typename ElementType>
inline bool VtArray<ElementType>::HasFabricCpuData() const
{
    if (m_stageId.id)
    {
        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        auto validBits = iStageReaderWriter->getAttributeValidBits(m_stageId, m_path, m_attr);
        return uint32_t(validBits & omni::fabric::ValidMirrors::eCPU) != 0;
    }
    return false;
}

template <typename ElementType>
inline void* VtArray<ElementType>::GetGpuData() const
{
    if (m_gpuData)
        return m_gpuData;
    if (m_stageId.id)
    {
        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        auto validBits = iStageReaderWriter->getAttributeValidBits(m_stageId, m_path, m_attr);
        if (uint32_t(validBits & omni::fabric::ValidMirrors::eCudaGPU) != 0)
        {
            auto fabCSpan = iStageReaderWriter->getAttributeRdGpu(m_stageId, m_path, m_attr);
            return *(void**)fabCSpan.ptr;
        }
    }
    return nullptr;
}

template <typename ElementType>
inline void VtArray<ElementType>::DetachFromSource()
{
    detach();
}

template <typename ElementType>
inline void VtArray<ElementType>::detach()
{
    if (m_sharedData && m_sharedData.use_count() == 1)
    {
        // No need to detach from anything
        return;
    }
    // multiple VtArray have pointers to
    // the same underyling data, so localize
    // a copy before modifiying
    // This mirror's VtArray's COW, CONCA behavior
    // https://graphics.pixar.com/usd/release/api/class_vt_array.html#details
    localize(span());
}

template <typename ElementType>
template <typename Source>
inline void VtArray<ElementType>::localize(const Source& other)
{
    reset();
    m_size = other.size();
    m_capacity = other.size();
    m_sharedData = std::make_shared<gsl::span<ElementType>>(new ElementType[m_size], m_size);
    std::copy(other.begin(), other.end(), m_sharedData->begin());
}

template <typename ElementType>
inline void VtArray<ElementType>::resize(size_t newSize)
{
    detach();

    std::shared_ptr<gsl::span<ElementType>> tmpSpan =
        std::make_shared<gsl::span<ElementType>>(new ElementType[newSize], newSize);
    if (newSize > m_capacity)
    {
        std::copy(m_sharedData->begin(), m_sharedData->end(), tmpSpan->begin());
    }
    else
    {
        std::copy(m_sharedData->begin(), m_sharedData->begin() + newSize, tmpSpan->begin());
    }

    delete m_sharedData->data();
    m_sharedData = tmpSpan;
    m_size = newSize;
    m_capacity = newSize;
}

template <typename ElementType>
inline void VtArray<ElementType>::reserve(size_t num)
{
    detach();

    if (num <= m_capacity)
    {
        return;
    }

    std::shared_ptr<gsl::span<ElementType>> tmpSpan = std::make_shared<gsl::span<ElementType>>(new ElementType[num], num);
    if (m_size > 0)
    {
        std::copy(m_sharedData->begin(), m_sharedData->end(), tmpSpan->begin());
        delete m_sharedData->data();
    }
    m_sharedData = tmpSpan;
    m_capacity = num;
}

template <typename ElementType>
inline void VtArray<ElementType>::push_back(const ElementType& element)
{
    detach();

    if (m_size == m_capacity)
    {
        if (m_size == 0)
        {
            reserve(2);
        }
        else
        {
            reserve(m_size * 2);
        }
    }

    (*m_sharedData)[m_size] = element;
    m_size++;
}

} // namespace usdrt
