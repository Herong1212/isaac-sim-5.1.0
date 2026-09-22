from enum import Enum
import random
import regex

import numpy as np

from omni.metropolis.utils.rand_util import RandUtil
from omni.metropolis.utils.rotation_util import RotationUtil

from .safe_eval import eval_expression
from ..py3dbp import Packer, Bin, Item
from ..utility.misc import (
    ensured_retrieve,
    error,
    get_relative_paths_of_suffix,
    tentative_retrieve,
)
from ..utility.scene import create_xform_prim, get_points_trimesh, scale_aabb

AWAIT_HARMONIZATION = "@@@@@"


class HarmonizerState(Enum):
    UNUSED = 0
    ABSORBING = 1
    REFLECTING = 2


def has_macro(value):
    return len(regex.findall("\$\[.*?\]", value)) > 0  # noqa


def get_macros(value):
    # here it unwraps patterns enclosed in $[] only once; for example, from $[abc$[de]]f$[gh] we get abc$[de] and gh
    # further, corresponding AttributeExpression are created
    return regex.findall("\$\[((?>[^\$\[\]]+|\[.*?\]|(?R))*)\]", value)  # noqa


class Description:
    def __init__(self, config, scene):
        self.mutable_elements = []
        self.harmonizers = []
        self.context = self.resolve_placeholders("", config)  # symbols are created and wired up
        for m in self.mutable_elements:
            m.context = self.context
        self.mapping = []
        self.scene = scene

    def initialize(self, index, overwrite_seed=None):
        for m in self.mutable_elements:
            m.initialize()
        for h in self.harmonizers:
            h.initialize()
        self.seed = ensured_retrieve("seed", self.context, int) + index if overwrite_seed is None else overwrite_seed
        random.seed(self.seed)
        self.mapping = {"seed": self.seed, "num_frames": self.scene.num_frames}

    def get_distributed_attribute_mutable_element(self, name, attribute_desc):
        distribution_type = ensured_retrieve("distribution_type", attribute_desc, str)
        if distribution_type == "range":
            return AttributeRange(
                self,
                name,
                ensured_retrieve("start", attribute_desc),
                ensured_retrieve("end", attribute_desc),
                tentative_retrieve("seed", attribute_desc),
            )
        if distribution_type == "folder":
            return AttributeFolder(
                self,
                name,
                ensured_retrieve("value", attribute_desc),
                ensured_retrieve("suffix", attribute_desc),
                tentative_retrieve("index", attribute_desc),
                tentative_retrieve("seed", attribute_desc),
            )
        if distribution_type == "set":
            return AttributeSet(
                self,
                name,
                ensured_retrieve("values", attribute_desc),
                tentative_retrieve("index", attribute_desc),
                tentative_retrieve("seed", attribute_desc),
            )
        if distribution_type == "geometry":
            return AttributeGeometry(
                self, name, ensured_retrieve("file", attribute_desc), tentative_retrieve("seed", attribute_desc)
            )
        if distribution_type == "camera_frustum":
            return AttributeCameraFrustum(
                self,
                name,
                ensured_retrieve("camera_parameters", attribute_desc),
                ensured_retrieve("distance_min", attribute_desc),
                ensured_retrieve("distance_max", attribute_desc),
                ensured_retrieve("screen_space_range", attribute_desc),
            )
        if distribution_type == "harmonized":
            return AttributeHarmonized(
                self,
                name,
                ensured_retrieve("harmonizer_name", attribute_desc),
                ensured_retrieve("pitch", attribute_desc),
                tentative_retrieve("index", attribute_desc),
                tentative_retrieve("count", attribute_desc),
            )

        error(f'unrecognized distribution type "{distribution_type}" in "{name}"')

    def get_harmonizer(self, name, attribute_desc):
        harmonizer_type = ensured_retrieve("harmonizer_type", attribute_desc, str)
        if harmonizer_type == "permutate":
            return HarmonizerPermutate(self, name)
        if harmonizer_type == "bin_pack":
            return HarmonizerBinPack(
                self,
                name,
                ensured_retrieve("bin_size", attribute_desc),
                tentative_retrieve("index", attribute_desc),
                tentative_retrieve("count", attribute_desc),
            )
        if harmonizer_type == "position_sample":
            return HarmonizerPositionSample(
                self,
                name,
                ensured_retrieve("zone", attribute_desc),
                ensured_retrieve("subtracted_zones", attribute_desc),
                ensured_retrieve("minimum_distance", attribute_desc),
                tentative_retrieve("index", attribute_desc),
                tentative_retrieve("count", attribute_desc),
            )
        error(f'unrecognized harmonizer type "{harmonizer_type}" in "{name}"')

    def resolve_string(self, name, value, index_mapping=None):
        index_mapping = {} if index_mapping is None else index_mapping
        value = value.strip()
        if value.startswith("$[") and value.endswith("]") and value.count("$[") == 1:
            return AttributeReference(self, name, value[2:-1])
        if has_macro(value):
            return AttributeExpression(self, name, value, index_mapping)
        return value

    # create symbols
    def resolve_placeholders(self, name, description_item, index_mapping=None):
        index_mapping = {} if index_mapping is None else index_mapping
        if isinstance(description_item, (float, int, bool)):
            return description_item
        if isinstance(description_item, str):
            return self.resolve_string(name, description_item, index_mapping)
        if isinstance(description_item, list):
            for i, item in enumerate(description_item):
                description_item[i] = self.resolve_placeholders(f"{name}~{i}", item, index_mapping)
            return description_item
        if isinstance(description_item, dict):
            if "distribution_type" in description_item:
                return self.get_distributed_attribute_mutable_element(name, description_item)
            elif "harmonizer_type" in description_item:
                return self.get_harmonizer(name, description_item)
            else:
                for key in description_item:
                    description_item[key] = self.resolve_placeholders(
                        f"{name}/{key}", description_item[key], index_mapping
                    )
                return description_item
        else:
            error(f"unknown type {type(description_item)} in config")  # should not reach here though


