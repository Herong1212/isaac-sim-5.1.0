"""Test the value of the gpu_ptr_kind on attributes"""

import omni.graph.core as og
import omni.graph.core.tests as ogts


class TestGpuPtrKind(ogts.OmniGraphTestCase):
    async def test_gpu_ptr_kind(self):
        keys = og.Controller.Keys
        (_, (cpu_node, gpu_node), _, _) = og.Controller.edit("/TestGraph", {
            keys.CREATE_NODES: [
                ("CpuNode", "omni.syntheticdata.SdRenderVarToRawArray"),
                ("GpuNode", "omni.syntheticdata.SdLinearArrayToTexture")
            ]
        })

        cpu_attr = cpu_node.get_attribute("outputs:data")
        self.assertEqual(cpu_attr.gpu_ptr_kind, og.PtrToPtrKind.CPU)

        gpu_attr = gpu_node.get_attribute("inputs:data")
        self.assertEqual(gpu_attr.gpu_ptr_kind, og.PtrToPtrKind.GPU)
