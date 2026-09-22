// Copied from USD repository: https://github.com/PixarAnimationStudios/USD
// Modified to support assignment and move between vectors of different internal storage
//
// Copyright 2019 Pixar
//
// Licensed under the Apache License, Version 2.0 (the "Apache License")
// with the following modification; you may not use this file except in
// compliance with the Apache License and the following modification to it:
// Section 6. Trademarks. is deleted and replaced with:
//
// 6. Trademarks. This License does not grant permission to use the trade
//    names, trademarks, service marks, or product names of the Licensor
//    and its affiliates, except as required to comply with Section 4(c) of
//    the License and to reproduce the content of the NOTICE file.
//
// You may obtain a copy of the Apache License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the Apache License with the above modification is
// distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied. See the Apache License for the specific
// language governing permissions and limitations under the Apache License.
//

#pragma once


#include <algorithm>
#include <vector>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <initializer_list>
#include <iterator>
#include <limits>
#include <memory>
#include <new>
#include <type_traits>

namespace omni
{
// Contains parts of the small vector implementation that do not depend on
// *all* of SmallVector's template parameters.
class SmallVectorBase
{
public:
    using size_type = std::uint32_t;
    using difference_type = std::uint32_t;

    // Returns the local capacity that may be used without increasing the size
    // of the SmallVector.  SmallVector<T, N> will never use more local
    // capacity than is specified by N but clients that wish to maximize local
    // occupancy in a generic way can compute N using this function.
    template <typename U>
    static constexpr size_type ComputeSerendipitousLocalCapacity()
    {
        return (alignof(U) <= alignof(_Data<U, 0>)) ? sizeof(_Data<U, 0>) / sizeof(U) : 0;
    }

protected:
    // Invoke std::uninitialized_copy that either moves or copies entries,
    // depending on whether the type is move constructible or not.
    template <typename Iterator>
    static Iterator _UninitializedMove(Iterator first, Iterator last, Iterator dest)
    {
        return std::uninitialized_copy(std::make_move_iterator(first), std::make_move_iterator(last), dest);
    }

    // Invokes either the move or copy constructor (via placement new),
    // depending on whether U is move constructible or not.
    template <typename U>
    static void _MoveConstruct(U* p, U* src)
    {
        new (p) U(std::move(*src));
    }

    // The data storage, which is a union of both the local storage, as well
    // as a pointer, holding the address to the remote storage on the heap, if
    // used.
    template <typename U, size_type M>
    union _Data
    {
    public:
        U* GetLocalStorage()
        {
            return reinterpret_cast<U*>(_local);
        }

        const U* GetLocalStorage() const
        {
            return reinterpret_cast<const U*>(_local);
        }

        U* GetRemoteStorage()
        {
            return _remote;
        }

        const U* GetRemoteStorage() const
        {
            return _remote;
        }

        void SetRemoteStorage(U* p)
        {
            _remote = p;
        }

    private:
        alignas(U) char _local[sizeof(U) * M];
        U* _remote;
    };

    // For N == 0 the _Data class has been specialized to elide the local
    // storage completely. This way we don't have to rely on compiler-specific
    // support for 0-sized arrays.
    template <typename U>
    union _Data<U, 0>
    {
    public:
        U* GetLocalStorage()
        {
            // XXX: Could assert here. Introduce dependency on tf/diagnostic.h?
            return nullptr;
        }

        const U* GetLocalStorage() const
        {
            // XXX: Could assert here. Introduce dependency on tf/diagnostic.h?
            return nullptr;
        }

        U* GetRemoteStorage()
        {
            return _remote;
        }

        const U* GetRemoteStorage() const
        {
            return _remote;
        }

        void SetRemoteStorage(U* p)
        {
            _remote = p;
        }

