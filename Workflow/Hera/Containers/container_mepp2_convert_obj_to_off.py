from hera.workflows import Container, models, Parameter


def define_mepp2_convert_obj_to_off(environment):
    mepp2_convert_obj_to_off_command = (
        "/MEPP2/build/Testing/CGAL/Surface_mesh/test_generic_writer_surfacemesh "
        + "{{inputs.parameters.input_file}} "
        + "{{inputs.parameters.output_file}} "
        # As its name indicates it, test_generic_writer_surfacemesh is
        # a test that as such will take a third argument that designates
        # a reference file to which the test compares its result. Although
        # we here divert the usage of this test in order to use it as a
        # simple filter, we still have to provide a reference file (to
        # compare the result with). But we have no such file, and
        # providing the result file as comparison file will also fail
        # since the test expects the third argument to be the filename
        # of file with ".coff" file format when the result has is in a
        # ".cnoff" format. We thus provide a dummy filename for the test
        # to accept to start and realize the first part of its job which
        # is to compute some off output file.
        + "dummy "
        # But then the comparison (between the output off file and the
        # un-existing dummy file) that the tests realizes will fail.
        # This will in turn make the container to fail (return a fail
        # exit code). In order to correct unwanted behavior, we use a
        # wrapping shell to trap the exit code of the filter and convert
        # it on the fly to become a success. That is we use
        #     bash -c "<FILTER and ARGS> || true"
        + "|| true"
    )

    return Container(
        name="mepp2-convert-obj-to-off",
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
        command=["bash", "-c", mepp2_convert_obj_to_off_command],
        volumes=[environment.persisted_volume.volume],
    )
