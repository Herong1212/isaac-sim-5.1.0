import importlib
from typing import Callable

import omni.graph.tools.ogn as ogn

from ..settings import Settings
from .type_definitions import AutoNodeDefinitionWrapper, TypeRegistry


# ==============================================================================================================
class AutoNode:
    @staticmethod
    def registry():
        return TypeRegistry.instance()

    # --------------------------------------------------------------------------------
    @staticmethod
    def generate_code_and_store(
        wrapper: AutoNodeDefinitionWrapper, unique_name: str, *, module_name: str = None
    ) -> None:
        """Generates the implementation for the Ogn class and stores it in the registry.

        Attributes
            func_wrapper: Positional. The function wrapper object for which code should be generated.
            func_name: name of function getting stored. Name is assumed to be sanitized
            module_name: [optional] override the name of the module as detected by the reflection system.
        """

        if not unique_name.find(".") == -1:
            raise NameError(f"{unique_name} is not a valid name for a class, since it contains a '.'")

        AutoNode.registry().func_name_to_func[unique_name] = wrapper
        name_prefixed = f"Ogn_{unique_name}"

        module_name = module_name or wrapper.get_module_name()

        code = ogn.code_generation(
            wrapper.get_ogn(),
            name_prefixed,
            module_name,
            "omni.graph.tools",
            Settings.generator_settings(),
        )

        ##################
        # Code Injection #
        ##################

        # create a virtual module
        v_module = importlib.util.module_from_spec(globals()["__spec__"])
        AutoNode.registry()._impl_modules[name_prefixed] = v_module  # noqa: PLW0212

        # inject dependencies into the generated module
        v_module.__dict__["AutoNode"] = AutoNode
        # v_module.__dict__.update([(a.__name__, a) for a in omni.graph.tools.ogn.typing.all_data_types])

        # DANGER ZONE: execute the python node database definition in the target node
        exec(code["python"], vars(v_module))  # noqa: PLW0122

        # inject the generated implementation into the module
        setattr(v_module, name_prefixed, wrapper.get_node_impl())
        node_class = getattr(v_module, name_prefixed)

        # retrieve the registration action from the node db and register the node
        db_class = getattr(v_module, name_prefixed + "Database")
        do_register = db_class.register
        do_register(node_class)

    # --------------------------------------------------------------------------------
    @staticmethod
    def generate_custom_node(wrapper: AutoNodeDefinitionWrapper):
        AutoNode.generate_code_and_store(
            wrapper, unique_name=wrapper.get_unique_name(), module_name=wrapper.get_module_name()
        )


# ==============================================================================================================
class AutoNodeEvaluationDelayedExecutionQueue:

    _queue = []

    def __init__(self):
        raise RuntimeError("AutoNodeEvaluationDelayedExecutionQueue is a singleton")

    # --------------------------------------------------------------------------------
    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls.__new__(cls)

    # --------------------------------------------------------------------------------
    @classmethod
    def add_to_queue(cls, callable_fn: Callable):
        cls.instance()._queue.append(callable_fn)  # noqa: PLW0212

    # --------------------------------------------------------------------------------
    @classmethod
    def execute_queue(cls):
        while len(cls.instance()._queue) > 0:  # noqa: PLW0212
            callable_fn = cls.instance()._queue.pop()  # noqa: PLW0212
            callable_fn()