    private:
        U* _remote = nullptr;
    };
};

////////////////////////////////////////////////////////////////////////////////
///
/// \class SmallVector
///
/// This is a small-vector class with local storage optimization, the local
/// storage can be specified via a template parameter, and expresses the
/// number of entries the container can store locally.
///
/// In addition to the local storage optimization, this vector is also
/// optimized for storing a smaller number of entries on the heap: It features
/// a reduced memory footprint (minimum 16 bytes) by limiting max_size() to
/// 2^32, which should still be more than enough for most use cases where a
/// small-vector is advantageous.
///
/// SmallVector mimics the std::vector API, and can thus be easily used as a
/// drop-in replacement where appropriate. Note, however, that not all the
/// methods on std::vector are implemented here, and that SmallVector may
/// have methods in addition to those that you would find on std::vector.
///
/// Note that a SmallVector that has grown beyond its local storage, will
/// NOT move its entries back into the local storage once it shrinks back to N.
///
template <typename T, std::size_t N>
class SmallVector : public SmallVectorBase
{
public:
    /// XXX: Functionality currently missing, and which we would like to add as
    ///  needed:
    ///     - emplace
    ///     - shrink_to_fit
    ///     - shrink_to_local / shrink_to_internal (or similar, free standing
    ///         function)

    /// \name Relevant Typedefs.
    /// @{

    typedef T value_type;
    typedef T& reference;
    typedef const T& const_reference;

    /// }@

    /// \name Iterator Support.
    /// @{

    using iterator = T*;
    using const_iterator = const T*;
    typedef std::reverse_iterator<iterator> reverse_iterator;
    typedef std::reverse_iterator<const_iterator> const_reverse_iterator;

    /// }@

    /// Default constructor.
    ///
    SmallVector() : _size(0), _capacity(N)
    {
    }

    /// Construct a vector holding \p n value-initialized elements.
    ///
    explicit SmallVector(size_type n) : _capacity(N)
    {
        _InitStorage(n);
        value_type* d = data();
        for (size_type i = 0; i < n; ++i)
        {
            new (d + i) value_type();
        }
    }

    /// Construct a vector holding \p n copies of \p v.
    ///
    SmallVector(size_type n, const value_type& v) : _capacity(N)
    {
        _InitStorage(n);
        std::uninitialized_fill_n(data(), n, v);
    }

    explicit SmallVector(const std::vector<T>& other) : _capacity(N)
    {
        _InitStorage(uint32_t(other.size()));
        std::uninitialized_copy(other.begin(), other.end(), begin());
    }

    /// Construct a vector holding \p n default-initialized elements.
    ///
    enum DefaultInitTag
    {
        DefaultInit
    };
    SmallVector(size_type n, DefaultInitTag) : _capacity(N)
    {
        _InitStorage(n);
        value_type* d = data();
        for (size_type i = 0; i < n; ++i)
        {
            new (d + i) value_type;
        }
    }

    /// Copy constructor.
    ///
    template <std::size_t rhsN>
    SmallVector(const SmallVector<T, rhsN>& rhs) : _capacity(N)
    {
        _InitStorage(rhs.size());
        std::uninitialized_copy(rhs.begin(), rhs.end(), begin());
    }

    SmallVector(const SmallVector& rhs) : _capacity(N)
    {
        _InitStorage(rhs.size());
        std::uninitialized_copy(rhs.begin(), rhs.end(), begin());
    }

    /// Move constructor.
    ///
    template <std::size_t rhsN>
    SmallVector(SmallVector<T, rhsN>&& rhs) : _size(0), _capacity(N)
    {
        // If rhs can not be stored locally, take rhs's remote storage and
        // reset rhs to empty.
        if (rhs.size() > N)
        {
            _data.SetRemoteStorage(rhs._data.GetRemoteStorage());
            std::swap(_capacity, rhs._capacity);
        }

        // If rhs is stored locally, it's faster to simply move the entries
        // into this vector's storage, destruct the entries at rhs, and swap
        // sizes. Note that capacities will be the same in this case, so no
        // need to swap those.
        else
        {
            _UninitializedMove(rhs.begin(), rhs.end(), begin());
            rhs._Destruct();
        }
        std::swap(_size, rhs._size);
    }

