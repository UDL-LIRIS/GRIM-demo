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
            name="offset_x", value_from=ValueFrom(path="/tmp/result_offset_x.txt")
        ),
        Parameter(
            name="offset_y", value_from=ValueFrom(path="/tmp/result_offset_y.txt")
        ),
        Parameter(
            name="offset_z", value_from=ValueFrom(path="/tmp/result_offset_z.txt")
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

    # Keeping digits, . (dot) and minus:
    line_of_interest = line_of_interest[0]
    line_of_interest = line_of_interest.replace("Scale", "")
    line_of_interest = line_of_interest.replace("=", "")
    line_of_interest = line_of_interest.replace("translate", "")
    line_of_interest = line_of_interest.replace(",", "")
    line_of_interest = line_of_interest.replace("(", "").replace(")", "")

    numbers = line_of_interest.split()
    scale = numbers[0]
    offset_x = numbers[1]
    offset_y = numbers[2]
    offset_z = numbers[3]

    with open("/tmp/result_scale.txt", "w") as f:
        f.write(scale)
    with open("/tmp/result_offset_x.txt", "w") as f:
        f.write(offset_x)
    with open("/tmp/result_offset_y.txt", "w") as f:
        f.write(offset_y)
    with open("/tmp/result_offset_z.txt", "w") as f:
        f.write(offset_z)

    print("Done.")
