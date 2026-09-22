from typing import AsyncIterator, Dict, List, Optional

from idl.connection.transport import Client
from idl.types import Literal, Record

from .data import *


class UserStore:
    def __init__(self, transport: Client):
        self.transport = transport

    async def __aenter__(self) -> 'UserStore':
        await self.transport.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.close()
    
    async def get(self, key: str, token: str) -> UserStoreResult:
        """
        Returns value in the user's store by the specified key.
        If the key does not exist, returns AuthStatus.NotFound.
        """
        _request = {}
        _request["version"] = UserStoreGetClientVersion
        _request["key"] = key
        _request["token"] = token
        _response = await self.transport.call("UserStore", "get", _request, request_type=UserStoreGetArgs, return_type=UserStoreResult)
        return _response
    
    async def set(self, key: str, value: str, token: str) -> UserStoreResult:
        """
        
        """
        _request = {}
        _request["version"] = UserStoreSetClientVersion
        _request["key"] = key
        _request["value"] = value
        _request["token"] = token
        _response = await self.transport.call("UserStore", "set", _request, request_type=UserStoreSetArgs, return_type=UserStoreResult)
        return _response
    
    async def remove(self, key: str, token: str) -> UserStoreResult:
        """
        Removes value from the user's store by the specified key.
        If the key does not exist, returns AuthStatus.NotFound.
        """
        _request = {}
        _request["version"] = UserStoreRemoveClientVersion
        _request["key"] = key
        _request["token"] = token
        _response = await self.transport.call("UserStore", "remove", _request, request_type=UserStoreRemoveArgs, return_type=UserStoreResult)
        return _response
    
    __interface_name__ = "UserStore"
    __interface_origin__ = "OmniAuth.idl.ts"
    __interface_capabilities__ = UserStoreClientLocalCapabilities
    

class Tokens:
    def __init__(self, transport: Client):
        self.transport = transport

    async def __aenter__(self) -> 'Tokens':
        await self.transport.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.close()
    
    async def generate(self, username: str, admin_token: str) -> Auth:
        """
        Allows administrator to generate tokens for users.
        Can let the user to work in a system for a limited period of time and
        reset his password.
        """
        _request = {}
        _request["version"] = TokensGenerateClientVersion
        _request["username"] = username
        _request["admin_token"] = admin_token
        _response = await self.transport.call("Tokens", "generate", _request, request_type=TokensGenerateArgs, return_type=Auth)
        return _response
    
    async def refresh(self, refresh_token: str) -> Auth:
        """
        Refreshes the authentication using a refresh token.
        """
        _request = {}
        _request["version"] = TokensRefreshClientVersion
        _request["refresh_token"] = refresh_token
        _response = await self.transport.call("Tokens", "refresh", _request, request_type=TokensRefreshArgs, return_type=Auth)
        return _response
    
    async def subscribe(self, ) -> AsyncIterator[Auth]:
        """
        Returns `nonce` with a random string and subscribes to its
        authentication results.
        Clients can use the login form with the `nonce` query argument.
        In this case, the login form will pass this `nonce` string back to the
        service to make it
        publish authentication tokens to this subscription.

        The first response returns an object with `status` equal to
        `AuthStatus.Subscribed` and `nonce`
        that should be sent to the login form.
        The following response returns the authentication result from the login
        form.
        """
        _request = {}
        _request["version"] = TokensSubscribeClientVersion
        agen = self.transport.call_many("Tokens", "subscribe", _request, request_type=TokensSubscribeArgs, return_type=Auth)
        try:
            async for _response in agen:
                yield _response
        finally:
            await agen.aclose()
    
    async def create_api_token(self, access_token: str, name: str) -> CreateApiToken:
        """
        Create a new API token
        """
        _request = {}
        _request["version"] = TokensCreateApiTokenClientVersion
        _request["access_token"] = access_token
        _request["name"] = name
        _response = await self.transport.call("Tokens", "create_api_token", _request, request_type=TokensCreateApiTokenArgs, return_type=CreateApiToken)
        return _response
    
    async def delete_api_token(self, access_token: str, name: str) -> DeleteApiToken:
        """
        Delete API token
        """
        _request = {}
        _request["version"] = TokensDeleteApiTokenClientVersion
        _request["access_token"] = access_token
        _request["name"] = name
        _response = await self.transport.call("Tokens", "delete_api_token", _request, request_type=TokensDeleteApiTokenArgs, return_type=DeleteApiToken)
        return _response
    
    async def get_api_tokens(self, access_token: str) -> GetApiTokens:
        """
        List API tokens
        """
        _request = {}
        _request["version"] = TokensGetApiTokensClientVersion
        _request["access_token"] = access_token
        _response = await self.transport.call("Tokens", "get_api_tokens", _request, request_type=TokensGetApiTokensArgs, return_type=GetApiTokens)
        return _response
    
    async def auth_with_api_token(self, api_token: str) -> Auth:
        """
        Auth using API token
        """
        _request = {}
        _request["version"] = TokensAuthWithApiTokenClientVersion
        _request["api_token"] = api_token
        _response = await self.transport.call("Tokens", "auth_with_api_token", _request, request_type=TokensAuthWithApiTokenArgs, return_type=Auth)
        return _response
    
    __interface_name__ = "Tokens"
    __interface_origin__ = "OmniAuth.idl.ts"
    __interface_capabilities__ = TokensClientLocalCapabilities
    