    /// Construct a new vector from initializer list
    SmallVector(std::initializer_list<T> values) : SmallVector(values.begin(), values.end())
    {
    }

    template <typename _ForwardIterator>
    using _EnableIfForwardIterator =
        typename std::enable_if<std::is_convertible<typename std::iterator_traits<_ForwardIterator>::iterator_category,
                                                    std::forward_iterator_tag>::value>::type;

    /// Creates a new vector containing copies of the data between
    /// \p first and \p last.
    template <typename ForwardIterator, typename = _EnableIfForwardIterator<ForwardIterator>>
    SmallVector(ForwardIterator first, ForwardIterator last) : _capacity(N)
    {
        _InitStorage(size_type(std::distance(first, last)));
        std::uninitialized_copy(first, last, begin());
    }

    /// Destructor.
    ///
    ~SmallVector()
    {
        _Destruct();
        _FreeStorage();
    }

    /// Assignment operators.
    ///
    SmallVector& operator=(const SmallVector& rhs)
    {
        if ((const void*)this != (const void*)&rhs)
        {
            assign(rhs.begin(), rhs.end());
        }
        return *this;
    }

    template <std::size_t rhsN>
    SmallVector& operator=(const SmallVector<T, rhsN>& rhs)
    {
        if ((const void*)this != (const void*)&rhs)
        {
            assign(rhs.begin(), rhs.end());
        }
        return *this;
    }

    /// Move assignment operator.
    ///
    template <std::size_t rhsN>
    SmallVector& operator=(SmallVector<T, rhsN>&& rhs)
    {
        if ((const void*)this != (const void*)&rhs)
        {
            swap(rhs);
        }
        return *this;
    }

    /// Replace existing contents with the contents of \p ilist.
    ///
    SmallVector& operator=(std::initializer_list<T> ilist)
    {
        assign(ilist.begin(), ilist.end());
        return *this;
    }

    void setRemoteDataAndCapacity(T* remoteStorage, size_type size, size_type capacity)
    {
        if (capacity <= N)
        {
            // move to local storage
            for (size_type i = 0; i < size; ++i)
            {
                _MoveConstruct(_data.GetLocalStorage() + i, remoteStorage + i);
                (*(remoteStorage + i)).~value_type();
            }
            _capacity = N;
            _size = size;

            free(remoteStorage);
        }
        else
        {
            _data.SetRemoteStorage(remoteStorage);
            _capacity = capacity;
            _size = size;
        }
    }

    template <std::size_t rhsN>
    void swapLocalToRemoteFits(SmallVector<T, rhsN>& rhs)
    {
        // Get a pointer to the remote storage. We'll be overwriting the
        // pointer value below, so gotta retain it first.
        value_type* remoteStorage = rhs._GetStorage();

        // Move all the entries from the vector with the local storage, to
        // the other vector's local storage. This will overwrite the pointer
        // to the other vectors remote storage. Note that we will have to
        // also destruct the elements at the source's local storage. The
        // source will become the one with the remote storage, so those
        // entries will be essentially freed.
        for (size_type i = 0; i < this->size(); ++i)
        {
            _MoveConstruct(rhs._data.GetLocalStorage() + i, &(*this)[i]);
            (*this)[i].~value_type();
        }


        // Swap sizes and capacities
        std::swap(rhs._size, this->_size);

        // Swap the remote storage into the vector which previously had the
        // local storage. It's been properly cleaned up now.
        setRemoteDataAndCapacity(remoteStorage, this->_size, rhs._capacity);
        rhs._capacity = rhsN;
    }

