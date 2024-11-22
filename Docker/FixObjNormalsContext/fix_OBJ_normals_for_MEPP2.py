#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Fix the normals in an OBJ file for MEPP2.
# Assume that the input file contains "vertex-normals", by opposition to
# "face-normals".
# The output file contains the same number of normal lines as vertex lines to
# force MEPP2 to use "vertex-normals". The extra lines are useless, only
# required by MEPP2 OBJ reader to work properly.
#

import argparse
import shutil

# parse command line arguments
argParser = argparse.ArgumentParser(description='Compare two files value by value.')
argParser.add_argument('input_file')
argParser.add_argument('output_file')
args = argParser.parse_args()

# 1st pass: count number of vertices and number of normals

with open(args.input_file, 'r') as infile:
    vertices_nbr = 0
    normals_nbr  = 0
    for line in infile:
        if line.startswith('v '):
            vertices_nbr += 1
        elif line.startswith('vn '):
            normals_nbr += 1

print(f'number of vertices: {vertices_nbr}')
print(f'number of normals:  {normals_nbr}')

# 2nd pass: add normal lines if needed

if vertices_nbr <= normals_nbr:
    print('nothing to do, copying input to output without any change')
    shutil.copyfile(args.input_file, args.output_file)
else:
    # not enough normals
    # insert normals lines before the 1st face line
    with open(args.input_file, 'r')  as infile, \
         open(args.output_file, 'w') as outfile:
        done = False
        for line in infile:
            if (not done) and line.startswith('f '):
                # insert normal lines
                lines_nbr = vertices_nbr - normals_nbr
                assert lines_nbr > 0
                new_line = 'vn 1 0 0'
                new_lines = [new_line] * lines_nbr
                new_lines = '\n'.join(new_lines)
                outfile.write(new_lines + '\n')
                print(f'{lines_nbr} normals added')
                done = True
            outfile.write(line)


