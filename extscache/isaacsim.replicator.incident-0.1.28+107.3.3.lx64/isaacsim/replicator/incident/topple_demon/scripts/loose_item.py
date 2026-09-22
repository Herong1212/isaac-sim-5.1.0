import carb
import carb.dictionary
import carb.events
import omni
from omni.kit.scripting import BehaviorScript

from pxr import Usd, UsdGeom, UsdPhysics, PhysxSchema, Gf

from isaacsim.replicator.incident.topple_demon.event_definitions import TOPPLE_EVENT, TARGET_KEY


class LooseItem(BehaviorScript):
    # def __init__(self):
    #     super().__init__()
    #     self._topple_event_sub = None

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

        self._init_rigid_body()
        self._init_box_collision()
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

    def _init_box_collision(self):
        prim = self.get_stage().GetPrimAtPath(self.prim_path)
        # collision_enabled_token = Tf.Token('collisionEnabled')
        # if collision_enabled_token in prim.GetAppliedSchemas():
        #     return
        if "collisionEnabled" in prim.GetAppliedSchemas():
            return
        UsdPhysics.CollisionAPI.Apply(prim)

    def _init_force_api(self):
        prim = self.get_stage().GetPrimAtPath(self.prim_path)
        force_api = PhysxSchema.PhysxForceAPI.Apply(prim)
        force_api.CreateWorldFrameEnabledAttr().Set(True)

        enabled_attr = force_api.CreateForceEnabledAttr()
        enabled_attr.Set(True, 0.0)

        force_attr = force_api.GetForceAttr()
        force_attr.Set(Gf.Vec3f(0.0, 0.0, 0.0), 0.0)

    def on_destroy(self):
        carb.log_info(f"{type(self).__name__}.on_destroy()->{self.prim_path}")
        self._topple_event_sub = None

    def on_play(self):

        carb.log_info(f"{type(self).__name__}.on_play()->{self.prim_path}")

    def on_pause(self):
        carb.log_info(f"{type(self).__name__}.on_pause()->{self.prim_path}")

    def on_stop(self):
        carb.log_info(f"{type(self).__name__}.on_stop()->{self.prim_path}")

    def on_update(self, current_time: float, delta_time: float):
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

    def on_topple_event(self, event: carb.events.IEvent):
        payload = event.payload
        # TODO : figure out how to use '/' in a carb.dictionary!
        prim_path_key = str(self.prim_path).replace("/", "____")

        # print(f"From {self.prim_path} the payload: {payload} {prim_path_key in payload}")
        if prim_path_key not in payload:
            return

        prim_payload = payload[prim_path_key]
        if TARGET_KEY not in prim_payload:
            carb.log_error(f"LooseItem: Incorrect payload sent to: {self.prim_path}")
            return

        carb.log_info(f"Topple event received by :{self.prim_path}")

        vec = prim_payload[TARGET_KEY]
        target = Gf.Vec3f(vec[0], vec[1], vec[2])

        stage = self.get_stage()

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

        force_attr.Set(80 * force_dir)

        enabled_attr = force_api.GetForceEnabledAttr()
        enabled_attr.Set(True)

        self._apply_force = True