    template <std::size_t rhsN>
    void swapLocalToRemoteNoFit(SmallVector<T, rhsN>& rhs)
    {
        size_type tempSize = _size;
        T* newData = _Allocate(tempSize);
        for (size_type i = 0; i < tempSize; ++i)
        {
            _MoveConstruct(newData + i, &(*this)[i]);
            (*this)[i].~value_type();
        }

        setRemoteDataAndCapacity(rhs._data.GetRemoteStorage(), rhs.size(), rhs.capacity());

        rhs._data.SetRemoteStorage(newData);
        rhs._capacity = rhs._size = tempSize;
    }

    template <std::size_t rhsN>
    void swapWithLargerLocal(SmallVector<T, rhsN>& larger)
    {
        // Swap all the entries up to the size of the smaller vector.
        std::swap_ranges(this->begin(), this->end(), larger.begin());

        // Move the tail end of the entries, and destruct them at the
        // source vector.
        for (size_type i = this->size(); i < larger.size(); ++i)
        {
            _MoveConstruct(this->data() + i, larger.begin() + i);
            (larger.begin() + i)->~value_type();
        }

        // Swap sizes. Capacities are already correct in this case.
        std::swap(this->_size, larger._size);
    }

    /// Swap two vector instances.
    ///
    template <std::size_t rhsN>
    void swap(SmallVector<T, rhsN>& rhs)
    {
        // Both this vector and rhs are stored locally.
        if (_IsLocal() && rhs._IsLocal())
        {
            if ((rhs.size() <= N) && (size() <= rhsN))
            {
                if (this->size() > rhs.size())
                {
                    rhs.swapWithLargerLocal(*this);
                }
                else
                {
                    this->swapWithLargerLocal(rhs);
                }
            }
            else
            {
                auto swapWithAlloc = [](size_type fitSize, T* fitBegin, size_type doesntSize, T* doesntBegin) {
                    T* newData = _Allocate(doesntSize);
                    for (size_t i = 0; i < doesntSize; i++)
                    {
                        _MoveConstruct(&newData[i], doesntBegin + i);
                    }
                    for (size_t i = 0; i < fitSize; i++)
                    {
                        _MoveConstruct(doesntBegin + i, fitBegin + i);
                    }
                    return newData;
                };

                if (rhs.size() > N)
                {
                    // rhs doesn't fit into this local storage
                    this->_data.SetRemoteStorage(swapWithAlloc(this->size(), this->begin(), rhs.size(), rhs.begin()));
                    this->_capacity = rhs.size();
                }
                else
                {
                    // this local storage doesn't fit into rhs
                    rhs._data.SetRemoteStorage(swapWithAlloc(rhs.size(), rhs.begin(), this->size(), this->begin()));
                    rhs._capacity = this->size();
                }

                std::swap(this->_size, rhs._size);
            }
        }

        // Both this vector and rhs are stored remotely
        // Make sure they get changed to local storage if appropriate
        else if (!_IsLocal() && !rhs._IsLocal())
        {
            value_type* tempStorage = _data.GetRemoteStorage();
            size_type tempSize = _size;
            size_type tempCapacity = _capacity;
            setRemoteDataAndCapacity(rhs._data.GetRemoteStorage(), rhs.size(), rhs.capacity());
            rhs.setRemoteDataAndCapacity(tempStorage, tempSize, tempCapacity);
        }

        // Either this vector or rhs is stored remotely, whereas the other
        // one is stored locally.
        else
        {
            if (this->_IsLocal())
            {
                if ((this->size() <= rhsN))
                {
                    // this is local and fits rhs local
                    this->swapLocalToRemoteFits(rhs);
                }
                else
                {
                    // this is local but doesn't fits rhs local
                    this->swapLocalToRemoteNoFit(rhs);
                }
            }
            else
            {
                if ((rhs.size() <= N))
                {
                    // rhs is local and fits this local
                    rhs.swapLocalToRemoteFits(*this);
                }
                else
                {
                    // rhs is local but doesnt fits this local
                    rhs.swapLocalToRemoteNoFit(*this);
                }
            }
        }
    }

