=========
Materials
=========

Introduction
============

The design considerations for non visual materials stems from the requirements that different sensor models need to compute return
strength from ray traced intersections. Therefore, the concept of a material must consist of a generic definition that can operate
from any custom excutable code, i.e. behavior, that has configurable inputs, outputs, and context that is operable on host and device hardware domains.

Non visual material support for different sensor models (i.e. support for Lidar, Radar, and Ultrasonic) can be segmented into to two domains.
The behavior and property domains. The behavior is synonymous with a BSDF (BiDirectional Scattering Distribution function) which defines the details
behind how reflection and transmission sub components are calculated and combined to define a specific behavior. The properties characterize the
data that drive how each component of the BSDF behavior is determined as a function of the non visual sensor wavelength. Upon return, the output
structure will contain a complete set of reflection and/or transmission coefficients, that are agnostic to the source unit space set by the sensor model,
that can be directed back to a receiver or continued through continuation ray methods for advanced ray tracing techniques. The agnostic unit space
simply means that the BSDF behavior does not need to know what the input state is. It can be a normalized intensity, absolute power measure, radiance, or
any input radiometric space a sensor model is designed to run in.

.. _MaterialRequirements:

The material system, which consists of the properties and the behaviors, must conform to the following design requirements in order to operate
in the most generic sense for sensor models.::

    Fully Customizable
    Layered concept
    Ease of use for content developers
    Ease of switching
    Various domains

A system that is fully customizable entails the ability for advanced users to override default behaviors and properties (i.e. input, output, and context).
This includes the ability for a model writer to support different material modeling techinques, such as advanced radiometric through to traditional graphics,
and APIs for fidelity and performance tunability that can be applicable to auto-tuning efforts as well. The layered concept serves normal users with an
"out of the box" experience but also allows for power, or advanced users, to dig in and do things their own way while maintaining separation from their
own sensor model implementation. The ease of use for content developers stems from the requirement that non visual materials can be daunting and require
domain expertise that not everyone has. By abstracting out these intricate details by semantic labeling, content developers can perform the same workflow
with only minimal effort to encode a non visual material with the look and feel of a visual material labeling. The purpose of ease of switching provides
fast and easy remappings of material mapping assignments and behaviors. This can be performed at the power user level where one can redefine everything or
a more basic level of remapping existing materials to fit a specific need. Finally, various domains must be accounted for to provide a generic material system.
The system must support different wave types and spectral information. This means that the materials must be spectrally dependent providing accurate data
for all wavelengths of the sensor models as well as wave types (electromagnetic and mechanical).

The Nvidia material infrastructure supports all of these requirements for Lidar, Radar, and Ultrasonic sensor models and wavetypes. To realize this, NvMaterials
is a plugin system design that encompasses an API for infrastructure execution or extending for partial or full re-implementation. The semantic labeling, shown in the
table below, is the backbone for ease of use for content developers to map non visual materials in assets and maps as well as it allows for power users to
remap properties and behaviors. As mentioned before, remappings can be fully re-implemented in the api design approach or remapping existing behavior and properties
with a simple commandline argument (or carb setting).

The Nvidia material labeling has two options. There is a :ref:`Legacy Material <LegacyMaterials>` workflow and the :ref:`Current Material <CurrentMaterials>`
worflow. The legacy method, though complete, is not very adaptive for future visual material mapping that requires a non visual counterpart. It provides a sufficient
"out of the box" experience but requires user intervention for additional mappings upon changes or additions by content creators. This produces a non visual material mapping
that can become stale over time and error prone from mislabeling. As a result, a new system was developed that provides the same experience but no intervention from the user
and fits under the requirements defined above. The semantic labeling for the non visual materials are set in the USD asset and maps directly. This provides a much easier
workflow that is less error prone. The proceedure for how this is accomplished is discussed in the :ref:`USD section below <USDNonVisualMaterials>`.

In addition to the material definitions, plugin framework, and :ref:`Material Manager <MaterialManager>` providing a complete non visual material architecture,
there are other utils available that depend on the NvMaterials. These include the **Wave Propagation Model** and **Beams Utilities**.
These utilities can be leveraged within a user defined sensor model to service more advanced ray traced configurations while adhering to the non visual material
architecture described above. These utilities also demonstrate how one can implement their own utility and add the material dependence that can be simply
called upon to use the configured BSDFs to compute non visual material outputs. The input and output constructs of the NvMaterial is discussed in greater
detail in the :ref:`NvMatInput <NvMatInput>` and :ref:`NvMatOutput <NvMatOutput>` section.

The key points to sum up for the material system is the following.::

    Non visual materials stem from a visual domain counterpart through the semantic mapping defined below.
    Non visual materials are defined by a csv map (legacy) or through USD attribution (current)
    Materials are easy to use and map
    Easily re-mapped and re-defined for maximum extendability

