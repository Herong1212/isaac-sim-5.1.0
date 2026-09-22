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

.. _MaterialManager:

Material Manager
################

The material manager is an interface that is responsible for containing, compiling and executing generically defined materially based Bidirectional Scattering Distribtion Functions (BSDF).
Material name and index combinations are input into the manager along with the details for the main entry shader responsible for performing any sensor processing.
Sensor Processing is achieved by the Material Manager encapsulating both the main cuda kernel hit shader for a given sensor and its corresponding material responses.
The main shader is executed and the material responses are resolved by the material Id from the RtxSensorReturn and performs the correct material interactions for the sensor casted ray.

This infrastructure provides a mechanism for supporting internally as well as externally developed material BSDF kernels. For externally developed materials, the material manager interface
simply needs a plugin material registered with the material manager, typically within an rtxsensor model, and defines a cuda kernel to provide the material interaction for the sensor response.
This user defined material must be compiled to PTX and the resultant image buffer is accessable from the material plugin. See the sample_rtxsensor and sample_materials for further details.

The material manager framework is shown here and is described below.

    .. figure:: material_framework.png
        :align: center


Instantiation
*************

To instantiate an material manager object, the following header must be included::

    #include <omni/sensors/materials/MaterialManager.h>

With this header the user can just create an object of the material manager, e.g.::

    omni::sensors::materials::MaterialManager m_materialManager;

Since the material manager interfaces with the device data, a more advanced creation technique is::

    std::map<int32_t, omni::sensors::materials::MaterialManager> m_materialManager;

Using a std::map allows the for interfacing with material managers on a per cuda device context.


Usage
*****

The Material Manager has just 3 main points of operation. First is initialization, second is re-initialization, and third is using
the manager within the RTX Sensor model when batch end is called to process all the hit returns (see sample_rtxsensor). The
re-initializtion allows the Material Mangager to be reset for during runtime. Initialization is performed upon startup but re-initialization
can be performed at any time for material properties (e.g. input data) and behaviors (e.g. BSDF functionality). Processing RtxSensorReturns
within batch end in the sensor model is done continuously throughout the simulation.

Initialization
--------------

The Material Manager and its dependency upon a valid cuda device index requires that the initialization process be done at a time
when RtxSensor provides the plugin with the cuda device. Within the context of the plugin being updated with
the cuda device (e.g. prepTrace), the following initialization can be performed::

    m_materialManager.init(
            m_materialMap, m_hitShaderPtxString, m_entryPointName, sizeof(UserData), m_cudaDevice);

The m_materialMap is a map containing the material descriptions to be included with the key being the desired material Id.
The m_hitShaderPtxString and m_entryPointName are the ptx compiled main hit shader string and the entry point name for the main hit shader respectively.
The final arguments are the size of the user data to be input into the main hit shader for its argument and the cuda device index to interface with.
As mentioned above, the material manager is designed to be for a single cuda context so a more well rounded solution would be to initialize multiple
material managers per cuda device::

    m_materialManager[m_cudaDevice].init(
            m_materialMap, m_hitShaderPtxString, m_entryPointName, sizeof(TraceData), m_cudaDevice);

The main difference here is the usage of the cuda device that is the key for resolving a material manager instance. This is done explicitly
since the material manager cannot easily integrate with the GpuMigrationHandler. Therefore, a material manager per cuda device is required.

It is important that the m_materialMap contains valid material name that properly maps to an existing material plugin. The carbonite registered name within that plugin
is keyed upon at this stage and must be resolved for proper execution. Failure to ensure this is correct will result in no materials mapped and
no meaningful returns for the desired sensor.

**Note**. The initialization stage is where the BSDF material fully defines a context via `getContext`. This is how the host side material property
data is passed into the context that is then written to the device side for kernel execution. This the the important link on how the device side BSDF
accesses the data for computing reflection/transmission functions. See :ref:`Custom Materials <CustomMaterials>` for more details.

.. _MaterialManager_MaterialMap:

Material Map
^^^^^^^^^^^^

The material map is a std::map between a material id and it's description::

    std::map<uint32_t, omni::sensors::materials::MaterialDesc> m_materialMap;

The `MaterialDesc` provides the name of the material and offers a sensor the ability to provide extended material parameters via the `IMaterialConfig` interface::

    using omni::sensors::materials::SpectralRange;
    using omni::sensors::materials::NvMatConfig;

    SpectralRange spectralRange {903.0f};

    m_materialMap[0] = { "CoreMaterial", std::make_shared<NvMatConfig>("RubberStandard", spectralRange) };
    // Alternatively
    m_materialMap[1] = std::make_pair("CoreMaterial", NvMatConfig("PlasticStandard", spectralRange));

