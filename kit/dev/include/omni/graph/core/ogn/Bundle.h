// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// =================================================================================================================
// This file contains interface classes which wrap attribute bundles in the OGN database for ease of use
//
//    BundleContents  Accessor to get at the attributes inside the bundle
//    BundleAttribute Access to the bundle attribute, with appropriate read/write abilities depending on port type
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

#ifdef THIS_IS_INCLUDED_IN_THE_DOCUMENTATION
// The information bracketed here with begin/end describes the interface that is recommended for use with bundled
// attributes. The documentation uses these markers to perform a literal include of this code into the docs so that
// it can be the single source of truth. Note that the interface described here is not the complete set of C++
// functions available, merely the ones that make sense for the user to access when dealing with bundles.
// begin-bundle-interface-description
// A bundle can be described as an opaque collection of attributes that travel together through the graph, whose
// contents and types can be introspected in order to determine how to deal with them. This section describes how
// the typical node will interface with the bundle content access. Use of the attributes within the bundles is the
// same as for the extended type attributes, described with their access methods.
//
// An important note regarding GPU bundles is that the bundle itself always lives on the CPU, specifying a memory
// space of "GPU/CUDA" for the bundle actually means that the default location of the attributes it contains will
// be on the GPU.
//
// The main bundle is extracted the same as any other attribute, by referencing its generated database location.
// For this example the bundle will be called "color" and it will have members that could either be the set
// ("r", "g", "b", "a") or the set ("c", "m", "y", "k") with the obvious implications of implied color space.
//
// The bundle itself has a path to which it refers; normally unnecessary to use but helpful for debugging
std::cout << "The color bundle came from " << db.inputs.color.path() << std::endl;

// As with other attribute types you can get an accessor to the bundle:
const auto& colorBundle = db.inputs.color();

// The accessor can determine if it points to valid data
const bool validColor = colorBundle.isValid();

// It can be queried for the number of attributes it holds
auto bundleAttributeCount = colorBundle.size();

// It can have its contents iterated over
for (const auto& bundledAttribute : colorBundle)
{ /* ... */ }

// It can be queried for an attribute in it with a specific name
auto bundledAttribute = colorBundle.attributeByName(db.tokens.red);

// And on the rare occasion when it is necessary, it can access the low level IBundle interface or ABI handle of the bundle's data
// to make direct ABI calls on it. (This is discouraged as it may bypass some important state updates.)
const auto& bundleHandle = colorBundle.abi_bundleHandle();

// *** The rest of these methods are for output bundles only, as they change the makeup of the bundle

// It can be assigned to an output bundle, which merely transfers ownership of the bundle.
// As in all C++ it's important to make the distinction between assignment and merely obtaining a reference
auto& computedColorBundle = db.outputs.computedColorBundle();  // No copy, just assignment of a reference object
computedColorBundle = colorBundle; // Copy the input bundle to the output bundle

// It can have its contents (i.e. attribute membership) cleared
computedColorBundle.clear();

// It can insert a new bundle, without replacing its current contents (with the caveat that all attribute names
// in the current and inserted bundle must be unique)
computedColorBundle.insertBundle(colorBundle);

// It can have a single attribute from another bundle inserted into its current list, like if you don't want
// the transparency value in your output color
computedColorBundle.clear();
computedColorBundle.insertAttribute(colorBundle.attributeByName(db.tokens.red));
computedColorBundle.insertAttribute(colorBundle.attributeByName(db.tokens.green));
computedColorBundle.insertAttribute(colorBundle.attributeByName(db.tokens.blue));

// It can add a brand new attribute with a specific type and name
namespace og = omni::graph::core;
og::Type floatType(og::BaseDataType::eFLOAT);
computedColorBundle.addAttribute(db.tokens.opacity, floatType);
// If you are adding an array attribute you can set its initial element count with the same call
og::Type boolArrayType(og::BaseDataType::eBOOLEAN, 1, 1);
computedColorBundle.addAttribute(db.tokens.bits, boolArrayType, 32);

// If you want to remove an attribute from a bundle you only need its name
computedColorBundle.removeAttribute(db.tokens.bits);
// end-bundle-interface-description
#endif

#include <omni/graph/core/ogn/RuntimeAttribute.h>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/Types.h>
#include <omni/graph/core/IBundle.h>
#include <omni/graph/core/ComputeGraph.h>
#include <omni/graph/core/IBundleChanges.h>
#include <carb/InterfaceUtils.h>

