import omni.kit.commands
from pxr import Usd, UsdGeom, Gf, Sdf
import carb
from enum import Enum

from omni.metropolis.utils.usd_util import USDUtil

from ..event_defines import IncidentData, IncidentCarbEventHelper
from omni.metropolis.utils.semantics_util import SemanticsUtils


class PyroEvent:
    flow_box_count = 0
    def __init__(self, name: str, selected_flammable_item_prim_path: str, pyro_nearby_radius: float = 0.0):
        self.name = name
        self.selected_flammable_item_prim_path = selected_flammable_item_prim_path
        self.pyro_nearby_radius = pyro_nearby_radius
        self.flame_emitter = None
        self.fuel_source = None

        result, prim = omni.kit.commands.execute(
            "FlowCreatePrim",
            prim_path=Sdf.Path(selected_flammable_item_prim_path).GetParentPath().AppendPath(f"flowEmitterBox_{PyroEvent.flow_box_count}"),
            type_name="FlowEmitterBox",
        )
        PyroEvent.flow_box_count += 1

        if not result:
            carb.log_error("Failed to create FlowEmitterBox")
            return


        ctx = omni.usd.get_context()
        stage = ctx.get_stage()
        purposes = [UsdGeom.Tokens.default_]
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
        self.flammable_item_prim = stage.GetPrimAtPath(selected_flammable_item_prim_path)
        # TODO: replace with USDGeomBoundableAPI
        bound = bbox_cache.ComputeWorldBound(self.flammable_item_prim)
        box_range = bound.ComputeAlignedBox()
        bbox_max = box_range.GetMax()
        bbox_min = box_range.GetMin()
        half_size = (bbox_max - bbox_min) / 2
        half_size_attr = prim.GetAttribute("halfSize")

        xform_cache = UsdGeom.XformCache(Usd.TimeCode.Default())
        prim_local_to_world = xform_cache.GetLocalToWorldTransform(prim)

        center_world = (bbox_max + bbox_min) / 2
        if half_size_attr:
            # print("half size: ", half_size_attr.Get())
            half_size_attr.Set(Gf.Vec3f(half_size[0], half_size[1], half_size[2]))

        if prim.GetAttribute("position"):
            # TODO: again with USDGeomBoundableAPI
            center_local = prim_local_to_world.GetInverse().Transform(center_world)
            prim.GetAttribute("position").Set(Gf.Vec3f(center_local[0], center_local[1], center_local[2]))

        if prim.GetAttribute("velocity"):
            # TODO: again with USDGeomBoundableAPI
            prim.GetAttribute("velocity").Set(Gf.Vec3f(0, 0, 0))

        if prim.GetAttribute("coupleRateFuel"):
            prim.GetAttribute("coupleRateFuel").Set(2.0)

        if prim.GetAttribute("coupleRateSmoke"):
            prim.GetAttribute("coupleRateSmoke").Set(2.0)

        if prim.GetAttribute("fuel"):
            prim.GetAttribute("fuel").Set(0.0)

        if prim.GetAttribute("smoke"):
            prim.GetAttribute("smoke").Set(0.0)

        prim.GetAttribute("layer").Set(3)

        self.flame_emitter = prim

    def trigger_pyro_event(self):
        self.fuel_source = FuelSource(self.flame_emitter)

        # Carb event
        stage = omni.usd.get_context().get_stage()
        pos = USDUtil.get_prim_pos(prim=self.flammable_item_prim, stage=stage, prim_path=None)
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=IncidentCarbEventHelper.carb_event_name(self.name),
            payload={
                "Payload": {
                    "event_data": IncidentData(event_name=self.name, event_type="Fire Event", event_position=pos)
                }
            },
        )
        carb.log_info(f"Trigger pyro event '{self.name}' at {pos}.")

        SemanticsUtils.add_update_prim_metrosim_semantics([self.flammable_item_prim], "class", "incident_flaming_item")

    def destroy(self):
        carb.log_info("Destroying PyroEvent")
        ctx = omni.usd.get_context()
        stage = ctx.get_stage()
        stage.RemovePrim(self.flame_emitter.GetPath())
        if self.flammable_item_prim and self.flammable_item_prim.IsValid():
            SemanticsUtils.remove_prim_metrosim_semantics([self.flammable_item_prim])
        if self.fuel_source:
            self.fuel_source.destroy()


class FuelSourceState(Enum):
    IDLE = 0
    IGNITION = 1
    FLAME = 2


# TODO: write a replacement fuel model that uses configurable fuel and smoke sources
# [METROPERF-943]
class FuelSource:
    def __init__(self, flame_emitter_prim : Usd.Prim):
        self.flame_emitter_prim = flame_emitter_prim

        self.timeline = omni.timeline.get_timeline_interface()
        self.ignition_time = self.timeline.get_current_time()

        self.flame_time = self.ignition_time + 5.0
        self._timeline_event_sub = self.timeline.get_timeline_event_stream().create_subscription_to_pop(
            lambda event: self._on_timeline_event(event), name="FuelSource::TimelineEvent"
        )

        # cache the state so we don't write usd attributes every frame
        self.state = FuelSourceState.IDLE

    def update_state(self, state: FuelSourceState):
        self.state = state
        if state == FuelSourceState.IDLE:
            self.flame_emitter_prim.GetAttribute("fuel").Set(0.0)
            self.flame_emitter_prim.GetAttribute("smoke").Set(0.0)
        elif state == FuelSourceState.IGNITION:
            self.flame_emitter_prim.GetAttribute("fuel").Set(0.0)
            self.flame_emitter_prim.GetAttribute("smoke").Set(2.0)
        elif state == FuelSourceState.FLAME:
            self.flame_emitter_prim.GetAttribute("fuel").Set(0.5)
            self.flame_emitter_prim.GetAttribute("smoke").Set(2.0)

    def _on_timeline_event(self, event: carb.events.IEvent):
        if event.type != omni.timeline.TimelineEventType.CURRENT_TIME_TICKED.value:
            return
        prev_state = self.state
        current_state = None
        current_time = self.timeline.get_current_time()
        if current_time <= self.ignition_time:
            current_state = FuelSourceState.IDLE
        elif current_time <= self.flame_time:
            current_state = FuelSourceState.IGNITION
        else:
            current_state = FuelSourceState.FLAME

        if prev_state != current_state:
            self.update_state(current_state)

    def destroy(self):
        self._timeline_event_sub.unsubscribe()
