# Public API for module omni.kit.collaboration.presence_layer:

## Classes

- class PresenceLayerAPI
  - def __init__(self, presence_layer_instance: PresenceLayerManager)
  - def is_bound_to_builtin_camera(self, user_id)
  - def get_bound_camera_prim(self, user_id) -> Union[Usd.Prim, None]
  - def get_following_user_id(self, user_id: str = None) -> str
  - def is_user_followed_by(self, user_id: str, followed_by_user_id: str) -> str
  - def get_selections(self, user_id: str) -> List[Sdf.Path]
  - def broadcast_local_bound_camera(self, local_camera_path: Sdf.Path)
  - def enter_follow_mode(self, following_user_id: str)
  - def quit_follow_mode(self)
  - def can_follow(self, user_id)
  - def is_in_following_mode(self, user_id: str = None)
  - def get_shared_data_stage(self) -> Usd.Stage

- class PresenceLayerEventType(IntEnum)
  - LOCAL_FOLLOW_MODE_CHANGED: Unknown
  - BOUND_CAMERA_CHANGED: Unknown
  - SELECTIONS_CHANGED: Unknown
  - BOUND_CAMERA_PROPERTIES_CHANGED: Unknown
  - BOUND_CAMERA_RESYNCED: Unknown

- class PresenceLayerEventPayload
  - def __init__(self, event: carb.events.IEvent)
  - [property] def changed_user_ids(self) -> List[str]
  - def get_changed_camera_properties(self, user_id: str) -> Set[str]

## Functions

- def get_presence_layer_interface(context_name_or_instance: Union[str, omni.usd.UsdContext] = '') -> Union[PresenceLayerAPI, None]
- def get_presence_layer_event_payload(event: carb.events.IEvent) -> PresenceLayerEventPayload

## Variables

- LAYER_SUBSCRIPTION_ORDER: Unknown
