"""This module provides functionality to evaluate different geometric mesh primitives and retrieve their names."""

__all__ = ["get_geometry_mesh_prim_list", "AbstractShapeEvaluator"]

import re

from .abstract_shape_evaluator import AbstractShapeEvaluator
from .cone import ConeEvaluator
from .disk import DiskEvaluator
from .cube import CubeEvaluator
from .cylinder import CylinderEvaluator
from .sphere import SphereEvaluator
from .torus import TorusEvaluator
from .plane import PlaneEvaluator


_all_evaluators = {}


def _get_all_evaluators():
    global _all_evaluators
    if not _all_evaluators:
        evaluator_classes = list(filter(lambda x: re.search(r".+Evaluator$", x), globals().keys()))
        evaluator_classes.remove(AbstractShapeEvaluator.__name__)
        for evaluator in evaluator_classes:
            name = re.sub(r"(.*)Evaluator$", r"\1", evaluator)
            _all_evaluators[name] = globals()[f"{name}Evaluator"]

    return _all_evaluators


def get_geometry_mesh_prim_list():
    """Returns a sorted list of all available geometry mesh primitive names.

    Returns:
        list of str: Sorted list of geometry mesh primitive names."""
    names = list(_get_all_evaluators().keys())
    names.sort()
    return names
