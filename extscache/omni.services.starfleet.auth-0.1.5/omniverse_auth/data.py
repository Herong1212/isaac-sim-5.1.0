from typing import List, Optional, Dict, AsyncIterator
from idl.types import Enum, Record, Literal


Capabilities = Dict[str, int]
UserStoreServerRemoteCapabilities = Capabilities
UserStoreServerLocalCapabilities = {'get': 0, 'set': 0, 'remove': 0}
UserStoreServerCapabilities = UserStoreServerRemoteCapabilities
UserStoreClientRemoteCapabilities = Capabilities
UserStoreClientLocalCapabilities = {'get': 0, 'set': 0, 'remove': 0}
UserStoreClientCapabilities = UserStoreClientLocalCapabilities
UserStoreRemoveServerRemoteVersion = int
UserStoreRemoveServerLocalVersion = 0
UserStoreRemoveServerVersion = UserStoreRemoveServerRemoteVersion
UserStoreRemoveClientRemoteVersion = int
UserStoreRemoveClientLocalVersion = 0
UserStoreSetServerRemoteVersion = int
UserStoreSetServerLocalVersion = 0
UserStoreSetServerVersion = UserStoreSetServerRemoteVersion
UserStoreSetClientRemoteVersion = int
UserStoreSetClientLocalVersion = 0
UserStoreGetServerRemoteVersion = int
UserStoreGetServerLocalVersion = 0
UserStoreGetServerVersion = UserStoreGetServerRemoteVersion
UserStoreGetClientRemoteVersion = int
UserStoreGetClientLocalVersion = 0
TokensServerRemoteCapabilities = Capabilities
TokensServerLocalCapabilities = {'generate': 0, 'refresh': 0, 'subscribe': 0, 'create_api_token': 0, 'delete_api_token': 0, 'get_api_tokens': 0, 'auth_with_api_token': 0}
TokensServerCapabilities = TokensServerRemoteCapabilities
TokensClientRemoteCapabilities = Capabilities
TokensClientLocalCapabilities = {'generate': 0, 'refresh': 0, 'subscribe': 0, 'create_api_token': 0, 'delete_api_token': 0, 'get_api_tokens': 0, 'auth_with_api_token': 0}
TokensClientCapabilities = TokensClientLocalCapabilities
TokensAuthWithApiTokenServerRemoteVersion = int
TokensAuthWithApiTokenServerLocalVersion = 0
TokensAuthWithApiTokenServerVersion = TokensAuthWithApiTokenServerRemoteVersion
TokensAuthWithApiTokenClientRemoteVersion = int
TokensAuthWithApiTokenClientLocalVersion = 0
TokensGetApiTokensServerRemoteVersion = int
TokensGetApiTokensServerLocalVersion = 0
TokensGetApiTokensServerVersion = TokensGetApiTokensServerRemoteVersion
TokensGetApiTokensClientRemoteVersion = int
TokensGetApiTokensClientLocalVersion = 0
TokensDeleteApiTokenServerRemoteVersion = int
TokensDeleteApiTokenServerLocalVersion = 0
TokensDeleteApiTokenServerVersion = TokensDeleteApiTokenServerRemoteVersion
TokensDeleteApiTokenClientRemoteVersion = int
TokensDeleteApiTokenClientLocalVersion = 0
TokensCreateApiTokenServerRemoteVersion = int
TokensCreateApiTokenServerLocalVersion = 0
TokensCreateApiTokenServerVersion = TokensCreateApiTokenServerRemoteVersion
TokensCreateApiTokenClientRemoteVersion = int
TokensCreateApiTokenClientLocalVersion = 0
TokensSubscribeServerRemoteVersion = int
TokensSubscribeServerLocalVersion = 0
TokensSubscribeServerVersion = TokensSubscribeServerRemoteVersion
TokensSubscribeClientRemoteVersion = int
TokensSubscribeClientLocalVersion = 0
TokensRefreshServerRemoteVersion = int
TokensRefreshServerLocalVersion = 0
TokensRefreshServerVersion = TokensRefreshServerRemoteVersion
TokensRefreshClientRemoteVersion = int
TokensRefreshClientLocalVersion = 0
TokensGenerateServerRemoteVersion = int
TokensGenerateServerLocalVersion = 0
TokensGenerateServerVersion = TokensGenerateServerRemoteVersion
TokensGenerateClientRemoteVersion = int
TokensGenerateClientLocalVersion = 0
SSOServerRemoteCapabilities = Capabilities
SSOServerLocalCapabilities = {'get_settings': 0, 'auth': 1, 'redirect': 0}
SSOServerCapabilities = SSOServerRemoteCapabilities
SSOClientRemoteCapabilities = Capabilities
SSOClientLocalCapabilities = {'get_settings': 0, 'auth': 1, 'redirect': 0}
SSOClientCapabilities = SSOClientLocalCapabilities
SSORedirectServerRemoteVersion = int
SSORedirectServerLocalVersion = 0
SSORedirectServerVersion = SSORedirectServerRemoteVersion
SSORedirectClientRemoteVersion = int
SSORedirectClientLocalVersion = 0
SSOAuthServerRemoteVersion = int
SSOAuthServerLocalVersion = 1
SSOAuthServerVersion = SSOAuthServerRemoteVersion
SSOAuthClientRemoteVersion = int
SSOAuthClientLocalVersion = 1
SSOGetSettingsServerRemoteVersion = int
SSOGetSettingsServerLocalVersion = 0
SSOGetSettingsClientRemoteVersion = int
SSOGetSettingsClientLocalVersion = 0
ProfilesServerRemoteCapabilities = Capabilities
ProfilesServerLocalCapabilities = {'get_settings': 0, 'get_all': 0, 'get': 0, 'set_info': 0, 'set_enabled': 0, 'set_admin': 0, 'set_nucleus_ro': 0, 'add': 0}
ProfilesServerCapabilities = ProfilesServerRemoteCapabilities
ProfilesClientRemoteCapabilities = Capabilities
ProfilesClientLocalCapabilities = {'get_settings': 0, 'get_all': 0, 'get': 0, 'set_info': 0, 'set_enabled': 0, 'set_admin': 0, 'set_nucleus_ro': 0, 'add': 0}
ProfilesClientCapabilities = ProfilesClientLocalCapabilities
ProfilesAddServerRemoteVersion = int
ProfilesAddServerLocalVersion = 0
ProfilesAddServerVersion = ProfilesAddServerRemoteVersion
ProfilesAddClientRemoteVersion = int
ProfilesAddClientLocalVersion = 0
ProfilesSetNucleusRoServerRemoteVersion = int
ProfilesSetNucleusRoServerLocalVersion = 0
ProfilesSetNucleusRoServerVersion = ProfilesSetNucleusRoServerRemoteVersion
ProfilesSetNucleusRoClientRemoteVersion = int
ProfilesSetNucleusRoClientLocalVersion = 0
ProfilesSetAdminServerRemoteVersion = int
ProfilesSetAdminServerLocalVersion = 0
ProfilesSetAdminServerVersion = ProfilesSetAdminServerRemoteVersion
ProfilesSetAdminClientRemoteVersion = int
ProfilesSetAdminClientLocalVersion = 0
ProfilesSetEnabledServerRemoteVersion = int
ProfilesSetEnabledServerLocalVersion = 0
ProfilesSetEnabledServerVersion = ProfilesSetEnabledServerRemoteVersion
ProfilesSetEnabledClientRemoteVersion = int
ProfilesSetEnabledClientLocalVersion = 0
ProfilesSetInfoServerRemoteVersion = int
ProfilesSetInfoServerLocalVersion = 0
ProfilesSetInfoServerVersion = ProfilesSetInfoServerRemoteVersion
ProfilesSetInfoClientRemoteVersion = int
ProfilesSetInfoClientLocalVersion = 0
ProfilesGetServerRemoteVersion = int
ProfilesGetServerLocalVersion = 0
ProfilesGetServerVersion = ProfilesGetServerRemoteVersion
ProfilesGetClientRemoteVersion = int
ProfilesGetClientLocalVersion = 0
ProfilesGetAllServerRemoteVersion = int
ProfilesGetAllServerLocalVersion = 0
ProfilesGetAllServerVersion = ProfilesGetAllServerRemoteVersion
ProfilesGetAllClientRemoteVersion = int
ProfilesGetAllClientLocalVersion = 0
ProfilesGetSettingsServerRemoteVersion = int
ProfilesGetSettingsServerLocalVersion = 0
ProfilesGetSettingsClientRemoteVersion = int
ProfilesGetSettingsClientLocalVersion = 0
CredentialsServerRemoteCapabilities = Capabilities
CredentialsServerLocalCapabilities = {'get_settings': 0, 'auth': 1, 'register': 1, 'reset': 0}
CredentialsServerCapabilities = CredentialsServerRemoteCapabilities
CredentialsClientRemoteCapabilities = Capabilities
CredentialsClientLocalCapabilities = {'get_settings': 0, 'auth': 1, 'register': 1, 'reset': 0}
CredentialsClientCapabilities = CredentialsClientLocalCapabilities
CredentialsResetServerRemoteVersion = int
CredentialsResetServerLocalVersion = 0
CredentialsResetServerVersion = CredentialsResetServerRemoteVersion
CredentialsResetClientRemoteVersion = int
CredentialsResetClientLocalVersion = 0
CredentialsRegisterServerRemoteVersion = int
CredentialsRegisterServerLocalVersion = 1
CredentialsRegisterServerVersion = CredentialsRegisterServerRemoteVersion
CredentialsRegisterClientRemoteVersion = int
CredentialsRegisterClientLocalVersion = 1
CredentialsAuthServerRemoteVersion = int
CredentialsAuthServerLocalVersion = 1
CredentialsAuthServerVersion = CredentialsAuthServerRemoteVersion
CredentialsAuthClientRemoteVersion = int
CredentialsAuthClientLocalVersion = 1
CredentialsGetSettingsServerRemoteVersion = int
CredentialsGetSettingsServerLocalVersion = 0
CredentialsGetSettingsClientRemoteVersion = int
CredentialsGetSettingsClientLocalVersion = 0