This is the full feature list of the Nvidia BSDF sub components defining the behaviors derived from the input properties.::

    Simple BSDF behaviors like Constant and Default lambertian
    Complex BSDF behaviors for full radiometric accountability respecting the materials physical and spectral properties
    BSDF response function for reflection/transmission for material boundaries, volumes, and layers
        This includes on sided (air-to-material and vice versa) as well as double sided (air-material-air) boundary types
    Allow sampling to define next even contribution (i.e. continuation rays)
    Ready params for various material bases, wave types, and spectral ranges
    Deterministic
    Optionally usable by users in combination of NV utils
    Optional Phase and Polarization
    Optional coating and layers boundary interactions (multilayer inter-reflection and inter-transmission functions)


Nvidia Non Visual Materials
===========================

There is a limited set of materials, but still rather complete, that exist with the current sensors material infrastructure. The details about
the material behaviors, properties and how their implementations come together will not be discussed, however the list can be identified.
Here is the list of existing materials for the current release::

    ConstantMaterial
    DefaultMaterial
    CoreMaterial
    RetroReflectiveMaterial
    AcousticMaterial
    CompositeMaterial

The ConstantMaterial BSDF is a simple constant value that is returned from every surface. No complex boundary interactions are computed with this BSDF type.
The DefaultMaterial BSDF is a simple lambertian returning a cosine weighted response with a set factor that has a default value of 0.15.
The CoreMaterial BSDF is more complex computing responses for diffuse and specular coefficients based upon the material properties resulting in reflection and
transmission elements.
The RetroReflectiveMaterial is the same as the CoreMaterial BSDF but includes retro reflective aspects of the material surface enhancing reflection returns
in accordance to retro reflective surface types.
The AcousticMaterial is a BSDF specific to ultrasonic sensor models that uses physical properties, rather than optical properties, for computing reflections and
transmissions for mechanical wave types
The CompositeMaterial is a collection of the DefaultMaterial, CoreMaterial, and RetroReflectiveMaterial. It is primarily used in the more sophisticated material
attribution described :ref:`below <CurrentMaterials>`.
The CoreMaterial, CompositeMaterial, RetroReflectiveMaterial, and AcousticMaterial must be configured by an :ref:`NvMatConfig <MaterialManager_MaterialMap>` instance in order to specify
material parameterizations for different surfaces.

.. _NonVisualMaterialsDefined:

Below is a list of supported non visual materials that support Lidar, Radar, and Ultrasonic wavelengths and wave types.::

    AsphaltStandard
    AsphaltWeathered
    VegetationGrass
    WaterStandard
    GlassStandard
    FiberGlass
    MetalAlloy
    MetalAluminum
    MetalAluminumOxidized
    PlasticStandard
    RetroMarkings
    RetroSign
    RubberStandard
    SoilClay
    ConcreteRough
    ConcreteSmooth
    OakTreeBark
    FabricStandard
    PlexiGlassStandard
    MetalSilver

Each of the materials above have a set of bulk and spectral properties. The bulk properties entail physical aspects of a material, such as
density, compressibility, porosity, etc., are used primarily in mechanical wavetype BSDFs for ultrasonic type sensor models. The spectral properties
cover electromagnetic wavetypes, that are defined for many wavelengths, covering optical aspects (such as refractive index) and used in BSDFs for
radar and lidar type sensor models.

.. _LegacyMaterials:

Legacy Materials
================

The legacy material support exists for backward compatibility. It solved the problem of mapping visual materials to a non visual equivalent but
had limitations. The description below depicts how materials are applied to sensor models, but has limitations. The biggest limitation is the
necessity of keeping a csv mapping up to date with visual to non visual material mappings.

The material set is defined in 3 places in order for them to be used in an existing sensor model::

    1. Define and implement the material name and ids in the sensor model extension
    2. Provide commandline options for drivesim corresponding to the material name and id structure within the sensor model
    3. Provide a mapping table from content material names to the materials used within the model