class Harmonizer:
    def __init__(self, description, name):
        self.name = name
        self.description = description
        description.harmonizers.append(self)

    def absorb(self, attr_name, pitch):
        self.input[attr_name] = pitch

    def reflect(self, mutable_name):
        return self.output[mutable_name]

    def harmonize(self, is_init_frame):
        pass

    def initialize(self):
        self.input = {}
        self.output = {}
        self.state = HarmonizerState.UNUSED

    def to_dict(self):
        return {
            "harmonizer_type": self.harmonizer_type,
        }


class HarmonizerPermutate(Harmonizer):
    def __init__(self, description, name):
        super().__init__(description, name)
        self.harmonizer_type = "permutate"

    def harmonize(self, is_init_frame):
        if is_init_frame:
            return
        values = list(self.input.values())
        random.shuffle(values)
        for i, key in enumerate(self.input):
            self.output[key] = values[i]


def get_dimension(min_xyz, max_xyz):
    return [max_xyz[0] - min_xyz[0], max_xyz[1] - min_xyz[1], max_xyz[2] - min_xyz[2]]


def serialize_packer(packer):
    serialized_packer = {}
    packer_bin = packer.bins[0]
    for item in packer_bin.items:
        serialized_packer[item.name] = {
            "fitted": True,
            "position": [float(item.position[0]), float(item.position[1]), float(item.position[2])],
            "rotation_type": int(item.rotation_type),
        }
    for item in packer_bin.unfitted_items:
        serialized_packer[item.name] = {"fitted": False}
    return serialized_packer


