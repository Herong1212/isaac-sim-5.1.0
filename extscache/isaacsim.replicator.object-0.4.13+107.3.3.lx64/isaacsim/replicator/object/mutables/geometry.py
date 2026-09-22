import os
import shutil
import urllib.request

from PIL import Image
from pxr import Gf, UsdGeom, UsdShade

import cv2
from omni.metropolis.utils.math_util import MathUtil
import omni.kit

from .bottle import Bottle
from .mutable import Mutable_DEV

# from .solder_point import SolderPoint
from ..utility.metadata import enable_semantics
from ..utility.misc import error, ensured_retrieve, get_base_name, get_tmp_dir, tentative_retrieve
from ..utility.tex_attr_ops import tex_mut_attr_operation
from ..utility.scene import (
    create_and_bind_material_shader,
    create_custom_mesh,
    create_or_get_mesh_prim,
    create_xform_prim,
    find_first_of_type,
    get_prim_aabb_trimesh,
    set_shader_tiling,
    apply_material_binding_recursive,
)
from pxr import Sdf
import random, logging
from ..utility.scene import get_stage, get_prim


def turn_off_physics(prim):
    physics_on = prim.GetAttribute("physics:rigidBodyEnabled")
    if physics_on:
        physics_on.Set(False)
    for child in prim.GetChildren():
        turn_off_physics(child)


def process_image(gmesh, src_path, usd_path, operation):
    abs_path = os.path.join(os.path.dirname(usd_path), str(src_path).strip("@"))
    if not abs_path.startswith("http"):
        abs_path = os.path.abspath(abs_path)
    ext = os.path.splitext(abs_path)[1]
    input_path = f"{get_tmp_dir()}/randomized_input{ext}"
    output_path = f"{get_tmp_dir()}/randomized_output_{gmesh.output_index}{ext}"
    if abs_path.startswith("http"):
        urllib.request.urlretrieve(abs_path, input_path)
    else:
        if not os.path.exists(input_path) or not os.path.samefile(abs_path, input_path):
            shutil.copy(abs_path, input_path)  # TODO: from nucleus
    gmesh.shader_original_image = input_path
    gmesh.shader_input.Set(input_path)
    img_input = cv2.imread(input_path)
    if operation in tex_mut_attr_operation:
        img_output = tex_mut_attr_operation[operation](img_input)
        cv2.imwrite(output_path, img_output)
    else:
        # we already did a check previously, should not reach here
        error(f"unknown operation: {operation}")
    return output_path


def create_variant_mesh(scene_path, usd_paths):  # TODO point instances
    xform_prim = create_xform_prim(scene_path)
    variant_set = xform_prim.GetVariantSets().AddVariantSet("Meshes")
    for usd_path in usd_paths:
        name = get_base_name(usd_path)
        variant_set.AddVariant(name)
        variant_set.SetVariantSelection(name)
        with variant_set.GetVariantEditContext():
            xform_prim.GetReferences().AddReference(usd_path)
            xform_prim.SetInstanceable(False)
    return xform_prim, variant_set


def create_shader_node(name, source, function, shader_path):
    # add construct_color node
    new_node = UsdShade.Shader.Define(get_stage(), shader_path.AppendChild(name))
    # Set attributes
    api_schemas = Sdf.TokenListOp()
    api_schemas.explicitItems = ["NodeGraphNodeAPI"]
    new_node.GetPrim().SetMetadata("apiSchemas", api_schemas)  # Add NodeGraphNodeAPI
    new_node.CreateIdAttr("sourceAsset")  # Set implementation source
    new_node.GetPrim().CreateAttribute("info:implementationSource", Sdf.ValueTypeNames.Token).Set("sourceAsset")
    new_node.GetPrim().CreateAttribute("info:mdl:sourceAsset", Sdf.ValueTypeNames.Asset).Set(source)
    new_node.GetPrim().CreateAttribute("info:mdl:sourceAsset:subIdentifier", Sdf.ValueTypeNames.Token).Set(function)
    new_node.GetPrim().CreateAttribute("ui:nodegraph:node:expansionState", Sdf.ValueTypeNames.Token).Set("open")
    new_node.GetPrim().CreateAttribute("ui:nodegraph:node:pos", Sdf.ValueTypeNames.Float2).Set(
        Gf.Vec2f(random.uniform(-800.0, -600.0), random.uniform(100.0, 200.0))
    )
    return new_node