The first step is within the sensor model implementation. The list is inserted into a material map that has a corresponding
index to :ref:`Material Description <MaterialManager_MaterialMap>` used by the :ref:`Material Manager <MaterialManager>`. The map setup within the sensor model is as follows::

    m_materialMap[0] = std::make_pair("DefaultMaterial", NvMatConfig("", spectralRange, 0.25f));
    m_materialMap[1] = std::make_pair("CoreMaterial", NvMatConfig("AsphaltStandard"));
    m_materialMap[2] = std::make_pair("CoreMaterial", NvMatConfig("AsphaltWeathered"));
    m_materialMap[3] = std::make_pair("CoreMaterial", NvMatConfig("VegetationGrass"));
    m_materialMap[4] = std::make_pair("CoreMaterial", NvMatConfig("WaterStandard"));
    m_materialMap[5] = std::make_pair("CoreMaterial", NvMatConfig("GlassStandard"));
    m_materialMap[6] = std::make_pair("CoreMaterial", NvMatConfig("FiberGlass"));
    m_materialMap[7] = std::make_pair("CoreMaterial", NvMatConfig("MetalAlloy"));
    m_materialMap[8] = std::make_pair("CoreMaterial", NvMatConfig("MetalAluminum"));
    m_materialMap[9] = std::make_pair("CoreMaterial", NvMatConfig("MetalAluminumOxidized"));
    m_materialMap[10] = std::make_pair("CoreMaterial", NvMatConfig("PlasticStandard"));
    m_materialMap[11] = std::make_pair("RetroReflectiveMaterial", NvMatConfig("RetroMarkings"));
    m_materialMap[12] = std::make_pair("RetroReflectiveMaterial", NvMatConfig("RetroSign"));
    m_materialMap[13] = std::make_pair("CoreMaterial", NvMatConfig("RubberStandard"));
    m_materialMap[14] = std::make_pair("CoreMaterial", NvMatConfig("SoilClay"));
    m_materialMap[15] = std::make_pair("CoreMaterial", NvMatConfig("ConcreteRough"));
    m_materialMap[16] = std::make_pair("CoreMaterial", NvMatConfig("ConcreteSmooth"));
    m_materialMap[17] = std::make_pair("CoreMaterial", NvMatConfig("OakTreeBark"));
    m_materialMap[18] = std::make_pair("CoreMaterial", NvMatConfig("FabricStandard"));
    m_materialMap[19] = std::make_pair("CoreMaterial", NvMatConfig("PlexiGlassStandard"));
    m_materialMap[20] = std::make_pair("CoreMaterial", NvMatConfig("MetalSilver"));

If your sensor has a specific spectral range you can provide that as part of the NvMatConfig::

    SpectralRange spectralRange { 903.0f };

    m_materialMap[1] = std::make_pair("CoreMaterial", NvMatConfig("AsphaltStandard", spectralRange));

The second step is to define a commandline argument that corresponds to the same index and name
pattern as the material map into the Material Manager. This will inform the kit framework on how to
map a given non visual material to a specified material Id. This is how one would execute drivesim with
the material names and Ids for proper indexing on the commandline::

    _build/linux-x86_64/release/omni.drivesim.e2e.sh --/app/drivesim/defaultNucleusRoot=<omniverse://your_nucleus_server> --/rtx/materialDb/rtSensorNameToIdMap=
    "DefaultMaterial:0;AsphaltStandardMaterial:1;AsphaltWeatheredMaterial:2;VegetationGrassMaterial:3;
    "WaterStandardMaterial:4;GlassStandardMaterial:5;FiberGlassMaterial:6;MetalAlloyMaterial:7;MetalAluminumMaterial:8;
    "MetalAluminumOxidizedMaterial:9;PlasticStandardMaterial:10;RetroMarkingsMaterial:11;RetroSignMaterial:12;RubberStandardMaterial:13;
    "SoilClayMaterial:14;ConcreteRoughMaterial:15;ConcreteSmoothMaterial:16;OakTreeBarkMaterial:17;FabricStandardMaterial:18;
    "PlexiGlassStandardMaterial:19,MetalSilverMaterial:20" --/rtx/materialDb/rtSensorMaterialLogs=false

Note that the name and index corresponds to the map index and name shown in the m_materialMap above. The constant material is
typically used for debugging purposes and is usually omitted from the argument list. The rtSensorMaterialLogs is an optional
arguement, that is defaulted to false, to indicate when a material is not mapped from the content to a non visual material counterpart.
This is useful for identifying whether a material from a map does not have a corresponding assignment in the csv file as described below.

The third step defines a csv file that maps the material assignments in the content from the maps into the non visual material
representation. This mapping is a simple table (named RtxSensorMaterialMap.csv) that contains a comprehensive list of materials encountered
from many different drivesim maps and consolidates those names into a set of names that corresponds to the argument list for drivesim::

    wheelbrakecaliper,MetalAluminumOxidizedMaterial
    omniglassred,GlassStandardMaterial
    wheelchrome,MetalAlloyMaterial
    plastic,PlasticStandardMaterial
    wheelplasticblack,PlasticStandardMaterial
    chrome,MetalSilverMaterial

The file can be quite lengthy when supporting large maps and/or many different maps. The file is located within the packman package
install under packman/chk/kit-sdk/install_version/rendering-data. The install_version is a unique directory name unique to the
version of the kit install. It is not required to have a unique non visual material per material in the content maps.
The mappings can be many to one wth respect to content material to non visual material.

.. _CurrentMaterials:

Current Materials
=================

