from collections import defaultdict

import api_calls as api
import util


def _infer_type(type_counter, entropy_thresh=0.95):
    # Store all the children of a type in a dictionary (hierarchical)
    children_per_type = defaultdict(list)
    for _type1 in type_counter:
        for _type2 in type_counter:
            if _type1 != _type2 and api.is_child(_type2, _type1):
                children_per_type[_type1].append(_type2)

    # Use entropy to find the most specific, AND correct, type
    best_type = max(type_counter.items(), key=lambda x: x[1])[0]
    inferring = True
    while inferring:
        print('---> {} ({})'.format(best_type, 
        						    [(x, type_counter[x]) for x in children_per_type[best_type]]))
        inferring = False
        if len(children_per_type[best_type]) == 1:
            curr_count = type_counter[best_type]
            child_count = type_counter[children_per_type[best_type][0]]
            if child_count >= curr_count // 2:
                best_type = children_per_type[best_type][0]
                inferring = True
        elif len(children_per_type[best_type]) > 1:
            children_counts = [type_counter[child] 
                               for child in children_per_type[best_type]]
            top_counts = sorted(children_counts)[-2:]
            uncertainty = util.normalized_entropy(top_counts)
            if uncertainty < entropy_thresh:
                best_type = max([(x, type_counter[x])
                                for x in children_per_type[best_type]], 
                               key=lambda x: x[1])[0]
                inferring = True
    return best_type


def create_type_counter(entities):
    type_counter = defaultdict(int)
    for entity in entities:
        for _type in api.get_rdf_types(entity):
            type_counter[_type] += 1
    return type_counter


def annotate_column(entities):
    type_counter = create_type_counter(entities)
    annotation = _infer_type(type_counter)

    parent = api.get_parent(annotation)
    while parent is not None:
        annotation = '{} {}'.format(annotation, parent)
        parent = api.get_parent(parent)

    annotations = annotation.split(' ')
    new_annotations = annotations[:]
    for annotation in annotations:
        new_annotations.extend(api.get_equivalent_classes(annotation))

    annotations = list(set(new_annotations))
    annotations = sorted(annotations, key=lambda x: -api.get_depth_of_type(x))
    return ' '.join(annotations)