class Geometry_DEV(Mutable_DEV):  # noqa
    def switch_material(self, mtl_url):
        basename = mtl_url[mtl_url.rfind("/") + 1 : -4]
        scene_path = self.materials_parent + basename
        if basename not in self.materials:
            UsdShade.MaterialBindingAPI.Apply(self.prim)
            omni.kit.commands.execute("CreateMdlMaterialPrim", mtl_url=mtl_url, mtl_name=basename, mtl_path=scene_path)
            self.materials[basename] = scene_path
        omni.kit.commands.execute("BindMaterial", material_path=scene_path, prim_path=[self.prim.GetPath()])


class GBasic(Geometry_DEV):
    def __init__(self, name, metadata, scene):
        super().__init__(name)
        shape = metadata["subtype"]
        if not get_prim("/World"):
            create_xform_prim("/World")
        if not get_prim("/World/Shapes"):
            create_xform_prim("/World/Shapes")
        self.prim = create_or_get_mesh_prim(shape, f"/World/Shapes/{shape}_{name}")
        # TODO
        if "material_path" in metadata:
            self.materials_parent = f"/World/Shapes/{shape}_{name}_material_"
            self.materials = {}
        elif "texture_path" in metadata or "color" in metadata:
            self.shape_shader = create_and_bind_material_shader(
                f"/World/Shapes/{shape}_{name}_material", "OmniPBR", self.prim
            )
        self.initialize_prim(metadata, scene)

    def step(self, metadata):
        super().step(metadata)
        if "material_path" in metadata:
            material_path = metadata["material_path"]
            self.switch_material(material_path)
        elif "texture_path" in metadata:
            texture_path = metadata["texture_path"]
            self.shape_shader.GetInput("diffuse_texture").Set(texture_path)

            # de-stretch TODO abstract with above
            rp = 960 / 544  # TODO ...really need to access this somewhere
            image_width, image_height = Image.open(texture_path).size
            ri = image_width / image_height

            if ri > rp:
                set_shader_tiling(self.shape_shader, rp / ri, 1)
            else:
                set_shader_tiling(self.shape_shader, 1, ri / rp)
        elif "color" in metadata:
            color = metadata["color"]
            self.shape_shader.GetInput("diffuse_tint").Set(Gf.Vec3f(color))


# class GCustomMesh(Geometry_DEV):
#     def __init__(self, name, metadata, scene):
#         super().__init__(name)
#         points = ensured_retrieve("points", metadata, list)
#         self.prim = create_custom_mesh()
#         #if 'material_path' in metadata:
#     def step(self, metadata):
#         super().step(metadata)


