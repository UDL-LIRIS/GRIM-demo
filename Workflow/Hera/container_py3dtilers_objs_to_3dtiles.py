from hera.workflows import Container, models, Parameter


def define_py3dtilers_objs_to_3dtiles_container(environment, inputs):

    command = [
        "obj-tiler",
        "-i",
        "{{inputs.parameters.input_directory}}",
        "-o",
        "{{inputs.parameters.output_directory}}",
        "--as_lods",
    ]

    command += ["--offset"] + inputs.parameters.geo_offset

    thresholds = inputs.parameters.threedtiles_thresholds[
        inputs.parameters.threedtiles_number_of_lods
    ]
    command += ["--geometric_error"] + thresholds

    return Container(
        name="py3dtilers-objs-to-3dtiles",
        inputs=[
            Parameter(name="input_directory"),
            Parameter(name="output_directory"),
        ],
        image=environment.cluster.docker_registry
        + "/"
        + environment.cluster.docker_organisation
        + "/"
        + "py3dtilers:1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        command=command,
        volumes=[environment.persisted_volume.volume],
    )