class SSO:
    def __init__(self, transport: Client):
        self.transport = transport

    async def __aenter__(self) -> 'SSO':
        await self.transport.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.close()
    
    async def get_settings(self, ) -> AsyncIterator[SSOSettings]:
        """
        
        """
        _request = {}
        _request["version"] = SSOGetSettingsClientVersion
        agen = self.transport.call_many("SSO", "get_settings", _request, request_type=SsoGetSettingsArgs, return_type=SSOSettings)
        try:
            async for _response in agen:
                yield _response
        finally:
            await agen.aclose()
    
    async def auth(self, type: str, params: SSOParams, nonce: Optional[str] = None) -> Auth:
        """
        Authenticates the client using the SSO parameters passed by an external
        authentication provider.
        Supports `nonce` that represents a random string generated by the
        service to let clients subscribe to
        the authentication results.
        """
        _request = {}
        _request["version"] = SSOAuthClientVersion
        _request["type"] = type
        _request["params"] = params
        if nonce is not None:
            _request["nonce"] = nonce
        _response = await self.transport.call("SSO", "auth", _request, request_type=SsoAuthArgs, return_type=Auth)
        return _response
    
    async def redirect(self, type: str, state: Optional[str] = None) -> SSORedirect:
        """
        Returns a redirect URL that can be used to navigate to the external
        authentication provider.
        Might be needed for some authentication methods that require to sign
        the query parameters.

        The `state` argument allows to pass local state to be sent the
        authentication provider
        and then restored back in the application when the SSO result is
        returned.
        """
        _request = {}
        _request["version"] = SSORedirectClientVersion
        _request["type"] = type
        if state is not None:
            _request["state"] = state
        _response = await self.transport.call("SSO", "redirect", _request, request_type=SsoRedirectArgs, return_type=SSORedirect)
        return _response
    
    __interface_name__ = "SSO"
    __interface_origin__ = "OmniAuth.idl.ts"
    __interface_capabilities__ = SSOClientLocalCapabilities
    

