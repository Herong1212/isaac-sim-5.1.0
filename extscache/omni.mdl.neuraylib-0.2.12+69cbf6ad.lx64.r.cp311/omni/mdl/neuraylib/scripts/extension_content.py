import os
import pathlib
import subprocess
import carb
import carb.tokens
from warnings import warn
import omni.kit.app

LOG_PREFIX: str = "[ExtensionContent]"

def _get_target_search_path(extensionName: str, extensionPackages: bool = False) -> str:
    """
    Get the search path to link content into.
    """
    tokens = carb.tokens.get_tokens_interface()
    targetSearchPath: str = ""

    # for the (depreated) extension packages, link a folder into an existing search path
    if extensionPackages:
        kitRelatativePath: str = "mdl/core/mdl"
        targetSearchPath = tokens.resolve("${kit}/" + kitRelatativePath)
        if not targetSearchPath:  # pragma: no cover
            targetSearchPath = tokens.resolve("${exe-path}/" + kitRelatativePath)

    # for registering content directly in the root a search path
    # we use an own search path for extensions
    else:
        targetSearchPath = tokens.resolve("${omni.mdl}/search_paths/omniverse_exts")

    if not targetSearchPath:  # pragma: no cover
        carb.log_error(f"{LOG_PREFIX}[{extensionName}] Default MDL search path in Kit not found.")
        return ""  # target search path to hook into can not be found
    return targetSearchPath


def _get_use_symlinks() -> bool:
    """
    On unix systems we always use symlinks so this function will return True.
    It also returns true if symlinks are prefered over junctions and hard links on windows,
    based on the setting: '--/exts/omni.mdl.neuraylib/extSearchPath/forceSymlinks'.
    Note, creating the symlink works only if the user has the appropriate rights on windows, so we prefer junctions / hard links
    # - Windows: Admin rights
    # - Windows: Developer Mode is one
    # - Windows: Users with SeCreateSymbolicLinkPrivilege
    """
    return os.name != 'nt' or bool(carb.settings.get_settings().get('exts/omni.mdl.neuraylib/extSearchPath/forceSymlinks'))


def _create_link(targetPath: str, linkPath: str, extensionName: str, useSymlinks: bool, force: bool = False) -> str:
    """
    Creates a link at location 'linkPath' that points to an existing file at 'targetPath'.

    Args:
        targetPath: The existing file the link should point to.
        linkPath: The path of the link to create.
        useSymlinks: If true, symlinks are used instead of junctions / hard links.
        force: If the 'linkPath' already exists, it's considered an error. 'force' will try to remove the existing link first.
    Returns:
        The absolute path of the registered path, or empty in case of failure.
    """

    mkLinkFlag: str = "/h"  # hard link for folders
    operationName: str = "hard link"
    targetIsDirectory: bool = os.path.isdir(targetPath)
    if (targetIsDirectory):
        mkLinkFlag = "/j"  # junction for folders
        operationName = "junction"
    if useSymlinks:
        operationName: str = "symlink"
        # no mklink used

    # check of the file exists
    if os.path.exists(linkPath):
        error: bool = True
        if force:
            error = not _delete_link(linkPath, extensionName)  # if the existing file has been deleted, it's not an error case anymore
        if error:
            carb.log_error(f"{LOG_PREFIX}[{extensionName}] Creating a {operationName} failed. The link location is already in use.\nTarget: {targetPath}\nLink: {linkPath}")
            return ""

    # make sure the parent folder exists
    linkParentFolder: str = os.path.dirname(linkPath)
    pathlib.Path(linkParentFolder).mkdir(parents=True, exist_ok=True)

    if useSymlinks:
        # try creating the link
        try:
            os.symlink(targetPath, linkPath, target_is_directory=targetIsDirectory)
            carb.log_verbose(f"{LOG_PREFIX}[{extensionName}] Created {operationName}.\nTarget: {targetPath}\nLink: {linkPath}")
            return linkPath
        except Exception as e:
            carb.log_error(f"{LOG_PREFIX}[{extensionName}] Creating a {operationName} failed. Make sure you have the rights or enable Developer mode in Windows.\nTarget: {targetPath}\nLink: {linkPath}\nDetails: {e}")
    else:
        # use hard links
        try:
            subprocess.check_call(f'mklink {mkLinkFlag} "{os.fsdecode(linkPath)}" "{os.fsdecode(targetPath)}"', shell=True)
            carb.log_verbose(f"{LOG_PREFIX}[{extensionName}] Created {operationName}.\nTarget: {targetPath}\nLink: {linkPath}")
            return linkPath
        except Exception as e:
            carb.log_error(f"{LOG_PREFIX}[{extensionName}] Creating a {operationName} failed.\nTarget: {targetPath}\nLink: {linkPath}\nDetails: {e}")
    # failure
    return ""


