import copy

import generic_model_output as gmo_utils
import numpy as np
import omni.sensors.nv.lidar._lidar as lidar
import open3d as o3d
from omni.sensors.nv.lidar.scripts.LidarFWLoader import LidarFWLoader  # noqa: N813
from omni.sensors.nv.lidar.scripts.LidarUtilities import PCGeneratorConfig, generate_pc_from_file  # noqa: N813

source_temp = None
target_temp = None


HeaderType = np.dtype(
    [("containerID", np.uint32), ("version", np.uint32), ("hostEndTime", np.uint64), ("pointCount", np.uint32)]
)


def load_lidar_eval_sweep_file(filename):
    # header = np.fromfile(filename, dtype=HeaderType, count=1)
    return np.fromfile(filename, dtype=np.dtype((np.float32, (4))), offset=HeaderType.itemsize)


def rmse(measured, truth):
    return np.linalg.norm(measured - truth) / np.sqrt(len(truth))


def draw_registration_result(source, target, transformation):
    def draw_source(vis):
        source_temp.points = copy.deepcopy(source.points)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.clear()
        vis.update_geometry(source_temp)
        vis.update_geometry(target_temp)
        vis.poll_events()
        vis.update_renderer()
        return False

    def draw_target(vis):
        target_temp.points = copy.deepcopy(target.points)
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        source_temp.clear()
        vis.update_geometry(source_temp)
        vis.update_geometry(target_temp)
        vis.poll_events()
        vis.update_renderer()
        return False

    def draw_icp_result(vis):
        source_temp.points = copy.deepcopy(source.points)
        target_temp.points = copy.deepcopy(target.points)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        source_temp.transform(transformation)

        vis.update_geometry(source_temp)
        vis.update_geometry(target_temp)

        vis.poll_events()
        vis.update_renderer()
        return False

    def change_background_to_black(vis):
        opt = vis.get_render_option()
        opt.background_color = np.asarray([0, 0, 0])
        return False

    key_to_callback = {
        ord("S"): draw_source,
        ord("T"): draw_target,
        ord("C"): draw_icp_result,
        ord("K"): change_background_to_black,
    }

    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)

    o3d.visualization.draw_geometries_with_key_callbacks([source_temp, target_temp], key_to_callback)


def geto3dpc(pc1):
    source = o3d.geometry.PointCloud()
    source.points = o3d.utility.Vector3dVector(pc1[:, 0:3])
    source.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    return source


def doicp(pc1, pc2, threshold, htminit, draw=False):
    source = geto3dpc(pc1)
    target = geto3dpc(pc2)

    evaluation = o3d.pipelines.registration.evaluate_registration(source, target, threshold, htminit)
    # print(evaluation)

    reg_p2l = o3d.pipelines.registration.registration_icp(
        source, target, threshold, htminit, o3d.pipelines.registration.TransformationEstimationPointToPlane()
    )

    if draw:
        draw_registration_result(source, target, reg_p2l.transformation)

    return reg_p2l


def computep2pdistance(pc1, pc2):
    source = geto3dpc(pc1)
    target = geto3dpc(pc2)
    dists = source.compute_point_cloud_distance(target)
    dists = np.asarray(dists)
    # print("median distance of correspondences: ", np.median(dists))
    # print("mean distance of correspondences: ", np.mean(dists))
    return np.mean(dists)


def computeintensitymetrics(pc1, pc2, reg_p2l):
    correspondences = np.asarray(reg_p2l.correspondence_set)
    # print("RMSE of intensities: ", rmse(pc1[correspondences[:, 0], 3], pc2[correspondences[:, 1], 3]))


def computenormalmetrics(pc1, pc2, reg_p2l):
    source = geto3dpc(pc1)
    target = geto3dpc(pc2)
    normals1 = np.asarray(source.normals)
    normals2 = np.asarray(target.normals)
    correspondences = np.asarray(reg_p2l.correspondence_set)
    # print("RMSE of normals: ", rmse(normals1[correspondences[:, 0], :], normals2[correspondences[:, 1], :]))
    return rmse(normals1[correspondences[:, 0], :], normals2[correspondences[:, 1], :])


def computetrafometric(reg_p2l):
    # print("Error of trafomatrix: ", error)
    return np.linalg.norm(np.asarray(reg_p2l.transformation) - np.eye(4))


def correspondencemetric(thruthpc, reg_p2l):
    correspondences = np.asarray(reg_p2l.correspondence_set)
    # print(
    #     "Number of points in GT: {0}, Num correspondences found: {1}, fraction: {2}".format(
    #         thruthpc.shape[0], correspondences.shape[0], float(correspondences.shape[0]) / thruthpc.shape[0]
    #     )
    # )
    return float(correspondences.shape[0]) / float(thruthpc.shape[0])


def getpcfromcsv(filename):
    pc = np.genfromtxt(filename, skip_header=1, delimiter=",")
    return pc[np.where(pc[:, 4] > 0.01)[0], :]


def getpcfromsweep(filename):
    pc = load_lidar_eval_sweep_file(filename)
    range_array = np.linalg.norm(pc[:, 0:3], axis=1)
    return pc[np.where(range_array > 0.01)[0], :]


# xyzi
def get_numpy_points(pc):
    points = np.asarray([pc.x, pc.y, pc.z, pc.scalar]).T
    return np.delete(points, np.asarray(pc.flags != gmo_utils.ElementFlags.VALID), 0)


