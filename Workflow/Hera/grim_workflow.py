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
    layout = layout(inputs.constants, environment)

    ### From now on, the only variables that must be used should be
    # derived/based-on the environment and layout variables
    ## Helpers and synthetic sugar
    volume = ExistingVolume(
        claim_name=environment.persisted_volume.claim_name,
        name="dummy",
        mount_path=environment.persisted_volume.mount_path,
    )
    subdivision = inputs.parameters.subdivision_level

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
        with DAG(name="main"):
            t1 = create_directory(
                name="create-directory-blender-generate",
                arguments=[
                    Parameter(
                        name="directory_to_create",
                        value=layout.blender_generate_stage_output_dir(),
                    ),
                    Parameter(
                        name="claim_name",
                        value=environment.persisted_volume.claim_name,
                    ),
                    Parameter(
                        name="mount_path",
                        value=environment.persisted_volume.mount_path,
                    ),
                ],
            )
            # For the time being bpy (Python blender) won't work on
            # AppleSilicon (either in native M3 nor in amd64 emulated with
            # Rosetta. Blame it on Apple for their failed move away from Intel.)
            # Here is the alternative:
            #
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
                arguments=[
                    Parameter(
                        name="directory_to_create",
                        value=layout.fix_obj_normals_stage_output_dir(),
                    ),
                    Parameter(
                        name="claim_name",
                        value=environment.persisted_volume.claim_name,
                    ),
                    Parameter(
                        name="mount_path",
                        value=environment.persisted_volume.mount_path,
                    ),
                ],
            )
            t4 = fix_obj_normals(
                arguments=[
                    Parameter(
                        name="input_file",
                        value=os.path.join(
                            environment.persisted_volume.mount_path,
                            layout.blender_generate_stage_output_filename(subdivision),
                        ),
                    ),
                    Parameter(
                        name="output_file",
                        value=layout.fix_obj_normals_stage_output_filename(subdivision),
                    ),
                ]
            )
            t2 >> t3 >> t4
    w.create()
