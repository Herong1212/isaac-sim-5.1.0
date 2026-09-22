import omni.kit.test
from carb import Float3
from omni.metropolis.utils.carb_util import CarbUtil
from pxr import Sdf, Gf
from typing import List
from isaacsim.anim.robot.utils import get_orient_with_timecode, get_translate_with_timecode, simplify_3d_points


class TestIARUtils(omni.kit.test.AsyncTestCase):
    """Test suite for animation utility functions."""

    async def setUp(self):
        """Set up test environment with a USD stage and test prims."""
        # Create new stage
        omni.usd.get_context().new_stage()
        self.stage = omni.usd.get_context().get_stage()

        # Set stage time range (start=0, end=10)
        self.stage.SetStartTimeCode(0.0)
        self.stage.SetEndTimeCode(10.0)

        await omni.kit.app.get_app().next_update_async()

        # Create test prim
        self.test_path = "/World/Test"
        self.test_prim = self.stage.DefinePrim(self.test_path, "Xform")
        await omni.kit.app.get_app().next_update_async()

        # Create transform attributes with change block
        with Sdf.ChangeBlock():
            self.translate_attr = self.test_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3)
            self.orient_attr = self.test_prim.CreateAttribute("xformOp:orient", Sdf.ValueTypeNames.Quatd)

            # Set xformOpOrder
            self.test_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, custom=False).Set(
                ["xformOp:translate", "xformOp:orient"]
            )

            # Set keyframe values
            self.translate_attr.Set(Gf.Vec3d(0, 0, 0), 0.0)
            self.translate_attr.Set(Gf.Vec3d(1, 1, 1), 1.0)
            self.translate_attr.Set(Gf.Vec3d(2, 2, 2), 2.0)

            self.orient_attr.Set(Gf.Quatd(1, 0, 0, 0), 0.0)  # Identity
            self.orient_attr.Set(Gf.Quatd(0.707, 0, 0, 0.707), 1.0)  # 90 degree rotation
            self.orient_attr.Set(Gf.Quatd(0, 0, 0, 1), 2.0)  # 180 degree rotation

        await omni.kit.app.get_app().next_update_async()

        # Verify the values were set correctly
        self.assertEqual(self.translate_attr.Get(0.0), Gf.Vec3d(0, 0, 0))
        self.assertEqual(self.translate_attr.Get(1.0), Gf.Vec3d(1, 1, 1))
        self.assertEqual(self.translate_attr.Get(2.0), Gf.Vec3d(2, 2, 2))

    async def tearDown(self):
        pass

    async def test_get_translate_exact_time(self):
        """Test translation interpolation at exact keyframe times."""
        # Test keyframe values
        await omni.kit.app.get_app().next_update_async()

        value = get_translate_with_timecode(self.test_prim, 0.0)
        self.assertEqual(value, Gf.Vec3d(0, 0, 0))

        value = get_translate_with_timecode(self.test_prim, 1.0)
        self.assertEqual(value, Gf.Vec3d(1, 1, 1))

    async def test_get_translate_interpolation(self):
        """Test translation interpolation between keyframes."""
        await omni.kit.app.get_app().next_update_async()

        # Test interpolated value at t=0.5
        value = get_translate_with_timecode(self.test_prim, 0.5)
        self.assertEqual(value, Gf.Vec3d(0.5, 0.5, 0.5))

    async def test_get_translate_loop(self):
        """Test translation looping behavior."""
        await omni.kit.app.get_app().next_update_async()

        # Test looping (t=3 should loop back to t=1)
        value = get_translate_with_timecode(self.test_prim, 3, loop=True)
        self.assertEqual(value, Gf.Vec3d(1, 1, 1))

        # Test no looping
        value = get_translate_with_timecode(self.test_prim, 3, loop=False)
        self.assertEqual(value, Gf.Vec3d(2, 2, 2))

    async def test_get_orient_exact_time(self):
        """Test orientation interpolation at exact keyframe times."""
        # Test keyframe values
        value = get_orient_with_timecode(self.test_prim, 0.0)
        self.assertEqual(value, Gf.Quatd(1, 0, 0, 0))

        value = get_orient_with_timecode(self.test_prim, 1.0)
        self.assertEqual(value, Gf.Quatd(0.707, 0, 0, 0.707))

    async def test_get_orient_interpolation(self):
        """Test orientation interpolation between keyframes."""
        # Test interpolated value at t=0.5 (should be ~45 degree rotation)
        value = get_orient_with_timecode(self.test_prim, 0.5)
        expected = Gf.Quatd(0.9239, 0, 0, 0.3827)  # ~45 degree rotation
        # Use approximate equality for quaternions due to floating point precision
        self.assertLess(abs(value.GetReal() - expected.GetReal()) ,  1e-3)
        self.assertLess((value.GetImaginary() - expected.GetImaginary()).GetLength() ,  1e-3)

    async def test_get_orient_loop(self):
        """Test orientation looping behavior."""
        # Test looping (t=3 should loop back to t=1)
        value = get_orient_with_timecode(self.test_prim, 3, loop=True)
        self.assertEqual(value, Gf.Quatd(0.707, 0, 0, 0.707))

        # Test no looping
        value = get_orient_with_timecode(self.test_prim, 3, loop=False)
        self.assertEqual(value, Gf.Quatd(0, 0, 0, 1))

    async def test_simplify_3d_points(self):
        """Test simplification of 3D points."""

        def polyline_length(points: List[Float3]) -> float:
            length = 0.0
            for i in range(1, len(points)):
                length += CarbUtil.dist3(points[i - 1], points[i])
            return length

        points = [
            Float3(-18.04433822631836, -14.728410720825195, 0),
            Float3(-17.906370162963867, -14.890584945678711, 0),
            Float3(-17.840194702148438, -14.968369483947754, 0),
            Float3(-17.65497589111328, -15.186083793640137, 0),
            Float3(-17.471811294555664, -15.401383399963379, 0),
            Float3(-17.406370162963867, -15.47830581665039, 0),
            Float3(-17.10342788696289, -15.834397315979004, 0),
            Float3(-16.906370162963867, -16.066028594970703, 0),
            Float3(-16.735044479370117, -16.267412185668945, 0),
            Float3(-16.406370162963867, -16.653751373291016, 0),
            Float3(-16.366662979125977, -16.700424194335938, 0),
            Float3(-16.255525588989258, -16.8310604095459, 0),
            Float3(-15.99828052520752, -17.133438110351562, 0),
            Float3(-15.906371116638184, -17.241472244262695, 0),
            Float3(-15.629897117614746, -17.566452026367188, 0),
            Float3(-15.406371116638184, -17.829195022583008, 0),
            Float3(-15.261514663696289, -17.999465942382812, 0),
            Float3(-14.906371116638184, -18.41691780090332, 0),
            Float3(-14.893133163452148, -18.432477951049805, 0),
            Float3(-14.856082916259766, -18.476028442382812, 0),
            Float3(-14.524752616882324, -18.865488052368164, 0),
            Float3(-14.406371116638184, -19.004638671875, 0),
            Float3(-14.156371116638184, -19.298500061035156, 0),
            Float3(-14.319999694824219, -19.34000015258789, 0),
        ]
        simplified = simplify_3d_points(points, 0.01)
        self.assertAlmostEqual(simplified[0].x, points[0].x)
        self.assertAlmostEqual(simplified[0].y, points[0].y)
        self.assertAlmostEqual(simplified[0].z, points[0].z)
        self.assertAlmostEqual(simplified[-1].x, points[-1].x)
        self.assertAlmostEqual(simplified[-1].y, points[-1].y)
        self.assertAlmostEqual(simplified[-1].z, points[-1].z)
        self.assertEqual(len(simplified), 3)
        self.assertAlmostEqual(polyline_length(simplified), polyline_length(points), 4)

        points = [
            Float3(-18.04433822631836, 14.386154174804688, 0),
            Float3(-18.00278663635254, 14.126975059509277, 0),
            Float3(-17.98940086364746, 14.043475151062012, 0),
            Float3(-17.922176361083984, 13.624150276184082, 0),
            Float3(-17.919981002807617, 13.610462188720703, 0),
            Float3(-17.906370162963867, 13.525562286376953, 0),
            Float3(-17.850561141967773, 13.177449226379395, 0),
            Float3(-17.841564178466797, 13.121325492858887, 0),
            Float3(-17.781143188476562, 12.744437217712402, 0),
            Float3(-17.760953903198242, 12.61850357055664, 0),
            Float3(-17.711645126342773, 12.310935020446777, 0),
            Float3(-17.680341720581055, 12.115680694580078, 0),
            Float3(-17.641963958740234, 11.876296997070312, 0),
            Float3(-17.599729537963867, 11.6128568649292, 0),
            Float3(-17.57240867614746, 11.44243335723877, 0),
            Float3(-17.519119262695312, 11.110032081604004, 0),
            Float3(-17.503183364868164, 11.010631561279297, 0),
            Float3(-17.438507080078125, 10.607207298278809, 0),
            Float3(-17.433977127075195, 10.57895278930664, 0),
            Float3(-17.40609359741211, 10.405027389526367, 0),
            Float3(-17.364625930786133, 10.146363258361816, 0),
            Float3(-17.35789680480957, 10.10438346862793, 0),
            Float3(-17.295207977294922, 9.713349342346191, 0),
            Float3(-17.277286529541016, 9.60155963897705, 0),
            Float3(-17.22579002380371, 9.2803373336792, 0),
            Float3(-17.19667625427246, 9.098737716674805, 0),
            Float3(-17.156370162963867, 8.847326278686523, 0),
            Float3(-17.156370162963867, 8.847326278686523, 0),
            Float3(-16.906370162963867, 8.630819320678711, 0),
            Float3(-16.656370162963867, 8.414313316345215, 0),
            Float3(-16.406370162963867, 8.197806358337402, 0),
            Float3(-16.156370162963867, 7.98129940032959, 0),
            Float3(-15.906370162963867, 7.7647929191589355, 0),
            Float3(-15.656139373779297, 7.764592170715332, 0),
            Float3(-15.65613842010498, 7.764592170715332, 0),
            Float3(-15.406136512756348, 7.7619781494140625, 0),
            Float3(-15.150028228759766, 7.759300231933594, 0),
            Float3(-14.904464721679688, 7.75673246383667, 0),
            Float3(-14.643917083740234, 7.754007816314697, 0),
            Float3(-14.598036766052246, 7.930781364440918, 0),
            Float3(-14.348036766052246, 8.14728832244873, 0),
            Float3(-14.348036766052246, 8.14728832244873, 0),
            Float3(-14.25274658203125, 8.281270980834961, 0),
            Float3(-14.184033393859863, 8.377884864807129, 0),
            Float3(-13.89316177368164, 8.786866188049316, 0),
            Float3(-13.871585845947266, 8.817203521728516, 0),
            Float3(-13.850415229797363, 8.846970558166504, 0),
            Float3(-13.681007385253906, 9.08516788482666, 0),
            Float3(-13.542486190795898, 9.279936790466309, 0),
            Float3(-13.49042797088623, 9.353133201599121, 0),
            Float3(-13.406112670898438, 9.471685409545898, 0),
            Float3(-13.299848556518555, 9.621098518371582, 0),
            Float3(-13.234238624572754, 9.713349342346191, 0),
            Float3(-13.109269142150879, 9.889063835144043, 0),
            Float3(-12.926276206970215, 10.1463623046875, 0),
            Float3(-12.918688774108887, 10.15703010559082, 0),
            Float3(-12.906371116638184, 10.174349784851074, 0),
            Float3(-12.728109359741211, 10.424996376037598, 0),
            Float3(-12.618313789367676, 10.579376220703125, 0),
            Float3(-12.537529945373535, 10.692963600158691, 0),
            Float3(-12.406371116638184, 10.87738037109375, 0),
            Float3(-12.346949577331543, 10.960929870605469, 0),
            Float3(-12.31035041809082, 11.01239013671875, 0),
            Float3(-12.156370162963867, 11.228896141052246, 0),
            Float3(-12.156370162963867, 11.445403099060059, 0),
            Float3(-12.156370162963867, 11.445403099060059, 0),
            Float3(-12.156370162963867, 11.661909103393555, 0),
            Float3(-12.156370162963867, 11.878414154052734, 0),
            Float3(-12.156370162963867, 12.094919204711914, 0),
            Float3(-12.156370162963867, 12.311426162719727, 0),
            Float3(-12.156370162963867, 12.527932167053223, 0),
            Float3(-12.156370162963867, 12.744439125061035, 0),
            Float3(-12.156370162963867, 12.960945129394531, 0),
            Float3(-12.156370162963867, 13.177450180053711, 0),
            Float3(-12.156370162963867, 13.393957138061523, 0),
            Float3(-12.156370162963867, 13.610464096069336, 0),
            Float3(-12.156370162963867, 13.826971054077148, 0),
            Float3(-12.0, 14.0, 0),
        ]
        simplified = simplify_3d_points(points, 0.01)
        self.assertAlmostEqual(simplified[0].x, points[0].x)
        self.assertAlmostEqual(simplified[0].y, points[0].y)
        self.assertAlmostEqual(simplified[0].z, points[0].z)
        self.assertAlmostEqual(simplified[-1].x, points[-1].x)
        self.assertAlmostEqual(simplified[-1].y, points[-1].y)
        self.assertAlmostEqual(simplified[-1].z, points[-1].z)
        self.assertEqual(len(simplified), 9)
        self.assertAlmostEqual(polyline_length(simplified), polyline_length(points), 4)

        points = [
            Float3(-13.281579971313477, 9.396337509155273, 0),
            Float3(-13.230247497558594, 9.280077934265137, 0),
            Float3(-13.121393203735352, 9.033540725708008, 0),
            Float3(-13.038535118103027, 8.845880508422852, 0),
            Float3(-12.902830123901367, 8.538529396057129, 0),
            Float3(-12.846392631530762, 8.410706520080566, 0),
            Float3(-12.811838150024414, 8.332446098327637, 0),
            Float3(-12.654919624328613, 7.977049827575684, 0),
            Float3(-12.502281188964844, 7.63134765625, 0),
            Float3(-12.464818954467773, 7.546502113342285, 0),
            Float3(-12.405272483825684, 7.4116387367248535, 0),
            Float3(-12.274288177490234, 7.1149797439575195, 0),
            Float3(-12.192726135253906, 6.930253982543945, 0),
            Float3(-12.083230972290039, 6.6822638511657715, 0),
            Float3(-11.906371116638184, 6.281704425811768, 0),
            Float3(-11.89204216003418, 6.249251842498779, 0),
            Float3(-11.883171081542969, 6.229159832000732, 0),
            Float3(-11.700852394104004, 5.816237926483154, 0),
            Float3(-11.573612213134766, 5.528059959411621, 0),
            Float3(-11.509662628173828, 5.3832244873046875, 0),
            Float3(-11.406371116638184, 5.149285793304443, 0),
            Float3(-11.318472862243652, 4.950211048126221, 0),
            Float3(-11.264054298400879, 4.826960563659668, 0),
            Float3(-11.127284049987793, 4.517198085784912, 0),
            Float3(-10.954497337341309, 4.125864028930664, 0),
            Float3(-10.936094284057617, 4.0841851234436035, 0),
            Float3(-10.906371116638184, 4.016866683959961, 0),
            Float3(-10.744905471801758, 3.651172637939453, 0),
            Float3(-10.644940376281738, 3.4247665405273438, 0),
            Float3(-10.553716659545898, 3.2181596755981445, 0),
            Float3(-10.406371116638184, 2.8844454288482666, 0),
            Float3(-10.362527847290039, 2.7851474285125732, 0),
            Float3(-10.335384368896484, 2.723670721054077, 0),
            Float3(-10.17133903503418, 2.3521347045898438, 0),
            Float3(-10.025827407836914, 2.0225741863250732, 0),
            Float3(-9.98015022277832, 1.9191218614578247, 0),
            Float3(-9.906371116638184, 1.7520238161087036, 0),
            Float3(-9.788961410522461, 1.4861093759536743, 0),
            Float3(-9.71627140045166, 1.3214784860610962, 0),
            Float3(-9.597772598266602, 1.053096890449524, 0),
            Float3(-9.406715393066406, 0.6203823089599609, 0),
            Float3(-9.406583786010742, 0.6200842261314392, 0),
            Float3(-9.406371116638184, 0.6196025609970093, 0),
            Float3(-9.215394973754883, 0.18707157671451569, 0),
            Float3(-9.097159385681152, -0.08071376383304596, 0),
            Float3(-9.024206161499023, -0.24594110250473022, 0),
            Float3(-8.906371116638184, -0.5128188133239746, 0),
            Float3(-8.833017349243164, -0.6789538860321045, 0),
            Float3(-8.787603378295898, -0.7818101048469543, 0),
            Float3(-8.641828536987305, -1.1119667291641235, 0),
            Float3(-8.478046417236328, -1.482906699180603, 0),
            Float3(-8.450639724731445, -1.5449795722961426, 0),
            Float3(-8.406371116638184, -1.6452409029006958, 0),
            Float3(-8.259450912475586, -1.977992057800293, 0),
            Float3(-8.168490409851074, -2.1840031147003174, 0),
            Float3(-8.068262100219727, -2.4110050201416016, 0),
            Float3(-7.906371593475342, -2.777661085128784, 0),
            Float3(-7.877072811126709, -2.844017744064331, 0),
            Float3(-7.858933448791504, -2.8851003646850586, 0),
            Float3(-7.68588399887085, -3.2770302295684814, 0),
            Float3(-7.549376964569092, -3.5861966609954834, 0),
            Float3(-7.494694709777832, -3.71004319190979, 0),
            Float3(-7.406371593475342, -3.910080909729004, 0),
            Float3(-7.3035054206848145, -4.143056392669678, 0),
            Float3(-7.2398200035095215, -4.287294387817383, 0),
            Float3(-7.112317085266113, -4.57606840133667, 0),
            Float3(-6.930263996124268, -4.988389492034912, 0),
            Float3(-6.921128273010254, -5.00908088684082, 0),
            Float3(-6.906371593475342, -5.042502403259277, 0),
            Float3(-6.7299394607543945, -5.442093372344971, 0),
            Float3(-6.6207075119018555, -5.689485549926758, 0),
            Float3(-6.538749694824219, -5.875106334686279, 0),
            Float3(-6.406371593475342, -6.174921989440918, 0),
            Float3(-6.347561359405518, -6.3081183433532715, 0),
            Float3(-6.311151027679443, -6.390582084655762, 0),
            Float3(-6.156371593475342, -6.7411322593688965, 0),
            Float3(-6.010000228881836, -6.989999771118164, 0),
        ]
        simplified = simplify_3d_points(points, 0.01)
        self.assertAlmostEqual(simplified[0].x, points[0].x)
        self.assertAlmostEqual(simplified[0].y, points[0].y)
        self.assertAlmostEqual(simplified[0].z, points[0].z)
        self.assertAlmostEqual(simplified[-1].x, points[-1].x)
        self.assertAlmostEqual(simplified[-1].y, points[-1].y)
        self.assertAlmostEqual(simplified[-1].z, points[-1].z)
        self.assertEqual(len(simplified), 3)
        self.assertAlmostEqual(polyline_length(simplified), polyline_length(points), 4)

        points = [Float3(0, 0, 0), Float3(3, 0, 0)]
        simplified = simplify_3d_points(points, 0.01)
        # Should do absolutely nothing if there's nothing to be done
        self.assertAlmostEqual(simplified[0].x, points[0].x, 10)
        self.assertAlmostEqual(simplified[0].y, points[0].y, 10)
        self.assertAlmostEqual(simplified[0].z, points[0].z, 10)
        self.assertAlmostEqual(simplified[-1].x, points[-1].x, 10)
        self.assertAlmostEqual(simplified[-1].y, points[-1].y, 10)
        self.assertAlmostEqual(simplified[-1].z, points[-1].z, 10)
        self.assertEqual(len(simplified), 2)
        self.assertAlmostEqual(polyline_length(simplified), polyline_length(points), 10)
