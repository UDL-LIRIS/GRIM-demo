from hera.workflows import (
    ExistingVolume,
    Parameter,
    script,
)


@script(
    inputs=[
        Parameter(name="geo_offsets_list"),
        Parameter(name="output_filename"),
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
def write_geo_offset(
    geo_offsets_list,
    output_filename,
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

    full_path_file_to_create = os.path.join(mount_path, output_filename)
    dir_path_of_file = os.path.dirname(full_path_file_to_create)
    if not os.path.isdir(dir_path_of_file):
        print(f"Target directory {dir_path_of_file} not found.")
        print("Exiting.")
        sys.exit(1)

    with open(full_path_file_to_create, "w") as f:
        f.write(" ".join(str(offset) for offset in geo_offsets_list))

    print("Done.")
