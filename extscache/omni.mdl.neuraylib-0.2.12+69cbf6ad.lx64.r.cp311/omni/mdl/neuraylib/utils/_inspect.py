import omni.mdl.pymdlsdk as pymdlsdk
from .._neuraylib import NeurayLib
from ..scripts.entrypoints import get_neuraylib
from ._scene_identifier import parse_resource_identifier_texture, parse_resource_identifier_lp, parse_resource_identifier_mbsdf
import omni.client

def get_graph_nodes(trans: pymdlsdk.ITransaction, root_db_name: str) -> list[str]:
    r"""lists all the nodes DB names attached to a given root, including itself"""

    result: list[str] = [ root_db_name ]
    call: pymdlsdk.IFunction_call = trans.access_as(pymdlsdk.IFunction_call, root_db_name)
    args: pymdlsdk.IExpression_list = call.get_arguments()
    for i in range(args.get_size()):
        child_call: pymdlsdk.IExpression_call = args.get_expression_as(pymdlsdk.IExpression_call, i)
        if child_call.is_valid_interface():
            child_call_db_name: str = child_call.get_call()
            if child_call_db_name == "":
                continue
            result = result + get_graph_nodes(trans, child_call_db_name)
    return result

def get_graph_modules(trans: pymdlsdk.ITransaction, node_db_names: list[str], skip_standard_and_builtins: bool) -> list[str]:
    r"""Lists all the MDL modules DB names that a given set of graph nodes depends on."""

    def is_standard_or_builtin(m: pymdlsdk.IModule) -> bool:
        return m.is_standard_module() or m.get_mdl_name() == '::%3Cbuiltins%3E' or m.get_mdl_name() == '::base'

    result: list[str] = []
    toProcess: list[str] = []
    for node_db_name in node_db_names:
        call: pymdlsdk.IFunction_call = trans.access_as(pymdlsdk.IFunction_call, node_db_name)
        call_def: pymdlsdk.IFunction_definition = trans.access_as(pymdlsdk.IFunction_definition, call.get_function_definition())
        toProcess.append(call_def.get_module())
        while len(toProcess) > 0:
            m_db_name: str = toProcess.pop(0)
            m: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, m_db_name)
            if (m_db_name not in result) and not (skip_standard_and_builtins and is_standard_or_builtin(m)):
                result.append(m_db_name)

                for i in range(m.get_import_count()):
                    import_db_name: str = m.get_import(i)
                    import_m: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, import_db_name)
                    if (import_db_name not in toProcess) and not (skip_standard_and_builtins and is_standard_or_builtin(import_m)):
                        toProcess.append(import_db_name)
    return result


