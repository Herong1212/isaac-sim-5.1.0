// Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <omni/fabric/IFabric.h>
#include <omni/utils/BitVector.h>
#include <carb/tasking/TaskingUtils.h>
#include <carb/cpp/Variant.h>

#include <cstdint>
#include <functional>
#include <vector>
#include <tuple>
#include <utility>

namespace query
{
using namespace std;

using Token = omni::fabric::Token;
using Span = omni::fabric::SpanC;
using ConstSpan = omni::fabric::ConstSpanC;
using StageReaderWriter = omni::fabric::StageReaderWriter;
using BucketId = omni::fabric::BucketId;
using AttribId = uint32_t;
using Type = omni::fabric::Type;
struct Tag {};
struct SchemaTag {};
struct PrimTypeTag {};
struct Path
{
    omni::fabric::PathC value;

    Path() = default;
    Path(omni::fabric::PathC v) : value(v) {};
    operator omni::fabric::PathC() const { return value; }
};
struct ElementCount
{
    size_t value = 0;

    ElementCount() = default;
    ElementCount(size_t v) : value(v) {};
    operator size_t() const { return value; }
};

struct DBAccess
{
    StageReaderWriter& rw;
    omni::fabric::IStageReaderWriter& irw;
    omni::fabric::StageReaderWriterId id;
    omni::fabric::IPrimBucketList* iPrimBucketList;
};


// typed version of the fabric span, so that we can do typed access
template<typename T>
struct TypedSpan : Span
{
    TypedSpan<T>() = default;
    TypedSpan<T>(const Span& span) : Span(span) {}

    T& operator[](size_t index) { return *(T*)(ptr + elementSize * index); }
};
template<typename T>
struct TypedConstSpan : ConstSpan
{
    TypedConstSpan<T>() = default;
    TypedConstSpan<T>(const ConstSpan& span) : ConstSpan(span) {}

    const T& operator[](size_t index) const { return *(const T*)(ptr + elementSize * index); }
};

template<>
struct TypedConstSpan<void> : ConstSpan
{
    TypedConstSpan<void>() = default;
    TypedConstSpan<void>(const ConstSpan& span) : ConstSpan(span) {}
};

struct Connection
{
    omni::fabric::PathC path;
    omni::fabric::TokenC token;

    Connection() = default;
    Connection(omni::fabric::PathC p, omni::fabric::TokenC t) : path(p), token(t) {};

};

omni::fabric::PathC getPath(const Path& p) { return p.value; }

omni::fabric::PathC getPath(const Connection& c) { return c.path; }


// parameter type traits to get the type description from the Type
template<typename T>
struct ParamTypeTrait
{
    static constexpr omni::fabric::Type typeDesc = { omni::fabric::BaseDataType::eUnknown };
};

#define TYPE_PARAMTYPETRAIT(type, baseType, components) namespace query { template<> struct ParamTypeTrait<type> { static constexpr Type typeDesc = { omni::fabric::BaseDataType::baseType, components }; }; }
#define TYPE_PARAMTYPETRAIT_ROLE(type, baseType, components, role) namespace query { template<> struct ParamTypeTrait<type> { static constexpr Type typeDesc = { omni::fabric::BaseDataType::baseType, components, 0, omni::fabric::AttributeRole::role }; }; }

struct AttribTypeDesc
{
    Type type;
    bool isPointer;
};

template<typename T>
constexpr AttribTypeDesc getParamDescTrait()
{
    return { ParamTypeTrait<typename std::remove_pointer<T>::type>::typeDesc, std::is_pointer<T>::value };
}

using Suffix = omni::fabric::NameSuffix;
using Role = omni::fabric::AttributeRole;

template<typename ValueT, typename ArrayT = ValueT, bool isArray = false>
omni::fabric::AttrNameAndType getAttrNameAndType(const char* usdAttribName, Role usdRole = 0)
{
    Suffix suffix = Suffix::none;
    AttribTypeDesc desc = getParamDescTrait<ValueT>();
    if (usdRole != Role::eNone)
    {
        desc.type.role = usdRole;
    }
    if (isArray)
    {
        AttribTypeDesc arrayTypeDesc = getParamDescTrait<ArrayT>();
        desc.type.baseType = arrayTypeDesc.type.baseType;
        desc.type.componentCount = arrayTypeDesc.type.componentCount;
        desc.type.arrayDepth = 1;
        suffix = Suffix::none;
        static_assert(!isArray || std::is_pointer_v<ValueT>, "Array attributes that are not the element count must be a pointer");
    }
    if (desc.type.baseType == omni::fabric::BaseDataType::eUnknown)
    {
        static_assert(sizeof(ValueT) / 4 < 256, "Can't store custom types larger than 256 uint32_t");
        CARB_ASSERT((sizeof(ValueT) & 0x3) == 0);
        desc.type.componentCount = sizeof(ValueT) / 4;
    }
    if (desc.type.baseType == omni::fabric::BaseDataType::eConnection)
    {
        suffix = Suffix::connection;
    }
    return { desc.type, usdAttribName, suffix };
}

#define DEFINE_FC_ATTRIB_BASE(arrayT, attributeType, attribName, usdAttribName, usdRole, isAttribArray) \
    struct attribName  \
    {  \
        using AttribT = attribName;  \
        using ArrayT = arrayT;  \
        using ValueT = attributeType;  \
        static constexpr const char* name = #attribName;  \
        static constexpr const char* usdName = usdAttribName;  \
        static constexpr omni::fabric::AttributeRole role = usdRole;  \
        static constexpr bool isArray = isAttribArray;  \
        static constexpr bool isElemCount = isArray && std::is_same_v<ValueT, query::ElementCount>;  \
        static constexpr uint32_t argTypeFlags = 0; \
};  \

#define DEFINE_FC_ATTRIB(attributeType, attribName) DEFINE_FC_ATTRIB_BASE(attributeType, attributeType, attribName, #attribName, omni::fabric::AttributeRole::eNone, false)
#define DEFINE_FC_ATTRIB_ROLE(attributeType, attribName, usdRole) DEFINE_FC_ATTRIB_BASE(attributeType, attributeType, attribName, #attribName, usdRole, false)
#define DEFINE_FC_ATTRIB_USDNAME(attributeType, attribName, usdAttribName) DEFINE_FC_ATTRIB_BASE(attributeType, attributeType, attribName, usdAttribName, omni::fabric::AttributeRole::eNone, false)
#define DEFINE_FC_ATTRIB_USDNAME_ROLE(attributeType, attribName, usdAttribName, usdRole) DEFINE_FC_ATTRIB_BASE(attributeType, attributeType, attribName, usdAttribName, usdRole, false)

#define DEFINE_FC_ARRAY(arrayT, attributeType, attribName) DEFINE_FC_ATTRIB_BASE(arrayT, attributeType, attribName, #attribName, omni::fabric::AttributeRole::eNone, true)
#define DEFINE_FC_ARRAY_ROLE(arrayT, attributeType, attribName, usdRole) DEFINE_FC_ATTRIB_BASE(arrayT, attributeType, attribName, #attribName, usdRole, true)
#define DEFINE_FC_ARRAY_USDNAME(arrayT, attributeType, attribName, usdAttribName) DEFINE_FC_ATTRIB_BASE(arrayT, attributeType, attribName, usdAttribName, omni::fabric::AttributeRole::eNone, true)
#define DEFINE_FC_ARRAY_USDNAME_ROLE(arrayT, attributeType, attribName, usdAttribName, usdRole) DEFINE_FC_ATTRIB_BASE(arrayT, attributeType, attribName, usdAttribName, usdRole, true)

enum class ArgTypeFlags
{
    None = 0,
    Optional = 1 << 0,
    OneOf = 1 << 1,
};

// a list of types for the various input slots of a query
template<typename... ArgTypes>
struct List
{
    using ListT = List<ArgTypes...>;
    static constexpr size_t length = sizeof...(ArgTypes);