def calc_box_xform(name, aabb, packer, bin_size):
    if not packer[name]["fitted"]:
        return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [10000, 0, 0, 1]]
    else:
        dimension = get_dimension(aabb[0], aabb[1])

        translate_local = [
            -(aabb[0][0] + aabb[1][0]) / 2,
            -(aabb[0][1] + aabb[1][1]) / 2,
            -(aabb[0][2] + aabb[1][2]) / 2,
        ]
        translate_local_xform = np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [translate_local[0], translate_local[1], translate_local[2], 1]]
        )

        if packer[name]["rotation_type"] == 0:
            rotate_xform_3d = np.identity(3)
            dimension_offset = [dimension[0], dimension[1], dimension[2]]
        elif packer[name]["rotation_type"] == 1:
            rotate_xform_3d = RotationUtil.rot_z_np(90)
            dimension_offset = [dimension[1], dimension[0], dimension[2]]
        elif packer[name]["rotation_type"] == 2:
            rotate_xform_3d = RotationUtil.rot_z_np(90) @ RotationUtil.rot_x_np(90)
            dimension_offset = [dimension[1], dimension[2], dimension[0]]  # z uses what's originally x as offset
        elif packer[name]["rotation_type"] == 3:
            rotate_xform_3d = RotationUtil.rot_y_np(90)
            dimension_offset = [dimension[2], dimension[1], dimension[0]]
        elif packer[name]["rotation_type"] == 4:
            rotate_xform_3d = RotationUtil.rot_z_np(90) @ RotationUtil.rot_y_np(90)
            dimension_offset = [dimension[2], dimension[0], dimension[1]]
        elif packer[name]["rotation_type"] == 5:
            rotate_xform_3d = RotationUtil.rot_x_np(90)
            dimension_offset = [dimension[0], dimension[2], dimension[1]]
        rotate_xform = np.identity(4)
        rotate_xform[:3, :3] = rotate_xform_3d

        position = np.array(packer[name]["position"]) + np.array(dimension_offset) / 2 - np.array(bin_size) / 2
        position_xform = np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [position[0], position[1], position[2], 1]]
        )

        return (translate_local_xform @ rotate_xform @ position_xform).tolist()


class HarmonizerBinPack(Harmonizer):
    def __init__(self, description, name, bin_size, ref_index=None, ref_count=None):
        super().__init__(description, name)
        self.harmonizer_type = "bin_pack"
        self.ref_index_mapping = {"index": ref_index, "count": ref_count}
        self.bin_size = description.resolve_placeholders(f"{name}", bin_size, self.ref_index_mapping)
        self.resolved_bin_size = None

    def harmonize(self, is_init_frame):
        if is_init_frame:
            return
        bin_size = resolve_value_generic(
            self.bin_size, self.description.mapping | self.ref_index_mapping, is_init_frame
        )
        self.resolved_bin_size = bin_size

        packer = Packer()
        packer.add_bin(Bin(self.name, bin_size[0], bin_size[1], bin_size[2], 1))
        for name, aabb in self.input.items():
            x, y, z = get_dimension(aabb[0], aabb[1])
            packer.add_item(Item(name, x, y, z, 0))
            # print(name, aabb)
        packer.pack()
        packer = serialize_packer(packer)

        num_packed_objects = 0
        for name, aabb in self.input.items():
            self.output[name] = calc_box_xform(name, aabb, packer, bin_size)
            if packer[name]["fitted"]:
                num_packed_objects += 1
        # print("packed: ", num_packed_objects)

    def to_dict(self):
        _ = super().to_dict()
        _.update({"bin_size": self.resolved_bin_size})
        return _


def is_point_in_range(point, lower_bound, upper_bound):
    return np.all(np.greater_equal(np.array(point), np.array(lower_bound))) and np.all(
        np.less_equal(point, upper_bound)
    )


def random_point_in_range(lower_bound, upper_bound):
    return [
        RandUtil.rand_range(lower_bound[0], upper_bound[0]),
        RandUtil.rand_range(lower_bound[1], upper_bound[1]),
        RandUtil.rand_range(lower_bound[2], upper_bound[2]),
    ]


def get_distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))


def get_random_point(zone, subtracted_zones, selected_points, minimum_distance):
    point = random_point_in_range(zone[0], zone[1])
    reject_count = 0
    while any(is_point_in_range(point, z[0], z[1]) for z in subtracted_zones) or any(
        get_distance(point, p) < minimum_distance for p in selected_points
    ):
        reject_count += 1
        if reject_count >= 10e4:
            error("max rejected samples reached.")
        point = random_point_in_range(zone[0], zone[1])
    return point


class HarmonizerPositionSample(Harmonizer):
    def __init__(self, description, name, zone, subtracted_zones, minimum_distance, ref_index=None, ref_count=None):
        super().__init__(description, name)
        self.harmonizer_type = "position_sample"
        self.ref_index_mapping = {"index": ref_index, "count": ref_count}
        self.zone = description.resolve_placeholders(f"{name}", zone, self.ref_index_mapping)
        self.subtracted_zones = description.resolve_placeholders(f"{name}", subtracted_zones, self.ref_index_mapping)
        self.minimum_distance = description.resolve_placeholders(f"{name}", minimum_distance, self.ref_index_mapping)

    def harmonize(self, is_init_frame):
        if is_init_frame:
            return
        zone = resolve_value_generic(self.zone, self.description.mapping | self.ref_index_mapping, is_init_frame)
        subtracted_zones = resolve_value_generic(
            self.subtracted_zones, self.description.mapping | self.ref_index_mapping, is_init_frame
        )
        minimum_distance = resolve_value_generic(
            self.minimum_distance, self.description.mapping | self.ref_index_mapping, is_init_frame
        )
        sampled_points = []
        while len(sampled_points) < len(self.input):
            sampled_points.append(get_random_point(zone, subtracted_zones, sampled_points, minimum_distance))
        for i, key in enumerate(self.input):
            self.output[key] = sampled_points[i]


