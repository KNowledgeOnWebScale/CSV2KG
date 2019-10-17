import api_calls as api
import util


def cell_lookup(value):
    """Use various lookup APIs using the provided value.

    Parameters
    ----------
    value : str
        The cell value to be provided to the different APIs.

    Returns
    -------

    """
    cleaned_value = util.clean_cell(value)
    fam_name = util.detect_name(cleaned_value)
    candidates = api.try_url(cleaned_value)
    if fam_name is not None:  # We detected a name and only use family name
        candidates += api.dbpedia_lookup(fam_name)
        candidates += api.try_url(fam_name)
    else:
        lang = util.get_language(cleaned_value)
        candidates += api.dbpedia_lookup(cleaned_value)

    if len(candidates) <= 1:
        lang = util.get_language(cleaned_value)
        candidates = api.spotlight_lookup(cleaned_value, lang=lang)

    if candidates:
        return util.string_disambiguation(cleaned_value, candidates, 
                                          name=fam_name is not None)
    else:
        return None
