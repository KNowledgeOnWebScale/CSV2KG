import os

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

    cea_targets = targets[targets[0] == 'cell']
    col_targets = list(cea_targets[1])
    cell_targets = list(cea_targets[2])

    lookup_annotations = []
    for cell_ix in cell_targets:
        for col_ix in col_targets:
            value = raw_values.iloc[cell_ix, col_ix]
            lookup = cell_lookup(value)
            lookup_annotations.append([col_ix, cell_ix, lookup])
    lookup_annotations = pd.DataFrame(lookup_annotations)
    lookup_annotations.to_csv('{}/lookup.csv'.format(output_dir))
    print('Performed lookup')
    print(raw_values.head(5))

if __name__ == '__main__':
    annotate()