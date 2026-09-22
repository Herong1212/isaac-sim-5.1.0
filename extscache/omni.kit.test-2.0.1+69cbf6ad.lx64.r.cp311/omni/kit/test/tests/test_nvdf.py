import omni.kit.test

from ..nvdf import remove_nvdf_form, to_nvdf_form


class TestNVDF(omni.kit.test.AsyncTestCase):
    async def test_convert_basic_types(self):
        d = {
            "some_boolean": True,
            "some_int": -123,
            "some_float": 0.001,
            "array_of_string": ["a", "b"],
        }
        nv = to_nvdf_form(d)
        self.assertDictEqual(
            nv, {"b_some_boolean": True, "l_some_int": -123, "d_some_float": 0.001, "s_array_of_string": ["a", "b"]}
        )
        r = remove_nvdf_form(nv)
        self.assertDictEqual(d, r)

    async def test_convert_advanced_types(self):
        class myClass:
            def __init__(self, int_value: int, float_value: float) -> None:
                self.cl_int: int = int_value
                self.cl_float: float = float_value

        m = myClass(12, 0.1)
        d = {
            "some_list": [3, 4],
            "some_tuple": (1, 2),
            "some_class": m,
        }
        nv = to_nvdf_form(d)
        self.assertDictEqual(
            nv, {"l_some_list": [3, 4], "l_some_tuple": (1, 2), "some_class": {"l_cl_int": 12, "d_cl_float": 0.1}}
        )
        d["some_class"] = m.__dict__
        r = remove_nvdf_form(nv)
        self.assertDictEqual(d, r)

    async def test_convert_reserved_types(self):
        d = {
            "ts_anything": 2992929,
            "ts_created": 56555,
            "_id": 69988,
        }
        nv = to_nvdf_form(d)
        self.assertDictEqual(
            nv, {"ts_anything": 2992929, "ts_created": 56555, "_id": 69988}
        )
        r = remove_nvdf_form(nv)
        self.assertDictEqual(d, r)

    async def test_convert_nested(self):
        d = {
            "some_dict": {
                "some_list": [{"a": 1}, {"b": 2}],
                "some_tuple": (1, 2),
                "empty_list": [],
                "empty_tuple": (),
            }
        }
        nv = to_nvdf_form(d)
        self.assertDictEqual(
            nv, {"some_dict": {"some_list": [{"l_a": 1}, {"l_b": 2}], "l_some_tuple": (1, 2), "empty_list": [], "empty_tuple": ()}}
        )
        r = remove_nvdf_form(nv)
        self.assertDictEqual(d, r)