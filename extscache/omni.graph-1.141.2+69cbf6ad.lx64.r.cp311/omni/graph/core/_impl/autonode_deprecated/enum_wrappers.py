from typing import Dict, Iterable, OrderedDict, Tuple

import carb

from .type_definitions import AutoNodeDefinitionGenerator, AutoNodeDefinitionWrapper
from .util import GeneratedCode


# ================================================================================
class OgnEnumExecutionWrapper:
    def __init_subclass__(cls, target_class: type) -> None:
        cls.target_class = target_class
        cls.member_names = list(target_class.__members__)
        cls.generate_compute()

    @classmethod
    def generate_compute(cls):
        code = GeneratedCode()
        code.line("from .type_definitions import TypeRegistry")
        code.line("@classmethod")
        with code.indent("def compute(*args):"):
            code.line("cls = args[0]")
            code.line("db = args[1]")
            with code.indent("if not db.inputs.exec:"):
                code.line("return True")
            code.line("input = db.inputs.enum")
            code.line("value = TypeRegistry.remove_from_graph(input).value")
            for name in cls.member_names:
                code.line(f"db.outputs.{name} = bool(value == cls.target_class.{name})")
            code.line("return True")

            carb.log_verbose(f"Generated code for {cls.target_class}:\n{str(code)}")
            exec(str(code), globals())  # noqa: PLW0122
            cls.compute = compute  # noqa: F821, PLE0602, Defined in exec() code


# ================================================================================
class OgnEnumWrapper(AutoNodeDefinitionWrapper):
    """Wrapper around Enums"""

    def __init__(self, target_class, unique_name: str, module_name: str, *, ui_name: str = None):
        super().__init__()
        self.target_class = target_class
        self.unique_name = unique_name
        self.ui_name = ui_name or target_class.__name__
        self.module_name = module_name
        self.descriptor: Dict = {}
        self.descriptor["uiName"] = ui_name
        self.descriptor["version"] = 1
        self.descriptor["language"] = "Python"
        self.descriptor["description"] = f"Enum Wrapper for {self.ui_name}"
        self.descriptor["inputs"] = OrderedDict(
            {
                "enum": {
                    "uiName": "Input",
                    "description": "Enum input",
                    "type": "objectId",
                    "default": 0,
                    "metadata": {"python_type_desc": self.unique_name},
                },
                "exec": {"uiName": "Exec", "description": "Execution input", "type": "execution", "default": 0},
            }
        )

        def signature(name):
            return {"uiName": name, "description": f"Execute on {name}", "type": "execution", "default": 0}

        self.descriptor["outputs"] = OrderedDict({name: signature(name) for name in self.target_class.__members__})

    # --------------------------------------------------------------------------------
    def get_unique_name(self) -> str:
        return self.unique_name

    # --------------------------------------------------------------------------------
    def get_module_name(self) -> str:
        return self.module_name

    # --------------------------------------------------------------------------------
    def get_node_impl(self):
        class OgnEnumReturnType(OgnEnumExecutionWrapper, target_class=self.target_class):
            pass

        return OgnEnumReturnType

    # --------------------------------------------------------------------------------
    def get_ogn(self) -> Dict:
        d = {self.unique_name: self.descriptor}
        return d


# ================================================================================
class EnumAutoNodeDefinitionGenerator(AutoNodeDefinitionGenerator):

    _name = "Enum"

    # --------------------------------------------------------------------------------
    @classmethod
    def generate_from_definitions(  # noqa: PLW0221
        cls, target_type: type, type_name_sanitized: str, type_name_short: str, module_name: str
    ) -> Tuple[Iterable[AutoNodeDefinitionWrapper], Iterable[str]]:

        members_covered = set()
        returned_generators = set()

        if hasattr(target_type, "__members__"):
            ret = OgnEnumWrapper(
                target_type,
                unique_name=type_name_sanitized,
                module_name=module_name,
                ui_name=f"Switch on {type_name_short}",
            )

            members_covered.update(target_type.__members__)
            returned_generators.add(ret)

        return returned_generators, members_covered