def _delete_link(linkPath: str, extensionName: str) -> bool:
    """
    Removes a link (file or folder) and returs true if the removal was successful.
    """
    # remove old symlink
    if os.path.islink(linkPath):
        os.unlink(linkPath)
        carb.log_verbose(f"{LOG_PREFIX}[{extensionName}] Removed symlink: {linkPath}")
        return True
    # remove junctions created by mklink
    elif os.path.isdir(linkPath):
        os.rmdir(linkPath)
        carb.log_verbose(f"{LOG_PREFIX}[{extensionName}] Removed junction: {linkPath}")
        return True
    # remove files or hard links
    elif os.path.isfile(linkPath):
        os.remove(linkPath)
        carb.log_verbose(f"{LOG_PREFIX}[{extensionName}] Removed hard link: {linkPath}")
        return True

    return not os.path.exists(linkPath)


def _list_content(rootPath: str, subfolder: str = None) -> list[str]:
    """
    Recursively lists the content of a given folder and returns a list of paths relative to the 'rootPath'.
    """
    result: list[str] = []
    currentFolderPath: str = rootPath
    if subfolder:
        currentFolderPath = currentFolderPath + "/" + subfolder
    for entry in os.listdir(currentFolderPath):
        currentEntryPath: str = subfolder + "/" + entry if subfolder else entry
        if os.path.isdir(currentFolderPath  + "/" + entry):
            result = result + _list_content(rootPath, currentEntryPath)
        else:
            result.append(currentEntryPath)
    return result