namespace omni {
namespace graph {
namespace core {
namespace ogn {

// ======================================================================
/**
 * Class responsible for managing the interaction with bundles of attributes.
 * It wraps the bundle in an interface with a more natural interaction than the raw ABI calls.
 *
 * <AttributeType> How the attribute is interpreted - input, output, or state value
 * <MemoryType> where the memory for the attributes in this bundle will live (CPU, GPU, or decided at runtime)
 * <GpuPtrType> where the pointer to array attributes in this bundle will live (CPU or GPU, for GPU data only)
 */
template <eAttributeType AttributeType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
class BundleContents
{
    //! Aliases used during overload resolution to differentiate between read-only and read-write.
    using roTag_t = std::true_type;
    using rwTag_t = std::false_type;

    //! The writability of a bundle will determine what kinds of operations can be performed on it
    static constexpr bool readOnly = (AttributeType == kOgnInput);
    using readOnly_t = std::conditional_t<AttributeType == kOgnInput, roTag_t, rwTag_t>;

    //! By defining the bundle type based on attribute type duplication of code in this class can be avoided
    using bundleHandle_t = std::conditional_t<readOnly, ConstBundleHandle, BundleHandle>;

    //! By defining the interface type based on attribute type duplication of code in this class can be avoided
    using bundleInterface_t = std::conditional_t<readOnly, IConstBundle2, IBundle2>;

    //! The handle types are not simply "X" and "const X" variations so the type has to be explicitly defined
    //! for writable (output/state) and non-writable (input) attribute types.
    using dataHandle_t = std::conditional_t<readOnly, ConstAttributeDataHandle, AttributeDataHandle>;

    //! Short form to reduce line length
    using runtime_t = RuntimeAttribute<AttributeType, MemoryType, GpuPtrType>;

    using bundleInterfacePtr = omni::core::ObjectPtr<bundleInterface_t>;
    bundleInterfacePtr m_bundlePtr;

    runtime_t m_invalid; //!< Special object representing invalid data

    mutable gsl::span<runtime_t> m_iterableArray; //!< Iterator wrapper

    // ================================================================================
    // Functions supporting both read-only and writable versions, necessitated by the different function calls
    // and argument types used for both (i.e. you can't just do a const_cast for these). Ideally they would be
    // broken out into utility functions and shared everywhere.
    //
    // They are selected by calling them using a first argument of "readOnly_t()", which will use overloading to
    // select the proper version. (roTag_t for read-only versions, rwTag_t for writable versions)

    /**
     * Extract the interface for an attribute in the bundle with the given name.
     *
     * @param name Token representing the name of the attribute in the bundle
     * @return Bundle member from which attribute information can be extracted (invalid if name was not found)
     */
    dataHandle_t extractNamedAttribute(rwTag_t, NameToken const& name) const
    {
        return m_bundlePtr->getAttributeByName(name);
    }
    dataHandle_t extractNamedAttribute(roTag_t, NameToken const& name) const
    {
        return m_bundlePtr->getConstAttributeByName(name);
    }

    /**
     * Get the list of attribute handles present on the bundle.
     *
     * @param Type representing writable (rwTag_t) or read-only (roTag_t) data
     * @param allHandles Pointer to array of handles that were extracted
     * @param count The size of the provided pointer array (in pointer count)
     */
    void extractHandles(rwTag_t, dataHandle_t* allHandles, size_t count) const
    {
        m_bundlePtr->getAttributes(allHandles, count);
    }
    void extractHandles(roTag_t, dataHandle_t* allHandles, size_t count) const
    {
        m_bundlePtr->getConstAttributes(allHandles, count);
    }

    /**
     * Construct bundle interface based on provided context and bundle handle.
     *
     * @param context Evaluation context.
     * @param handle Bundle handle.
     */
    bundleInterfacePtr getInterface(rwTag_t, GraphContextObj const& context, bundleHandle_t handle) const
    {
        return getBundleFactoryInterface()->getBundle(context, handle);
    }
    bundleInterfacePtr getInterface(roTag_t, GraphContextObj const& context, bundleHandle_t handle) const
    {
        return getBundleFactoryInterface()->getConstBundle(context, handle);
    }

    /**
     * Construct bundle interface based on provided context and bundle path.
     *
     * @param context Evaluation context.
     * @param path Bundle path.
     */
    bundleInterfacePtr getInterface(rwTag_t, GraphContextObj const& context, omni::fabric::PathC path) const
    {
        auto factory = omni::core::cast<IBundleFactory2>(getBundleFactoryInterface());
        return factory ? factory->getBundleFromPath(context, path) : bundleInterfacePtr{};
    }
    bundleInterfacePtr getInterface(roTag_t, GraphContextObj const& context, omni::fabric::PathC path) const
    {
        auto factory = omni::core::cast<IBundleFactory2>(getBundleFactoryInterface());
        return factory ? factory->getConstBundleFromPath(context, path) : bundleInterfacePtr{};
    }

