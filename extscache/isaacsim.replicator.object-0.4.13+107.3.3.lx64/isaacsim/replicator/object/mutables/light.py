from pxr import Gf

from .mutable import Mutable_DEV
from ..utility.misc import CHECK, error, ensured_retrieve, tentative_retrieve
from ..utility.scene import create_or_get_distant_light, create_or_get_dome_light, create_or_get_sphere_light


class Light_DEV(Mutable_DEV):  # noqa
    def __init__(self, name, metadata, scene):
        super().__init__(name)

        with CHECK(f"mutable {name}(light) creation"):
            subtype = ensured_retrieve("subtype", metadata, str)
            if subtype == "dome":
                self.prim = create_or_get_dome_light(f"/World/Lights/dome_light_{name}")
            elif subtype == "distant":
                self.prim = create_or_get_distant_light(f"/World/Lights/distant_light_{name}")
            elif subtype == "sphere":
                self.prim = create_or_get_sphere_light(f"/World/Lights/sphere_light_{name}")
            else:
                error(f"unrecognized light type {subtype}")
            self.initialize_prim(metadata, scene)

    def step(self, metadata):
        super().step(metadata)
        intensity = tentative_retrieve("intensity", metadata, (float, int), 1000)
        self.prim.GetAttribute("inputs:intensity").Set(intensity)

        texture_path = tentative_retrieve("texture_path", metadata, str, None)
        if texture_path is not None:
            self.prim.GetAttribute("inputs:texture:file").Set(texture_path)

        color = tentative_retrieve("color", metadata, list, None)
        if color is not None:
            self.prim.GetAttribute("inputs:color").Set(Gf.Vec3f(color))