This section details how a new material infrastructure can be used to assign non visual materials. The main benefit is that the non visual material is defined
in USD making the csv mapping file obsolete. This eliminates any of the concerns where the csv mapping can become stale over time or error prone with mislabeling.
When the usd schema is read, it will produce an encoded materialId that will be decoded in the BSDF to define base and additional BSDF component behavior.
Below details the USD attributes for non visual materials. The definition of the cube is not required. It is shown here to illustrate how the
material.binding USD framework ties into a /Look that contains the USD material schema. It is that material definition where the essential
mapping defines what base material is chosen and any additional details for more advanced BSDF behavior modeling.

.. _USDNonVisualMaterials:
.. code-block:: USD

    def Cube "Cube3" (
    prepend apiSchemas = []
    )
    {
        float3[] extent = [(-1, -1, -1), (1, 1, 1)]
        rel material:binding = </Looks/new_enc> (
                bindMaterialAs = "weakerThanDescendants"
            )
        vector3f physics:angularVelocity = (0, 0, 0)
        bool physics:collisionEnabled = 0
        bool physics:kinematicEnabled = 0
        bool physics:rigidBodyEnabled = 1
        vector3f physics:velocity = (0, 0, 0)
        bool physxRigidBody:disableGravity = 1 (
            allowedTokens = []
        )
        double size = 1.1
        quatf xformOp:orient = (0.707, 0.0, 0.0, -0.707)
        double3 xformOp:scale = (0.000299999888241291, 1, 1)
        double3 xformOp:translate = (-16, -55.25, 1.25)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:orient", "xformOp:scale"]
    }

    def Scope "Looks"
    {
        def Material "new_enc"
        {
            token outputs:mdl:displacement.connect = </Looks/new_enc/Shader.outputs:out>
            token outputs:mdl:surface.connect = </Looks/new_enc/Shader.outputs:out>
            token outputs:mdl:volume.connect = </Looks/new_enc/Shader.outputs:out>

            custom string inputs:nonvisual:base = "aluminum"
            custom string inputs:nonvisual:coating = "clearcoat"
            custom string inputs:nonvisual:attributes = "retroreflective"


            def Shader "Shader"
            {
                uniform token info:implementationSource = "sourceAsset"
                uniform asset info:mdl:sourceAsset = @OmniPBR.mdl@
                uniform token info:mdl:sourceAsset:subIdentifier = "OmniPBR"
                color3f inputs:diffuse_color_constant = (0.67, 0.67, 0.97) (
                    customData = {
                    float3 default = (0.2, 0.2, 0.2)
                    }
                    displayGroup = "Albedo"
                    displayName = "Albedo Color"
                    doc = "This is the albedo base color"
                    hidden = false
                )
                token outputs:out
            }
        }
    }

The example cube above has a material binding that corresponds to the /Look definition for the applied material. Within the Material block, the base, coatings, and attributes
define the base material and additional information for more detailed sub component BSDF behavior. The base material is required but the other fields for coatings
and attributes are optional. For such a situation, the coatings and attributes can be set to "none". The list below details all the supported base materials, coating, and attributes.

Materials, Coatings, and Attributes
***********************************
.. _MaterialsCoatingsAttributes:

Base Materials
--------------

+------------------------+------+-------------------------------------------------------+
|Material Name           |Index |Description                                            |
+========================+======+=======================================================+
|none                    |0     |Default, unlabeled, or unspecified                     |
+------------------------+------+-------------------------------------------------------+

Metals
------

+------------------------+------+-------------------------------------------------------+
|aluminum                |1     |Signs, poles, etc.                                     |
+------------------------+------+-------------------------------------------------------+
|steel                   |2     |Heavy construction metals                              |
+------------------------+------+-------------------------------------------------------+
|oxidized_steel          |3     |Rusted Steel                                           |
+------------------------+------+-------------------------------------------------------+
|iron                    |4     |Manhole covers, drainage grills, etc                   |
+------------------------+------+-------------------------------------------------------+
|oxidized_iron           |5     |Rusted iron                                            |
+------------------------+------+-------------------------------------------------------+
|silver                  |6     |Shiny metals                                           |
+------------------------+------+-------------------------------------------------------+
|brass                   |7     |Architecture                                           |
+------------------------+------+-------------------------------------------------------+
|bronze                  |8     |Statues, etc                                           |
+------------------------+------+-------------------------------------------------------+
|oxidized_Bronze_Patina  |9     |Old Statues                                            |
+------------------------+------+-------------------------------------------------------+
|tin                     |10    |Food cans, etc                                         |
+------------------------+------+-------------------------------------------------------+

Polymers
--------

+------------------------+------+-------------------------------------------------------+
|plastic                 |11    |Generic plastics, etc                                  |
+------------------------+------+-------------------------------------------------------+
|fiberglass              |12    |Car bumpers, etc                                       |
+------------------------+------+-------------------------------------------------------+
|carbon_fiber            |13    |Car parts, bycicle parts, etc                          |
+------------------------+------+-------------------------------------------------------+
|vinyl                   |14    |Car interior, etc                                      |
+------------------------+------+-------------------------------------------------------+
|plexiglass              |15    |Light covers, etc                                      |
+------------------------+------+-------------------------------------------------------+
|pvc                     |16    |Water tubing, etc                                      |
+------------------------+------+-------------------------------------------------------+
|nylon                   |17    |Plastic batc, etc                                      |
+------------------------+------+-------------------------------------------------------+
|polyester               |18    |Some Clothing, etc                                     |
+------------------------+------+-------------------------------------------------------+

