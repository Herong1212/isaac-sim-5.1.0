import os
import omni.kit.test
import omni.graph.core as og
import omni.graph.core.tests as ogts
from omni.graph.core.tests.omnigraph_test_utils import _TestGraphAndNode
from omni.graph.core.tests.omnigraph_test_utils import _test_clear_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_setup_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_verify_scene


class TestOgn(ogts.OmniGraphTestCase):

    TEST_DATA = [
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 10}, False],
                    ['inputs:b', {'type': 'double', 'value': 6}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double', 'value': 16}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 10}, False],
                    ['inputs:b', {'type': 'float', 'value': 6}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float', 'value': 16}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 10}, False],
                    ['inputs:b', {'type': 'half', 'value': 6}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half', 'value': 16}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 10}, False],
                    ['inputs:b', {'type': 'int', 'value': 6}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int', 'value': 16}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int64', 'value': 10}, False],
                    ['inputs:b', {'type': 'int64', 'value': 6}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int64', 'value': 16}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uchar', 'value': 10}, False],
                    ['inputs:b', {'type': 'uchar', 'value': 6}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'uchar', 'value': 16}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint', 'value': 10}, False],
                    ['inputs:b', {'type': 'uint', 'value': 6}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'uint', 'value': 16}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint64', 'value': 10}, False],
                    ['inputs:b', {'type': 'uint64', 'value': 6}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'uint64', 'value': 16}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 10}, False],
                    ['inputs:b', {'type': 'double[]', 'value': [6, 12]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[]', 'value': [16, 22]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 10}, False],
                    ['inputs:b', {'type': 'float[]', 'value': [6, 12]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[]', 'value': [16, 22]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 10}, False],
                    ['inputs:b', {'type': 'half[]', 'value': [6, 12]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[]', 'value': [16, 22]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 10}, False],
                    ['inputs:b', {'type': 'int[]', 'value': [6, 12]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[]', 'value': [16, 22]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int64', 'value': 10}, False],
                    ['inputs:b', {'type': 'int64[]', 'value': [6, 12]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int64[]', 'value': [16, 22]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uchar', 'value': 10}, False],
                    ['inputs:b', {'type': 'uchar[]', 'value': [6, 12]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'uchar[]', 'value': [16, 22]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint', 'value': 10}, False],
                    ['inputs:b', {'type': 'uint[]', 'value': [6, 12]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'uint[]', 'value': [16, 22]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint64', 'value': 10}, False],
                    ['inputs:b', {'type': 'uint64[]', 'value': [6, 12]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'uint64[]', 'value': [16, 22]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [6, 12]}, False],
                    ['inputs:b', {'type': 'double[]', 'value': [10, 23]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[]', 'value': [16, 35]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[]', 'value': [6, 12]}, False],
                    ['inputs:b', {'type': 'float[]', 'value': [10, 23]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[]', 'value': [16, 35]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[]', 'value': [6, 12]}, False],
                    ['inputs:b', {'type': 'half[]', 'value': [10, 23]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[]', 'value': [16, 35]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[]', 'value': [6, 12]}, False],
                    ['inputs:b', {'type': 'int[]', 'value': [10, 23]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[]', 'value': [16, 35]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int64[]', 'value': [6, 12]}, False],
                    ['inputs:b', {'type': 'int64[]', 'value': [10, 23]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int64[]', 'value': [16, 35]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uchar[]', 'value': [6, 12]}, False],
                    ['inputs:b', {'type': 'uchar[]', 'value': [10, 23]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'uchar[]', 'value': [16, 35]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint[]', 'value': [6, 12]}, False],
                    ['inputs:b', {'type': 'uint[]', 'value': [10, 23]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'uint[]', 'value': [16, 35]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint64[]', 'value': [6, 12]}, False],
                    ['inputs:b', {'type': 'uint64[]', 'value': [10, 23]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'uint64[]', 'value': [16, 35]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[2]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'double[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[2]', 'value': [4, 6]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[3]', 'value': [1, 2, 3]}, False],
                    ['inputs:b', {'type': 'double[3]', 'value': [4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[3]', 'value': [5, 7, 9]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[4]', 'value': [1, 2, 3, 4]}, False],
                    ['inputs:b', {'type': 'double[4]', 'value': [5, 6, 7, 8]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[4]', 'value': [6, 8, 10, 12]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'matrixd[2]', 'value': [2, 2, 2, 2]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[2]', 'value': [3, 3, 3, 3]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[3]', 'value': [1, 1, 1, 1, 1, 1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'matrixd[3]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[3]', 'value': [3, 3, 3, 3, 3, 3, 3, 3, 3]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[4]', 'value': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'matrixd[4]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[4]', 'value': [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[2]', 'value': [1.0, 2.0]}, False],
                    ['inputs:b', {'type': 'float[2]', 'value': [0.5, 1.0]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[2]', 'value': [1.5, 3.0]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[3]', 'value': [1, 2, 3]}, False],
                    ['inputs:b', {'type': 'float[3]', 'value': [4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[3]', 'value': [5, 7, 9]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[4]', 'value': [1, 2, 3, 4]}, False],
                    ['inputs:b', {'type': 'float[4]', 'value': [5, 6, 7, 8]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[4]', 'value': [6, 8, 10, 12]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[2]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'half[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[2]', 'value': [4, 6]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[3]', 'value': [1, 2, 3]}, False],
                    ['inputs:b', {'type': 'half[3]', 'value': [4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[3]', 'value': [5, 7, 9]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[4]', 'value': [1, 2, 3, 4]}, False],
                    ['inputs:b', {'type': 'half[4]', 'value': [5, 6, 7, 8]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[4]', 'value': [6, 8, 10, 12]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[2]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[2]', 'value': [4, 6]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[3]', 'value': [1, 2, 3]}, False],
                    ['inputs:b', {'type': 'int[3]', 'value': [4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[3]', 'value': [5, 7, 9]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[4]', 'value': [1, 2, 3, 4]}, False],
                    ['inputs:b', {'type': 'int[4]', 'value': [5, 6, 7, 8]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[4]', 'value': [6, 8, 10, 12]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[2][]', 'value': [[10, 5], [1, 1]]}, False],
                    ['inputs:b', {'type': 'double[2]', 'value': [5, 5]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[2][]', 'value': [[15, 10], [6, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[3]', 'value': [4, 5, 6]}, False],
                    ['inputs:b', {'type': 'double[3][]', 'value': [[1, 2, 3]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[3][]', 'value': [[5, 7, 9]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[4]', 'value': [5, 6, 7, 8]}, False],
                    ['inputs:b', {'type': 'double[4][]', 'value': [[1, 2, 3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[4][]', 'value': [[6, 8, 10, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2]', 'value': [2, 2, 2, 2]}, False],
                    ['inputs:b', {'type': 'matrixd[2][]', 'value': [[1, 1, 1, 1]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[2][]', 'value': [[3, 3, 3, 3]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[3]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                    ['inputs:b', {'type': 'matrixd[3][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[3][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[4]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                    ['inputs:b', {'type': 'matrixd[4][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[4][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[2]', 'value': [3, 4]}, False],
                    ['inputs:b', {'type': 'float[2][]', 'value': [[1, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[2][]', 'value': [[4, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[3]', 'value': [4, 5, 6]}, False],
                    ['inputs:b', {'type': 'float[3][]', 'value': [[1, 2, 3]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[3][]', 'value': [[5, 7, 9]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[4]', 'value': [5, 6, 7, 8]}, False],
                    ['inputs:b', {'type': 'float[4][]', 'value': [[1, 2, 3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[4][]', 'value': [[6, 8, 10, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[2]', 'value': [3, 4]}, False],
                    ['inputs:b', {'type': 'half[2][]', 'value': [[1, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[2][]', 'value': [[4, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[3]', 'value': [4, 5, 6]}, False],
                    ['inputs:b', {'type': 'half[3][]', 'value': [[1, 2, 3]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[3][]', 'value': [[5, 7, 9]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[4]', 'value': [5, 6, 7, 8]}, False],
                    ['inputs:b', {'type': 'half[4][]', 'value': [[1, 2, 3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[4][]', 'value': [[6, 8, 10, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[2]', 'value': [3, 4]}, False],
                    ['inputs:b', {'type': 'int[2][]', 'value': [[1, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[2][]', 'value': [[4, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[3]', 'value': [4, 5, 6]}, False],
                    ['inputs:b', {'type': 'int[3][]', 'value': [[1, 2, 3]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[3][]', 'value': [[5, 7, 9]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[4]', 'value': [5, 6, 7, 8]}, False],
                    ['inputs:b', {'type': 'int[4][]', 'value': [[1, 2, 3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[4][]', 'value': [[6, 8, 10, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[2][]', 'value': [[3, 4]]}, False],
                    ['inputs:b', {'type': 'double[2][]', 'value': [[1, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[2][]', 'value': [[4, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[3][]', 'value': [[4, 5, 6]]}, False],
                    ['inputs:b', {'type': 'double[3][]', 'value': [[1, 2, 3]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[3][]', 'value': [[5, 7, 9]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[4][]', 'value': [[5, 6, 7, 8]]}, False],
                    ['inputs:b', {'type': 'double[4][]', 'value': [[1, 2, 3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[4][]', 'value': [[6, 8, 10, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2][]', 'value': [[2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'matrixd[2][]', 'value': [[1, 1, 1, 1]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[2][]', 'value': [[3, 3, 3, 3]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[3][]', 'value': [[2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'matrixd[3][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[3][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[4][]', 'value': [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'matrixd[4][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[4][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[2][]', 'value': [[3, 4]]}, False],
                    ['inputs:b', {'type': 'float[2][]', 'value': [[1, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[2][]', 'value': [[4, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[3][]', 'value': [[4, 5, 6]]}, False],
                    ['inputs:b', {'type': 'float[3][]', 'value': [[1, 2, 3]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[3][]', 'value': [[5, 7, 9]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[4][]', 'value': [[5, 6, 7, 8]]}, False],
                    ['inputs:b', {'type': 'float[4][]', 'value': [[1, 2, 3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[4][]', 'value': [[6, 8, 10, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[2][]', 'value': [[3, 4]]}, False],
                    ['inputs:b', {'type': 'half[2][]', 'value': [[1, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[2][]', 'value': [[4, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[3][]', 'value': [[4, 5, 6]]}, False],
                    ['inputs:b', {'type': 'half[3][]', 'value': [[1, 2, 3]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[3][]', 'value': [[5, 7, 9]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[4][]', 'value': [[5, 6, 7, 8]]}, False],
                    ['inputs:b', {'type': 'half[4][]', 'value': [[1, 2, 3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[4][]', 'value': [[6, 8, 10, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[2][]', 'value': [[3, 4]]}, False],
                    ['inputs:b', {'type': 'int[2][]', 'value': [[1, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[2][]', 'value': [[4, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[3][]', 'value': [[4, 5, 6]]}, False],
                    ['inputs:b', {'type': 'int[3][]', 'value': [[1, 2, 3]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[3][]', 'value': [[5, 7, 9]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[4][]', 'value': [[5, 6, 7, 8]]}, False],
                    ['inputs:b', {'type': 'int[4][]', 'value': [[1, 2, 3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[4][]', 'value': [[6, 8, 10, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 8}, False],
                    ['inputs:b', {'type': 'double[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[2]', 'value': [11, 12]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 8}, False],
                    ['inputs:b', {'type': 'double[3]', 'value': [4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[3]', 'value': [12, 13, 14]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 8}, False],
                    ['inputs:b', {'type': 'double[4]', 'value': [5, 6, 7, 8]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[4]', 'value': [13, 14, 15, 16]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2]', 'value': [2, 2, 2, 2]}, False],
                    ['inputs:b', {'type': 'double', 'value': 8}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[2]', 'value': [10, 10, 10, 10]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 8}, False],
                    ['inputs:b', {'type': 'matrixd[3]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[3]', 'value': [10, 10, 10, 10, 10, 10, 10, 10, 10]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 8}, False],
                    ['inputs:b', {'type': 'matrixd[4]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[4]', 'value': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 8}, False],
                    ['inputs:b', {'type': 'float[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[2]', 'value': [11, 12]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 8}, False],
                    ['inputs:b', {'type': 'float[3]', 'value': [4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[3]', 'value': [12, 13, 14]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 8}, False],
                    ['inputs:b', {'type': 'float[4]', 'value': [5, 6, 7, 8]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[4]', 'value': [13, 14, 15, 16]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 8}, False],
                    ['inputs:b', {'type': 'half[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[2]', 'value': [11, 12]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 8}, False],
                    ['inputs:b', {'type': 'half[3]', 'value': [4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[3]', 'value': [12, 13, 14]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 8}, False],
                    ['inputs:b', {'type': 'half[4]', 'value': [5, 6, 7, 8]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[4]', 'value': [13, 14, 15, 16]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 8}, False],
                    ['inputs:b', {'type': 'int[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[2]', 'value': [11, 12]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 8}, False],
                    ['inputs:b', {'type': 'int[3]', 'value': [4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[3]', 'value': [12, 13, 14]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 8}, False],
                    ['inputs:b', {'type': 'int[4]', 'value': [5, 6, 7, 8]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[4]', 'value': [13, 14, 15, 16]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[2][]', 'value': [[10, 5], [1, 1]]}, False],
                    ['inputs:b', {'type': 'double', 'value': 5}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[2][]', 'value': [[15, 10], [6, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 8}, False],
                    ['inputs:b', {'type': 'double[3][]', 'value': [[4, 5, 6]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[3][]', 'value': [[12, 13, 14]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 8}, False],
                    ['inputs:b', {'type': 'double[4][]', 'value': [[5, 6, 7, 8]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[4][]', 'value': [[13, 14, 15, 16]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2][]', 'value': [[2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'double', 'value': 8}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[2][]', 'value': [[10, 10, 10, 10]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 8}, False],
                    ['inputs:b', {'type': 'matrixd[3][]', 'value': [[2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[3][]', 'value': [[10, 10, 10, 10, 10, 10, 10, 10, 10]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 8}, False],
                    ['inputs:b', {'type': 'matrixd[4][]', 'value': [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[4][]', 'value': [[10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 8}, False],
                    ['inputs:b', {'type': 'float[2][]', 'value': [[3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[2][]', 'value': [[11, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 8}, False],
                    ['inputs:b', {'type': 'float[3][]', 'value': [[4, 5, 6]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[3][]', 'value': [[12, 13, 14]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 8}, False],
                    ['inputs:b', {'type': 'float[4][]', 'value': [[5, 6, 7, 8]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[4][]', 'value': [[13, 14, 15, 16]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 8}, False],
                    ['inputs:b', {'type': 'half[2][]', 'value': [[3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[2][]', 'value': [[11, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 8}, False],
                    ['inputs:b', {'type': 'half[3][]', 'value': [[4, 5, 6]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[3][]', 'value': [[12, 13, 14]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 8}, False],
                    ['inputs:b', {'type': 'half[4][]', 'value': [[5, 6, 7, 8]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[4][]', 'value': [[13, 14, 15, 16]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 8}, False],
                    ['inputs:b', {'type': 'int[2][]', 'value': [[3, 4]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[2][]', 'value': [[11, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 8}, False],
                    ['inputs:b', {'type': 'int[3][]', 'value': [[4, 5, 6]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[3][]', 'value': [[12, 13, 14]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 8}, False],
                    ['inputs:b', {'type': 'int[4][]', 'value': [[5, 6, 7, 8]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[4][]', 'value': [[13, 14, 15, 16]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'double[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[2][]', 'value': [[4, 5], [5, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'double[3]', 'value': [3, 4, 5]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[3][]', 'value': [[4, 5, 6], [5, 6, 7]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'double[4]', 'value': [3, 4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[4][]', 'value': [[4, 5, 6, 7], [5, 6, 7, 8]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2]', 'value': [2, 2, 2, 2]}, False],
                    ['inputs:b', {'type': 'double[]', 'value': [1, 2]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[2][]', 'value': [[3, 3, 3, 3], [4, 4, 4, 4]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'matrixd[3]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[3][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3], [4, 4, 4, 4, 4, 4, 4, 4, 4]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'matrixd[4]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[4][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'float[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[2][]', 'value': [[4, 5], [5, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'float[3]', 'value': [3, 4, 5]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[3][]', 'value': [[4, 5, 6], [5, 6, 7]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'float[4]', 'value': [3, 4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[4][]', 'value': [[4, 5, 6, 7], [5, 6, 7, 8]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'half[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[2][]', 'value': [[4, 5], [5, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'half[3]', 'value': [3, 4, 5]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[3][]', 'value': [[4, 5, 6], [5, 6, 7]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'half[4]', 'value': [3, 4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[4][]', 'value': [[4, 5, 6, 7], [5, 6, 7, 8]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int[2]', 'value': [3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[2][]', 'value': [[4, 5], [5, 6]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int[3]', 'value': [3, 4, 5]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[3][]', 'value': [[4, 5, 6], [5, 6, 7]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int[4]', 'value': [3, 4, 5, 6]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[4][]', 'value': [[4, 5, 6, 7], [5, 6, 7, 8]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'double[2][]', 'value': [[3, 4], [5, 6]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[2][]', 'value': [[4, 5], [7, 8]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'double[3][]', 'value': [[3, 4, 5], [6, 7, 8]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[3][]', 'value': [[4, 5, 6], [8, 9, 10]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'double[4][]', 'value': [[3, 4, 5, 6], [7, 8, 9, 10]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'double[4][]', 'value': [[4, 5, 6, 7], [9, 10, 11, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2][]', 'value': [[2, 2, 2, 2], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'double[]', 'value': [1, 2]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[2][]', 'value': [[3, 3, 3, 3], [4, 4, 4, 4]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'matrixd[3][]', 'value': [[2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[3][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3], [4, 4, 4, 4, 4, 4, 4, 4, 4]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'matrixd[4][]', 'value': [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'matrixd[4][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'float[2][]', 'value': [[3, 4], [5, 6]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[2][]', 'value': [[4, 5], [7, 8]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'float[3][]', 'value': [[3, 4, 5], [6, 7, 8]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[3][]', 'value': [[4, 5, 6], [8, 9, 10]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'float[4][]', 'value': [[3, 4, 5, 6], [7, 8, 9, 10]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'float[4][]', 'value': [[4, 5, 6, 7], [9, 10, 11, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'half[2][]', 'value': [[3, 4], [5, 6]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[2][]', 'value': [[4, 5], [7, 8]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'half[3][]', 'value': [[3, 4, 5], [6, 7, 8]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[3][]', 'value': [[4, 5, 6], [8, 9, 10]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'half[4][]', 'value': [[3, 4, 5, 6], [7, 8, 9, 10]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'half[4][]', 'value': [[4, 5, 6, 7], [9, 10, 11, 12]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int[2][]', 'value': [[3, 4], [5, 6]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[2][]', 'value': [[4, 5], [7, 8]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int[3][]', 'value': [[3, 4, 5], [6, 7, 8]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[3][]', 'value': [[4, 5, 6], [8, 9, 10]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int[4][]', 'value': [[3, 4, 5, 6], [7, 8, 9, 10]]}, False],
                ],
                'outputs': [
                    ['outputs:sum', {'type': 'int[4][]', 'value': [[4, 5, 6, 7], [9, 10, 11, 12]]}, False],
                ],
            },
        },
    ]

    test_cap = os.getenv("OGN_GENERATED_TEST_LIMIT")
    if test_cap is not None:  # pragma: no cover
        TEST_DATA = TEST_DATA[0: int(test_cap)]

    async def test_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_Add", "omni.graph.nodes.Add", test_run, _TestGraphAndNode())
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.Add User test case #{i+1}")

    async def test_vectorized_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_Add","omni.graph.nodes.Add", test_run, _TestGraphAndNode(), 16)
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.Add User test case #{i+1}", 16)

    async def test_thread_safety(self):
        import omni.kit
        # Generate multiple instances of the test setup to run them concurrently
        instance_setup = dict()
        for n in range(24):
            instance_setup[f"/TestGraph_{n}"] = _TestGraphAndNode()

        valid_test_runs = self.TEST_DATA

        # Build a map of test graph to setup data
        test_data_setup = {}
        idx = 0
        for n in range(24):
            test_data_setup[f"/TestGraph_{n}"] = valid_test_runs[idx]
            idx = (idx + 1) % len(valid_test_runs)

        await omni.usd.get_context().new_stage_async()
        for (key, test_info) in instance_setup.copy().items():
            instance_setup[key] = await _test_setup_scene(self, og.Controller(allow_exists_prim=True), key, "TestNode_omni_graph_nodes_Add", "omni.graph.nodes.Add", test_data_setup[key], test_info)
        self.assertEqual(len(og.get_all_graphs()), 24)

        # We want to evaluate all graphs concurrently. Kick them all.
        # Evaluate multiple times to skip 2 serial frames and increase chances for a race condition.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        for (key, test_info) in instance_setup.items():
            _test_verify_scene(self, og.Controller(), test_data_setup[key], test_info, f"omni.graph.nodes.Add User test case instance{key}")

    async def test_data_access(self):
        test_file_name = "OgnAddTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_nodes_Add")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 2)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"