class Profiles:
    def __init__(self, transport: Client):
        self.transport = transport

    async def __aenter__(self) -> 'Profiles':
        await self.transport.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.close()
    
    async def get_settings(self, ) -> ProfileSettings:
        """
        
        """
        _request = {}
        _request["version"] = ProfilesGetSettingsClientVersion
        _response = await self.transport.call("Profiles", "get_settings", _request, request_type=ProfilesGetSettingsArgs, return_type=ProfileSettings)
        return _response
    
    async def get_all(self, token: str) -> AsyncIterator[ProfileResponse]:
        """
        
        """
        _request = {}
        _request["version"] = ProfilesGetAllClientVersion
        _request["token"] = token
        agen = self.transport.call_many("Profiles", "get_all", _request, request_type=ProfilesGetAllArgs, return_type=ProfileResponse)
        try:
            async for _response in agen:
                yield _response
        finally:
            await agen.aclose()
    
    async def get(self, username: str) -> ProfileResponse:
        """
        
        """
        _request = {}
        _request["version"] = ProfilesGetClientVersion
        _request["username"] = username
        _response = await self.transport.call("Profiles", "get", _request, request_type=ProfilesGetArgs, return_type=ProfileResponse)
        return _response
    
    async def set_info(self, username: str, token: str, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None) -> ProfileResponse:
        """
        
        """
        _request = {}
        _request["version"] = ProfilesSetInfoClientVersion
        _request["username"] = username
        _request["token"] = token
        if first_name is not None:
            _request["first_name"] = first_name
        if last_name is not None:
            _request["last_name"] = last_name
        if email is not None:
            _request["email"] = email
        _response = await self.transport.call("Profiles", "set_info", _request, request_type=ProfilesSetInfoArgs, return_type=ProfileResponse)
        return _response
    
    async def set_enabled(self, username: str, token: str, enabled: bool) -> ProfileResponse:
        """
        
        """
        _request = {}
        _request["version"] = ProfilesSetEnabledClientVersion
        _request["username"] = username
        _request["token"] = token
        _request["enabled"] = enabled
        _response = await self.transport.call("Profiles", "set_enabled", _request, request_type=ProfilesSetEnabledArgs, return_type=ProfileResponse)
        return _response
    
    async def set_admin(self, username: str, token: str, admin: bool) -> ProfileResponse:
        """
        
        """
        _request = {}
        _request["version"] = ProfilesSetAdminClientVersion
        _request["username"] = username
        _request["token"] = token
        _request["admin"] = admin
        _response = await self.transport.call("Profiles", "set_admin", _request, request_type=ProfilesSetAdminArgs, return_type=ProfileResponse)
        return _response
    
    async def set_nucleus_ro(self, username: str, token: str, nucleus_ro: bool) -> ProfileResponse:
        """
        
        """
        _request = {}
        _request["version"] = ProfilesSetNucleusRoClientVersion
        _request["username"] = username
        _request["token"] = token
        _request["nucleus_ro"] = nucleus_ro
        _response = await self.transport.call("Profiles", "set_nucleus_ro", _request, request_type=ProfilesSetNucleusRoArgs, return_type=ProfileResponse)
        return _response
    
    async def add(self, username: str, token: str, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None) -> ProfileResponse:
        """
        
        """
        _request = {}
        _request["version"] = ProfilesAddClientVersion
        _request["username"] = username
        _request["token"] = token
        if first_name is not None:
            _request["first_name"] = first_name
        if last_name is not None:
            _request["last_name"] = last_name
        if email is not None:
            _request["email"] = email
        _response = await self.transport.call("Profiles", "add", _request, request_type=ProfilesAddArgs, return_type=ProfileResponse)
        return _response
    
    __interface_name__ = "Profiles"
    __interface_origin__ = "OmniAuth.idl.ts"
    __interface_capabilities__ = ProfilesClientLocalCapabilities
    

class Credentials:
    def __init__(self, transport: Client):
        self.transport = transport

    async def __aenter__(self) -> 'Credentials':
        await self.transport.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.close()
    
    async def get_settings(self, ) -> CredentialSettings:
        """
        
        """
        _request = {}
        _request["version"] = CredentialsGetSettingsClientVersion
        _response = await self.transport.call("Credentials", "get_settings", _request, request_type=CredentialsGetSettingsArgs, return_type=CredentialSettings)
        return _response
    
    async def auth(self, username: str, password: str, nonce: Optional[str] = None) -> Auth:
        """
        Authenticates the client using the specified credentials.
        Supports `nonce` that represents a random string generated by the
        service to let clients subscribe to
        the authentication results.
        """
        _request = {}
        _request["version"] = CredentialsAuthClientVersion
        _request["username"] = username
        _request["password"] = password
        if nonce is not None:
            _request["nonce"] = nonce
        _response = await self.transport.call("Credentials", "auth", _request, request_type=CredentialsAuthArgs, return_type=Auth)
        return _response
    
    async def register(self, username: str, password: str, profile: Profile, nonce: Optional[str] = None) -> Auth:
        """
        Register the client using the specified credentials and profile.
        Supports `nonce` that represents a random string generated by the
        service to let clients subscribe to
        the authentication results.
        """
        _request = {}
        _request["version"] = CredentialsRegisterClientVersion
        _request["username"] = username
        _request["password"] = password
        _request["profile"] = profile
        if nonce is not None:
            _request["nonce"] = nonce
        _response = await self.transport.call("Credentials", "register", _request, request_type=CredentialsRegisterArgs, return_type=Auth)
        return _response
    
    async def reset(self, username: str, new_password: str, token: str) -> Auth:
        """
        
        """
        _request = {}
        _request["version"] = CredentialsResetClientVersion
        _request["username"] = username
        _request["new_password"] = new_password
        _request["token"] = token
        _response = await self.transport.call("Credentials", "reset", _request, request_type=CredentialsResetArgs, return_type=Auth)
        return _response
    
    __interface_name__ = "Credentials"
    __interface_origin__ = "OmniAuth.idl.ts"
    __interface_capabilities__ = CredentialsClientLocalCapabilities


