import argparse

import json

import os

import shutil

import types

from colmap_utils import import_features, reconstruct


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--dataset_path', type=str, required=True,
        help='path to the dataset'
    )

    parser.add_argument(
        '--colmap_path', type=str, required=True,
        help='path to the COLMAP executable folder'
    )

    parser.add_argument(
        '--method_name', type=str, required=True,
        help='name of the method'
    )
    parser.add_argument(
        '--matches_file', type=str, required=True,
        help='path to the matches file'
    )
    parser.add_argument(
        '--solution_file', type=str, default=None,
        help='path to the multi-view optimization solution file (leave None for no refinement)'
    )

    parser.add_argument(
        '--output_file', type=str, required=True,
        help='path to the output file'
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    refine = (args.solution_file is not None)

    paths = types.SimpleNamespace()
    paths.database_path = os.path.join(
        args.dataset_path, '%s-%s.db' % (args.method_name, 'ref' if refine else 'raw')
    )
    paths.image_path = os.path.join(
        args.dataset_path, 'images'
    )
    paths.match_list_path = os.path.join(
        args.dataset_path, 'match-list.txt'
    )
    paths.sparse_path = os.path.join(
        args.dataset_path, 'sparse-%s-%s' % (args.method_name, 'ref' if refine else 'raw')
    )

    if os.path.exists(paths.database_path):
        raise FileExistsError('Database file already exists.')
    shutil.copy(
        os.path.join(args.dataset_path, 'database.db'),
        paths.database_path
    )

    matching_stats = import_features(
        args.colmap_path, args.method_name,
        paths.database_path, paths.image_path, paths.match_list_path,
        args.matches_file, args.solution_file
    )
    reconstruction_stats = reconstruct(
        args.colmap_path,
        paths.database_path, paths.image_path, paths.sparse_path
    )

    with open(args.output_file, 'w') as f:
        f.write(json.dumps(matching_stats))
        f.write('\n')
        f.write(json.dumps(reconstruction_stats))


if __name__ == '__main__':
    main()
