import re

import langid
from whoswho import who
from polyleven import levenshtein
from ftfy import fix_text


def get_language(string):
    try:
        return langid.classify(string)[0]
    except:
        return 'en'


def string_disambiguation(value, candidates, name=False):

    def get_label(x):
        return x.split('resource')[1][1:].replace('_', ' ')

    if name:
        best_dist, best_match = (-1, -float('inf')), None
        for entity in candidates:
            label = get_label(entity)
            name_sim = who.ratio(label, value)
            neg_lev_dist = -levenshtein(value.lower(), label.lower())
            dist = (name_sim, neg_lev_dist)
            if dist[1] <= 0 and dist > best_dist:
                best_dist = dist
                best_match = entity
    else:
        distances = []
        best_dist, best_match = 999999, None
        for entity in candidates:
            label = get_label(entity)
            dist = levenshtein(value.lower(), label.lower(), best_dist)
            if 0 <= dist < best_dist:
                best_dist = dist
                best_match = entity

    return best_match


def detect_name(value):
    """Checks whether value is a name with a single letter for each
    surname (e.g. G. Vandewiele) and returns the family names if so"""
    match = re.match("^(\w\. )+([\w\-']+)$", value, re.UNICODE)
    if match is not None:
        return match.group(2)
    return None


def clean_cell(s):
    """Apply some sanitization on an input string: 
    (i) use fix_text from ftfy
    (ii) remove % characters;
    (iii) replace double quotes by escaped single quotes; and
    (iv) remove final parts if ( or [ is present"""
    s = fix_text(s.replace('%', ''))
    s = s.replace('"', '').replace('\\', '')
    s = s.split('(')[0].split('[')[0]
    return s

