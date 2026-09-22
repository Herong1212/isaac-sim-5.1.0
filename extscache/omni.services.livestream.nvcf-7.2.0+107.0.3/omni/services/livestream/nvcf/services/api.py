# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

"""REST API for the livestream nvcf service."""

import carb
import time
import omni.kit.app
import omni.kit.livestream.bind

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from omni.services.core import routers
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks


class StreamingCredentialsRequestModel(BaseModel):
    """The nvcf streaming credentials."""

    stunIp: Optional[str] = Field(
        None,
        title="STUN IP",
        description="The IP of the STUN server.",
    )
    stunPort: Optional[int] = Field(
        None,
        title="STUN Port",
        description="The port of the STUN server.",
    )
    username: Optional[str] = Field(
        None,
        title="Username",
        description="The username.",
    )
    password: Optional[str] = Field(
        None,
        title="Password",
        description="The password.",
    )
    privateSharedPort: Optional[int] = Field(
        None,
        title="Private Shared Port",
        description="The private shared port.",
    )

class StreamingCredentialsResponseModel(BaseModel):
    """Response to the nvcf streaming credentials request."""

    success: bool = Field(
        ...,
        title="Success",
        description="Flag indicating if the request was successful.",
    )
    errorMessage: Optional[str] = Field(
        None,
        title="Error message",
        description="Details about the error that occurred, in case of failure.",
    )

class EndSessionRequestModel(BaseModel):
    """The nvcf end session request."""

    sessionId: Optional[str] = Field(
        None,
        title="Session Id",
        description="The Id of the streaming session.",
    )

    gracefulShutdown: Optional[bool] = Field(
        None,
        title="Graceful shutdown",
        description="Did the session end gracefully or not?",
    )

class EndSessionResponseModel(BaseModel):
    """Response to the nvcf end session request."""

    sessionStatus: Optional[str] = Field(
        None,
        title="Status message",
        description="Details about the current streaming session status.",
    )

class StreamingReadyResponseModel(BaseModel):
    statusMessage: Optional[str] = Field(
        None,
        title="Status message",
        description="Details about the current streaming ready status.",
    )

router = routers.ServiceAPIRouter()
app_ready = False
rtx_ready = False
custom_ready = False
client_connected = False
quit_on_session_ended = True
streaming_session_ended = False
waiting_for_session_resume = False
session_resume_timeout_seconds = 0
session_resume_timeout_started = None
wait_for_custom_ready_event = False
waiting_for_client_disconnect = False

def on_session_ended(background_tasks: BackgroundTasks):
    global custom_ready, session_resume_timeout_started, quit_on_session_ended, streaming_session_ended, client_connected, waiting_for_client_disconnect

    custom_ready = False
    session_resume_timeout_started = None
    if quit_on_session_ended:
        # Immediately quit the application.
        background_tasks.add_task(omni.kit.app.get_app().post_uncancellable_quit(0))
        streaming_session_ended = True
    else:
        # Send an event so the app can respond as needed.
        session_ended_event_type = carb.events.type_from_string("omni.services.livestream.nvcf.session_ended")
        omni.kit.app.get_app().get_message_bus_event_stream().push(session_ended_event_type)

        # If a client is currently connected, we must also wait for it to disconnect.
        if client_connected:
            waiting_for_client_disconnect = True
            carb.log_warn(f"omni.services.livestream.nvcf session ending while client still connected.")

@router.post(
    "/v1/streaming/creds",
    summary="Post the nvcf streaming credentials.",
    description="Post the nvcf streaming credentials.",
    response_model=StreamingCredentialsResponseModel,
)
def post_streaming_credentials(data: StreamingCredentialsRequestModel) -> StreamingCredentialsResponseModel:
    try:
        carb.log_verbose(f"omni.services.livestream.nvcf stunIp: {data.stunIp}")
        carb.log_verbose(f"omni.services.livestream.nvcf stunPort: {data.stunPort}")
        if data.privateSharedPort:
            carb.log_verbose(f"omni.services.livestream.nvcf privateSharedPort: {data.privateSharedPort}")

        kit_livestream = omni.kit.livestream.bind.acquire_livestream_interface()
        if data.privateSharedPort:
            kit_livestream.set_stun_credentials_with_shared_port(data.stunIp, data.stunPort, data.username, data.password, data.privateSharedPort)
        else:
            kit_livestream.set_stun_credentials(data.stunIp, data.stunPort, data.username, data.password)
        kit_livestream = None
        return StreamingCredentialsResponseModel(success=True)
    except Exception as exc:
        return StreamingCredentialsResponseModel(success=False, errorMessage=str(exc))


