import os
import errno
import numpy as np
from enum import Enum
from typing import Callable, List
import re


class UsdaReader:
    def __init__(self, file_name: str):
        self._file_name = file_name
        self._file = None

    def __enter__(self):
        self._file = open(self._file_name, 'r')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._file:
            self._file.close()

    def get_signature(self) -> int:
        for line in self._file:
            match = re.search(r'mesh:signature\s*=\s*(\d+)', line)
            if match:
                return int(match.group(1))
        return -1

    def get_path_points(self) -> List:
        content = self._file.read()
        pattern = r'def BasisCurves\s+"[^"]+"\s*\{[^}]*?point3f\[\]\s*points\s*=\s*\[(.*?)\]'
        matches = re.findall(pattern.replace('\n', ''), content.replace('\n', ''), re.DOTALL)

        float_values = []
        for point_data in matches:
            point_data = point_data.replace('(', '').replace(')', '')
            tuples = point_data.split('], [')
            for tup in tuples:
                float_values.extend(float(num) for num in tup.split(', '))

        points = [tuple(float_values[i:i + 3]) for i in range(0, len(float_values), 3)]
        return points
