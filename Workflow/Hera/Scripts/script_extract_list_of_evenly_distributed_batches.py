from typing import List
from hera.workflows import ExistingVolume, Parameter, script


@script(
    image="python:alpine3.6",
    command=["python"],
    add_cwd_to_sys_path=False,
    inputs=[
        Parameter(name="log_filename"),
        Parameter(name="desired_number_of_batches"),
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
def extract_list_of_evenly_distributed_batches(
    log_filename,
    desired_number_of_batches,
    # claim_name and mount_path argument are only used by the @script decorator
    # and are present here only because Hera seems to require it
    claim_name,
    mount_path,
) -> List[int]:
    """
    Compute a list of evenly distributed batches (integers) taken among the
    interval [0, last_batch] where last_batch is
    - extracted from the log_filename file (an output of the decompression
      algorithm),
    - the last and highest batch number

    The length of that [0, last_batch] sublist is given by the parameter
    desired_number_of_batches
    """
    import sys
    import os
    import re
    import json

    debug = False

    if not os.path.isfile(log_filename):
        print(f"Log file {log_filename} not found.", file=sys.stderr)
        print("Exiting", file=sys.stderr)
        sys.exit(1)
    try:
        desired_number_of_batches = int(desired_number_of_batches)
        if debug:
            print(
                "Desired number of batches: ",
                desired_number_of_batches,
                type(desired_number_of_batches),
                file=sys.stderr,
            )
    except:
        print(
            f"Desired number of batches input {desired_number_of_batches} not an int.",
        )
        print("Exiting")
        sys.exit(1)

    ########## First step: extract the highest batch number from the log file
    log_file = open(log_filename, "r")
    log_lines = log_file.readlines()
    log_file.close()
    line_of_interest = [line for line in log_lines if re.search("batch", line)]
    if len(line_of_interest) == 0:
        print(f"Erroneous matching pattern.")
        print("Exiting")
        sys.exit(1)

    # The last (and highest) decompressed batch is the one we are looking for
    line_of_interest = line_of_interest[-1]
    # Keeping digits
    line_of_interest = line_of_interest.replace("batch", "")
    line_of_interest = line_of_interest.replace("done", "")

    # Eventually we have extracted the last/highest batch
    last_bash = int(line_of_interest)
    if debug:
        print("Found last/highest batch: ", last_bash, type(last_bash), file=sys.stderr)

    ########### Second step: construct a list of length desired_number_of_batches
    # of (almost) evenly distributed batch numbers taken among the
    # [0, last_bash] interval.

    result = list()

    if last_bash <= desired_number_of_batches:
        # When they not enough batches, extract all of them (aka 1 LOD per batch):
        result = list(range(last_bash))
    else:
        # number of intervals between LODs
        interval_between_lods = desired_number_of_batches - 1
        if debug:
            print(
                "Intervals between lods: ",
                interval_between_lods,
                type(interval_between_lods),
                file=sys.stderr,
            )

        # Size of one interval (in batches unit)
        interval_size = last_bash // interval_between_lods
        if debug:
            print(
                "Interval size: ",
                type(interval_size),
                interval_size,
                file=sys.stderr,
            )

        # The last one is out of the loop in order to make sure (because of
        # rounding effect) that the last one is last_bash:
        for i in range(interval_between_lods):
            result.append(i * interval_size)
        result.append(last_bash)
        if len(result) != desired_number_of_batches:
            print(f"Erroneous length of batch list: ")
            print("Exiting")
            sys.exit(1)

    ### In order to chain this script with downstream tasks, the output of
    # the script must be in JSON format
    # Reference: https://argo-workflows.readthedocs.io/en/latest/walk-through/loops/#withparam-example-from-another-step-in-the-workflow
    json.dump(result, sys.stdout)
