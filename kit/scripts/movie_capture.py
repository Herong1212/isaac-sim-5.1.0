import carb
import argparse
import omni.usd
from omni.kit.viewport.utility import get_active_viewport
from pxr import Sdf, Usd
import omni.graph.core as og

basePath = ""
viewportId = 0
baseFilename = ""
inflightFileIO = 0
renderProductPath = ""
rpPrimPathPostFix = "_MovieRecord_Script"
ogNodePath = "/Pipeline"


def create_tmp_render_product(curr_rp_prim_path):
    # if the current rendering product is our current movie record prim then
    # this is a sequence capture and don't need to create a new prim
    #
    # Otherwise, we delete previous tmp render product if it exists
    # and create a new one
    stage = omni.usd.get_context().get_stage()
    if rpPrimPathPostFix in curr_rp_prim_path:
        set_active_in_omnigraph(stage, curr_rp_prim_path, curr_rp_prim_path, curr_rp_prim_path + ogNodePath)
        return (curr_rp_prim_path, curr_rp_prim_path + ogNodePath)

    session_layer = stage.GetSessionLayer()
    with Usd.EditContext(stage, session_layer):
        new_rp_prim_path = curr_rp_prim_path + rpPrimPathPostFix
        base_og_path = new_rp_prim_path + ogNodePath
        remove_existing_graph(stage, new_rp_prim_path, base_og_path)
        omni.kit.commands.execute("CopyPrim", path_from=curr_rp_prim_path, path_to=new_rp_prim_path, exclusive_select=False)
        omni.usd.editor.set_hide_in_stage_window(stage.GetPrimAtPath(new_rp_prim_path), True)
        omni.usd.editor.set_no_delete(stage.GetPrimAtPath(new_rp_prim_path), False)
        stage.GetPrimAtPath(new_rp_prim_path).CreateAttribute("ogPostProcessPath", Sdf.ValueTypeNames.String).Set(base_og_path)

        create_omnigraph_nodes(stage, curr_rp_prim_path, new_rp_prim_path, base_og_path)

        return (new_rp_prim_path, base_og_path)


def set_active_in_omnigraph(stage, curr_rp_prim_path, rp_prim_path, og_prim_path):
    global baseFilename

    session_layer = stage.GetSessionLayer()
    with Usd.EditContext(stage, session_layer):
        wrapped_graph = get_or_create_graph(stage, rp_prim_path, og_prim_path)

        aovs = get_aov_list(stage, curr_rp_prim_path)
        for aov in aovs:
            cpu_to_disk_node_path = og_prim_path + "/GpuInteropCpuToDisk" + "_" + aov
            cpu_to_disk_prim_node = wrapped_graph.get_node(cpu_to_disk_node_path)
            if cpu_to_disk_prim_node:
                cpu_to_disk_prim_inputs_active_attr = cpu_to_disk_prim_node.get_attribute("inputs:active")
                og.Controller.set(cpu_to_disk_prim_inputs_active_attr, True)

                cpu_to_disk_prim_inputs_fileType_attr = cpu_to_disk_prim_node.get_attribute("inputs:fileName")
                og.Controller.set(cpu_to_disk_prim_inputs_fileType_attr, baseFilename)


def create_omnigraph_nodes(stage, curr_rp_prim_path, rp_prim_path, og_prim_path):
    global basePath
    global viewportId
    global baseFilename
    global renderProductPath
    global inflightFileIO

    wrapped_graph = get_or_create_graph(stage, rp_prim_path, og_prim_path)

    session_layer = stage.GetSessionLayer()
    with Usd.EditContext(stage, session_layer):

        og.cmds.CreateNode(graph=wrapped_graph,
                           node_path=og_prim_path + "/GpuInteropRenderProductEntry",
                           node_type="omni.graph.nodes.GpuInteropRenderProductEntry", create_usd=True)
        entry_prim_node = wrapped_graph.get_node(og_prim_path + "/GpuInteropRenderProductEntry")
        entry_prim_rp_attr = entry_prim_node.get_attribute("outputs:rp")
        entry_prim_gpu_attr = entry_prim_node.get_attribute("outputs:gpu")

        aovs = get_aov_list(stage, curr_rp_prim_path)
        for aov in aovs:
            gpu_to_cpu_node_path = og_prim_path + "/GpuInteropGpuToCpuCopy" + "_" + aov
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

            cpu_to_disk_node_path = og_prim_path + "/GpuInteropCpuToDisk" + "_" + aov
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

            cpu_to_disk_prim_inputs_active_attr = cpu_to_disk_prim_node.get_attribute("inputs:active")
            og.Controller.set(cpu_to_disk_prim_inputs_active_attr, True)

            cpu_to_disk_prim_inputs_saveLocation_attr = cpu_to_disk_prim_node.get_attribute("inputs:saveLocation")
            og.Controller.set(cpu_to_disk_prim_inputs_saveLocation_attr, basePath)

            cpu_to_disk_prim_inputs_fileType_attr = cpu_to_disk_prim_node.get_attribute("inputs:fileType")
            if "exr" in baseFilename.lower():
                og.Controller.set(cpu_to_disk_prim_inputs_fileType_attr, "exr")
            else:
                og.Controller.set(cpu_to_disk_prim_inputs_fileType_attr, "png")

            cpu_to_disk_prim_inputs_fileType_attr = cpu_to_disk_prim_node.get_attribute("inputs:fileName")
            og.Controller.set(cpu_to_disk_prim_inputs_fileType_attr, baseFilename)

            cpu_to_disk_prim_inputs_inflightFileIO_attr = cpu_to_disk_prim_node.get_attribute("inputs:maxInflightWrites")
            og.Controller.set(cpu_to_disk_prim_inputs_inflightFileIO_attr, inflightFileIO)


