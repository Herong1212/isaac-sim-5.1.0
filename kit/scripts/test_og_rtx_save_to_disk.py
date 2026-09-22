import carb
import carb.eventdispatcher
import asyncio
import argparse
import omni.usd
from omni.kit.viewport.utility import get_active_viewport
from pxr import Sdf, Usd, UsdRender
import omni.graph.core as og

aovs = []
frameNo = 0
frameStart = 0
frameCount = 0
inflightFileIO = 0
saveFolder = ""
eventSubscription = None


def load_callback(result, err):
    if result:
        settings = carb.settings.get_settings()
        settings.set_bool("/rtx/directLighting/sampledLighting/enabled", False)

        resX, resY = settings.get("/app/window/width"), settings.get("/app/window/height")
        if resX and resY:
            get_active_viewport().resolution = (resX, resY)

        asyncio.ensure_future(create_render_product())
    else:
        carb.log_error("Usd stage file load failed")
        omni.kit.app.get_app().post_quit(-1)


async def do_shutdown():
    global eventSubscription
    omni.usd.get_context().close_stage(None)
    omni.kit.app.get_app().post_quit(0)
    eventSubscription = None


def on_rendering_event(e: carb.eventdispatcher.Event):
    global frameNo
    global frameStart
    global frameCount
    frameNo = e["frame_number"]
    if (frameNo > (frameStart + frameCount + 10)):
        asyncio.ensure_future(do_shutdown())


