from hera.workflows import (
    ExistingVolume,
    Parameter,
    script,
)


@script(
    inputs=[
        Parameter(name="directory_to_check"),
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
def check_final_result(
    directory_to_check,
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

    if not os.path.isdir(directory_to_check):
        print(f"Target directory {directory_to_check} not found.")
        print("Exiting.")
        sys.exit(1)

    files = os.listdir(directory_to_check)

    if "geo_offset.txt" not in files:
        print(f"Target directory {directory_to_check} misses the geo_offset file.")
        print("Exiting.")
        sys.exit(1)

    if "skeleton.obj" not in files:
        print(f"Target directory {directory_to_check} misses the skeleton.obj file.")
        print("Exiting.")
        sys.exit(1)

    if "tileset.json" not in files:
        print(f"Target directory {directory_to_check} misses the tileset.json file.")
        print("Exiting.")
        sys.exit(1)

    if not (
        "tiles" in files and os.path.isdir(os.path.join(directory_to_check, "tiles"))
    ):
        print(
            f"Tiles must be a sub-directory of target directory {directory_to_check}."
        )
        print("Exiting.")
        sys.exit(1)

    # Because this directory will be later on server by nginx, that requires
    # (by default) an index.html file, generate that file:
    with open(os.path.join(directory_to_check, "index.html"), "w") as f:

        html_content = (
            "<html>\n"
            "<head>\n"
            "<title>Grim workflow results</title>"
            "</head>\n"
            '<body BGCOLOR="#FFFFFF" bgproperties="fixed">\n'
            "<b>Files</b>:\n"
            "<ul>\n"
            "<li>\n"
            '[<a href="./geo_offset.txt">geo_offset.txt</a>]\n'
            "</li>\n"
            "<li>\n"
            '[<a href="./skeleton.obj">skeleton.obj</a>]\n'
            "</li>\n"
            "<li>\n"
            '[<a href="./tileset.json">tileset.json</a>]\n'
            "</li>\n"
            "</body>\n"
            "</html>\n"
        )
        f.write(html_content)
    print("Final results seems to have all its components.")
