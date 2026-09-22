"""Suite of tests to exercise the implications of the removal of various settings."""

from typing import Any, Dict, List

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
import omni.usd
import OmniGraphSchema
from pxr import Gf

KEYS = og.Controller.Keys
"""Shorten keyword names"""

FILE_FORMAT_VERSION_INTRODUCING_SCHEMAS = Gf.Vec2i(1, 4)
"""File format version where the schema prims became the default"""

CURRENT_FORMAT_VERSION = Gf.Vec2i(
    og.Graph.CURRENT_FILE_FORMAT_VERSION.majorVersion, og.Graph.CURRENT_FILE_FORMAT_VERSION.minorVersion
)
"""The current version of settings"""


# ==============================================================================================================
def _verify_stage_contents(expected_contents: Dict[str, str], expected_inactive_prims: List[str] = None) -> List[str]:
    """Confirm that a stage contains the hierarchical prim type structure passed in.

    Args:
        expected_contents: Dictionary of primPath:primType of stage contents that were expected.
                           e.g. a two level prim hierarchy with an Xform and a Mesh would be passed in as
                            {"/MyXform": "Xform", "/MyXform/MyMesh": "Mesh"}
        expected_inactive_prims: A list of keys to the above whose prims are also expected to be inactive

    Returns:
        A list of a description of the differences found (may not be complete), or [] if all was as expected
    """
    stage = omni.usd.get_context().get_stage()
    if stage is None:
        return [] if not expected_contents else [f"Stage is empty but expected to find {expected_contents}"]

    # Copy of the dictionary to removed found prims from that should be empty when done
    inactive_list = expected_inactive_prims or []
    not_found = expected_contents.copy()
    errors_found = []
    iterator = iter(stage.TraverseAll())
    for prim in iterator:
        prim_path = str(prim.GetPrimPath())
        prim_type = prim.GetTypeName()
        # Ignore these boilerplate prims
        if prim_path.startswith("/Omniverse") or prim_path.startswith("/Render"):
            continue
        if prim_path not in expected_contents:
            errors_found.append(
                f"Prim '{prim_path}' of type '{prim_type}' was not in the expected list {expected_contents}"
            )
            continue

        if expected_contents[prim_path] != prim_type:
            errors_found.append(
                f"Prim '{prim_path}' expected to be of type '{expected_contents[prim_path]}' but was '{prim_type}'"
            )
            continue

        if prim_path in inactive_list and prim.IsActive():
            errors_found.append(f"Prim '{prim_path}' of type '{prim_type}' expected to be inactive but was not")

        if prim.GetTypeName() == "OmniGraphNode":
            # Confirm that the expected schema attributes exist on the node as non-custom types
            node_prim = OmniGraphSchema.OmniGraphNode(prim)
            if not node_prim:
                errors_found.append(f"Prim '{prim_path}' could not be interpreted as OmniGraphNode")
            else:
                type_attr = node_prim.GetNodeTypeAttr()
                if not type_attr.IsValid() or type_attr.IsCustom():
                    errors_found.append(f"Node '{prim_path}' did not have schema attribute node:type")
                version_attr = node_prim.GetNodeTypeVersionAttr()
                if not version_attr.IsValid() or version_attr.IsCustom():
                    errors_found.append(f"Node '{prim_path}' did not have schema attribute node:typeVersion")
        elif prim.GetTypeName() == "OmniGraph":
            # Confirm that the expected schema attributes exist on the graph as non-custom types
            graph_prim = OmniGraphSchema.OmniGraph(prim)
            if not graph_prim:
                errors_found.append(f"Prim '{prim_path}' could not be interpreted as OmniGraph")
            else:
                evaluator_attr = graph_prim.GetEvaluatorTypeAttr()
                if not evaluator_attr.IsValid() or evaluator_attr.IsCustom():
                    errors_found.append(f"Graph '{prim_path}' did not have schema attribute evaluatorType")
                version_attr = graph_prim.GetFileFormatVersionAttr()
                if not version_attr.IsValid() or version_attr.IsCustom():
                    errors_found.append(f"Graph '{prim_path}' did not have schema attribute fileFormatVersion")
                backing_attr = graph_prim.GetFabricCacheBackingAttr()
                if not backing_attr.IsValid() or backing_attr.IsCustom():
                    errors_found.append(f"Graph '{prim_path}' did not have schema attribute fabricCacheBacking")
                pipeline_attr = graph_prim.GetPipelineStageAttr()
                if not pipeline_attr.IsValid() or pipeline_attr.IsCustom():
                    errors_found.append(f"Graph '{prim_path}' did not have schema attribute pipelineStage")
                evaluation_mode_attr = graph_prim.GetEvaluationModeAttr()
                if not evaluation_mode_attr.IsValid() or evaluation_mode_attr.IsCustom():
                    errors_found.append(f"Graph '{prim_path}' did not have schema attribute evaluationMode")
        del not_found[prim_path]

    for prim_path, prim_type in not_found.items():
        errors_found.append(f"Prim '{prim_path}' of type '{prim_type}' was expected but not found")

    return errors_found


