from hera.workflows import Container, models, Parameter


def define_convert_sdp_to_obj_container(environment):
    return Container(
        name="convert-sdp-to-obj",
        inputs=[
            Parameter(name="input_file"),
            Parameter(name="output_file"),
        ],
        image=environment.cluster.docker_registry
        + "/"
        + environment.cluster.docker_organisation
        + "/"
        + "convertsdptoobj:1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        command=[
            "python3",
            "convert_sdp_to_obj.py",
            "--input_file",
            "{{inputs.parameters.input_file}}",
            "--output_file",
            "{{inputs.parameters.output_file}}",
        ],
        volumes=[environment.persisted_volume.volume],
    )
