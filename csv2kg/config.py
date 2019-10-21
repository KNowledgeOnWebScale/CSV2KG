import pandas as pd
from collections import defaultdict


DBP_LOOKUP_URI = "http://lookup.dbpedia.org"
SPOTLIGHT_URI = "http://model.dbpedia-spotlight.org"
SPARQL_URI = "https://dbpedia.org/sparql"

dbpedia_classes = open('data/classes.txt', 'r').readlines()
dbpedia_classes = [x.strip() for x in dbpedia_classes]

eq_classes = pd.read_csv('data/equivalent.csv')
mapping = defaultdict(list)
for i, row in eq_classes.iterrows():
    mapping[row['o']].append(row['s'])
    mapping[row['s']].append(row['o'])