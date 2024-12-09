def at_distance_one(x1, y1, z1, x2, y2, z2):
    """
    We consider voxels on a regular (integer) grid and assume the vertex
    v_one(x1, y1, z1) is given. Return True when both following conditions are met
    - the vertex v_two(x2, y2, z2) is at topological distance of 1 from v_one
    - v_two is not the same vertex as v_one.
    Return False otherwise
    """
    if x1 == x2 and y1 == y2 and z1 == z2:
        # This is the same vertex and thus distance is zero (not one)
        return False
    return (abs(x1 - x2) <= 1) and (abs(y1 - y2) <= 1) and (abs(z1 - z2) <= 1)


def checkExtension(filename, expected_extension):
    return filename.lower().endswith(expected_extension.lower())


if __name__ == "__main__":
    import argparse
    import sys
    import os
    import copy
    from pathlib import Path

    # Parse command line arguments
    argParser = argparse.ArgumentParser(
        description="Convert a skeleton file (SDP extension) to an undirected graph of lines (OBJ extension)."
    )
    argParser.add_argument(
        "--input_file",
        type=str,
        help="Filename of the input file (sdp file format).",
        required=True,
    )
    argParser.add_argument(
        "--output_file", type=str, help="Filename of the output file (obj file format)."
    )

    args = argParser.parse_args()

    if not checkExtension(args.input_file, ".sdp"):
        print("Input filename must have an sdp extension.")
        print("Exiting.")
        sys.exit(1)

    if not args.output_file:
        outputFilePath = args.input_file.split(".")[0] + ".obj"
    else:
        if not checkExtension(args.output_file, ".obj"):
            print("Output filename must have an obj extension.")
            print("Exiting.")
            sys.exit(1)
        outputFilePath = args.output_file
    if os.path.isfile(outputFilePath):
        print(f"Output filename {outputFilePath} already exists.")
        renamedFilePath = outputFilePath + ".renamed"
        print(f"Renaming already existing file {outputFilePath} to {renamedFilePath}.")
        os.rename(outputFilePath, renamedFilePath)

    # Read from input file and write to output file
    with open(args.input_file, "r") as inFile:
        # Lines to be used within the outer loop (refer below)
        lines_outer = inFile.readlines()

        with open(outputFilePath, "w") as outFile:
            # First, assert the vertices coordinates are all integer numbers
            # (otherwise this is not a true SDP file.
            for outer_index in range(len(lines_outer)):
                try:
                    x_int, y_int, z_int = map(
                        lambda x: int(x),
                        lines_outer[outer_index].strip().split(),
                    )
                except ValueError:
                    print(
                        f"Erroneous integer entry on line {outer_index}: {lines_outer[outer_index]} "
                    )
                    print(f"in file {args.input_file}")
                    print("Exiting.")
                    sys.exit(1)
                outFile.write(f"v {x_int} {y_int} {z_int}\n")
            #### Then find the lines connecting those vertices. Let's make it
            # brute force (that O(n^2)) with two loops (outer and inner).
            # Lines to be used within the inner loop (refer below)
            lines_inner = copy.deepcopy(lines_outer)
            for outer_index in range(len(lines_outer)):
                # No need to check on the conversion because we already did
                x_int_outer, y_int_outer, z_int_outer = map(
                    lambda x: int(x),
                    lines_outer[outer_index].strip().split(),
                )
                for inner_index in range(len(lines_inner)):
                    x_int_inner, y_int_inner, z_int_inner = map(
                        lambda x: int(x),
                        lines_inner[inner_index].strip().split(),
                    )
                    if not at_distance_one(
                        x_int_outer,
                        y_int_outer,
                        z_int_outer,
                        x_int_inner,
                        y_int_inner,
                        z_int_inner,
                    ):
                        continue
                    # Adding one to index because line to index correspondance
                    outFile.write(f"l {outer_index+1} {inner_index+1}\n")
