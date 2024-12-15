from hera.workflows import Container, models, Parameter


def define_mepp2_compress_obj_container(environment):
    return Container(
        name="mepp2-compress-obj",
        inputs=[
            Parameter(name="input_file"),
            Parameter(name="output_file"),
        ],
        image=environment.cluster.docker_registry
        + "/"
        + environment.cluster.docker_organisation
        + "/"
        + "mepp2:1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        command=[
            "/MEPP2/build/Examples/CGAL/Surface_mesh/progressive_compression_filter_cgal_surface_mesh",
            "{{inputs.parameters.input_file}}",
            "0",
            "{{inputs.parameters.output_file}}",
            '""',
            # Note: only Vincent Vidal knows why the following parameters
            # do work (as opposed to other values). Black magic (a.k.a.
            # non reproducible thingies rule the numerical world :-( )
            "1 0 0 70 -1 0 12",
        ],
        volumes=[environment.persisted_volume.volume],
    )
