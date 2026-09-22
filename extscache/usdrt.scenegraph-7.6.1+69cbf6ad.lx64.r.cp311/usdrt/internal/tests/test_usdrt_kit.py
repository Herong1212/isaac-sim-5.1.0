import omni.kit.test
import omni.kit.app
import omni.usd

from usdrt import Usd, Rt, Sdf, Gf


class TestUsdrtKit(omni.kit.test.AsyncTestCase):

    async def test_no_background_fabric_topology_changes(self):
        """
        If at all possible, we should avoid making topological changes
        to Fabric in the course of rendering a frame without having
        a good reason to do so. If you change causes this test to fail,
        ask #omni-fabric for help to resolve it.
        """

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()
        stage_id = omni.usd.get_context().get_stage_id()
        usdrt_stage = Usd.Stage.Attach(stage_id)

        await omni.kit.app.get_app().next_update_async()
        cube = stage.DefinePrim("/cube", "Cube")

        await omni.kit.app.get_app().next_update_async()
        attrib = "size"
        selection = usdrt_stage.SelectPrims(
                require_applied_schemas=[],
                require_attrs=[
                    (Sdf.ValueTypeNames.Double, attrib, Usd.Access.ReadWrite),
                ],
                device=str("cpu"),
                want_paths=True,
            )

        for i in range(10):
            await omni.kit.app.get_app().next_update_async()
            # Fabric topology should not change just by moving to the next frame
            self.assertFalse(selection.PrepareForReuse())

