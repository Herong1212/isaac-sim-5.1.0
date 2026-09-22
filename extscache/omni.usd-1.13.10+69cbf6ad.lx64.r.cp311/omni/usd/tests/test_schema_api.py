# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.test
import omni.usd

from pxr import Usd, UsdGeom, Gf, Sdf


class TestSchemaAPI(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()
        self.context = omni.usd.get_context()

    async def tearDown(self):
        pass

    async def test_add_schema_api(self):
        # Create a test prim
        sphere = UsdGeom.Sphere.Define(self.stage, "/TestSphere")
        cube = UsdGeom.Cube.Define(self.stage, "/TestCube")

        # Create a list of prims to test
        test_prims = [sphere.GetPrim(), cube.GetPrim()]

        # Test appending UsdGeomModelAPI schema
        schema_reg = Usd.SchemaRegistry()
        (api_schema, api_instance) = schema_reg.GetTypeNameAndInstance("GeomModelAPI")
        omni.kit.commands.execute("AppendAPIToPrims",
                                  paths=[p.GetPath().pathString for p in test_prims],
                                  api_schema=api_schema,
                                  api_instance=api_instance,
                                )

        # Verify the API schema was applied to both prims
        for prim in test_prims:
            # Check if the API schema is in the applied API schemas
            applied_schemas = prim.GetAppliedSchemas()
            self.assertIn("GeomModelAPI", applied_schemas)

            # Verify we can access the API schema
            model_api = UsdGeom.ModelAPI(prim)
            self.assertTrue(model_api)

        # Test undo
        omni.kit.undo.undo()

        # Verify the API schema was removed
        for prim in test_prims:
            applied_schemas = prim.GetAppliedSchemas()
            self.assertNotIn("GeomModelAPI", applied_schemas)

        # Test redo
        omni.kit.undo.redo()

        # Verify the API schema was reapplied
        for prim in test_prims:
            applied_schemas = prim.GetAppliedSchemas()
            self.assertIn("GeomModelAPI", applied_schemas)

        # Test undo
        omni.kit.undo.undo()

        # Verify the API schema was removed
        for prim in test_prims:
            applied_schemas = prim.GetAppliedSchemas()
            self.assertNotIn("GeomModelAPI", applied_schemas)

    async def test_add_schema_api_instance(self):
        # Create a test prim
        sphere = UsdGeom.Sphere.Define(self.stage, "/TestSphere")
        cube = UsdGeom.Cube.Define(self.stage, "/TestCube")

        # Create a list of prims to test
        test_prims = [sphere.GetPrim(), cube.GetPrim()]

        # Test appending UsdGeomModelAPI schema
        schema_reg = Usd.SchemaRegistry()
        (api_schema, api_instance) = schema_reg.GetTypeNameAndInstance("CollectionAPI:shadowLink")
        omni.kit.commands.execute("AppendAPIToPrims",
                                  paths=[p.GetPath().pathString for p in test_prims],
                                  api_schema=api_schema,
                                  api_instance=api_instance,
                                )

        # Verify the API schema was applied to both prims
        for prim in test_prims:
            # Check if the API schema is in the applied API schemas
            applied_schemas = prim.GetAppliedSchemas()
            self.assertIn("CollectionAPI:shadowLink", applied_schemas)

        # Test undo
        omni.kit.undo.undo()

        # Verify the API schema was removed
        for prim in test_prims:
            applied_schemas = prim.GetAppliedSchemas()
            self.assertNotIn("CollectionAPI:shadowLink", applied_schemas)

        # Test redo
        omni.kit.undo.redo()

        # Verify the API schema was reapplied
        for prim in test_prims:
            applied_schemas = prim.GetAppliedSchemas()
            self.assertIn("CollectionAPI:shadowLink", applied_schemas)

        # Test undo
        omni.kit.undo.undo()

        # Verify the API schema was removed
        for prim in test_prims:
            applied_schemas = prim.GetAppliedSchemas()
            self.assertNotIn("CollectionAPI:shadowLink", applied_schemas)
     
    async def test_remove_schema_api(self):
            # Create test prims
            sphere = UsdGeom.Sphere.Define(self.stage, "/TestSphere")
            cube = UsdGeom.Cube.Define(self.stage, "/TestCube")
            test_prims = [sphere.GetPrim(), cube.GetPrim()]

            # First add the API schema to test prims
            schema_reg = Usd.SchemaRegistry()
            (api_schema, api_instance) = schema_reg.GetTypeNameAndInstance("GeomModelAPI")
            omni.kit.commands.execute("AppendAPIToPrims",
                                    paths=[p.GetPath().pathString for p in test_prims],
                                    api_schema=api_schema,
                                    api_instance=api_instance)

            # Verify the API schema was initially applied
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertIn("GeomModelAPI", applied_schemas)

            # Test removing the API schema
            omni.kit.commands.execute("RemoveAPIFromPrims",
                                    paths=[p.GetPath().pathString for p in test_prims],
                                    api_schema=api_schema,
                                    api_instance=api_instance)

            # Verify the API schema was removed from both prims
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertNotIn("GeomModelAPI", applied_schemas)

            # Test undo
            omni.kit.undo.undo()

            # Verify the API schema was restored
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertIn("GeomModelAPI", applied_schemas)

            # Test redo
            omni.kit.undo.redo()

            # Verify the API schema was removed again
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertNotIn("GeomModelAPI", applied_schemas)

            # Test undo
            omni.kit.undo.undo()

            # Verify the API schema was restored
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertIn("GeomModelAPI", applied_schemas)


    async def test_remove_schema_api_instance(self):
            # Create test prims
            sphere = UsdGeom.Sphere.Define(self.stage, "/TestSphere")
            cube = UsdGeom.Cube.Define(self.stage, "/TestCube")
            test_prims = [sphere.GetPrim(), cube.GetPrim()]

            # First add the API schema to test prims
            schema_reg = Usd.SchemaRegistry()
            (api_schema, api_instance) = schema_reg.GetTypeNameAndInstance("CollectionAPI:shadowLink")
            omni.kit.commands.execute("AppendAPIToPrims",
                                    paths=[p.GetPath().pathString for p in test_prims],
                                    api_schema=api_schema,
                                    api_instance=api_instance)

            # Verify the API schema was initially applied
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertIn("CollectionAPI:shadowLink", applied_schemas)

            # Test removing the API schema
            omni.kit.commands.execute("RemoveAPIFromPrims",
                                    paths=[p.GetPath().pathString for p in test_prims],
                                    api_schema=api_schema,
                                    api_instance=api_instance)

            # Verify the API schema was removed from both prims
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertNotIn("CollectionAPI:shadowLink", applied_schemas)

            # Test undo
            omni.kit.undo.undo()

            # Verify the API schema was restored
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertIn("CollectionAPI:shadowLink", applied_schemas)

            # Test redo
            omni.kit.undo.redo()

            # Verify the API schema was removed again
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertNotIn("CollectionAPI:shadowLink", applied_schemas)

            # Test undo
            omni.kit.undo.undo()

            # Verify the API schema was restored
            for prim in test_prims:
                applied_schemas = prim.GetAppliedSchemas()
                self.assertIn("CollectionAPI:shadowLink", applied_schemas)

