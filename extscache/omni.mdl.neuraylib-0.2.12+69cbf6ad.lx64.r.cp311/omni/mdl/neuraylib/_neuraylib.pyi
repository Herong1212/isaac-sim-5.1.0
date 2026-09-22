from __future__ import annotations
import omni.mdl.neuraylib._neuraylib
import typing

__all__ = [
    "Interop",
    "MdlEntity",
    "MdlEntitySnapshot",
    "MdlModule",
    "NeurayLib",
    "acquire_interface",
    "release_interface"
]


class Interop():
    """
    A Collection of functions to support renderer and tools with common tasks.
    """
    def recreateMaterialInScope(self, arg0: MdlEntitySnapshot, arg1: str, arg2: str) -> bool: 
        """
        Creates a deep copy of a material in a temporary scope.
        This includes module loading and resource resolution.
        It's meant to be used by tools that work with the MDL representation like the exporters or bakers.
        """
    pass
class MdlEntity():
    """
    Maps between USD shade nodes and the MDL representation of a shade node.

    Identified by the USD Prim Path, different components can access this entity in a scene.
    """
    def getMdlModule(self) -> MdlModule: 
        """
        Handle to the module that contains the entities definition.

        This can change during the lifetime of the object.
        Since this is module is not 'created' here, don't call `destroy` on it.
        """
    def valid(self) -> bool: 
        """
        Get the state of entity. It is valid if a module a simple name is assigned.
        """
    @property
    def dbScopeName(self) -> str:
        """
                Name of the neuray database scope of the ISceneRenderer in which this entity is stored in.

                This can NOT change during the lifetime of the object.
                

        :type: str
        """
    @property
    def simpleNameWithSignature(self) -> str:
        """
                Name of the material or function within its module along with its parameter list attached.
                This can change during the lifetime of the object.
                

        :type: str
        """
    @property
    def uniquePrimPath(self) -> str:
        """
                The USD Prim Path that identifies this entity in the scene.

                This can NOT change during the lifetime of the object.
                

        :type: str
        """
    pass
class MdlEntitySnapshot():
    """
    MDL representation of a shade node along with the currently set parameters.
    Parameters can be inspected while changes are reflected from USD (in rtx.hydra.plugin).
    This snapshot is passed to the ISceneRenderer for creating and updating the renderer material.

    Created from an MdlEntity at a certain point in time. When the MdlEntity did not change in the meantime, the same
    MdlEntitySnapshot can be accessed using the create function.
    When the MdlEntity changed (different module or function name),
    a new snapshot can be created while to old one still exist but might not be valid anymore (in case of reloads).
    """
    def getMdlModule(self) -> MdlModule: 
        """
        Handle to the module that contains the entities definition.
        Since this module is not 'created' here, don't call `destroy` on it.
        """
    @property
    def dbName(self) -> str:
        """
        Name of a MDL material instance or functions call in the neuray database.

        :type: str
        """
    @property
    def dbScopeName(self) -> str:
        """
        Name of the neuray database scope (of the ISceneRenderer) in which this entity is stored in.

        :type: str
        """
    @property
    def simpleNameWithSignature(self) -> str:
        """
        Name of the material or function within its module along with its parameter list attached.

        :type: str
        """
    pass
class MdlModule():
    """
    The representation of an MDL module to load or loaded by neuray.
    """
    def valid(self) -> bool: 
        """
        Get the state of module, describes if loaded and if valid or not
        """
    @property
    def dbName(self) -> str:
        """
        The name of the MDL module in the neuray database.

        :type: str
        """
    @property
    def dbScopeName(self) -> str:
        """
        The name of the DB scope to load the definitions to.

        :type: str
        """
    @property
    def qualifiedName(self) -> str:
        """
        The fully qualified MDL name of the module

        :type: str
        """
    pass