@router.post(
    "/v1/streaming/endsession",
    summary="Post the nvcf end session request.",
    description="Post the nvcf end session request.",
    response_model=EndSessionResponseModel,
)
async def end_session(data: EndSessionRequestModel, background_tasks: BackgroundTasks) -> EndSessionResponseModel:
    global session_resume_timeout_started, session_resume_timeout_seconds

    response = EndSessionResponseModel()
    if data.gracefulShutdown:
        # "Intended" disconnect, end the session.
        carb.log_info(f"omni.services.livestream.nvcf received request to end session `{data.sessionId}` gracefully, ending session.")
        response.sessionStatus = "COMPLETE"
        on_session_ended(background_tasks)
    elif session_resume_timeout_started:
        elapsed = time.time() - session_resume_timeout_started
        if (elapsed >= session_resume_timeout_seconds):
            # Resume timeout elapsed, end the session.
            carb.log_info(f"omni.services.livestream.nvcf received request to end session `{data.sessionId}` and the resume timeout of {session_resume_timeout_seconds} seconds has expired, ending session.")
            response.sessionStatus = "COMPLETE"
            on_session_ended(background_tasks)
        else:
            # Keep waiting for the session to resume.
            carb.log_info(f"omni.services.livestream.nvcf received request to end session `{data.sessionId}` and the resume timeout of {session_resume_timeout_seconds} seconds has not expired ({elapsed}ms elapsed).")
            response.sessionStatus = "AWAITING_RESUME"
    elif session_resume_timeout_seconds and session_resume_timeout_seconds > 0:
        # Unintended disconnect and resume is allowed, start waiting.
        carb.log_info(f"omni.services.livestream.nvcf received request to end session `{data.sessionId}` and the resume timeout is set to {session_resume_timeout_seconds} seconds, starting resume window.")
        session_resume_timeout_started = time.time()
        response.sessionStatus = "AWAITING_RESUME"
    else:
        # Unintended disconnect and resume is not allowed, end the session.
        carb.log_info(f"omni.services.livestream.nvcf received request to end session `{data.sessionId}` and the resume timeout is not set, ending session.")
        response.sessionStatus = "COMPLETE"
        on_session_ended(background_tasks)

    return response


@router.get(
    "/v1/streaming/ready",
    summary="Health endpoint for the streaming service.",
    description="Health endpoint for the streaming service.",
    response_model=StreamingReadyResponseModel,
)
def get_streaming_ready() -> StreamingReadyResponseModel:
    response = StreamingReadyResponseModel()
    if not app_ready:
        response.statusMessage = "Status: App not ready"
        return JSONResponse(content=response.dict(), status_code=503) # Service unavailable
    elif not rtx_ready:
        response.statusMessage = "Status: Rtx not ready"
        return JSONResponse(content=response.dict(), status_code=503) # Service unavailable
    elif wait_for_custom_ready_event and not custom_ready:
        response.statusMessage = "Status: Custom ready event not received"
        return JSONResponse(content=response.dict(), status_code=503) # Service unavailable
    elif waiting_for_client_disconnect:
        response.statusMessage = "Status: Waiting for previous client to disconnect"
        return JSONResponse(content=response.dict(), status_code=503) # Service unavailable
    elif streaming_session_ended:
        response.statusMessage = "Status: Streaming session ended (recycle instance)"
        return JSONResponse(content=response.dict(), status_code=503) # Service unavailable
    elif session_resume_timeout_started:
        response.statusMessage = "Status: Awaiting session resume (keep alive)"
        return response
    elif client_connected:
        response.statusMessage = "Status: Streaming session active (keep alive)"
        return response

    response.statusMessage = "Status: Ready for connection"
    return response