def get_resource_uri_mask(trans: pymdlsdk.ITransaction, resource: pymdlsdk.IValue_resource) -> str:
    r"""
    Resolves a resource URI or the mask in case of tiled or animated resources.

    Returns the empty string in case the resource can not be resolved.
    """
    ov_neuraylib: NeurayLib = get_neuraylib()
    neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ov_neuraylib.getNeurayAPI())
    cfg: pymdlsdk.IMdl_configuration = neuray.get_api_component(pymdlsdk.IMdl_configuration)
    er: pymdlsdk.IMdl_entity_resolver = cfg.get_entity_resolver()
    factory: pymdlsdk.IMdl_factory = neuray.get_api_component(pymdlsdk.IMdl_factory)
    context: pymdlsdk.IMdl_execution_context = factory.create_execution_context()
    context.set_option("resolve_resources", False)  # to get MDL file path and the resolved file name

    mdl_file_path: str = resource.get_file_path()
    value: str = resource.get_value()
    if mdl_file_path:
        resolved_uri: str =  ov_neuraylib._unmangleUri(mdl_file_path, '/')
        resolved_uri = resolved_uri.replace("<", "%3C")  # encode special characters
        resolved_uri = resolved_uri.replace(">", "%3E")
        resolved_uri_cl = omni.client.break_url(resolved_uri)
        if resolved_uri_cl.scheme == None or resolved_uri_cl.scheme == "":
            # if the parsed identifier isn't a uri, it should be an MDL name (unresolved)
            owner_db_name: str = resource.get_owner_module()
            owner_file_path: str = ""
            owner_mdl_name: str = ""
            if owner_db_name:
                mdl_module: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, owner_db_name)
                owner_file_path = mdl_module.get_filename()
                owner_mdl_name = mdl_module.get_mdl_name()
                mdl_module = None
            res: pymdlsdk.IMdl_resolved_resource = er.resolve_resource(mdl_file_path, owner_file_path, owner_mdl_name, 0, 0, context)
            if res.is_valid_interface():
                return res.get_filename_mask()
            return ""
        else:
            # ER in OV works with absolute URIs, too
            res: pymdlsdk.IMdl_resolved_resource = er.resolve_resource(resolved_uri, "", "", 0, 0, context)
            if res.is_valid_interface():
                return res.get_filename_mask()
            return ""
    elif value:
        # resources specified in USD/hydra.
        encodedUri: str = ""
        tex: pymdlsdk.IValue_texture = resource.get_interface(pymdlsdk.IValue_texture)
        lp: pymdlsdk.IValue_light_profile = resource.get_interface(pymdlsdk.IValue_light_profile)
        mbsdf: pymdlsdk.IValue_bsdf_measurement = resource.get_interface(pymdlsdk.IValue_bsdf_measurement)
        if tex.is_valid_interface():
            encodedUri = parse_resource_identifier_texture(value)[0]
        elif lp.is_valid_interface():
            encodedUri = parse_resource_identifier_lp(value)
        elif mbsdf.is_valid_interface():
            encodedUri = parse_resource_identifier_mbsdf(value)

        res: pymdlsdk.IMdl_resolved_resource = er.resolve_resource(encodedUri, "", "", 0, 0, context)
        if res.is_valid_interface():
            return res.get_filename_mask()
        return ""

    return ""

def get_module_resource(trans: pymdlsdk.ITransaction, module_db_name: str) -> list[pymdlsdk.IValue_resource]:
    r"""Collect all resources references by an MDL module."""
    result: list[pymdlsdk.IValue_resource] = []
    mdl_module: pymdlsdk.IModule = trans.access_as(pymdlsdk.IModule, module_db_name)
    for i in range(mdl_module.get_resources_count()):
        resource: pymdlsdk.IValue_resource = mdl_module.get_resource(i)
        if resource.is_valid_interface() and (resource.get_file_path() or resource.get_value()):
            result.append(resource)
    mdl_module = None
    return result

def get_graph_node_resources(trans: pymdlsdk.ITransaction, node_db_name: str):
    r"""Collect all resources directly referenced by an MDL function call."""
    result: list[pymdlsdk.IValue_resource] = []
    call: pymdlsdk.IFunction_call = trans.access_as(pymdlsdk.IFunction_call, node_db_name)
    args: pymdlsdk.IExpression_list =  call.get_arguments()
    for i in range(args.get_size()):
        a: pymdlsdk.IExpression_constant = args.get_expression_as(pymdlsdk.IExpression_constant, i)
        if a.is_valid_interface():
            resource: pymdlsdk.IValue_resource = a.get_value_as(pymdlsdk.IValue_resource)
            if resource.is_valid_interface() and (resource.get_file_path() or resource.get_value()):
                result.append(resource)
    call = None
    return result

def get_graph_resources(trans: pymdlsdk.ITransaction, root_db_name: str):
    r"""Collect all resources required by a given material graph."""
    # get all nodes of our material graph
    node_db_names: list[str] = get_graph_nodes(trans, root_db_name)
    # get all modules our material graph depends on
    modules: list[str] = get_graph_modules(trans, node_db_names, True)

    # gather the module resources (includes body and default resources)
    resources: list[pymdlsdk.IValue_resource] = []
    for m in modules:
        resources = resources + get_module_resource(trans, m)

    # gather the parameter resources
    for n in node_db_names:
        resources = resources + get_graph_node_resources(trans, n)

    return resources
