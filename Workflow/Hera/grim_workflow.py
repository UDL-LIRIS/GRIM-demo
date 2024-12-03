if __name__ == "__main__":
    import os
    from parser import parser
    from layout import layout
    from environment import environment
    from inputs import inputs
    from script_create_directory import create_directory

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
        mepp2_convert_obj_to_off = Container(
            name="mepp2-convert-obj-to-ff",
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
                # As its name announces it, test_generic_writer_surfacemesh is
                # a test that as such will take a third argument that designates
                # a reference file to which the test compares its result. Although
                # we here divert the usage of this test in order to use it as a
                # simple filter, we still have to provide a reference file (to
                # compare the result with). But we have no such file, and
                # providing the result file as comparison file will also fail
                # since the test expects the third argument to be the filename
                # of file with a ".coff" extension (when the result has an ".off"
                # extension). We thus provide a dummy filename for the test to
                # accept to start and realize the first part of its job which
                # is to compute some off output file.
                # But then the comparison (between the output off file and the
                # un-existing dummy file) that the tests realizes will fail.
                # This will in turn make the container to fail (return a fail
                # exit code). In order to correct unwanted behavior, we use a
                # wrapping shell to trap the exit code of the filter and convert
                # it on the fly to become a success. That is we use
                #     bash -c "<FILTER and ARGS> || true"
                "bash",
                "-c",
                "/MEPP2/build/Testing/CGAL/Surface_mesh/test_generic_writer_surfacemesh {{inputs.parameters.input_file}} {{inputs.parameters.output_file}} dummy || true",
            ],
            volumes=[volume],
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
                "/home/digital/git/DGtalTools/build/converters/mesh2vol",
                "-i",
                "{{inputs.parameters.input_file}}",
                "-o",
                "{{inputs.parameters.output_file}}",
                "-r",
                inputs.parameters.mesh2vol_resolution,
            ],
            volumes=[volume],
        )

        with DAG(name="main"):
            t1 = create_directory(
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
            t2 = Task(name="blender-generate", template=blender_generate)
            t1 >> t2

            t3 = create_directory(
                name="create-directory-fix-obj-normals",
                arguments={
                    "directory_to_create": layout.fix_obj_normals_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t4 = fix_obj_normals(
                arguments={
                    "input_file": layout.blender_generate_stage_output_filename(),
                    "output_file": layout.fix_obj_normals_stage_output_filename(),
                }
            )
            t2 >> t3 >> t4

            t5 = create_directory(
                name="create-directory-mepp2-convert-obj-to-off",
                arguments={
                    "directory_to_create": layout.convert_obj_to_off_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t6 = mepp2_convert_obj_to_off(
                arguments={
                    "input_file": layout.fix_obj_normals_stage_output_filename(),
                    "output_file": layout.convert_obj_to_off_stage_output_filename(),
                }
            )
            t4 >> t5 >> t6

            t7 = create_directory(
                name="create-directory-dgtal-from-off-to-hollow-vol",
                arguments={
                    "directory_to_create": layout.from_off_to_hollow_vol_stage_output_dir(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )
            t8 = dgtal_from_off_to_hollow_vol(
                arguments={
                    "input_file": layout.convert_obj_to_off_stage_output_filename(),
                    "output_file": layout.from_off_to_hollow_vol_stage_output_filename(),
                }
            )
            t6 >> t7 >> t8

    w.create()