    std::vector<omni::fabric::AttrNameAndType> nameAndTypes;
    std::vector<omni::fabric::Typeinfo> typeInfos;
    std::vector<uint32_t> argTypeFlags;

    void make()
    {
        nameAndTypes = { getAttrNameAndType<typename ArgTypes::ValueT, typename ArgTypes::ArrayT, ArgTypes::isArray>(ArgTypes::usdName, ArgTypes::role)... };
        typeInfos = { { sizeof(typename ArgTypes::ValueT), ArgTypes::isArray, ArgTypes::isArray ? sizeof(typename ArgTypes::ArrayT) : 0}... };
        argTypeFlags = { ArgTypes::argTypeFlags... };
    }

    void build(omni::fabric::set<omni::fabric::AttrNameAndType>& all, omni::fabric::set<omni::fabric::AttrNameAndType>& any)
    {
        make();

        uint32_t idx = 0;
        for (omni::fabric::AttrNameAndType nameAndType : nameAndTypes)
        {
            if (nameAndType.suffix != omni::fabric::NameSuffix::connection)
            {
                nameAndType.suffix = omni::fabric::NameSuffix::none; // the suffix is not part of the bucket attribute search, so we need to clear it here
            }
            if ((argTypeFlags[idx] & uint32_t(ArgTypeFlags::OneOf)) != 0)
            {
                any.insert(std::move(nameAndType));
            }
            else if ((argTypeFlags[idx] & uint32_t(ArgTypeFlags::Optional)) == 0)
            {
                all.insert(std::move(nameAndType));
            }
            idx++;
        }
    }

    void bind(DBAccess& dbAccess) const
    {
    }

    template<std::size_t I = 0, typename T, typename... Args>
    inline static constexpr typename std::enable_if<I == sizeof...(Args), size_t>::type
        getIdxInternal()
    {
        return ~0;
    }

    template<std::size_t I = 0, typename T, typename... Args>
    inline static constexpr typename std::enable_if < I < sizeof...(Args), size_t>::type
        getIdxInternal()
    {
        if (std::is_same_v<typename std::tuple_element<I, std::tuple<Args...>>::type::AttribT, T>)
            return I;
        else
            return getIdxInternal<I + 1, T, Args...>();
    }

    template<typename T>
    constexpr static size_t getIdx()
    {
        constexpr auto I = getIdxInternal<0, T, ArgTypes...>();
        static_assert(I < sizeof...(ArgTypes), "Requested attribute not found in list. Index out of range");
        return I;
    }

    // base class for the storage of the data binding to attribute spans
    template<typename DerivedT>
    struct Data
    {
        size_t row = 0;
        bool isCreated = false;

        template<std::size_t I = 0, typename... Args>
        inline typename std::enable_if<I == sizeof...(Args), bool>::type
        bindBucketAttributes(BucketId bucket, const ListT& attributes, DBAccess& dbAccess, const omni::fabric::PrimBucketListId& PrimBucketListId)
        {
            return true;
        }

        template<std::size_t I = 0, typename... Args>
        inline typename std::enable_if < I < sizeof...(Args), bool>::type
        bindBucketAttributes(BucketId bucket, const ListT& attributes, DBAccess& dbAccess, const omni::fabric::PrimBucketListId& PrimBucketListId)
        {
            using AttributeTuple = std::tuple<Args...>;
            derived().template getSpan<I>() = derived().template bindAttribute<typename std::tuple_element<0, AttributeTuple>::type>(bucket, attributes.nameAndTypes[I], dbAccess, PrimBucketListId);
            if (!(attributes.argTypeFlags[I] & uint32_t(ArgTypeFlags::Optional)) && (derived().template getSpan<I>().ptr == nullptr))
            {
                return false;
            }
            return bindBucketAttributes<I + 1, Args...>(bucket, attributes, dbAccess, PrimBucketListId);            
        }

