import requests
import xmltodict
import warnings

import spotlight
from SPARQLWrapper import SPARQLWrapper, JSON

from config import *


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