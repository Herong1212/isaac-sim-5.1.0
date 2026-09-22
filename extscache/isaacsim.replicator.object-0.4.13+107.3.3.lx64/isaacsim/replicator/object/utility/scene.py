import omni, carb, time
import trimesh
from .misc import error
from pxr import UsdGeom, UsdPhysics, PhysxSchema, Gf, Sdf, UsdShade
from omni.physx.scripts.physicsUtils import add_physics_material_to_prim


def apply_settings(settings):
    for key, value in settings.items():
        carb.settings.get_settings().set(key, value)


## scene


async def wait_frames(cnt=1):
    for i in range(cnt):
        await omni.kit.app.get_app_interface().next_update_async()


async def wait_seconds(cnt=1):
    cnt_f = 0
    if cnt == 0:
        return
    start = time.time()
    while time.time() - start < cnt:
        await wait_frames()
        cnt_f += 1
        print("waited ", cnt_f)


async def new_stage_async():
    await omni.usd.get_context().new_stage_async()


def get_next_free_path(path):
    return omni.usd.get_stage_next_free_path(get_stage(), path, True)


def get_stage():
    return omni.usd.get_context().get_stage()


def get_prim(scene_path):
    return get_stage().GetPrimAtPath(scene_path)


def create_xform_prim(scene_path):
    return UsdGeom.Xform.Define(get_stage(), scene_path).GetPrim()


def create_or_get_prim_attribute(prim, name, sdf_type):
    attr = prim.GetAttribute(name)
    if attr.Get() is None:
        attr = prim.CreateAttribute(name, sdf_type)
        attr.Set(sdf_type.defaultValue)
    return attr


def get_attribute_sdf_type(attr):
    return Sdf.ValueTypeNames.Find(str(attr.GetTypeName()))


def create_or_get(scene_path, operation):
    prim = get_prim(scene_path)
    if not prim or prim is None:
        operation()
        prim = get_prim(scene_path)
    return prim


def create_or_get_dome_light(scene_path="/World/DomeLight", intensity=1000):
    return create_or_get(
        scene_path,
        lambda: omni.kit.commands.execute(
            "CreatePrim",
            prim_path=scene_path,
            prim_type="DomeLight",
            attributes={"inputs:intensity": intensity, "inputs:texture:format": "latlong"},
        ),
    )


def create_or_get_distant_light(scene_path="/World/DistantLight", intensity=3000):
    return create_or_get(
        scene_path,
        lambda: omni.kit.commands.execute(
            "CreatePrim",
            prim_path=scene_path,
            prim_type="DistantLight",
            attributes={"inputs:angle": 1.0, "inputs:intensity": intensity},
        ),
    )


def create_or_get_sphere_light(scene_path="/World/SphereLight", intensity=30000, radius=50):
    return create_or_get(
        scene_path,
        lambda: omni.kit.commands.execute(
            "CreatePrim",
            prim_path=scene_path,
            prim_type="SphereLight",
            attributes={"inputs:radius": radius, "inputs:intensity": intensity},
        ),
    )


## basic shapes


def create_custom_mesh(scene_path, face_vertex_indices=None, face_vertex_counts=None, points=None, sts=None):
    mesh = UsdGeom.Mesh.Define(get_stage(), scene_path)
    mesh.CreateSubdivisionSchemeAttr("none")
    if face_vertex_indices is not None:
        mesh.GetFaceVertexIndicesAttr().Set(face_vertex_indices)
    if face_vertex_counts is not None:
        mesh.GetFaceVertexCountsAttr().Set(face_vertex_counts)
    if points is not None:
        mesh.GetPointsAttr().Set(points)
    if sts is not None:
        sts_primvar = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray)
        sts_primvar.SetInterpolation("faceVarying")
        sts_primvar.Set(sts)
    return mesh


def create_or_get_mesh_prim(type, scene_path):
    if not type in ["cone", "cube", "cylinder", "disk", "torus", "plane", "sphere", "torus"]:
        error(f"unkown geometry type: {type}")

    def create_mesh_prim(type, scene_path):
        _, path = omni.kit.commands.execute(
            "CreateMeshPrimWithDefaultXform", prim_type=type.capitalize(), prim_path=scene_path
        )
        if path != scene_path:
            omni.kit.commands.execute(
                "MovePrims", paths_to_move={path: scene_path}, keep_world_transform=True, destructive=False
            )

    return create_or_get(scene_path, lambda: create_mesh_prim(type, scene_path))