# ==============================================================================================================
def _verify_graph_settings(graph_prim_path: str, expected_settings: Dict[str, Any]):
    """Verify that the graph prim has the expected settings (after conversion or loading of a new file)

    Args:
        graph_prim_path: Path to the graph's prim
        expected_settings: Dictionary of attributeName:expectedValue for all of the settings

    Returns:
        List of descriptions of the differences found or [] if all was as expected
    """
    errors_found = []
    stage = omni.usd.get_context().get_stage()
    graph_prim = stage.GetPrimAtPath(graph_prim_path) if stage is not None else None
    if graph_prim is None:
        return [f"Could not find prim `{graph_prim_path}` that is supposed to hold the settings"]

    for attribute_name, expected_value in expected_settings.items():
        attribute = graph_prim.GetAttribute(attribute_name)
        if not attribute.IsValid():
            errors_found.append(f"Could not find setting attribute '{attribute_name}' on prim '{graph_prim_path}'")
        else:
            actual_value = attribute.Get()
            if actual_value != expected_value:
                errors_found.append(
                    f"Expected value of setting '{attribute_name}' was '{expected_value}', got '{actual_value}'"
                )
    return errors_found


# ==============================================================================================================
class TestSettingsRemoval(ogts.OmniGraphTestCase):
    """Wrapper for tests to verify backward compatibility for the removal of the settings prim"""

    # Settings values when nothing is specified.
    DEFAULT_SETTINGS = {
        "evaluator:type": "push",
        "fileFormatVersion": CURRENT_FORMAT_VERSION,
        "fabricCacheBacking": "StageWithoutHistory",
        "pipelineStage": "pipelineStageSimulation",
        "evaluationMode": "Automatic",
    }

    # ----------------------------------------------------------------------
    async def test_create_graph(self):
        """Test creation of a simple graph"""
        og.Controller.edit("/SimpleGraph", {KEYS.CREATE_NODES: ("NoOp", "omni.graph.nodes.Noop")})
        await og.Controller.evaluate()
        results = _verify_stage_contents({"/SimpleGraph": "OmniGraph", "/SimpleGraph/NoOp": "OmniGraphNode"})
        self.assertEqual([], results)
        results = _verify_graph_settings("/SimpleGraph", self.DEFAULT_SETTINGS)
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_no_settings_1_1(self):
        """Test that a v1.1 file with a graph and no settings is converted correctly"""
        (result, error) = await ogts.load_test_file("SettingsMissingFromGraph_v1_1.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/defaultGraph": "OmniGraph",
            }
        )
        self.assertEqual([], results)
        results = _verify_graph_settings(
            "/defaultGraph",
            {
                "evaluator:type": "push",
                "fileFormatVersion": CURRENT_FORMAT_VERSION,
                "fabricCacheBacking": "Shared",
                "pipelineStage": "pipelineStageSimulation",
                "evaluationMode": "Automatic",
            },
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_no_settings_post_schema(self):
        """Test that an updated file without explicit settings has the default values"""
        (result, error) = await ogts.load_test_file(
            "SettingsMissingFromGraph_postSchema.usda", use_caller_subdirectory=True
        )
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/defaultGraph": "OmniGraph",
            }
        )
        self.assertEqual([], results)
        results = _verify_graph_settings(
            "/defaultGraph",
            {
                "evaluator:type": "push",
                "fileFormatVersion": CURRENT_FORMAT_VERSION,
                "fabricCacheBacking": "Shared",
                "pipelineStage": "pipelineStageSimulation",
                "evaluationMode": "Automatic",
            },
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_no_graph_1_0(self):
        """Test that a v1.0 file that has settings data without FC and pipeline settings is converted correctly"""
        (result, error) = await ogts.load_test_file("SettingsWithoutGraph_v1_0.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/__graphUsingSchemas": "OmniGraph",
                "/__graphUsingSchemas/NoOp": "OmniGraphNode",
                "/__graphUsingSchemas/computegraphSettings": "ComputeGraphSettings",
            },
            ["/__graphUsingSchemas/computegraphSettings"],
        )
        self.assertEqual([], results)
        results = _verify_graph_settings(
            "/__graphUsingSchemas",
            {
                "evaluator:type": "push",
                "fileFormatVersion": CURRENT_FORMAT_VERSION,
                "fabricCacheBacking": "Shared",
                "pipelineStage": "pipelineStageSimulation",
                "evaluationMode": "Automatic",
            },
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_no_graph_1_1(self):
        """Test that a v1.1 file with an implicit graph is converted correctly"""
        (result, error) = await ogts.load_test_file("SettingsWithoutGraph_v1_1.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/__graphUsingSchemas": "OmniGraph",
                "/__graphUsingSchemas/NoOp": "OmniGraphNode",
                "/__graphUsingSchemas/computegraphSettings": "ComputeGraphSettings",
            },
            ["/__graphUsingSchemas/computegraphSettings"],
        )
        self.assertEqual([], results)
        results = _verify_graph_settings(
            "/__graphUsingSchemas",
            {
                "evaluator:type": "push",
                "fileFormatVersion": CURRENT_FORMAT_VERSION,
                "fabricCacheBacking": "StageWithHistory",
                "pipelineStage": "pipelineStagePreRender",
                "evaluationMode": "Automatic",
            },
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_no_graph_child_1_1(self):
        """Test that a v1.1 file with a graph underneath a World prim is converted correctly"""
        (result, error) = await ogts.load_test_file("SettingsWithChildGraph_v1_1.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/World": "World",
                "/World/__graphUsingSchemas": "OmniGraph",
                "/World/__graphUsingSchemas/NoOp": "OmniGraphNode",
                "/World/__graphUsingSchemas/computegraphSettings": "ComputeGraphSettings",
            },
            ["/World/__graphUsingSchemas/computegraphSettings"],
        )
        self.assertEqual([], results)
        results = _verify_graph_settings(
            "/World/__graphUsingSchemas",
            {
                "evaluator:type": "push",
                "fileFormatVersion": CURRENT_FORMAT_VERSION,
                "fabricCacheBacking": "StageWithHistory",
                "pipelineStage": "pipelineStagePreRender",
                "evaluationMode": "Automatic",
            },
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_with_graph_1_1(self):
        """Test that a v1.1 file with an explicit graph and settings is converted correctly"""
        (result, error) = await ogts.load_test_file("SettingsWithGraph_v1_1.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/pushGraph": "OmniGraph",
                "/pushGraph/NoOp": "OmniGraphNode",
                "/pushGraph/computegraphSettings": "ComputeGraphSettings",
            },
            ["/pushGraph/computegraphSettings"],
        )
        self.assertEqual([], results)
        results = _verify_graph_settings(
            "/pushGraph",
            {
                "evaluator:type": "push",
                "fileFormatVersion": CURRENT_FORMAT_VERSION,
                "fabricCacheBacking": "StageWithHistory",
                "pipelineStage": "pipelineStagePreRender",
                "evaluationMode": "Automatic",
            },
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_with_bad_backing_name(self):
        """Test that a file using the backing name with a typo gets the correct name"""
        (result, error) = await ogts.load_test_file("SettingsWithBadBackingName.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/pushGraph": "OmniGraph",
                "/pushGraph/NoOp": "OmniGraphNode",
                "/pushGraph/computegraphSettings": "ComputeGraphSettings",
            },
            ["/pushGraph/computegraphSettings"],
        )
        self.assertEqual([], results)
        results = _verify_graph_settings(
            "/pushGraph",
            {
                "evaluator:type": "push",
                "fileFormatVersion": CURRENT_FORMAT_VERSION,
                "fabricCacheBacking": "StageWithHistory",
                "pipelineStage": "pipelineStagePreRender",
                "evaluationMode": "Automatic",
            },
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_with_graph_post_schema(self):
        """Test that an updated file with a graph and a node is read safely"""
        (result, error) = await ogts.load_test_file("SettingsWithGraph_postSchema.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents({"/pushGraph": "OmniGraph", "/pushGraph/NoOp": "OmniGraphNode"})
        self.assertEqual([], results)
        results = _verify_graph_settings(
            "/pushGraph",
            {
                "evaluator:type": "push",
                "fileFormatVersion": CURRENT_FORMAT_VERSION,
                "fabricCacheBacking": "StageWithHistory",
                "pipelineStage": "pipelineStagePreRender",
                "evaluationMode": "Automatic",
            },
        )
        self.assertEqual([], results)


# ==============================================================================================================
class TestSettingsPreservation(ogts.OmniGraphTestCase):
    """Wrapper for tests to confirm old files can still be safely loaded"""

    # ----------------------------------------------------------------------
    async def test_no_settings_1_1(self):
        """Test that a v1.1 file with a graph and no settings is read safely"""
        (result, error) = await ogts.load_test_file("SettingsMissingFromGraph_v1_1.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/defaultGraph": "OmniGraph",
            }
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_no_graph_1_1(self):
        """Test that a v1.1 file with a scene with a global implicit graph is read safely"""
        (result, error) = await ogts.load_test_file("SettingsWithoutGraph_v1_1.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/__graphUsingSchemas/computegraphSettings": "ComputeGraphSettings",
                "/__graphUsingSchemas/NoOp": "OmniGraphNode",
                "/__graphUsingSchemas": "OmniGraph",
            }
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_with_graph_1_1(self):
        """Test that a v1.1 file with a graph and settings is read safely"""
        (result, error) = await ogts.load_test_file("SettingsWithGraph_v1_1.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        results = _verify_stage_contents(
            {
                "/pushGraph": "OmniGraph",
                "/pushGraph/computegraphSettings": "ComputeGraphSettings",
                "/pushGraph/NoOp": "OmniGraphNode",
            }
        )
        self.assertEqual([], results)

    # ----------------------------------------------------------------------
    async def test_with_bad_connections(self):
        """Test that a file with old prims fails migration"""
        (result, error) = await ogts.load_test_file("SettingsWithBadConnections.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)

        stage = omni.usd.get_context().get_stage()

        graph_prim = stage.GetPrimAtPath("/pushGraph")
        self.assertTrue(graph_prim.IsValid())
        self.assertEqual("OmniGraph", graph_prim.GetTypeName())

        settings_prim = stage.GetPrimAtPath("/pushGraph/computegraphSettings")
        self.assertTrue(settings_prim.IsValid())
        self.assertEqual("ComputeGraphSettings", settings_prim.GetTypeName())

        node_prim = stage.GetPrimAtPath("/pushGraph/BundleInspector")
        self.assertTrue(node_prim.IsValid())
        self.assertEqual("OmniGraphNode", node_prim.GetTypeName())
