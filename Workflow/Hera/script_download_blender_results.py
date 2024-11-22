from hera.workflows import (
    ConfigMapEnvFrom,
    ExistingVolume,
    Parameter,
    script,
)


@script(
    inputs=[
        Parameter(name="target_directory"),
        Parameter(name="mount_path"),
    ],
    env_from=[
        # Assumes the corresponding config map is defined at k8s level
        ConfigMapEnvFrom(
            name="{{inputs.parameters.config_map_name}}",
            optional=False,
        )
    ],
    volumes=[
        ExistingVolume(
            name="dummy",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def download_blender_results(
    # claim_name and config_map_name arguments are only used by the @script
    # decorator and are repeated here only because Hera seems to require it
    config_map_name,
    claim_name,
    target_directory,
    mount_path,
):
    import subprocess
    import sys

    # Installing a package with pip requires an http access to PyPi (by default)
    # which can be blocked by the cluster networking configuration and might
    # thus require the configuration of an http proxy server.
    subprocess.check_call([sys.executable, "-m", "pip", "install", "wget"])
    print("Wget python package successfully installed.")

    import sys
    import os
    import wget

    if not os.path.isdir(mount_path):
        print(f"Persisted volume directory {mount_path} not found.")
        print("Exiting")
        sys.exit(1)

    full_target_directory = os.path.join(mount_path, target_directory)
    if os.path.isdir(full_target_directory):
        print(f"Directory {full_target_directory} already exists.")

    os.chdir(full_target_directory)
    # Because the server/network are sometimes flaky, giving many tries might
    # robustify the process:
    download_success = False
    number_max_wget_trial = 5
    url_to_seek = "https://dataset-dl.liris.cnrs.fr/synthetic-cave-and-tunnel-systems/Cave/cave_sub_1_grid_size_x_1_grid_size_y_1_no_boundaries_triangulation.obj"
    while not download_success:
        try:
            wget.download(url_to_seek)
            download_success = True
            print(f"Download of {url_to_seek} successful.")
        except:
            number_max_wget_trial -= 1
            if number_max_wget_trial:
                print(f"Download of {url_to_seek} failed: retying.")
            else:
                print(f"Download of {url_to_seek} failed: exiting.")
                sys.exit(1)
    print("Done.")
