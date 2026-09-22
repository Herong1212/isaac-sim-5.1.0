import omni
from pxr import UsdPhysics, Sdf
from ..incident_report import IncidentReport
from .topple_event_setup import ToppleEventSetup

from omni.metropolis.utils.triggers.core import TriggerBase


def get_curr_time_frame() -> int:
    t = omni.timeline.get_timeline_interface()
    return round(t.time_to_time_code(t.get_current_time()) * t.get_ticks_per_frame())


class ToppleEventObserver:
    """
    This class is responsible for observing a topple event.
    It is responsible for checking if the event is finished and calling the on_finished_callback.
    It creates data for the incident report.
    """

    TOPPLE_EVENT_FINISHED_EVENT = "isaacsim.replicator.incident.ToppleEventFinished"

    def __init__(
        self,
        event: ToppleEventSetup,
        report: IncidentReport,
        trigger: TriggerBase = None,
        on_finished_callback: callable = None,
    ):
        timeline = omni.timeline.get_timeline_interface()
        self.event = event
        self.report = report
        self.frames_duration = 0
        self.start_time_frame = get_curr_time_frame()
        self.update_sub = timeline.get_timeline_event_stream().create_subscription_to_pop(
            self.on_update, name="ToppleEventObserver"
        )
        self.on_finished_callback = on_finished_callback
        # Currently observer is created right after event is triggered,
        # so we write event data here
        if self.report:
            event_data = {
                "event_type": "Topple Event",
                "selected_loose_items": list(self.event.selected_loose_items),
                "topple_nearby_radius": self.event.topple_nearby_radius,
                "topple_prim_path": self.event.topple_prim_path,
                "topple_prim_location": str(self.event.topple_prim_location),
            }
            self.report.add_event_data(self.event.event_name, event_data)
            if trigger:
                self.report.add_trigger_data(self.event.event_name, trigger.to_dict())

    def destroy(self):
        self.update_sub = None

    def is_valid_prim(self, prim_path):
        if prim_path is None:
            return False
        context = omni.usd.get_context()
        stage = context.get_stage()  # Usd.Stage.Attach(stage_id)

        # If a prim does not already exist in Fabric,
        # it will be fetched from USD by simply creating the
        # Usd.Prim object. At this time, only the attributes that have
        # authored opinions will be fetch into Fabric.
        prim = stage.GetPrimAtPath(Sdf.Path(prim_path))

        if not prim:
            return False

        rigid_body_api = UsdPhysics.RigidBodyAPI(prim)
        if not rigid_body_api:
            return False
        return True

    def get_velocity(self, path):
        if path is None:
            return "Nothing selected"
        context = omni.usd.get_context()
        stage = context.get_stage()  # Usd.Stage.Attach(stage_id)

        # If a prim does not already exist in Fabric,
        # it will be fetched from USD by simply creating the
        # Usd.Prim object. At this time, only the attributes that have
        # authored opinions will be fetch into Fabric.
        prim = stage.GetPrimAtPath(Sdf.Path(path))

        if not prim:
            return None

        rigid_body_api = UsdPhysics.RigidBodyAPI(prim)
        if not rigid_body_api:
            return None

        return rigid_body_api.GetVelocityAttr().Get()

    def get_angular_velocity(self, path):
        if path is None:
            return "Nothing selected"
        context = omni.usd.get_context()
        stage = context.get_stage()  # Usd.Stage.Attach(stage_id)

        # If a prim does not already exist in Fabric,
        # it will be fetched from USD by simply creating the
        # Usd.Prim object. At this time, only the attributes that have
        # authored opinions will be fetch into Fabric.
        prim = stage.GetPrimAtPath(Sdf.Path(path))

        if not prim:
            return None

        rigid_body_api = UsdPhysics.RigidBodyAPI(prim)
        if not rigid_body_api:
            return None

        return rigid_body_api.GetAngularVelocityAttr().Get()

    def is_sleeping(self, path):
        if not self.is_valid_prim(path):
            return False
        from omni.physx.bindings._physx import acquire_physx_simulation_interface
        from pxr.PhysicsSchemaTools import sdfPathToInt

        physx_simulation = acquire_physx_simulation_interface()
        return physx_simulation.is_sleeping(omni.usd.get_context().get_stage_id(), sdfPathToInt(path))

    def on_update(self, e):
        if not e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED.value):
            return
        if self.frames_duration < 3:
            self.frames_duration += 1
            return
        # Observe
        self.frames_duration += 1
        for prim_path in self.event.selected_loose_items:
            if not self.is_sleeping(prim_path):
                return

        self.update_sub = None

        if self.report:
            sim_data = {
                "begin_time_frame": self.start_time_frame,
                "end_time_frame": get_curr_time_frame(),
            }
            self.report.add_simulation_data(self.event.event_name, sim_data)

        if self.on_finished_callback:
            self.on_finished_callback()


class ToppleEventObserverManager:
    def __init__(self):
        self.observers = []

    def destroy(self):
        for observer in self.observers:
            observer.destroy()
        self.observers = []

    def add_observer(
        self,
        event: ToppleEventSetup,
        report: IncidentReport = None,
        trigger: TriggerBase = None,
        on_finished_callback: callable = None,
    ):
        self.observers.append(ToppleEventObserver(event, report, trigger, on_finished_callback))