    /// Insert an rvalue-reference entry at the given iterator position.
    ///
    iterator insert(const_iterator it, value_type&& v)
    {
        return _Insert(it, std::move(v));
    }

    /// Insert an entry at the given iterator.
    ///
    iterator insert(const_iterator it, const value_type& v)
    {
        return _Insert(it, v);
    }

    /// Erase an entry at the given iterator.
    ///
    iterator erase(const_iterator it)
    {
        return erase(it, it + 1);
    }

    /// Erase entries between [ \p first, \p last ) from the vector.
    ///
    iterator erase(const_iterator it, const_iterator last)
    {
        value_type* p = const_cast<value_type*>(&*it);
        value_type* q = const_cast<value_type*>(&*last);

        // If we're not removing anything, bail out.
        if (p == q)
        {
            return iterator(p);
        }

        const difference_type num = static_cast<difference_type>(std::distance(p, q));

        // Move entries starting at last, down a few slots to starting a it.
        value_type* e = data() + size();
        std::move(q, e, p);

        // Destruct all the freed up slots at the end of the vector.
        for (value_type* i = (e - num); i != e; ++i)
        {
            i->~value_type();
        }

        // Bump down the size.
        _size -= num;

        // Return an iterator to the next entry.
        return iterator(p);
    }

    /// Reserve storage for \p newCapacity entries.
    ///
    void reserve(size_type newCapacity)
    {
        // Only reserve storage if the new capacity would grow past the local
        // storage, or the currently allocated storage. We'll grow to
        // accommodate exactly newCapacity entries.
        if (newCapacity > capacity())
        {
            _GrowStorage(newCapacity);
        }
    }

    /// Resize the vector to \p newSize and insert copies of \v.
    ///
    void resize(size_type newSize, const value_type& v = value_type())
    {
        // If the new size is smaller than the current size, let go of some
        // entries at the tail.
        if (newSize < size())
        {
            erase(const_iterator(data() + newSize), const_iterator(data() + size()));
        }

        // Otherwise, lets grow and fill: Reserve some storage, fill the tail
        // end with copies of v, and update the new size.
        else if (newSize > size())
        {
            reserve(newSize);
            std::uninitialized_fill(data() + size(), data() + newSize, v);
            _size = newSize;
        }
    }

    /// Clear the entries in the vector. Does not let go of the underpinning
    /// storage.
    ///
    void clear()
    {
        _Destruct();
        _size = 0;
    }

    /// Clears any previously held entries, and copies entries between
    /// [ \p first, \p last ) to this vector.
    ///
    template <typename ForwardIterator, typename = _EnableIfForwardIterator<ForwardIterator>>
    void assign(ForwardIterator first, ForwardIterator last)
    {
        clear();
        const difference_type newSize = static_cast<difference_type>(std::distance(first, last));
        reserve(newSize);
        std::uninitialized_copy(first, last, begin());
        _size = newSize;
    }

    /// Replace existing contents with the contents of \p ilist.
    ///
    void assign(std::initializer_list<T> ilist)
    {
        assign(ilist.begin(), ilist.end());
    }

    /// Emplace an entry at the back of the vector.
    ///
    template <typename... Args>
    void emplace_back(Args&&... args)
    {
        if (size() == capacity())
        {
            _GrowStorage(_NextCapacity());
        }
        new (data() + size()) value_type(std::forward<Args>(args)...);
        _size += 1;
    }

    /// Copy an entry to the back of the vector,
    ///
    void push_back(const value_type& v)
    {
        emplace_back(v);
    }

    /// Move an entry to the back of the vector.
    ///
    void push_back(value_type&& v)
    {
        emplace_back(std::move(v));
    }

