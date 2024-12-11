if __name__ == "__main__":

    # A workflow that tests whether the defined environment is correct as
    # seen and used from within the Argo server engine (at Workflow runtime)
    from hera.workflows import (
        Container,
        DAG,
        ExistingVolume,
        models,
        Parameter,
        Task,
        Workflow,
    )

    import os
    from parser import parser
    from layout import layout
    from environment import environment
    from inputs import inputs
    from script_create_directory import create_directory
    from script_debug import debug
    from script_extract_mesh2vol_outputs import extract_mesh2vol_outputs
    from script_extract_list_of_evenly_distributed_batches import (
        extract_list_of_evenly_distributed_batches,
    )

    args = parser().parse_args()
    environment = environment(args)
    layout = layout(inputs, environment)

    ### From now on, the only variables that must be used should be
    # derived/based-on the environment and layout variables
    ## Helpers and synthetic sugar
    volume = ExistingVolume(
        claim_name=environment.persisted_volume.claim_name,
        name="dummy",
        mount_path=environment.persisted_volume.mount_path,
    )

    with Workflow(generate_name="grim-workflow-", entrypoint="main") as w:

        # Reference: https://github.com/VCityTeam/UD-Reproducibility/blob/master/Computations/3DTiles/Ribs/Readme.md#for-the-cave-system
        blender_generate = Container(
            name="blender-generate",
            image=environment.cluster.docker_registry
            + "/"
            + environment.cluster.docker_organisation
            + "/"
            + "ribs:1.0",
            image_pull_policy=models.ImagePullPolicy.always,
            command=[
                "python",
                "Cave.py",
                "-v",
                "--subdivision",
                "1",
                "--fill_holes",
                "True",
                "--outputdir",
                layout.blender_generate_stage_output_dir(),
            ],
            volumes=[volume],
        )
        fix_obj_normals = Container(
            name="fix-obj-normals",
            inputs=[
                Parameter(name="input_file"),
                Parameter(name="output_file"),
            ],
            image=environment.cluster.docker_registry
            + "/"
            + environment.cluster.docker_organisation
            + "/"
            + "fixobjnormals:1.0",
            image_pull_policy=models.ImagePullPolicy.always,
            command=[
                "python3",
                "fix_OBJ_normals_for_MEPP2.py",
                "{{inputs.parameters.input_file}}",
                "{{inputs.parameters.output_file}}",
            ],
            volumes=[volume],
        )

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

        mepp2_convert_obj_to_off = Container(
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
            volumes=[volume],
        )

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
            + os.path.join(
                layout.from_off_to_hollow_vol_stage_output_dir(), "mesh2vol.log"
            )
        )

        dgtal_from_off_to_hollow_vol = Container(
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
            volumes=[volume],
        )

        dgtal_from_hollow_to_filled_vol = Container(
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
            volumes=[volume],
        )

        dgtal_from_vol_to_raw_obj = Container(
            name="dgtal-from-vol-to-raw-obj",
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
                "/home/digital/git/DGtalTools/build/converters/vol2obj",
                "-i",
                "{{inputs.parameters.input_file}}",
                "-o",
                "{{inputs.parameters.output_file}}",
            ],
            volumes=[volume],
        )

        dgtal_from_vol_to_sdp = Container(
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
            volumes=[volume],
        )

        convert_sdp_to_obj = Container(
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
            volumes=[volume],
        )

        obj_to_obj_scale_offset = Container(
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
            volumes=[volume],
        )

        mepp2_compress_obj = Container(
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
                # FIXME: only Vincent Vidal knows why the following parameters
                # do work (as opposed to other values). Black magic (a.k.a.
                # non reproducible thingies rule the numerical world :-( )
                "1 0 0 70 -1 0 12",
            ],
            volumes=[volume],
        )

        mepp2_maximum_decompression_command = (
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

        mepp2_maximum_decompression_level = Container(
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
                mepp2_maximum_decompression_command,
            ],
            volumes=[volume],
        )

        mepp2_single_level_decompression_command = (
            "set -x; /MEPP2/build/Examples/CGAL/Surface_mesh/progressive_decompression_filter_cgal_surface_mesh "
            + "{{inputs.parameters.input_file}} "
            + "{{inputs.parameters.output_basename}}{{inputs.parameters.batch_id}}.obj "
            + "{{inputs.parameters.batch_id}}"
        )

        mepp2_single_level_decompression_level = Container(
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
                mepp2_single_level_decompression_command,
            ],
            volumes=[volume],
        )

        with DAG(name="main"):
            t_main_1 = create_directory(
                name="create-directory-blender-generate",
                arguments={
                    "directory_to_create": layout.blender_generate_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )

            # For the time being bpy (Python blender) won't work on
            # AppleSilicon (either in native M3 nor in amd64 emulated with
            # Rosetta. Blame it on Apple for their failed move away from Intel.)
            # Thus the  following Task won't work when ran e.g. on Minikube
            # with an M3 processor. Here is the alternative:
            #
            # from script_download_blender_results import download_blender_results
            # t2 = download_blender_results(
            #     arguments=[
            #         Parameter(
            #             name="config_map_name",
            #             value=environment.cluster.configmap,
            #         ),
            #         Parameter(
            #             name="target_directory",
            #             value=layout.blender_generate_stage_output_dir(),
            #         ),
            #         Parameter(
            #             name="claim_name",
            #             value=environment.persisted_volume.claim_name,
            #         ),
            #         Parameter(
            #             name="mount_path",
            #             value=environment.persisted_volume.mount_path,
            #         ),
            #     ]
            # )
            #
            t_main_2 = Task(name="blender-generate", template=blender_generate)
            t_main_1 >> t_main_2

            t_main_3 = create_directory(
                name="create-directory-fix-obj-normals",
                arguments={
                    "directory_to_create": layout.fix_obj_normals_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_4 = fix_obj_normals(
                arguments={
                    "input_file": layout.blender_generate_stage_output_filename(),
                    "output_file": layout.fix_obj_normals_stage_output_filename(),
                }
            )
            t_main_2 >> t_main_3 >> t_main_4

            t_main_a_1 = create_directory(
                name="create-directory-mepp2-convert-obj-to-off",
                arguments={
                    "directory_to_create": layout.convert_obj_to_off_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_a_2 = mepp2_convert_obj_to_off(
                arguments={
                    "input_file": layout.fix_obj_normals_stage_output_filename(),
                    "output_file": layout.convert_obj_to_off_stage_output_filename(),
                }
            )
            t_main_4 >> t_main_a_1 >> t_main_a_2

            t_main_a_3 = create_directory(
                name="create-directory-dgtal-from-off-to-hollow-vol",
                arguments={
                    "directory_to_create": layout.from_off_to_hollow_vol_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_a_4 = dgtal_from_off_to_hollow_vol(
                name="mesh2vol",
                arguments={
                    "input_file": layout.convert_obj_to_off_stage_output_filename(),
                    "output_file": layout.from_off_to_hollow_vol_stage_output_filename(),
                },
            )
            t_main_a_2 >> t_main_a_3 >> t_main_a_4

            t_main_a_a_1 = create_directory(
                name="create-directory-dgtal-from-hollow-to-filled-vol",
                arguments={
                    "directory_to_create": layout.from_hollow_to_filled_vol_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_a_a_2 = dgtal_from_hollow_to_filled_vol(
                arguments={
                    "input_file": layout.from_off_to_hollow_vol_stage_output_filename(),
                    "output_file": layout.from_hollow_to_filled_vol_stage_output_filename(),
                },
            )
            t_main_a_4 >> t_main_a_a_1 >> t_main_a_a_2

            t_main_a_a_b_1 = create_directory(
                name="create-directory-dgtal-from-vol-to-raw-obj",
                arguments={
                    "directory_to_create": layout.from_vol_to_raw_obj_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_a_a_b_2 = dgtal_from_vol_to_raw_obj(
                arguments={
                    "input_file": layout.from_hollow_to_filled_vol_stage_output_filename(),
                    "output_file": layout.from_vol_to_raw_obj_stage_output_filename(),
                }
            )
            t_main_a_a_2 >> t_main_a_a_b_1 >> t_main_a_a_b_2

            t_main_a_a_a_1 = create_directory(
                name="create-directory-dgtal-from-vol-to-sdp",
                arguments={
                    "directory_to_create": layout.from_vol_to_sdp_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_a_a_a_2 = dgtal_from_vol_to_sdp(
                arguments={
                    "input_file": layout.from_hollow_to_filled_vol_stage_output_filename(),
                    "output_file": layout.from_vol_to_sdp_stage_output_filename(),
                }
            )
            t_main_a_a_2 >> t_main_a_a_a_1 >> t_main_a_a_a_2

            t_main_a_a_a_3 = create_directory(
                name="create-directory-from-sdp-to-obj",
                arguments={
                    "directory_to_create": layout.from_sdp_to_obj_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_a_a_a_4 = convert_sdp_to_obj(
                arguments={
                    "input_file": layout.from_vol_to_sdp_stage_output_filename(),
                    "output_file": layout.from_sdp_to_obj_stage_output_filename(),
                }
            )

            t_main_a_a_a_2 >> t_main_a_a_a_3 >> t_main_a_a_a_4

            ### Rescaling the SDP
            t_main_a_b_1 = extract_mesh2vol_outputs(
                name="mesh2vol-log",
                arguments={
                    "log_filename": layout.from_off_to_hollow_vol_stage_log_filename(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_a_4 >> t_main_a_b_1

            t_main_a_b_debug = debug(
                arguments=t_main_a_b_1.get_parameter("scale").with_name("message")
            )
            t_main_a_b_1 >> t_main_a_b_debug

            t_main_a_a_a_5 = create_directory(
                name="create-directory-from-obj-to-rescaled-obj",
                arguments={
                    "directory_to_create": layout.from_obj_to_rescaled_obj_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_a_a_a_4 >> t_main_a_a_a_5
            t_main_a_a_a_6 = obj_to_obj_scale_offset(
                arguments={
                    "scale": t_main_a_b_1.get_parameter("scale"),
                    "offset_x": t_main_a_b_1.get_parameter("offset_x"),
                    "offset_y": t_main_a_b_1.get_parameter("offset_y"),
                    "offset_z": t_main_a_b_1.get_parameter("offset_z"),
                    "input_file": layout.from_sdp_to_obj_stage_output_filename(),
                    "output_file": layout.from_obj_to_rescaled_obj_stage_output_filename(),
                }
            )
            t_main_a_a_a_5 >> t_main_a_a_a_6
            t_main_a_b_1 >> t_main_a_a_a_6

            ####################### Compression of triangulation
            t_main_b_1 = create_directory(
                name="create-directory-from-obj-to-bin",
                arguments={
                    "directory_to_create": layout.from_obj_to_bin_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_4 >> t_main_b_1
            t_main_b_2 = mepp2_compress_obj(
                arguments={
                    "input_file": layout.fix_obj_normals_stage_output_filename(),
                    "output_file": layout.from_obj_to_bin_stage_output_filename(),
                }
            )
            t_main_b_1 >> t_main_b_2

            ####################### Retrieve a fixed number of ad-hoc compressed
            # triangulations (out of the possible range)
            # Start with discovering the highest decompression level
            t_main_b_3 = create_directory(
                name="create-directory-decompression-level",
                arguments={
                    "directory_to_create": layout.from_bin_to_objs_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_b_2 >> t_main_b_3
            t_main_b_4 = mepp2_maximum_decompression_level(
                arguments={
                    "input_file": layout.from_obj_to_bin_stage_output_filename(),
                }
            )
            t_main_b_3 >> t_main_b_4

            # Then produce a restricted list of evenly distributed (among the
            # possible decompression levels) triangulations:
            t_main_b_5 = extract_list_of_evenly_distributed_batches(
                arguments={
                    "log_filename": os.path.join(
                        layout.from_bin_to_objs_stage_output_dir(), "decompress.log"
                    ),
                    "desired_number_of_batches": 4,
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                }
            )
            t_main_b_4 >> t_main_b_5

            t_main_b_6 = mepp2_single_level_decompression_level(
                name="decompress-loop",
                arguments={
                    "input_file": layout.from_obj_to_bin_stage_output_filename(),
                    "output_basename": layout.from_bin_to_objs_stage_output_single_level_basename(),
                    "batch_id": "{{item}}",
                },
                # with_items=[1, 6, 18],
                # FAIL with_items=[t_main_b_5.get_parameter("list_of_batches")],
                # with_param=t_main_b_5.get_parameter("list_of_batches"),
                with_param=t_main_b_5.result,
                # with_items=["foo", "bar", "baz"]
            )
            t_main_b_5 >> t_main_b_6

    w.create()
