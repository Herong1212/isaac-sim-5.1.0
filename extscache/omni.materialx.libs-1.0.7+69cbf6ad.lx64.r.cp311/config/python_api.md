
# Public API for module MaterialX:

## Functions

- def getTypeString(value)
- def getValueString(value)
- def createValueFromStrings(valueString, typeString)
- def isColorType(t)
- def isColorValue(value)
- def stringToBoolean(value)
- def getDefaultDataSearchPath()
- def getDefaultDataLibraryFolders()
- def getColorSpaces(cms = 'ocio', config = None)
- def transformColor(color, sourceColorSpace, destColorSpace, cms = 'ocio', config = None)
- def getDefaultOCIOConfig()

## Variables

- typeToName: _typeToName
- valueToString: _valueToString
- stringToValue: _stringToValue
- readFromXmlFile: readFromXmlFileBase

## Other

- warnings: builtin module
- UNKNOWN_MODULE_DEFS: unknown
- sys: builtin module
- os: builtin module
