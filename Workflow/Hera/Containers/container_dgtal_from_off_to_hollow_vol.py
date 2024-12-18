import os
from hera.workflows import Container, models, Parameter


def define__dgtal_from_off_to_hollow_vol_container(environment, layout, inputs):
    mes2vol_command = (
        "/home/digital/git/DGtalTools/build/converters/mesh2vol "
        + "-i {{inputs.parameters.input_file}} "
        + "-o {{inputs.parameters.output_file}} "
        + "-r "
        + str(inputs.parameters.mesh2vol_resolution)
        # Black magic (following) line:
        # - mesh2vol log outputs are routed to stderr,
        # - yet running the same command, but without the stderr redirection
        #   to stdout, with docker -t will still produce a mesh2vol.log with
        #   some content (because the -t option regroups stderr with stdout),
        # - but running that command (still without the stderr redirection
        #   to stdout) over Kubernetes will produce an empty mesh2vol.log
        #   file.
        # - yet if one adds the stderr redirection to stdout, then even over
        #   Kubernetes the mesh2vol.log file will the proper content.
        + " 2>&1 "
        # The workflow needs to extract some parameters (required as input
        # to some downstream Tasks) from the logs. We thus tee in order
        # to have both the AW logs and an output file that the workflow
        # can use
        + "| tee "
        + os.path.join(layout.from_off_to_hollow_vol_stage_output_dir(), "mesh2vol.log")
    )

    return Container(
        name="dgtal-from-off-to-hollow-vol",
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
            # We need to redirect the standard output of the mesh2vol filter
            # to a file in order to extract the scaling factor and the offset.
            # For this we use the shell pipe mechanism together with a tee
            # trick
            "bash",
            "-c",
            mes2vol_command,
        ],
        volumes=[environment.persisted_volume.volume],
    )
