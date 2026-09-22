import carb
import omni.kit.test
from pxr import Usd
from usd.schema.sequence import get_instance


def sequence_schema_plugins_loaded():
    try:
        import SequenceSchema
    except ImportError:
        carb.log_warn("Could not import SequenceSchema.")
        return False

    def _getSchemaPrimDef(schema):
        isApi = Usd.SchemaRegistry().IsAppliedAPISchema(schema)
        schemaToken = (
            Usd.SchemaRegistry().GetAPISchemaTypeName(schema)
            if isApi
            else Usd.SchemaRegistry().GetConcreteSchemaTypeName(schema)
        )

        return (
            Usd.SchemaRegistry().FindAppliedAPIPrimDefinition(schemaToken)
            if isApi
            else Usd.SchemaRegistry().FindConcretePrimDefinition(schemaToken)
        )

    expected_prim_types = [
        SequenceSchema.Sequence,
        SequenceSchema.Track,
        SequenceSchema.AssetClip,
        SequenceSchema.ShotClip,
    ]

    for prim_type in expected_prim_types:
        if not _getSchemaPrimDef(prim_type):
            carb.log_warn(f"Could not find {prim_type}")
            return False
    return True


class UsdSequenceSchemaTests(omni.kit.test.AsyncTestCase):
    async def test_sequence_schema_plugins_loaded(self):
        self.assertTrue(sequence_schema_plugins_loaded())
        ext = get_instance()
        self.assertIsNotNone(ext)
        self.assertTrue(ext.plugins_registered)
