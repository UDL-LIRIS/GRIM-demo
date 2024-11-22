from hera.workflows import (
    ExistingVolume,
    Parameter,
    script,
)


@script(
    inputs=[
        Parameter(name="directory_to_create"),
        Parameter(name="claim_name"),
        Parameter(name="mount_path"),
    ],
    volumes=[
        ExistingVolume(
            name="dummy",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def create_directory(
    # claim_name argument is only used by the @script decorator and is present
    # here only because Hera seems to require it
    claim_name,
    mount_path,
):
    import sys
    import os

    if not os.path.isdir(mount_path):
        print(f"Persisted volume directory {mount_path} not found.")
        print("Exiting")
        sys.exit(1)

    full_path_directory_to_create = os.path.join(mount_path, directory_to_create)
    if os.path.isdir(full_path_directory_to_create):
        print(f"Directory {directory_to_create} already exists.")
        print("Ending task with nothing to do.")
        sys.exit(0)

    os.makedirs(full_path_directory_to_create)
    if not os.path.isdir(full_path_directory_to_create):
        print(f"Failed to create directory {full_path_directory_to_create}.")
        print("Exiting")
        sys.exit(1)

    print("Done.")
