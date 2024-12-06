from hera.workflows import ExistingVolume, Parameter, script
from hera.workflows.models import ValueFrom


@script(
    inputs=[
        Parameter(name="log_filename"),
        Parameter(name="claim_name"),
        Parameter(name="mount_path"),
    ],
    outputs=[
        Parameter(name="scale", value_from=ValueFrom(path="/tmp/result_scale.txt")),
        Parameter(
            name="x_offset", value_from=ValueFrom(path="/tmp/result_x_offset.txt")
        ),
        Parameter(
            name="y_offset", value_from=ValueFrom(path="/tmp/result_y_offset.txt")
        ),
        Parameter(
            name="z_offset", value_from=ValueFrom(path="/tmp/result_z_offset.txt")
        ),
    ],
    volumes=[
        ExistingVolume(
            name="dummy",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def extract_mesh2vol_outputs(
    # claim_name argument is only used by the @script decorator and is present
    # here only because Hera seems to require it
    log_filename,
    claim_name,
    mount_path,
):
    import sys
    import os
    import re

    if not os.path.isfile(log_filename):
        print(f"Log file {log_filename} not found.")
        print("Exiting")
        sys.exit(1)

    log_file = open(log_filename, "r")
    log_lines = log_file.readlines()
    log_file.close()
    line_of_interest = [
        line for line in log_lines if re.search("Scale.*translate", line)
    ]
    if len(line_of_interest) != 1:
        print(f"Erroneous matching pattern. Found lines: {line_of_interest}")
        print("Exiting")
        sys.exit(1)
    line_of_interest = line_of_interest[0]

    print("aaaaaaa", log_lines)
    print("bbbbbbbb", line_of_interest)
    line_of_interest = line_of_interest.replace("Scale", "")
    line_of_interest = line_of_interest.replace("=", "")
    line_of_interest = line_of_interest.replace("translate", "")
    line_of_interest = line_of_interest.replace(",", "")
    line_of_interest = line_of_interest.replace("(", "").replace(")", "")
    print("ccccccc", line_of_interest)
    numbers = line_of_interest.split()
    scale = numbers[0]
    x_offset = numbers[1]
    y_offset = numbers[2]
    z_offset = numbers[3]
    with open("/tmp/result_scale.txt", "w") as f:
        f.write(scale)
    with open("/tmp/result_x_offset.txt", "w") as f:
        f.write(x_offset)
    with open("/tmp/result_y_offset.txt", "w") as f:
        f.write(y_offset)
    with open("/tmp/result_z_offset.txt", "w") as f:
        f.write(z_offset)

    print("Done.")
