__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


from collections import defaultdict

from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade

from .test_utils import Test_Operation, _get_test_data_file_path

# Duplicate Method values
DUPLICATE_METHOD_COPYVALUES = 0  # Copy the points and normals values
DUPLICATE_METHOD_REFERENCE = 1  # Reference composition arc
DUPLICATE_METHOD_INSTANCEABLEREFERENCE = 2  # Reference composition arc with instanceable true
DUPLICATE_METHOD_SET_ATTRIBUTE = 3  # Set duplication set attribute


# Default arguments for the command
DEFAULT_ARGS = {
    "meshPrimPaths": [],
    "considerDeepTransforms": True,
    "tolerance": 0.05,
    "duplicateMethod": DUPLICATE_METHOD_INSTANCEABLEREFERENCE,
    "fuzzy": False,
    "useGpu": False,
    "allowScaling": False,
}


def _get_meshes(stage):
    return [x for x in stage.TraverseAll() if x.IsA(UsdGeom.Mesh)]


def _compute_hash_value_vec3f_array(value):
    """Generate a hash for a vec3f array based on values"""
    if value is None:
        return None
    # Hash each value individually, then array of hashes.
    values_hashes = tuple([hash(x) for x in value])
    result = hash(values_hashes)
    return result


def _get_unique_mesh_paths(stage):
    """Returns a list of lists of containing prim paths for meshes that RTX would consider duplicates"""
    # This is intended to mirror the de-dupe logic of RTX so that we can assert the desired result.
    result = defaultdict(list)

    # Iterate prims using stage traversal so that only the mesh prims visible to the renderer are encountered.
    for prim in stage.Traverse():

        # Skip prims that are not meshes
        mesh = UsdGeom.Mesh(prim)
        if not mesh:
            continue

        points = mesh.GetPointsAttr().Get()
        extent = mesh.GetExtentAttr().Get()

        # Use the attr normals unless primvar normals are authored, in which case use the flattened values
        normals = mesh.GetNormalsAttr().Get()
        primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
        if primvar:
            normals = primvar.ComputeFlattened()

        # Get points and normals hashes then add the prim path to the result for that key.
        p_hash = _compute_hash_value_vec3f_array(points)
        n_hash = _compute_hash_value_vec3f_array(normals)
        e_hash = _compute_hash_value_vec3f_array(extent)
        key = (p_hash, n_hash, e_hash)

        result[key].append(prim.GetPath())

    return [x for x in result.values()]


def _get_mesh_paths(stage):
    """Returns a pair of mesh paths and instance proxy mesh paths"""
    # Declare return variables.
    mesh_paths = list()
    instance_proxy_mesh_paths = list()

    # Iterate the stage and populate lists with mesh paths.
    for prim in Usd.PrimRange.Stage(stage, Usd.TraverseInstanceProxies()):
        if UsdGeom.Mesh(prim):

            # Put the path in the appropriate list.
            if prim.IsInstanceProxy():
                instance_proxy_mesh_paths.append(prim.GetPath())
            else:
                mesh_paths.append(prim.GetPath())

    # Return result.
    return (mesh_paths, instance_proxy_mesh_paths)


def _get_all_mesh_paths(stage):
    """Returns a list of paths of all prims representing meshes"""
    # Declare return variables.
    result = list()
    for x in _get_mesh_paths(stage):
        for path in x:
            result.append(path)
    return result


def _get_worldspace_points(prim, xformCache):
    """Returns points in worldspace"""
    result = []
    # Traverse from the given prim down collecting all the Mesh prims
    for x in Usd.PrimRange(prim, Usd.TraverseInstanceProxies()):
        # Get the points and local to world transform matrix.
        mesh = UsdGeom.Mesh(x)
        if mesh:
            points = mesh.GetPointsAttr().Get()
            matrix = xformCache.GetLocalToWorldTransform(x)
            # Add points with the matrix applied to the result
            for point in points:
                result.append(matrix.Transform(point))
    return result


def _get_subsets_and_bound_materials(prim):
    """Yields pairs of UsdGeom.Subset and the UsdShade.Material bound to it"""
    # Yield nothing if the prim is not Imageable
    imageable = UsdGeom.Imageable(prim)
    if imageable:

        # Iterate over all subsets incase the family name is not set correctly.
        for subset in UsdGeom.Subset.GetAllGeomSubsets(imageable):

            # Only yield if there is a bound material.
            material, _ = UsdShade.MaterialBindingAPI(subset.GetPrim()).ComputeBoundMaterial()
            if material:
                yield (subset, material)


def _get_per_face_bound_materials(prim):
    """Returns a map of material paths and the faces they are bound to"""
    result = defaultdict(list)
    subsets = []

    # Iterate over all the material bound subsets collecting the face indices the material is bound to.
    for subset, material in _get_subsets_and_bound_materials(prim):

        # Add the faces bound to the material to the result.
        faces_indices = subset.GetIndicesAttr().Get()
        result[material.GetPath()].extend(faces_indices)

        # Add the subset to the list of subsets so we can calculate unassigned faces.
        subsets.append(subset)

    # Add any materials bound directly to the prim.
    material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
    if material:

        # Build an accurate face indices list so that we are asserting the effective shaded faces.
        face_count = len(UsdGeom.Mesh(prim).GetFaceVertexCountsAttr().Get())
        if subsets:  # pragma: no cover
            faces_indices = UsdGeom.Subset.GetUnassignedIndices(subsets, face_count)
        else:
            faces_indices = range(face_count)

        # Add the faces bound to the material to the result.
        result[material.GetPath()].extend(faces_indices)

    return result