Glass
-----

+------------------------+------+-------------------------------------------------------+
|clear_glass             |19    |Glass that is clear with no contaminants               |
+------------------------+------+-------------------------------------------------------+
|frosted_glass           |20    |Glass that has volumetric particulates/imperfections   |
+------------------------+------+-------------------------------------------------------+
|one_way_mirror          |21    |Building glass panels                                  |
+------------------------+------+-------------------------------------------------------+
|mirror                  |22    |Side mirrors, etc                                      |
+------------------------+------+-------------------------------------------------------+
|ceramic_glass           |23    |Heavy Duty glass in construction                       |
+------------------------+------+-------------------------------------------------------+

Other
-----

+------------------------+------+-------------------------------------------------------+
|asphalt                 |24    |Roads, etc                                             |
+------------------------+------+-------------------------------------------------------+
|concrete                |25    |Construction                                           |
+------------------------+------+-------------------------------------------------------+
|leaf_grass              |26    |Live vegetation                                        |
+------------------------+------+-------------------------------------------------------+
|dead_leaf_grass         |27    |Dead vegetation                                        |
+------------------------+------+-------------------------------------------------------+
|rubber                  |28    |Tires, etc                                             |
+------------------------+------+-------------------------------------------------------+
|wood                    |29    |Construction                                           |
+------------------------+------+-------------------------------------------------------+
|bark                    |30    |Trees, vegetation                                      |
+------------------------+------+-------------------------------------------------------+
|cardboard               |31    |Boxes, etc                                             |
+------------------------+------+-------------------------------------------------------+
|paper                   |32    |News papers, paper bags, writing paper, etc            |
+------------------------+------+-------------------------------------------------------+
|fabric                  |33    |Clothing                                               |
+------------------------+------+-------------------------------------------------------+
|skin                    |34    |Human, pig, etc                                        |
+------------------------+------+-------------------------------------------------------+
|fur_hair                |35    |Human head, animal, etc                                |
+------------------------+------+-------------------------------------------------------+
|leather                 |36    |Clothing, car interior, etc                            |
+------------------------+------+-------------------------------------------------------+
|marble                  |37    |Construction                                           |
+------------------------+------+-------------------------------------------------------+
|brick                   |38    |Construction                                           |
+------------------------+------+-------------------------------------------------------+
|stone                   |39    |Nature, stones that have structure                     |
+------------------------+------+-------------------------------------------------------+
|gravel                  |40    |Nature, finer stones such as pebbles                   |
+------------------------+------+-------------------------------------------------------+
|dirt                    |41    |Nature, very fine grainoles such as sand/dust          |
+------------------------+------+-------------------------------------------------------+
|mud                     |42    |Nature, wet dirt                                       |
+------------------------+------+-------------------------------------------------------+
|water                   |43    |Nature, water fountains, lakes, rivers, etc            |
+------------------------+------+-------------------------------------------------------+
|salt_water              |44    |Nature, oceans and seas, free from biologics           |
+------------------------+------+-------------------------------------------------------+
|snow                    |45    |Nature, frozen water droplets (crystalline)            |
+------------------------+------+-------------------------------------------------------+
|ice                     |46    |Nature, frozen water, larger bodies                    |
+------------------------+------+-------------------------------------------------------+
|calibration_lambertion  |47    |Special material with defined diffuse reflectance      |
|                        |      |such as target panels with know reflectance            |
+------------------------+------+-------------------------------------------------------+

Coatings
--------

+------------------------+------+-------------------------------------------------------+
|Coating Name            |Index |Description                                            |
+========================+======+=======================================================+
|none                    |0     |Default, unlabeled, or unspecified coating             |
+------------------------+------+-------------------------------------------------------+
|paint                   |1     |Painted                                                |
+------------------------+------+-------------------------------------------------------+
|clearcoat               |2     |Clear-coated                                           |
+------------------------+------+-------------------------------------------------------+
|paint_clearcoat         |3     |Painted and clear coated                               |
+------------------------+------+-------------------------------------------------------+
|TBD                     |4     |Unused, reserved for future                            |
+------------------------+------+-------------------------------------------------------+
|TBD                     |5     |Unused, reserved for future                            |
+------------------------+------+-------------------------------------------------------+
|TBD                     |6     |Unused, reserved for future                            |
+------------------------+------+-------------------------------------------------------+
|TBD                     |7     |Unused, reserved for future                            |
+------------------------+------+-------------------------------------------------------+

