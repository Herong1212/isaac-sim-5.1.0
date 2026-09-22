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
                    ['inputs:a', {'type': 'bool', 'value': True}, False],
                    ['inputs:b', {'type': 'bool', 'value': False}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'bool', 'value': True}, False],
                    ['inputs:b', {'type': 'bool[]', 'value': [True, False]}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'bool[]', 'value': [True, False]}, False],
                    ['inputs:b', {'type': 'bool', 'value': True}, False],
                    ['inputs:operation', "!=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'bool[]', 'value': [True, False]}, False],
                    ['inputs:b', {'type': 'bool[]', 'value': [True, False]}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 1}, False],
                    ['inputs:b', {'type': 'double', 'value': 2}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double', 'value': 1}, False],
                    ['inputs:b', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'double', 'value': 1}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[]', 'value': [2.0, 3.0]}, False],
                    ['inputs:b', {'type': 'double[]', 'value': [2.0, 3.1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 42.0}, False],
                    ['inputs:b', {'type': 'float', 'value': 1.0}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': True}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 42.0}, False],
                    ['inputs:b', {'type': 'float', 'value': 1.0}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float', 'value': 1}, False],
                    ['inputs:b', {'type': 'float[]', 'value': [1, 2]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'float', 'value': 1}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[]', 'value': [1.0, 2.0]}, False],
                    ['inputs:b', {'type': 'float[]', 'value': [1.0, 2.01]}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 1}, False],
                    ['inputs:b', {'type': 'half', 'value': 2}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half', 'value': 1}, False],
                    ['inputs:b', {'type': 'half[]', 'value': [1, 2]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'half', 'value': 1}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'half[]', 'value': [3, 0]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 1}, False],
                    ['inputs:b', {'type': 'int', 'value': 2}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int', 'value': 1}, False],
                    ['inputs:b', {'type': 'int[]', 'value': [1, 2]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int', 'value': 1}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int[]', 'value': [3, 0]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int64', 'value': 9223372036854775807}, False],
                    ['inputs:b', {'type': 'int64', 'value': 9223372036854775807}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': True}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int64', 'value': 1}, False],
                    ['inputs:b', {'type': 'int64[]', 'value': [1, 2]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int64[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int64', 'value': 1}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int64[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'int64[]', 'value': [3, 0]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'token', 'value': ''}, False],
                    ['inputs:b', {'type': 'token', 'value': ''}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': True}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'token', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'token', 'value': 'abc'}, False],
                    ['inputs:operation', "!=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'token', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'token', 'value': 'd'}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'token', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'token', 'value': ''}, False],
                    ['inputs:operation', "!=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': True}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'token', 'value': ''}, False],
                    ['inputs:b', {'type': 'token[]', 'value': ['abc', 'a', '']}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'token[]', 'value': ['abc', 'a', '']}, False],
                    ['inputs:b', {'type': 'token', 'value': 'a'}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'token[]', 'value': ['abcd', 'a', 'foo']}, False],
                    ['inputs:b', {'type': 'token[]', 'value': ['abc', 'a', 'food']}, False],
                    ['inputs:operation', "!=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': ''}, False],
                    ['inputs:b', {'type': 'string', 'value': ''}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': True}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:operation', "!=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'string', 'value': 'd'}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'string', 'value': ''}, False],
                    ['inputs:operation', "!=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': True}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': ''}, False],
                    ['inputs:b', {'type': 'string', 'value': ''}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'string', 'value': 'ad'}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': True}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'string', 'value': ''}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': True}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': True}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'uchar[]', 'value': [97, 98, 99]}, False],
                    ['inputs:operation', "!=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, False, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uchar[]', 'value': [97, 98, 99]}, False],
                    ['inputs:b', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, True, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uchar', 'value': 98}, False],
                    ['inputs:b', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'string', 'value': 'abc'}, False],
                    ['inputs:b', {'type': 'uchar', 'value': 98}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uchar', 'value': 1}, False],
                    ['inputs:b', {'type': 'uchar', 'value': 2}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uchar', 'value': 1}, False],
                    ['inputs:b', {'type': 'uchar[]', 'value': [1, 2]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uchar[]', 'value': [97, 98, 99]}, False],
                    ['inputs:b', {'type': 'uchar', 'value': 98}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uchar[]', 'value': []}, False],
                    ['inputs:b', {'type': 'uchar[]', 'value': []}, False],
                    ['inputs:operation', "==", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': []}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint', 'value': 1}, False],
                    ['inputs:b', {'type': 'uint', 'value': 2}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint', 'value': 1}, False],
                    ['inputs:b', {'type': 'uint[]', 'value': [1, 2]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'uint', 'value': 1}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'uint[]', 'value': [3, 0]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint64', 'value': 1}, False],
                    ['inputs:b', {'type': 'uint64', 'value': 2}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint64', 'value': 1}, False],
                    ['inputs:b', {'type': 'uint64[]', 'value': [1, 2]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint64[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'uint64', 'value': 1}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'uint64[]', 'value': [1, 2]}, False],
                    ['inputs:b', {'type': 'uint64[]', 'value': [3, 0]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[2]', 'value': [1, 1]}, False],
                    ['inputs:b', {'type': 'double[2]', 'value': [2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[2]', 'value': [1, 1]}, False],
                    ['inputs:b', {'type': 'double[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:b', {'type': 'double[2]', 'value': [1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:b', {'type': 'double[2][]', 'value': [[3, 3], [0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:b', {'type': 'double[3]', 'value': [2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:b', {'type': 'double[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'double[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[3][]', 'value': [[2.0, 3.0, 1.0], [1.0, 2.0, 5.0]]}, False],
                    ['inputs:b', {'type': 'double[3][]', 'value': [[2.0, 1.0, 4.0], [2.0, 2.0, 2.0]]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'double[4]', 'value': [2, 2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'double[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'double[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'double[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'double[4][]', 'value': [[3, 3, 3, 3], [0, 0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'matrixd[2]', 'value': [2, 2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'matrixd[2][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'matrixd[2]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[2][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'matrixd[2][]', 'value': [[3, 3, 3, 3], [0, 0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[3]', 'value': [1, 1, 1, 1, 1, 1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'matrixd[3]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[3]', 'value': [1, 1, 1, 1, 1, 1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'matrixd[3][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[3][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'matrixd[3]', 'value': [1, 1, 1, 1, 1, 1, 1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[3][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'matrixd[3][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3], [0, 0, 0, 0, 0, 0, 0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[4]', 'value': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'matrixd[4]', 'value': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[4]', 'value': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'matrixd[4][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[4][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'matrixd[4]', 'value': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'matrixd[4][]', 'value': [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'matrixd[4][]', 'value': [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[2]', 'value': [1, 1]}, False],
                    ['inputs:b', {'type': 'float[2]', 'value': [2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[2]', 'value': [1, 1]}, False],
                    ['inputs:b', {'type': 'float[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:b', {'type': 'float[2]', 'value': [1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:b', {'type': 'float[2][]', 'value': [[3, 3], [0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:b', {'type': 'float[3]', 'value': [2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:b', {'type': 'float[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'float[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'float[3][]', 'value': [[3, 3, 3], [0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'float[4]', 'value': [2, 2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'float[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'float[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'float[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'float[4][]', 'value': [[3, 3, 3, 3], [0, 0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[2]', 'value': [1, 1]}, False],
                    ['inputs:b', {'type': 'half[2]', 'value': [2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[2]', 'value': [1, 1]}, False],
                    ['inputs:b', {'type': 'half[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:b', {'type': 'half[2]', 'value': [1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:b', {'type': 'half[2][]', 'value': [[3, 3], [0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:b', {'type': 'half[3]', 'value': [2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:b', {'type': 'half[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'half[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'half[3][]', 'value': [[3, 3, 3], [0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'half[4]', 'value': [2, 2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'half[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'half[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'half[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'half[4][]', 'value': [[3, 3, 3, 3], [0, 0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[2]', 'value': [1, 1]}, False],
                    ['inputs:b', {'type': 'int[2]', 'value': [2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[2]', 'value': [1, 1]}, False],
                    ['inputs:b', {'type': 'int[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:b', {'type': 'int[2]', 'value': [1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[2][]', 'value': [[1, 1], [2, 2]]}, False],
                    ['inputs:b', {'type': 'int[2][]', 'value': [[3, 3], [0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:b', {'type': 'int[3]', 'value': [2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:b', {'type': 'int[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'int[3]', 'value': [1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[3][]', 'value': [[1, 1, 1], [2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'int[3][]', 'value': [[3, 3, 3], [0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'int[4]', 'value': [2, 2, 2, 2]}, False],
                    ['inputs:operation', ">", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool', 'value': False}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:b', {'type': 'int[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:operation', "<", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'int[4]', 'value': [1, 1, 1, 1]}, False],
                    ['inputs:operation', "<=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [True, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:a', {'type': 'int[4][]', 'value': [[1, 1, 1, 1], [2, 2, 2, 2]]}, False],
                    ['inputs:b', {'type': 'int[4][]', 'value': [[3, 3, 3, 3], [0, 0, 0, 0]]}, False],
                    ['inputs:operation', ">=", False],
                ],
                'outputs': [
                    ['outputs:result', {'type': 'bool[]', 'value': [False, True]}, False],
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
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_Compare", "omni.graph.nodes.Compare", test_run, _TestGraphAndNode())
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.Compare User test case #{i+1}")

    async def test_vectorized_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_Compare","omni.graph.nodes.Compare", test_run, _TestGraphAndNode(), 16)
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.Compare User test case #{i+1}", 16)

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
            instance_setup[key] = await _test_setup_scene(self, og.Controller(allow_exists_prim=True), key, "TestNode_omni_graph_nodes_Compare", "omni.graph.nodes.Compare", test_data_setup[key], test_info)
        self.assertEqual(len(og.get_all_graphs()), 24)

        # We want to evaluate all graphs concurrently. Kick them all.
        # Evaluate multiple times to skip 2 serial frames and increase chances for a race condition.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        for (key, test_info) in instance_setup.items():
            _test_verify_scene(self, og.Controller(), test_data_setup[key], test_info, f"omni.graph.nodes.Compare User test case instance{key}")

    async def test_data_access(self):
        test_file_name = "OgnCompareTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_nodes_Compare")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:operation"))
        attribute = test_node.get_attribute("inputs:operation")
        self.assertTrue(attribute.is_valid())
        expected_value = ">"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
