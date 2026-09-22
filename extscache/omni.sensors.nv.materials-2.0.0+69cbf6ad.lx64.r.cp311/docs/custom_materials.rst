.. Header 1
.. ########

.. Header 2
.. ********

.. Header 3
.. ========

.. Header 4
.. --------

.. Header 5
.. ^^^^^^^^

.. Header 6
.. """"""""

.. _CustomMaterials:

Custom Materials
################

This section describes how to develop a plugin custom material that can be integrated into a rtxsensor model. The plugin is
registered with the carbonite framework thereby allowing the material manager to pick it up and resolve the
material plugin when called upon in the material manager initialization. This provides a generic interface that preserves
the decoupling of the material manager and a given material plugin. This flexibility is the cornerstone for custom material
development. Having such flexibility does have its requirements to fulfill. An attempt to load a material through the material manager
must be properly registered with carb and built. Without this step, it will result in the material manager not able to resolve the desired material.


Registration
************

To register and subsequently instantiate a custom material, some fundamental carbonite functionality must be in place.

Definition
----------

This section details code sections on the definition for carb implementation in the custom material::

    const struct carb::PluginImplDesc kPluginImpl = { "omni.drivesim.sensors.nv.samples.samplegeneric", "Default", "NVIDIA",
                                                  carb::PluginHotReload::eDisabled, "dev" };

    CARB_PLUGIN_IMPL(kPluginImpl, omni::sensors::materials::IMaterial)

    void fillInterface(omni::sensors::materials::IMaterial& iface)
    {
        using namespace omni::drivesim::sensors::nv::samples;
        iface = { getHash, getContextSize, getContext, getBSDFProgramSizeInfo, getBSDFProgram };
    }

In this sample case, it can be seen the plugin implementation defined and passed into the carb plugin architecture under the
IMaterial interface. This is key as it will allow carb to resolve the material when iterated upon within the material manager
for custom material resolution. The fill interface delineates the function calls to be implemented within the custom material.

Implementation
--------------

The interfaces to fill include getHash, getContextSize, getContext, getBSDFProgramSizeInfo, and getBSDFProgram.
The implementation of these functions are essential since the material manager will call upon these to setup executing custom material
Bidirectional Scattering Distribution Function (BSDF) cuda kernel shader. The following shows how one would implement the interfacing required for the material manager::

    static constexpr char EP_NAME[] = "BSDF_SampleGeneric";
    static constexpr char MAT_NAME[] = "SampleGeneric";

    inline void getBSDFProgramSizeInfo(size_t& programSize, size_t& entryPointNameSize)
    {
        programSize = strlen(reinterpret_cast<const char*>(imageBytes));
        entryPointNameSize = strlen(EP_NAME);
    }

    inline void getBSDFProgram(char* const ptxString, char* const entryPointName)
    {
        memcpy(ptxString, imageBytes, strlen(reinterpret_cast<const char*>(imageBytes)));
        memcpy(entryPointName, EP_NAME, strlen(EP_NAME));
    }

    inline uint64_t getHash()
    {
        return carb::hashString(MAT_NAME);
    }

    inline size_t getContextSize()
    {
        return sizeof(SampleGenericContext);
    }

    inline void getContext(void* context, const omni::drivesim::sensors::materials::IMaterialConfig* materialConfig)
    {
        // Here the material should initialize it's context values. this can be also read from a cfg file.
        SampleGenericContext* mcontext = reinterpret_cast<SampleGenericContext*>(context);
        mcontext->factor = 1.f;
    }

Get hash and getContextSize are rather self explanatory. The function getContext is where one would go about writing details that
encapsulate specific elements required for a custom material. For example, the materialConfig is an opaque pointer to a struct that can be used for providing
data to fill in the context which will be set as an input argument to the custom material kernel shader. It is here where the material property data
specific to a BSDF behavior is passed to the material context so that the data is available in the device side when the kernel processes the return. As the
comment in the code shows, this is where some config file can be read in and parsed for data to fill in the context for the BSDF kernel.
NvMaterials leverages the json reading capability of the :ref:`Material Reader <MaterialReader>` to fill in the BSDF context with non visual material data.
This effectively provides a bridge between the outside rtxsensor model and the standalone custom material. This keeps the custom material independent of the sensor.

The functions getBSDFProgramSizeInfo and getBSDFProgram have an important as well in that the usage of the imageBytes requires a precursor step.
The cuda kernel for the custom material must be compiled to PTX beforehand. The imageBytes variable in this implementation is defined from this
compile process and is found in a header file that is included in this implementation here::

    #include "SampleGenericCuda.ptx.h"

When a material is resolved and added to the material manager, the manager will perform some steps to complete the just in time compilation
of the custom material. In addition, it will get the context details and call upon it for setting up the input details for the custom material
into the BSDF implementation.


Custom Kernel
*************