class MutableElement:
    def __init__(self, description, name, ref_index=None, ref_count=None):
        self.name = name
        self.initiated_resolution = False  # to detect cyclic reference
        self.description = description
        description.mutable_elements.append(self)
        self.await_harmonization = False
        self.ref_index_mapping = {"index": ref_index, "count": ref_count}

    def resolve(self, is_init_frame):
        pass

    # mutable elements that have not resolve, resolve its value
    def get_value(self, is_init_frame):
        if self.initiated_resolution:
            error(f'cyclic reference is detected. "{self.name}" is depending on itself!')
        self.initiated_resolution = True
        if not self.resolved:
            self.resolve(is_init_frame)
            if not self.await_harmonization and self.value != AWAIT_HARMONIZATION:
                self.resolved = True
        self.initiated_resolution = False
        if self.await_harmonization:
            return AWAIT_HARMONIZATION
        return self.value

    def initialize(self):
        self.resolved = False
        self.value = None

    def set_seed(self, is_init_frame):
        seed = (
            resolve_value_generic(self.seed, self.description.mapping, is_init_frame) if self.seed is not None else None
        )
        RandUtil.attribute_seed(self.name, self.description.seed, seed)


# resolves the values recursively
def resolve_value_generic(value, mapping=None, is_init_frame=False):
    mapping = {} if mapping is None else mapping
    if isinstance(value, MutableElement):
        return value.get_value(is_init_frame)
    if isinstance(value, Harmonizer):
        return value.to_dict()
    if isinstance(value, (float, int, bool, str)):
        return value
    if isinstance(value, list):
        data = []
        await_harmonization = False
        for item in value:
            _value = resolve_value_generic(item, mapping, is_init_frame)
            if _value == AWAIT_HARMONIZATION:
                await_harmonization = True
            data.append(_value)
        if await_harmonization:
            return AWAIT_HARMONIZATION
        return data
    if isinstance(value, dict):
        data = {}
        await_harmonization = False
        for key in value:
            if key in mapping:
                data[key] = mapping[key]
                continue
            _value = resolve_value_generic(value[key], mapping, is_init_frame)
            if _value == AWAIT_HARMONIZATION:
                await_harmonization = True
            data[key] = _value
        if await_harmonization:
            return AWAIT_HARMONIZATION
        return data
    error(f"unknown type {type(value)} in symbols")  # should not reach here though


def resolve_scene(description, is_init_frame=False):
    metadata = AWAIT_HARMONIZATION
    while metadata == AWAIT_HARMONIZATION:
        metadata = resolve_value_generic(description.context, description.mapping, is_init_frame)
        for h in description.harmonizers:
            if h.state == HarmonizerState.ABSORBING:
                h.harmonize(is_init_frame)
                h.state = HarmonizerState.REFLECTING
    return metadata


# resolve relative macro's absolute name
def get_absolute_reference(path):
    names = path.split("/")
    res = []
    for name in names:
        if (
            name == ".."
        ):  # there is a "" at the beginning so popping once at the root is fine but further popping causes error
            # - TODO more detailed error handling
            res.pop()
        else:
            res.append(name)
    return "/".join(res)


