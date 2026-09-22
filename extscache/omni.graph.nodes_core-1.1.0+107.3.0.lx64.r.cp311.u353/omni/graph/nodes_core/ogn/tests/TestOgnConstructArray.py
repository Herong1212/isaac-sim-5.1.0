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
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "bool[]", False],
                    ['inputs:input0', {'type': 'bool', 'value': True}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'bool[]', 'value': [True]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "double[]", False],
                    ['inputs:input0', {'type': 'double', 'value': 2.35423}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'double[]', 'value': [2.35423]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "float[]", False],
                    ['inputs:input0', {'type': 'float', 'value': 5.22}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'float[]', 'value': [5.22]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "half[]", False],
                    ['inputs:input0', {'type': 'half', 'value': 0.5}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'half[]', 'value': [0.5]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "int[]", False],
                    ['inputs:input0', {'type': 'int', 'value': -78}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int[]', 'value': [-78]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "int64[]", False],
                    ['inputs:input0', {'type': 'int64', 'value': -8294}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int64[]', 'value': [-8294]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "token[]", False],
                    ['inputs:input0', {'type': 'token', 'value': 'TEST'}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'token[]', 'value': ['TEST']}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "uchar[]", False],
                    ['inputs:input0', {'type': 'uchar', 'value': 2}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'uchar[]', 'value': [2]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "uint[]", False],
                    ['inputs:input0', {'type': 'uint', 'value': 123}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'uint[]', 'value': [123]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "uint64[]", False],
                    ['inputs:input0', {'type': 'uint64', 'value': 345}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'uint64[]', 'value': [345]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "double[2][]", False],
                    ['inputs:input0', {'type': 'double[2]', 'value': [1.23, 3.45]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'double[2][]', 'value': [[1.23, 3.45]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "double[3][]", False],
                    ['inputs:input0', {'type': 'double[3]', 'value': [1.23, 3.45, 6.78]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'double[3][]', 'value': [[1.23, 3.45, 6.78]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "double[4][]", False],
                    ['inputs:input0', {'type': 'double[4]', 'value': [1.23, 3.45, 6.78, 9.01]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'double[4][]', 'value': [[1.23, 3.45, 6.78, 9.01]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "matrixd[2][]", False],
                    ['inputs:input0', {'type': 'matrixd[2]', 'value': [1, 0, 0, 1]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'matrixd[2][]', 'value': [[1, 0, 0, 1]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "matrixd[3][]", False],
                    ['inputs:input0', {'type': 'matrixd[3]', 'value': [1, 0, 0, 0, 1, 0, 0, 0, 1]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'matrixd[3][]', 'value': [[1, 0, 0, 0, 1, 0, 0, 0, 1]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "matrixd[4][]", False],
                    ['inputs:input0', {'type': 'matrixd[4]', 'value': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'matrixd[4][]', 'value': [[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "float[2][]", False],
                    ['inputs:input0', {'type': 'float[2]', 'value': [1.23, 3.45]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'float[2][]', 'value': [[1.23, 3.45]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "float[3][]", False],
                    ['inputs:input0', {'type': 'float[3]', 'value': [1.23, 3.45, 6.78]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'float[3][]', 'value': [[1.23, 3.45, 6.78]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "float[4][]", False],
                    ['inputs:input0', {'type': 'float[4]', 'value': [1.23, 3.45, 6.78, 9.01]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'float[4][]', 'value': [[1.23, 3.45, 6.78, 9.01]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "half[2][]", False],
                    ['inputs:input0', {'type': 'half[2]', 'value': [0.25, 0.5]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'half[2][]', 'value': [[0.25, 0.5]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "half[3][]", False],
                    ['inputs:input0', {'type': 'half[3]', 'value': [0.25, 0.5, 0.75]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'half[3][]', 'value': [[0.25, 0.5, 0.75]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "half[4][]", False],
                    ['inputs:input0', {'type': 'half[4]', 'value': [0.25, 0.5, 0.75, 1.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'half[4][]', 'value': [[0.25, 0.5, 0.75, 1.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "int[2][]", False],
                    ['inputs:input0', {'type': 'int[2]', 'value': [1, 2]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int[2][]', 'value': [[1, 2]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "int[3][]", False],
                    ['inputs:input0', {'type': 'int[3]', 'value': [1, 2, 3]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int[3][]', 'value': [[1, 2, 3]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "int[4][]", False],
                    ['inputs:input0', {'type': 'int[4]', 'value': [1, 2, 3, 4]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int[4][]', 'value': [[1, 2, 3, 4]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "timecode[]", False],
                    ['inputs:input0', {'type': 'timecode', 'value': 2.35423}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'timecode[]', 'value': [2.35423]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "frame[4][]", False],
                    ['inputs:input0', {'type': 'frame[4]', 'value': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'frame[4][]', 'value': [[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "colord[3][]", False],
                    ['inputs:input0', {'type': 'colord[3]', 'value': [0.567, 0.567, 0.567]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'colord[3][]', 'value': [[0.567, 0.567, 0.567]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "colorf[3][]", False],
                    ['inputs:input0', {'type': 'colorf[3]', 'value': [0.56, 0.56, 0.56]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'colorf[3][]', 'value': [[0.56, 0.56, 0.56]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "colorh[3][]", False],
                    ['inputs:input0', {'type': 'colorh[3]', 'value': [0.5, 0.5, 0.5]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'colorh[3][]', 'value': [[0.5, 0.5, 0.5]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "colord[4][]", False],
                    ['inputs:input0', {'type': 'colord[4]', 'value': [0.567, 0.567, 0.567, 0.567]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'colord[4][]', 'value': [[0.567, 0.567, 0.567, 0.567]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "colorf[4][]", False],
                    ['inputs:input0', {'type': 'colorf[4]', 'value': [0.56, 0.56, 0.56, 0.56]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'colorf[4][]', 'value': [[0.56, 0.56, 0.56, 0.56]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "colorh[4][]", False],
                    ['inputs:input0', {'type': 'colorh[4]', 'value': [0.5, 0.5, 0.5, 0.5]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'colorh[4][]', 'value': [[0.5, 0.5, 0.5, 0.5]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "normald[3][]", False],
                    ['inputs:input0', {'type': 'normald[3]', 'value': [0.567, 0.567, 0.567]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'normald[3][]', 'value': [[0.567, 0.567, 0.567]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "normalf[3][]", False],
                    ['inputs:input0', {'type': 'normalf[3]', 'value': [0.56, 0.56, 0.56]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'normalf[3][]', 'value': [[0.56, 0.56, 0.56]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "normalh[3][]", False],
                    ['inputs:input0', {'type': 'normalh[3]', 'value': [0.5, 0.5, 0.5]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'normalh[3][]', 'value': [[0.5, 0.5, 0.5]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "pointd[3][]", False],
                    ['inputs:input0', {'type': 'pointd[3]', 'value': [0.567, 0.567, 0.567]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'pointd[3][]', 'value': [[0.567, 0.567, 0.567]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "pointf[3][]", False],
                    ['inputs:input0', {'type': 'pointf[3]', 'value': [0.56, 0.56, 0.56]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'pointf[3][]', 'value': [[0.56, 0.56, 0.56]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "pointh[3][]", False],
                    ['inputs:input0', {'type': 'pointh[3]', 'value': [0.5, 0.5, 0.5]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'pointh[3][]', 'value': [[0.5, 0.5, 0.5]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "quatd[4][]", False],
                    ['inputs:input0', {'type': 'quatd[4]', 'value': [0.567, 0.567, 0.567, 0.567]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'quatd[4][]', 'value': [[0.567, 0.567, 0.567, 0.567]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "quatf[4][]", False],
                    ['inputs:input0', {'type': 'quatf[4]', 'value': [0.56, 0.56, 0.56, 0.56]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'quatf[4][]', 'value': [[0.56, 0.56, 0.56, 0.56]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "quath[4][]", False],
                    ['inputs:input0', {'type': 'quath[4]', 'value': [0.5, 0.5, 0.5, 0.5]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'quath[4][]', 'value': [[0.5, 0.5, 0.5, 0.5]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "texcoordd[2][]", False],
                    ['inputs:input0', {'type': 'texcoordd[2]', 'value': [0.567, 0.567]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'texcoordd[2][]', 'value': [[0.567, 0.567]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "texcoordf[2][]", False],
                    ['inputs:input0', {'type': 'texcoordf[2]', 'value': [0.56, 0.56]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'texcoordf[2][]', 'value': [[0.56, 0.56]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "texcoordh[2][]", False],
                    ['inputs:input0', {'type': 'texcoordh[2]', 'value': [0.5, 0.5]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'texcoordh[2][]', 'value': [[0.5, 0.5]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "texcoordd[3][]", False],
                    ['inputs:input0', {'type': 'texcoordd[3]', 'value': [0.567, 0.567, 0.567]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'texcoordd[3][]', 'value': [[0.567, 0.567, 0.567]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "texcoordf[3][]", False],
                    ['inputs:input0', {'type': 'texcoordf[3]', 'value': [0.56, 0.56, 0.56]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'texcoordf[3][]', 'value': [[0.56, 0.56, 0.56]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "texcoordh[3][]", False],
                    ['inputs:input0', {'type': 'texcoordh[3]', 'value': [0.5, 0.5, 0.5]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'texcoordh[3][]', 'value': [[0.5, 0.5, 0.5]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "vectord[3][]", False],
                    ['inputs:input0', {'type': 'vectord[3]', 'value': [0.567, 0.567, 0.567]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'vectord[3][]', 'value': [[0.567, 0.567, 0.567]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "vectorf[3][]", False],
                    ['inputs:input0', {'type': 'vectorf[3]', 'value': [0.56, 0.56, 0.56]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'vectorf[3][]', 'value': [[0.56, 0.56, 0.56]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:arraySize', 1, False],
                    ['inputs:arrayType', "vectorh[3][]", False],
                    ['inputs:input0', {'type': 'vectorh[3]', 'value': [0.5, 0.5, 0.5]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'vectorh[3][]', 'value': [[0.5, 0.5, 0.5]]}, False],
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
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_ConstructArray", "omni.graph.nodes.ConstructArray", test_run, _TestGraphAndNode())
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.ConstructArray User test case #{i+1}")

    async def test_vectorized_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_ConstructArray","omni.graph.nodes.ConstructArray", test_run, _TestGraphAndNode(), 16)
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.ConstructArray User test case #{i+1}", 16)

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
            instance_setup[key] = await _test_setup_scene(self, og.Controller(allow_exists_prim=True), key, "TestNode_omni_graph_nodes_ConstructArray", "omni.graph.nodes.ConstructArray", test_data_setup[key], test_info)
        self.assertEqual(len(og.get_all_graphs()), 24)

        # We want to evaluate all graphs concurrently. Kick them all.
        # Evaluate multiple times to skip 2 serial frames and increase chances for a race condition.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        for (key, test_info) in instance_setup.items():
            _test_verify_scene(self, og.Controller(), test_data_setup[key], test_info, f"omni.graph.nodes.ConstructArray User test case instance{key}")

    async def test_data_access(self):
        test_file_name = "OgnConstructArrayTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_nodes_ConstructArray")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:arraySize"))
        attribute = test_node.get_attribute("inputs:arraySize")
        self.assertTrue(attribute.is_valid())
        expected_value = 1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:arrayType"))
        attribute = test_node.get_attribute("inputs:arrayType")
        self.assertTrue(attribute.is_valid())
        expected_value = "auto"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
