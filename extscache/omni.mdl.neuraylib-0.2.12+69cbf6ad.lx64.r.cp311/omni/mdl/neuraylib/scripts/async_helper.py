import asyncio
from .entrypoints import get_neuraylib

async def create_mdl_module_async(usdIdentifier: str, dbScopeName: str = ""):
    R"""
    Loads an MDL module and stores the loaded definitions in the neuray DB scope provided.

    Args:
        usdIdentifier: The USD asset identifier of the module to load.

        scopeName (optional): Name of the DB scope to load the definitions to (default: '').

    Returns:
        The handle that contains the database name of the created module.
        Needs to be released using `destroyMdlModule` when not required anymore.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_neuraylib().createMdlModule, usdIdentifier, dbScopeName)