def ensure_shader(material_path, material_name):
    shader = UsdShade.Shader(get_stage().GetPrimAtPath(f"{material_path}/Shader"))

    def ensure_attribute(name, type):
        if not shader.GetInput(name):
            shader.CreateInput(name, type)

    attrs = {
        "diffuse_texture": Sdf.ValueTypeNames.Asset,
        "diffuse_tint": Sdf.ValueTypeNames.Float3,
    }
    if material_name == "OmniGlass":
        attrs["glass_color"] = Sdf.ValueTypeNames.Float3
        attrs["glass_ior"] = Sdf.ValueTypeNames.Float
    else:
        attrs["reflection_roughness_constant"] = Sdf.ValueTypeNames.Float
    for _name, _type in attrs.items():
        ensure_attribute(_name, _type)
    if not material_name == "OmniGlass":
        shader.GetInput("reflection_roughness_constant").Set(1)
    return shader


def apply_material_binding_recursive(prim):
    if prim is None or not hasattr(prim, 'GetTypeName'):
        return
    if prim.GetPrim().GetTypeName() == "Mesh":
        UsdShade.MaterialBindingAPI.Apply(prim)
    for child in prim.GetChildren():
        apply_material_binding_recursive(child)


def create_and_bind_material_shader(scene_path, _mtl_name, prim):
    apply_material_binding_recursive(prim)
    omni.kit.commands.execute(
        "CreateMdlMaterialPrim", mtl_url=f"{_mtl_name}.mdl", mtl_name=_mtl_name, mtl_path=scene_path
    )
    omni.kit.commands.execute("BindMaterial", material_path=scene_path, prim_path=[prim.GetPath()])
    return ensure_shader(scene_path, _mtl_name)


def set_shader_tiling(shader, scale_x, scale_y):
    if not shader.GetInput("texture_scale"):
        shader.CreateInput("texture_scale", Sdf.ValueTypeNames.Float2)
    shader.GetInput("texture_scale").Set(Gf.Vec2f(scale_x, scale_y))


def find_first_of_type(prim, type):
    if prim is None or not hasattr(prim, 'GetTypeName'):
        return None
    if prim.GetTypeName() == type:
        return prim
    for child in prim.GetChildren():
        material = find_first_of_type(child, type)
        if material is not None:
            return material
    return None


def get_first_selected():
    return get_stage().GetPrimAtPath(omni.usd.get_context().get_selection().get_selected_prim_paths()[0])


## physics


def apply_collision_recursive(prim, approximation):
    if prim is None or not hasattr(prim, 'GetTypeName'):
        return
    if prim.GetTypeName() == "Mesh":
        UsdPhysics.CollisionAPI.Apply(prim)  # needs to apply on each single mesh for local bounding box query
        mesh_collision_api = UsdPhysics.MeshCollisionAPI.Apply(prim)
        mesh_collision_api.GetApproximationAttr().Set(approximation)
        # LOG(prim, prim.GetAttribute('physics:collisionEnabled').Get())
    for child in prim.GetChildren():
        apply_collision_recursive(child, approximation)


