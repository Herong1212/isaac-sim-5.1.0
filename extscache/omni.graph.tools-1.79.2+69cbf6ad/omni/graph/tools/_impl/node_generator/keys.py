"""Common location for all of the keyword definitions for the .ogn format"""


# ==============================================================================================================
class AttributeKeys:
    """Container for the text for all of the .ogn keywords used at the attribute definition level"""

    ALLOWED_TOKENS = "allowedTokens"
    """Metadata list of all allowed tokens on a token-type attribute"""
    CUDA_POINTERS = "cudaPointers"
    """Metadata of the type of array pointers for GPU data"""
    DEFAULT = "default"
    """Default value of the attribute"""
    DEPRECATED = "deprecated"
    """Is the attribute deprecated?"""
    DESCRIPTION = "description"
    """Full description of the attribute"""
    MAXIMUM = "maximum"
    """Maximum value the numeric attribute can use"""
    MEMORY_TYPE = "memoryType"
    """Memory location preferred by the generated attribute access code"""
    METADATA = "metadata"
    """General string-based metadata"""
    MINIMUM = "minimum"
    """Minimum value the numeric attribute can use"""
    OPTIONAL = "optional"
    """The attribute is not required to be valid to allow compute"""
    TYPE = "type"
    """The type of attribute data"""
    UI_NAME = "uiName"
    """The name of the attribute as it will appear in the UI"""
    UNVALIDATED = "unvalidated"
    """True if an extended attribute does not have to be resolved to allow compute"""

    MANDATORY = [DESCRIPTION, TYPE]
    """Attribute keywords required to exist for all attributes"""

    PROCESSED = MANDATORY + [
        CUDA_POINTERS,
        DEFAULT,
        DEPRECATED,
        MEMORY_TYPE,
        METADATA,
        OPTIONAL,
        UI_NAME,
        UNVALIDATED,
        ALLOWED_TOKENS,
    ]
    """Attribute keys that are always directly processed, not relying on AttributeManager derived classes to do it"""


# ==============================================================================================================
class CategoryTypeValues:
    """Container for the set of values allowed for defining node type categories"""

    ANIMATION = "animation"
    DEBUG = "debug"
    FUNCTION = "function"
    GENERIC = "generic"
    GEOMETRY = "geometry"
    INPUT = "input"
    IO = "io"
    MATERIAL = "material"
    MATH = "math"
    RENDERING = "rendering"
    SCENE_GRAPH = "scene_graph"
    TEXTURE = "texture"
    TIME = "time"
    UI = "ui"


# ==============================================================================================================
class CudaPointerValues:
    """Container for the set of values .ogn accepts for the cudaPointers node type"""

    CPU = "cpu"
    CUDA = "cuda"
    NA = "na"
    # These values are members of the enum class omni::fabric::PtrToPtrKind, assuming to have a "using" declaration
    CPP = {
        CPU: "PtrToPtrKind::eCpuPtrToGpuPtr",
        CUDA: "PtrToPtrKind::eGpuPtrToGpuPtr",
        NA: "PtrToPtrKind::eNotApplicable",
    }
    PYTHON = {
        CPU: "og.PtrToPtrKind.CPU",
        CUDA: "og.PtrToPtrKind.CUDA",
        NA: "og.PtrToPtrKind.NA",
    }


# ==============================================================================================================
class ExclusionTypeValues:
    """Container for the .ogn keywords allowed for types of generated code that can be excluded"""

    CPP = "c++"
    DOCS = "docs"
    ICON = "icon"
    PYTHON = "python"
    TEMPLATE = "template"
    TESTS = "tests"
    USD = "usd"


# ==============================================================================================================
class ExtraTypeValues:
    """Container for the .ogn keywords allowed for types of generated code that can be added"""

    PYTHON = "python"


# ==============================================================================================================
class GraphSetupKeys:
    """Container for keywords encapsulating the graph setup entries in the test dictionary, v2+."""

    CONNECT = "connect"
    CREATE_ATTRIBUTES = "create_attributes"
    CREATE_NODES = "create_nodes"
    CREATE_PRIMS = "create_prims"
    CREATE_VARIABLES = "create_variables"
    DELETE_NODES = "delete_nodes"
    DISCONNECT = "disconnect"
    DISCONNECT_ALL = "disconnect_all"
    EXPOSE_PRIMS = "expose_prims"
    SET_VALUES = "set_values"
    PROMOTE_ATTRIBUTES = "promote_attributes"
    ALL = [
        CONNECT,
        CREATE_ATTRIBUTES,
        CREATE_NODES,
        CREATE_PRIMS,
        CREATE_VARIABLES,
        DELETE_NODES,
        DISCONNECT,
        DISCONNECT_ALL,
        EXPOSE_PRIMS,
        SET_VALUES,
        PROMOTE_ATTRIBUTES,
    ]