Attributes
----------

+------------------------+------+-------------------------------------------------------+
|Attribute Name          |Index |Description                                            |
+========================+======+=======================================================+
|none                    |0     |Unspecified attribute                                  |
+------------------------+------+-------------------------------------------------------+
|emissive                |1     |Energy emitting surface                                |
+------------------------+------+-------------------------------------------------------+
|retroreflective         |2     |retro reflective surface                               |
+------------------------+------+-------------------------------------------------------+
|single_sided            |4     |Single-sided surface (non-thin geometry)               |
+------------------------+------+-------------------------------------------------------+
|visually_transparent    |8     |Material is visually transparent                       |
+------------------------+------+-------------------------------------------------------+
|TDB                     |16    |Unused, reserved for future                            |
+------------------------+------+-------------------------------------------------------+


The specification tables above with the usd schema defining the base material, coatings, and attributes eliminates the need of a
csv file to perform mappings to non visual materials. These mappings are read in and then used to encode a final material Id. Note
that the semantic material mappings to non visual materials are automatically done for ease of use. The base material Id to non visual
material can be remapped for more advanced usage and is described below.

The material Id is a uint_16 that is uniquely encoded to encompass the base material, coatings, and attributes. The lower byte of the
material Id identifies the base material index. The upper byte encodes the coatings and attributes. The lower 3 bits of the upper byte
encodes the paints and coatings. The upper 5 bits of the upper byte encodes the attributes. The attributes are encoded as a bit field resulting in
each bit uniquely mapping to one of the 5 attributes defined in the table above.::

    attributes  coatings    base material
    xxxxx       xxx         xxxxxxxx

For example, a base material of steel with a paint coating and a retro reflective attribute will have the following encoded materialId.::

    attribute   coating     base material       Final MaterialId generated
    00010       001         00000010            0x0001000100000010 = 4354

It is the responsibility of the BSDF to decode the materialId and perform the specific sub actions defining the desired behavior derived from
the data and the attribution. Despite this requirement, adhering to the material Id specification and leveraging usd for the mapping, the 3
steps identified in the :ref:`Legacy Material <LegacyMaterials>` section above have been reduced down to only two small steps. These steps are to initiate
the loading of the materials into a map that can be parsed by the :ref:`Material Manager <MaterialManager>` and provide variable options enabling
this feature

The material management is reduced down to 2 actions that are considerably simpler and less error prone than the legacy method::

    1. Provide commandline arguments (or carb settings) to enable usd based materials and any optional remappings
    2. Fill material map for material manager to processing

The only required option for enabling the USD based material mapping is the following.::

    --/rtx/materialDb/nonVisualMaterialCSV/enabled=false

.. _Remappings:

Additional arguments exist per sensor modality to provide a means to remap bsdf behaviors and non visual materials per material Id. The remapping only needs
to be performed for the material Id requiring the desired change. For example, the following settings will remap the BSDF behavior and non visual material for
material index 5 and 6 of a lidar sensor.::

    --/app/sensors/nv/lidar/matBehaviorToIdOverrides="CompositeMaterial:5;RetroReflectiveMaterial:6"
    --/app/sensors/nv/lidar/matNameToIdMapOverrides="AsphaltStandard:5;MetalAluminum:6"

In this example, it can be seen that material Ids 5 and 6 have been remapped to the Asphalt and Aluminum properties respectively. Additionally, the BSDF behavior has
been remapped to a CompositeMaterial and RetroReflectiveMaterial. These functions are will now reference asphalt and aluminum base materials but will include the
composite and retroreflective behaviors when computing the output returns. Such changes can be done upon startup or during runtime. If runtime changes are desired, one
additional setting is required that can be done via python using the carb interface.::

    --/app/sensors/nv/materials/resetMaterials=true

These options are all accounted for with a minor amount of code that leverages the :ref:`material reader <MaterialReader>` plugin. This plugin is used within current Nvidia sensor modalities and
is shown here for users who wish to write their own model and need to factor these options in. The following code will perform the desired tasks.::

    SpectralRange spectralRange{ 905.0f };
    std::map<uint32_t, MaterialDesc> materialMap;
    const char* materialToken = nullptr;
    const char* bsdfToken = nullptr;
    omni::string baseRemappings;
    omni::string bsdfRemappings;

    // Determine if the tokens referenced exist. If so, set the remapping scheme.
    // This is not necessary if no remappings are desired
    if (auto* iSettings = carb::getCachedInterface<carb::settings::ISettings>())
    {
        const char* setting = iSettings->getStringBuffer(materialToken);

        if (setting)
            baseRemappings = setting;

        setting = iSettings->getStringBuffer(bsdfToken);

        if (setting)
            bsdfRemappings = setting;
    }

    // Acquire plugin and read the mappings for setup.
    omni::sensors::materials::IMaterialReaderPtr materialReader =
        carb::getFramework()->acquireInterface<omni::sensors::materials::IMaterialReaderFactory>()->createInstance();
    materialReader->readMaterialMapping(materialMap, spectralRange, baseRemappings, bsdfRemappings);