class GMesh(Geometry_DEV):
    def __init__(self, name, metadata, scene):
        super().__init__(name)
        usd_candidates = ensured_retrieve("usd_path", metadata)
        if isinstance(usd_candidates, str):
            usd_candidates = [usd_candidates]
        elif not isinstance(usd_candidates, list):
            error(f"incorrect type for usd_path {type(usd_candidates)} at {name}")
        self.prim, self.mesh_variant_set = create_variant_mesh(f"/World/Meshes/mesh_{name}", usd_candidates)
        apply_material_binding_recursive(self.prim)

        # DEV
        animation_path = tentative_retrieve("animation", metadata, str, None)
        if animation_path is not None:
            self.animation = create_xform_prim("/World/TestAnim")
            self.animation.GetReferences().AddReference(animation_path)
            prim_anim_biped = find_first_of_type(self.animation, "SkelRoot")
            prim_anim_biped.GetAttribute("visibility").Set("invisible")

        # TODO standardize texture substitution
        """if 'texture_path' in self.config_item_template:
            mesh = get_prim(f'{self.prim.GetPath().pathString}/KV001_Tide_PUO_32ct')
            mesh_2 = get_prim(f'{self.prim.GetPath().pathString}')
            self.shape_shader = create_and_bind_material_shader(
                f"/World/Shapes/{shape}_{name}_material", "OmniPBR", mesh
            )
            #print(self.config_item_template['texture_path'])"""

        self.initialize_prim(metadata, scene)
        self.has_updated_usd = False

        # restore shader after image processing
        self.shader_input = None
        self.shader_original_image = None
        self.output_index = 1

    def step(self, metadata):
        super().step(metadata)

        # restore shader after image processing, before changing variant set
        self.output_index = (self.output_index + 1) % 2
        if self.shader_input is not None:
            self.shader_input.Set(self.shader_original_image)

        if not self.has_updated_usd:
            self.update_usd(metadata["usd_path"])

        # DEV
        animation_path = tentative_retrieve("animation", metadata, str, None)
        if animation_path is not None:
            omni.kit.commands.execute(
                "ApplyAnimationGraphAPICommand",
                paths=[find_first_of_type(self.prim, "SkelRoot").GetPath()],
                animation_graph_path=find_first_of_type(self.animation, "AnimationGraph").GetPath(),
            )

        shader_attributes = tentative_retrieve("shader_attributes", metadata, dict)
        if shader_attributes is not None:
            self.mesh_shader = UsdShade.Shader(find_first_of_type(self.prim, "Shader"))
            for name, value in shader_attributes.items():
                self.shader_input = self.mesh_shader.GetInput(name)
                if not self.shader_input:
                    error(f"shader attribute {name} does not exist")
                self.shader_original_image = self.shader_input.Get()
                if isinstance(value, list):
                    value = tuple(value)
                if isinstance(value, str):
                    value = value.strip()
                    if value.startswith("<") and value.endswith(">"):
                        operator = value.strip("<>")
                        if operator == "perlin_noise":
                            message = f"[METROPERF]: constructing noise mdl graph"
                            logging.info(message)
                            print(message)
                            shader_path = self.mesh_shader.GetPath().GetParentPath()

                            # add construct_color nodes
                            construct_color_1 = create_shader_node(
                                "construct_color_1",
                                "nvidia/aux_definitions.mdl",
                                "construct_color(::base::texture_return)",
                                shader_path,
                            )
                            construct_color_1_input = construct_color_1.CreateInput("a", Sdf.ValueTypeNames.Token)
                            construct_color_1_input.SetRenderType("::base::texture_return")
                            construct_color_1_output = construct_color_1.CreateOutput("out", Sdf.ValueTypeNames.Color3f)
                            construct_color_1_output.SetRenderType("color")

                            construct_color_2 = create_shader_node(
                                "construct_color_2",
                                "nvidia/aux_definitions.mdl",
                                "construct_color(::base::texture_return)",
                                shader_path,
                            )
                            construct_color_2_input = construct_color_2.CreateInput("a", Sdf.ValueTypeNames.Token)
                            construct_color_2_input.SetRenderType("::base::texture_return")
                            construct_color_2_output = construct_color_2.CreateOutput("out", Sdf.ValueTypeNames.Color3f)
                            construct_color_2_output.SetRenderType("color")

                            construct_color_3 = create_shader_node(
                                "construct_color_3",
                                "nvidia/aux_definitions.mdl",
                                "construct_color(::base::texture_return)",
                                shader_path,
                            )
                            construct_color_3_input = construct_color_3.CreateInput("a", Sdf.ValueTypeNames.Token)
                            construct_color_3_input.SetRenderType("::base::texture_return")
                            construct_color_3_output = construct_color_3.CreateOutput("out", Sdf.ValueTypeNames.Color3f)
                            construct_color_3_output.SetRenderType("color")

                            # add perlin_noise_texture node
                            noise_shader = create_shader_node(
                                "perlin_noise_texture",
                                "nvidia/core_definitions.mdl",
                                "perlin_noise_texture",
                                shader_path,
                            )
                            noise_output = noise_shader.CreateOutput("out", Sdf.ValueTypeNames.Token)

                            # add file_texture node
                            base_texture_shader = create_shader_node(
                                "file_texture", "nvidia/core_definitions.mdl", "file_texture", shader_path
                            )
                            base_texture_input = base_texture_shader.CreateInput("texture", Sdf.ValueTypeNames.Asset)
                            texture_path = os.path.join(
                                os.path.dirname(metadata["usd_path"]), str(self.shader_original_image).strip("@")
                            )
                            base_texture_input.Set(texture_path)
                            base_texture_output = base_texture_shader.CreateOutput("out", Sdf.ValueTypeNames.Token)
                            base_texture_output.SetRenderType("::base::texture_return")

                            # add blend_colors node
                            blend_colors_shader = create_shader_node(
                                "blend_colors", "nvidia/core_definitions.mdl", "blend_colors", shader_path
                            )
                            blend_colors_output = blend_colors_shader.CreateOutput("out", Sdf.ValueTypeNames.Token)
                            blend_colors_output.SetRenderType("::base::texture_return")
                            blend_colors_input_weight = blend_colors_shader.CreateInput(
                                "weight", Sdf.ValueTypeNames.Float
                            )
                            blend_colors_input_weight.Set(0.8)
                            blend_colors_input_color_1 = blend_colors_shader.CreateInput(
                                "color_1", Sdf.ValueTypeNames.Color3f
                            )
                            blend_colors_input_color_2 = blend_colors_shader.CreateInput(
                                "color_2", Sdf.ValueTypeNames.Color3f
                            )
                            blend_colors_input_mode = blend_colors_shader.CreateInput("mode", Sdf.ValueTypeNames.Token)
                            blend_colors_input_mode.SetRenderType("::base::color_layer_mode")
                            blend_colors_input_mode.Set("color_layer_multiply")

                            # Connections
                            blend_colors_input_color_1.ConnectToSource(construct_color_1_output)
                            blend_colors_input_color_2.ConnectToSource(construct_color_2_output)
                            construct_color_1_input.ConnectToSource(base_texture_output)
                            construct_color_2_input.ConnectToSource(noise_output)
                            construct_color_3_input.ConnectToSource(blend_colors_output)
                            # clear diffuse texture because it can override the "diffuse_color_constant"
                            value = ""
                            self.mesh_shader.GetInput("diffuse_color_constant").ConnectToSource(
                                construct_color_3_output
                            )
                        else:
                            value = process_image(
                                self, self.shader_input.Get(), metadata["usd_path"], value.strip("<>")
                            )
                self.shader_input.Set(value)

        base_name = get_base_name(metadata["usd_path"])
        if tentative_retrieve("tracked", metadata, bool, False):
            enable_semantics(self.prim, f"{self.name}~~~{base_name}")
        elif tentative_retrieve("attach_label", metadata, bool, False):
            enable_semantics(self.prim, f"{self.name}~~~{base_name}", semantic_class="attach_label")
        self.has_updated_usd = False

    def update_usd(self, usd_path, get_prim_aabb=False):
        self.has_updated_usd = True
        base_name = get_base_name(usd_path)
        # after SetVariantSelection, [translate, rotateXYZ, scale] values will be spawned
        # but not added to the xformOp list if they did not exist
        self.mesh_variant_set.SetVariantSelection(base_name)
        if get_prim_aabb:
            return get_prim_aabb_trimesh(self.prim)


