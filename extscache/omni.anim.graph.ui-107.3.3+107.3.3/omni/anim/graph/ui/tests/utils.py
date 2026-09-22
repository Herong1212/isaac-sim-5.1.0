import carb
import math


def convert(v):
    return carb.Float3(v[0], v[1], v[2])


def add(a, b):
    return carb.Float3(a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return carb.Float3(a[0] - b[0], a[1] - b[1], a[2] - b[2])


def length(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def normalize(a, d):
    le = length(a)
    if le > 0.001:
        return carb.Float3(a[0] / le, a[1] / le, a[2] / le)
    else:
        return d


def scale(v, f):
    return carb.Float3(v[0] * f, v[1] * f, v[2] * f)


def lerp(a, b, t):
    return add(a, scale(sub(b, a), t))


def clamp(x, low, high):
    return max(min(x, high), low)
