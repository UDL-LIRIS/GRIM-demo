import os
from hera.workflows import Container, models, Parameter


def define_mepp2_maximum_decompression_container(environment, layout):
    command = (
        "/MEPP2/build/Examples/CGAL/Surface_mesh/progressive_decompression_filter_cgal_surface_mesh "
        + "{{inputs.parameters.input_file}} "
        + "maximum_decompressed_lod_dummy.obj "
        + "2>&1 "
        + "| tee "
        + os.path.join(layout.from_bin_to_objs_stage_output_dir(), "decompress.log")
        # But then the comparison (between the output off file and the
        # un-existing dummy file) that the tests realizes will fail.
        # Oddly enough the progressive_decompression_filter will exit with
        # an error message of the form
        #    terminate called after throwing an instance of 'std::runtime_error'
        #       what():  Writer::write_obj_file -> output file failed to open.
        # and a fail as exit code. In order to correct this unwanted behavior,
        # (just as done with mepp2_convert_obj_to_off_command) we use a
        # wrapping shell to trap the exit code of the filter and convert it
        # on the fly to become a success. That is why we use
        #     bash -c "<FILTER and ARGS> || true"
        + "|| true"
    )

    return Container(
        name="mepp2-maximum-decompression-level",
        inputs=[
            Parameter(name="input_file"),
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
