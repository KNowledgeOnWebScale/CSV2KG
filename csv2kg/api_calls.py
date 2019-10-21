import requests
import xmltodict
import warnings

import spotlight
from SPARQLWrapper import SPARQLWrapper, JSON

from config import *


def get_equivalent_classes(annotation):
    sparql = SPARQLWrapper(SPARQL_URI)
    sparql.setQuery("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?eq
        WHERE { <"""+annotation+"""> owl:equivalentClass ?eq }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    results = [x['eq']['value'] 
               for x in results['results']['bindings'] 
               if x['eq']['value'].startswith('http://dbpedia.org/ontology/')]
    if annotation in eq_classes:
        results.extend(eq_classes[annotation])
    return list(set(results))


def get_parent(x):
    sparql = SPARQLWrapper(SPARQL_URI)
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?parent
        WHERE { <"""+x+"""> rdfs:subClassOf ?parent }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    results = [x['parent']['value'] 
               for x in results['results']['bindings'] 
               if x['parent']['value'] in dbpedia_classes]
    if len(results) > 0:
        return results[0]
    else:
        return None


def get_depth_of_type(x):
    for i in range(8):
        sparql = SPARQLWrapper(SPARQL_URI)
        sparql.setQuery("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            ASK WHERE {
              <"""+x+"""> rdfs:subClassOf{"""+str(i)+"""} owl:Thing . 
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        if results['boolean']:
            return i

    return 0


def is_child(x, y):
    sparql = SPARQLWrapper(SPARQL_URI)
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        ASK WHERE {
          <"""+x+"""> rdfs:subClassOf <"""+y+"""> . 
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results['boolean']


def get_rdf_types(x):
    try:
        sparql = SPARQLWrapper(SPARQL_URI)
        sparql.setQuery("""
            SELECT ?type
            WHERE { <"""+x+"""> a ?type }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        types = [x['type']['value'] for x in results['results']['bindings']]

        return [x for x in types if x in dbpedia_classes]
    except:
        return []


def spotlight_lookup(x, lang='en', conf=0.01):
    url = '{}/{}/annotate'.format(SPOTLIGHT_URI, lang)
    try:
        results = spotlight.annotate(url, x, confidence=conf)

        matches = []
        for result in results:
            result = result['URI'].replace('de.', '').replace('pt.', '')
            result = 'http://' + result.split('://')[1]
            resp = requests.get(result, headers={'Connection': 'close'})
            result = resp.url.replace('/page/', '/resource/')
            matches.append(result)
    except Exception as e:
        warnings.warn('[SPOTLIGHT] Something went wrong with request to '
                      '{}. Returning nothing...'.format(url))
        return []

    return matches


def try_url(x):
    """Replace spaces by underscores and check whether its a valid URI"""
    url = 'http://dbpedia.org/resource/{}'.format(x.replace(' ', '_'))
    try:
        response = requests.get(url, headers={'Connection': 'close'})
        status = response.status_code
        if status == 200:
            return [url]
        else:
            warn_msg = '[TRY_URL] Got code {} with request to {}. '\
                       'Returning nothing...'
            warnings.warn(warn_msg.format(status, url))
            return []
    except Exception as e:
        warnings.warn('[TRY_URL] Something went wrong with request to '
                      '{}. Returning nothing...'.format(url))
        return []


def dbpedia_lookup(value, col_type=None, max_hits=50):
    # URL encode the spaces
    value = str(value).replace(" ", "%20")
    base_url = '{}/api/search/KeywordSearch?MaxHits={}&QueryString="{}"'
    url = base_url.format(DBP_LOOKUP_URI, max_hits, value)
    if col_type is not None:
        # If a col_type is provided, we append an extra 
        # parameter to the API
        url_suffix = '&QueryClass="{}"'.format(col_type)
        url = base_url.format(DBP_LOOKUP_URI, max_hits, value)
        url += url_suffix

    try:
        response = requests.get(url, headers={'Connection': 'close'})
        # Response is in XML, we parse it
        tree = xmltodict.parse(response.content.decode('utf-8'))

        # Check if it contains results
        if 'ArrayOfResult' in tree and 'Result' in tree['ArrayOfResult']:
            result = tree['ArrayOfResult']['Result']

            if isinstance(result, dict):
                parsed_result = [result['URI']]
            else:
                parsed_result = [x['URI'] for x in result]

            return parsed_result
        else:
            return []
    except Exception as e:
        warnings.warn('[DBPEDIA_LOOKUP] Something went wrong with request to '
                      '{}. Returning nothing...'.format(url))
        return []