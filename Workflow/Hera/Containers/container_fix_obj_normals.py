from hera.workflows import Container, models, Parameter


def define_fix_obj_normals_container(environment):
    return Container(
        name="fix-obj-normals",
        inputs=[
            Parameter(name="input_file"),
            Parameter(name="output_file"),
        ],
        image=environment.cluster.docker_registry
        + "/"
        + environment.cluster.docker_organisation
        + "/"
        + "fixobjnormals:1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        command=[
            "python3",
            "fix_OBJ_normals_for_MEPP2.py",
            "{{inputs.parameters.input_file}}",
            "{{inputs.parameters.output_file}}",
        ],
        volumes=[environment.persisted_volume.volume],
    )
