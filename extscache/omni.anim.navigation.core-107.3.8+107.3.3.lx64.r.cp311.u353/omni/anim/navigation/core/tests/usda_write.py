import os
import errno
import numpy as np
from enum import Enum
from typing import Callable, List


FORMAT_LINE_THICKNESS = '{:0.4f}'
FORMAT_VERTEX_COMPONENT = '{:0.4f}'
FORMAT_COLOR_COMPONENT = '{:0.4f}'
INDENT_SPACES = 4


class UsdaVisibility(Enum):
    INVISIBLE = 0
    INHERITED = 1
    UNSPECIFIED = 2

    def is_valid(self) -> bool:
        return self in UsdaVisibility

    def to_usda(self) -> str:
        assert self.is_valid()
        if self == UsdaVisibility.INVISIBLE:
            return 'invisible'
        elif self == UsdaVisibility.INHERITED:
            return 'inherited'
        else:
            return 'unspecified'

    @classmethod
    def from_bool(cls, b: bool) -> 'UsdaVisibility':
        return cls.INHERITED if b else cls.UNSPECIFIED


class UsdaFile:

    @classmethod
    def default_config(cls):
        return {
            'up_axis': (0.0, 1.0, 0.0),
            'forward_axis': (0.0, 0.0, 1.0)
        }

    def __init__(self, file_name: str, cfg={}):
        self._file_name = file_name
        self._file = None
        self._current_indentation = 0
        self._new_line = False
        self._node_id = 0
        self.cfg = cfg
        self.up_axis = cfg.get('up_axis')
        self.up_axis = (0.0, 1.0, 0.0) if self.up_axis is None else tuple(self.up_axis)
        self.forward_axis = cfg.get('forward_axis')
        self.forward_axis = (0.0, 0.0, 1.0) if self.forward_axis is None else tuple(self.forward_axis)

    def __enter__(self):
        self._file = open(self._file_name, 'w')
        self.fprintf('#usda 1.0\n')
        if self.up_axis == (1.0, 0.0, 0.0):
            if self.forward_axis != (0.0, 0.0, 1.0):
                raise Exception()
            self.fprintf('(\n    upAxis = "X"\n)\n')
        elif self.up_axis == (0.0, 1.0, 0.0):
            if self.forward_axis != (0.0, 0.0, 1.0):
                raise Exception()
        else:
            if self.up_axis != (0.0, 0.0, 1.0):
                raise Exception()
            if self.forward_axis != (0.0, 1.0, 0.0):
                raise Exception()
            self.fprintf('(\n    upAxis = "Z"\n)\n')
        self.fprintf('\n')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._file:
            self._file.close()

    @staticmethod
    def format_vertex(v):
        return f'({FORMAT_VERTEX_COMPONENT}, {FORMAT_VERTEX_COMPONENT}, {FORMAT_VERTEX_COMPONENT})'.format(v[0], v[1], v[2])

    @staticmethod
    def format_color(color: int):
        assert (color & 0xFF000000) == 0xFF000000
        return f'({FORMAT_COLOR_COMPONENT}, {FORMAT_COLOR_COMPONENT}, {FORMAT_COLOR_COMPONENT})'.format(
            ((color >> 16) & 255) / 255.0,
            ((color >> 8) & 255) / 255.0,
            (color & 255) / 255.0)

    @staticmethod
    def format_line_thickness(thickness: float):
        assert thickness > 0
        return f'{FORMAT_LINE_THICKNESS}'.format(thickness)

    def fprintf(self, fmt, *args):
        buffer = fmt % args
        lines = buffer.splitlines(True)
        for line in lines:
            push = self._check_indent_push_pop(line)
            self._file.write(f'{self._indent() if self._new_line else ""}{line}')
            self._new_line = line[-1] == '\n'
            if push:
                self._indent_push()

    def new_scope(self, type: str, id_prefix: str, vis: UsdaVisibility = UsdaVisibility.INHERITED):
        class scope:
            def __enter__(s):
                nonlocal self, type, id_prefix, vis
                assert len(id_prefix) > 0
                assert vis.is_valid()
                self.fprintf('def %s "%s_%04d"\n{\n', type, id_prefix, self._node_id)
                self._node_id += 1
                if vis != UsdaVisibility.UNSPECIFIED:
                    self.fprintf('token visibility = "%s"\n', vis.to_usda())

            def __exit__(s, exc_type, exc_value, traceback):
                nonlocal self
                self.fprintf('}\n')
        return scope()

    def new_xform(self, id_prefix: str, vis: UsdaVisibility = UsdaVisibility.INHERITED):
        assert len(id_prefix) > 0
        assert vis.is_valid()
        return self.new_scope('Xform', id_prefix, vis)

    def write_signature(self, signature: int):
        self.fprintf('uint mesh:signature = %d\n', signature)

    def write_verts(self, vertices: List, height_bias: float, prefix: str, verts_per_line: int) -> str:
        c = 0
        for v in vertices:
            self.fprintf(f'{prefix}{UsdaFile.format_vertex((v[0], v[1] + height_bias, v[2]))}')
            c += 1
            prefix = ', ' if c % verts_per_line else ',\n'
        return prefix

    def write_line_list(self, id_prefix: str, line_vert_list: List, color: int, thickness: float = 0.5, vis: UsdaVisibility = UsdaVisibility.INHERITED):
        assert len(id_prefix) > 0
        vert_count = len(line_vert_list)
        assert (vert_count % 2) == 0
        assert (color & 0xFF000000) == 0xFF000000
        assert thickness > 0
        assert vis.is_valid()
        ln = (
            'uniform token basis = "bezier"\n'
            'int[] curveVertexCounts = [2]\n'
            'uniform bool singleSided = 1\n'
            'uniform token type = "linear"\n'
            f'float[] widths = [{UsdaFile.format_line_thickness(thickness)}] ( interpolation = "constant" )\n'
            f'color3f[] primvars:displayColor = [{UsdaFile.format_color(color)}]\n'
            f'point3f[] points = '
        )
        for i in range(0, vert_count, 2):
            with self.new_scope('BasisCurves', id_prefix, vis):
                self.fprintf(
                    f'{ln}[{UsdaFile.format_vertex(line_vert_list[i])}, {UsdaFile.format_vertex(line_vert_list[i + 1])}]\n'
                )

    def write_line_strip(self, id_prefix: str, line_vert_strip: List, color: int, thickness: float = 0.5, vis: UsdaVisibility = UsdaVisibility.INHERITED):
        assert len(id_prefix) > 0
        vert_count = len(line_vert_strip)
        assert vert_count > 1
        assert (color & 0xFF000000) == 0xFF000000
        assert thickness > 0
        assert vis.is_valid()

        points_ln = ''
        for i in range(vert_count):
            if i == 0:
                points_ln += f'{UsdaFile.format_vertex(line_vert_strip[i])}'
            else:
                points_ln += f', {UsdaFile.format_vertex(line_vert_strip[i])}'

        ln = (
            'uniform token basis = "bezier"\n'
            f'int[] curveVertexCounts = [{vert_count}]\n'
            'uniform bool singleSided = 1\n'
            'uniform token type = "linear"\n'
            f'float[] widths = [{UsdaFile.format_line_thickness(thickness)}] ( interpolation = "constant" )\n'
            f'color3f[] primvars:displayColor = [{UsdaFile.format_color(color)}]\n'
            f'point3f[] points = [{points_ln}]\n'
        )

        with self.new_scope('BasisCurves', id_prefix, vis):
            self.fprintf(f'{ln}')

    def write_box(self, id_prefix: str, position, width: float, height: float, color: int, vis: UsdaVisibility = UsdaVisibility.INHERITED):
        assert len(id_prefix) > 0
        assert vis.is_valid()
        y = np.array(self.up_axis)
        z = np.array(self.forward_axis)
        x = np.cross(y, z)
        pos = np.array(position)
        w = width * 0.5
        verts = [
            pos - x * w - z * w,
            pos + x * w - z * w,
            pos - x * w + z * w,
            pos + x * w + z * w,
            pos - x * w + y * height - z * w,
            pos + x * w + y * height - z * w,
            pos - x * w + y * height + z * w,
            pos + x * w + y * height + z * w
        ]
        indices = (
            4, 5, 0, 0, 5, 1,
            5, 7, 1, 1, 7, 3,
            7, 6, 3, 3, 6, 2,
            6, 4, 2, 2, 4, 0,
            6, 7, 4, 4, 7, 5,
            3, 2, 1, 1, 2, 0
        )
        self.write_mesh_polygons_indexed_tri_list(id_prefix, verts, indices, color, 0, vis)

    def write_mesh_polygons_tri_list(self, id_prefix: str, verts: List, color: int, height_bias: float = 0, vis: UsdaVisibility = UsdaVisibility.INHERITED):
        assert len(id_prefix) > 0
        vert_count = len(verts)
        assert (vert_count % 3) == 0
        assert vis.is_valid()

        def get_index(v: int):
            assert v >= 0
            assert v < vert_count
            return v
        self._write_mesh_polygons_indexed_tri_list(id_prefix, verts, int(vert_count / 3), color, height_bias, vis, get_index)

    def write_mesh_polygons_indexed_tri_list(self, id_prefix: str, verts: List, indices: List, color: int, height_bias: float = 0, vis: UsdaVisibility = UsdaVisibility.INHERITED):
        assert len(id_prefix) > 0
        vert_count = len(verts)
        index_count = len(indices)
        assert (index_count % 3) == 0
        assert vis.is_valid()

        def get_index(i):
            assert i >= 0
            assert i < index_count
            v = indices[i]
            assert v >= 0
            assert v < vert_count
            return v

        self._write_mesh_polygons_indexed_tri_list(id_prefix, verts, int(index_count / 3), color, height_bias, vis, get_index)

    def _write_mesh_polygons_indexed_tri_list(self, id_prefix: str, verts: List, tri_count: int, color: int, height_bias: float, vis: UsdaVisibility, get_index: Callable[[int], int]):
        assert len(id_prefix) > 0
        assert (color & 0xFF000000) == 0xFF000000
        assert vis.is_valid()
        vert_count = len(verts)
        if vert_count == 0:
            return
        with self.new_scope('Mesh', id_prefix, vis):
            self.fprintf(
                'uniform bool singleSided = 1\n'
                'int[] faceVertexCounts =')
            prefix = ' [\n'
            for i in range(tri_count):
                self.fprintf(f'{prefix}3')
                prefix = ', ' if (i + 1) % 32 else ',\n'
            self.fprintf(
                '\n]\n'
                'int[] faceVertexIndices =')
            prefix = ' [\n'
            for i in range(tri_count * 3):
                v = get_index(i)
                assert v >= 0
                assert v < vert_count
                self.fprintf(f'{prefix}{v}')
                prefix = ', ' if (i + 1) % 30 else ',\n'
            self.fprintf(
                '\n]\n'
                'point3f[] points =')
            self.write_verts(verts, height_bias, ' [\n', 6)
            self.fprintf(
                '\n]\n'
                f'color3f[] primvars:displayColor = [{UsdaFile.format_color(color)}]\n')

    def _indent_push(self):
        self._current_indentation += 1

    def _indent_pop(self):
        assert self._current_indentation > 0
        self._current_indentation -= 1

    def _check_indent_push_pop(self, s: str) -> bool:
        c1 = s.count('[')
        c2 = s.count(']')
        c3 = s.count('{')
        c4 = s.count('}')
        if c1 < c2 or c3 < c4:
            self._indent_pop()
        return c1 > c2 or c3 > c4

    def _indent(self):
        return f"{' ' * INDENT_SPACES * self._current_indentation}"


def main():
    with UsdaFile('test.usda') as usda:
        with usda.new_xform('Test'):
            usda.write_mesh_polygons_indexed_tri_list(
                'Mesh',
                [(-50, 0, -50), (50, 0, -50), (-50, 0, 50), (50, 0, 50)],
                [0, 2, 1, 1, 2, 3],
                0xFF0000FF)

        with usda.new_xform('Test'):
            usda.write_mesh_polygons_tri_list(
                'Mesh',
                [(-50, 0, -50), (50, 0, -50), (-50, 0, 50), (-50, 0, 50), (50, 0, -50), (50, 0, 50)],
                0xFF0000FF)

        with usda.new_xform('Line'):
            usda.write_line_list('Line', [(-10, 0, 0), (-10, 50, 0), (10, 0, 0), (10, 50, 0)], 0xFFFF0000, .5)

        usda.write_box('Box', 0, 20, 5, 0xFF00FF00)


if __name__ == '__main__':
    main()
