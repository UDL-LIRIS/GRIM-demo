from hera.workflows import Container, models, Parameter


def define_dgtal_from_hollow_to_filled_vol_container(environment):
    return Container(
        name="dgtal-from-hollow-to-filled-vol",
        inputs=[
            Parameter(name="input_file"),
            Parameter(name="output_file"),
        ],
        image=environment.cluster.docker_registry
        + "/"
        + environment.cluster.docker_organisation
        + "/"
        + "dgtal:1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        command=[
            "/home/digital/git/DGtalTools/build/volumetric/volFillInterior",
            "-i",
            "{{inputs.parameters.input_file}}",
            "-o",
            "{{inputs.parameters.output_file}}",
        ],
        volumes=[environment.persisted_volume.volume],
    )
