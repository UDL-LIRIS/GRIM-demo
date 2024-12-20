if __name__ == "__main__":

    # A workflow that tests whether the defined environment is correct as
    # seen and used from within the Argo server engine (at Workflow runtime)
    from hera.workflows import (
        DAG,
        Task,
        Workflow,
    )

    import os
    from parser import parser
    from layout import layout
    from environment import environment
    from inputs import inputs
    from Containers import *  # Containers definitions
    from Scripts import *  # Scripts definitions

    args = parser().parse_args()
    environment = environment(args)
    layout = layout(inputs, environment)

    ### From now on, the only variables that must be used should be derived
    # (or based-on) the environment, layout and inputs variables

    with Workflow(
        generate_name="grim-workflow-",
        entrypoint="main",
        volumes=[environment.persisted_volume.volume],
    ) as w:

        #### Container definitions (must be within Workflow context)
        blender_generate_c = define_blender_generate_container(environment, layout)
        fix_obj_normals_c = define_fix_obj_normals_container(environment)
        mepp2_convert_obj_to_off_c = define_mepp2_convert_obj_to_off(environment)
        dgtal_from_off_to_hollow_vol_c = define__dgtal_from_off_to_hollow_vol_container(
            environment, layout, inputs
        )
        dgtal_from_hollow_to_filled_vol_c = (
            define_dgtal_from_hollow_to_filled_vol_container(environment)
        )
        dgtal_from_vol_to_raw_obj_c = define_dgtal_from_vol_to_raw_obj_container(
            environment
        )
        dgtal_from_vol_to_sdp_c = define_dgtal_from_vol_to_sdp_container(environment)
        convert_sdp_to_obj_c = define_convert_sdp_to_obj_container(environment)
        obj_to_obj_scale_offset_c = define_obj_to_obj_scale_offset_container(
            environment
        )
        mepp2_compress_obj_c = define_mepp2_compress_obj_container(environment)
        mepp2_maximum_decompression_c = define_mepp2_maximum_decompression_container(
            environment, layout
        )
        mepp2_single_level_decompression_c = (
            define_mepp2_single_level_decompression_container(environment)
        )
        py3dtilers_objs_to_3dtiles_c = define_py3dtilers_objs_to_3dtiles_container(
            environment, inputs
        )
        http_serve_resulting_data_c = define_http_serve_resulting_data_container(
            environment
        )
        create_resulting_data_http_service_r = (
            define_http_serve_resulting_data_create_service_resource()
        )
        delete_resulting_data_http_service_r = (
            define_http_serve_resulting_data_delete_service_resource()
        )

        ### Proceed with a DAG workflow
        with DAG(name="main"):
            # The final task of the data production pipeline. The tasks
            # following t_data_final are dedicated to using/exploring that
            # resulting data

            t_data_final = check_final_result(
                name="final-data-check",
                arguments={
                    "directory_to_check": layout.workflow_resulting_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )

            t_main_0 = create_directory(
                name="create-workflow-resulting-dir",
                arguments={
                    "directory_to_create": layout.workflow_resulting_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )

            t_main_1 = create_directory(
                name="create-directory-blender-generate",
                arguments={
                    "directory_to_create": layout.blender_generate_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_0 >> t_main_1

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
            t_main_2 = Task(name="blender-generate", template=blender_generate_c)
            t_main_1 >> t_main_2

            t_main_3 = create_directory(
                name="create-directory-fix-obj-normals",
                arguments={
                    "directory_to_create": layout.fix_obj_normals_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_4 = fix_obj_normals_c(
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
            t_main_a_2 = mepp2_convert_obj_to_off_c(
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
            t_main_a_4 = dgtal_from_off_to_hollow_vol_c(
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
            t_main_a_a_2 = dgtal_from_hollow_to_filled_vol_c(
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
            t_main_a_a_b_2 = dgtal_from_vol_to_raw_obj_c(
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
            t_main_a_a_a_2 = dgtal_from_vol_to_sdp_c(
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
            t_main_a_a_a_4 = convert_sdp_to_obj_c(
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

            t_main_a_a_a_5 = obj_to_obj_scale_offset_c(
                arguments={
                    "scale": t_main_a_b_1.get_parameter("scale"),
                    "offset_x": t_main_a_b_1.get_parameter("offset_x"),
                    "offset_y": t_main_a_b_1.get_parameter("offset_y"),
                    "offset_z": t_main_a_b_1.get_parameter("offset_z"),
                    "input_file": layout.from_sdp_to_obj_stage_output_filename(),
                    "output_file": layout.from_obj_to_rescaled_obj_stage_output_filename(),
                }
            )
            t_main_a_a_a_4 >> t_main_a_a_a_5
            t_main_a_b_1 >> t_main_a_a_a_5
            t_main_a_a_a_5 >> t_data_final

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
            t_main_b_2 = mepp2_compress_obj_c(
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
            t_main_b_4 = mepp2_maximum_decompression_c(
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

            # Proceed with decompression with a parallel loop
            # Note: refer here for a loop with a dynamically (unknown at
            # submission stage) parametrized list as input
            # https://hera.readthedocs.io/en/latest/examples/workflows/upstream/loops_param_result/
            t_main_b_6 = mepp2_single_level_decompression_c(
                name="decompress-loop",
                arguments={
                    "input_file": layout.from_obj_to_bin_stage_output_filename(),
                    "output_basename": layout.from_bin_to_objs_stage_output_single_level_basename(),
                    "batch_id": "{{item}}",
                },
                with_param=t_main_b_5.result,
            )
            t_main_b_5 >> t_main_b_6

            t_main_b_7 = py3dtilers_objs_to_3dtiles_c(
                name="py3dtilers-objs-to-3dtiles",
                arguments={
                    "input_directory": layout.from_bin_to_objs_stage_output_dir(),
                    "output_directory": layout.workflow_resulting_dir(),
                },
            )
            t_main_0 >> t_main_b_7
            t_main_b_6 >> t_main_b_7
            t_main_b_7 >> t_data_final

            ### Writing the geo-offsets to the resulting directory
            t_main_c = write_geo_offset(
                name="write-geo-offset",
                arguments={
                    "geo_offsets_list": inputs.parameters.geo_offset,
                    "output_filename": os.path.join(
                        layout.workflow_resulting_dir(), "geo_offset.txt"
                    ),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t_main_0 >> t_main_c
            t_main_c >> t_data_final

            ####################### Using the computed data
            t_use_data_1 = http_serve_resulting_data_c(
                name="http-serve-resulting-data-task",
                arguments={
                    "exposed_dir_subpath": layout.relative_workflow_resulting_dir(),
                },
            )
            t_data_final >> t_use_data_1

            t_use_data_2 = Task(
                name="create-http-serve-service",
                template=create_resulting_data_http_service_r.name,
            )
            t_use_data_1 >> t_use_data_2

            # The http_serve_resulting_data_c is launched as a daemon that will
            # be terminated as soon as the last task of the workflow is finished.
            # The purpose of the sleep task is thus to keep the http servers
            # alive long enough for a reasonable delay (that is a delay allowing
            # the final user to interacts with the data web viewer):
            t_sleep = sleep(arguments={"delay": 120})  # Sleep delay in seconds
            t_use_data_2 >> t_sleep

            # Cleaning up Resources that are no longer necessary
            t_use_data_3 = Task(
                name="delete-http-serve-service",
                template=delete_resulting_data_http_service_r.name,
            )
            t_sleep >> t_use_data_3

    w.create()