async def create_render_product():
    try:
        global frameNo
        global frameStart
        global frameCount
        global saveFolder
        global inflightFileIO
        global eventSubscription
        global aovs

        viewport = get_active_viewport()
        usd_context = viewport.usd_context

        stage = usd_context.get_stage()
        session_layer = stage.GetSessionLayer()

        await usd_context.next_frame_async(viewport)

        render_prod_src = "/Render/OmniverseKit/HydraTextures/omni_kit_widget_viewport_ViewportTexture_0"
        render_prod_dupe = "/Render/RenderProduct_Dupe"
        pipeline_path = f"{render_prod_dupe}/Pipeline"


        with Usd.EditContext(stage, session_layer):
            omni.kit.commands.execute("CopyPrim", path_from=render_prod_src, path_to=render_prod_dupe)
            # eventSubscription = None
            # await omni.kit.app.get_app().next_update_async()

            rp_dup_prim = stage.GetPrimAtPath(render_prod_dupe)
            rp_dup_prim.CreateAttribute("ogPostProcessPath", Sdf.ValueTypeNames.String).Set(pipeline_path)
            ordered_var_paths = []
            for aov in aovs:
                new_var = UsdRender.Var.Define(stage, f"/Render/Vars/{aov}")
                new_var.GetSourceNameAttr().Set(aov)
                ordered_var_paths.append(new_var.GetPrim().GetPath())

            ordered_vars = UsdRender.Product(rp_dup_prim).GetOrderedVarsRel()
            ordered_vars.SetTargets(ordered_var_paths)

            # Based off kit\source\extensions\omni.graph.ui\python\scripts\menu.py
            orchestration_graphs = og.get_global_orchestration_graphs_in_pipeline_stage(og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_POSTRENDER)
            orchestration_graph = orchestration_graphs[0]
            (result, wrapper_node) = og.cmds.CreateGraphAsNode(
                graph=orchestration_graph,
                node_name="Pipeline",
                graph_path=pipeline_path,
                evaluator_name="push",
                is_global_graph=True,
                backed_by_usd=True,
                fc_backing_type=og.GraphBackingType.GRAPH_BACKING_TYPE_FABRIC_SHARED,
                pipeline_stage=og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_POSTRENDER)
            # await omni.kit.app.get_app().next_update_async()

            wrapped_graph = wrapper_node.get_wrapped_graph()

            og.cmds.CreateNode(graph=wrapped_graph,
                               node_path=f"{pipeline_path}/GpuInteropRenderProductEntry",
                               node_type="omni.graph.nodes.GpuInteropRenderProductEntry", create_usd=True)
            entry_prim_node = wrapped_graph.get_node(f"{pipeline_path}/GpuInteropRenderProductEntry")
            entry_prim_rp_attr = entry_prim_node.get_attribute("outputs:rp")
            entry_prim_gpu_attr = entry_prim_node.get_attribute("outputs:gpu")

            for aov in aovs:
                gpu_to_cpu_node_path = f"{pipeline_path}/GpuInteropGpuToCpuCopy" + "_" + aov
                og.cmds.CreateNode(graph=wrapped_graph,
                                   node_path=gpu_to_cpu_node_path,
                                   node_type="omni.graph.examples.cpp.GpuInteropGpuToCpuCopy", create_usd=True)
                gpu_to_cpu_prim_node = wrapped_graph.get_node(gpu_to_cpu_node_path)
                gpu_to_cpu_prim_inputs_rp_attr = gpu_to_cpu_prim_node.get_attribute("inputs:rp")
                gpu_to_cpu_prim_inputs_gpu_attr = gpu_to_cpu_prim_node.get_attribute("inputs:gpu")
                og.cmds.ConnectAttrs(src_attr=entry_prim_rp_attr, dest_attr=gpu_to_cpu_prim_inputs_rp_attr, modify_usd=True)
                og.cmds.ConnectAttrs(src_attr=entry_prim_gpu_attr, dest_attr=gpu_to_cpu_prim_inputs_gpu_attr, modify_usd=True)
                gpu_to_cpu_prim_outputs_rp_attr = gpu_to_cpu_prim_node.get_attribute("outputs:rp")
                gpu_to_cpu_prim_outputs_gpu_attr = gpu_to_cpu_prim_node.get_attribute("outputs:gpu")
                gpu_to_cpu_prim_outputs_aovCpu_attr = gpu_to_cpu_prim_node.get_attribute("outputs:aovCpu")

                gpu_to_cpu_prim_inputs_aov_attr = gpu_to_cpu_prim_node.get_attribute("inputs:aovGpu")
                og.Controller.set(gpu_to_cpu_prim_inputs_aov_attr, str(aov))

                cpu_to_disk_node_path = f"{pipeline_path}/GpuInteropCpuToDisk" + "_" + aov
                og.cmds.CreateNode(graph=wrapped_graph,
                                   node_path=cpu_to_disk_node_path,
                                   node_type="omni.graph.examples.cpp.GpuInteropCpuToDisk", create_usd=True)
                cpu_to_disk_prim_node = wrapped_graph.get_node(cpu_to_disk_node_path)
                cpu_to_disk_prim_inputs_rp_attr = cpu_to_disk_prim_node.get_attribute("inputs:rp")
                cpu_to_disk_prim_inputs_gpu_attr = cpu_to_disk_prim_node.get_attribute("inputs:gpu")
                cpu_to_disk_prim_inputs_aovCpu_attr = cpu_to_disk_prim_node.get_attribute("inputs:aovCpu")
                og.cmds.ConnectAttrs(src_attr=gpu_to_cpu_prim_outputs_rp_attr, dest_attr=cpu_to_disk_prim_inputs_rp_attr, modify_usd=True)
                og.cmds.ConnectAttrs(src_attr=gpu_to_cpu_prim_outputs_gpu_attr, dest_attr=cpu_to_disk_prim_inputs_gpu_attr, modify_usd=True)
                og.cmds.ConnectAttrs(src_attr=gpu_to_cpu_prim_outputs_aovCpu_attr, dest_attr=cpu_to_disk_prim_inputs_aovCpu_attr, modify_usd=True)

                cpu_to_disk_prim_inputs_aov_attr = cpu_to_disk_prim_node.get_attribute("inputs:aovGpu")
                og.Controller.set(cpu_to_disk_prim_inputs_aov_attr, str(aov))

                cpu_to_disk_prim_inputs_startFrame_attr = cpu_to_disk_prim_node.get_attribute("inputs:startFrame")
                og.Controller.set(cpu_to_disk_prim_inputs_startFrame_attr, frameStart)

                cpu_to_disk_prim_inputs_frameCount_attr = cpu_to_disk_prim_node.get_attribute("inputs:frameCount")
                og.Controller.set(cpu_to_disk_prim_inputs_frameCount_attr, frameCount)

                cpu_to_disk_prim_inputs_saveLocation_attr = cpu_to_disk_prim_node.get_attribute("inputs:saveLocation")
                og.Controller.set(cpu_to_disk_prim_inputs_saveLocation_attr, saveFolder)

                cpu_to_disk_prim_inputs_fileType_attr = cpu_to_disk_prim_node.get_attribute("inputs:fileType")
                if aov == "HdrColor":
                    og.Controller.set(cpu_to_disk_prim_inputs_fileType_attr, "exr")
                else:
                    og.Controller.set(cpu_to_disk_prim_inputs_fileType_attr, "png")

                cpu_to_disk_prim_inputs_inflightFileIO_attr = cpu_to_disk_prim_node.get_attribute("inputs:maxInflightWrites")
                og.Controller.set(cpu_to_disk_prim_inputs_inflightFileIO_attr, inflightFileIO)

        viewport.render_product_path = render_prod_dupe

    except Exception as e:
        carb.log_error(str(e))
        omni.kit.app.get_app().post_quit(-1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to USD stage", required=True)
    parser.add_argument("--aovs", nargs='+', default=[], help="List of AOVs to capture (i.e LdrColor)", required=True)
    parser.add_argument("--frameCount", type=int, help="Number of frames to capture", required=True)
    parser.add_argument("--frameStart", type=int, help="Frame number when capture to disk begins", required=True)
    parser.add_argument("--saveFolder", help="Path to folder to save images", required=True)
    parser.add_argument("--inflightFileIO", type=int, help="Number of inflight file save operations per node", default=2)

    try:
        global aovs
        global frameStart
        global frameCount
        global saveFolder
        global inflightFileIO
        global eventSubscription

        options = parser.parse_args()
        context = omni.usd.get_context()
        aovs = options.aovs
        frameCount = options.frameCount
        frameStart = options.frameStart
        saveFolder = options.saveFolder
        inflightFileIO = options.inflightFileIO
        context.open_stage_with_callback(options.file, load_callback)
        eventSubscription = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=context.stage_rendering_event_name(omni.usd.StageRenderingEventType.NEW_FRAME, True),
            on_event=on_rendering_event,
            observer_name="test_og_rtx_save_to_disk"
        )
    except Exception as e:
        carb.log_error(str(e))
        omni.kit.app.get_app().post_quit(-1)


if __name__ == "__main__":
    main()
