import sys

print("Python Version: {}".format(sys.version))

from pxr import Usd, UsdGeom
import omni.usd
import random

stage = omni.usd.get_context().get_stage()


def rand_col():
    return random.uniform(0.0, 1.0)


def rand_p():
    return random.randint(-100, 100)


def spawn(path):
    xformPrim = UsdGeom.Xform.Define(stage, path)
    sphere = UsdGeom.Sphere.Define(stage, path + "/sphere")

    def set_translate(prim, value):
        component = prim.AddXformOp(UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.PrecisionFloat)
        component.Set(value)
        return component

    colorAttr = UsdGeom.Gprim.Get(stage, path + "/sphere").GetDisplayColorAttr()
    colorAttr.Set([(rand_col(), rand_col(), rand_col())])

    radiusAttr = sphere.GetPrim().GetAttribute("radius")
    radiusAttr.Set(random.randint(1, 21))

    set_translate(sphere, (rand_p(), rand_p(), rand_p()))


spawn("/obj" + str(random.randint(1, 1000000)))
