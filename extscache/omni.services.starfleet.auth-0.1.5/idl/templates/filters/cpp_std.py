from idl.spec import Spec, BuiltinType


def include(spec: Spec):
    return {
        "cpp_std.safe": cpp_std_safe,
        "cpp_std.type_name": cpp_std_type_name,
        "cpp_std.count_required": count_required
    }


cpp_keywords = {'asm', 'else', 'new', 'this', 'auto', 'enum', 'operator', 'throw', 'bool', 'explicit', 'private',
                'true', 'break   ', 'export', 'protected', 'try', 'case', 'extern', 'public', 'typedef', 'catch',
                'except', 'false', 'register', 'typeid', 'char', 'float', 'reinterpret_cast', 'typename', 'class',
                'for', 'return', 'union', 'const', 'friend', 'short', 'unsigned', 'const_cast', 'goto', 'signed',
                'using', 'continue', 'if', 'sizeof', 'virtual', 'default', 'inline', 'static', 'void', 'delete', 'int',
                'static_cast', 'volatile', 'do', 'long', 'struct', 'wchar_t', 'double', 'mutable', 'switch', 'while',
                'dynamic_cast', 'namespace', 'template', 'and', 'bitor', 'not_eq', 'xor', 'and_eq', 'compl', 'or',
                'xor_eq', 'bitand', 'not', 'or_eq'}

type_mapping = {
    BuiltinType.int8: "int8_t",
    BuiltinType.uint8: "uint8_t",
    BuiltinType.int16: "int16_t",
    BuiltinType.uint16: "uint16_t",
    BuiltinType.int32: "int32_t",
    BuiltinType.uint32: "uint32_t",
    BuiltinType.int64: "int64_t",
    BuiltinType.uint64: "uint64_t",
    BuiltinType.bytes: "std::vector<uint8_t>",
    BuiltinType.boolean: "bool",
    BuiltinType.number: "int64_t",
    BuiltinType.float: "float",
    BuiltinType.double: "double",
    BuiltinType.string: "std::string",
    BuiltinType.blob: "std::vector<uint8_t>",
}


def cpp_std_safe(unsafe):
    if isinstance(unsafe, str):
        unsafe = unsafe.replace('-', '_')
        if unsafe in cpp_keywords:
            unsafe += '_'
        return unsafe
    return unsafe


def cpp_std_type_name(type_name: str):
    return type_mapping.get(type_name, type_name)


def count_required(members):
    return sum(not v['optional'] for v in members)