    /**
     * Get read-only or read-write handle depending on writability permissions of this interface.
     */
    bundleHandle_t getBundleHandle(rwTag_t) const
    {
        return m_bundlePtr->getHandle();
    }
    bundleHandle_t getBundleHandle(roTag_t) const
    {
        return m_bundlePtr->getConstHandle();
    }

    void clearAttributeCache() const
    {
        delete[] m_iterableArray.data();
        m_iterableArray = gsl::span<runtime_t>{};
    }

    void updateAttributeCache() const
    {
        // Only reallocate the bundle members if the size changed. If it didn't then the
        // in-place constructor will put the correct data in place.
        size_t newSize = attributeCount();
        if (!m_iterableArray.empty() && (newSize != m_iterableArray.size()))
        {
            clearAttributeCache();
        }
        if (m_iterableArray.empty() && (newSize > 0))
        {
            m_iterableArray = gsl::span<runtime_t>{ new runtime_t[newSize], newSize };
        }
        if (!m_iterableArray.empty())
        {
            auto context = m_bundlePtr->getContext();
            dataHandle_t* allHandles = reinterpret_cast<dataHandle_t*>(alloca(newSize * sizeof(dataHandle_t)));
            extractHandles(readOnly_t(), allHandles, newSize);
            for (size_t i = 0; i < newSize; ++i)
            {
                new (&m_iterableArray[i]) runtime_t(context, allHandles[i]);
            }
        }
    }

public:
    // Pass through the span iterator so that this class can iterate over it transparently
    using iterator = typename gsl::span<runtime_t>::iterator;
    using reverse_iterator = typename gsl::span<runtime_t>::reverse_iterator;

    /**
     * Default constructor
     */
    BundleContents() = default;

    /**
     * Constructor with direct initialization from context and bundle handle.
     */
    BundleContents(GraphContextObj const& context, bundleHandle_t handle) : BundleContents()
    {
        reset(context, handle);
    }

    /**
     * Constructor with direct initialization from context and bundle path.
     */
    BundleContents(GraphContextObj const& context, omni::fabric::Path path)
        : BundleContents()
    {
        reset(getInterface(readOnly_t{}, context, path));
    }

    /**
     * Data managed by the bundle cannot be duplicated
     */
    BundleContents(const BundleContents&) = delete;
    BundleContents& operator=(const BundleContents&) = delete;

    /**
     * Clean up any cached data
     */
    ~BundleContents()
    {
        clearAttributeCache();
    }

    /**
     * @deprecated Calling abi_primHandle() is deprecated. Use abi_bundleHandle() instead!
     */
    [[deprecated("Calling abi_primHandle() is deprecated. Use abi_bundleHandle() instead!")]]
    bundleHandle_t const abi_primHandle() const
    {
        return abi_bundleHandle();
    }

    /**
     * @deprecated Calling abi_primHandle() is deprecated. Use abi_bundleHandle() instead!
     */
    [[deprecated("Calling abi_primHandle() is deprecated. Use abi_bundleHandle() instead!")]]
    bundleHandle_t abi_primHandle()
    {
        return abi_bundleHandle();
    }

    /**
     * Return bundle factory interface.
     */
    static IBundleFactory* getBundleFactoryInterface()
    {
        static omni::core::ObjectPtr<IBundleFactory> factory =
            carb::getCachedInterface<ComputeGraph>()->getBundleFactoryInterfacePtr();
        return factory.get();
    }

    /**
     * @return the raw bundle handle for use via the ABI directly
     */
    bundleHandle_t const abi_bundleHandle() const
    {
        if (isValid())
            return getBundleHandle(readOnly_t{});
        return {};
    }

    /**
     * @return the raw bundle handle for use via the ABI directly
     */
    bundleHandle_t abi_bundleHandle()
    {
        if (isValid())
            return getBundleHandle(readOnly_t{});
        return {};
    }

    /**
     * @return the raw bundle interface for use via the ABI directly
     */
    bundleInterface_t* abi_bundleInterface() const
    {
        return m_bundlePtr.get();
    }

    /**
     * @return true if the handle points to valid data within the fabric
     */
    bool isValid() const
    {
        return m_bundlePtr && m_bundlePtr->isValid();
    }

    /**
     * Set the bundle for evaluation. Delayed so that the contents can be created
     * early with just-in-time initialization.
     *
     * @param bundle Evaluation context to use when extracting information
     */
    void reset(omni::core::ObjectParam<bundleInterface_t> bundle)
    {
        m_bundlePtr = omni::core::borrow(bundle.get());
        clearAttributeCache();
    }