def get_aov_list(stage, primPath):
    aovs = []
    renderVars = stage.GetPrimAtPath(primPath).GetRelationship("orderedVars").GetForwardedTargets()
    for renderVar in renderVars:
        aovName = stage.GetPrimAtPath(renderVar).GetAttribute("sourceName").Get()
        aovs.append(aovName)
    return aovs


def remove_existing_graph(stage, rp_prim_path, og_prim_path):
    graph = og.get_graph_by_path(og_prim_path)
    if graph:
        nodes = graph.get_nodes()
        for node in nodes:
            og.cmds.DeleteNode(graph=graph, node_path=node.get_prim_path(), modify_usd=True)
    old_rp_prim = stage.GetPrimAtPath(rp_prim_path)
    if old_rp_prim:
        omni.usd.editor.set_no_delete(old_rp_prim, False)
        omni.kit.commands.execute("DeletePrims", paths=[rp_prim_path])


def get_or_create_graph(stage, rp_prim_path, primPath):
    graph = og.get_graph_by_path(primPath)
    if graph:
        return graph
    else:
        orchestration_graphs = og.get_global_orchestration_graphs_in_pipeline_stage(og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_POSTRENDER)
        orchestration_graph = orchestration_graphs[0]
        (result, wrapper_node) = og.cmds.CreateGraphAsNode(
            graph=orchestration_graph,
            node_name="Pipeline",
            graph_path=primPath,
            evaluator_name="push",
            is_global_graph=True,
            backed_by_usd=True,
            fc_backing_type=og.GraphBackingType.GRAPH_BACKING_TYPE_FABRIC_SHARED,
            pipeline_stage=og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_POSTRENDER)
        return wrapper_node.get_wrapped_graph()


def attach_post_process_save_to_disk():
    try:
        global viewportId

        # [TODO] map viewportId to proper window rather than defaultWindow
        viewport_api = get_active_viewport()
        if viewport_api:
            currentRpPrimPath = viewport_api.render_product_path
            (rp_prim_path, og_prim_path) = create_tmp_render_product(currentRpPrimPath)
            viewport_api.render_product_path = rp_prim_path
            carb.log_info(f"Render product capture with {currentRpPrimPath} -> {rp_prim_path}.")
        else:
            carb.log_warn("Render product capture failed due to unable to get Viewport interface.")

    except Exception as e:
        carb.log_warn(str(e))


def main():
    global basePath
    global baseFilename
    global renderProductPath
    global viewportId
    global inflightFileIO

    parser = argparse.ArgumentParser()
    parser.add_argument("--viewportId", help="Viewport window name", required=True)
    parser.add_argument("--baseFilename", help="Base filename for output images", required=True)
    parser.add_argument("--basePath", help="Base path to save output images", required=True)
    parser.add_argument("--renderProduct", help="Render product prim path containing renderVars", required=True)
    parser.add_argument("--inflightFileIO", type=int, help="Number of inflight file save operations per node", default=2)

    try:
        options = parser.parse_args()
        basePath = options.basePath
        viewportId = options.viewportId
        baseFilename = options.baseFilename
        inflightFileIO = options.inflightFileIO
        renderProductPath = options.renderProduct
        attach_post_process_save_to_disk()
    except Exception as e:
        carb.log_warn(str(e))


if __name__ == "__main__":
    main()