# calling_context: the mutable element name that intiates referencing
# (AttributeReference, AttributeExpression, AttributHarmonized)
# context: the context (a dict) to find requested reference
# outer_context: if not found in local context, fall back to the globalest context
# retrieves referenced value; and it only resolve when necessary (meeting a mutable that resolves as a list)
def resolve_reference(outer_context, context, calling_context, reference, mapping=None):
    mapping = {} if mapping is None else mapping
    entering_reference = reference
    if reference in mapping:  # special value, like seed
        return mapping[reference]
    reference = reference.strip()
    if not reference.startswith(
        "/"
    ):  # it is a macro relative to current calling context, so we resolve its absolute name
        reference = get_absolute_reference(calling_context[: calling_context.rfind("/") + 1] + reference)
    reference = reference[1:]
    nxt = reference.find("/")
    if nxt != -1:  # there are still children to unpack
        key = reference[:nxt]
        reference = reference[nxt:]
        if key.find("~") != -1:  # retrieve from a list: a~0 is a[0]
            keys = key.split("~")
            context = ensured_retrieve(keys[0], context)[int(keys[1])]
        else:
            context = ensured_retrieve(key, context)
        return resolve_reference(outer_context, context, None, reference, mapping)
    else:  # this is the end
        if reference.find("~") != -1:
            keys = reference.split("~")
            if (
                keys[0] not in context
            ):  # TODO: need to prevent recursive reference; if not find in local, fall back to global
                return resolve_reference(outer_context, outer_context, None, "/" + reference, mapping)
            referred_item = context[keys[0]]
            if isinstance(referred_item, MutableElement):  # in this case it resolves to a list (often a range)
                referred_item = resolve_value_generic(referred_item, mapping)  # if it's a harmonized attr...
            return referred_item[int(keys[1])]
        else:
            if (
                reference not in context
            ):  # this is to prevent recursive reference; if not find in local, fall back to global
                if entering_reference == "/" + reference:
                    error(f"not found reference: {entering_reference}")
                return resolve_reference(outer_context, outer_context, None, "/" + reference, mapping)
            return context[reference]


class AttributeReference(MutableElement):
    def __init__(self, description, name, ref_key):
        super().__init__(description, name)
        self.ref_key = ref_key

    def resolve(self, is_init_frame):
        _value = resolve_value_generic(
            resolve_reference(self.context, self.context, self.name, self.ref_key, self.description.mapping),
            self.description.mapping,
            is_init_frame,
        )
        if isinstance(_value, (list, dict)):
            self.value = resolve_value_generic(_value, self.description.mapping, is_init_frame)
        else:
            self.value = _value


class AttributeExpression(MutableElement):
    def __init__(self, description, name, expression, index_mapping=None):
        super().__init__(description, name)
        self.expression = expression
        self.index_mapping = {} if index_mapping is None else index_mapping
        self.macros = get_macros(expression)
        for i, macro in enumerate(self.macros):
            if has_macro(macro):
                # self.macros[i] = AttributeExpression(description, f'{name}/macro_{i}', macro)
                self.macros[i] = AttributeExpression(
                    description, f"{name}", macro, self.index_mapping
                )  # the inner macro should have the same name context

    def resolve(self, is_init_frame):
        expression = self.expression
        for macro in self.macros:
            if isinstance(macro, str):
                resolved_macro_value = resolve_value_generic(
                    resolve_reference(
                        self.context, self.context, self.name, macro, self.description.mapping | self.index_mapping
                    ),
                    self.description.mapping | self.index_mapping,
                    is_init_frame,
                )
                if resolved_macro_value is None or resolved_macro_value == AWAIT_HARMONIZATION:
                    self.value = resolved_macro_value
                    return
                expression = expression.replace(f"$[{macro}]", str(resolved_macro_value))
            elif isinstance(macro, AttributeExpression):
                resolved_macro = resolve_value_generic(macro, self.description.mapping, is_init_frame)
                resolved_macro_value = resolve_value_generic(
                    resolve_reference(
                        self.context,
                        self.context,
                        self.name,
                        resolved_macro,
                        self.description.mapping | self.index_mapping,
                    ),
                    self.description.mapping | self.index_mapping,
                    is_init_frame,
                )
                if resolved_macro_value is None or resolved_macro_value == AWAIT_HARMONIZATION:
                    self.value = resolved_macro_value
                    return
                expression = expression.replace(f"$[{macro.expression}]", str(resolved_macro_value))
            else:
                error(f"invalid type {type(macro)} in {self.name}")
        self.value = eval_expression(expression)


def get_transform_opeartor_key_index(transform_operators, key):
    indices = {}
    for i, op in enumerate(transform_operators):
        # op is a dict of form {'translate': xxx}
        indices[list(op.keys())[0]] = i
    if key in indices:
        return indices[key]
    return None


