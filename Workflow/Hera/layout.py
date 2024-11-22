import os


class layout:
    """
    The directory tree specified within this layout class is not aware of the
    volumes used by cluster to support the workflow. This layout focuses on
    the experiment layout (as opposed to the deployment details).
    """

    def __init__(self, constants, environment) -> None:
        self.experiment_absolute_output_dir = os.path.join(
            environment.persisted_volume.mount_path, constants.experiment_output_dir
        )

    def stage_output_dir(self, stage_output_dir):
        return os.path.join(self.experiment_absolute_output_dir, stage_output_dir)

    ###### stage 1: generate the initial cave with Blender
    def blender_generate_stage_output_dir(self):
        return self.stage_output_dir("stage_1_blender_generate")

    def blender_generate_stage_output_filename(self, subdivision):
        filename = (
            "cave_sub_"
            + str(subdivision)
            + "_grid_size_x_1_grid_size_y_1_no_boundaries_triangulation.obj"
        )
        return os.path.join(self.blender_generate_stage_output_dir(), filename)

    ###### stage 2: fix the normals for MEPP2 to work properly
    def fix_obj_normals_stage_output_dir(self):
        return self.stage_output_dir("stage_2_fix_normals")

    def fix_obj_normals_stage_output_filename(self, subdivision):
        filename = (
            "cave_sub_"
            + str(subdivision)
            + "_grid_size_x_1_grid_size_y_1_no_boundaries_triangulation_fixed_normals.obj"
        )
        return os.path.join(self.fix_obj_normals_stage_output_dir(), filename)
