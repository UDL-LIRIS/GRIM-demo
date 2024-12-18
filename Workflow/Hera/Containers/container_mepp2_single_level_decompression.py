from hera.workflows import Container, models, Parameter


def define_mepp2_single_level_decompression_container(environment):
    command = (
        "set -x; /MEPP2/build/Examples/CGAL/Surface_mesh/progressive_decompression_filter_cgal_surface_mesh "
        + "{{inputs.parameters.input_file}} "
        + "{{inputs.parameters.output_basename}}{{inputs.parameters.batch_id}}.obj "
        + "{{inputs.parameters.batch_id}}"
    )

    return Container(
        name="mepp2-single-level-decompression",
        inputs=[
            Parameter(name="input_file"),
            Parameter(name="output_basename"),
            Parameter(name="batch_id"),
        ],
        image=environment.cluster.docker_registry
        + "/"
        + environment.cluster.docker_organisation
        + "/"
        + "mepp2:1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        command=[
            "bash",
            "-c",
            command,
        ],
        volumes=[environment.persisted_volume.volume],
    )