        bool bindBucketAttributes(BucketId bucket, const ListT& attributes, DBAccess& dbAccess, const omni::fabric::PrimBucketListId& PrimBucketListId)
        {
            return bindBucketAttributes<0, ArgTypes...>(bucket, attributes, dbAccess, PrimBucketListId);
        }

        void setRow(size_t idx, bool isNew_ = false)
        {
            row = idx;
        }

        DerivedT& derived() { return *(DerivedT*)this; }
    };


    struct DataRead : Data<DataRead>
    {
        tuple<TypedConstSpan<typename ArgTypes::ValueT>...> refs;

        template<typename T>
        auto bindAttribute(BucketId bucket, const omni::fabric::AttrNameAndType& attrib, DBAccess& db, const omni::fabric::PrimBucketListId& primBucketListId)
        {
            // TODO use return type that merges the array and non-array case
            if (attrib.type.isArray())
            {
                omni::fabric::ConstArrayPointersAndSizesWithTypeC arrayData = db.irw.getArrayAttributeArrayWithSizesRd(db.id, primBucketListId, bucket.id, attrib.name.asTokenC());
                return TypedConstSpan<typename T::ValueT>(omni::fabric::ConstSpanC{ (const uint8_t*)arrayData.arrayPtrs, arrayData.elementCount, sizeof(void*) });
            }
            else
            {
                omni::fabric::ConstSpanWithTypeC arrayData;
                db.irw.getAttributeArrayRd(&arrayData, db.id, primBucketListId, bucket.id, attrib.name.asTokenC());
                return TypedConstSpan<typename T::ValueT>(omni::fabric::ConstSpanC{ arrayData.ptr, arrayData.elementCount, arrayData.elementSize });
            }
        }

        template<std::size_t I = 0>
        auto& getSpan()
        {
            static_assert(I < sizeof...(ArgTypes), "index out of range");
            return std::get<I>(refs);
        }

        template<size_t I = 0>
        const auto& get() const
        {
            static_assert(I < sizeof...(ArgTypes), "index out of range");
            return std::get<I>(refs)[Data<DataRead>::row];
        }
    };

    struct DataReadWrite : Data<DataReadWrite>
    {
        tuple<TypedSpan<typename ArgTypes::ValueT>...> refs;

        template<typename T>
        auto bindAttribute(BucketId bucket, const omni::fabric::AttrNameAndType& attrib, DBAccess& db, const omni::fabric::PrimBucketListId& primBucketListId)
        {            
            if (attrib.type.isArray())
            {
                omni::fabric::ConstArrayPointersAndSizesWithTypeC arrayData = db.irw.getArrayAttributeArrayWithSizes(db.id, primBucketListId, bucket.id, attrib.name.asTokenC());
                return TypedSpan<typename T::ValueT>{ arrayData.arrayPtrs, arrayData.elementCount, sizeof(void*)};
            }
            else
            {
                omni::fabric::ConstSpanWithTypeC arrayData;
                db.irw.getAttributeArray(&arrayData, db.id, primBucketListId, bucket.id, attrib.name.asTokenC());
                return TypedSpan<typename T::ValueT>{ arrayData.ptr, arrayData.elementCount, arrayData.elementSize};
            }
        }

        template<size_t I = 0>
        auto& getSpan()
        {
            static_assert(I < sizeof...(ArgTypes), "index out of range");
            return std::get<I>(refs);
        }

        template<size_t I = 0>
        auto& get()
        {
            static_assert(I < sizeof...(ArgTypes), "index out of range");
            return std::get<I>(refs)[Data<DataReadWrite>::row];
        }
    };

    struct DataAdd
    {
        Path path;
        size_t attribIndex;
        carb::cpp::variant<size_t*, typename ArgTypes::ValueT...> attribute;
    };
};

struct QueryAttributeLists
{
    omni::fabric::set<omni::fabric::AttrNameAndType> all;
    omni::fabric::set<omni::fabric::AttrNameAndType> addAttributes;
    omni::fabric::set<omni::fabric::AttrNameAndType> newAttributes;
    omni::fabric::set<omni::fabric::AttrNameAndType> any;
    omni::fabric::set<omni::fabric::AttrNameAndType> none;
    bool hasRegisteredTypes = false;
};

struct SingleThreading
{
    constexpr static bool value = false;
    constexpr static size_t batchSize = 1;
};

template<size_t BatchSize = 16>
struct MultiThreading
{
    constexpr static bool value = true;
    constexpr static size_t batchSize = BatchSize;
};

template<typename T>
struct Optional : T
{
    static constexpr uint32_t argTypeFlags = uint32_t(ArgTypeFlags::Optional);
};

template<typename T>
struct OneOf : T
{
    static constexpr uint32_t argTypeFlags = uint32_t(ArgTypeFlags::OneOf);
};

struct AttribNone
{
};

struct QueryNone
{
    struct Attributes
    {
        void build(QueryAttributeLists& lists) {}
    };

    struct Row
    {
        size_t elementCount;
    };
};

struct StandardTransformType
{
    using InnerQueryT = QueryNone;
    static constexpr int queryType = 0;
};

template<typename AttribType, typename InnerQueryType>
struct Gather
{
    using AttribT = AttribType;
    using InnerQueryT = InnerQueryType;
    static constexpr int queryType = 1;
};

struct TransformContext
{
    TransformContext(const DBAccess& db_, omni::fabric::IPath* path_)
        : db(db_), path(path_)
    {}

