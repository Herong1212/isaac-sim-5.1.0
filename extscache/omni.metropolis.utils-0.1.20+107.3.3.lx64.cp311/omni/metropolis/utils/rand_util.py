import hashlib
import math
import random
from typing import List

from pxr import Gf


# TODO METROPERF-822: Add use comments and consider reorganizing util functions to different util classes
class RandUtil:
    @staticmethod
    def attribute_seed(name, global_seed, user_seed=None):
        """Set random seed based on additional global or user data"""
        seed = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)
        if user_seed is None:
            seed += global_seed
        else:
            seed += user_seed
        random.seed(seed)

    @staticmethod
    def rand_range(a: float, b: float) -> float:
        """Return random number between a and b, inclusive"""
        if b < a:
            a, b = b, a
        return a + (b - a) * random.random()

    @staticmethod
    def rand_range_list(a: List[float], b: List[float]) -> List[float]:
        """Return list of random numbers between a[i] and b[i], inclusive"""
        assert len(a) == len(b)  # keeping it here, there is another check that throws error when calling
        return [RandUtil.rand_range(a[i], b[i]) for i in range(len(a))]

    @staticmethod
    def random_reciprocal(a: float, b: float) -> float:
        return a * b / RandUtil.rand_range(a, b)

    @staticmethod
    def rand_2d() -> Gf.Vec2f:
        """Returns random Vec2f of unit length"""
        theta = RandUtil.rand_range(0, 2 * math.pi)
        return Gf.Vec2f(math.cos(theta), math.sin(theta))

    @staticmethod
    def rand_3d() -> Gf.Vec3f:
        """Returns random Vec3f of unit length"""
        alpha = RandUtil.rand_range(0, 2 * math.pi)
        beta = RandUtil.rand_range(0, 2 * math.pi)
        cos_beta = math.cos(beta)

        return Gf.Vec3f(
            math.cos(alpha) * cos_beta,
            math.sin(alpha) * cos_beta,
            math.sin(beta),
        )

    @staticmethod
    def rand_quatd() -> Gf.Quatd:
        """Returns a random quaternion of type Gf.Quatd"""
        return Gf.Quatd(
            RandUtil.rand_range(-1, 1),
            Gf.Vec3d(RandUtil.rand_3d()),
        ).GetNormalized()

    @staticmethod
    def rand_quatf() -> Gf.Quatf:
        """Returns a random quaternion of type Gf.Quatf"""
        return Gf.Quatf(
            RandUtil.rand_range(-1, 1),
            RandUtil.rand_3d(),
        ).GetNormalized()