    /// Copy the range denoted by [\p first, \p last) into this vector
    /// before \p pos.
    ///
    template <typename ForwardIterator>
    void insert(iterator pos, ForwardIterator first, ForwardIterator last)
    {
        static_assert(std::is_convertible<typename std::iterator_traits<ForwardIterator>::iterator_category,
                                          std::forward_iterator_tag>::value,
                      "Input Iterators not supported.");

        // Check for the insert-at-end special case as the very first thing so
        // that we give the compiler the best possible opportunity to
        // eliminate the general case code.
        const bool insertAtEnd = pos == end();

        const difference_type numNewElems = static_cast<difference_type>(std::distance(first, last));
        const size_type neededCapacity = size() + numNewElems;
        const size_type nextCapacity = std::max(_NextCapacity(), neededCapacity);

        // Insertions at the end would be handled correctly by the code below
        // without this special case.  However, insert(end(), f, l) is an
        // extremely common operation so we provide this fast path both to
        // avoid unneeded work and to make it easier for the compiler to
        // eliminate dead code when pos == end().
        if (insertAtEnd)
        {
            // The reallocation here is not a simple reserve.  We want to grow
            // the storage only when there are too many new elements but the
            // desired size is based on the growth factor.
            if (neededCapacity > capacity())
            {
                _GrowStorage(nextCapacity);
            }
            std::uninitialized_copy(first, last, end());
            _size += numNewElems;
            return;
        }

        if (neededCapacity > capacity())
        {
            // Because we need to realloc, we can do the insertion by copying
            // each range, [begin(), pos), [first, last), [pos, end()), into
            // the new storage.

            const size_type posI = static_cast<difference_type>(std::distance(begin(), pos));
            value_type* newStorage = _Allocate(nextCapacity);

            iterator newPrefixBegin = iterator(newStorage);
            iterator newPos = newPrefixBegin + posI;
            iterator newSuffixBegin = newPos + numNewElems;
            _UninitializedMove(begin(), pos, newPrefixBegin);
            std::uninitialized_copy(first, last, newPos);
            _UninitializedMove(pos, end(), newSuffixBegin);

            // Destroy old data and set up this new buffer.
            _Destruct();
            _FreeStorage();
            _data.SetRemoteStorage(newStorage);
            _capacity = nextCapacity;
        }
        else
        {
            // Insert in-place requires handling four ranges.
            //
            // For both the range-to-move [pos, end()) and the range-to-insert
            // [first, last), there are two subranges: the subrange to copy
            // and the subrange to uinitialized_copy.  Note that only three of
            // these ranges may be non-empty: either there is a non-empty
            // prefix of [pos, end()) that needs to be copied over existing
            // elements or there is a non-empty suffix of [first, last) that
            // needs to be placed in uninitialized storage.

            const difference_type numMoveElems = static_cast<difference_type>(std::distance(pos, end()));
            const difference_type numUninitMoves = std::min(numNewElems, numMoveElems);
            const difference_type numInitMoves = numMoveElems - numUninitMoves;
            const difference_type numUninitNews = numNewElems - numUninitMoves;
            const difference_type numInitNews = numNewElems - numUninitNews;

            // Move our existing elements out of the way of new elements.
            iterator umSrc = pos + numInitMoves;
            iterator umDst = end() + numUninitNews;
            _UninitializedMove(umSrc, end(), umDst);
            std::copy_backward(pos, umSrc, umDst);

            // Copy new elements into place.
            for (difference_type i = 0; i < numInitNews; ++i, ++first, ++pos)
            {
                *pos = *first;
            }
            std::uninitialized_copy(first, last, end());
        }

        _size += numNewElems;
    }

    /// Insert elements from \p ilist starting at position \p pos.
    ///
    void insert(iterator pos, std::initializer_list<T> ilist)
    {
        insert(pos, ilist.begin(), ilist.end());
    }

    /// Remove the entry at the back of the vector.
    ///
    void pop_back()
    {
        back().~value_type();
        _size -= 1;
    }

    /// Returns the current size of the vector.
    ///
    size_type size() const
    {
        return _size;
    }

    /// Returns the maximum size of this vector.
    ///
    static constexpr size_type max_size()
    {
        return std::numeric_limits<size_type>::max();
    }

