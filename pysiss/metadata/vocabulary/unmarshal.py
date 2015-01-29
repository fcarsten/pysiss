""" file:   unmarshal.py (pysiss.vocabulary)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    description: Wrapper functionality for unmarshalling XML elements
"""

from ..namespaces import shorten_namespace, expand_namespace
from . import gml, gsml, erml, wcs, csw

from lxml.etree import iterparse, XMLSyntaxError

UNMARSHALLERS = {}
UNMARSHALLERS.update(gml.UNMARSHALLERS)
UNMARSHALLERS.update(gsml.UNMARSHALLERS)
UNMARSHALLERS.update(erml.UNMARSHALLERS)
UNMARSHALLERS.update(wcs.UNMARSHALLERS)


def unmarshal(elem):
    """ Unmarshal an lxml.etree.Element element

        If there is no unmarshalling function available, this just returns the
        lxml.etree element.
    """
    tag = shorten_namespace(elem.tag)
    unmarshal = UNMARSHALLERS.get(tag)
    if unmarshal:
        return unmarshal(elem)
    else:
        return None


def unmarshal_all(tree, tag):
    """ Unmarshal all instances of <tag> in a tree
    """
    tag = expand_namespace(tag).lower()
    results = []
    for elem in tree.iter():
        if elem.tag.lower() == tag:
            results.append(unmarshal(elem))
    return results

def unmarshal_all_from_file(file, tag='gsml:MappedFeature'):
    """ Unmarshal all instances of a tag from an xml file
        and return them as a list of objects
    """
    tag = expand_namespace(tag)
    results = []
    with open(filename, 'rb') as fhandle:
        try:
            context = iter(iterparse(fhandle, events=('end',), tag=tag))
            for _, elem in context:
                results.append(unmarshal(elem))
        except XMLSyntaxError:
            pass
    return results
