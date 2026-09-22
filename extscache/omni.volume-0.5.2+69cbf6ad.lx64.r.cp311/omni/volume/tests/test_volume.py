import numpy

import omni.kit.test
import omni.volume


class CreateFromDenseTest(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    # Actual test, notice it is "async" function, so "await" can be used if needed
    async def test_create_from_dense(self):
        ivolume = omni.volume.get_volume_interface()
        o = numpy.array([0, 0, 0]).astype(numpy.float64)

        float_x = numpy.arange(30).reshape((5, 3, 2)).astype(numpy.float32)
        float_volume = ivolume.create_from_dense(0, float_x, 1, o, "floatTest")
        self.assertEqual(ivolume.get_num_grids(float_volume), 1)
        self.assertEqual(ivolume.get_grid_class(float_volume, 0), 0)
        self.assertEqual(ivolume.get_grid_type(float_volume, 0), 1)
        self.assertEqual(ivolume.get_short_grid_name(float_volume, 0), "floatTest")
        float_index_bounding_box = ivolume.get_index_bounding_box(float_volume, 0)
        self.assertEqual(float_index_bounding_box, [(0, 0, 0), (1, 2, 4)])
        float_world_bounding_box = ivolume.get_world_bounding_box(float_volume, 0)
        self.assertEqual(float_world_bounding_box, [(0, 0, 0), (2, 3, 5)])

        double_x = numpy.arange(30).reshape((5, 3, 2)).astype(numpy.float64)
        double_volume = ivolume.create_from_dense(0, double_x, 1, o, "doubleTest")
        self.assertEqual(ivolume.get_num_grids(double_volume), 1)
        self.assertEqual(ivolume.get_grid_class(double_volume, 0), 0)
        self.assertEqual(ivolume.get_grid_type(double_volume, 0), 2)
        self.assertEqual(ivolume.get_short_grid_name(double_volume, 0), "doubleTest")
        double_index_bounding_box = ivolume.get_index_bounding_box(double_volume, 0)
        self.assertEqual(double_index_bounding_box, [(0, 0, 0), (1, 2, 4)])
        double_world_bounding_box = ivolume.get_world_bounding_box(double_volume, 0)
        self.assertEqual(double_world_bounding_box, [(0, 0, 0), (2, 3, 5)])


class OpenVDBPythonTest(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    async def test_openvdb(self):
        import openvdb


class NanoVDBPythonTest(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    async def test_nanovdb(self):
        import nanovdb