    /**
     * Set the context and prim handle for evaluation. Delayed so that the contents can be created
     * early with just-in-time initialization.
     *
     * @param context Evaluation context to use when extracting information
     * @param handle Virtual prim implementing the bundle interface
     */
    void reset(GraphContextObj const& context, bundleHandle_t handle)
    {
        reset(getInterface(readOnly_t{}, context, handle));
    }

    /**
     * @deprecated Calling size() is deprecated. Use attributeCount instead!
     */
    [[deprecated("Calling size() is deprecated. Use attributeCount instead!")]]
    size_t size() const
    {
        return attributeCount();
    }

    /**
     * @return The number of attributes contained within the bundle if valid, 0 otherwise
     */
    size_t attributeCount() const
    {
        return isValid() ? m_bundlePtr->getAttributeCount() : 0;
    }

    /**
     * @return The number of child bundles contained within the bundle if valid, 0 otherwise
     */
    size_t childCount() const
    {
        return isValid() ? m_bundlePtr->getChildBundleCount() : 0;
    }

    /**
     * Extract the interface for an attribute in the bundle with the given name.
     *
     * @param[in] name Token representing the name of the attribute in the bundle
     * @return Bundle member from which attribute information can be extracted (invalid if name was not found)
     */
    runtime_t const attributeByName(NameToken const& name) const
    {
        if ((name == omni::fabric::kUninitializedToken) or ! isValid())
        {
            return runtime_t();
        }
        updateAttributeCache();
        auto namedAttribute = extractNamedAttribute(readOnly_t(), name);
        return runtime_t(m_bundlePtr->getContext(), namedAttribute);
    }

    /**
     * Iteration interfaces that just pass through responsibility to the underlying span data.
     * Inputs call with const objects, hence the two variations of the functions.
     */
    iterator begin() const
    {
        updateAttributeCache();
        return m_iterableArray.begin();
    }
    iterator end() const
    {
        updateAttributeCache();
        return m_iterableArray.end();
    }
    reverse_iterator rbegin() const
    {
        updateAttributeCache();
        return m_iterableArray.rbegin();
    }
    reverse_iterator rend() const
    {
        updateAttributeCache();
        return m_iterableArray.rend();
    }
    iterator begin()
    {
        updateAttributeCache();
        return m_iterableArray.begin();
    }
    iterator end()
    {
        updateAttributeCache();
        return m_iterableArray.end();
    }
    reverse_iterator rbegin()
    {
        updateAttributeCache();
        return m_iterableArray.rbegin();
    }
    reverse_iterator rend()
    {
        updateAttributeCache();
        return m_iterableArray.rend();
    }

    /**
     * Assignment operator is only active for writable bundle contents (i.e. outputs)
     * Copies the entire input bundle onto the output.
     *
     * @param[in] toBeCopied Bundle attribute to be copied
     * @returns Reference to this bundle
     */
    template <eAttributeType AttributeTypeToCopy, eMemoryType MemoryTypeToCopy, PtrToPtrKind GpuPtrTypeToCopy = PtrToPtrKind::eNotApplicable>
    BundleContents<AttributeType, MemoryType, GpuPtrType>& operator=(const BundleContents<AttributeTypeToCopy, MemoryTypeToCopy, GpuPtrTypeToCopy>& toBeCopied)
    {
        static_assert(!readOnly, "Assignment is not allowed on input bundles");

        m_bundlePtr->copyBundle(toBeCopied.abi_bundleHandle());
        reset(m_bundlePtr);
        return *this;
    }

    /**
     * Bundle insertion is only active for writable bundle contents (i.e. outputs)
     * Adds the entire input bundle onto the output.
     *
     * @param[in] toBeInserted Bundle attribute to be inserted
     * @returns Reference to this bundle
     */
    template <eAttributeType AttributeTypeToInsert, eMemoryType MemoryTypeToInsert, PtrToPtrKind GpuPtrTypeToInsert = PtrToPtrKind::eNotApplicable>
    void insertBundle(const BundleContents<AttributeTypeToInsert, MemoryTypeToInsert, GpuPtrTypeToInsert>& toBeInserted)
    {
        static_assert(!readOnly, "Bundle insertion is not allowed on input bundles");
        if (! toBeInserted.isValid())
        {
            CARB_LOG_ERROR("Cannot insert an invalid bundle");
            return;
        }
        if (! isValid())
        {
            CARB_LOG_ERROR("Cannot insert into an invalid bundle");
            return;
        }

        m_bundlePtr->copyBundle(toBeInserted.abi_bundleHandle());
        reset(m_bundlePtr);
    }

    /**
     * Clear the entire bundle contents (outputs only).
     */
    bool clear()
    {
        static_assert(!readOnly, "Clearing of input bundles is not allowed");

        if (!isValid())
        {
            CARB_LOG_ERROR("Cannot clear an invalid bundle");
            return false;
        }

        clearAttributeCache();
        return OMNI_SUCCEEDED(m_bundlePtr->clearContents(true));
    }