# ==============================================================================================================
class PrimExposureValues:
    """Options for importing a prim into OmniGraph"""

    READ_PRIM = "read"
    """Read the prim and create dynamic attributes to access each prim attribute"""
    READ_PRIM_BUNDLE = "readBundle"
    """Read the prim and create a single bundle with every prim attribute in it"""
    WRITE_PRIM = "write"
    """Create inputs for every attribute in the prim,
    writing them to the prim if they are connected"""


# ======================================================================
class IconKeys:
    """Holder for the set of keywords that could appear in the icon dictionary"""

    BACKGROUND_COLOR = "backgroundColor"
    BORDER_COLOR = "borderColor"
    COLOR = "color"
    PATH = "path"


# ======================================================================
class LanguageTypeValues:
    """Holder for the set of values that define a language specification"""

    CPP = "C++"
    PYTHON = "Python"
    ALL = {CPP: ["cpp", "c++", "C++"], PYTHON: ["py", "python", "Python"]}

    @staticmethod
    def key_from_text(language: str) -> str:
        """Gets the language name in a canonical form, or raises ValueError if it is not a recognized language"""
        if language in LanguageTypeValues.ALL[LanguageTypeValues.CPP]:
            return LanguageTypeValues.CPP
        if language in LanguageTypeValues.ALL[LanguageTypeValues.PYTHON]:
            return LanguageTypeValues.PYTHON
        raise ValueError(f"Unrecognized language '{language}' - should be one of {list(LanguageTypeValues.ALL.keys())}")


# ======================================================================
class MemoryTypeValues:
    """Holder for the set of keywords identifying memory types"""

    CPU = "cpu"
    CUDA = "cuda"
    ANY = "any"
    ALL = [ANY, CPU, CUDA]
    # These values are members of the type omni::graph::core::ogn::eMemoryType
    CPP = {CUDA: "ogn::kCuda", CPU: "ogn::kCpu", ANY: "ogn::kAny"}
    # These values are members of the type omni.graph.core.MemoryType
    PYTHON = {CUDA: "og.MemoryType.CUDA", CPU: "og.MemoryType.CPU", ANY: "og.MemoryType.ANY"}


# ======================================================================
class MetadataKeys:
    """Holder for common metadata information
    These should match the C++ constant values found in include/omni/graph/core/ogn/Database.h
    as well as the members of MetadataKeyOutput below.
    """

    ALLOW_MULTI_INPUTS = "allowMultiInputs"
    ALLOWED_TOKENS = "allowedTokens"
    ALLOWED_TOKENS_RAW = "__allowedTokens"
    CATEGORIES = "__categories"
    CATEGORY_DESCRIPTIONS = "__categoryDescriptions"
    CUDA_POINTERS = "__cudaPointers"
    DEFAULT = "__default"
    DESCRIPTION = "__description"
    EXCLUSIONS = "__exclusions"
    EXTENSION = "__extension"
    HIDDEN = "hidden"
    ICON_BACKGROUND_COLOR = "__iconBackgroundColor"
    ICON_BORDER_COLOR = "__iconBorderColor"
    ICON_COLOR = "__iconColor"
    ICON_PATH = "__icon"
    INTERNAL = "internal"
    LANGUAGE = "__language"
    MEMORY_TYPE = "__memoryType"
    OBJECT_ID = "__objectId"
    OPTIONAL = "__optional"
    OUTPUT_ONLY = "outputOnly"
    LITERAL_ONLY = "literalOnly"
    SINGLETON = "singleton"
    TAGS = "tags"
    TOKENS = "__tokens"
    UI_NAME = "uiName"
    UI_TYPE = "uiType"

    @classmethod
    def key_names(cls):
        key_names = []
        for key, value in cls.__dict__.items():
            if key == key.upper():
                key_names.append(value)
        return key_names