    DBAccess db;
    omni::fabric::IPath* path;
};

// base class of a derived query. a derived query overloads the types (Read, Write, Deps, Create) to add attributes 
template<typename QueryType>
struct Query
{
    using TransformType = StandardTransformType;
    using Read = List<>;        // attributes accessible as read-only
    using Write = List<>;       // attributes accessible as read-write
    using Deps = List<>;        // attributes that only need to be present (tags)
    using Exclude = List<>;     // attributes that should not be present
    using Add = List<>;         // attributes that will be added, they can be accessed as write-only
    using AddDeferred = List<>; // attributes that can be added optionally, they will be added only after the transform has executed
    using Create = List<>;      // attributes of new prims that can be created
    using Threading = SingleThreading; // threading policy for this query
    using ThreadStorage = uint32_t; // Per thread storage allocated on the stack but shared between invocations of the transformation on the same worker thread

    static constexpr char profileZone[] = "Parallel transform";

    static void clearAdd(TransformContext& context, size_t attrIdx, const omni::fabric::SpanC& data) {}

    struct Attributes
    {
        typename QueryType::Read read;
        typename QueryType::Write write;
        typename QueryType::Deps deps;
        typename QueryType::Add add;
        typename QueryType::AddDeferred addDeferred;
        typename QueryType::Create create;
        typename QueryType::Exclude exclude;

        void build(QueryAttributeLists& lists)
        {
            read.build(lists.all, lists.any);
            write.build(lists.all, lists.any);
            deps.build(lists.all, lists.any);
            lists.addAttributes = lists.all;
            omni::fabric::set<omni::fabric::AttrNameAndType> dummy;
            add.build(lists.addAttributes, dummy);
            CARB_ASSERT(dummy.size() == 0); // cannot have optional add attributes
            exclude.build(lists.none, dummy);
            CARB_ASSERT(dummy.size() == 0); // cannot have optional exclude attributes
            create.build(lists.newAttributes, dummy);
            CARB_ASSERT(dummy.size() == 0); // cannot have optional create attributes
            addDeferred.build(dummy, dummy);
        }
    };

    struct Row
    {
        using QueryT = QueryType;
        using InnerRowT = typename QueryT::TransformType::InnerQueryT::Row;

        const Attributes& attributes;
        std::vector<typename QueryType::AddDeferred::DataAdd>& addDeferred;
        InnerRowT* innerRowPtr;
        typename QueryType::ThreadStorage* threadStorage;        
        omni::fabric::ConstPathCSpan pathArray;

        typename QueryType::Read::DataRead read;
        typename QueryType::Write::DataReadWrite write;
        typename QueryType::Add::DataReadWrite add;
        typename QueryType::Create::DataReadWrite create;

        BucketId createBucket(DBAccess& db, const omni::fabric::set<omni::fabric::AttrNameAndType>& attributes)
        {
            if (attributes.size())
            {
                CARB_CHECK(false);
                return 0;
            }
            return 0;
        }

        bool bind(BucketId bucket_, DBAccess& db, const omni::fabric::PrimBucketListId& bucketListId, BucketId newBucket_)
        {
            bucket = bucket_;
            newBucket = newBucket_;
            db.irw.getPathArray(&pathArray, db.id, bucketListId, bucket.id);
            if (!read.bindBucketAttributes(bucket_, attributes.read, db, bucketListId))
            {
                return false;
            }
            if (!write.bindBucketAttributes(bucket_, attributes.write, db, bucketListId))
            {
                return false;
            }
            if (!add.bindBucketAttributes(bucket_, attributes.add, db, bucketListId))
            {
                return false;
            }
            elementCount = pathArray.elementCount;
            return true;
        }

        void setRow(size_t idx, bool isNew_ = false, size_t gatherIdx_ = 0, size_t gatherCount_ = 1)
        {
            row = idx;
            read.setRow(idx);
            write.setRow(idx);
            add.setRow(idx);

            gatherIdx = gatherIdx_;
            gatherCount = gatherCount_;
            isNew = isNew_;
        }

        template<size_t I = 0, typename T>
        void writeNew(DBAccess& db, const T& value)
        {
            create.template get<I>() = value;
        }

        template<size_t I = 0, typename T, typename... ArgTypes>
        void writeNew(DBAccess& db, const T& value, const ArgTypes&... args)
        {
            create.template get<I>() = value;
            writeNew<I + 1>(db, args...);
        }

        template<typename... ArgTypes>
        void createRow(DBAccess& db, const omni::fabric::PathC& path, const ArgTypes&... args)
        {
            size_t newIndex = db.rw.createPrim(omni::fabric::Path(path));
            create.setRow(newIndex);
            create.bindBucketAttributes(newBucket, attributes.create, db); // need to rebind after allocation
            writeNew<0>(db, args...);
        }

        InnerRowT& innerRow() { return *innerRowPtr; }

        BucketId bucket = 0;
        BucketId newBucket = 0;
        size_t row = 0;
        size_t elementCount = 0;
        size_t gatherIdx = 0;
        size_t gatherCount = 1;
        bool isNew = false;
    };
};

/*
namespace details
{
    struct JoinSortValue
    {
        size_t pathBucketId;
        size_t pathElementIdx;
        size_t primBucketId;
        size_t elemIdx;
    };

    struct JoinEntry
    {
        size_t start;
        size_t primCount;
    };

    size_t countBucketSize(const std::vector<JoinSortValue>& values, size_t bucketId, size_t idx)
    {
        size_t count = 1;
        while ((idx + count < values.size()) && (values[idx + count].pathBucketId == bucketId))
        {
            count++;
        }
        return count;
    }

    size_t countPrims(const std::vector<JoinSortValue>& values, size_t pathElementIdx, size_t idx, size_t maxIdx)
    {
        size_t count = 1;
        while ((idx + count < maxIdx) && (values[idx + count].pathElementIdx == pathElementIdx))
        {
            count++;
        }
        return count;
    }

    bool checkBucket(omni::fabric::PathToAttributesMap& map, size_t bucketId
        , const omni::fabric::set<omni::fabric::AttrNameAndType>& all
        , const omni::fabric::set<omni::fabric::AttrNameAndType>& any
        , const omni::fabric::set<omni::fabric::AttrNameAndType>& none)
    {     
        return map.filterBucket(bucketId, all, any, none);
    }
}
*/
struct QueryInstanceBase
{
};

struct TransformBase
{
};

// the actual instance of a query
template<typename QueryType>
struct QueryInstance : QueryInstanceBase
{
    using Row = typename QueryType::Row;