class GBottle(Geometry_DEV):
    def __init__(self, name, metadata, scene):
        super().__init__(name)

        scene_path = f"/World/Bottles/bottle_{name}"
        self.prim = create_xform_prim(scene_path)
        self.bottle = Bottle()
        self.control_points = [
            (0, -70, 0),
            (0, -70, 0),
            (0, -70, 18),
            (0, -60, 20),
            (0, -30, 20),
            (0, 20, 10),
            (0, 45, 8),
            (0, 75, 6),
            (0, 90, 6),
            (0, 90, 0),
            (0, 90, 0),
        ]
        self.bottle_body = create_custom_mesh(
            f"{scene_path}/Body",
            face_vertex_indices=[0, 1, 2],
            face_vertex_counts=[3],
            points=[Gf.Vec3f(0, 0, 0), Gf.Vec3f(0, 1, 0), Gf.Vec3f(0, 0, 1)],
        )
        self.bottle_label = create_custom_mesh(
            f"{scene_path}/Label",
            face_vertex_indices=[0, 1, 2],
            face_vertex_counts=[3],
            points=[Gf.Vec3f(0, 0, 0), Gf.Vec3f(0, 1, 0), Gf.Vec3f(0, 0, 1)],
            sts=[],
        )
        self.bottle_body_shader = create_and_bind_material_shader(
            f"{scene_path}/BodyMaterial", "OmniGlass", self.bottle_body
        )
        self.bottle_label_shader = create_and_bind_material_shader(
            f"{scene_path}/LabelMaterial", "OmniPBR", self.bottle_label
        )

        self.initialize_prim(metadata, scene)

    def step(self, metadata):
        super().step(metadata)

        def get_effector(name):
            return ensured_retrieve(name, metadata, (int, float))

        self.control_points[5] = (
            0,
            MathUtil.lerp(0, 35, get_effector("vertical_effector")),
            MathUtil.lerp(8, 20, get_effector("horizontal_effector")),
        )
        self.control_points[4] = (
            0,
            MathUtil.lerp(-30, self.control_points[5][1] - 20, get_effector("base_effector")),
            20,
        )
        self.control_points[6] = (
            0,
            MathUtil.lerp(self.control_points[5][1] + 10, 65, get_effector("neck_effector")),
            8,
        )

        self.bottle.update(self.control_points, 5)  # TODO
        # body
        self.bottle_body.GetPointsAttr().Set((self.bottle.body_mesh_points))
        self.bottle_body.GetFaceVertexIndicesAttr().Set(self.bottle.body_face_vertex_indices)
        self.bottle_body.GetFaceVertexCountsAttr().Set(self.bottle.body_face_vertex_counts)
        # label
        self.bottle_label.GetPointsAttr().Set((self.bottle.label_mesh_points))
        self.bottle_label.GetFaceVertexIndicesAttr().Set(self.bottle.get_label_face_vertex_indices())
        self.bottle_label.GetFaceVertexCountsAttr().Set(self.bottle.get_label_face_vertex_counts())
        UsdGeom.PrimvarsAPI(self.bottle_label).GetPrimvar("st").Set(self.bottle.get_label_sts())
        # label texture
        if "texture_path" in metadata:
            texture_path = metadata["texture_path"]
            self.bottle_label_shader.GetInput("diffuse_texture").Set(texture_path)

            # de-stretch
            rp = self.bottle.label_size_ratio
            image_width, image_height = Image.open(texture_path).size
            ri = image_width / image_height

            if ri > rp:
                set_shader_tiling(self.bottle_label_shader, rp / ri, 1)
            else:
                set_shader_tiling(self.bottle_label_shader, 1, ri / rp)
        if "color" in metadata:
            color = metadata["color"]
            self.bottle_body_shader.GetInput("glass_color").Set(Gf.Vec3f(color))
