from hera.workflows import Container, models, Parameter


def define_dgtal_from_vol_to_sdp_container(environment):
    return Container(
        name="dgtal-from-vol-to-sdp",
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
            "criticalKernelsThinning3D",
            "--input",
            "{{inputs.parameters.input_file}}",
            "--select",
            "dmax",
            "--skel",
            "1isthmus",
            "--persistence",
            "1",
            "-e",
            "{{inputs.parameters.output_file}}",
        ],
        volumes=[environment.persisted_volume.volume],
    )
