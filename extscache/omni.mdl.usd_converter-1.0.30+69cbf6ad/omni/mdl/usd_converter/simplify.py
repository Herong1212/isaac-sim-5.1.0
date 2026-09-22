from pxr import Usd, UsdGeom, Sdf, UsdShade
import re
import carb

props_to_ignore = ['ui:']

def filter_relevant_properties(properties: list):
    """
    Filter out some elements from the input list.
    """
    out = []
    if not properties is None:
        for p in properties:
            if all(not p.startswith(f) for f in props_to_ignore):
                    out.append(p)
    return out

def log_info(message: str):
    if not message is None:
        carb.log_info(message)

def log_error(message: str):
    if not message is None:
        carb.log_error(message)

def are_prim_properties_identical(stage, prim1, prim2, indent = 0, visited=None):
    """
    Compare properties of two USD prims to determine if they are identical.

    Args:
        stage (Usd.Stage): The USD stage.
        prim1 (Usd.Prim): The first prim to compare.
        prim2 (Usd.Prim): The second prim to compare.
        indent (int): Indentation for debugging.
        visited (set): A set to track visited (prim, property) pairs.

    Returns:
        bool: True if the properties are identical, False otherwise.
    """
    if stage is None:
        raise ValueError("Error: One or more required parameters are None.")

    if visited is None:
        visited = set()

    # Track visited prims to prevent infinite recursion
    visited_key1 = (prim1.GetPath(), prim2.GetPath())
    if visited_key1 in visited:
        # Skip further recursion for circular dependencies
        return True
    visited.add(visited_key1)

    if not prim1 or not prim2:
        return False

    if prim1 == prim2:
        # Simple case, we are comparing the same prims
        return True

    properties1 = filter_relevant_properties(prim1.GetPropertyNames())
    properties2 = filter_relevant_properties(prim2.GetPropertyNames())

    if properties1 != properties2:
        return False

    for prop_name in properties1:
        prop1 = prim1.GetProperty(prop_name)
        prop2 = prim2.GetProperty(prop_name)

        if not prop1 or not prop2:
            return False

        if prop1.GetTypeName() != prop2.GetTypeName():
            return False

        if prop1.Get() != prop2.Get():
            return False

        if prop1.Get() is None and prop2.Get() is None:
            # Retrieve connections
            if prop1 and prop1.HasAuthoredConnections() and prop2 and prop2.HasAuthoredConnections():
                connections1 = sorted(prop1.GetConnections())
                connections2 = sorted(prop2.GetConnections())

                if len(connections1) != len(connections2):
                    # Different number of connections, the nodes are not identical
                    return False

                # Handle multiple connections
                for c1, c2 in zip(connections1, connections2):
                    childprim1 = stage.GetPrimAtPath(c1.GetPrimPath())
                    childprim2 = stage.GetPrimAtPath(c2.GetPrimPath())
                    if not are_prim_properties_identical(stage, childprim1, childprim2, indent + 1, visited):
                        return False
    return True

def find_connections_to_prim(stage, target_prim_path):
    """
    Find all prims and attributes in the stage where the target prim is the
    target of a connection.

    Args:
        stage (Usd.Stage): The USD stage to analyze.
        target_prim_path (str): The path of the prim to check connections for.

    Returns:
        list: A list of tuples containing (source_prim_path, attribute_name).
    """
    if None in (stage, target_prim_path):
        raise ValueError("Error: One or more required parameters are None.")

    target_path = Sdf.Path(target_prim_path)
    connections = []

    # Iterate over all prims in the stage
    for prim in stage.Traverse():
        # Iterate over all attributes of the current prim
        for attr in prim.GetAttributes():
            if attr.IsValid() and attr.HasAuthoredConnections():
                # Get all connections for this attribute
                connected_paths = attr.GetConnections()
                for path in connected_paths:
                    # Check if the connection targets the specified prim
                    if path.GetPrimPath() == target_path:
                        connections.append((prim.GetPath(), attr.GetName()))

    return connections

def get_connected_attribute_names(stage, source_prim_path, attribute_name):
    """
    Retrieve the attribute names connected to a specific attribute.

    Args:
        stage (Usd.Stage): The USD stage to inspect.
        source_prim_path (str): The path of the prim with the attribute to inspect.
        attribute_name (str): The name of the attribute to check.

    Returns:
        list: A list of full connection paths (e.g., '/PrimName.outputs:out').
    """
    if None in (stage, source_prim_path, attribute_name):
        raise ValueError("Error: One or more required parameters are None.")

    # Get the source prim
    source_prim = stage.GetPrimAtPath(source_prim_path)
    if not source_prim:
        print(f"Source prim not found: {source_prim_path}")
        return []

    # Get the attribute
    attribute = source_prim.GetAttribute(attribute_name)
    if not attribute:
        print(f"Attribute '{attribute_name}' not found on prim: {source_prim_path}")
        return []

    # Retrieve connections
    if attribute.HasAuthoredConnections():
        connections = attribute.GetConnections()
        return [str(conn) for conn in connections]
    else:
        print(f"No connections found for attribute '{attribute_name}' on prim: {source_prim_path}")
        return []