class AttributeHarmonized(MutableElement):
    def __init__(self, description, name, harmonizer_name, pitch, ref_index=None, ref_count=None):
        super().__init__(description, name, ref_index, ref_count)
        self.pitch = description.resolve_placeholders(f"{name}/pitch", pitch, self.ref_index_mapping)
        self.harmonizer_name = description.resolve_placeholders(f"{name}", harmonizer_name, self.ref_index_mapping)

    def resolve(self, is_init_frame=False):
        if is_init_frame:
            self.await_harmonization = False  # can't harmonize during scene creation
            return
        harmonizer_name = resolve_value_generic(
            self.harmonizer_name, self.description.mapping | self.ref_index_mapping, is_init_frame
        )
        harmonizer = ensured_retrieve(harmonizer_name, self.context, Harmonizer)
        if (
            harmonizer.state == HarmonizerState.REFLECTING
        ):  # the harmonized value is ready to be dispatched to the attribute harmonized
            self.value = harmonizer.reflect(self.name)
            self.await_harmonization = False
        else:
            if harmonizer.state == HarmonizerState.UNUSED:  # harmonization has not started; trigger it
                harmonizer.state = HarmonizerState.ABSORBING
            if self.pitch == "local_aabb":
                # we need to query fabric info from the mutable; the scene is updated
                # e.g. self.name: /mutable_name/transform_operators~0/transform
                mutable_name = self.name[: self.name.rfind("/")]  # e.g. /mutable_name/transform_operators~0
                usd_path = str(
                    resolve_value_generic(
                        resolve_reference(
                            self.context, self.context, mutable_name, "usd_path", self.description.mapping
                        ),
                        self.description.mapping,
                        is_init_frame,
                    )
                )
                transform_operators = resolve_reference(
                    self.context, self.context, mutable_name, "transform_operators", self.description.mapping
                )
                scale_index = get_transform_opeartor_key_index(transform_operators, "scale")
                if scale_index is not None:
                    # e.g. /mutable_name/transform_operators~{scale_index}
                    scale_path = f"{mutable_name[: mutable_name.rfind('/')]}/transform_operators~{scale_index}"
                    scale = resolve_value_generic(
                        resolve_reference(self.context, self.context, None, scale_path, self.description.mapping),
                        self.description.mapping,
                        is_init_frame,
                    )["scale"]
                else:
                    scale = [1, 1, 1]
                mutable_name = mutable_name[
                    1 : mutable_name.rfind("/")
                ]  # mutables are defined as children of the root, e.g. mutable_name
                mutable = self.description.scene.mutables[mutable_name]
                aabb = mutable.update_usd(usd_path, True)
                pitch = scale_aabb(aabb, scale)
            else:
                pitch = resolve_value_generic(
                    self.pitch, self.description.mapping | self.ref_index_mapping, is_init_frame
                )
            harmonizer.absorb(self.name, pitch)

    def initialize(self):
        super().initialize()
        self.await_harmonization = True


class AttributeRange(MutableElement):
    def __init__(self, description, name, start, end, seed=None):
        super().__init__(description, name)
        # self.start = description.resolve_placeholders(f'{name}/start', start)
        # self.end = description.resolve_placeholders(f'{name}/end', end)
        self.start = description.resolve_placeholders(f"{name}", start)
        self.end = description.resolve_placeholders(f"{name}", end)
        self.seed = description.resolve_placeholders(f"{name}", seed) if seed is not None else None

    def resolve(self, is_init_frame):
        start, end = resolve_value_generic(self.start, self.description.mapping, is_init_frame), resolve_value_generic(
            self.end, self.description.mapping, is_init_frame
        )
        self.set_seed(is_init_frame)
        if isinstance(start, (float, int)) and isinstance(end, (float, int)):
            self.value = RandUtil.rand_range(start, end)
        elif isinstance(start, list) and isinstance(end, list):
            if len(self.start) != len(self.end):
                error(f"mismatching start/end dimension in range, in {self.name}")
            self.value = RandUtil.rand_range_list(start, end)
        else:
            error(f"invalid types for start {type(start)} and/or {type(end)} in {self.name}")


# point sampling from mesh
class AttributeGeometry(MutableElement):
    def __init__(self, description, name, file, seed=None):
        super().__init__(description, name)
        self.file = description.resolve_placeholders(f"{name}", file)

    def resolve(self, is_init_frame):
        xform_prim = create_xform_prim("/Scene/temp")
        xform_prim.GetReferences().AddReference(self.file)
        points = get_points_trimesh(xform_prim)
        self.value = list(random.choice(points))