As an example, the tokens in the code above for lidar would be the following.::

    constexpr char materialToken[] = "/app/sensors/nv/lidar/matNameToIdMapOverrides";
    constexpr char bsdfToken[] = "/app/sensors/nv/lidar/matBehaviorToIdOverrides";

Note that the remappings can be null which results in a automatic mapping from the materials identified in the table above to the :ref:`Non Visual Materials <NonVisualMaterialsDefined>`.
This block of code is done at init time and during the prepTrace stage in an rtxSensorModel. This allows the materials to be mapped upon startup or modified during runtime. The
materialMap is simply a material Id to :ref:`material description <MaterialManager_MaterialMap>` map that is parsed by the material manager. The full code
would look like this including the handoff to the material manager. The init call on the material manager is described in the :ref:`material manager <MaterialManager>` section of the docs.::

    SpectralRange spectralRange{ 905.0f };
    std::map<uint32_t, MaterialDesc> materialMap;
    constexpr char materialToken[] = "/app/sensors/nv/lidar/matNameToIdMapOverrides";
    constexpr char bsdfToken[] = "/app/sensors/nv/lidar/matBehaviorToIdOverrides";
    omni::string baseRemappings;
    omni::string bsdfRemappings;

    // Determine if the tokens referenced exist. If so, set the remapping scheme
    // This is not necessary if no remappings are desired
    if (auto* iSettings = carb::getCachedInterface<carb::settings::ISettings>())
    {
        const char* setting = iSettings->getStringBuffer(materialToken);

        if (setting)
            baseRemappings = setting;

        setting = iSettings->getStringBuffer(bsdfToken);

        if (setting)
            bsdfRemappings = setting;
    }

    // Acquire plugin and read the mappings for setup.
    omni::sensors::materials::IMaterialReaderPtr materialReader =
        carb::getFramework()->acquireInterface<omni::sensors::materials::IMaterialReaderFactory>()->createInstance();
    materialReader->readMaterialMapping(materialMap, spectralRange, baseRemappings, bsdfRemappings);

    // Hand off to the material manager for BSDF behavior creation and material property data collection.
    m_materialManager.init(
            materialMap, m_hitShaderPtxString, m_entryPointName, sizeof(UserData), m_cudaDevice);

A final point that a sensor modality needs to accout for is communicating with the rtxSensor infrastructure to request additional data for additional features in
the BSDF behavior. This includes retrieving additional information such as visible band diffuse reflectance and roughness. These option requests to rtxSensor are
enabled by 2 additonal flags. The :ref:`additional data <AdditionalData>` details are also discussed here but is presented here as well for easy reading.::

    // result is a rtx::rtxsensor::RtxSensorRequirements* type coming from the rtxSensor call to getModelRequirements
    result->returnDataConfig |= rtx::rtxsensor::RtxSensorReturnData::RTXSENSOR_RETURN_MATERIAL_REFLECTANCE;
    result->returnDataConfig |= rtx::rtxsensor::RtxSensorReturnData::RTXSENSOR_RETURN_MATERIAL_ADDITIONAL;

The additional information comes in the form of a roughness parameter for visual material surface normal variances. Though the non visual material properties include
such information, the visible band information provides another variable to augment the non visual material roughness to provide a similar roughness scale as the visual.
In addition, the visual band diffuse reflectance information can be accessed when a paint is defined in the non visual material schema. The diffuse color provides a lookup
to retrieve spectral paint data to augment the base material return in a layered fashion for the given sensor modality wavelength.

The Nvidia sensor models can conditionally enable or disable these features by use of two carb settings. The following settings show each of the sensor modalities for
requesting additional information from rtxSensor.::

    --/app/sensors/nv/lidar/enableRtxReflectanceInformation=true
    --/app/sensors/nv/lidar/enableAdditionalRtxReturnInformation=true

    --/app/sensors/nv/radar/enableRtxReflectanceInformation=true
    --/app/sensors/nv/radar/enableAdditionalRtxReturnInformation=true

    --/app/sensors/nv/ultrasonic/enableRtxReflectanceInformation=true
    --/app/sensors/nv/ultrasonic/enableAdditionalRtxReturnInformation=true

