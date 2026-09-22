"""
AutoNode - module for decorating code to populate it into OmniGraph nodes.

Allows generating nodes by decorating free functions, classes and modules by adding `@AutoFunc()` or `@AutoClass()` to
the declaration of the class.

Generating code relies on function signatures provided by python's type annotations, therefore the module only supports
native python types with `__annotations__`. CPython classes need need to be wrapped for now.

Exports: `AutoClass`, `AutoFunc`


How an AutoNode decorator works: # TODO

How an AutoNode function execution works:

1. Attribute discovery
    Attributes are scanned from the db at runtime
2. Attribute type resolution
    types.py contains type conversion facilities to decide on the outgoing type of afunction
3. Attribute value resolution
    If needed, values are retrieved from the object store
4. Function execution
    function is called.
5. Return value resolution
    if the return value needs to be stored outside node, it happens now.
6. Dispatch to other nodes
    propagation of values and execution statnode"""

# standard lib imports
import inspect

# meta imports
from typing import Callable, Dict, List

# framework imports
import carb

from .core import AutoNode
from .enum_wrappers import EnumAutoNodeDefinitionGenerator
from .event import EventAutoNodeDefinitionGenerator
from .function import AutoFunctionWrapper
from .property import AutoPropertyWrapper

# module imports
from .type_definitions import AutoNodeDefinitionGenerator
from .util import FUNC_INFIX, GET_SUFFIX, PROP_INFIX, SET_SUFFIX, is_private, python_name_to_ui_name, sanitize_qualname


# ================================================================================
def GenerateAutoFunc(  # noqa: N802
    func: Callable,
    *,
    qualname: str = None,
    ui_name: str = None,
    pure: bool = False,
    module_name: str = None,
    tags: List[str] = None,
    annotation: Dict = None,
):
    """Decorator for methods and function objects.

    Attributes
        func: the function object being wrapped. Should be a pure python function object or any other callable which
                has an `__annotations__` property.
        qualname:   [optional] override the inferred qualified name
        ui_name:    [optional] name that appears in the funcion's menu and node display.
        pure:       [optional] override this function to be a pure function - a function independent of object state
                    and without side effects, which doesn't enforce a specific execution order.
        module_name:[optional] override the inferred module name
        tags:       [optional]
        annotation: [optional] override annotations
    """
    qualname = qualname or func.__qualname__
    unique_name = sanitize_qualname(qualname)
    module_name = module_name or func.__module__
    ui_name = ui_name or python_name_to_ui_name(qualname)

    func_wrapper = AutoFunctionWrapper(
        func, unique_name=unique_name, ui_name=ui_name, pure=pure, tags=tags, annotation=annotation
    )

    AutoNode.generate_code_and_store(func_wrapper, unique_name=unique_name, module_name=module_name)

    return func