class ApiToken(Record):
    name: str


class AuthStatus(metaclass=Enum):
    OK = "OK"
    NotFound = "NOT_FOUND"
    Exists = "EXISTS"
    Disabled = "DISABLED"
    Denied = "DENIED"
    Expired = "EXPIRED"
    ReadOnly = "READONLY"
    UsernameRequired = "USERNAME_REQUIRED"
    NotSupported = "NOT_SUPPORTED"
    ConnectionError = "CONNECTION_ERROR"
    InternalError = "INTERNAL_ERROR"
    InvalidUsername = "INVALID_USERNAME"
    UnknownError = "UNKNOWN_ERROR"
    InvalidToken = "INVALID_TOKEN"
    Subscribed = "SUBSCRIBED"


class AuthProvider(metaclass=Enum):
    Internal = "Internal"
    NVIDIA = "NVIDIA"
    Starfleet = "Starfleet"
    Microsoft = "Microsoft"
    System = "System"


SSOGetSettingsServerVersion = SSOGetSettingsServerRemoteVersion
ProfilesGetSettingsServerVersion = ProfilesGetSettingsServerRemoteVersion


class Profile(Record):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    admin: Optional[bool]
    provider: Optional[str]
    readonly: Optional[bool]
    nucleus_ro: Optional[bool]
    enabled: Optional[bool]
    activated: Optional[bool]