Below is the full list of carb settings for controlling material properties and BSDF behaviors. What they are set at indicate their default state.::

    --/app/sensors/nv/lidar/enableRtxReflectanceInformation=false
    --/app/sensors/nv/lidar/enableAdditionalRtxReturnInformation=false
    --/app/sensors/nv/lidar/enablePolarization=false
    --/app/sensors/nv/lidar/matBehaviorToIdOverrides=""
    --/app/sensors/nv/lidar/matNameToIdMapOverrides=""

    --/app/sensors/nv/radar/enableRtxReflectanceInformation=false
    --/app/sensors/nv/radar/enableAdditionalRtxReturnInformation=false
    --/app/sensors/nv/radar/enablePolarization=false
    --/app/sensors/nv/radar/matBehaviorToIdOverrides=""
    --/app/sensors/nv/radar/matNameToIdMapOverrides=""

    --/app/sensors/nv/ultrasonic/enableRtxReflectanceInformation=false
    --/app/sensors/nv/ultrasonic/enableAdditionalRtxReturnInformation=false
    --/app/sensors/nv/ultrasonic/enablePolarization=false
    --/app/sensors/nv/ultrasonic/matBehaviorToIdOverrides=""
    --/app/sensors/nv/ultrasonic/matNameToIdMapOverrides=""

    --/app/sensors/nv/materials/resetMaterials=false
    --/app/sensors/nv/materials/enableMaterialInterLayerContribution=false

    --/rtx/materialDb/nonVisualMaterialCSV/enabled=true
    --/rtx/materialDb/rtSensorMaterialLogs=false
    --/rtx/materialDb/rtSensorNameToIdMap=""

The only paramters that have not been discussed in this document are the enablePolarization and the enableMaterialInterLayerContribution flags. These options
are discussed in the :ref:`NvMatFlags <NvMatFlags>` section.


Plugins
^^^^^^^

This section describes the plugins used to deliver the non visual material framework discussed above.

.. _MaterialReader:

MaterialReader
--------------

The material reader provides an easy to use layer for loading material property data, organizing material property and behavior mappings, and overriding/remapping of
properties and/or behaviors. The interface is defined in::

    include/omni/sensors/materials/IMaterialReader.h

A user can create an instance of the material reader by acquiring the IMaterialReaderFactory (include/omni/sensors/materials/IMaterialReaderFactory.h) carbonite interface
and calling the createInstance() method to instantiate.

Instantiation
*************

Instantiation of the MaterialReader is done through the carbonite interface create instance method from the IMaterialReaderFactory.::

    IMaterialReaderPtr materialReader = carb::getFramework()->acquireInterface<omni::sensors::materials::IMaterialReaderFactory>()->createInstance();


Initialization
**************

In order to read json data containing material property data, the material reader needs to be initialized.::
    materialReader->initialize();


Filling in Material Data (NvMaterial specific)
**********************************************

After instantiation, the material profile reader can read json files, for the input argument path, that contains material property data.::

    omni::sensors::materials::IMaterialReaderPtr materialReader =
        carb::getFramework()->acquireInterface<omni::sensors::materials::IMaterialReaderFactory>()->createInstance();
    materialReader->initialize();
    materialReader->readAndParseJsonFile(materialProfilePath);

    // Optional reading of paints and coating data
    materialReader->readAndParseCoatingVariantJsonFile(coatingsPath);
    materialReader->readAndParsePaintVariantJsonFile(paintsPath);

This part of the material reader plugin is specific to NvMaterials and its defined datasets. User defined materials and behaviors would not use
these features of the material reader. It is mentioned here to fully document the plugin. A model author would be responsible for capturing the
data and storing in a material context that is then accessable in a user defined BSDF. This is where more advanced data can be set via the call
to `getContext` in the IMaterial framework as shown in :ref:`Custom Materials <CustomMaterials>` section for more details. The Material Manager
init function is where the context is fully defined.


Material Map Processing
***********************

The filling in Material data section above is specific to NvMaterials functionality but the material map processing is not Nvidia specific. In this part of the
material reader plugin, the default mappings defined above will be applied unless remapping information is provided. The id to material and id to BSDF behavior
will be parsed and applied such that a map can be passed to the material manager for BSDF plugin behavior creation and data population. The code was already shown
above but is shown again here for ease of readability.::

    SpectralRange spectralRange{ 905.0f };
    std::map<uint32_t, MaterialDesc> materialMap;
    omni::string baseRemappings;
    omni::string bsdfRemappings;

    // Acquire plugin and read the mappings for setup.
    omni::sensors::materials::IMaterialReaderPtr materialReader =
        carb::getFramework()->acquireInterface<omni::sensors::materials::IMaterialReaderFactory>()->createInstance();
    materialReader->readMaterialMapping(materialMap, spectralRange, baseRemappings, bsdfRemappings);

The empty remapping strings simply reflects that the material map will be filled via the default mappings already discussed in the :ref:`Legacy Materials <LegacyMaterials>`
and the :ref:`Current Materials <CurrentMaterials>` sections.

BSDF Material Behavior
----------------------

In order to meet the :ref:`requirements <MaterialRequirements>` for generic support of sensor models and customizable material framework, The BSDF behavior interface
is published as a plugin architecture. The details on how a BSDF plugin is implemented can be found in the :ref:`custom materials <CustomMaterials>` page.