    /**
     * Copy an attribute into the bundle. If no name is passed in then use the attribute's current name.
     */
    template <typename RuntimeAttributeType>
    bool insertAttribute(RuntimeAttributeType const& attributeToCopy,
                         NameToken newName = omni::fabric::kUninitializedToken)
    {
        static_assert(!readOnly, "Attribute insertion is not allowed on input bundles");
        if (!isValid())
        {
            CARB_LOG_ERROR("Cannot insert into an invalid bundle");
            return false;
        }

        clearAttributeCache();
        AttributeDataHandle attrib = m_bundlePtr->copyAttribute(attributeToCopy.abi_handle(), true, newName);
        return attrib.isValid();
    }

    /**
     * Create a new attribute in the bundle.
     *
     * @param[in] attributeName Name for the new attribute
     * @param[in] attributeType Base type for the attribute
     * @param[in] elementCount If an array type then this is the initial element count
     * @return Runtime attribute wrapper for the newly created attribute
     */
    runtime_t addAttribute(NameToken const& attributeName, Type const& attributeType, size_t elementCount = 0)
    {
        static_assert(!readOnly, "Attribute addition is not allowed on input bundles");
        if (! isValid())
        {
            CARB_LOG_ERROR("Cannot add to an invalid bundle");
            return runtime_t();
        }

        clearAttributeCache();
        auto attribHandle = m_bundlePtr->createAttribute(attributeName, attributeType, elementCount);
        return runtime_t(m_bundlePtr->getContext(), attribHandle);
    }

    /**
     * Add a batch of attributes to a bundle prim.
     *
     * @param[in] attributeCount Number of attributes to be added
     * @param[in] attrNames Array of names for the new attributes
     * @param[in] attrTypes Array of types for the new attributes
     * @return Whether addition was successful
     */
    bool addAttributes(size_t attributeCount, NameToken const* attributeNames, Type const* attributeTypes)
    {
        static_assert(!readOnly, "Attribute addition is not allowed on input bundles");
        if (! isValid())
        {
            CARB_LOG_ERROR("Cannot add attributes to an invalid bundle");
            return false;
        }

        clearAttributeCache();
        size_t createdCount = 0;
        auto result =
            m_bundlePtr->createAttributes(attributeNames, attributeTypes, attributeCount, nullptr /*elementCount*/,
                                          nullptr /*createdAttributes*/, &createdCount);
        if (OMNI_FAILED(result))
            return false;

        return attributeCount == createdCount;
    }

    /**
     * Add a batch of child bundles to this bundle.
     *
     * @param childCount Number of children to be added
     * @param childNames Array of names for the new children
     * @param childHandles Output handles of child bundles, 'nullptr' can be passed if no output is required
     * @return Whether addition was successful
     */
    bool addChildBundles(size_t childCount, NameToken const* childNames, BundleHandle* childHandles = nullptr)
    {
        static_assert(!readOnly, "Attribute addition is not allowed on input bundles");
        if (!isValid())
        {
            CARB_LOG_ERROR("Cannot add children to an invalid bundle");
            return false;
        }

        size_t createdCount = 0;
        auto result = m_bundlePtr->createChildBundles(childNames, childCount, childHandles, &createdCount);

        if (OMNI_FAILED(result))
            return false;

        return childCount == createdCount;
    }

    /**
     * Remove an existing attribute from the bundle.
     * Silently succeeds if an attribute with the given name did not exist on the bundle
     *
     * @param[in] attributeName Name of the attribute to remove
     */
    bool removeAttribute(NameToken const& attributeName)
    {
        return removeAttributes(1, &attributeName);
    }

    /**
    * Remove a batch of attributes from a bundle prim.
    *
    * @param[in] attributeCount Number of attributes to be removed
    * @param[in] attrNames Array of names to be removed
     * @return Whether removal was successful
    */
    bool removeAttributes(size_t attributeCount, NameToken const* attributeNames)
    {
        static_assert(!readOnly, "Attribute removal is not allowed on input bundles");
        if (!isValid())
        {
            CARB_LOG_ERROR("Cannot remove attributes to an invalid bundle");
            return false;
        }

        clearAttributeCache();
        size_t removedCount = 0;
        auto result = m_bundlePtr->removeAttributesByName(attributeNames, attributeCount, &removedCount);
        if (OMNI_FAILED(result))
            return false;

        return removedCount == attributeCount;
    }
};

//! ======================================================================
//! @class BundleChanges
//! @brief This class is designed for inspecting modifications within a bundle during its lifetime.
//!
//! The BundleChanges class enables the inspection of changes in a bundle's attributes and child bundles
//! during the lifetime of the BundleChanges instance. It keeps a record of modifications that have occurred,
//! providing a suite of functionalities to inspect these changes.
//!
//! An integral feature of BundleChanges is its automatic clearing of changes upon destruction,
//! i.e., when the instance goes out of scope. This ties the lifetime of the recorded changes tightly
//! with the BundleChanges instance, ensuring the changes do not persist beyond the intended scope.
template <bool readOnly>
class BundleChanges
{
    using BundleHandle_t = std::conditional_t<readOnly, ConstBundleHandle, BundleHandle>;

public:
    BundleChanges(omni::core::ObjectPtr<IBundleChanges> const& changes, BundleHandle_t handle, bool clearAtExit = true)
        : m_bundleChanges(changes),
          m_bundleHandle(handle),
          m_clearAtExit(clearAtExit)
    {
        CARB_ASSERT(m_bundleChanges);
    }