class UserStoreGetArgs(Record):
    version: Literal(UserStoreGetClientVersion) = UserStoreGetClientVersion
    key: str
    token: str


class UserStoreSetArgs(Record):
    version: Literal(UserStoreSetClientVersion) = UserStoreSetClientVersion
    key: str
    value: str
    token: str


class UserStoreRemoveArgs(Record):
    version: Literal(UserStoreRemoveClientVersion) = UserStoreRemoveClientVersion
    key: str
    token: str


class TokensGenerateArgs(Record):
    version: Literal(TokensGenerateClientVersion) = TokensGenerateClientVersion
    username: str
    admin_token: str


class TokensRefreshArgs(Record):
    version: Literal(TokensRefreshClientVersion) = TokensRefreshClientVersion
    refresh_token: str


class TokensSubscribeArgs(Record):
    version: Literal(TokensSubscribeClientVersion) = TokensSubscribeClientVersion


class TokensCreateApiTokenArgs(Record):
    version: Literal(TokensCreateApiTokenClientVersion) = TokensCreateApiTokenClientVersion
    access_token: str
    name: str


class TokensDeleteApiTokenArgs(Record):
    version: Literal(TokensDeleteApiTokenClientVersion) = TokensDeleteApiTokenClientVersion
    access_token: str
    name: str


class TokensGetApiTokensArgs(Record):
    version: Literal(TokensGetApiTokensClientVersion) = TokensGetApiTokensClientVersion
    access_token: str


class TokensAuthWithApiTokenArgs(Record):
    version: Literal(TokensAuthWithApiTokenClientVersion) = TokensAuthWithApiTokenClientVersion
    api_token: str


class SsoGetSettingsArgs(Record):
    version: Literal(SSOGetSettingsClientVersion) = SSOGetSettingsClientVersion


class SsoAuthArgs(Record):
    version: Literal(SSOAuthClientVersion) = SSOAuthClientVersion
    type: str
    params: SSOParams
    nonce: Optional[str]


class SsoRedirectArgs(Record):
    version: Literal(SSORedirectClientVersion) = SSORedirectClientVersion
    type: str
    state: Optional[str]


class ProfilesGetSettingsArgs(Record):
    version: Literal(ProfilesGetSettingsClientVersion) = ProfilesGetSettingsClientVersion


class ProfilesGetAllArgs(Record):
    version: Literal(ProfilesGetAllClientVersion) = ProfilesGetAllClientVersion
    token: str


class ProfilesGetArgs(Record):
    version: Literal(ProfilesGetClientVersion) = ProfilesGetClientVersion
    username: str


class ProfilesSetInfoArgs(Record):
    version: Literal(ProfilesSetInfoClientVersion) = ProfilesSetInfoClientVersion
    username: str
    token: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]


class ProfilesSetEnabledArgs(Record):
    version: Literal(ProfilesSetEnabledClientVersion) = ProfilesSetEnabledClientVersion
    username: str
    token: str
    enabled: bool


class ProfilesSetAdminArgs(Record):
    version: Literal(ProfilesSetAdminClientVersion) = ProfilesSetAdminClientVersion
    username: str
    token: str
    admin: bool


class ProfilesSetNucleusRoArgs(Record):
    version: Literal(ProfilesSetNucleusRoClientVersion) = ProfilesSetNucleusRoClientVersion
    username: str
    token: str
    nucleus_ro: bool


class ProfilesAddArgs(Record):
    version: Literal(ProfilesAddClientVersion) = ProfilesAddClientVersion
    username: str
    token: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]


class CredentialsGetSettingsArgs(Record):
    version: Literal(CredentialsGetSettingsClientVersion) = CredentialsGetSettingsClientVersion


class CredentialsAuthArgs(Record):
    version: Literal(CredentialsAuthClientVersion) = CredentialsAuthClientVersion
    username: str
    password: str
    nonce: Optional[str]


class CredentialsRegisterArgs(Record):
    version: Literal(CredentialsRegisterClientVersion) = CredentialsRegisterClientVersion
    username: str
    password: str
    profile: Profile
    nonce: Optional[str]


class CredentialsResetArgs(Record):
    version: Literal(CredentialsResetClientVersion) = CredentialsResetClientVersion
    username: str
    new_password: str
    token: str