.. _MaterialManager_InitializeExample:

Initialization Example
----------------------

The initialization example here can be seen in the RtxSensorSample::setupMaterials() method in the sample_rtxsensor plugin::

    if (m_materialManager.empty())
    {
        // Add material manager for device in map
        m_materialManager.emplace(m_cudaDevice, omni::drivesim::sensors::materials::MaterialManager());
        // Add material to the mapping -> can be changed anytime
        m_materialMap[0] = { "SampleGeneric" };

        m_hitShaderPtxString = (const char*)imageBytes;
        // name of the function in the hitshader
        m_entryPointName = "ProcessReturns_CUDA";
        // init manager
        m_materialManager[m_cudaDevice].init(
            m_materialMap, m_hitShaderPtxString, m_entryPointName, sizeof(TraceData), m_cudaDevice);
    } // MaterialManager cannot be handled by the migration handler -- so do it yourself
    else if (!m_materialManager.empty() && m_materialManager.find(m_cudaDevice) == m_materialManager.end())
    {
        m_materialManager.emplace(m_cudaDevice, omni::drivesim::sensors::materials::MaterialManager());
        m_materialManager[m_cudaDevice].init(
            m_materialMap, m_hitShaderPtxString, m_entryPointName, sizeof(TraceData), m_cudaDevice);
    }

This code demonstrates the index and material name provided to the material map, In addition, the entry point name for the main hit shader,
and the manager creation and initialization is performed with the perscribed input quantities. The imageBytes is the main hit shader data
that has already been compiled to ptx. Compiling the main hit shader and material plugin shaders are required for proper usage of the manager.

Re-initialization
-----------------

Referencing the same example above for material manager initialization, the code can add additional conditionals for runtime re-initialization.::

    if (m_materialManager.empty())
    {
        // Add material manager for device in map
        m_materialManager.emplace(m_cudaDevice, omni::drivesim::sensors::materials::MaterialManager());
        // Add material to the mapping -> can be changed anytime
        m_materialMap[0] = { "SampleGeneric" };

        m_hitShaderPtxString = (const char*)imageBytes;
        // name of the function in the hitshader
        m_entryPointName = "ProcessReturns_CUDA";
        // init manager
        m_materialManager[m_cudaDevice].init(
            m_materialMap, m_hitShaderPtxString, m_entryPointName, sizeof(TraceData), m_cudaDevice);
    } // MaterialManager cannot be handled by the migration handler -- so do it yourself
    else if (!m_materialManager.empty() && m_materialManager.find(m_cudaDevice) == m_materialManager.end())
    {
        m_materialManager[m_cudaDevice].resetMaterialManager();
        m_materialManager[m_cudaDevice].init(
            m_materialMap, m_hitShaderPtxString, m_entryPointName, sizeof(TraceData), m_cudaDevice);
    }

The only difference here is that rather creating a new material manager and initializing, it can be reset and then re-initialized.
This allows the existing materials within the map to persist but be reprocessed allowing any changes to input data or behaviors.


Material Processing
-------------------

Within each trace from RtxSensor, either a single or a series of batchBegin and batchEnd calls are made. Since the material manager must do
something with the returned hits from the ray traced scene, material processing is executed from within the batchEnd notification. This
provides the necessary access to the RtxSensorReturns. The function call to process returns performs this action::

    omni::sensors::materials::MaterialManager::LaunchCfg launchCfg;
    UserData m_userData;
    m_materialManager->processReturns(launchCfg, &m_userData);

The userData is a pointer to some user defined structure that is the input argument to the main hit shader. The init method required the
size of this structure to preallocate the memory for sensor processing within batchEnd. The launchCfg is a structure within the Material Manager
that defines the device side details for launching the main hit shader and subsequent material processing. The LaunchCfg structure has the
following layout::

    struct LaunchCfg
    {
        dim3 blocksPerGrid;
        dim3 threadsPerBlock;
        cudaStream_t cudaStream;
        unsigned int sharedMemBytes{ 0 };
        int cudaDevice;
    };

Allowing for multiple cuda devices, the material manager map can be leveraged to suffice a multi device solution::

    omni::sensors::materials::MaterialManager::LaunchCfg launchCfg;
    UserData m_userData;
    m_materialManager[m_cudaDevice]->processReturns(launchCfg, &m_userData);

Each material that is registered with the MaterialManager has a cuda BSDF (BiDirectional Scattering Distribution Function)
kernel, compiled to ptx, that determines the reflectance and transmission at the boundary. This unique material BSDF program is resolved
by the MaterialManager and called from within the hit shader through the processMaterialById function::

    processMaterialById(void* outBlob, void* inBlob, unsigned int materialId)