The final step in implementing a custom material plugin is to implement the BSDF function. The general architecture of the custom material
with the decoupled plugin interface really demonstrates how one can implement the BSDF function in any way desired. The loose coupling
to the material manager has lead to this very generic interface.
The BSDF example here can be found in the sample_materials plugin::

    namespace samples = omni::drivesim::sensors::nv::samples;
    namespace materials = omni::sensors::materials;

    NV_HOSTDEVICENOINLINE void BSDF_SampleGeneric(void* outBlob, void* inBlob, void* inContext)
    {
        materials::NvMatInput* matIn = reinterpret_cast<materials::NvMatInput*>(inBlob);
        materials::NvMatOutput* matOut = reinterpret_cast<materials::NvMatOutput*>(outBlob);
        samples::SampleGenericContext* context = reinterpret_cast<samples::SampleGenericContext*>(inContext);
        // here only reflectance is calculated as the dot product of the incidence ray and surface normal, multiplied by a
        // factor
        float3 negIncDirection = -1.0f * matIn->incRayProps.dir;
        matOut->reflRayProps.vector.x = dot(negIncDirection, matIn->matNormal) * context->factor;
    }

The input and output structures define typical data elements found when computing BSDFs. The context is also found here showing that the custom
material has the ability to input unique data for its BSDF. The input and output structures have the following data members::

    enum class NvMatInFlags : uint8_t
    {
        CALC_R = 1, /**< compute mirror reflectance component */
        CALC_T = 2, /**< computes transmission component */
        CALC_PHASE_AND_POLARIZED = 4,
        CALC_INTERNAL_TERMS = 8,
    };

    struct NvMatProps
    {
        // transmissive or reflectance
        float3 vector; /**< either field vector or 0-value,1 tetm[0],2 tetm[1] */
    };

    struct NvMatInput
    {
        float3 matNormal; /**< unit vector defining the surface normal at incidence hit point */
        float3 lookupRayDir; /**< unit vector defining the view direction for BSDF lookup */
        float3 hitPoint; /**< hit point of the material in same coordinates like ray */
        uint32_t materialId{ 0 }; /**< Id of current material intersected */
        float thickness{ 0 }; /**< thickness of material at hit point */
        curandStateType randomState; /**< curand state */
        uint8_t flags{ 0 }; /** <specifies the types of bsdf components to compute */
        NvMatRayProps* incRayProps;
        float3 diffuseRefl{ make_float3(-0.5f, -0.5f, -0.5f) }; /**< visible band diffuse reflectance */
        float roughness{ 0.f };
        uint32_t customPropsSize{ 0 };
        float distPrevHit{ 0 };
        float sourceDivergence{ 0.f }; /**< characterize beam divergence of source radiation */
    };

    struct NvMatOutput
    {
        float3 exitPoint; /**< transmitted ray exit point in same coordinates like ray */
        float distThroughCurMat{ 0.f }; /**< propagated distance within material */
        uint32_t materialId{ 0 }; /**< Id of current material intersected */
        NvMatRayProps* lookupRayProps; /**< reflectance along the backscatter direction */
        float3 reflRayDir; /**< if CALC_R, reflected ray direction*/
        NvMatRayProps* reflRayProps; /**< Ideal reflected ray props */
        float3 transRayDir; /**< if CALC_T, transmitted ray direction */
        NvMatRayProps* transRayProps; /**< Transmitted ray props */
    };

The NvMatInFlags enumeration provides a means to control which reflection and transmission components to compute. The enum is a bitfield definition
to provide a means for the BSDF to selectively add computing for mirror direction reflection components and/or transmission components. The Phase and
Polarization flag computes reflection and transmission coefficients maintaining the polarized structure of the incident light and the material interaction.
It additionally keeps track of phase details for a sensor model to accumulate for coherent summation. The last flag adds an additional layering
where the reflection and transmission coefficients are more accurately computed accounting for layering of materials (i.e. clearcoat on metal).

The NvMatRayProps structure contains the data from a reflection or transmission event. The "vector" member, is a generic storage that can
contain the unpolarized and polarized (in 2 planes) reflection or transmission data. Alternatively, it can contain the full field
amplitude upon reflection or transmission.

The NvMatInput structure contains all the necessary information for computing light matter interactions at a boundary surface. The matNormal
variable contains the normal of the surface. the lookupRayDir is the view direction (or look direction) for which a reflection event is viewed
from. This is can include look directions that are parallel with the incident direction (i.e. backscatter). If the lookupRayDir is a zero vector,
no view dependent reflection component is computed. The hitPoint variable is the 3D location in space where the ray intersected a primitive.
The materialId is the material index returned from the RtxSensor within the RtxSensorReturn structure from the intersected primitive. The thickness
is the at normal incidence depth of the intersected primitive. The randomState is the random number state for the curand library. It provides a
means to compute random values to inject variance into the reflected or transmitted data. The flag variable identifies which bsdf components to
compute for output per NvMatInFlags. The incRayProps provides the ability to perform continuation rays where the incident diminished from the first
boundary interaction (i.e. incRayProps are less than 1). The diffuseRefl and roughness are additional data members input from rtxSensorReturns to provide
information for the BSDF to augment paints with color information and surface roughness thereby giving more variation in the reflection and transmission
returns. The customPropsSize is the size of the RayProps structure size. This is important since the NvMatRayProps is a base class pointer
and can be extended. The customPropsSize details the size of the derived instance. The distPrevHit is used for continuation rays where the hit distance
can be accumulated for multiple continuations. The source divergence is a variable to help model the wave optical phenomena of the source beam.
The BSDF can more accurately compute reflection and transmission having information about the source beam divergence. Additional description of
input and output can be found :ref:`here <NvMatInput>`.