def register_extension_content(extensionName: str, contentPath: str) -> list[str]:
    """
    Register a folder of your extension data in the root of the MDL extension search path.

    Since content is registered in a search path root you need to be cautious to not conflict with other content.
    The MDL module space is similar to package names in Python and Java.
    Module paths have to be unique. If not, the module from the higher priority search path will be used.

    The MDL search path system adds some save guards for extension content.
    For instance you can't override `nvidia/core_definitions.mdl` or other modules that required by the renderer
    because they life in a higher priority search path. The conflicting extension content will not be accessible.

    This kind of save does not prevent collisions between content of different extensions.
    Therefore you are urged to follow some basic guideline when authoring your MDL content:

    Put your content into packages! A common pattern is to put the company in front, followed by a project or product name.
    The content of the `contentPath` folder could look like this:

    >>> nvidia/ProjectABC/main.mdl
    >>> nvidia/ProjectABC/sub1/A.mdl

    Then, the paths above, can be used as USD source asset paths for USD Shader nodes in the 'mdl' context.
    When addressing these Modules from other MDL content, you can import them like this:

    >>> import ::nvidia::ProjectABC::main::*;
    >>> import ::nvidia::ProjectABC::sub1::A::*;

    For more information please refer the MDL specification or reach out to the MDL team.

    Args:
        extensionName:  The name of your extension, e.g., ``omni.foo.bar``.
                        This allows to improve the messaging about conflict cases.

        contentPath:    The absolute path of the content you want to register.
                        If the path points to a folder, the entire content of the folder is registered
                        while the folder itself is not represented as package.

    Returns:
        A list of the absolute path links created or an empty list in case of failure.
        Keep this list to unregister content on shutdown of your extension.
    """
    targetSearchPath: str = _get_target_search_path(extensionName)
    if not targetSearchPath:
        return []  # pragma: no cover

    # do NOT resolve symlinks in the input path
    # symlinks are a explicitly defined new view on the file system
    # not resolving might have the consequence that there are more than one absolute paths to an MDL module,
    # but in that case the MDL SDK / neuray has to consider them as two different modules.
    # contentPath = str(pathlib.Path(contentPath).resolve())

    # content path needs to be a folder
    if not isinstance(contentPath, str):
        carb.log_error(f"{LOG_PREFIX}[{extensionName}] Provided content path '{contentPath}' is not a 'str'. Did you pass a 'pathlib.Path'?")
        return []
    if not os.path.isdir(contentPath):
        carb.log_error(f"{LOG_PREFIX}[{extensionName}] Provided content path '{contentPath}' does not exist.")
        return []
    if not os.path.isabs(contentPath):
        carb.log_error(f"{LOG_PREFIX}[{extensionName}] Provided content path '{contentPath}' has to be an absolute path.")
        return []

    # list all files to be linked
    # folders are created in the search path
    contentFiles: list[str] = _list_content(contentPath)
    createLinks: list[str] = []
    success: bool = True
    useSymlinks: bool =  _get_use_symlinks()
    for entry in contentFiles:
        linkPath: str = targetSearchPath + "/" + entry
        linkPath =_create_link(contentPath + "/" + entry, linkPath, extensionName, useSymlinks, force=True)  # we cannot rely on shutdown happening
        if linkPath:
            createLinks.append(linkPath)
        else:
            success = False
            break

    # cleanup in case of failure
    if not success:
        carb.log_error(f"{LOG_PREFIX}[{extensionName}] Content registration failed. Cleaning up already created links.")
        for l in createLinks:
            if not _delete_link(l, extensionName):
                carb.log_error(f"{LOG_PREFIX}[{extensionName}] Failed to cleanup link: {l}")
        return []

    # report the created links
    log: str = f"{LOG_PREFIX}[{extensionName}] Linked extension content:"
    for l in createLinks:
        log = log + f"\n-  {l}"
    carb.log_verbose(log)
    return createLinks

def deregister_extension_content(extensionName: str, registeredFiles: list[str]) -> bool:
    R"""
    Removes your extension data from the extension search path.

    Resolving modules in the extensions data folder will fail.
    However, if MDL modules are currently loaded they will be available till the next start of kit.

    Args:
        extensionName:      The name of your extension, e.g., ``omni.foo.bar``.

        registeredFiles:    The list returned by 'register_extension_content'

    Returns:
        True if removing was successful.
    """

    # cleanup in case of failure
    success: bool = True
    folderSet: set[str] = set({})
    targetSearchPath: str = _get_target_search_path(extensionName)
    for l in registeredFiles:
        if not l.startswith(targetSearchPath):
            continue  # limit to the extension content
        if not _delete_link(l, extensionName):
            carb.log_error(f"{LOG_PREFIX}[{extensionName}] Failed to remove link: {l}")
            success = False
        folder: str = os.path.dirname(l)
        # make sure to only list subfolders for deleting when empty, not the search path root itself
        while folder.startswith(targetSearchPath) and len(folder) > len(targetSearchPath):
            folderSet.add(folder)
            folder = os.path.dirname(folder)

    # remove empty folders
    folderList: list[str] = list(folderSet)
    folderList.sort(key=lambda s: len(s), reverse=True)
    for f in folderList:
        with os.scandir(f) as it:
            if not any(it):
                os.rmdir(f)
                carb.log_verbose(f"{LOG_PREFIX}[{extensionName}] Removed empty package: {f}")
            else:
                carb.log_verbose(f"{LOG_PREFIX}[{extensionName}] Kept non-empty package: {f}")

    return success

@omni.kit.app.deprecated("use register_extension_content instead")
def RegisterExtensionContent(extensionName: str, contentPath: str) -> list[str]:
    return register_extension_content(extensionName, contentPath)

@omni.kit.app.deprecated("use deregister_extension_content instead")
def UnregisterExtensionContent(extensionName: str, registeredFiles: list[str]) -> bool:
    return deregister_extension_content(extensionName, registeredFiles)