class NeurayLib():
    """
    Access to the MDL Material back-end in Omniverse.
    """
    def ResolveTiledResourceUri(self, arg0: str) -> typing.List[str]: 
        """
        Collect the matching file URIs for a given resolved URI that contains a mask.

        Args:
            resolvedFileNameMask: A resolved URI that contains the a tiling marker like ``%3CUDIM%3E`` which is the uri encoding for ``<UDIM>``.
        """
    def _getInterop(self) -> Interop: 
        """
        Get access to the interop functions.
        """
    def _mangleUri(self, arg0: str, arg1: str) -> str: 
        """
        Temporary internal functions that is required for the USD to MDL exporter.
        Will be removed or changed as soon as mangling is removed or simplified.
        """
    def _unmangleMdlModulePath(self, arg0: str) -> str: 
        """
        Temporary internal functions that is required for the USD to MDL exporter.

        Will be removed or changed as soon as mangling is removed or simplified.
        """
    def _unmangleUri(self, arg0: str, arg1: str) -> str: 
        """
        Temporary internal functions that is required for the USD to MDL exporter.

        Will be removed or changed as soon as mangling is removed or simplified.
        """
    def createEditingTransaction(self, dbScopeName: str = '') -> int: 
        """
        Creates a write access transaction for a given database scope with short term usage in mind.

        This transaction should be used for write access e.g. for editing a material instance
        code. Use the transaction on a per task level and from one thread only.
        When done, call `commit` in case you made changes or `abort` in case you only read information.
        However, keep in mind that the this new transaction can only see DB state that was already committed.
        The function returns a handle hat has to be attached to the MDL SDK API using `omni.mdl.pymdlsdk.attach_itransaction`.

        Args:
            dbScopeName (optional): Name of the DB scope to edit.

        Returns:
            The created transaction or `None` if the creation failed, e.g. because of an invalid scope.
        """
    def createMdlEntity(self, uniquePrimPath: str, dbScopeName: str = '') -> MdlEntity: 
        """
        Creates an MdlEnity for a selected scope. It maps an MDL representation to a particular USD shade graph node.

        If there already is an MdlEntity the same object is returned again with an increased reference count.
        This allows multiple components to access the same data based on the USD Prim Path.

        Args:
            uniquePrimPath: USD path of the shade node this entity will belong to.
                            Allows to identify the node from different kit components.

            scopeName (optional): Name of the DB scope to later store snapshots in (default: '').

        Returns:
            The handle that represents the shade USD graph node.
            Needs to be released using `destroyMdlEntity` when not required anymore.
        """
    def createMdlEntitySnapshot(self, arg0: MdlEntity) -> MdlEntitySnapshot: 
        """
        Creates an MDL material instance or function call in the neuray DB scope provided.

        This snapshot is used for editing and creating material representations specific to the renderer.
        If there already is a valid snapshot for this MdlEntity and if the selected function name did not change,
        the same snapshot is returned again with an increased reference count.

        Args:
            mdlEntity: An MdlEntityId with a valid function name set (currently only from C++).

        Returns:
            A snapshot that represents a MDL material instance or function call present in the neuray database.
            Needs to be released using `destroyMdlEntity` when not required anymore.
        """
    def createMdlModule(self, usdIdentifier: str, dbScopeName: str = '') -> MdlModule: 
        """
        Loads an MDL module and stores the loaded definitions in the neuray DB scope provided.

        Args:
            usdIdentifier: The USD asset identifier of the module to load.

            scopeName (optional): Name of the DB scope to load the definitions to (default: '').

        Returns:
            The handle that contains the database name of the created module.
            Needs to be released using `destroyMdlModule` when not required anymore.
        """
    def createMdlModuleFromDbName(self, usdIdentifier: str, dbScopeName: str = '') -> MdlModule: 
        """
        Get a loaded module and increase its ref count.

        Args:
            scopeName (optional): Name of the DB scope to load the definitions to (default: '').

            moduleDbName: The DB name of the module.

        Returns:
            The handle that contains the database name of the created module.
            Needs to be released using `destroyMdlModule` when not required anymore.
        """
    def createReadingTransaction(self, dbScopeName: str = '') -> int: 
        """
        Creates a read-only transaction for a given database scope with short term usage in mind.

        This transaction can only be used for read access e.g. for generating shader
        code. Use the transaction on a per task level and from one thread only.
        This transaction can not be committed as it is not allowed to make changes to the database.
        However, keep in mind that the this new transaction can only see DB state that was already committed.
        The function returns a handle hat has to be attached to the MDL SDK API using `omni.mdl.pymdlsdk.attach_itransaction`.

        Args:
            dbScopeName (optional): Name of the DB scope to read from.

        Returns:
            The created transaction handle or `None` if the creation failed, e.g. because of an invalid scope.
        """
    def createScope(self, arg0: str) -> bool: 
        """
        Create a database scope with a given alphanumeric name if not yet existing.

        Scopes are hierarchical and this hierarchy is mapped to scope names by using dots.
        The global scope with the empty name is reserved. Parent scopes have to exist before creating child scopes.

        :type scopeName: str
        :param scopeName: Name of the DB scope to create.

        :return: True if the scope was created,
                 False if the scope existed before or the name referenced a none existing parent scope.
        """
    def destroyMdlEntity(self, arg0: MdlEntity) -> None: 
        """
        Releases a previously created entity.

        Args:
            mdlEntity: An MdlEntity that was created using`createMdlEntity`.
        """
    def destroyMdlEntitySnapshot(self, arg0: MdlEntitySnapshot) -> None: 
        """
        Releases a previously created entity snapshot.

        Args:
            mdlEntitySnapshot: An MdlEntitySnapshot that was created using`createMdlEntitySnapshot`.
        """
    def destroyMdlModule(self, arg0: MdlModule) -> None: 
        """
        Releases a previously loaded module.

        Args:
            mdlModule: A module that was created using`createMdlModule`.
        """
    def destroyScope(self, arg0: str) -> bool: 
        """
        Removes a database scope with a given alphanumeric name and all of its child scopes if existing.

        :type scopeName: str
        :param scopeName: Name of the DB scope to remove.

        :return: True if the scopes were removed, False if the scope does not existed.
        """
    def getCurrentDefaultScope(self) -> str: 
        """
        Returns the current default database scope name depending on the active renderer.

        If there is no active scene renderer with a corresponding, properly initialized scope,
        the 'default_scope' with default settings is returned.
        """
    def getNeurayAPI(self) -> int: 
        """
        Returns a handle to the neuray API.

        This handle has to be attached to the MDL SDK Python binding using `omni.mdl.pymdlsdk.attach_ineuray`.
        """
    def setScopeOption(self, arg0: str, arg1: str, arg2: str) -> bool: 
        """
        Configures the loading on a per scope base.

        :type scopeName: str
        :param scopeName: Name of the DB scope to set the option.

        :type option: str
        :param option: Name of the option to set.

        :type value: str
        :param value: The value of the option to set, "on" or "off" for booleans.

        :return: True in case of success, false if the scope does not exist or the provided option/value is invalid.
        """
    pass
def acquire_interface(plugin_name: str = None, library_path: str = None) -> NeurayLib:
    pass
def release_interface(arg0: NeurayLib) -> None:
    pass
