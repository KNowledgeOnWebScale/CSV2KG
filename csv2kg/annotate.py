import os
import csv

import pandas as pd
import click

from cell_annotation import cell_lookup 


@click.command()
@click.option('--input_file', help='The CSV file to annotate')
@click.option('--target_file', help='The target cells/columns/relations')
@click.option('--output_dir', help='Where to store (temporary) results')
def annotate(input_file, target_file, output_dir):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    targets = pd.read_csv(target_file, header=None)

    raw_values = pd.read_csv(input_file, header=None)
    print('Going to annotate the following file:')
    print(raw_values.head(5))

    ###################################################################
    #       Phase 1: Perform lookups for crude cell annotations       #
    ###################################################################

    cea_targets = targets[targets[0] == 'cell']
    col_targets = set(cea_targets[1])
    cell_targets = set(cea_targets[2])

    lookup_annotations = []
    for cell_ix in cell_targets:
        for col_ix in col_targets:
            if cell_ix >= raw_values.shape[0] or col_ix >= raw_values.shape[1]:
                continue
            value = raw_values.iloc[cell_ix, col_ix]
            lookup = cell_lookup(value)
            lookup_annotations.append([col_ix, cell_ix, lookup])

    lookup_annotations = pd.DataFrame(lookup_annotations)
    lookup_annotations.to_csv('{}/lookup.csv'.format(output_dir),
                              header=False, index=False,
                              quoting=csv.QUOTE_ALL)
    print('Performed lookup')
    print(lookup_annotations.head(5))

    ###################################################################
    #                       Phase 2: Infer columns                    #
    ###################################################################

if __name__ == '__main__':
    annotate()