The materialId is the index that resolves which BSDF shader to call and the outBlob and inBlob are the output and input structure
to the BSDF. The material input and output structures are defined within the following header file::

    #include <omni/sensors/materials/MaterialDefines.h>

.. _NvMatFlags:

Though the materials interface has defined structures for input and output, the fact that these arguments are void* types signifies
that the MaterialManager infrastructure can support any user defined BSDF kernel for material processing. The structures
within the MaterialDefines.h are the current members for material BSDF computations and have the following definitions::

    enum class NvMatInFlags : uint8_t
    {
        CALC_R = 1,
        CALC_T = 2,
        CALC_PHASE_AND_POLARIZED = 4,
        CALC_INTERNAL_TERMS = 8,
    };

The NvMatInFlags enumeration defines which components within the BSDF to compute. The BSDF will perform a bitwise OR operation to determine
which additional components to compute. The CALC_R component computes the reflectance along the mirror reflection angle direction. The CALC_T
component computes the transmission component in the direction defined by the input direction and the material properties. The CALC_PHASE_AND_POLARIZED
option instructs the BSDF to compute component wise transverse electric and transverse magnetic polarized values and phase tracking. It is the
responsibility of the sensor model to define sensor space aperture polarization (aka analyzer) for polarized returns that are phase tracked. Finally
CALC_INTERNAL_TERMS is an option that works in conjunction with paints and coating layering on the base material return. Light can reflect many times
within a layer adding reflection and transmission terms to the base reflection and transmission options selected. This provides an additional level
of accuracy when paint and coatings are applied to a base material layer. These options are implemented in the current Nvidia based BSDF
functionality. User defined BSDF would need to implement the behavior for such flags if desired::

    struct NvMatRayProps
    {
        float3 vector;
    };

The NvMatRayProps structures are members within the input and output structures for the BSDF (shown below) which are filled once the reflection and transmission
data is calculated. It stores the reflected or transmitted coefficients from the surface boundary and returned to the sensor model hit shader for additional
processing.

.. _NvMatInput:

Given the generic infrastructure behind the material manager and its ability to operate on user defined BSDF behavior types, the NvMatRayProps can be extended
and used in user defined BSDF types. By inheriting from the NvMatRayProps and adding variables unique to any custom BSDF, additional information can be stored
and passed back to the sensor model's hit shader for any user defined additional processing beyond just reflection and transmission functions. User defined materials
is discussed more thoroughly in the :ref:`Custom Materials <CustomMaterials>` section.::

    struct NvMatInput
    {
        float3 matNormal;
        float3 lookupRayDir;
        float3 hitPoint;
        uint32_t materialId{ 0 };
        float thickness{ 0 };
        curandStateType randomState;
        uint8_t flags{ 0 };
        float3 incRayDir;
        float3 diffuseRefl{ make_float3(-0.5f, -0.5f, -0.5f) };
        float roughness{ 0.f };
        NvMatRayProps* incRayProps;
        uint32_t customPropsSize{ 0 };
        float distPrevHit{ 0 };
        float sourceDivergence{ 0.f };
    };

The NvMatInput structure contains input details required for computing material reflection and transmission information. The matNormal
is the normal of the current hit point from within the hit shader. The lookupRayDir is an optional member that defines a look direction
If this look direction is a zero vector, then no computations for the output lookupRayProps will be computed. If the look vector is a non zero
normalized vector, then the reflection components along that view direction are computed. The hitPoint member is the location where the ray intersected
the scene. All of these members are in relative sensor coordinate space. The materialId is the material index from the intersected geometry that is
returned from the RtxSensorReturn. This id is passed down to the BSDF via the input structure to provide material index information. The thickness
provides the at normal incidence depth of the primitive that is hit from the ray traced scene. The randomState is for the cuRand library to compute random
numbers for injecting some material variances. the flag is a control for the to identify how reflection or transmission components are computed (see NvMatInFlags above).
Its value is bitwise ORed with the NvMatInFlags to determine whether to include mirror direction reflection and/or transmission components, phase and polarization, and internal layer contributions.
The incRayDir is self explanatory in that it defines the direction of the incident ray in sensor space. The diffuseRefl flag is an optional parameter that defines
the visible material diffuse color from the hit geometry. This information can be used for providing additonal information for the BSDF to use for more advanced processing.
One such example is providing paint color variants for a single base material type. The roughness variable is another optional additional information piece that can
come from the visible material data. The roughness can be used to provide additional variances (i.e. perturbed normals) derived from visible band content modeling.
The incRayProps allows the vector to define an input starting point. Rather than assuming 1 for the input, it can be in any unit space such that the BSDF behavior
can augment for specific return spaces (i.e. unitless reflectance/transmission, Power space, Radiance space, etc). Note that the input is a pointer to the NvMatRayProps.
This is by design to support generic user defined capabilities. Rather than just using the base vector in the structure to store input states, a user defined derived classtype
can store additional information that the BSDF can leverage. This is one of the primary strengths behind the Material Infrastructure. The customPropsSize supports
the derived aspect of the NvMatRayProps. It is used to keep track of the size of a derived NvMatRayProps. The distPrevHit stores the previous hit distance for
accumulating distances where continuation rays can be cast from previous ray hit point. Finally, the sourceDivergence is a variable that is optional to define how the
source radiation diverges. This can be important for the sensor model since the radiometry in any BSDF may need to account for sufficiently diverging source illumination