The NvMatOutput structure contains variables that store information about the reflection or transmission event at a boundary. The exitPoint is
the location where a new ray (secondary ray) is starting from. It is the exit location of the first ray which is coincident with a secondary ray
start position. The distThroughCurMat is the distance through a material that is transmission angle dependent. The materialId is the index from
the intersected primitive from the ray tracer. It is typically the same index in the materialId member in the NvMatInput structure. The lookupRayProps
contains the backscattered or view reflectance. It is stored as a float3 to capture both the unpolarized and polarized reflectance components. The reflRayProps
and transRayProps are the essential parts that contain the reflection and transmission information when the ray interacts with a material. The
reflRayProps is the reflection components along the mirror reflection angle (i.e. opposite angle from the indicence angle with respect to the normal).
The reflRayDir and transRayDir are the directions of the ray upon reflection and transmission. These are primarily used by continuation rays.

**Note:** The entry and exit points of the BSDF are void* types allowing a custom BSDF to use any input and output data structure.
These structs can be anything defined by the user as long the material and the model using the material both have same definition.
For example, the NvMatInput and NvMatOutput structures can be extended for users who wish to expand upon the current capability. The above
structs are examples from the definitions for existing Nvidia materials. Rather than extending the input and output data structures, the
NvMatInput and NvMatOutput can be used in the current state but the NvMatRayProps can be extended. The derived behavior can provide additional data
for a user defined BSDF to operate upon. This is one of the essential capabilities of the input and output of the BSDF. It can be fully customized
to any desirable level. The infrastructure can be used as is, partially customized or fully customized.

The sample_rtxsensor will demonstrate how the material is integrated into the material manager. The only significant key aspect to this designed
is that providing the correct material name to the material manager is paramount for proper integration.

Material Definitions and Execution (Legacy Material Mapping)
************************************************************

In order to run custom materials through the legacy workstream, 3 key things need to be implemented::

    1. Define and implement the material name and ids in the sensor model extension
    2. Provide commandline options for drivesim corresponding to the material name and id structure within the sensor model
    3. Provide a mapping table from content material names to the materials used within the model


The first step is to define the material within the sensor model.
See the :ref:`Initialization Example <MaterialManager_InitializeExample>` and the :ref:`Legacy Materials <LegacyMaterials>` on how a
material map is populated for custom materials to be utilized within a custom model.

The second step is to specify the commandline options for drive sim to assign the material Id for the custom materials. The description found
in the :ref:`Legacy Materials <LegacyMaterials>` section cover this detail. Simply adding the string and Id for each material
and adding it in the same fashion in the sensor model implementation will tie the material Id from the RtxSensorReturn to what is
indexed in the custom BSDF shown above.

The third step involves providing a table that maps the materials from loaded content to the custom non visual materials. The :ref:`Legacy Materials <LegacyMaterials>`
section details the csv file and how all the encountered materials from the content in the scene need to map to a non visual material.
This will assign a valid material Id so that each RtxSensorReturn will have a valid BSDF to index call upon. This call to the BSDF
is handled with the :ref:`Material Manager <MaterialManager>` in the materials processing example.

Material Definitions and Execution (Current Material Mapping)
*************************************************************

In order to run custom materials in this workflow, attribution needs to be defined on the USD for all assets and maps. This is already covered
in the :ref:`Current Materials <CurrentMaterials>` section. For custom materials, two steps are required for operability.

    1. Define the materials
    2. Provide mappings to allow user defined BSDF to be executed


The first step is to define the material within the sensor model.
See the :ref:`Initialization Example <MaterialManager_InitializeExample>` and the :ref:`Current Materials <CurrentMaterials>` on how a
material map is populated for custom materials to be utilized within a custom model.

The second step is to specify commandline options to provide any remappings for the non visual material and BSDF behavior. The sample_rtxsensor
demonstrates how the material and bsdf behavior are mapped but a more advanced configuration requires the remapping the BSDF behavior as discussed :ref:`here <Remappings>`.
User defined BSDFs can be mapped to the input material Id under the USD material attribution scheme.

These steps will enable a custom material, detailing both the properties and behaviors, to be executed in a generic fashion.