def calculate_metrics_for_npy_points(npc_new, npc_ref):
    distance_metric = computep2pdistance(npc_new, npc_ref)
    htminit = np.asarray([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    reg_p2l = doicp(npc_new, npc_ref, 0.1, htminit)
    # normal_metric = computenormalmetrics(npc_new, npc_ref, reg_p2l)
    trafo_metric = computetrafometric(reg_p2l)
    corr_metric = 1.0 - correspondencemetric(npc_ref, reg_p2l)
    return distance_metric, trafo_metric, corr_metric


def compare_lidar_bin_files(bin_file, ref_file, group_name, client_name_new, client_name_ref):
    cfg_new = PCGeneratorConfig(bin_file)
    cfg_new.cfg.mode = lidar.LidarPCConverterMode.GENERIC_FILE
    cfg_new.cfg.desiredCoordsType = gmo_utils.CoordsType.CARTESIAN
    cfg_new.cfg.groupName = group_name
    cfg_new.cfg.clientName = client_name_new
    cfg_ref = PCGeneratorConfig(ref_file)
    cfg_ref.cfg.mode = lidar.LidarPCConverterMode.GENERIC_FILE
    cfg_new.cfg.desiredCoordsType = gmo_utils.CoordsType.CARTESIAN
    cfg_new.cfg.groupName = group_name
    cfg_ref.cfg.clientName = client_name_ref
    gen_new = generate_pc_from_file(cfg_new)
    gen_ref = generate_pc_from_file(cfg_ref)
    # max 10 pcs should be enough
    num_pcs = 0

    sum_distance_metric = 0.0
    # sum_normal_metric = 0. Not in the first round
    sum_trafo_metric = 0.0
    sum_corr_metric = 0.0
    num_points_metric = 0.0
    for i in range(0, 10):
        pc_new = next(gen_new, None)
        pc_ref = next(gen_ref, None)
        if pc_new is None or pc_ref is None:
            break
        valid_new_elements = np.sum(np.asarray(pc_new.flags == gmo_utils.ElementFlags.VALID))
        valid_ref_elements = np.sum(np.asarray(pc_ref.flags == gmo_utils.ElementFlags.VALID))
        if valid_new_elements == 0 or valid_ref_elements == 0:
            continue
        num_pcs = i + 1
        npc_new = get_numpy_points(pc_new)
        npc_ref = get_numpy_points(pc_ref)
        distance_metric = computep2pdistance(npc_new, npc_ref)

        htminit = np.asarray([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
        reg_p2l = doicp(npc_new, npc_ref, 0.1, htminit)

        trafo_metric = computetrafometric(reg_p2l)
        corr_metric = 1.0 - correspondencemetric(npc_ref, reg_p2l)

        num_points_scale = np.abs(1.0 - (float(valid_ref_elements) / float(valid_new_elements)))
        num_points_metric = 1000.0 if num_points_scale > 0.1 else 0.0
        # add to sum
        sum_distance_metric += distance_metric
        sum_trafo_metric += trafo_metric
        sum_corr_metric += corr_metric
    result = 1000.0
    if num_pcs > 0:
        # build mean by dividing through num_pcs
        sum_distance_metric /= num_pcs
        # sum_normal_metric /= num_pcs
        sum_trafo_metric /= num_pcs
        sum_corr_metric /= num_pcs
        # build combined value of metrics
        result = (sum_distance_metric + sum_trafo_metric + sum_corr_metric) / 3.0
        result += num_points_metric  # If number of points is super different than it has to fail!
    # print("i: {0}: Result: {1} Distance Metric {2}, Trafo Metric {3}, Corr_Metric {4} \n".format(i,result, distance_metric,trafo_metric,corr_metric) ) # noqa: E501
    return result  # noqa: R504


if __name__ == "__main__":
    pass
    # import os
    # import sys
    # lidar_test_scripts_path = os.path.dirname(os.path.realpath(__file__)) + "/../tests"
    # sys.path.append(lidar_test_scripts_path)
    # loader = LidarFWLoader()

    # fileName1 = "/home/bnaujoks/git/sensors_second/_testdata/test_sensors/test_compute_stability_regressions/lidar.h5"
    # fileName2 = "/home/bnaujoks/git/sensors_second/source/tests/compute_stability/ref-lidar.h5"
    # print(compare_lidar_bin_files(fileName1, fileName2, "Lidar", "lidar_new", "lidar_ref"))

    # fileName1 = "/home/bnaujoks/Documents/Files/133333333.txt"
    # fileName2 = "/home/bnaujoks/Documents/Files/166666666.txt"
    # filename1 = "/home/bnaujoks/Downloads/ash/sim_10.0.csv"
    # filename2 = "/home/bnaujoks/Downloads/ash/lidarSweep_10.bin"

    # htminit = np.asarray([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])

    # pc1 = getpcfromcsv(filename1)
    # pc2 = getpcfromsweep(filename2)

    # computep2pdistance(pc1, pc2)
    # reg_p2l = doicp(pc1, pc2, 0.1, htminit, True)

    # computeintensitymetrics(pc1, pc2, reg_p2l)
    # computenormalmetrics(pc1, pc2, reg_p2l)
    # computetrafometric(reg_p2l)
    # correspondencemetric(pc2, reg_p2l)
    # print(reg_p2l)
