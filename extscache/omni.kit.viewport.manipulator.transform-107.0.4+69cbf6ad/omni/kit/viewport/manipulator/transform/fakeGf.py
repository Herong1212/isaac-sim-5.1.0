import math
from usdrt import Gf

def GfRotation(axis0, angle):
    axis = Gf.Vec3d(axis0[0], axis0[1], axis0[2]).GetNormalized()
    quat = Gf.Quatd()

    s = math.sin(math.radians (angle*0.5 ) )
    qx = axis[0] * s
    qy = axis[1] * s
    qz = axis[2] * s
    qw = math.cos( math.radians (angle/2) )

    i = Gf.Vec3d(qx, qy, qz)
    quat.SetReal(qw)
    quat.SetImaginary(i)
    return quat