    template<typename... ArgTypes>
    struct Transform : TransformBase
    {
        using FunctorType = std::function<void(TransformContext&, typename QueryType::Row&, ArgTypes...)>;
        FunctorType functor;
        omni::fabric::PrimBucketListId changePrimBucketListId;

        Transform(omni::fabric::PrimBucketListId changePrimBucketListId_)
            : changePrimBucketListId(changePrimBucketListId_)
        {

        }

        template<typename FunctorT>
        Transform(FunctorT functor_)
        {
            functor = functor_;
        }

        void addAttributes(const QueryInstance& instance, TransformContext& context) const
        {
            // loop over buckets
            for (uint32_t i = 0; i < instance.m_Attributes.add.nameAndTypes.size(); i++)
            {
                CARB_CHECK(false);
                /*
                // currently we can't get the new bucketID out when adding an attribute
                // so we need to get the buckets again for each change
                // TODO : replace this by bulk editing which returns the new bucketid
                context.db.primBucketList = context.db.rw.findPrims(instance.m_Lists.all, instance.m_Lists.any, instance.m_Lists.none);

                size_t bucketCount = context.db.primBucketList.bucketCount();
                for (size_t bucketIdx = 0; bucketIdx < bucketCount; bucketIdx++)
                {                    
                    bool isNew = context.attributeMap.getArrayRdC(bucketId, instance.m_Attributes.add.nameAndTypes[i].name, Suffix::none).ptr == nullptr;
                    size_t oldElemCount = context.attributeMap.getElementCount(bucketId);
                    omni::fabric::SpanC newAttribute = context.attributeMap.getOrCreateArrayWrC(bucketId, instance.m_Attributes.add.nameAndTypes[i].name, *(omni::fabric::TypeC*)&instance.m_Attributes.add.nameAndTypes[i].type, Suffix::none); // add the new attribute without suffix
                    if (isNew)
                    {
                        CARB_ASSERT(newAttribute.elementCount >= oldElemCount);
                        // If the bucket got merged with another bucket we only clear the last oldElemCount elements as that should be the appended elements
                        size_t newElementStart = newAttribute.elementCount - oldElemCount;
                        newAttribute.ptr += newAttribute.elementSize * newElementStart;
                        newAttribute.elementCount -= newElementStart;
                        QueryType::clearAdd(context, i, newAttribute);
                    }
                }
                */
            }
        }

        template<typename DataAddT>
        void processDeferredEvents(const QueryInstance& instance, TransformContext& context, const std::vector<DataAddT>& addDeferred) const
        {
            for (auto& addEvent : addDeferred)
            {
                CARB_CHECK(false);
                /*
                const omni::fabric::AttrNameAndType& nameAndType = instance.m_Attributes.addDeferred.nameAndTypes[addEvent.attribIndex];
                if (nameAndType.type.arrayDepth == 0)
                {
                    context.attributeMap.addAttributeC(addEvent.path, nameAndType.name, nameAndType.suffix, omni::fabric::TypeC(nameAndType.type), &addEvent.attribute);
                }
                else
                {
                    size_t* data = carb::cpp17::get<size_t*>(addEvent.attribute);
                    if (data)
                    {
                        context.attributeMap.addArrayAttributeC(addEvent.path, nameAndType.name, nameAndType.suffix, omni::fabric::TypeC(nameAndType.type), data + 1, *data);
                        delete data;
                    }
                }
                */
            }
        }

        static bool accept(TransformContext& context,
            omni::fabric::PrimBucketListId bucketListId,
            size_t bucketIdx,
            const omni::fabric::set<omni::fabric::AttrNameAndType>& all,
            const omni::fabric::set<omni::fabric::AttrNameAndType>& any,
            const omni::fabric::set<omni::fabric::AttrNameAndType>& none)
        {
            return context.db.irw.acceptBucket(context.db.id, bucketListId, bucketIdx, all, any, none);
        }

