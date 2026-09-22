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
                    ['inputs:bool_0', True, False],
                    ['inputs:bool_1', True, False],
                ],
                'outputs': [
                    ['outputs:bool_0', False, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:bool_arr_0', [True, True, False, False], False],
                    ['inputs:bool_arr_1', [True, False, True, False], False],
                ],
                'outputs': [
                    ['outputs:bool_arr_0', [False, True, True, False], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colord3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:colord3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:colord3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colord3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:colord3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:colord3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colord4_0', [1.0, 2.0, 3.0, 4.0], False],
                    ['inputs:colord4_1', [2.0, 3.0, 4.0, 5.0], False],
                ],
                'outputs': [
                    ['outputs:colord4_0', [3.0, 5.0, 7.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colord4_arr_0', [[1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]], False],
                    ['inputs:colord4_arr_1', [[2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0]], False],
                ],
                'outputs': [
                    ['outputs:colord4_arr_0', [[3.0, 5.0, 7.0, 9.0], [3.0, 5.0, 7.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colorf3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:colorf3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:colorf3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colorf3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:colorf3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:colorf3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colorf4_0', [1.0, 2.0, 3.0, 4.0], False],
                    ['inputs:colorf4_1', [2.0, 3.0, 4.0, 5.0], False],
                ],
                'outputs': [
                    ['outputs:colorf4_0', [3.0, 5.0, 7.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colorf4_arr_0', [[1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]], False],
                    ['inputs:colorf4_arr_1', [[2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0]], False],
                ],
                'outputs': [
                    ['outputs:colorf4_arr_0', [[3.0, 5.0, 7.0, 9.0], [3.0, 5.0, 7.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colorh3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:colorh3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:colorh3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colorh3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:colorh3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:colorh3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colorh4_0', [1.0, 2.0, 3.0, 4.0], False],
                    ['inputs:colorh4_1', [2.0, 3.0, 4.0, 5.0], False],
                ],
                'outputs': [
                    ['outputs:colorh4_0', [3.0, 5.0, 7.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:colorh4_arr_0', [[1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]], False],
                    ['inputs:colorh4_arr_1', [[2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0]], False],
                ],
                'outputs': [
                    ['outputs:colorh4_arr_0', [[3.0, 5.0, 7.0, 9.0], [3.0, 5.0, 7.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:double_0', 1.0, False],
                    ['inputs:double_1', 2.0, False],
                ],
                'outputs': [
                    ['outputs:double_0', 3.0, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:double_arr_0', [1.0, 2.0], False],
                    ['inputs:double_arr_1', [2.0, 1.0], False],
                ],
                'outputs': [
                    ['outputs:double_arr_0', [3.0, 3.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:double2_0', [1.0, 2.0], False],
                    ['inputs:double2_1', [2.0, 3.0], False],
                ],
                'outputs': [
                    ['outputs:double2_0', [3.0, 5.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:double2_arr_0', [[1.0, 2.0], [2.0, 3.0]], False],
                    ['inputs:double2_arr_1', [[2.0, 3.0], [1.0, 2.0]], False],
                ],
                'outputs': [
                    ['outputs:double2_arr_0', [[3.0, 5.0], [3.0, 5.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:double3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:double3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:double3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:double3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:double3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:double3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:double4_0', [1.0, 2.0, 3.0, 4.0], False],
                    ['inputs:double4_1', [2.0, 3.0, 4.0, 5.0], False],
                ],
                'outputs': [
                    ['outputs:double4_0', [3.0, 5.0, 7.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:double4_arr_0', [[1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]], False],
                    ['inputs:double4_arr_1', [[2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0]], False],
                ],
                'outputs': [
                    ['outputs:double4_arr_0', [[3.0, 5.0, 7.0, 9.0], [3.0, 5.0, 7.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:float_0', 1.0, False],
                    ['inputs:float_1', 2.0, False],
                ],
                'outputs': [
                    ['outputs:float_0', 3.0, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:float_arr_0', [1.0, 2.0], False],
                    ['inputs:float_arr_1', [2.0, 1.0], False],
                ],
                'outputs': [
                    ['outputs:float_arr_0', [3.0, 3.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:float2_0', [1.0, 2.0], False],
                    ['inputs:float2_1', [2.0, 3.0], False],
                ],
                'outputs': [
                    ['outputs:float2_0', [3.0, 5.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:float2_arr_0', [[1.0, 2.0], [2.0, 3.0]], False],
                    ['inputs:float2_arr_1', [[2.0, 3.0], [1.0, 2.0]], False],
                ],
                'outputs': [
                    ['outputs:float2_arr_0', [[3.0, 5.0], [3.0, 5.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:float3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:float3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:float3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:float3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:float3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:float3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:float4_0', [1.0, 2.0, 3.0, 4.0], False],
                    ['inputs:float4_1', [2.0, 3.0, 4.0, 5.0], False],
                ],
                'outputs': [
                    ['outputs:float4_0', [3.0, 5.0, 7.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:float4_arr_0', [[1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]], False],
                    ['inputs:float4_arr_1', [[2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0]], False],
                ],
                'outputs': [
                    ['outputs:float4_arr_0', [[3.0, 5.0, 7.0, 9.0], [3.0, 5.0, 7.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:frame4_0', [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5], False],
                    ['inputs:frame4_1', [1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0, 1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0], False],
                ],
                'outputs': [
                    ['outputs:frame4_0', [2.0, 4.0, 6.0, 8.0, 9.0, 9.0, 9.0, 9.0, 2.5, 4.5, 6.5, 8.5, 9.5, 9.5, 9.5, 9.5], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:half_0', 1.0, False],
                    ['inputs:half_1', 2.0, False],
                ],
                'outputs': [
                    ['outputs:half_0', 3.0, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:half_arr_0', [1.0, 2.0], False],
                    ['inputs:half_arr_1', [2.0, 1.0], False],
                ],
                'outputs': [
                    ['outputs:half_arr_0', [3.0, 3.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:half2_0', [1.0, 2.0], False],
                    ['inputs:half2_1', [2.0, 3.0], False],
                ],
                'outputs': [
                    ['outputs:half2_0', [3.0, 5.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:half2_arr_0', [[1.0, 2.0], [2.0, 3.0]], False],
                    ['inputs:half2_arr_1', [[2.0, 3.0], [1.0, 2.0]], False],
                ],
                'outputs': [
                    ['outputs:half2_arr_0', [[3.0, 5.0], [3.0, 5.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:half3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:half3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:half3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:half3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:half3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:half3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:half4_0', [1.0, 2.0, 3.0, 4.0], False],
                    ['inputs:half4_1', [2.0, 3.0, 4.0, 5.0], False],
                ],
                'outputs': [
                    ['outputs:half4_0', [3.0, 5.0, 7.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:half4_arr_0', [[1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]], False],
                    ['inputs:half4_arr_1', [[2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0]], False],
                ],
                'outputs': [
                    ['outputs:half4_arr_0', [[3.0, 5.0, 7.0, 9.0], [3.0, 5.0, 7.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int_0', 1, False],
                    ['inputs:int_1', 2, False],
                ],
                'outputs': [
                    ['outputs:int_0', 3, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int_arr_0', [1, 2], False],
                    ['inputs:int_arr_1', [2, 1], False],
                ],
                'outputs': [
                    ['outputs:int_arr_0', [3, 3], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int2_0', [1, 2], False],
                    ['inputs:int2_1', [2, 3], False],
                ],
                'outputs': [
                    ['outputs:int2_0', [3, 5], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int2_arr_0', [[1, 2], [2, 3]], False],
                    ['inputs:int2_arr_1', [[2, 3], [1, 2]], False],
                ],
                'outputs': [
                    ['outputs:int2_arr_0', [[3, 5], [3, 5]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int3_0', [1, 2, 3], False],
                    ['inputs:int3_1', [2, 3, 4], False],
                ],
                'outputs': [
                    ['outputs:int3_0', [3, 5, 7], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int3_arr_0', [[1, 2, 3], [2, 3, 4]], False],
                    ['inputs:int3_arr_1', [[2, 3, 4], [1, 2, 3]], False],
                ],
                'outputs': [
                    ['outputs:int3_arr_0', [[3, 5, 7], [3, 5, 7]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int4_0', [1, 2, 3, 4], False],
                    ['inputs:int4_1', [2, 3, 4, 5], False],
                ],
                'outputs': [
                    ['outputs:int4_0', [3, 5, 7, 9], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int4_arr_0', [[1, 2, 3, 4], [2, 3, 4, 5]], False],
                    ['inputs:int4_arr_1', [[2, 3, 4, 5], [1, 2, 3, 4]], False],
                ],
                'outputs': [
                    ['outputs:int4_arr_0', [[3, 5, 7, 9], [3, 5, 7, 9]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int64_0', 1, False],
                    ['inputs:int64_1', 2, False],
                ],
                'outputs': [
                    ['outputs:int64_0', 3, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:int64_arr_0', [1, 2], False],
                    ['inputs:int64_arr_1', [2, 1], False],
                ],
                'outputs': [
                    ['outputs:int64_arr_0', [3, 3], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:matrixd2_0', [1.0, 2.0, 5.0, 6.0], False],
                    ['inputs:matrixd2_1', [1.0, 2.0, 4.0, 3.0], False],
                ],
                'outputs': [
                    ['outputs:matrixd2_0', [2.0, 4.0, 9.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:matrixd2_arr_0', [[1.0, 2.0, 5.0, 6.0], [1.0, 2.0, 4.0, 3.0]], False],
                    ['inputs:matrixd2_arr_1', [[1.0, 2.0, 4.0, 3.0], [1.0, 2.0, 5.0, 6.0]], False],
                ],
                'outputs': [
                    ['outputs:matrixd2_arr_0', [[2.0, 4.0, 9.0, 9.0], [2.0, 4.0, 9.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:matrixd3_0', [1.0, 2.0, 3.0, 5.0, 6.0, 7.0, 1.5, 2.5, 3.5], False],
                    ['inputs:matrixd3_1', [1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0, 2.0, 3.0], False],
                ],
                'outputs': [
                    ['outputs:matrixd3_0', [2.0, 4.0, 6.0, 9.0, 9.0, 9.0, 2.5, 4.5, 6.5], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:matrixd3_arr_0', [[1.0, 2.0, 3.0, 5.0, 6.0, 7.0, 1.5, 2.5, 3.5], [1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0, 2.0, 3.0]], False],
                    ['inputs:matrixd3_arr_1', [[1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0, 2.0, 3.0], [1.0, 2.0, 3.0, 5.0, 6.0, 7.0, 1.5, 2.5, 3.5]], False],
                ],
                'outputs': [
                    ['outputs:matrixd3_arr_0', [[2.0, 4.0, 6.0, 9.0, 9.0, 9.0, 2.5, 4.5, 6.5], [2.0, 4.0, 6.0, 9.0, 9.0, 9.0, 2.5, 4.5, 6.5]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:matrixd4_0', [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5], False],
                    ['inputs:matrixd4_1', [1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0, 1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0], False],
                ],
                'outputs': [
                    ['outputs:matrixd4_0', [2.0, 4.0, 6.0, 8.0, 9.0, 9.0, 9.0, 9.0, 2.5, 4.5, 6.5, 8.5, 9.5, 9.5, 9.5, 9.5], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:matrixd4_arr_0', [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5], [1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0, 1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0]], False],
                    ['inputs:matrixd4_arr_1', [[1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0, 1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]], False],
                ],
                'outputs': [
                    ['outputs:matrixd4_arr_0', [[2.0, 4.0, 6.0, 8.0, 9.0, 9.0, 9.0, 9.0, 2.5, 4.5, 6.5, 8.5, 9.5, 9.5, 9.5, 9.5], [2.0, 4.0, 6.0, 8.0, 9.0, 9.0, 9.0, 9.0, 2.5, 4.5, 6.5, 8.5, 9.5, 9.5, 9.5, 9.5]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:normald3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:normald3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:normald3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:normald3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:normald3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:normald3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:normalf3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:normalf3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:normalf3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:normalf3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:normalf3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:normalf3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:normalh3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:normalh3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:normalh3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:normalh3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:normalh3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:normalh3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:pointd3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:pointd3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:pointd3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:pointd3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:pointd3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:pointd3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:pointf3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:pointf3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:pointf3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:pointf3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:pointf3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:pointf3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:pointh3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:pointh3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:pointh3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:pointh3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:pointh3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:pointh3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:quatd4_0', [1.0, 2.0, 3.0, 4.0], False],
                    ['inputs:quatd4_1', [2.0, 3.0, 4.0, 5.0], False],
                ],
                'outputs': [
                    ['outputs:quatd4_0', [3.0, 5.0, 7.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:quatd4_arr_0', [[1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]], False],
                    ['inputs:quatd4_arr_1', [[2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0]], False],
                ],
                'outputs': [
                    ['outputs:quatd4_arr_0', [[3.0, 5.0, 7.0, 9.0], [3.0, 5.0, 7.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:quatf4_0', [1.0, 2.0, 3.0, 4.0], False],
                    ['inputs:quatf4_1', [2.0, 3.0, 4.0, 5.0], False],
                ],
                'outputs': [
                    ['outputs:quatf4_0', [3.0, 5.0, 7.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:quatf4_arr_0', [[1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]], False],
                    ['inputs:quatf4_arr_1', [[2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0]], False],
                ],
                'outputs': [
                    ['outputs:quatf4_arr_0', [[3.0, 5.0, 7.0, 9.0], [3.0, 5.0, 7.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:quath4_0', [1.0, 2.0, 3.0, 4.0], False],
                    ['inputs:quath4_1', [2.0, 3.0, 4.0, 5.0], False],
                ],
                'outputs': [
                    ['outputs:quath4_0', [3.0, 5.0, 7.0, 9.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:quath4_arr_0', [[1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]], False],
                    ['inputs:quath4_arr_1', [[2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0]], False],
                ],
                'outputs': [
                    ['outputs:quath4_arr_0', [[3.0, 5.0, 7.0, 9.0], [3.0, 5.0, 7.0, 9.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordd2_0', [1.0, 2.0], False],
                    ['inputs:texcoordd2_1', [2.0, 3.0], False],
                ],
                'outputs': [
                    ['outputs:texcoordd2_0', [3.0, 5.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordd2_arr_0', [[1.0, 2.0], [2.0, 3.0]], False],
                    ['inputs:texcoordd2_arr_1', [[2.0, 3.0], [1.0, 2.0]], False],
                ],
                'outputs': [
                    ['outputs:texcoordd2_arr_0', [[3.0, 5.0], [3.0, 5.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordd3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:texcoordd3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:texcoordd3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordd3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:texcoordd3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:texcoordd3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordf2_0', [1.0, 2.0], False],
                    ['inputs:texcoordf2_1', [2.0, 3.0], False],
                ],
                'outputs': [
                    ['outputs:texcoordf2_0', [3.0, 5.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordf2_arr_0', [[1.0, 2.0], [2.0, 3.0]], False],
                    ['inputs:texcoordf2_arr_1', [[2.0, 3.0], [1.0, 2.0]], False],
                ],
                'outputs': [
                    ['outputs:texcoordf2_arr_0', [[3.0, 5.0], [3.0, 5.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordf3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:texcoordf3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:texcoordf3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordf3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:texcoordf3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:texcoordf3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordh2_0', [1.0, 2.0], False],
                    ['inputs:texcoordh2_1', [2.0, 3.0], False],
                ],
                'outputs': [
                    ['outputs:texcoordh2_0', [3.0, 5.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordh2_arr_0', [[1.0, 2.0], [2.0, 3.0]], False],
                    ['inputs:texcoordh2_arr_1', [[2.0, 3.0], [1.0, 2.0]], False],
                ],
                'outputs': [
                    ['outputs:texcoordh2_arr_0', [[3.0, 5.0], [3.0, 5.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordh3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:texcoordh3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:texcoordh3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:texcoordh3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:texcoordh3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:texcoordh3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:timecode_0', 1.0, False],
                    ['inputs:timecode_1', 2.0, False],
                ],
                'outputs': [
                    ['outputs:timecode_0', 3.0, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:timecode_arr_0', [1.0, 2.0], False],
                    ['inputs:timecode_arr_1', [2.0, 1.0], False],
                ],
                'outputs': [
                    ['outputs:timecode_arr_0', [3.0, 3.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:token_0', "hello", False],
                    ['inputs:token_1', "world", False],
                ],
                'outputs': [
                    ['outputs:token_0', "helloworld", False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:token_arr_0', ["hello", "world"], False],
                    ['inputs:token_arr_1', ["world", "hello"], False],
                ],
                'outputs': [
                    ['outputs:token_arr_0', ["helloworld", "worldhello"], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:uchar_0', 1, False],
                    ['inputs:uchar_1', 2, False],
                ],
                'outputs': [
                    ['outputs:uchar_0', 3, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:uchar_arr_0', [1, 2], False],
                    ['inputs:uchar_arr_1', [2, 1], False],
                ],
                'outputs': [
                    ['outputs:uchar_arr_0', [3, 3], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:uint_0', 1, False],
                    ['inputs:uint_1', 2, False],
                ],
                'outputs': [
                    ['outputs:uint_0', 3, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:uint_arr_0', [1, 2], False],
                    ['inputs:uint_arr_1', [2, 1], False],
                ],
                'outputs': [
                    ['outputs:uint_arr_0', [3, 3], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:uint64_0', 1, False],
                    ['inputs:uint64_1', 2, False],
                ],
                'outputs': [
                    ['outputs:uint64_0', 3, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:uint64_arr_0', [1, 2], False],
                    ['inputs:uint64_arr_1', [2, 1], False],
                ],
                'outputs': [
                    ['outputs:uint64_arr_0', [3, 3], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:vectord3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:vectord3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:vectord3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:vectord3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:vectord3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:vectord3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:vectorf3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:vectorf3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:vectorf3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:vectorf3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:vectorf3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:vectorf3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:vectorh3_0', [1.0, 2.0, 3.0], False],
                    ['inputs:vectorh3_1', [2.0, 3.0, 4.0], False],
                ],
                'outputs': [
                    ['outputs:vectorh3_0', [3.0, 5.0, 7.0], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:vectorh3_arr_0', [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], False],
                    ['inputs:vectorh3_arr_1', [[2.0, 3.0, 4.0], [1.0, 2.0, 3.0]], False],
                ],
                'outputs': [
                    ['outputs:vectorh3_arr_0', [[3.0, 5.0, 7.0], [3.0, 5.0, 7.0]], False],
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
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_examples_cpp_UniversalAdd", "omni.graph.examples.cpp.UniversalAdd", test_run, _TestGraphAndNode())
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.examples.cpp.UniversalAdd User test case #{i+1}")

    async def test_vectorized_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_examples_cpp_UniversalAdd","omni.graph.examples.cpp.UniversalAdd", test_run, _TestGraphAndNode(), 16)
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.examples.cpp.UniversalAdd User test case #{i+1}", 16)

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
            instance_setup[key] = await _test_setup_scene(self, og.Controller(allow_exists_prim=True), key, "TestNode_omni_graph_examples_cpp_UniversalAdd", "omni.graph.examples.cpp.UniversalAdd", test_data_setup[key], test_info)
        self.assertEqual(len(og.get_all_graphs()), 24)

        # We want to evaluate all graphs concurrently. Kick them all.
        # Evaluate multiple times to skip 2 serial frames and increase chances for a race condition.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        for (key, test_info) in instance_setup.items():
            _test_verify_scene(self, og.Controller(), test_data_setup[key], test_info, f"omni.graph.examples.cpp.UniversalAdd User test case instance{key}")

    async def test_data_access(self):
        test_file_name = "OgnUniversalAddTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_examples_cpp_UniversalAdd")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:bool_0"))
        attribute = test_node.get_attribute("inputs:bool_0")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:bool_1"))
        attribute = test_node.get_attribute("inputs:bool_1")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:bool_arr_0"))
        attribute = test_node.get_attribute("inputs:bool_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:bool_arr_1"))
        attribute = test_node.get_attribute("inputs:bool_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colord3_0"))
        attribute = test_node.get_attribute("inputs:colord3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colord3_1"))
        attribute = test_node.get_attribute("inputs:colord3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colord3_arr_0"))
        attribute = test_node.get_attribute("inputs:colord3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colord3_arr_1"))
        attribute = test_node.get_attribute("inputs:colord3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colord4_0"))
        attribute = test_node.get_attribute("inputs:colord4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colord4_1"))
        attribute = test_node.get_attribute("inputs:colord4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colord4_arr_0"))
        attribute = test_node.get_attribute("inputs:colord4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colord4_arr_1"))
        attribute = test_node.get_attribute("inputs:colord4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorf3_0"))
        attribute = test_node.get_attribute("inputs:colorf3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorf3_1"))
        attribute = test_node.get_attribute("inputs:colorf3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorf3_arr_0"))
        attribute = test_node.get_attribute("inputs:colorf3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorf3_arr_1"))
        attribute = test_node.get_attribute("inputs:colorf3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorf4_0"))
        attribute = test_node.get_attribute("inputs:colorf4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorf4_1"))
        attribute = test_node.get_attribute("inputs:colorf4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorf4_arr_0"))
        attribute = test_node.get_attribute("inputs:colorf4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorf4_arr_1"))
        attribute = test_node.get_attribute("inputs:colorf4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorh3_0"))
        attribute = test_node.get_attribute("inputs:colorh3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorh3_1"))
        attribute = test_node.get_attribute("inputs:colorh3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorh3_arr_0"))
        attribute = test_node.get_attribute("inputs:colorh3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorh3_arr_1"))
        attribute = test_node.get_attribute("inputs:colorh3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorh4_0"))
        attribute = test_node.get_attribute("inputs:colorh4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorh4_1"))
        attribute = test_node.get_attribute("inputs:colorh4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorh4_arr_0"))
        attribute = test_node.get_attribute("inputs:colorh4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:colorh4_arr_1"))
        attribute = test_node.get_attribute("inputs:colorh4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double2_0"))
        attribute = test_node.get_attribute("inputs:double2_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double2_1"))
        attribute = test_node.get_attribute("inputs:double2_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double2_arr_0"))
        attribute = test_node.get_attribute("inputs:double2_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double2_arr_1"))
        attribute = test_node.get_attribute("inputs:double2_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double3_0"))
        attribute = test_node.get_attribute("inputs:double3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double3_1"))
        attribute = test_node.get_attribute("inputs:double3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double3_arr_0"))
        attribute = test_node.get_attribute("inputs:double3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double3_arr_1"))
        attribute = test_node.get_attribute("inputs:double3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double4_0"))
        attribute = test_node.get_attribute("inputs:double4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double4_1"))
        attribute = test_node.get_attribute("inputs:double4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double4_arr_0"))
        attribute = test_node.get_attribute("inputs:double4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double4_arr_1"))
        attribute = test_node.get_attribute("inputs:double4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double_0"))
        attribute = test_node.get_attribute("inputs:double_0")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double_1"))
        attribute = test_node.get_attribute("inputs:double_1")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double_arr_0"))
        attribute = test_node.get_attribute("inputs:double_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:double_arr_1"))
        attribute = test_node.get_attribute("inputs:double_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float2_0"))
        attribute = test_node.get_attribute("inputs:float2_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float2_1"))
        attribute = test_node.get_attribute("inputs:float2_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float2_arr_0"))
        attribute = test_node.get_attribute("inputs:float2_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float2_arr_1"))
        attribute = test_node.get_attribute("inputs:float2_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float3_0"))
        attribute = test_node.get_attribute("inputs:float3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float3_1"))
        attribute = test_node.get_attribute("inputs:float3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float3_arr_0"))
        attribute = test_node.get_attribute("inputs:float3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float3_arr_1"))
        attribute = test_node.get_attribute("inputs:float3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float4_0"))
        attribute = test_node.get_attribute("inputs:float4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float4_1"))
        attribute = test_node.get_attribute("inputs:float4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float4_arr_0"))
        attribute = test_node.get_attribute("inputs:float4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float4_arr_1"))
        attribute = test_node.get_attribute("inputs:float4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float_0"))
        attribute = test_node.get_attribute("inputs:float_0")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float_1"))
        attribute = test_node.get_attribute("inputs:float_1")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float_arr_0"))
        attribute = test_node.get_attribute("inputs:float_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:float_arr_1"))
        attribute = test_node.get_attribute("inputs:float_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:frame4_0"))
        attribute = test_node.get_attribute("inputs:frame4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:frame4_1"))
        attribute = test_node.get_attribute("inputs:frame4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:frame4_arr_0"))
        attribute = test_node.get_attribute("inputs:frame4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:frame4_arr_1"))
        attribute = test_node.get_attribute("inputs:frame4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half2_0"))
        attribute = test_node.get_attribute("inputs:half2_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half2_1"))
        attribute = test_node.get_attribute("inputs:half2_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half2_arr_0"))
        attribute = test_node.get_attribute("inputs:half2_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half2_arr_1"))
        attribute = test_node.get_attribute("inputs:half2_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half3_0"))
        attribute = test_node.get_attribute("inputs:half3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half3_1"))
        attribute = test_node.get_attribute("inputs:half3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half3_arr_0"))
        attribute = test_node.get_attribute("inputs:half3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half3_arr_1"))
        attribute = test_node.get_attribute("inputs:half3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half4_0"))
        attribute = test_node.get_attribute("inputs:half4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half4_1"))
        attribute = test_node.get_attribute("inputs:half4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half4_arr_0"))
        attribute = test_node.get_attribute("inputs:half4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half4_arr_1"))
        attribute = test_node.get_attribute("inputs:half4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half_0"))
        attribute = test_node.get_attribute("inputs:half_0")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half_1"))
        attribute = test_node.get_attribute("inputs:half_1")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half_arr_0"))
        attribute = test_node.get_attribute("inputs:half_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:half_arr_1"))
        attribute = test_node.get_attribute("inputs:half_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int2_0"))
        attribute = test_node.get_attribute("inputs:int2_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int2_1"))
        attribute = test_node.get_attribute("inputs:int2_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int2_arr_0"))
        attribute = test_node.get_attribute("inputs:int2_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int2_arr_1"))
        attribute = test_node.get_attribute("inputs:int2_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int3_0"))
        attribute = test_node.get_attribute("inputs:int3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int3_1"))
        attribute = test_node.get_attribute("inputs:int3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int3_arr_0"))
        attribute = test_node.get_attribute("inputs:int3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int3_arr_1"))
        attribute = test_node.get_attribute("inputs:int3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int4_0"))
        attribute = test_node.get_attribute("inputs:int4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 0, 0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int4_1"))
        attribute = test_node.get_attribute("inputs:int4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 0, 0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int4_arr_0"))
        attribute = test_node.get_attribute("inputs:int4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int4_arr_1"))
        attribute = test_node.get_attribute("inputs:int4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int64_0"))
        attribute = test_node.get_attribute("inputs:int64_0")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int64_1"))
        attribute = test_node.get_attribute("inputs:int64_1")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int64_arr_0"))
        attribute = test_node.get_attribute("inputs:int64_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int64_arr_1"))
        attribute = test_node.get_attribute("inputs:int64_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int_0"))
        attribute = test_node.get_attribute("inputs:int_0")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int_1"))
        attribute = test_node.get_attribute("inputs:int_1")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int_arr_0"))
        attribute = test_node.get_attribute("inputs:int_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:int_arr_1"))
        attribute = test_node.get_attribute("inputs:int_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd2_0"))
        attribute = test_node.get_attribute("inputs:matrixd2_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd2_1"))
        attribute = test_node.get_attribute("inputs:matrixd2_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd2_arr_0"))
        attribute = test_node.get_attribute("inputs:matrixd2_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd2_arr_1"))
        attribute = test_node.get_attribute("inputs:matrixd2_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd3_0"))
        attribute = test_node.get_attribute("inputs:matrixd3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd3_1"))
        attribute = test_node.get_attribute("inputs:matrixd3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd3_arr_0"))
        attribute = test_node.get_attribute("inputs:matrixd3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd3_arr_1"))
        attribute = test_node.get_attribute("inputs:matrixd3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd4_0"))
        attribute = test_node.get_attribute("inputs:matrixd4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd4_1"))
        attribute = test_node.get_attribute("inputs:matrixd4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd4_arr_0"))
        attribute = test_node.get_attribute("inputs:matrixd4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:matrixd4_arr_1"))
        attribute = test_node.get_attribute("inputs:matrixd4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normald3_0"))
        attribute = test_node.get_attribute("inputs:normald3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normald3_1"))
        attribute = test_node.get_attribute("inputs:normald3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normald3_arr_0"))
        attribute = test_node.get_attribute("inputs:normald3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normald3_arr_1"))
        attribute = test_node.get_attribute("inputs:normald3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalf3_0"))
        attribute = test_node.get_attribute("inputs:normalf3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalf3_1"))
        attribute = test_node.get_attribute("inputs:normalf3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalf3_arr_0"))
        attribute = test_node.get_attribute("inputs:normalf3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalf3_arr_1"))
        attribute = test_node.get_attribute("inputs:normalf3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalh3_0"))
        attribute = test_node.get_attribute("inputs:normalh3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalh3_1"))
        attribute = test_node.get_attribute("inputs:normalh3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalh3_arr_0"))
        attribute = test_node.get_attribute("inputs:normalh3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normalh3_arr_1"))
        attribute = test_node.get_attribute("inputs:normalh3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointd3_0"))
        attribute = test_node.get_attribute("inputs:pointd3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointd3_1"))
        attribute = test_node.get_attribute("inputs:pointd3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointd3_arr_0"))
        attribute = test_node.get_attribute("inputs:pointd3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointd3_arr_1"))
        attribute = test_node.get_attribute("inputs:pointd3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointf3_0"))
        attribute = test_node.get_attribute("inputs:pointf3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointf3_1"))
        attribute = test_node.get_attribute("inputs:pointf3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointf3_arr_0"))
        attribute = test_node.get_attribute("inputs:pointf3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointf3_arr_1"))
        attribute = test_node.get_attribute("inputs:pointf3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointh3_0"))
        attribute = test_node.get_attribute("inputs:pointh3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointh3_1"))
        attribute = test_node.get_attribute("inputs:pointh3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointh3_arr_0"))
        attribute = test_node.get_attribute("inputs:pointh3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:pointh3_arr_1"))
        attribute = test_node.get_attribute("inputs:pointh3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quatd4_0"))
        attribute = test_node.get_attribute("inputs:quatd4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quatd4_1"))
        attribute = test_node.get_attribute("inputs:quatd4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quatd4_arr_0"))
        attribute = test_node.get_attribute("inputs:quatd4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quatd4_arr_1"))
        attribute = test_node.get_attribute("inputs:quatd4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quatf4_0"))
        attribute = test_node.get_attribute("inputs:quatf4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quatf4_1"))
        attribute = test_node.get_attribute("inputs:quatf4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quatf4_arr_0"))
        attribute = test_node.get_attribute("inputs:quatf4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quatf4_arr_1"))
        attribute = test_node.get_attribute("inputs:quatf4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quath4_0"))
        attribute = test_node.get_attribute("inputs:quath4_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quath4_1"))
        attribute = test_node.get_attribute("inputs:quath4_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quath4_arr_0"))
        attribute = test_node.get_attribute("inputs:quath4_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:quath4_arr_1"))
        attribute = test_node.get_attribute("inputs:quath4_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordd2_0"))
        attribute = test_node.get_attribute("inputs:texcoordd2_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordd2_1"))
        attribute = test_node.get_attribute("inputs:texcoordd2_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordd2_arr_0"))
        attribute = test_node.get_attribute("inputs:texcoordd2_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordd2_arr_1"))
        attribute = test_node.get_attribute("inputs:texcoordd2_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordd3_0"))
        attribute = test_node.get_attribute("inputs:texcoordd3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordd3_1"))
        attribute = test_node.get_attribute("inputs:texcoordd3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordd3_arr_0"))
        attribute = test_node.get_attribute("inputs:texcoordd3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordd3_arr_1"))
        attribute = test_node.get_attribute("inputs:texcoordd3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordf2_0"))
        attribute = test_node.get_attribute("inputs:texcoordf2_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordf2_1"))
        attribute = test_node.get_attribute("inputs:texcoordf2_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordf2_arr_0"))
        attribute = test_node.get_attribute("inputs:texcoordf2_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordf2_arr_1"))
        attribute = test_node.get_attribute("inputs:texcoordf2_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordf3_0"))
        attribute = test_node.get_attribute("inputs:texcoordf3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordf3_1"))
        attribute = test_node.get_attribute("inputs:texcoordf3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordf3_arr_0"))
        attribute = test_node.get_attribute("inputs:texcoordf3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordf3_arr_1"))
        attribute = test_node.get_attribute("inputs:texcoordf3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordh2_0"))
        attribute = test_node.get_attribute("inputs:texcoordh2_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordh2_1"))
        attribute = test_node.get_attribute("inputs:texcoordh2_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordh2_arr_0"))
        attribute = test_node.get_attribute("inputs:texcoordh2_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordh2_arr_1"))
        attribute = test_node.get_attribute("inputs:texcoordh2_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordh3_0"))
        attribute = test_node.get_attribute("inputs:texcoordh3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordh3_1"))
        attribute = test_node.get_attribute("inputs:texcoordh3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordh3_arr_0"))
        attribute = test_node.get_attribute("inputs:texcoordh3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:texcoordh3_arr_1"))
        attribute = test_node.get_attribute("inputs:texcoordh3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:timecode_0"))
        attribute = test_node.get_attribute("inputs:timecode_0")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:timecode_1"))
        attribute = test_node.get_attribute("inputs:timecode_1")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:timecode_arr_0"))
        attribute = test_node.get_attribute("inputs:timecode_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:timecode_arr_1"))
        attribute = test_node.get_attribute("inputs:timecode_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:token_0"))
        attribute = test_node.get_attribute("inputs:token_0")
        self.assertTrue(attribute.is_valid())
        expected_value = "default_token"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:token_1"))
        attribute = test_node.get_attribute("inputs:token_1")
        self.assertTrue(attribute.is_valid())
        expected_value = "default_token"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:token_arr_0"))
        attribute = test_node.get_attribute("inputs:token_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:token_arr_1"))
        attribute = test_node.get_attribute("inputs:token_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uchar_0"))
        attribute = test_node.get_attribute("inputs:uchar_0")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uchar_1"))
        attribute = test_node.get_attribute("inputs:uchar_1")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uchar_arr_0"))
        attribute = test_node.get_attribute("inputs:uchar_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uchar_arr_1"))
        attribute = test_node.get_attribute("inputs:uchar_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uint64_0"))
        attribute = test_node.get_attribute("inputs:uint64_0")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uint64_1"))
        attribute = test_node.get_attribute("inputs:uint64_1")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uint64_arr_0"))
        attribute = test_node.get_attribute("inputs:uint64_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uint64_arr_1"))
        attribute = test_node.get_attribute("inputs:uint64_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uint_0"))
        attribute = test_node.get_attribute("inputs:uint_0")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uint_1"))
        attribute = test_node.get_attribute("inputs:uint_1")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uint_arr_0"))
        attribute = test_node.get_attribute("inputs:uint_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:uint_arr_1"))
        attribute = test_node.get_attribute("inputs:uint_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectord3_0"))
        attribute = test_node.get_attribute("inputs:vectord3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectord3_1"))
        attribute = test_node.get_attribute("inputs:vectord3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectord3_arr_0"))
        attribute = test_node.get_attribute("inputs:vectord3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectord3_arr_1"))
        attribute = test_node.get_attribute("inputs:vectord3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectorf3_0"))
        attribute = test_node.get_attribute("inputs:vectorf3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectorf3_1"))
        attribute = test_node.get_attribute("inputs:vectorf3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectorf3_arr_0"))
        attribute = test_node.get_attribute("inputs:vectorf3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectorf3_arr_1"))
        attribute = test_node.get_attribute("inputs:vectorf3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectorh3_0"))
        attribute = test_node.get_attribute("inputs:vectorh3_0")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectorh3_1"))
        attribute = test_node.get_attribute("inputs:vectorh3_1")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectorh3_arr_0"))
        attribute = test_node.get_attribute("inputs:vectorh3_arr_0")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:vectorh3_arr_1"))
        attribute = test_node.get_attribute("inputs:vectorh3_arr_1")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs:bool_0"))
        attribute = test_node.get_attribute("outputs:bool_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:bool_arr_0"))
        attribute = test_node.get_attribute("outputs:bool_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colord3_0"))
        attribute = test_node.get_attribute("outputs:colord3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colord3_arr_0"))
        attribute = test_node.get_attribute("outputs:colord3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colord4_0"))
        attribute = test_node.get_attribute("outputs:colord4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colord4_arr_0"))
        attribute = test_node.get_attribute("outputs:colord4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colorf3_0"))
        attribute = test_node.get_attribute("outputs:colorf3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colorf3_arr_0"))
        attribute = test_node.get_attribute("outputs:colorf3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colorf4_0"))
        attribute = test_node.get_attribute("outputs:colorf4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colorf4_arr_0"))
        attribute = test_node.get_attribute("outputs:colorf4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colorh3_0"))
        attribute = test_node.get_attribute("outputs:colorh3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colorh3_arr_0"))
        attribute = test_node.get_attribute("outputs:colorh3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colorh4_0"))
        attribute = test_node.get_attribute("outputs:colorh4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:colorh4_arr_0"))
        attribute = test_node.get_attribute("outputs:colorh4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:double2_0"))
        attribute = test_node.get_attribute("outputs:double2_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:double2_arr_0"))
        attribute = test_node.get_attribute("outputs:double2_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:double3_0"))
        attribute = test_node.get_attribute("outputs:double3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:double3_arr_0"))
        attribute = test_node.get_attribute("outputs:double3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:double4_0"))
        attribute = test_node.get_attribute("outputs:double4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:double4_arr_0"))
        attribute = test_node.get_attribute("outputs:double4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:double_0"))
        attribute = test_node.get_attribute("outputs:double_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:double_arr_0"))
        attribute = test_node.get_attribute("outputs:double_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:float2_0"))
        attribute = test_node.get_attribute("outputs:float2_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:float2_arr_0"))
        attribute = test_node.get_attribute("outputs:float2_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:float3_0"))
        attribute = test_node.get_attribute("outputs:float3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:float3_arr_0"))
        attribute = test_node.get_attribute("outputs:float3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:float4_0"))
        attribute = test_node.get_attribute("outputs:float4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:float4_arr_0"))
        attribute = test_node.get_attribute("outputs:float4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:float_0"))
        attribute = test_node.get_attribute("outputs:float_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:float_arr_0"))
        attribute = test_node.get_attribute("outputs:float_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:frame4_0"))
        attribute = test_node.get_attribute("outputs:frame4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:frame4_arr_0"))
        attribute = test_node.get_attribute("outputs:frame4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:half2_0"))
        attribute = test_node.get_attribute("outputs:half2_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:half2_arr_0"))
        attribute = test_node.get_attribute("outputs:half2_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:half3_0"))
        attribute = test_node.get_attribute("outputs:half3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:half3_arr_0"))
        attribute = test_node.get_attribute("outputs:half3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:half4_0"))
        attribute = test_node.get_attribute("outputs:half4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:half4_arr_0"))
        attribute = test_node.get_attribute("outputs:half4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:half_0"))
        attribute = test_node.get_attribute("outputs:half_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:half_arr_0"))
        attribute = test_node.get_attribute("outputs:half_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int2_0"))
        attribute = test_node.get_attribute("outputs:int2_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int2_arr_0"))
        attribute = test_node.get_attribute("outputs:int2_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int3_0"))
        attribute = test_node.get_attribute("outputs:int3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int3_arr_0"))
        attribute = test_node.get_attribute("outputs:int3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int4_0"))
        attribute = test_node.get_attribute("outputs:int4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int4_arr_0"))
        attribute = test_node.get_attribute("outputs:int4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int64_0"))
        attribute = test_node.get_attribute("outputs:int64_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int64_arr_0"))
        attribute = test_node.get_attribute("outputs:int64_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int_0"))
        attribute = test_node.get_attribute("outputs:int_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:int_arr_0"))
        attribute = test_node.get_attribute("outputs:int_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:matrixd2_0"))
        attribute = test_node.get_attribute("outputs:matrixd2_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:matrixd2_arr_0"))
        attribute = test_node.get_attribute("outputs:matrixd2_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:matrixd3_0"))
        attribute = test_node.get_attribute("outputs:matrixd3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:matrixd3_arr_0"))
        attribute = test_node.get_attribute("outputs:matrixd3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:matrixd4_0"))
        attribute = test_node.get_attribute("outputs:matrixd4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:matrixd4_arr_0"))
        attribute = test_node.get_attribute("outputs:matrixd4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:normald3_0"))
        attribute = test_node.get_attribute("outputs:normald3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:normald3_arr_0"))
        attribute = test_node.get_attribute("outputs:normald3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:normalf3_0"))
        attribute = test_node.get_attribute("outputs:normalf3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:normalf3_arr_0"))
        attribute = test_node.get_attribute("outputs:normalf3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:normalh3_0"))
        attribute = test_node.get_attribute("outputs:normalh3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:normalh3_arr_0"))
        attribute = test_node.get_attribute("outputs:normalh3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:pointd3_0"))
        attribute = test_node.get_attribute("outputs:pointd3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:pointd3_arr_0"))
        attribute = test_node.get_attribute("outputs:pointd3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:pointf3_0"))
        attribute = test_node.get_attribute("outputs:pointf3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:pointf3_arr_0"))
        attribute = test_node.get_attribute("outputs:pointf3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:pointh3_0"))
        attribute = test_node.get_attribute("outputs:pointh3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:pointh3_arr_0"))
        attribute = test_node.get_attribute("outputs:pointh3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:quatd4_0"))
        attribute = test_node.get_attribute("outputs:quatd4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:quatd4_arr_0"))
        attribute = test_node.get_attribute("outputs:quatd4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:quatf4_0"))
        attribute = test_node.get_attribute("outputs:quatf4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:quatf4_arr_0"))
        attribute = test_node.get_attribute("outputs:quatf4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:quath4_0"))
        attribute = test_node.get_attribute("outputs:quath4_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:quath4_arr_0"))
        attribute = test_node.get_attribute("outputs:quath4_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordd2_0"))
        attribute = test_node.get_attribute("outputs:texcoordd2_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordd2_arr_0"))
        attribute = test_node.get_attribute("outputs:texcoordd2_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordd3_0"))
        attribute = test_node.get_attribute("outputs:texcoordd3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordd3_arr_0"))
        attribute = test_node.get_attribute("outputs:texcoordd3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordf2_0"))
        attribute = test_node.get_attribute("outputs:texcoordf2_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordf2_arr_0"))
        attribute = test_node.get_attribute("outputs:texcoordf2_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordf3_0"))
        attribute = test_node.get_attribute("outputs:texcoordf3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordf3_arr_0"))
        attribute = test_node.get_attribute("outputs:texcoordf3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordh2_0"))
        attribute = test_node.get_attribute("outputs:texcoordh2_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordh2_arr_0"))
        attribute = test_node.get_attribute("outputs:texcoordh2_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordh3_0"))
        attribute = test_node.get_attribute("outputs:texcoordh3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:texcoordh3_arr_0"))
        attribute = test_node.get_attribute("outputs:texcoordh3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:timecode_0"))
        attribute = test_node.get_attribute("outputs:timecode_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:timecode_arr_0"))
        attribute = test_node.get_attribute("outputs:timecode_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:token_0"))
        attribute = test_node.get_attribute("outputs:token_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:token_arr_0"))
        attribute = test_node.get_attribute("outputs:token_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:uchar_0"))
        attribute = test_node.get_attribute("outputs:uchar_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:uchar_arr_0"))
        attribute = test_node.get_attribute("outputs:uchar_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:uint64_0"))
        attribute = test_node.get_attribute("outputs:uint64_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:uint64_arr_0"))
        attribute = test_node.get_attribute("outputs:uint64_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:uint_0"))
        attribute = test_node.get_attribute("outputs:uint_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:uint_arr_0"))
        attribute = test_node.get_attribute("outputs:uint_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:vectord3_0"))
        attribute = test_node.get_attribute("outputs:vectord3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:vectord3_arr_0"))
        attribute = test_node.get_attribute("outputs:vectord3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:vectorf3_0"))
        attribute = test_node.get_attribute("outputs:vectorf3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:vectorf3_arr_0"))
        attribute = test_node.get_attribute("outputs:vectorf3_arr_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:vectorh3_0"))
        attribute = test_node.get_attribute("outputs:vectorh3_0")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:vectorh3_arr_0"))
        attribute = test_node.get_attribute("outputs:vectorh3_arr_0")
        self.assertTrue(attribute.is_valid())
