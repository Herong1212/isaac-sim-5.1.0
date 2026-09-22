from .._neuraylib import NeurayLib
from ..scripts.entrypoints import get_neuraylib

def parse_resource_identifier_texture(sceneIdentifier: str) -> tuple[str|None,str|None,float|None]:
    # handle default resources
    if sceneIdentifier.startswith("MI_default_texture"):
        ov_neuraylib: NeurayLib = get_neuraylib()
        sceneIdentifier = ov_neuraylib._unmangleUri(sceneIdentifier, '/')
        sceneIdentifier = sceneIdentifier[sceneIdentifier.find('/')+1:-1]
        underscore = sceneIdentifier.rfind('_')
        g = sceneIdentifier[underscore + 1:]
        sceneIdentifier = sceneIdentifier[:underscore]
        if g == "1":
            colorspace = "raw"
        elif g == "0":
            colorspace = "auto"
        else:
            colorspace = "sRGB"

    # drop the db prefix
    elif sceneIdentifier.startswith("mdl::"):
        sceneIdentifier = sceneIdentifier[5:]
        underscore = sceneIdentifier.rfind('_')
        if underscore == -1:
            return (None, None, None)
        # read the colorspace
        colorspace = sceneIdentifier[underscore + 1:]
        sceneIdentifier = sceneIdentifier[:underscore]
        underscore = sceneIdentifier.rfind('_')
        if underscore == -1:
            return (None, None, None)
        # read the resource marker
        resourceType = sceneIdentifier[underscore + 1:]
        if resourceType != "texture":
            return (None, None, None)
        # get and (check?) the uri
        sceneIdentifier = sceneIdentifier[:underscore]

    else:
        return (None, None, None)

    gamma: float = 0.0
    if colorspace == "raw":
        gamma = 1.0
    elif colorspace == "sRGB":
        gamma = 2.2
    elif colorspace == "auto":
        gamma = 0.0
    else:
        return (None, None, None)

    return (sceneIdentifier, colorspace, gamma)

def parse_resource_identifier_mbsdf(sceneIdentifier: str) -> str|None:
    # drop the db prefix
    if not sceneIdentifier.startswith("mdl::"):
        return None
    sceneIdentifier = sceneIdentifier[5:]
    underscore = sceneIdentifier.rfind('_')
    if underscore == -1:
        return None
    # read the resource marker
    resourceType = sceneIdentifier[underscore + 1:]
    if resourceType != "mbsdf":
        return None
    # get and (check?) the uri
    sceneIdentifier = sceneIdentifier[:underscore]
    return sceneIdentifier

def parse_resource_identifier_lp(sceneIdentifier: str) -> str|None:
    # drop the db prefix
    if not sceneIdentifier.startswith("mdl::"):
        return None
    sceneIdentifier = sceneIdentifier[5:]
    underscore = sceneIdentifier.rfind('_')
    if underscore == -1:
        return None
    # read the resource marker
    resourceType = sceneIdentifier[underscore + 1:]
    if resourceType != "lp":
        return None
    # get and (check?) the uri
    sceneIdentifier = sceneIdentifier[:underscore]
    return sceneIdentifier