def set_physics_properties(
    prim, is_rigidbody=True, friction=0.15, linear_damping=0, angular_damping=0, is_concave=False
):
    UsdPhysics.CollisionAPI.Apply(prim)

    if is_rigidbody:
        if is_concave:
            approximation = "convexDecomposition"
        else:
            approximation = "convexHull"
    else:
        approximation = "meshSimplification"

    apply_collision_recursive(prim, approximation)
    mesh_collision_api = UsdPhysics.MeshCollisionAPI.Apply(prim)
    mesh_collision_api.GetApproximationAttr().Set(approximation)

    if is_rigidbody:
        # basic physics properties
        physicsAPI = UsdPhysics.RigidBodyAPI.Apply(prim)
        # physicsAPI.CreateVelocityAttr().Set(Gf.Vec3f(0.0))
        # physicsAPI.CreateAngularVelocityAttr().Set(Gf.Vec3f(0.0))
        massApi = UsdPhysics.MassAPI.Apply(prim)
        # massApi.GetMassAttr().Set(10000)

        # physx properties
        physicsBodyAPI = PhysxSchema.PhysxRigidBodyAPI.Apply(prim)
        physicsBodyAPI.CreateLinearDampingAttr(linear_damping)
        physicsBodyAPI.CreateAngularDampingAttr(angular_damping)  # TODO sep

        PhysxSchema.PhysxCollisionAPI.Apply(prim)

    # material
    material_prim = UsdShade.Material.Define(get_stage(), f"{prim.GetPath().pathString}_physicsMaterial").GetPrim()
    material = UsdPhysics.MaterialAPI.Apply(material_prim)
    material.CreateStaticFrictionAttr().Set(friction)
    material.CreateDynamicFrictionAttr().Set(friction)

    add_physics_material_to_prim(get_stage(), prim, material_prim.GetPath())


def reset_velocity(prim):
    physicsAPI = UsdPhysics.RigidBodyAPI.Apply(prim)
    physicsAPI.CreateVelocityAttr().Set(Gf.Vec3f(0.0))
    physicsAPI.CreateAngularVelocityAttr().Set(Gf.Vec3f(0.0))


def get_points_trimesh_inner(prim, points):
    if prim is None or not hasattr(prim, 'GetTypeName'):
        return
    if prim.GetTypeName() == "Mesh":
        points.extend(prim.GetAttribute("points").Get())
    for child in prim.GetChildren():
        get_points_trimesh_inner(child, points)


def get_points_trimesh(prim):
    points = []
    get_points_trimesh_inner(prim, points)
    return points


def get_bounds_trimesh(points):
    bounds = trimesh.PointCloud(points).bounds
    return Gf.BBox3d(
        Gf.Range3d(
            Gf.Vec3d(bounds[0][0], bounds[0][1], bounds[0][2]), Gf.Vec3d(bounds[1][0], bounds[1][1], bounds[1][2])
        )
    )


def get_prim_aabb_trimesh_inner(prim, aabb_local):
    if prim is None or not hasattr(prim, 'GetTypeName'):
        return
    if prim.GetTypeName() == "Mesh":
        points = prim.GetAttribute("points").Get()
        scale = prim.GetAttribute("xformOp:scale").Get()
        if scale:
            for i, p in enumerate(points):
                points[i] = Gf.Vec3f(p[0] * scale[0], p[1] * scale[1], p[2] * scale[2])
        bbox3d = get_bounds_trimesh(points)
        aabb_local[0] = Gf.BBox3d.Combine(aabb_local[0], bbox3d)
    for child in prim.GetChildren():
        get_prim_aabb_trimesh_inner(child, aabb_local)


def get_prim_aabb_trimesh(prim):
    aabb_local = [Gf.BBox3d()]
    get_prim_aabb_trimesh_inner(prim, aabb_local)
    return (aabb_local[0].GetBox().GetMin(), aabb_local[0].GetBox().GetMax())


def scale_aabb(aabb, scale):
    a, b = aabb
    return (
        Gf.Vec3d(a[0] * scale[0], a[1] * scale[1], a[2] * scale[2]),
        Gf.Vec3d(b[0] * scale[0], b[1] * scale[1], b[2] * scale[2]),
    )


## timeline


def timeline_play():
    omni.timeline.get_timeline_interface().play()


def timeline_pause():
    omni.timeline.get_timeline_interface().pause()


def timeline_stop():
    omni.timeline.get_timeline_interface().stop()


def observe_event(event_name, action, observer_name="isaacsim.replicator.object"):
    return carb.eventdispatcher.get_eventdispatcher().observe_event(
        observer_name=observer_name,
        event_name=event_name,
        on_event=action
    )

def iro_environment_setup(ext):
    if not ext.is_environment_setup:
        ext.is_environment_setup = True

        settings = {
            "/persistent/app/stage/upAxis": "Y",
            "/persistent/simulation/defaultMetersPerUnit": 0.01,
            "/persistent/app/primCreation/DefaultXformOpType": "Scale, Rotate, Translate",
        }
        apply_settings(settings)
        omni.usd.get_context().new_stage()