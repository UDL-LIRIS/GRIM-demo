from hera.workflows import Container, models, Parameter


def define_blender_generate_container(environment, layout):
    # Reference: https://github.com/VCityTeam/UD-Reproducibility/blob/master/Computations/3DTiles/Ribs/Readme.md#for-the-cave-system
    return Container(
        name="blender-generate",
        inputs=[
            Parameter(name="subdivision_level"),
        ],
        image=environment.cluster.docker_registry
        + "/"
        + environment.cluster.docker_organisation
        + "/"
        + "ribs:1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        command=[
            "python",
            "Cave.py",
            "-v",
            "--subdivision",
            "{{inputs.parameters.subdivision_level}}",
            "--fill_holes",
            "True",
            "--outputdir",
            layout.blender_generate_stage_output_dir(),
        ],
        volumes=[environment.persisted_volume.volume],
    )