        //------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        // standard transform
        //------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        template<bool useChangeTracking, typename UseTransformType = typename QueryType::TransformType, typename Functor>
        typename std::enable_if<UseTransformType::queryType == 0, void>::type
        exec(QueryInstance& instance, TransformContext& context, Functor functor_, ArgTypes... args) const
        {
            if (!instance.m_Lists.hasRegisteredTypes)
            {
                instance.m_Attributes.create.bind(context.db);
                instance.m_Attributes.add.bind(context.db);
                instance.m_Attributes.addDeferred.bind(context.db);
                instance.m_Lists.hasRegisteredTypes = true;
            }

            addAttributes(instance, context);

            typename QueryNone::Row innerRow;
            std::vector<typename QueryType::AddDeferred::DataAdd> addDeferred;
            typename QueryType::Row row{ instance.m_Attributes, addDeferred, &innerRow };
            BucketId newBucket = row.createBucket(context.db, instance.m_Lists.newAttributes);

            if ((instance.m_Lists.all.size() + instance.m_Lists.any.size()) == 0)
            {
                row.bind(-1, context.db, omni::fabric::PrimBucketListId{}, newBucket);

                // nothing in the filter, just call once
                functor_(context, row, args...);
            }
            else
            {
                omni::fabric::PrimBucketListId bucketsToTravers{};
                if (!useChangeTracking)
                {
                    bucketsToTravers = context.db.irw.findPrims(context.db.id, instance.m_Lists.all, instance.m_Lists.any, instance.m_Lists.none);
                }
                else
                {
                    bucketsToTravers = changePrimBucketListId;
                }


                typename QueryType::ThreadStorage storage;
                row.threadStorage = &storage;

                size_t bucketCount = context.db.iPrimBucketList->getBucketCount(bucketsToTravers);
                for (size_t bucketIdx = 0; bucketIdx < bucketCount; bucketIdx++)
                {
                    // when we use change tracking we need to verify that the bucket contains the right attributes as this doesn't happen automatically like for findprims
                    if (useChangeTracking && !accept(context, bucketsToTravers, bucketIdx, instance.m_Lists.all, instance.m_Lists.any, instance.m_Lists.none))
                    {
                        continue;
                    }

                    // bind the rows
                    if (!row.bind(bucketIdx, context.db, bucketsToTravers, newBucket))
                    {
                        continue;
                    }

                    bool allChanged = false;
                    bool isNew = false;
                    if (!useChangeTracking)
                    {
                        allChanged = true;
                        isNew = true;
                    }
                    else
                    {
                        omni::fabric::BucketChangesC changes = context.db.iPrimBucketList->getChanges(changePrimBucketListId, bucketIdx);
                        // TODO : decide which approach to iteration to take based on the number of changes and size of path array
                        instance.m_changedIndices.resize(changes.pathArray.elementCount, false);
                        instance.m_changedIndices.setAll(false);

                        omni::fabric::AddedPrimIndicesC addedPrims = context.db.iPrimBucketList->getAddedPrims(changePrimBucketListId, bucketIdx);
                        for (uint64_t elemIdx = 0; elemIdx < addedPrims.addedIndices.elementCount; elemIdx++)
                        {
                            uint64_t remappedIndex = addedPrims.addedIndices.ptr[elemIdx];
                            row.setRow(remappedIndex, true);
                            functor_(context, row, args...);
                            instance.m_changedIndices.set(remappedIndex, true);
                        }

                        for (uint64_t changeIndex = 0; changeIndex < changes.changedIndices.elementCount; changeIndex++)
                        {
                            allChanged |= changes.changedIndices.ptr[changeIndex].allIndicesChanged;
                        }

                        if (!allChanged && changes.changedIndices.elementCount)
                        {
                            for (uint64_t changeIndex = 0; changeIndex < changes.changedIndices.elementCount; changeIndex++)
                            {
                                omni::fabric::ConstChangedIndicesC index = changes.changedIndices.ptr[changeIndex];
                                for (uint64_t elemIdx = 0; elemIdx < index.changedIndices.elementCount; elemIdx++)
                                {
                                    uint64_t remappedIndex = index.changedIndices.ptr[elemIdx];
                                    if (!instance.m_changedIndices.get(remappedIndex))
                                    {
                                        row.setRow(remappedIndex);
                                        functor_(context, row, args...);
                                        instance.m_changedIndices.set(remappedIndex, true);
                                    }
                                }
                            }
                        }
                    }

                    if (allChanged)
                    {
                        for (size_t i = 0; i < row.elementCount; i++)
                        {
                            row.setRow(i, isNew);
                            functor_(context, row, args...);
                        }
                    }
                }

                /*
                omni::fabric::set<omni::fabric::BucketId> buckets = context.attributeMap.findBuckets(instance.m_Lists.all, instance.m_Lists.any, instance.m_Lists.none);
                if (!QueryType::Threading::value)
                {
                    typename QueryType::ThreadStorage storage;
                    row.threadStorage = &storage;

                    for (omni::fabric::BucketId bucketId : buckets)
                    {
                        // bind the rows
                        row.bind(bucketId, context.attributeMap, newBucket);

                        for (size_t i = 0; i < row.elementCount; i++)
                        {
                            row.setRow(i);
                            functor_(context, row, args...);
                        }
                    }
                }
                else
                {
                    carb::tasking::ITasking* tasking = carb::getFramework()->acquireInterface<carb::tasking::ITasking>();
                    for (omni::fabric::BucketId bucketId : buckets)
                    {
                        // bind the rows
                        row.bind(bucketId, context.attributeMap, newBucket);

                        tasking->applyRangeBatch(row.elementCount, QueryType::Threading::batchSize, [row, this, &context, &functor_](size_t start, size_t end)
                            {
                                CARB_PROFILE_ZONE(1, QueryType::profileZone);
                                typename QueryType::Row threadRow = row;
                                typename QueryType::ThreadStorage storage;
                                threadRow.threadStorage = &storage;

                                for (size_t idx = start; idx < end; idx++)
                                {
                                    threadRow.setRow(idx);
                                    functor_(context, threadRow, args...);
                                }
                            });
                    }
                }
                */
            }

            processDeferredEvents(instance, context, addDeferred);
        }