    BundleChanges(BundleChanges const&) = delete;
    BundleChanges(BundleChanges&&) = default;

    BundleChanges& operator=(BundleChanges const&) = delete;
    BundleChanges& operator=(BundleChanges&&) = default;

    ~BundleChanges()
    {
        if (m_clearAtExit)
        {
            clearChanges();
        }
    }

    //! @brief Activates the change tracking system for a bundle.
    //!
    //! This method controls the change tracking system of a bundle. It's only applicable
    //! for read-write bundles (when readOnly template parameter is false). For read-only
    //! bundles, this method will cause a compilation error if called.
    //!
    //! @throws A static_assert error at compile-time if the method is called on a
    //! read-only bundle.
    void activate() noexcept
    {
        static_assert(!readOnly, "Can't activate change tracking for read-only bundle.");

        CARB_ASSERT(m_bundleChanges);
        m_bundleChanges->activateChangeTracking(m_bundleHandle);
    }

    //! @brief Deactivates the change tracking system for a bundle.
    //!
    //! This method controls the change tracking system of a bundle. It's only applicable
    //! for read-write bundles (when readOnly template parameter is false). For read-only
    //! bundles, this method will cause a compilation error if called.
    //!
    //! @throws A static_assert error at compile-time if the method is called on a
    //! read-only bundle.
    void deactivate() noexcept
    {
        static_assert(!readOnly, "Can't activate change tracking for read-only bundle.");

        CARB_ASSERT(m_bundleChanges);
        m_bundleChanges->deactivateChangeTracking(m_bundleHandle);
    }

    //! @brief Implicit conversion to bool.
    //!
    //! This operator allows an instance of BundleChanges to be automatically converted to a bool.
    //! The boolean value indicates whether the bundle has undergone any changes within its lifetime.
    //! It leverages the hasChanged() method to provide this information.
    //!
    //! @returns True if the bundle has changed; false otherwise.
    operator bool() noexcept
    {
        return hasChanged();
    }

    //! @brief Clears the recorded changes.
    //!
    //! This method is used to manually clear the recorded changes of the bundle.
    omni::core::Result clearChanges() noexcept
    {
        CARB_ASSERT(m_bundleChanges);

        return m_bundleChanges->clearChanges();
    }

    //! @brief Checks if the bundle has changed.
    //!
    //! This method is used to check if any changes have been made to the bundle's attributes or child bundles
    //! within the lifetime of the BundleChanges instance.
    //!
    //! @returns True if the bundle has changed; false otherwise.
    bool hasChanged() noexcept
    {
        CARB_ASSERT(m_bundleChanges);

        return m_bundleChanges->getChange(m_bundleHandle) != BundleChangeType::None;
    }

    //! @brief Retrieves the change status of a specific attribute.
    //!
    //! This method is used to check if a specific attribute of the bundle has been modified
    //! within the lifetime of the BundleChanges instance.
    //!
    //! @param attribute The specific attribute of the bundle to check for modifications.
    //!
    //! @returns True if the specified attribute has changed; false otherwise.
    template <eAttributeType AttributeType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType>
    BundleChangeType getChange(RuntimeAttribute<AttributeType, MemoryType, GpuPtrType> const& attribute) noexcept
    {
        CARB_ASSERT(m_bundleChanges);

        auto const handle = attribute.abi_handle();
        return m_bundleChanges->getChange(handle);
    }

    //! @brief Retrieves the change status of a specific bundle.
    //!
    //! This method is used to check if a specific bundle or its contents have been modified
    //! within the lifetime of the BundleChanges instance.
    //!
    //! @param bundle The specific bundle to check for modifications.
    //!
    //! @returns A BundleChangeType value indicating the type of change (if any) that has occurred to the specified
    //! bundle.
    template <eAttributeType AttributeType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType>
    BundleChangeType getChange(BundleContents<AttributeType, MemoryType, GpuPtrType> const& bundle) noexcept
    {
        CARB_ASSERT(m_bundleChanges);

        auto const handle = bundle.abi_bundleHandle();
        return m_bundleChanges->getChange(handle);
    }

