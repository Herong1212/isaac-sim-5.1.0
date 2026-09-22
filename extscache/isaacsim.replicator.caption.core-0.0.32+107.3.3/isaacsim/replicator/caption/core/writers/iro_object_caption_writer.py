"""
This writer only works for IsaacSim.replicator.object. The writer class is inherited from the WorkerWriter class in the replicator core.
"""

import logging, os, asyncio

from omni.replicator.core import AnnotatorRegistry, BackendDispatch

import importlib

iro_module_name = "isaacsim.replicator.object"
IROSceneGraphWriter = None


# enable IRO functions when the module is available
try:
    iro_module = importlib.import_module(iro_module_name)
    misc_module = importlib.import_module(f"{iro_module_name}.utility.misc")
    simple_writer_module = importlib.import_module(f"{iro_module_name}.simple_writer")
    camera_module = importlib.import_module(f"{iro_module_name}.mutables.camera")
    WorkerWriter = getattr(simple_writer_module, "WorkerWriter")
    tentative_retrieve = getattr(misc_module, "tentative_retrieve")
    write_yaml = getattr(misc_module, "write_yaml")
    P = getattr(misc_module, "P")
    VERSION = getattr(misc_module, "VERSION")
    Camera_DEV = getattr(camera_module, "Camera_DEV")

    from omni.replicator.core.scripts import functional as F
    from omni.replicator.core import WriterRegistry

    from ..object_caption.generate_object_caption import GenObjectCap

    class IRObjectCaptionWriter(WorkerWriter):  # not workking because camera view is not iterating
        """
        Generates object captions for the USD files tracked by IRO.

        obj_caption_configs (dict): The configurations for object caption generation.
        scene (Scene): The scene object.
        annotators (list): The list of annotators to use for writing the scene.
        oro_metadata (dict): The metadata for the current frame.
        oro_index (int): The index of the current frame.
        global_metadata (dict): The global metadata for the scene.
        is_multi_camera (bool): Whether the scene has multiple cameras.
        camera_name_to_rp_name (dict): The mapping of camera names to replicator product names.
        gen_object_cap (GenObjectCap): The object caption generator.
        """

        def __init__(self, obj_caption_configs, scene):
            self._backend = BackendDispatch({"paths": {"out_dir": ""}})
            self.obj_caption_configs = obj_caption_configs
            self.scene = scene
            self.annotators = [
                AnnotatorRegistry.get_annotator("rgb"),
            ]

            self.oro_metadata = None
            self.oro_index = None

            self._frame_id = 0
            self.global_metadata = {}
            self.is_multi_camera = False
            self.camera_name_to_rp_name = None

            self.gen_object_cap = GenObjectCap(model_name=self.obj_caption_configs["model_name"])

        def write(self, data):
            """
            Writes the object caption for the current frame. And upload the caption to the database.

            data (dict): The collected writer data for the current frame.
                More details see https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/custom_writer.html.
            """
            self.oro_metadata = self.global_metadata.pop(self._frame_id)
            self.oro_index = self._frame_id

            # in multi-camera case, match rp names with camera names
            if self.is_multi_camera and self.camera_name_to_rp_name is None:
                self.camera_name_to_rp_name = {}
                for key in data:
                    if key.startswith("rp_Replicator"):
                        rp_name = key[3:]
                        replicator_camera_path = data[key]["camera"]
                        camera_name = replicator_camera_path[
                            len("/Replicator/Camera_") : replicator_camera_path.find("_Xform/Camera_")
                        ]
                        self.camera_name_to_rp_name[camera_name] = rp_name

            with P(f"write {self.oro_index}"):

                at_least_one_visible_tracked_mutable = False
                for mutable in self.scene.mutables.values():
                    if isinstance(mutable, Camera_DEV):
                        if self.is_multi_camera:
                            mutable.rp_name = self.camera_name_to_rp_name[mutable.name]

                        output_name = tentative_retrieve(
                            "output_name", self.oro_metadata, str, f'{self.oro_metadata["seed"]}_{mutable.name}'
                        )

                        output_name = output_name.replace("$(camera_name)", mutable.name).replace(
                            "$(camera_index)", str(mutable.ref_index)
                        )

                        image = mutable.capture_image_only(data)

                        if self.scene.output_switches["images"]:
                            output_path = f"{self.scene.output_path}/images/{output_name}.jpg"
                            message = f"[METROPERF]: frame saved at {output_path}, [{self.oro_index + 1}/{self.scene.num_frames}]"
                            logging.info(message)
                            print(message)
                            self._backend.write_image(f"{output_path}", image)

                        if self.scene.progress_bar is not None:
                            self.scene.progress_bar.model.set_value((self.oro_index + 1) / self.scene.num_frames)

                # if nothing is tracked, don't write  xxx
                if tentative_retrieve("skip_frames_with_no_visible_tracked_mutables", self.oro_metadata, bool, False):
                    if not at_least_one_visible_tracked_mutable:
                        self._frame_id += 1
                        return

                output_name_global = tentative_retrieve(
                    "output_name", self.oro_metadata, str, f'{self.oro_metadata["seed"]}'
                )
                output_name_global = output_name_global.replace("$(camera_name)", "GLOBAL").replace(
                    "$(camera_index)", "GLOBAL"
                )
                metadata_with_header = {
                    "isaacsim.replicator.object": {
                        "version": VERSION,
                    }
                }

                metadata_with_header["isaacsim.replicator.object"].update(self.oro_metadata)
                if self.scene.output_switches["descriptions"]:
                    metadata_with_header["isaacsim.replicator.object"][
                        "output_path"
                    ] += "__NEXT"  # convenience for restoration
                    write_yaml(metadata_with_header, f"{self.scene.output_path}/descriptions/{output_name_global}.yaml")

                if self.scene.output_switches["object_caption"]:
                    prim_path = self.oro_metadata["mesh_0"]["usd_path"]  # read from metadata
                    image_names = [
                        f'{self.oro_metadata["seed"]}_camera_{i}.jpg' for i in range(1, 5)
                    ]  #  Assumption: no output name in metadata !
                    image_paths = [
                        os.path.join(self.scene.output_path, "images", image_name) for image_name in image_names
                    ]
                    try:
                        asyncio.run(self.gen_object_cap.run(prim_usd_path=prim_path, image_paths=image_paths))
                    except Exception as e:
                        raise Exception(f"Error in object caption generation: {e}")

            self._frame_id += 1

    print("[INFO] Register IRObjectCaptionWriter to the WriterRegistry")
    # registry it when the IRO module is available
    WriterRegistry.register(IRObjectCaptionWriter)

except ImportError as e:
    # placeholder for the case when the IRO module is not available
    IRObjectCaptionWriter = None
    print(f"[Warning] Could not import module {iro_module_name}: {e}")
