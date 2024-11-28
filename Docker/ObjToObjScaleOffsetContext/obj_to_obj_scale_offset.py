import sys
import argparse

#### Deal with parameters
argParser = argparse.ArgumentParser(description="Apply scale and offset to input file.")
argParser.add_argument(
    "--input_file",
    type=str,
    help="Filename of the input file (obj file format).",
    required=True,
)
argParser.add_argument(
    "--output_file",
    nargs="?",
    type=str,
    help="Filename of the output file (obj file format).",
)
argParser.add_argument(
    "--scale", type=float, help="Scaling factor as given by skeleton extractor."
)
argParser.add_argument(
    "--offset_x",
    type=float,
    help="Offset in the X direction as given by skeleton extractor.",
)
argParser.add_argument(
    "--offset_y",
    type=float,
    help="Offset in the Y direction as given by skeleton extractor.",
)
argParser.add_argument(
    "--offset_z",
    type=float,
    help="Offset in the Z direction as given by skeleton extractor.",
)

args = argParser.parse_args()
if not args.input_file.lower().endswith(".obj"):
    print("Input filename must have an obj extension.")
    print("Exiting.")
    sys.exit(1)

if not args.output_file:
    output_file = args.input_file.split(".")[0] + ".scaled.obj"
else:
    output_file = args.output_file

with open(args.input_file, "r") as infile:
    with open(output_file, "w") as outfile:
        for line in infile:
            split = line.split()
            if split[0] != "v":
                # Not a vertex: just copy the line
                outfile.write(line)
                continue
            x, y, z = split[1:4]
            if args.scale:
                x = float(x) / args.scale
                y = float(y) / args.scale
                z = float(z) / args.scale
            if args.offset_x:
                x -= args.offset_x
            if args.offset_y:
                y -= args.offset_y
            if args.offset_z:
                z -= args.offset_z
            outfile.write(f"v {x} {y} {z}\n")