class Test_Operation_Deduplicate_Geometry(Test_Operation):

    OPERATION = "deduplicateGeometry"

    def assertVec3ArrayAlmostEqual(self, expected, returned, tolerance, msg):
        """Assert that the individual values that make up two Vec3 Arrays are almost equal"""
        # Track equality.
        are_equal = True

        # Compare each value with a length difference tolerance.
        for expected_point, returned_point in zip(expected, returned):
            # Compute the length of the distance vector between the two points.
            box = Gf.Range3f(expected_point, returned_point)
            delta = box.GetSize().GetLength()
            # Early out if two points are further apart than the tolerance allows for.
            if delta > tolerance:  # pragma: no cover
                are_equal = False
                break

        # Assert the resulting equality.
        self.assertTrue(are_equal, msg)

    def assertWorldspacePointsEqual(self, prim_before, prim_after, xformCache, tolerance=None):
        """Assert that world space points values of two prims match"""
        # Get the before and after point in worldspace.
        expected = _get_worldspace_points(prim_before, xformCache)
        returned = _get_worldspace_points(prim_after, xformCache)

        # Assert that the values match exactly or with a tolerance.
        msg = 'World space points differ for "{}" and "{}"'.format(prim_before.GetPath(), prim_after.GetPath())
        if tolerance is None:
            self.assertEqual(expected, returned, msg)
        else:
            self.assertVec3ArrayAlmostEqual(expected, returned, tolerance, msg)

    def assertWorldspaceScenePointsEqual(self, stage_before, stage_after, tolerance=None):
        """Assert that world space points values of all mesh prims in stage_before and stage_after match"""
        paths_before = _get_all_mesh_paths(stage_before)
        paths_after = _get_all_mesh_paths(stage_after)
        self.assertEqual(paths_before, paths_after)

        xformCache = UsdGeom.XformCache()

        for path_before, path_after in zip(paths_before, paths_after):
            prim_before = stage_before.GetPrimAtPath(path_before)
            prim_after = stage_after.GetPrimAtPath(path_after)
            self.assertWorldspacePointsEqual(prim_before, prim_after, xformCache, tolerance)

    def assertBoundMaterialsEqual(self, prim_before, prim_after):
        """Assert that the paths of materials bound to two prims match"""
        # Get bound materials and the faces they are bound to so that we can compare UsdGeomSubset material bindings.
        materials_before = _get_per_face_bound_materials(prim_before)
        materials_after = _get_per_face_bound_materials(prim_after)

        # Assert that the material paths before and after match.
        expected = set(materials_before.keys())
        returned = set(materials_after.keys())
        self.assertEqual(returned, expected)

        # Assert that the face indices for each material path match.
        material_paths = materials_before.keys()
        for material_path in material_paths:

            # Get the sorted face indices for the material before and after
            expected = sorted(materials_before[material_path])
            returned = sorted(materials_after[material_path])

            # Assert that they are equal.
            self.assertEqual(returned, expected)

    async def test_copy_values_improves_rtx_deduplicate(self):
        """Check that after the operation has run there are less unique meshes than there were before hand"""
        # Get a copy of the default arguments for this command
        args = DEFAULT_ARGS.copy()

        # Open the stage and get the initial list of unique meshs.
        stage = self._open_stage("deduplicateGeometryExample.usd")
        unique_meshes_before = _get_unique_mesh_paths(stage)

        # RTX finds 8 unique meshes in this scene so assert that we find the same.
        self.assertEqual(len(unique_meshes_before), 8)

        # Enable deep transform checks, set method to copy values, then execute command.
        # This should produce a result that has less unique meshes from the point of view on RTX.
        args["considerDeepTransforms"] = True
        args["tolerance"] = 0.05
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES
        self._execute_command(args)

        # Assert that there are less unique meshes after execution.
        unique_meshes_after = _get_unique_mesh_paths(stage)
        self.assertTrue(len(unique_meshes_before) > len(unique_meshes_after))

        # The logic currently results in 4 unique meshes.
        self.assertEqual(len(unique_meshes_after), 4)

        # The input meshes have names that describe the changes that were made to them during creation.
        # Reduce the paths down to names so that we can assert the cases we currently cover.
        unique_cases = list()
        for paths in unique_meshes_after:
            names = sorted(list(set([path.name for path in paths])))
            unique_cases.append(names)
        unique_cases.sort()

        # Expected outcome.
        cases_0 = [
            "BaseMesh0",
            "BaseMesh1",
            "RotatedMesh0",
            "RotatedMesh1",
            "ScaledMesh0",
            "ScaledMesh1",
            "TranslatedMesh0",
            "TranslatedMesh1",
            "WithinToleranceMesh0",
            "WithinToleranceMesh1",
        ]
        cases_1 = [
            "DifferentMesh0",
            "DifferentMesh1",
        ]
        cases_2 = [
            "DifferentNormalsMesh0",
            "DifferentNormalsMesh1",
        ]
        cases_3 = [
            "NoNormalsMesh0",
            "NoNormalsMesh1",
        ]

        # Ensure that the currently expected cases are covered.
        self.assertEqual(unique_cases[0], cases_0)
        self.assertEqual(unique_cases[1], cases_1)
        self.assertEqual(unique_cases[2], cases_2)
        self.assertEqual(unique_cases[3], cases_3)

    async def test_copy_values(self):
        """Check that deduplicate geometry via json dedudplicates."""
        # Open the stage and get the initial list of unique meshs.
        stage = self._open_stage("twoWithinToleranceMeshes.usda")
        # RTX finds 2 unique meshes in this scene so assert that we find the same.
        self.assertEqual(len(_get_unique_mesh_paths(stage)), 2)

        # Enable deep transform checks, set method to copy values, then execute json.
        # This should produce a result that has less unique meshes from the point of view on RTX.
        self._execute_json(stage, "deduplicateGeometry_copyValues.json")
        # Expecting one unique mesh after deduplication.
        self.assertEqual(len(_get_unique_mesh_paths(stage)), 1)

    async def test_copy_values_no_dt(self):
        """Check that deduplicateGeometry_copyValuesNoDeepTransforms.json does reduce the number of unique meshes"""
        # Open the stage and get the initial list of unique meshs.
        stage = self._open_stage("twoWithinToleranceMeshes.usda")
        # Enable deep transform checks, set method to copy values, then execute command.
        # This should produce a result that has less unique meshes from the point of view on RTX.
        self._execute_json(stage, "deduplicateGeometry_copyValuesNoDeepTransforms.json")
        # Assert that there are less unique meshes after execution.
        unique_meshes_after = _get_unique_mesh_paths(stage)

        # The logic currently results in 4 unique meshes.
        self.assertEqual(len(unique_meshes_after), 2)

    async def test_copy_values_tight_tolerance(self):
        """Check that very tigth tolerance does not change the number of unique meshes"""
        # Open the stage and get the initial list of unique meshs.
        stage = self._open_stage("twoWithinToleranceMeshes.usda")
        # Enable deep transforms but tight tolerance.
        self._execute_json(stage, "deduplicateGeometry_copyValuesTightTolerance.json")
        # With a very tight tollerance there should still be two meshes.
        self.assertEqual(len(_get_unique_mesh_paths(stage)), 2)

    async def test_copy_values_no_dt_execute_command(self):
        """Check that no deep transforms is picked up by _execute_command"""
        # Get a copy of the default arguments for this command
        args = DEFAULT_ARGS.copy()
        # Open the stage and get the initial list of unique meshs.
        stage = self._open_stage("twoWithinToleranceMeshes.usda")
        # Disable deep transforms.
        args["considerDeepTransforms"] = False
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES
        self._execute_command(args)

        # Without deep transforms there should still be two meshes.
        self.assertEqual(len(_get_unique_mesh_paths(stage)), 2)

    async def test_copy_values_tight_tolerance_execute_command(self):
        """Check that tight tolerance is picked up by _execute_command"""
        # Get a copy of the default arguments for this command
        args = DEFAULT_ARGS.copy()
        # Open the stage and get the initial list of unique meshs.
        stage = self._open_stage("twoWithinToleranceMeshes.usda")
        # Enable deep transforms but tight tolerance.
        args["tolerance"] = 0.00000001
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES
        self._execute_command(args)
        # With tight tolerance there should still be two meshes.
        self.assertEqual(len(_get_unique_mesh_paths(stage)), 2)

    async def test_multiple_peer_meshes_to_instanced_references(self):
        """Check that world space points match before and after deduplicate"""
        # Example scene with 4 peer meshes, 3 of which are the same. We expect the 3 that are the same to be de-duped.
        # There should be an extra xform added to one mesh and the other 2 should be instanced references of that one.
        file_name = "deduplicatePeerMeshes.usda"
        file_path = _get_test_data_file_path(file_name)

        # Get a copy of the default arguments for this command then set overrides
        args = DEFAULT_ARGS.copy()
        args["meshPrimPaths"] = ["/World//"]
        args["duplicateMethod"] = DUPLICATE_METHOD_INSTANCEABLEREFERENCE

        # Given a lookup table of before and after paths we can assert that the worldspace points match.
        lookup_table = [
            ("/World/Asset/Part/Geom/mesh_0", "/World/Asset/Part/Geom/mesh_0"),
            ("/World/Asset/Part/Geom/mesh_1", "/World/Asset/Part/Geom/mesh_1/Mesh"),
            ("/World/Asset/Part/Geom/mesh_2", "/World/Asset/Part/Geom/mesh_2/Mesh"),
            ("/World/Asset/Part/Geom/mesh_3", "/World/Asset/Part/Geom/mesh_3/Mesh"),
        ]

        # Get a handle to the stage and run the command.
        stage_after = self._open_stage(file_name)
        self._execute_command(args)

        # Get a handle to the stage in its original form.
        layer = Sdf.Layer.OpenAsAnonymous(file_path)
        stage_before = Usd.Stage.Open(layer)

        # Construct an xform cache to speed up local to world calculations.
        xformCache = UsdGeom.XformCache()

        # Iterate over before and after pair makign assertions
        for path_before, path_after in lookup_table:

            # Get the matching prims from the before and after stages.
            prim_before = stage_before.GetPrimAtPath(path_before)
            prim_after = stage_after.GetPrimAtPath(path_after)

            # Assert that the expected prims exist in the stages.
            self.assertTrue(prim_before.IsValid())
            self.assertTrue(prim_after.IsValid())

            # Assert that the points values match before and after command execution.
            self.assertWorldspacePointsEqual(prim_before, prim_after, xformCache)

        # Check that any prims which were Mesh before and are Xform after have had the schema attributes that no longer
        # apply removed.
        names = set(UsdGeom.Mesh.GetSchemaAttributeNames()) - set(UsdGeom.Xform.GetSchemaAttributeNames())
        # Remove primvars as they can be inherited.
        names.remove("primvars:displayColor")
        names.remove("primvars:displayOpacity")

        # Iterate over the paths of mesh prims before the command was run.
        for path, _ in lookup_table:
            prim = prim_after.GetPrimAtPath(path)

            # Assert that xform prims do not have any Mesh properties.
            if UsdGeom.Xform(prim):
                for name in names:
                    self.assertFalse(prim.HasAttribute(name))

    async def test_instance_proxies_as_input(self):
        """Check that we do not attempt to modify instance proxies during deduplicate"""
        # Example scene containing 6 meshes that are all the same mesh, but split over 3 materials, there is also an
        # instance of the whole asset in the scene. We expect the meshes with matching materials to be de-duped. The
        # instanced prims should pick up the de-dupe via composition, but there should be no direct edits.
        file_name = "deduplicateWithMaterials.usda"
        file_path = _get_test_data_file_path(file_name)

        # Get a copy of the default arguments for this command then set overrides
        args = DEFAULT_ARGS.copy()
        args["duplicateMethod"] = DUPLICATE_METHOD_INSTANCEABLEREFERENCE
        args["considerDeepTransforms"] = True
        args["tolerance"] = 0.05

        # Given a lookup table of before and after paths we can assert that the worldspace points match.
        lookup_table = [
            ("/World/Asset/Geom/mesh_0", "/World/Asset/Geom/mesh_0/Mesh"),
            ("/World/Asset/Geom/mesh_1", "/World/Asset/Geom/mesh_1/Mesh"),
            ("/World/Asset/Geom/mesh_2", "/World/Asset/Geom/mesh_2/Mesh"),
            ("/World/Asset/Geom/mesh_3", "/World/Asset/Geom/mesh_3/Mesh"),
            ("/World/Asset/Geom/mesh_4", "/World/Asset/Geom/mesh_4/Mesh"),
            ("/World/Asset/Geom/mesh_5", "/World/Asset/Geom/mesh_5/Mesh"),
            # mesh_6 and mesh_7 have UsdGeomSubsets so do not get instanced ... yet.
            ("/World/Asset/Geom/mesh_6", "/World/Asset/Geom/mesh_6"),
            ("/World/Asset/Geom/mesh_7", "/World/Asset/Geom/mesh_7"),
            # The meshes below "AssetInstance" will not have been modified but because the prims that they reference
            # have been changed they will inherit the changes.
            ("/World/AssetInstance/Geom/mesh_0", "/World/AssetInstance/Geom/mesh_0/Mesh"),
            ("/World/AssetInstance/Geom/mesh_1", "/World/AssetInstance/Geom/mesh_1/Mesh"),
            ("/World/AssetInstance/Geom/mesh_2", "/World/AssetInstance/Geom/mesh_2/Mesh"),
            ("/World/AssetInstance/Geom/mesh_3", "/World/AssetInstance/Geom/mesh_3/Mesh"),
            ("/World/AssetInstance/Geom/mesh_4", "/World/AssetInstance/Geom/mesh_4/Mesh"),
            ("/World/AssetInstance/Geom/mesh_5", "/World/AssetInstance/Geom/mesh_5/Mesh"),
            ("/World/AssetInstance/Geom/mesh_6", "/World/AssetInstance/Geom/mesh_6"),
            ("/World/AssetInstance/Geom/mesh_7", "/World/AssetInstance/Geom/mesh_7"),
        ]

        # Get a handle to the stage and run the command.
        stage_after = self._open_stage(file_name)
        self._execute_command(args)

        # Get a handle to the stage in its original form.
        layer = Sdf.Layer.OpenAsAnonymous(file_path)
        stage_before = Usd.Stage.Open(layer)

        # Get paths of meshes in the stage before and after de-duplication.
        meshes_before, instanced_meshes_before = _get_mesh_paths(stage_before)
        meshes_after, instanced_meshes_after = _get_mesh_paths(stage_after)

        expected = len(meshes_before) + len(instanced_meshes_before)
        returned = len(meshes_after) + len(instanced_meshes_after)
        self.assertEqual(returned, expected)

        # Assert the expected number of meshes instanced after de-duplication.
        expected = 5
        returned = len(instanced_meshes_after) - len(instanced_meshes_before)
        self.assertEqual(returned, expected)

        # Assert that the lookup table covers all the meshes both before and after.
        expected = sorted(Sdf.Path(x) for x, _ in lookup_table)
        returned = sorted(meshes_before + instanced_meshes_before)
        self.assertEqual(returned, expected)

        expected = sorted(Sdf.Path(x) for _, x in lookup_table)
        returned = sorted(meshes_after + instanced_meshes_after)
        self.assertEqual(returned, expected)

        # Construct a cache to speed up local to world calculations.
        xform_cache = UsdGeom.XformCache()

        # Iterate over before and after pair makign assertions
        for path_before, path_after in lookup_table:

            # Get the matching prims from the before and after stages.
            prim_before = stage_before.GetPrimAtPath(path_before)
            prim_after = stage_after.GetPrimAtPath(path_after)

            # Assert that the expected prims exist in the stages.
            self.assertTrue(prim_before.IsValid())
            self.assertTrue(prim_after.IsValid())

            # Assert that the points values match before and after command execution.
            self.assertWorldspacePointsEqual(prim_before, prim_after, xform_cache, tolerance=args["tolerance"])

            # Assert that the materials bound before and after have the same paths.
            self.assertBoundMaterialsEqual(prim_before, prim_after)

    async def test_crash_with_empty_extent(self):
        """Check that we do not crash when deduplicate operations are run in series"""
        # The crash in this case was caused by meshes that do not have extent values defined being deduplicated multiple
        # times. During the copy values run the extent attribute changes from un-authored to authored, but the value is
        # still empty. Subsequently the second run crashes when it finds an authored extent that does not hold 2 values.

        # We assert this here simply because it was reported and we need a test to cover the case.

        # Load a simple scene that has 4 cubes that do not have extent values.
        self._open_stage("simpleFourCubes.usda")

        # Get a copy of the default arguments for this command then set overrides.
        args = DEFAULT_ARGS.copy()
        args["considerDeepTransforms"] = True
        args["tolerance"] = 0.05

        # Run once with copy values.
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES
        self._execute_command(args)

        # Run a second time with instanceable references.
        args["duplicateMethod"] = DUPLICATE_METHOD_INSTANCEABLEREFERENCE
        self._execute_command(args)

        # Just getting this far proves the crash is gone.

    async def test_deduplicate_payload_with_transforms(self):
        """Check that before and after point positions are correct when duplicate prims are coming from a payload"""
        # Example scene with 2 peer meshes that both have transforms and come from a payload.
        # They need to have the xforms as well as be payloads so that we get mixed strength when the instanceable
        # reference arcs are added.

        # Get a copy of the default arguments for this command then set overrides
        args = DEFAULT_ARGS.copy()
        args["meshPrimPaths"] = ["/World//"]
        args["duplicateMethod"] = DUPLICATE_METHOD_INSTANCEABLEREFERENCE

        # Given a lookup table of before and after paths we can assert that the worldspace points match.
        lookup_table = [
            ("/World/mesh0", "/World/mesh0/Mesh"),
            ("/World/mesh1", "/World/mesh1/Mesh"),
        ]

        # Get a handle to the stage and run the command.
        file_name = "deduplicateWithTransforms_wrapper.usda"
        file_path = _get_test_data_file_path(file_name)
        stage_after = self._open_stage(file_name)
        self._execute_command(args)

        # Get a handle to the stage in its original form.
        # Due to an annoying bug in path resolution we need the same data in a different file rather than opening the
        # layer as anonymous.
        file_name = "deduplicateWithTransforms_wrapper2.usda"
        file_path = _get_test_data_file_path(file_name)
        layer = Sdf.Layer.FindOrOpen(file_path)
        stage_before = Usd.Stage.Open(layer)

        # Construct an xform cache to speed up local to world calculations.
        xformCache = UsdGeom.XformCache()

        # Iterate over before and after pair making assertions
        for path_before, path_after in lookup_table:

            # Get the matching prims from the before and after stages.
            prim_before = stage_before.GetPrimAtPath(path_before)
            prim_after = stage_after.GetPrimAtPath(path_after)

            # Assert that the expected prims exist in the stages.
            self.assertTrue(prim_before.IsValid())
            self.assertTrue(prim_after.IsValid())

            # Assert that the points values match within tolerance before and after command execution.
            self.assertWorldspacePointsEqual(prim_before, prim_after, xformCache)

    async def test_deduplicate_nearly_planar_meshes(self):
        """Check deduplication of planar and nearly planar meshes."""
        # Example scene with 2 planar meshes, one being a deep transformed version of the other.
        # The second, due to rounding errors during deep transform being only nearly planar.
        # Thus, the scene contains a planar and a nearly planar mesh that should be deduplicated.

        # Get a copy of the default arguments for this command then set overrides
        args = DEFAULT_ARGS.copy()
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES

        # Get a handle to the stage and run the command.
        file_name = "deduplicate_planes.usda"
        file_path = _get_test_data_file_path(file_name)
        stage_after = self._open_stage(file_name)
        self._execute_command(args)

        # Check that nearly planar mesh has been deduplicated, and number of unique meshes is reduced to 1.
        self.assertEqual(len(_get_unique_mesh_paths(stage_after)), 1)

        # General check that objects remain at the place, before and after the operation.
        layer = Sdf.Layer.FindOrOpen(file_path)
        stage_before = Usd.Stage.Open(layer)
        self.assertWorldspaceScenePointsEqual(stage_before, stage_after, None)

    async def test_transform_of_near_planar_meshes(self):
        """Check that planar non-planar meshes can be deduplicated with "reasonable" transforms"""
        # Example scene with 2 peer meshes that both both planes, but one has been deep rotated.

        # Get a copy of the default arguments for this command then set overrides
        args = DEFAULT_ARGS.copy()
        args["meshPrimPaths"] = ["/World/mesh_0", "/World/mesh_1"]
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES

        # Get a handle to the stage and run the command.
        file_name = "deduplicate_planes.usda"
        file_path = _get_test_data_file_path(file_name)
        stage_after = self._open_stage(file_name)
        self._execute_command(args)

        # Get the resulting transform of the prim values were copied to.
        prim = stage_after.GetPrimAtPath("/World/mesh_0")
        xformCache = UsdGeom.XformCache()
        matrix = xformCache.GetLocalToWorldTransform(prim)
        transform = Gf.Transform(matrix)

        # The scale should be near identity as the mesh only required rotating.
        msg = "Scale of {} differs from identity".format(transform.GetScale())
        expected = (1.0, 1.0, 1.0)
        returned = transform.GetScale()
        self.assertAlmostEqual(returned[0], expected[0], places=6, msg=msg)
        self.assertAlmostEqual(returned[1], expected[1], places=6, msg=msg)
        self.assertAlmostEqual(returned[2], expected[2], places=6, msg=msg)

    async def test_specifier_unchanged(self):
        """Check that deduplicate does not modify the specifier of prims"""
        # This test case contains meshes that are composed from references to prims with class and over specifiers.
        stage = self._open_stage("abstractPrims_input.usda")

        # Assert the initial state of the specifiers
        self.assertEqual(stage.GetPrimAtPath("/World/Classes").GetSpecifier(), Sdf.SpecifierClass)
        self.assertEqual(stage.GetPrimAtPath("/World/Meshes").GetSpecifier(), Sdf.SpecifierOver)

        # Get a copy of the default arguments for this command then set overrides.
        args = DEFAULT_ARGS.copy()
        args["considerDeepTransforms"] = True
        args["tolerance"] = 0.05

        # Run once with copy values.
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES
        self._execute_command(args)

        # Assert that the specifiers are still the same
        self.assertEqual(stage.GetPrimAtPath("/World/Classes").GetSpecifier(), Sdf.SpecifierClass)
        self.assertEqual(stage.GetPrimAtPath("/World/Meshes").GetSpecifier(), Sdf.SpecifierOver)

        # Reopen the stage
        stage = self._open_stage("abstractPrims_input.usda")

        # Run a second time with instanceable references.
        args["duplicateMethod"] = DUPLICATE_METHOD_INSTANCEABLEREFERENCE
        self._execute_command(args)

        # Assert that the specifiers are still the same
        self.assertEqual(stage.GetPrimAtPath("/World/Classes").GetSpecifier(), Sdf.SpecifierClass)
        self.assertEqual(stage.GetPrimAtPath("/World/Meshes").GetSpecifier(), Sdf.SpecifierOver)

    async def test_scaled_deduplicates_with_tolerance(self):
        """Check that before and after meshes are within tolerance values when scaling is applied"""
        # Example scene with 2 peer meshes that have large scale difference and some point jitter applied.
        # If they are seen as duplicates we expect the before and after points to have moved no more than the tolerance
        # value in worldspace.
        file_name = "deduplicateTolerance.usda"
        file_path = _get_test_data_file_path(file_name)

        # Construct an xform cache to speed up local to world calculations.
        xformCache = UsdGeom.XformCache()

        # Get a copy of the default arguments for this command then set overrides
        args = DEFAULT_ARGS.copy()
        args["meshPrimPaths"] = ["/World/Mesh_1", "/World/Mesh_0"]
        args["duplicateMethod"] = DUPLICATE_METHOD_REFERENCE
        args["tolerance"] = 1.1

        # Get a handle to the stage and run the command.
        stage_after = self._open_stage(file_name)
        self._execute_command(args)

        # Get a handle to the stage in its original form.
        layer = Sdf.Layer.OpenAsAnonymous(file_path)
        stage_before = Usd.Stage.Open(layer)

        # Iterate over path in the before and after stage making assertions.
        for path in args["meshPrimPaths"]:

            # Get the matching prims from the before and after stages.
            prim_before = stage_before.GetPrimAtPath(path)
            prim_after = stage_after.GetPrimAtPath(path)

            # Assert that the expected prims exist in the stages.
            self.assertTrue(prim_before.IsValid())
            self.assertTrue(prim_after.IsValid())

            # Assert that the points values match within tolerance before and after command execution.
            self.assertWorldspacePointsEqual(prim_before, prim_after, xformCache, tolerance=args["tolerance"])

    async def test_normals(self):
        """Check that the different styles of normals expression are all supported"""
        file_name = "normals_options.usda"
        file_path = _get_test_data_file_path(file_name)

        # Open the stage and get the initial list of unique meshs.
        stage = self._open_stage(file_name)
        unique_meshes_before = _get_unique_mesh_paths(stage)

        # RTX finds 10 unique meshes in this scene so assert that we find the same.
        self.assertEqual(len(unique_meshes_before), 10)

        paths = [
            "/none/mesh_0",
            "/attr_uniform/mesh_0",
            "/attr_vertex/mesh_0",
            "/attr_facevarying/mesh_0",
            "/primvar_uniform/mesh_0",
            "/primvar_vertex/mesh_0",
            "/primvar_facevarying/mesh_0",
            "/primvar_uniform_indexed/mesh_0",
            "/primvar_vertex_indexed/mesh_0",
            "/primvar_facevarying_indexed/mesh_0",
        ]

        # Execute the deduplicate command using copy values.
        args = DEFAULT_ARGS.copy()
        args["meshPrimPaths"] = paths
        args["considerDeepTransforms"] = True
        args["tolerance"] = 0.05
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES
        self._execute_command(args)

        # Assert that there are less unique meshes after execution.
        unique_meshes_after = _get_unique_mesh_paths(stage)
        self.assertTrue(len(unique_meshes_before) > len(unique_meshes_after))

        # The logic currently results in 4 unique meshes.
        self.assertEqual(len(unique_meshes_after), 4)

        # Get a handle to the stage in its original form.
        layer = Sdf.Layer.OpenAsAnonymous(file_path)
        stage_before = Usd.Stage.Open(layer)

        # Construct an xform cache to speed up local to world calculations.
        xformCache = UsdGeom.XformCache()

        # Iterate over path in the before and after stage making assertions.
        for path in paths:

            # Get the matching prims from the before and after stages.
            prim_before = stage_before.GetPrimAtPath(path)
            prim_after = stage.GetPrimAtPath(path)

            # Assert that the expected prims exist in the stages.
            self.assertTrue(prim_before.IsValid())
            self.assertTrue(prim_after.IsValid())

            # Assert that the points values match within tolerance before and after command execution.
            self.assertWorldspacePointsEqual(prim_before, prim_after, xformCache, tolerance=args["tolerance"])

    async def test_data_volume_ignored_in_buckets(self):
        """Check that data volume of prims does not cause multiple buckets"""
        # When "Merge Static Meshes" uses the Bucket class it wants to split Buckets to ensure that the
        # total point count stay below the array size limit. However "Deduplicate Geometry" does not have
        # this concern and we do not want to artificially split prim sets that are actually duplicates.

        # Open the stage.
        file_name = "maxDataVolume.usdc"
        stage = self._open_stage(file_name)

        # Assert that there are no prototypes before deduplicate has run
        expected = 0
        returned = len(stage.GetPrototypes())
        self.assertEqual(returned, expected)

        # Execute the deduplicate command using instanceable references
        args = DEFAULT_ARGS.copy()
        args["considerDeepTransforms"] = True
        args["tolerance"] = 10000.0  # Use crazy tolerance to ensure all prims are equal
        args["duplicateMethod"] = DUPLICATE_METHOD_INSTANCEABLEREFERENCE

        self._execute_command(args)

        # Assert that there is one prototype after deduplicate has run
        expected = 1
        returned = len(stage.GetPrototypes())
        self.assertEqual(returned, expected)

        # Assert that there is one non instanced Mesh after deduplicate has run
        expected = 1
        returned = len([x for x in stage.Traverse() if x.GetTypeName() == "Mesh"])
        self.assertEqual(returned, expected)

    async def test_complex_composition_crash(self):
        """Check that deduplicate does not cause crashes when complex composition is at play"""
        # Previously the transform setting code had caused crashes because, after checking if prims
        # had a named xform op we would blindly add them, however as composition was updated some prims
        # would inherit an xform op and the name clash were fatal.

        file_name = "various_construction_arcs.usda"

        # Use this path order so that the target prims are those taht have complex composition.
        args = DEFAULT_ARGS.copy()
        args["meshPrimPaths"] = ["/World_Copy", "/World"]
        args["considerDeepTransforms"] = True
        args["tolerance"] = 0.05

        # Execute the deduplicate command using copy values.
        self._open_stage(file_name)
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES
        self._execute_command(args)

        # Execute the deduplicate command using instanceable references.
        self._open_stage(file_name)
        args["duplicateMethod"] = DUPLICATE_METHOD_INSTANCEABLEREFERENCE
        self._execute_command(args)

        # Reaching this point indicates that we have not crashed.

    async def test_deduplicate_geometry_fuzzy(self):
        """Test deduplicate geometry (fuzzy)"""

        # Test DUPLICATE_METHOD_SET_ATTRIBUTE
        args = DEFAULT_ARGS.copy()
        args["duplicateMethod"] = DUPLICATE_METHOD_SET_ATTRIBUTE
        args["fuzzy"] = True

        expectedSets0 = []
        expectedSets1 = []

        for testCase in range(4):

            if testCase == 0:

                args["tolerance"] = 0.01
                args["allowScaling"] = False
                expectedSets0 = [1, 1, 0, 0, 0, 0]
                expectedSets1 = [1, 1, 0, 0, 0, 0]

            elif testCase == 1:

                args["tolerance"] = 0.01
                args["allowScaling"] = True
                expectedSets1 = [1, 1, 1, 0, 2, 2]
                expectedSets0 = [2, 2, 2, 0, 1, 1]

            elif testCase == 2:

                args["tolerance"] = 0.1
                args["allowScaling"] = False
                expectedSets0 = [1, 1, 0, 2, 2, 0]
                expectedSets1 = [2, 2, 0, 1, 1, 0]

            elif testCase == 3:

                args["tolerance"] = 0.1
                args["allowScaling"] = True
                expectedSets0 = [1, 1, 1, 2, 2, 2]
                expectedSets1 = [2, 2, 2, 1, 1, 1]

            stage = self._open_stage("fuzzyDedupTest.usda")

            success, result = self._execute_command(args)

            self.assertTrue(success)

            sets = []

            sets.append(stage.GetPrimAtPath("/box1/box1").GetAttribute("duplicationSet").Get())
            sets.append(stage.GetPrimAtPath("/box2/box2").GetAttribute("duplicationSet").Get())
            sets.append(stage.GetPrimAtPath("/box3/box3").GetAttribute("duplicationSet").Get())

            sets.append(stage.GetPrimAtPath("/torus1/torus1").GetAttribute("duplicationSet").Get())
            sets.append(stage.GetPrimAtPath("/torus2/torus2").GetAttribute("duplicationSet").Get())
            sets.append(stage.GetPrimAtPath("/torus3/torus3").GetAttribute("duplicationSet").Get())

            self.assertTrue(sets == expectedSets0 or sets == expectedSets1)

        # Test DUPLICATE_METHOD_REFERENCE
        args = DEFAULT_ARGS.copy()
        args["duplicateMethod"] = DUPLICATE_METHOD_REFERENCE
        args["fuzzy"] = True
        args["useGpu"] = False
        args["tolerance"] = 0.1
        args["allowScaling"] = True

        stage = self._open_stage("fuzzyDedupTest.usda")

        success, result = self._execute_command(args)

        self.assertTrue(success)

        boxes = ["/box1/box1", "/box2/box2", "/box3/box3"]
        toruses = ["/torus1/torus1", "/torus2/torus2", "/torus3/torus3"]

        numReferences = 0
        for box in boxes:
            if stage.GetPrimAtPath(box).HasAuthoredReferences():
                numReferences += 1

        self.assertTrue(numReferences == 1)

        numReferences = 0
        for torus in toruses:
            if stage.GetPrimAtPath(torus).HasAuthoredReferences():
                numReferences += 1

        self.assertTrue(numReferences == 1)

        # Test DUPLICATE_METHOD_INSTANCEABLEREFERENCE
        args = DEFAULT_ARGS.copy()
        args["duplicateMethod"] = DUPLICATE_METHOD_INSTANCEABLEREFERENCE
        args["fuzzy"] = True
        args["useGpu"] = False
        args["tolerance"] = 0.1
        args["allowScaling"] = True

        stage = self._open_stage("fuzzyDedupTest.usda")

        success, result = self._execute_command(args)

        self.assertTrue(success)

        numReferences = 0
        for box in boxes:
            if stage.GetPrimAtPath(box).HasAuthoredReferences():
                numReferences += 1

        self.assertTrue(numReferences == 1)

        numReferences = 0
        for torus in toruses:
            if stage.GetPrimAtPath(torus).HasAuthoredReferences():
                numReferences += 1

        self.assertTrue(numReferences == 1)

        # Test DUPLICATE_METHOD_COPYVALUES
        args = DEFAULT_ARGS.copy()
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES
        args["fuzzy"] = True
        args["useGpu"] = False
        args["tolerance"] = 0.1
        args["allowScaling"] = True

        stage = self._open_stage("fuzzyDedupTest.usda")

        success, result = self._execute_command(args)

        self.assertTrue(success)

        allPrimNames = [
            ["/torus1/torus1", "/torus2/torus2", "/torus3/torus3"],
            ["/box1/box1", "/box2/box2", "/box3/box3"],
        ]

        for i in range(len(allPrimNames)):
            equalPrimNames = allPrimNames[i]

            # Test whether the prims have the same primvars (checking the lengths only)
            sizes = []

            for j in range(len(equalPrimNames)):
                prim = stage.GetPrimAtPath(equalPrimNames[j])
                api = UsdGeom.PrimvarsAPI(prim)
                primvars = api.GetPrimvars()

                for k in range(len(primvars)):
                    primvar = primvars[k]
                    value = primvar.Get()
                    size = len(value) if value is not None else 0
                    if j == 0:
                        sizes.append(size)
                    else:
                        self.assertTrue(size == sizes[k])

        # Test DUPLICATE_METHOD_INSTANCEABLEREFERENCE with constant color and varied tesselation
        args = DEFAULT_ARGS.copy()
        args["duplicateMethod"] = DUPLICATE_METHOD_INSTANCEABLEREFERENCE
        args["fuzzy"] = True
        args["tolerance"] = 0.1
        args["allowScaling"] = True

        stage = self._open_stage("fuzzyDedupConstantColorTest.usda")

        success, result = self._execute_command(args)

        self.assertTrue(success)

        numReferences = 0
        for box in boxes:
            if stage.GetPrimAtPath(box).HasAuthoredReferences():
                numReferences += 1

        self.assertTrue(numReferences == 1)

    async def test_time_varying_meshes(self):
        """Test deduplicate operation on meshes with authored time varying attributes, the mesh should not be processed"""
        # Get a copy of the default arguments for this command
        args = DEFAULT_ARGS.copy()
        # Open the stage
        stage = self._open_stage("time_varying_meshes.usd")
        # run command
        success, result = self._execute_command(args)

        # asserts success of execution
        self.assertTrue(success)

        # currently skipping time sampled meshes to avoid corrupting the scene
        # test to be expanded when time samples are better handled in the operation
        # assert that no meshes have been turned into instances
        meshes = _get_meshes(stage)
        for mesh in meshes:
            self.assertFalse(mesh.IsInstance())

    def assert_pivot(self, prim, pivot):
        """Assert the expected value of a pivot"""

        pivotVal = prim.GetAttribute("xformOp:translate:pivot").Get()
        self.assertEqual(pivotVal, pivot)

    async def test_deduplicate_inverse_pivot_copy(self):
        """Test deduplicating meshes with a pivot using copyValues"""

        stage = self._open_stage("deduplicateGeometryPivot.usda")

        cube = stage.GetPrimAtPath("/World/Cube")
        cubeDup = stage.GetPrimAtPath("/World/CubeDuplicate")
        cubeDupPivot = stage.GetPrimAtPath("/World/CubeDuplicateCustomPivot")
        cubeDupAlt = stage.GetPrimAtPath("/World/CubeDuplicateAlternateTopology")

        pointsCube = cube.GetAttribute("points").Get()
        pointsDup = cubeDup.GetAttribute("points").Get()
        pointsDupPivot = cubeDupPivot.GetAttribute("points").Get()
        pointsDupAlt = cubeDupAlt.GetAttribute("points").Get()

        # Assert initial state - cube and cubeDup have the same vertices,
        # the others are both different.
        self.assertEqual(pointsCube, pointsDup)
        self.assertNotEqual(pointsCube, pointsDupPivot)
        self.assertNotEqual(pointsCube, pointsDupAlt)
        self.assertNotEqual(pointsDupPivot, pointsDupAlt)

        args = DEFAULT_ARGS.copy()
        args["duplicateMethod"] = DUPLICATE_METHOD_COPYVALUES

        success, result = self._execute_command(args)
        self.assertTrue(success)

        # Assert all cubes have matching vertices after deduplication
        pointsCube = cube.GetAttribute("points").Get()
        pointsDup = cubeDup.GetAttribute("points").Get()
        pointsDupPivot = cubeDupPivot.GetAttribute("points").Get()
        pointsDupAlt = cubeDupAlt.GetAttribute("points").Get()

        # Assert new topology state
        self.assertEqual(pointsCube, pointsDup)
        self.assertEqual(pointsCube, pointsDupPivot)
        self.assertEqual(pointsCube, pointsDupAlt)

        # Assert pivot values
        self.assert_pivot(cube, Gf.Vec3d(-175, -175, -175))
        self.assert_pivot(cubeDup, Gf.Vec3d(-175, -175, -175))
        self.assert_pivot(cubeDupAlt, Gf.Vec3d(-175, -175, -175))
        # This is the main difference (custom pivot)
        self.assert_pivot(cubeDupPivot, Gf.Vec3d(-200, -200, -200))

    async def test_deduplicate_inverse_pivot_instance(self):
        """Test deduplicating meshes with a pivot using instanceableref"""

        stage = self._open_stage("deduplicateGeometryPivot.usda")

        cube = stage.GetPrimAtPath("/World/Cube")
        cubeDup = stage.GetPrimAtPath("/World/CubeDuplicate")
        cubeDupPivot = stage.GetPrimAtPath("/World/CubeDuplicateCustomPivot")
        cubeDupAlt = stage.GetPrimAtPath("/World/CubeDuplicateAlternateTopology")

        self.assertTrue(cube.IsA(UsdGeom.Mesh))
        self.assertTrue(cubeDup.IsA(UsdGeom.Mesh))
        self.assertTrue(cubeDupPivot.IsA(UsdGeom.Mesh))
        self.assertTrue(cubeDupAlt.IsA(UsdGeom.Mesh))

        # Execute operation
        args = DEFAULT_ARGS.copy()
        success, result = self._execute_command(args)
        self.assertTrue(success)

        # Original prims are now xforms
        self.assertTrue(cube.IsA(UsdGeom.Xform))
        self.assertTrue(cubeDup.IsA(UsdGeom.Xform))
        self.assertTrue(cubeDupPivot.IsA(UsdGeom.Xform))
        self.assertTrue(cubeDupAlt.IsA(UsdGeom.Xform))

        # Assert Xform pivot values
        self.assert_pivot(cube, Gf.Vec3d(-225, -225, -225))
        self.assert_pivot(cubeDup, Gf.Vec3d(-225, -225, -225))
        self.assert_pivot(cubeDupAlt, Gf.Vec3d(-225, -225, -225))
        # As with copy values, the custom pivot should be different.
        self.assert_pivot(cubeDupPivot, Gf.Vec3d(-250, -250, -250))

        mesh = stage.GetPrimAtPath("/World/Cube/Mesh")
        meshDup = stage.GetPrimAtPath("/World/CubeDuplicate/Mesh")
        meshPivot = stage.GetPrimAtPath("/World/CubeDuplicateCustomPivot/Mesh")
        meshAlt = stage.GetPrimAtPath("/World/CubeDuplicateAlternateTopology/Mesh")

        # Assert mesh pivot values
        # The meshes are instance proxies, so won't have the custom pivot
        self.assert_pivot(mesh, Gf.Vec3d(-225, -225, -225))
        self.assert_pivot(meshDup, Gf.Vec3d(-225, -225, -225))
        self.assert_pivot(meshPivot, Gf.Vec3d(-225, -225, -225))
        self.assert_pivot(meshAlt, Gf.Vec3d(-225, -225, -225))