# ================================================================================
def GenerateAutoClass(target_class, *, module_name: str, annotation: Dict = None):  # noqa: N802
    """Decorator for classes.
    Registers the class in the type registry, and returns the wrapped class.

    Attributes
        target_class: class being wrapped.
        module_name: [optional] override the inferred module name
        annotation: a dict containing annotations for all members
            in the class. Used if passed a type with no annotations.
    """
    class_directory = {}
    module_name = module_name or target_class.__module__
    class_shortname = target_class.__name__
    class_unique_name = f"{target_class.__qualname__}"
    class_sanitized_name = sanitize_qualname(target_class.__qualname__)

    # first, extract special type functionality and ignore special type helpers
    members_to_ignore = set()
    for type_handler in AutoNode.registry().type_handlers:
        definitions, members = type_handler.generate_from_definitions(
            target_type=target_class,
            type_name_sanitized=class_sanitized_name,
            type_name_short=class_shortname,
            module_name=module_name,
        )

        for definition in definitions:
            AutoNode.generate_custom_node(definition)

        members_to_ignore.update(members)

    def _member_filter(name):
        ret = True
        ret &= not is_private(name)
        ret &= name not in members_to_ignore
        return ret

    members_to_scan = [key for key in target_class.__dict__ if _member_filter(key)]

    # scan remaining, ordinary members

    for key in members_to_scan:
        key_unique_name = f"{class_unique_name} : {python_name_to_ui_name(key)}"
        value = target_class.__dict__[key]

        if inspect.ismethoddescriptor(value):
            # this method came from C++, but isn't a function
            if annotation is None or key not in annotation:
                # can't handle instance methods for now
                carb.log_warn(
                    f"Can't wrap {key_unique_name}: C functions require an annotation shim and none was provided"
                )
                continue

            func_sanitized_name = f"{class_sanitized_name}{FUNC_INFIX}{key}"
            func_ui_name = f"{class_unique_name} : {python_name_to_ui_name(key)}"
            GenerateAutoFunc(
                value,
                qualname=func_sanitized_name,
                ui_name=func_ui_name,
                module_name=module_name,
                pure=False,
                annotation=annotation[key],
            )

            class_directory[key] = func_sanitized_name

        elif inspect.isfunction(value):
            # python function object
            func_sanitized_name = f"{class_sanitized_name}{FUNC_INFIX}{key}"
            func_ui_name = f"{class_unique_name} : {python_name_to_ui_name(key)}"
            shim = annotation.get(key, None) if annotation else None
            GenerateAutoFunc(
                value,
                qualname=func_sanitized_name,
                ui_name=func_ui_name,
                module_name=module_name,
                pure=False,
                annotation=shim,
            )

            class_directory[key] = func_sanitized_name

        elif inspect.isdatadescriptor(value):
            # has a getter, a setter and a deleter
            prop_sanitized_name = f"{class_sanitized_name}{PROP_INFIX}{key}"
            getter_sanitized_name = f"{prop_sanitized_name}{GET_SUFFIX}"
            getter_ui_name = f"{class_unique_name} : Get {key}"
            setter_sanitized_name = f"{prop_sanitized_name}{SET_SUFFIX}"
            setter_ui_name = f"{class_unique_name} : Set {key}"

            type_override = annotation.get(key, None) if annotation else None
            if not type_override:
                carb.log_warn(f"{class_unique_name}.{key} has no annotation, and will be skipped")
                continue

            getter_shim = {"return": type_override}
            setter_shim = {"value": type_override, "return": None}

            GenerateAutoFunc(
                value.getter,
                qualname=getter_sanitized_name,
                ui_name=getter_ui_name,
                module_name=module_name,
                annotation=getter_shim,
            )

            GenerateAutoFunc(
                value.setter,
                qualname=setter_sanitized_name,
                ui_name=setter_ui_name,
                module_name=module_name,
                annotation=setter_shim,
            )

            class_directory[key] = {"get": getter_sanitized_name, "set": setter_sanitized_name}

        else:
            # it's a value and should be wrapped in a property

            prop_sanitized_name = f"{class_sanitized_name}{PROP_INFIX}{key}"
            getter_sanitized_name = f"{prop_sanitized_name}{GET_SUFFIX}"
            getter_ui_name = f"{class_unique_name} : Get {key}"
            setter_sanitized_name = f"{prop_sanitized_name}{SET_SUFFIX}"
            setter_ui_name = f"{class_unique_name} : Set {key}"

            shim = annotation.get(key, None) if annotation else None
            wrapper = AutoPropertyWrapper(target_class, name=key, type_override=shim)

            GenerateAutoFunc(
                wrapper.get, qualname=getter_sanitized_name, ui_name=getter_ui_name, module_name=module_name, pure=False
            )

            GenerateAutoFunc(
                wrapper.set, qualname=setter_sanitized_name, ui_name=setter_ui_name, module_name=module_name, pure=False
            )

            class_directory[key] = {"get": getter_sanitized_name, "set": setter_sanitized_name}

            AutoNode.registry().func_name_to_func[prop_sanitized_name] = wrapper

    AutoNode.registry().class_to_methods[target_class] = class_directory
    return target_class


##################################################################################
#                                                                                #
#  public interface                                                              #
#                                                                                #
##################################################################################


# ================================================================================
def AutoClass(**kwargs):  # noqa: N802
    # inject locals for linking
    if "module_name" not in kwargs:
        try:
            kwargs["module_name"] = inspect.currentframe().f_back.f_locals["__package__"]
        except (AttributeError, KeyError):
            kwargs["module_name"] = "default_module"
            carb.log_warn("No module name found in package. Assigning default name 'default_module'")

    def ret(cls):
        return GenerateAutoClass(cls, **kwargs)  # noqa: PLE1125

    ret.__doc__ = GenerateAutoClass.__doc__
    return ret


# ================================================================================
def AutoFunc(**kwargs):  # noqa: N802
    # inject locals for linking
    if "module_name" not in kwargs:
        try:
            kwargs["module_name"] = inspect.currentframe().f_back.f_locals["__package__"]
        except (AttributeError, KeyError):
            kwargs["module_name"] = "default_module"
            carb.log_warn("No module name found in package. Assigning default name 'default_module'")

    def ret(func):
        return GenerateAutoFunc(func, **kwargs)

    ret.__doc__ = GenerateAutoFunc.__doc__
    return ret


# ================================================================================
def register_autonode_type_extension(handler: AutoNodeDefinitionGenerator, **kwargs):
    # if "module_name" not in kwargs:
    #     kwargs['module_name'] = inspect.currentframe().f_back.f_locals["__package__"]
    AutoNode.registry().type_handlers.add(handler)


# ================================================================================
def unregister_autonode_type_extension(handler: AutoNodeDefinitionGenerator, **kwargs):
    # if "module_name" not in kwargs:
    #     kwargs['module_name'] = inspect.currentframe().f_back.f_locals["__package__"]
    AutoNode.registry().type_handlers.remove(handler)


# should help clean in hot reloads
AutoNode.registry()._reset()  # noqa: PLW0212

# Add Enums
register_autonode_type_extension(EnumAutoNodeDefinitionGenerator)

# Add Events
register_autonode_type_extension(EventAutoNodeDefinitionGenerator)
