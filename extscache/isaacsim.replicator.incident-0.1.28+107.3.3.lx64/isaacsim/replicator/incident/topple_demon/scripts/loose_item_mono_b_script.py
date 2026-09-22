import carb
import carb.dictionary
import carb.events
import omni

from pxr import Usd, UsdGeom, UsdPhysics, PhysxSchema, Gf, Sdf

from omni.metropolis.utils.mono_b_script_util import MonoBScript
from omni.metropolis.utils.semantics_util import SemanticsUtils

from isaacsim.replicator.incident.topple_demon.event_definitions import TOPPLE_EVENT


class LooseItemMonoBScript(MonoBScript):

    def __init__(self, prim_path: str):
        super().__init__(prim_path)

    def on_init(self):
        carb.log_info(f"{type(self).__name__}.on_init()->{self.prim_path}")
        bus = omni.kit.app.get_app().get_message_bus_event_stream()
        if not bus:
            carb.log_error("Could not get the message bus!")

        self._topple_event_sub = bus.create_subscription_to_pop_by_type(TOPPLE_EVENT, lambda e: self.on_topple_event(e))

        if not self._topple_event_sub:
            carb.log_error("Could not create subscription!")

        self._num_frames_applied = 0
        self._apply_force = False

        self._stage = omni.usd.get_context().get_stage()

        self._init_box_collision()
        self._init_rigid_body()
        self._init_force_api()

    def get_stage(self):
        return self._stage

    def _init_rigid_body(self):
        prim = self.get_stage().GetPrimAtPath(self.prim_path)
        # rigid_body_token = Tf.Token('rigidBody')
        # if rigid_body_token in prim.GetAppliedSchemas():
        #     return
        if "rigidBody" in prim.GetAppliedSchemas():
            return

        rigid_body_api = UsdPhysics.RigidBodyAPI.Apply(prim)
        enabled_attr = rigid_body_api.GetRigidBodyEnabledAttr()
        enabled_attr.Set(True)
        carb.log_info(f"Rigid body enabled: {self.prim_path}")

    def has_collision_api_children(self, prim_path: Sdf.Path):
        prim = self.get_stage().GetPrimAtPath(prim_path)
        if prim.HasAPI(UsdPhysics.CollisionAPI):
            return True

        for child in prim.GetChildren():
            if self.has_collision_api_children(child.GetPath()):
                return True
        return False

    def make_colliders_dynamic_nested(self, prim_path: Sdf.Path):
        prim = self.get_stage().GetPrimAtPath(prim_path)
        if prim.HasAPI(UsdPhysics.MeshCollisionAPI):
            mesh_collision_api = UsdPhysics.MeshCollisionAPI.Get(prim.GetStage(), prim_path)
            approximation_attr = mesh_collision_api.CreateApproximationAttr().Get()
            is_allowed_dynamic = True
            if approximation_attr == "none" or approximation_attr == "meshSimplification":
                is_allowed_dynamic = False

            if not is_allowed_dynamic:
                carb.log_info(f"[ColliderInitialization]: MeshCollisionAPI approximation type \
                                 {mesh_collision_api.CreateApproximationAttr().Get()} on prim {str(prim_path)} \
                                 not allowed to be dynamic, setting to convexDecomposition")
                mesh_collision_api.CreateApproximationAttr().Set("convexDecomposition")

        for child in prim.GetChildren():
            self.make_colliders_dynamic_nested(child.GetPath())

    def _init_box_collision(self):
        prim = self.get_stage().GetPrimAtPath(self.prim_path)

        # Search for descendants with UsdPhysicsCollisionAPI already applied
        has_collision_api = self.has_collision_api_children(Sdf.Path(self.prim_path))
        if not has_collision_api:
            UsdPhysics.CollisionAPI.Apply(prim)

        self.make_colliders_dynamic_nested(Sdf.Path(self.prim_path))

    def _init_force_api(self):
        prim = self.get_stage().GetPrimAtPath(self.prim_path)
        force_api = PhysxSchema.PhysxForceAPI.Apply(prim)
        force_api.CreateWorldFrameEnabledAttr().Set(True)

        enabled_attr = force_api.CreateForceEnabledAttr()
        enabled_attr.Set(True)

        force_attr = force_api.GetForceAttr()
        force_attr.Set(Gf.Vec3f(0.0, 0.0, 0.0))

    def on_destroy(self):
        carb.log_info(f"{type(self).__name__}.on_destroy()->{self.prim_path}")
        self._topple_event_sub = None

    def on_play(self):

        carb.log_info(f"{type(self).__name__}.on_play()->{self.prim_path}")

    def on_pause(self):
        carb.log_info(f"{type(self).__name__}.on_pause()->{self.prim_path}")

    def on_stop(self):
        carb.log_info(f"{type(self).__name__}.on_stop()->{self.prim_path}")

    def on_update(self):
        # carb.log_info(f"{type(self).__name__}.on_update({current_time}, {delta_time})->{self.prim_path}")
        if self._apply_force:
            if self._num_frames_applied >= 1:
                stage = self.get_stage()
                force_api = PhysxSchema.PhysxForceAPI.Get(stage, self.prim_path)
                enabled_attr = force_api.GetForceEnabledAttr()
                enabled_attr.Set(False)
                carb.log_info("Force disabled")

                self._num_frames_applied = 0
                self._apply_force = False
            else:
                self._num_frames_applied += 1
                carb.log_info("Force continued")

    def add_semantics(self):
        pass
        # prim = self.get_stage().GetPrimAtPath(self.prim_path)
        # SemanticsUtils.add_update_semantics_timecode(prim, "topple_item", "class")

    def on_topple_event(self, target: Gf.Vec3f):

        stage = self.get_stage()

        self.add_semantics()

        box_center = Gf.Vec3f(
            UsdGeom.Xformable(self.prim).ComputeLocalToWorldTransform(Usd.TimeCode.Default()).ExtractTranslation()
        )

        # Get the up axis
        up_axis = UsdGeom.Tokens.y  # Default is Y-up
        up_vector = Gf.Vec3f(0, 1, 0)

        # Check if the stage has a different up axis set
        if stage.HasMetadata(UsdGeom.Tokens.upAxis):
            up_axis = stage.GetMetadata(UsdGeom.Tokens.upAxis)

        # Get the up vector based on the up axis
        if up_axis == UsdGeom.Tokens.y:
            up_vector = Gf.Vec3f(0, 1, 0)
        elif up_axis == UsdGeom.Tokens.z:
            up_vector = Gf.Vec3f(0, 0, 1)
        else:  # Assuming X-up
            up_vector = Gf.Vec3f(1, 0, 0)

        force_vec = target - box_center
        force_dir = (Gf.GetComplement(force_vec, up_vector)).GetNormalized()

        stage = self.get_stage()
        force_api = PhysxSchema.PhysxForceAPI.Get(stage, self.prim_path)

        force_attr = force_api.GetForceAttr()

        # print("Force direction: " + str(force_dir))

        force_attr.Set(200 * force_dir)

        enabled_attr = force_api.GetForceEnabledAttr()
        enabled_attr.Set(True)

        self._apply_force = True