def change_connection(stage, source_prim_path, attribute_name, new_target_prim_path, target_output_name):
    """
    Change a connection on a source attribute to point to a new target prim.

    Args:
        stage (Usd.Stage): The USD stage to modify.
        source_prim_path (str): The path of the prim with the attribute to modify.
        attribute_name (str): The name of the attribute to update.
        new_target_prim_path (str): The path of the new target prim.
    """
    # Ensure no parameter is None
    if None in (stage, source_prim_path, attribute_name, new_target_prim_path, target_output_name):
        raise ValueError("Error: One or more required parameters are None.")

    # Get the source prim
    source_prim = stage.GetPrimAtPath(source_prim_path)
    if not source_prim:
        log_error(f"Source prim not found: {source_prim_path}")
        return

    # Get the attribute
    attribute = source_prim.GetAttribute(attribute_name)
    if not attribute:
        log_error(f"Attribute '{attribute_name}' not found on prim: {source_prim_path}")
        return

    # Construct the full target path, including the attribute
    full_target_path = Sdf.Path(f"{new_target_prim_path}.{target_output_name}")

    # Set the new connection
    new_target_path = Sdf.Path(full_target_path)
    attribute.SetConnections([new_target_path])
    log_info(f"Updated connection for {attribute_name} on {source_prim_path} to target {str(new_target_path)}")

def merge_identical_subgraphs(stage, start_prim_path : str = '/', dry_run : bool = False):
    """
    Simplify the USD stage by removing identical nodes.

    Args:
        stage (Usd.Stage): The USD stage to modify.
        start_prim_path (str): The path of the prim under which to start to simplify.
        dry_run (bool): Do not modify the stage, only output log.
    """
    if stage is None:
        raise ValueError("Error: One or more required parameters are None.")

    visited_prims = []
    to_remove = []
    replace_with = []

    start_prim : Usd.Prim = stage.GetPrimAtPath(start_prim_path)
    if not start_prim.IsValid():
        log_error(f"Error: Invalid prim {start_prim_path}")
        return

    for prim in Usd.PrimRange(start_prim):
        if not prim.IsActive():
            continue

        if not UsdShade.Material(prim) and not UsdShade.Shader(prim) and not UsdShade.NodeGraph(prim):
            # Only consider materials, shaders and nodegraphs
            continue

        for other in visited_prims:
            if are_prim_properties_identical(stage, prim, other):
                assert prim != other, "Warning: Comparing the same Prim"
                log_info(f"{prim.GetPath()} is identical to {other.GetPath()}")
                to_remove.append(prim.GetPath())
                replace_with.append(other.GetPath())
                break
        else:
            visited_prims.append(prim)

    # Find out where the removed prims are referenced and what attribute connect are connected
    for index, target_prim_path in enumerate(to_remove):
        connections = find_connections_to_prim(stage, target_prim_path)
        if connections:
            for source_prim_path, attribute_name in connections:
                new_target_prim_path = replace_with[index]
                conn = get_connected_attribute_names(stage, source_prim_path, attribute_name)
                target_output_name = "outputs:out"  # Specify the attribute to connect to
                # TODO: Handle multiple connections
                # TODO: output_names_regex = [re.search(r'\.(outputs:[\w:]+)$', conn).group(1) for conn in connections]
                # assert len(conn) == 1, "merge_identical_subgraphs() does not Handle multiple connections"
                if len(conn) == 1:
                    # TODO Use the Sdf.Path API for robust path parsing instead of regex. HOW?
                    match = re.search(r'\.(outputs:[\w:]+)$', conn[0])
                    if match:
                        target_output_name = match.group(1)

                if not dry_run:
                    change_connection(stage, source_prim_path, attribute_name, new_target_prim_path, target_output_name)
        else:
            pass

    # Remove identical nodes
    for path in to_remove:
        if not dry_run:
            stage.RemovePrim(path)
        log_info(f"Removed duplicate node: {path}")

    if not to_remove:
        log_info(f"Nothing to simplify in stage")
