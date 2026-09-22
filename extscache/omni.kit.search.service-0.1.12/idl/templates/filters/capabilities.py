from typing import Optional, Dict

from idl.schema import ConstSchema
from idl.spec import Spec
from functools import partial


def include(spec: Spec):
    return {
        "capabilities.find": partial(find_capabilities, consts=spec.consts)
    }


def find_capabilities(interface_name: str, side: str, consts: Dict[str, ConstSchema]) -> Optional[ConstSchema]:
    if side == "server":
        capabilities_name = f"{interface_name}ServerLocalCapabilities"
    else:
        capabilities_name = f"{interface_name}ClientLocalCapabilities"
    return consts.get(capabilities_name)