# ======================================================================
class MetadataKeyOutput:
    """Names of the C++ equivalent constants from MetadataKeys.
    These should match the C++ constant names found in include/omni/graph/core/ogn/Database.h
    as well as the members of MetadataKeys above
    """

    ALLOW_MULTI_INPUTS = "kOgnMetadataAllowMultiInputs"
    ALLOWED_TOKENS = "kOgnMetadataAllowedTokens"
    ALLOWED_TOKENS_RAW = "kOgnMetadataAllowedTokensRaw"
    CATEGORIES = "kOgnMetadataCategories"
    CATEGORY_DESCRIPTIONS = "kOgnMetadataCategoryDescriptions"
    CUDA_POINTERS = "kOgnMetadataCudaPointers"
    DEFAULT = "kOgnMetadataDefault"
    DESCRIPTION = "kOgnMetadataDescription"
    EXCLUSIONS = "kOgnMetadataExclusions"
    EXTENSION = "kOgnMetadataExtension"
    HIDDEN = "kOgnMetadataHidden"
    ICON_BACKGROUND_COLOR = "kOgnMetadataIconBackgroundColor"
    ICON_BORDER_COLOR = "kOgnMetadataIconBorderColor"
    ICON_COLOR = "kOgnMetadataIconColor"
    ICON_PATH = "kOgnMetadataIconPath"
    INTERNAL = "kOgnMetadataInternal"
    LANGUAGE = "kOgnMetadataLanguage"
    MEMORY_TYPE = "kOgnMetadataMemoryType"
    OBJECT_ID = "kOgnMetadataObjectId"
    OPTIONAL = "kOgnMetadataOptional"
    OUTPUT_ONLY = "kOgnMetadataOutputOnly"
    LITERAL_ONLY = "kOgnMetadataLiteralOnly"
    SINGLETON = "kOgnSingletonName"
    TAGS = "kOgnMetadataTags"
    TOKENS = "kOgnMetadataTokens"
    UI_NAME = "kOgnMetadataUiName"
    UI_TYPE = "kOgnMetadataUiType"

    @classmethod
    def cpp_name_from_key(cls, metadata_key: str) -> str:
        """Returns the C++ constant name that defines the given metadata key string, the key itself if no match"""
        # If the key is already one of the constants use it directly
        if metadata_key in MetadataKeyOutput.__dict__.values():
            return metadata_key
        # Find the key corresponding to the value name, if it exists
        for key, value in MetadataKeys.__dict__.items():
            if value == metadata_key:
                return getattr(cls, key)
        # Use the string directly, but return None so that the caller knows to quote it
        return None

    @classmethod
    def python_name_from_key(cls, metadata_key: str) -> str:
        """Returns the Python constant name that defines the given metadata key string, the key itself if no match"""
        # If it's already a member variable use it directly
        if metadata_key.startswith("ogn.MetadataKeys"):
            return metadata_key
        # Find the key corresponding to the value name, if it exists
        for key, value in MetadataKeys.__dict__.items():
            if value == metadata_key:
                return f"ogn.MetadataKeys.{key}"
        # Use the string directly, but return None so that the caller knows to quote it
        return None


# ==============================================================================================================
class NodeTypeKeys:
    """Container for the text for all of the .ogn keywords used at the node definition level"""

    CATEGORIES = "categories"
    CATEGORY_DEFINITIONS = "categoryDefinitions"
    CUDA_POINTERS = "cudaPointers"
    DESCRIPTION = "description"
    EXCLUDE = "exclude"
    EXTRAS = "extras"
    ICON = "icon"
    INPUTS = "inputs"
    LANGUAGE = "language"
    MEMORY_TYPE = "memoryType"
    METADATA = "metadata"
    OUTPUTS = "outputs"
    SCHEDULING = "scheduling"
    SINGLETON = "singleton"
    STATE = "state"
    TAGS = "tags"
    TESTS = "tests"
    TOKENS = "tokens"
    TYPE_DEFINITIONS = "typeDefinitions"
    UI_NAME = "uiName"
    VERSION = "version"
    # Node type keywords required to exist for all attributes
    MANDATORY = [DESCRIPTION]


# ==============================================================================================================
class TestKeys:
    """Container for the text for all of the .ogn keywords used at the test definition level"""

    DESCRIPTION = "description"
    FILE = "file"
    GPU_ATTRIBUTES = "gpu"
    INPUTS = "inputs"
    OUTPUTS = "outputs"
    SETUP = "setup"
    STATE = "state"
    STATE_GET = "state_get"
    STATE_SET = "state_set"
    ALL = [DESCRIPTION, FILE, GPU_ATTRIBUTES, INPUTS, OUTPUTS, SETUP, STATE, STATE_GET, STATE_SET]
    ATTRIBUTES = [INPUTS, OUTPUTS, SETUP, STATE, STATE_GET, STATE_SET]


# ==============================================================================================================
#  _____   ______  _____   _____   ______  _____         _______  ______  _____
# |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
# | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
# | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
# | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
# |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/
#