CredentialsGetSettingsServerVersion = CredentialsGetSettingsServerRemoteVersion


class UserStoreResult(Record):
    status: AuthStatus
    version: int
    value: Optional[str]


UserStoreRemoveClientVersion = UserStoreRemoveClientLocalVersion
UserStoreSetClientVersion = UserStoreSetClientLocalVersion
UserStoreGetClientVersion = UserStoreGetClientLocalVersion


class Auth(Record):
    status: AuthStatus
    version: int
    access_token: Optional[str]
    refresh_token: Optional[str]
    username: Optional[str]
    profile: Optional[Profile]
    nonce: Optional[str]


TokensAuthWithApiTokenClientVersion = TokensAuthWithApiTokenClientLocalVersion


class GetApiTokens(Record):
    status: AuthStatus
    version: int
    tokens: Optional[List[ApiToken]]


TokensGetApiTokensClientVersion = TokensGetApiTokensClientLocalVersion


class DeleteApiToken(Record):
    status: AuthStatus
    version: int


TokensDeleteApiTokenClientVersion = TokensDeleteApiTokenClientLocalVersion


class CreateApiToken(Record):
    status: AuthStatus
    version: int
    token: Optional[str]


TokensCreateApiTokenClientVersion = TokensCreateApiTokenClientLocalVersion
TokensSubscribeClientVersion = TokensSubscribeClientLocalVersion
TokensRefreshClientVersion = TokensRefreshClientLocalVersion
TokensGenerateClientVersion = TokensGenerateClientLocalVersion


class SSORedirect(Record):
    status: AuthStatus
    redirect: str


SSORedirectClientVersion = SSORedirectClientLocalVersion


SSOParams = Dict[str, str]
SSOAuthClientVersion = SSOAuthClientLocalVersion


class SSOSettings(Record):
    public_name: str
    type: str
    redirect: str
    image: str
    version: SSOGetSettingsServerVersion


SSOGetSettingsClientVersion = SSOGetSettingsClientLocalVersion


class ProfileResponse(Record):
    status: AuthStatus
    version: int
    username: Optional[str]
    profile: Optional[Profile]


ProfilesAddClientVersion = ProfilesAddClientLocalVersion
ProfilesSetNucleusRoClientVersion = ProfilesSetNucleusRoClientLocalVersion
ProfilesSetAdminClientVersion = ProfilesSetAdminClientLocalVersion
ProfilesSetEnabledClientVersion = ProfilesSetEnabledClientLocalVersion
ProfilesSetInfoClientVersion = ProfilesSetInfoClientLocalVersion
ProfilesGetClientVersion = ProfilesGetClientLocalVersion
ProfilesGetAllClientVersion = ProfilesGetAllClientLocalVersion


class ProfileSettings(Record):
    can_manage: bool
    version: ProfilesGetSettingsServerVersion


ProfilesGetSettingsClientVersion = ProfilesGetSettingsClientLocalVersion
CredentialsResetClientVersion = CredentialsResetClientLocalVersion
CredentialsRegisterClientVersion = CredentialsRegisterClientLocalVersion
CredentialsAuthClientVersion = CredentialsAuthClientLocalVersion


class CredentialSettings(Record):
    login_url: Optional[str]
    can_register: Optional[bool]
    is_ui_visible: Optional[bool]
    version: Optional[CredentialsGetSettingsServerVersion]


CredentialsGetSettingsClientVersion = CredentialsGetSettingsClientLocalVersion