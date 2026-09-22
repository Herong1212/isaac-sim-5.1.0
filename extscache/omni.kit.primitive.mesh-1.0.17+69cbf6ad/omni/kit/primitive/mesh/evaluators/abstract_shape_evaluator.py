from typing import List, Tuple
from pxr import Gf


class AbstractShapeEvaluator:  # pragma: no cover
    """A base class for evaluating geometric shapes.

    This abstract class serves as a template for creating shape evaluators. Subclasses are expected to implement the `eval` method, which calculates geometric data for a given shape based on provided attributes.

    Args:
        attributes (dict): A dictionary containing shape-specific attributes needed for evaluation."""

    def __init__(self, attributes: dict):
        """Initializes an instance of the AbstractShapeEvaluator."""
        self._attributes = attributes

    def eval(self, **kwargs) -> Tuple[List[Gf.Vec3f], List[Gf.Vec3f], List[Gf.Vec2f], List[int], List[int]]:
        """It must be implemented to return tuple
        [points, normals, uvs, face_indices, face_vertex_counts], where:
        * points and normals are array of Gf.Vec3f.
        * uvs are array of Gf.Vec2f that represents uv coordinates.
        * face_indexes are array of int that represents face indices.
        * face_vertex_counts are array of int that represents vertex count per face.
        * Normals and uvs must be face varying.

        Keyword Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Tuple[List[Gf.Vec3f], List[Gf.Vec3f], List[Gf.Vec2f], List[int], List[int]]: Tuple containing lists of points, normals, uvs, face_indices, and face_vertex_counts.
        """
        raise NotImplementedError("Eval must be implemented for this shape.")

    @staticmethod
    def build_setting_ui():
        """Builds the UI for setting configurations. This method should be implemented by subclasses."""
        pass

    @staticmethod
    def reset_setting():
        """Resets the settings to their default values. This method should be implemented by subclasses."""
        pass

    @staticmethod
    def get_default_half_scale():
        """Returns the default half scale value.

        Returns:
            int: The default half scale value."""
        return 50