    //! @brief Retrieves the change status of a specific bundle or attribute using its handle.
    //!
    //! This function is used to check if a specific bundle or attribute, identified by its handle, has been modified
    //! within the lifetime of the BundleChanges instance.
    //!
    //! @tparam HANDLE_TYPE The type of the handle (ConstBundleHandle or ConstAttributeDataHandle).
    //! @param handle The handle to the specific bundle or attribute to check for modifications.
    //!
    //! @returns A BundleChangeType value indicating the type of change (if any) that has occurred to the bundle or
    //! attribute associated with the specified handle.
    template <typename HANDLE_TYPE>
    BundleChangeType abi_getChange(HANDLE_TYPE const& handle) noexcept
    {
        constexpr auto isBundle =
            std::is_same<HANDLE_TYPE, ConstBundleHandle>::value || std::is_same<HANDLE_TYPE, BundleHandle>::value;
        constexpr auto isAttrib =
            std::is_same<HANDLE_TYPE, ConstAttributeDataHandle>::value || std::is_same<HANDLE_TYPE, AttributeDataHandle>::value;

        static_assert(isBundle || isAttrib, "Unsupported handle type for abi_getChange!");
        CARB_ASSERT(m_bundleChanges);

        return m_bundleChanges->getChange(handle);
    }

private:
    omni::core::ObjectPtr<IBundleChanges> m_bundleChanges;
    BundleHandle_t m_bundleHandle;
    bool m_clearAtExit;
};

// ======================================================================
/**
 * Template class responsible for managing the interaction with bundle type input attributes.
 * It wraps the bundle in an interface with a more natural interaction than the raw ABI calls.
 *
 * <AttributeType> How the attribute is interpreted - input, output, or state value
 * <MemoryType> where the memory for the attributes in this bundle will live (CPU, GPU, or decided at runtime)
 */
template <eAttributeType AttributeType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct BundleAttribute
{
    //friend with other templates
    template <eAttributeType, eMemoryType, PtrToPtrKind>
    friend struct BundleAttribute;

private :
    //! Aliases used during overload resolution to differentiate between read-only and read-write.
    using roTag_t = std::true_type;
    using rwTag_t = std::false_type;

    // The writability of a bundle will determine what kinds of operations can be performed on it
    static constexpr bool readOnly = (AttributeType == kOgnInput);
    using readOnly_t = std::conditional_t<AttributeType == kOgnInput, roTag_t, rwTag_t>;
    using bundleHandle_t = std::conditional_t<readOnly, ConstBundleHandle, BundleHandle>;

    /**
     * Construct bundle interface based on provided context and bundle handle.
     *
     * @param context Evaluation context.
     * @param handle Bundle handle.
     */
    auto getInterface(rwTag_t, GraphContextObj const& context, bundleHandle_t handle) const
    {
        auto iComputeGraph = carb::getCachedInterface<ComputeGraph>();
        auto factory = iComputeGraph->getBundleFactoryInterfacePtr();
        return factory->getBundle(context, handle);
    }
    auto getInterface(roTag_t, GraphContextObj const& context, bundleHandle_t handle) const
    {
        auto iComputeGraph = carb::getCachedInterface<ComputeGraph>();
        auto factory = iComputeGraph->getBundleFactoryInterfacePtr();
        return factory->getConstBundle(context, handle);
    }

    /**
     * Bundle attributes always live on the CPU since they are always small, containing only a single value through
     * which their contents can be referenced. The memory type is passed down though, to provide the appropriate
     * interfaces to the attributes within the bundle.
     *
     * @param[in] index In vectorized context, the instance index to access
     * @return The corresponding bundle handle
     */
    bundleHandle_t bundleHandle(size_t index = 0) const
    {
        bundleHandle_t* rel = m_bundleHandleArrayPtr ?  m_bundleHandleArrayPtr[m_offset + index] : nullptr;
        //TODO: multiple input rel
        return rel ? rel[0] : bundleHandle_t{ bundleHandle_t::invalidValue() };
    }

    // --------------------------------------------------------------------------------------------------------------
    //! Data members

    //! Pointer to the vectorized set of data
    bundleHandle_t** m_bundleHandleArrayPtr{ nullptr };

    //! ABI OmniGraph context object
    const GraphContextObj* m_context{ nullptr };

    //! Interface to the bundle data, constructed on demand
    BundleContents<AttributeType, MemoryType, GpuPtrType> m_bundle;

    //! In vectorized context, offset at which we should read our handle
    size_t const& m_offset;

    //! Top level bundle change tracking
    omni::core::ObjectPtr<IBundleChanges> m_bundleChanges;

public:
    // --------------------------------------------------------------------------------------------------------------
    /**
     * Set up the accessor for output attributes with Bundle data
     */
    BundleAttribute(size_t const& offset)
        : m_offset(offset)
    {
    }

    /**
     * Bundle attributes always live on the CPU since they are always small, containing only a single value through
     * which their contents can be referenced. The memory type is passed down though, to provide the appropriate
     * interfaces to the attributes within the bundle.
     *
     * @param[in] index In vectorized context, the instance index to access
     * @return Reference to the raw fabric data.
     */
    BundleContents<AttributeType, MemoryType, GpuPtrType>& operator()(size_t index = 0)
    {
        CARB_ASSERT(context());
        m_bundle.reset(*context(), bundleHandle(index));
        return m_bundle;
    }

    /**
     * Called by the framework to notify the attribute that any cached pointer(s) is/are now invalid.
     *
     * This function is currently not in use, but might becomes relevant in the future with bundle schema
     */
    inline void invalidateCachedPointer()
    {}

    /**
     * Set the evaluation context for the attribute to allow later access. The data isn't available at construction
     * time so this method is provided to add it in when it becomes available.
     *
     * @param[in] contextObj OmniGraph context object to which this attribute belongs
     */
    void setContext(const GraphContextObj& contextObj)
    {
        m_context = &contextObj;
        m_bundleChanges.release();
    }

    /**
     * Set the attribute handle for input bundles
     *
     * @param[in] handle Handle to the attribute to which the bundle belongs
     */
    void setHandle(ConstAttributeDataHandle handle)
    {
        m_context->iAttributeData->getDataR((const void**)&m_bundleHandleArrayPtr, *m_context, &handle, 1);
        m_bundleChanges.release();
    }

    /**
     * Retrieve the context object
     *
     */
    GraphContextObj const* context() const
    {
        return m_context;
    }

    /**
     * @param[in] index In vectorized context, the instance index to access
     * @return The path to the bundle data
     */
    char const* path(size_t index = 0) const
    {
        auto bundlePtr = getInterface(readOnly_t{}, *context(), bundleHandle(index));
        if (!bundlePtr)
        {
            return nullptr;
        }
        omni::fabric::PathC path = bundlePtr->getPath();
        return carb::getCachedInterface<omni::fabric::IPath>()->getText(path);
    }

    /**
     * @param[in] index In vectorized context, the instance index to access
     * @return True if the underlying attribute data is valid for accessing
     */
    bool isValid(size_t index = 0) const
    {
        return bundleHandle(index).isValid();
    }

    /**
     * Assignment operator is only active for writable bundle contents (i.e. outputs).
     * At this level if the data is being stolen it redirects the output to point to the input, otherwise it
     * copies the entire bundle.
     *
     * @note Any accessors to this bundle (operator()) must be called after the assignment or they will be invalid
     *
     * @param[in] toBeCopied Bundle attribute from which this one will be redirected or copied
     * @returns Reference to this bundle
     */
    template <eAttributeType AttributeTypeToCopy, eMemoryType MemoryTypeToCopy, PtrToPtrKind GpuPtrTypeToCopy = PtrToPtrKind::eNotApplicable>
    BundleAttribute<AttributeType, MemoryType, GpuPtrType>& operator=(const BundleAttribute<AttributeTypeToCopy, MemoryTypeToCopy, GpuPtrTypeToCopy>& toBeCopied)
    {
        static_assert(!readOnly, "Assignment is not allowed on input bundles");
        if (!context() || !toBeCopied.isValid())
        {
            CARB_LOG_ERROR_ONCE("Could not assign to or from invalid bundle attribute");
            return *this;
        }

        auto bundlePtr = getInterface(readOnly_t{}, *context(), bundleHandle());
        if (bundlePtr)
        {
            bundlePtr->copyBundle(toBeCopied.bundleHandle());
        }
        return *this;
    }

    //! @brief Retrieves the `BundleChanges` object.
    //!
    //! The `changes` function returns the `BundleChanges` object associated with requested instance.
    //! It allows access to the bundle change tracking.
    //!
    //! @return Returns the `BundleChanges` object associated with requested instance.
    BundleChanges<readOnly> changes(size_t instanceIndex = 0, bool clearAtExit = true) noexcept
    {
        CARB_ASSERT(context());
        if (!m_bundleChanges)
        {
            m_bundleChanges = carb::getCachedInterface<ComputeGraph>()->getBundleChangesInterfacePtr(*context());
        }
        return { m_bundleChanges, bundleHandle(instanceIndex), clearAtExit };
    }
};


} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
