# CSV2KG

This repository contains a CLI that can be used to convert CSV files into "Semantic Knowledge". It can link the raw cell values to DBPedia entities, infer the probable class of a column and draw relations between the entities.

## Usage

```
Usage: annotate.py [OPTIONS]

Options:
  --input_file TEXT   The CSV file to annotate
  --target_file TEXT  The target cells/columns/relations
  --output_dir TEXT   Where to store (temporary) results
  --help              Show this message and exit.
```

## Example

### Input Data

```
Y. Khamis,Al-Wasl,Dubai,1982-07-23
W. Foulke,Chelsea F.C.,Shropshire,1874-04-12
T. Revill,Stoke City F.C.,England,1892-5-9
```

### Targets

```
cell,2,6
cell,2,7
cell,2,8
cell,2,9
column,0,0
column,1,1
column,2,2
property,0,1
```

`python3 annotate.py --input_file=example_input.csv --target_file=example_targets.csv --output_dir=output`

## References
* [Paper](http://www.cs.ox.ac.uk/isg/challenges/sem-tab/papers/IDLab.pdf) 
* [Poster](...)
* [Presentation](...)


Written and maintained by [Gilles Vandewiele](https://github.com/GillesVandewiele/) and [Bram Steenwinckel](https://github.com/bsteenwi)