class AttributeFolder(MutableElement):
    def __init__(self, description, name, folder, suffix, index, seed=None):
        super().__init__(description, name)
        self.folder = description.resolve_placeholders(f"{name}", folder)
        self.suffix = description.resolve_placeholders(f"{name}", suffix)
        self.index = description.resolve_placeholders(f"{name}", index) if index is not None else None
        self.values = None
        self.seed = description.resolve_placeholders(f"{name}", seed) if seed is not None else None

    def resolve(self, is_init_frame):
        folder = resolve_value_generic(self.folder, self.description.mapping, is_init_frame)
        suffix = resolve_value_generic(self.suffix, self.description.mapping, is_init_frame)
        if self.values is None:
            self.values = get_relative_paths_of_suffix(folder, suffix, True)
            if self.values is None or len(self.values) == 0:
                error(f"folder {folder} is empty")
            self.value = self.values  # initial frame
        else:
            if self.index is not None:
                index = resolve_value_generic(self.index, self.description.mapping, is_init_frame)
                self.value = self.values[int(index) % len(self.values)]
            else:
                self.set_seed(is_init_frame)
                self.value = random.choice(self.values)


class AttributeSet(MutableElement):
    def __init__(self, description, name, values, index, seed=None):
        super().__init__(description, name)
        self.values = description.resolve_placeholders(f"{name}", values)
        self.index = description.resolve_placeholders(f"{name}", index) if index is not None else None
        self.seed = description.resolve_placeholders(f"{name}", seed) if seed is not None else None

    def resolve(self, is_init_frame):
        values = resolve_value_generic(self.values, self.description.mapping, is_init_frame)
        if is_init_frame:
            self.value = values
        elif self.index is not None:
            index = resolve_value_generic(self.index, self.description.mapping, is_init_frame)
            self.value = values[int(index) % len(values)]
        else:
            self.set_seed(is_init_frame)
            self.value = random.choice(values)


# TODO msoriano: REdundant remove (in metadata.py)
def camera_ov_to_standard(camera_parameters):
    standard_camera_parameters = {}
    for key, value in camera_parameters.items():
        if key not in ["focal_length", "horizontal_aperture"]:
            standard_camera_parameters[key] = value
    standard_camera_parameters["pinhole_ratio"] = (
        2
        * camera_parameters["focal_length"]
        / camera_parameters["horizontal_aperture"]
        * camera_parameters["screen_width"]
        / camera_parameters["screen_height"]
    )
    return standard_camera_parameters


class AttributeCameraFrustum(MutableElement):
    def __init__(self, description, name, camera_parameters, distance_min, distance_max, screen_space_range):
        super().__init__(description, name)
        self.camera_parameters = description.resolve_placeholders(f"{name}", camera_parameters)
        self.distance_min = description.resolve_placeholders(f"{name}", distance_min)
        self.distance_max = description.resolve_placeholders(f"{name}", distance_max)
        self.screen_space_range = description.resolve_placeholders(f"{name}", screen_space_range)

    def resolve(self, is_init_frame):
        camera_parameters = resolve_value_generic(self.camera_parameters, self.description.mapping, is_init_frame)
        distance_min = resolve_value_generic(self.distance_min, self.description.mapping, is_init_frame)
        distance_max = resolve_value_generic(self.distance_max, self.description.mapping, is_init_frame)
        screen_space_range = resolve_value_generic(self.screen_space_range, self.description.mapping, is_init_frame)
        standard_camera_parameters = camera_ov_to_standard(camera_parameters)
        pinhole_ratio = standard_camera_parameters["pinhole_ratio"]
        aspect_ratio = standard_camera_parameters["screen_width"] / standard_camera_parameters["screen_height"]

        distance = RandUtil.random_reciprocal(distance_min, distance_max)
        x_rand = screen_space_range * RandUtil.rand_range(-1, 1)
        y_rand = screen_space_range * RandUtil.rand_range(-1, 1)
        x_ndc, y_ndc = x_rand * distance, y_rand * distance
        res_x, res_y = x_ndc / pinhole_ratio * aspect_ratio, y_ndc / pinhole_ratio
        self.value = [res_x, res_y, -distance]