    /// Returns \c true if this vector is empty.
    ///
    bool empty() const
    {
        return size() == 0;
    }

    /// Returns the current capacity of this vector. Note that if the returned
    /// value is <= N, it does NOT mean the storage is local. A vector that has
    /// previously grown beyond its local storage, will not move entries back to
    /// the local storage once it shrinks to N.
    ///
    size_type capacity() const
    {
        return _capacity;
    }

    /// Returns the local storage capacity. The vector uses its local storage
    /// if capacity() <= internal_capacity().
    /// This method mimics the boost::container::small_vector interface.
    ///
    static constexpr size_type internal_capacity()
    {
        return N;
    }

    /// \name Returns an iterator to the beginning of the vector.
    /// @{

    iterator begin()
    {
        return iterator(_GetStorage());
    }

    const_iterator begin() const
    {
        return const_iterator(_GetStorage());
    }

    const_iterator cbegin() const
    {
        return begin();
    }

    /// @}

    /// \name Returns an iterator to the end of the vector.
    /// @{

    iterator end()
    {
        return iterator(_GetStorage() + size());
    }

    const_iterator end() const
    {
        return const_iterator(_GetStorage() + size());
    }

    const_iterator cend() const
    {
        return end();
    }

    /// @}

    /// \name Returns a reverse iterator to the beginning of the vector.
    /// @{

    reverse_iterator rbegin()
    {
        return reverse_iterator(end());
    }

    const_reverse_iterator rbegin() const
    {
        return const_reverse_iterator(end());
    }

    const_reverse_iterator crbegin() const
    {
        return rbegin();
    }

    /// @}

    /// \name Returns a reverse iterator to the end of the vector.
    /// @{

    reverse_iterator rend()
    {
        return reverse_iterator(begin());
    }

    const_reverse_iterator rend() const
    {
        return const_reverse_iterator(begin());
    }

    const_reverse_iterator crend() const
    {
        return rend();
    }

    /// @}

    /// Returns the first element in the vector.
    ///
    reference front()
    {
        return *begin();
    }

    /// Returns the first element in the vector.
    ///
    const_reference front() const
    {
        return *begin();
    }

    /// Returns the last element in the vector.
    ///
    reference back()
    {
        return *(data() + size() - 1);
    }

    /// Returns the last elements in the vector.
    ///
    const_reference back() const
    {
        return *(data() + size() - 1);
    }

    /// Access the specified element.
    ///
    reference operator[](size_type i)
    {
        return *(data() + i);
    }

    /// Access the specified element.
    ///
    const_reference operator[](size_type i) const
    {
        return *(data() + i);
    }

    /// Direct access to the underlying array.
    ///
    value_type* data()
    {
        return _GetStorage();
    }

    /// Direct access to the underlying array.
    ///
    const value_type* data() const
    {
        return _GetStorage();
    }

    /// Lexicographically compares the elements in the vectors for equality.
    ///
    bool operator==(const SmallVector& rhs) const
    {
        return size() == rhs.size() && std::equal(begin(), end(), rhs.begin());
    }

    /// Lexicographically compares the elements in the vectors for inequality.
    ///
    bool operator!=(const SmallVector& rhs) const
    {
        return !operator==(rhs);
    }

    // Returns true if the local storage is used.
    bool _IsLocal() const
    {
        return _capacity <= N;
    }

    // Return a pointer to the storage, which is either local or remote
    // depending on the current capacity.
    value_type* _GetStorage()
    {
        return _IsLocal() ? _data.GetLocalStorage() : _data.GetRemoteStorage();
    }

    // Return a const pointer to the storage, which is either local or remote
    // depending on the current capacity.
    const value_type* _GetStorage() const
    {
        return _IsLocal() ? _data.GetLocalStorage() : _data.GetRemoteStorage();
    }

    // Free the remotely allocated storage.
    void _FreeStorage()
    {
        if (!_IsLocal())
        {
            free(_data.GetRemoteStorage());
        }
    }

