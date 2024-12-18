from hera.workflows import Container, models, Parameter


def define_obj_to_obj_scale_offset_container(environment):
    return Container(
        name="obj-to-obj-scale-offset",
        inputs=[
            Parameter(name="scale"),
            Parameter(name="offset_x"),
            Parameter(name="offset_y"),
            Parameter(name="offset_z"),
            Parameter(name="input_file"),
            Parameter(name="output_file"),
        ],
        image=environment.cluster.docker_registry
        + "/"
        + environment.cluster.docker_organisation
        + "/"
        + "objtoobjscaleoffset:1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        command=[
            "python3",
            "obj_to_obj_scale_offset.py",
            "--scale",
            "{{inputs.parameters.scale}}",
            "--offset_x",
            "{{inputs.parameters.offset_x}}",
            "--offset_y",
            "{{inputs.parameters.offset_y}}",
            "--offset_z",
            "{{inputs.parameters.offset_z}}",
            "--input_file",
            "{{inputs.parameters.input_file}}",
            "--output_file",
            "{{inputs.parameters.output_file}}",
        ],
        volumes=[environment.persisted_volume.volume],
    )