        /*
        //------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        // gather transform
        //------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        template<typename UseTransformType = typename QueryType::TransformType, typename Functor>
        typename std::enable_if<UseTransformType::queryType == 1, void>::type
            exec(const QueryInstance& instance, TransformContext& context, Functor functor_, ArgTypes... args) const
        {
            if (!instance.m_Lists.hasRegisteredTypes)
            {
                instance.m_Attributes.create.bind(context.attributeMap);
                instance.m_Attributes.add.bind(context.attributeMap);
                instance.m_Attributes.addDeferred.bind(context.attributeMap);
                instance.m_InnerAttributes.addDeferred.bind(context.attributeMap);
                instance.m_Lists.hasRegisteredTypes = true;
            }

            using InnerQueryT = typename QueryType::TransformType::InnerQueryT;
            static_assert(QueryType::Create::length == 0, "Gather transform cannot create new prims");
            static_assert(InnerQueryT::Create::length == 0, "Gather transform cannot create prims on inner query");
            static_assert(InnerQueryT::Add::length == 0, "Gather transform cannot add attributes on inner query (use add deferred)");

            addAttributes(instance, context);

            std::vector<typename QueryType::TransformType::InnerQueryT::AddDeferred::DataAdd> addDeferredInner;
            typename QueryType::TransformType::InnerQueryT::Row innerRow{ instance.m_InnerAttributes, addDeferredInner, nullptr };
            std::vector<typename QueryType::AddDeferred::DataAdd> addDeferred;
            typename QueryType::Row row{ instance.m_Attributes, addDeferred, &innerRow };
            BucketId newBucket = row.createBucket(context.attributeMap, instance.m_Lists.newAttributes);

            // first find all the outer buckets
            omni::fabric::set<omni::fabric::BucketId> outerBuckets = context.attributeMap.findBuckets(instance.m_Lists.all, instance.m_Lists.any, instance.m_Lists.none);

            std::vector<details::JoinSortValue> sort;

            // read the join value and obtain the bucketid/elem for it
            for (omni::fabric::BucketId bucketId : outerBuckets)
            {
                // bind the rows
                row.bind(bucketId, context.attributeMap, -1);

                for (size_t i = 0; i < row.elementCount; i++)
                {
                    // join value must be a path for now
                    static constexpr const size_t I = typename QueryType::Read::template getIdx<typename QueryType::TransformType::AttribT>();
                    Path joinValue = getPath(row.read.template getSpan<I>()[i]);

                    // get the bucketid for the path
                    size_t pathBucketId, pathElementIdx;
                    std::tie(pathBucketId, pathElementIdx) = context.attributeMap.getBucketAndArrayIndex(joinValue);
                    sort.push_back({pathBucketId, pathElementIdx, bucketId, i });
                }
            }

            std::sort(sort.begin(), sort.end(), [](const details::JoinSortValue& a, const details::JoinSortValue& b)
                {
                    if (a.pathBucketId != b.pathBucketId)
                        return a.pathBucketId < b.pathBucketId;
                    else if (a.pathElementIdx != b.pathElementIdx)
                        return a.pathElementIdx < b.pathElementIdx;
                    else
                        return a.primBucketId < b.primBucketId;
                });

            std::vector<details::JoinEntry> entries;
            entries.reserve(sort.size());

            // build a list of entries, counting the number of prims for each path
            // parallel execution then spreads over the path, but makes sure all prims for one path are executed on the same thread
            for (size_t i = 0; i < sort.size();)
            {
                size_t bucketId = sort[i].pathBucketId;
                size_t currentBucketSize = details::countBucketSize(sort, bucketId, i);

                // test if the bucket fits the outer filter
                if (!details::checkBucket(context.attributeMap, bucketId, instance.m_InnerLists.all, instance.m_InnerLists.any, instance.m_InnerLists.none))
                {
                    i += currentBucketSize;
                    continue;
                }

                // now iterate all within the same outer bucket
                size_t currentBucketStart = i;
                for (; i < currentBucketStart + currentBucketSize;)
                {
                    size_t pathElementIdx = sort[i].pathElementIdx;

                    // count the number of prims in the outer bucket
                    size_t currentPrims = details::countPrims(sort, pathElementIdx, i, currentBucketStart + currentBucketSize);
                    entries.push_back({i, currentPrims});
                    i += currentPrims;
                }
            }

            auto transform = [&](typename QueryType::Row row, typename QueryType::TransformType::InnerQueryT::Row& innerRow, size_t start, size_t end)
            {
                // single threaded, just loop over the entries
                typename QueryType::ThreadStorage storage;
                row.threadStorage = &storage;

                Path currentPath{};
                size_t currentPathBucketId = -1;
                size_t currentPrimBucketId = -1;

                // now iterate the entries
                for (size_t i = start; i < end; i++)
                {
                    const details::JoinEntry& entry = entries[i];
                    size_t bucketId = sort[entry.start].pathBucketId;
                    if (bucketId != currentPathBucketId)
                    {
                        innerRow.bind(bucketId, context.attributeMap, -1);
                        currentPathBucketId = bucketId;
                    }

                    innerRow.setRow(sort[entry.start].pathElementIdx);

                    for (size_t n = 0; n < entry.primCount; n++)
                    {
                        size_t primBucketId = sort[entry.start + n].primBucketId;
                        // now iterate the inner buckets within the gather args (we should sort by those first if the relationship is 1:1)
                        if (primBucketId != currentPrimBucketId)
                        {
                            row.bind(primBucketId, context.attributeMap, newBucket);
                            currentPrimBucketId = primBucketId;
                        }

                        // set row index together with gather index/count
                        row.setRow(sort[entry.start + n].elemIdx, n, entry.primCount);

                        functor_(context, row, args...);
                    }
                }
            };

            if (!QueryType::Threading::value)
            {
                transform(row, innerRow, 0, entries.size());
            }
            else
            {
                carb::tasking::ITasking* tasking = carb::getFramework()->acquireInterface<carb::tasking::ITasking>();
                carb::tasking::applyRangeBatch(*tasking, entries.size(), QueryType::Threading::batchSize, QueryType::profileZone, [&row, &innerRow, &transform](size_t start, size_t end)
                    {
                        typename QueryType::TransformType::InnerQueryT::Row threadInnerRow = innerRow;
                        typename QueryType::Row threadRow = row;
                        threadRow.innerRowPtr = &threadInnerRow;
                        transform(threadRow, threadInnerRow, start, end);
                    });
            }

            processDeferredEvents(instance, context, addDeferred);
            processDeferredEvents(instance, context, addDeferredInner);
        }
        */
    };

