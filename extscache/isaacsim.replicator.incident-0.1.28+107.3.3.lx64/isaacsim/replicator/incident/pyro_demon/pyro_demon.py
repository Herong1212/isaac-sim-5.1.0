import omni
import os
import omni.kit.commands

from pxr import Gf


class PyroDemon:
    def __init__(self):
        omni.kit.commands.execute("FlowCreatePrim", prim_path="/World/flowSimulate", type_name="FlowSimulate")
        stage = omni.usd.get_context().get_stage()
        parent_prim = stage.DefinePrim("/World/PyroDemonSettings", "Xform")
        file_path = os.path.join(os.path.dirname(__file__), "assets", "warehouse_fire_settings.usda")
        parent_prim.GetReferences().AddReference(file_path)

        # sphere_emitter = FlowEmitterSphere.Define(stage, "/World/PyroDemonEmitters/SphereEmitter")
        result, prim = omni.kit.commands.execute(
            "FlowCreatePrim", prim_path="/World/flowSimulate", type_name="FlowEmitterBox"
        )
        if not result:
            print("Failed to create FlowEmitterBox")
            return

        half_size_attr = prim.GetAttribute("halfSize")
        if half_size_attr:
            print("half size: ", half_size_attr.Get())
            half_size_attr.Set(Gf.Vec3f(3.14, 3.14, 3.14))
        else:
            print("half size attr not found")