.. _AdditionalData:

Note that the flags that control the BSDF behavior details are Nvidia BSDF supported features. A user defined BSDF can define different flags with associated functionality.
Also, the diffuseRefl and roughness parameters are dependent upon flags to rtxSensor. If the following flags are not set, the rtxSensorReturn struct that stores
these values will be nullptr.::

    // result is a rtx::rtxsensor::RtxSensorRequirements* type coming from the rtxSensor call to getModelRequirements
    result->returnDataConfig |= rtx::rtxsensor::RtxSensorReturnData::RTXSENSOR_RETURN_MATERIAL_REFLECTANCE;
    result->returnDataConfig |= rtx::rtxsensor::RtxSensorReturnData::RTXSENSOR_RETURN_MATERIAL_ADDITIONAL;

.. _NvMatOutput:

The following structure defines the output structure that the BSDF fills for the model to consume::

    struct NvMatOutput
    {
        float3 exitPoint;
        float distThroughCurMat{ 0.f };
        uint32_t materialId{ 0 };
        NvMatRayProps* lookupRayProps;
        float3 reflRayDir;
        NvMatRayProps* reflRayProps;
        float3 transRayDir;
        NvMatRayProps* transRayProps;
    };

The NvMatOutput structure stores necessary elements for reflection and transmission at a boundary surface. The exitPoint details where the
ray has exited a material in sensor local space. The distanceThroughCurMat holds the length through the material that is transmission angle
dependent. The materialId is the index from the currently intersected geometry from the traced ray. It is typically the same index as the
material index from the NvMatInput structure. The lookupRayProps is the view direction reflection components. The reflection values are stored
as a float3 to account for both unpolarized and polarized forms of reflection for general sensor model support. The reflRayProps and transRayProps
hold the details about the reflected and transmitted ray. The reflRayDir and transRayDir contain idealized reflected direction and materially defined
transmission direction respectively with respect to the normal vector. Additionally, the "vector" member in the NvMatRayProps
stores the reflection and transmission data both in polarized and unpolarized form. If the input view vector has zero length, the reflected ray props
compute the mirror angle reflection components. If the view vector is non zero, it will determine reflectance data as a function of the view vector.
This structure can be extended to add more user defined data. Note that the NvMatRayProps are pointers to allow for extended user defined behavior.

Material Processing Example
---------------------------

The following depicts how the material manager is used to process returns within the batchEnd rtxSensor stage::

    // Hit shader will be called through the material manager
    // Fill launchConfig for material manager
    const uint32_t numThreadsPerBlock{ std::min((uint32_t)256, m_userData.numRays) };
    const uint32_t numBlocks{ DivideRoundUp(m_userData.numRays, numThreadsPerBlock) };
    omni::drivesim::sensors::materials::MaterialManager::LaunchCfg launchCfg;
    launchCfg.blocksPerGrid.x = numBlocks;
    launchCfg.blocksPerGrid.y = 1;
    launchCfg.blocksPerGrid.z = 1;
    launchCfg.threadsPerBlock.x = numThreadsPerBlock;
    launchCfg.threadsPerBlock.y = 1;
    launchCfg.threadsPerBlock.z = 1;
    launchCfg.cudaDevice = cudaDevice;
    launchCfg.cudaStream = cudaStream;

    m_materialManager[m_cudaDevice]->processReturns(launchCfg, &m_userData);

As mentioned earlier, the m_userData structure is a complete structure that contains all necessary data required
for the main hit shader. As shown here, it provides information that helps segment number of blocks and number of
threads per block.

The sample_rtxsensor example illustrates the full scope of the material manager usage.
