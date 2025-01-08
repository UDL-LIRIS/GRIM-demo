import tarfile
import os
import sys
import io

from hera.workflows import (
    ExistingVolume,
    Parameter,
    script,
)


def build_tarball_as_bytes():
    contexts_directory = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..",
        "..",
        "Docker",
    )
    contexts_directory = os.path.realpath(contexts_directory)
    relative_contexts = [x[1] for x in os.walk(contexts_directory)][0]
    absolute_contexts = [os.path.join(contexts_directory, x) for x in relative_contexts]
    print("All the contexts", absolute_contexts)
    try_context_dir = absolute_contexts[1]
    try_archive_name = "bozo.tgz"
    with tarfile.open(try_archive_name, "w:gz") as tar:
        tar.add(try_context_dir)

    # Reference
    #   https://stackoverflow.com/questions/39603978/reading-a-tarfile-into-bytesio
    with open(try_archive_name, "rb") as fin:
        data = io.BytesIO(fin.read())
        return data


@script(
    inputs=[
        Parameter(name="tarfile_as_bytes"),
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
def expand_context_to_pvc(
    tarfile_as_bytes,
    # claim_name argument is only used by the @script decorator and is present
    # here only because Hera seems to require it
    claim_name,
    mount_path,
):
    import sys
    import os
    import io

    if not os.path.isdir(mount_path):
        print(f"Persisted volume directory {mount_path} not found.")
        print("Exiting")
        sys.exit(1)

    file_like_object = io.BytesIO(tarfile_as_bytes)
    tar = tarfile.open(fileobj=file_like_object)
    # use "tar" as a regular TarFile object
    for member in tar.getmembers():
        f = tar.extractfile(member)
        print("extracted", f)


@script()
def debug(message: str):
    print(f"Hello {message}")


##########################################################


if __name__ == "__main__":

    from hera.workflows import (
        DAG,
        Workflow,
    )

    import os
    from parser import parser
    from environment import environment

    args = parser().parse_args()
    environment = environment(args)

    ### From now on, the only variables that must be used should be derived
    # (or based-on) the environment

    with Workflow(
        generate_name="grim-build-images-",
        entrypoint="main",
    ) as w:

        ### Proceed with a DAG workflow
        with DAG(name="main"):
            # The final task of the data production pipeline. The tasks
            # following t_data_final are dedicated to using/exploring that
            # resulting data

            t_copy_contexts = expand_context_to_pvc(
                name="copy-contexts",
                arguments={
                    "tarfile_as_bytes": build_tarball_as_bytes(),
                    "claim_name": environment.persisted_volume.claim_name,
                    "mount_path": environment.persisted_volume.mount_path,
                },
            )

            t_debug = debug(arguments={"message": "bozo"})
            t_copy_contexts >> t_debug

    w.create()