    typename QueryType::Attributes m_Attributes;
    typename QueryType::TransformType::InnerQueryT::Attributes m_InnerAttributes;
    QueryAttributeLists m_Lists;
    QueryAttributeLists m_InnerLists;
    omni::BitVector m_changedIndices;

    QueryInstance()
    {
        m_Attributes.build(m_Lists);
        m_InnerAttributes.build(m_InnerLists);
    }

    template<typename FunctorT, typename... ArgTypes>
    void exec(TransformContext& context, FunctorT functor_, ArgTypes&&... args)
    {
        Transform<ArgTypes...> transform{ omni::fabric::kInvalidPrimBucketListId };
        transform.template exec<false>(*this, context, functor_, args...);
    }
};

template<typename QueryType>
struct TrackedQueryInstance : QueryInstance<QueryType>
{
    using BaseType = QueryInstance<QueryType>;

    omni::fabric::ListenerId m_listenerId{};
    omni::fabric::StageReaderWriterId m_listenerStageId{};

    TrackedQueryInstance()
    {
        omni::fabric::IChangeTrackerConfig* iTrackingConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
        m_listenerId = iTrackingConfig->createListener();
    }

    ~TrackedQueryInstance()
    {
        detachListener();
    }

    void detachListener()
    {
        if (m_listenerStageId.id)
        {
            omni::fabric::IChangeTrackerConfig* iTrackingConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
            iTrackingConfig->detachListener(m_listenerStageId, m_listenerId);
        }
        m_listenerStageId.id = 0;
    }

    template<typename FunctorT, typename... ArgTypes>
    void execWithTracking(TransformContext& context, FunctorT functor_, ArgTypes&&... args)
    {
        if (m_listenerStageId != context.db.id)
        {
            detachListener();
            omni::fabric::IChangeTrackerConfig* iTrackingConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
            for (uint64_t i = 0; i < this->m_Lists.all.size(); i++)
            {
                iTrackingConfig->attributeEnable(context.db.id, this->m_Lists.all.v[i].name.asTokenC(), m_listenerId);
            }
            for (uint64_t i = 0; i < this->m_Lists.any.size(); i++)
            {
                iTrackingConfig->attributeEnable(context.db.id, this->m_Lists.any.v[i].name.asTokenC(), m_listenerId);
            }
            iTrackingConfig->enablePrimCreateTracking(context.db.id, m_listenerId);
            m_listenerStageId = context.db.id;

            // no change tracking yet, run the full thing
            typename QueryInstance<QueryType>::template Transform<ArgTypes...> transform{ omni::fabric::kInvalidPrimBucketListId };
            transform.template exec<false>(*this, context, functor_, args...);
        }
        else
        {
            omni::fabric::PrimBucketListId changes = context.db.irw.getChanges(context.db.id, m_listenerId);
            context.db.irw.popChanges(context.db.id, m_listenerId);

            typename QueryInstance<QueryType>::template Transform<ArgTypes...> transform{ changes };
            transform.template exec<true>(*this, context, functor_, args...);
        }
    }
};

#define FC_DEFINE_QUERY(queryName) \
    queryName : query::Query<queryName>

#define FC_DEFINE_CLEAR_ADD(attrName, value) \
    static void clearAdd(query::TransformContext& context, size_t attrIdx, const omni::fabric::SpanC& data) \
    { \
        if(Add::getIdx<attrName>() == attrIdx) \
        { \
            for(size_t i = 0; i < data.elementCount; i++) \
            { \
                *(typename attrName::ValueT*)(data.ptr + i * data.elementSize) = value; \
            } \
        } \
    } \

} // namespace query

TYPE_PARAMTYPETRAIT(bool, eBool, 1);
TYPE_PARAMTYPETRAIT(uint32_t, eUInt, 1);
TYPE_PARAMTYPETRAIT(int32_t, eInt, 1);
TYPE_PARAMTYPETRAIT(uint64_t, eUInt64, 1);
TYPE_PARAMTYPETRAIT(int64_t, eInt64, 1);
TYPE_PARAMTYPETRAIT(float, eFloat, 1);
TYPE_PARAMTYPETRAIT(double, eDouble, 1);
TYPE_PARAMTYPETRAIT(usdrt::GfVec3f, eFloat, 3);
TYPE_PARAMTYPETRAIT(usdrt::GfVec3d, eDouble, 3);
TYPE_PARAMTYPETRAIT(usdrt::GfMatrix3f, eFloat, 9);
TYPE_PARAMTYPETRAIT(usdrt::GfMatrix3d, eDouble, 9);
TYPE_PARAMTYPETRAIT_ROLE(usdrt::GfMatrix4f, eFloat, 16, eMatrix);
TYPE_PARAMTYPETRAIT_ROLE(usdrt::GfMatrix4d, eDouble, 16, eMatrix);
TYPE_PARAMTYPETRAIT(omni::fabric::Token, eToken, 1);
TYPE_PARAMTYPETRAIT(Tag, eTag, 1);
TYPE_PARAMTYPETRAIT_ROLE(SchemaTag, eTag, 1, eAppliedSchema);
TYPE_PARAMTYPETRAIT_ROLE(PrimTypeTag, eTag, 1, ePrimTypeName);
TYPE_PARAMTYPETRAIT(Path, ePath, 1);
TYPE_PARAMTYPETRAIT(ElementCount, eUInt64, 1);
TYPE_PARAMTYPETRAIT(Connection, eConnection, 1);

