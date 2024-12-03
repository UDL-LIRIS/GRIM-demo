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
        return self.stage_output_dir("stage_1_0_convert_to_OFF")

    def convert_obj_to_off_stage_output_filename(self):
        input_filename = self.fix_obj_normals_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename + ".off"
        return os.path.join(self.convert_obj_to_off_stage_output_dir(), filename)

    ### Off to hollow VOL
    def from_off_to_hollow_vol_stage_output_dir(self):
        return self.stage_output_dir("stage_1_1_convert_OFF_to_hollow_VOL")

    def from_off_to_hollow_vol_stage_output_filename(self):
        input_filename = self.convert_obj_to_off_stage_output_filename()
        stem_filename = Path(input_filename).stem
        filename = stem_filename + "_hollow.vol"
        return os.path.join(self.from_off_to_hollow_vol_stage_output_dir(), filename)