    // Destructs all the elements stored in this vector.
    void _Destruct()
    {
        value_type* b = data();
        value_type* e = b + size();
        for (value_type* p = b; p != e; ++p)
        {
            p->~value_type();
        }
    }

    // Allocate a buffer on the heap.
    static value_type* _Allocate(size_type size)
    {
        return static_cast<value_type*>(malloc(sizeof(value_type) * size));
    }

    // Initialize the vector with new storage, updating the capacity and size.
    void _InitStorage(size_type size)
    {
        if (size > capacity())
        {
            _data.SetRemoteStorage(_Allocate(size));
            _capacity = size;
        }
        _size = size;
    }

    // Grow the storage to be able to accommodate newCapacity entries. This
    // always allocates remotes storage.
    void _GrowStorage(const size_type newCapacity)
    {
        value_type* newStorage = _Allocate(newCapacity);
        _UninitializedMove(begin(), end(), iterator(newStorage));
        _Destruct();
        _FreeStorage();
        _data.SetRemoteStorage(newStorage);
        _capacity = newCapacity;
    }

    // Returns the next capacity to use for vector growth. The growth factor
    // here is 1.5. A constant 1 is added so that we do not have to special
    // case initial capacities of 0 and 1.
    size_type _NextCapacity() const
    {
        const size_type cap = capacity();
        return cap + (cap / 2) + 1;
    }

    // Insert the value v at iterator it. We use this method that takes a
    // universal reference to de-duplicate the logic required for the insert
    // overloads, one taking an rvalue reference, and the other one taking a
    // const reference. This way, we can take the most optimal code path (
    // move, or copy without making redundant copies) based on whether v is
    // a rvalue reference or const reference.
    template <typename U>
    iterator _Insert(const_iterator it, U&& v)
    {
        value_type* newEntry;

        // If the iterator points to the end, simply push back.
        if (it == end())
        {
            push_back(std::forward<U>(v));
            return end() - 1;
        }

        // Grow the remote storage, if we need to. This invalidates iterators,
        // so special care must be taken in order to return a new, valid
        // iterator.
        else if (size() == capacity())
        {
            const size_type newCapacity = _NextCapacity();
            value_type* newStorage = _Allocate(newCapacity);

            value_type* i = const_cast<value_type*>(&*it);
            value_type* curData = data();
            newEntry = _UninitializedMove(curData, i, newStorage);

            new (newEntry) value_type(std::forward<U>(v));

            _UninitializedMove(i, curData + size(), newEntry + 1);

            _Destruct();
            _FreeStorage();

            _data.SetRemoteStorage(newStorage);
            _capacity = newCapacity;
        }

        // Our current capacity is big enough to allow us to simply shift
        // elements up one slot and insert v at it.
        else
        {
            // Move all the elements after it up by one slot.
            newEntry = const_cast<value_type*>(&*it);
            value_type* last = const_cast<value_type*>(&back());
            new (data() + size()) value_type(std::move(*last));
            std::move_backward(newEntry, last, last + 1);

            // Move v into the slot at the supplied iterator position.
            newEntry->~value_type();
            new (newEntry) value_type(std::forward<U>(v));
        }

        // Bump size and return an iterator to the newly inserted entry.
        ++_size;
        return iterator(newEntry);
    }

    // The current size of the vector, i.e. how many entries it contains.
    size_type _size;

    // The current capacity of the vector, i.e. how big the currently allocated
    // storage space is.
    size_type _capacity;

    // The vector storage, which is a union of the local storage and a pointer
    // to the heap memory, if allocated.
    _Data<value_type, N> _data;
};

////////////////////////////////////////////////////////////////////////////////

template <typename T, std::size_t N>
void swap(SmallVector<T, N>& a, SmallVector<T, N>& b)
{
    a.swap(b);
}

////////////////////////////////////////////////////////////////////////////////

} // namespace omni
