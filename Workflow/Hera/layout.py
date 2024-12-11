import os
from pathlib import Path


class layout:
    """
    The directory tree specified within this layout class is not aware of the
    volumes used by cluster to support the workflow. This layout focuses on
    the experiment layout (as opposed to the deployment details).
    """

    def __init__(self, inputs, environment) -> None:
        self.experiment_absolute_output_dir = os.path.join(
            environment.persisted_volume.mount_path,
            inputs.constants.experiment_output_dir,
        )
        self.subdivision = inputs.parameters.subdivision_level

    def stage_output_dir(self, stage_output_dir):
        return os.path.join(self.experiment_absolute_output_dir, stage_output_dir)

    ###### Generate the initial cave with Blender
    def blender_generate_stage_output_dir(self):
        return self.stage_output_dir("stage_0_5_blender_generate")

    def blender_generate_stage_output_filename(self):
        filename = (
            "cave_sub_"
            + str(self.subdivision)
            + "_grid_size_x_1_grid_size_y_1_no_boundaries_triangulation.obj"
        )
        return os.path.join(self.blender_generate_stage_output_dir(), filename)

    ###### Fix the normals for MEPP2 to work properly
    def fix_obj_normals_stage_output_dir(self):
        return self.stage_output_dir("stage_0_6_fix_normals")

    def fix_obj_normals_stage_output_filename(self):
        input_filename = self.blender_generate_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename + "_fixed_normals.obj"
        return os.path.join(self.fix_obj_normals_stage_output_dir(), filename)

    ###### Step 1: DGTAL (well mainly)
    def convert_obj_to_off_stage_output_dir(self):
        return self.stage_output_dir("stage_1_1_0_convert_to_OFF")

    def convert_obj_to_off_stage_output_filename(self):
        input_filename = self.fix_obj_normals_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename + ".off"
        return os.path.join(self.convert_obj_to_off_stage_output_dir(), filename)

    ### Off to hollow VOL
    def from_off_to_hollow_vol_stage_output_dir(self):
        return self.stage_output_dir("stage_1_1_1_from_OFF_to_hollow_VOL")

    def from_off_to_hollow_vol_stage_output_filename(self):
        input_filename = self.convert_obj_to_off_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename + "_hollow.vol"
        return os.path.join(self.from_off_to_hollow_vol_stage_output_dir(), filename)

    def from_off_to_hollow_vol_stage_log_filename(self):
        return os.path.join(
            self.from_off_to_hollow_vol_stage_output_dir(), "mesh2vol.log"
        )

    ### Hollow VOL to filled VOL
    def from_hollow_to_filled_vol_stage_output_dir(self):
        return self.stage_output_dir("stage_1_1_2_from_hollow_to_filled_VOL")

    def from_hollow_to_filled_vol_stage_output_filename(self):
        input_filename = self.from_off_to_hollow_vol_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename.replace("_hollow", "_filled") + ".vol"
        return os.path.join(self.from_hollow_to_filled_vol_stage_output_dir(), filename)

    ### VOL to raw OBJ (for intermediate visualization)
    def from_vol_to_raw_obj_stage_output_dir(self):
        return self.stage_output_dir("stage_1_1_3_from_vol_to_raw_VOL")

    def from_vol_to_raw_obj_stage_output_filename(self):
        input_filename = self.from_hollow_to_filled_vol_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename.replace("_filled", "_voxels") + ".obj"
        return os.path.join(self.from_vol_to_raw_obj_stage_output_dir(), filename)

    ### Extract median axis
    # VOL to SDP
    def from_vol_to_sdp_stage_output_dir(self):
        return self.stage_output_dir("stage_1_2_1_from_vol_to_SDP")

    def from_vol_to_sdp_stage_output_filename(self):
        input_filename = self.from_hollow_to_filled_vol_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename + "_skeleton.sdp"
        return os.path.join(self.from_vol_to_sdp_stage_output_dir(), filename)

    # SDP to OBJ
    def from_sdp_to_obj_stage_output_dir(self):
        return self.stage_output_dir("stage_1_2_2_from_SDP_to_OBJ")

    def from_sdp_to_obj_stage_output_filename(self):
        input_filename = self.from_vol_to_sdp_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename + ".obj"
        return os.path.join(self.from_sdp_to_obj_stage_output_dir(), filename)

    # OBJ to rescaled OBJ
    def from_obj_to_rescaled_obj_stage_output_dir(self):
        return self.stage_output_dir("stage_1_2_3_from_OBJ_to_rescaled_OBJ")

    def from_obj_to_rescaled_obj_stage_output_filename(self):
        input_filename = self.from_sdp_to_obj_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename + "_rescaled.obj"
        return os.path.join(self.from_obj_to_rescaled_obj_stage_output_dir(), filename)

    ### Triangulation compression (OBJ to BIN)
    # OBJ to BIN
    def from_obj_to_bin_stage_output_dir(self):
        return self.stage_output_dir("stage_2_1_from_OBJ_to_BIN")

    def from_obj_to_bin_stage_output_filename(self):
        input_filename = self.fix_obj_normals_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename + ".bin"
        return os.path.join(self.from_obj_to_bin_stage_output_dir(), filename)

    # Decompression extracts many OBJ files (thus the plural for OBJs)
    def from_bin_to_objs_stage_output_dir(self):
        return self.stage_output_dir("stage_2_2_from_BIN_to_OBJs")

    def from_bin_to_objs_stage_output_single_level_basename(self):
        filename = self.from_obj_to_bin_stage_output_filename()
        stem_filename = Path(filename).stem
        return os.path.join(self.from_bin_to_objs_stage_output_dir(), stem_filename)
