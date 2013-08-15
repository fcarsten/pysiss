#!/usr/bin/env python
""" file:   __init__.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of the borehole_analysis module.
"""

import sklearn
import cwavelets
import borehole_analysis.analyser as analyser
from analyser import Analyst
from borehole_analysis.borehole import Borehole
import borehole_analysis.importers as importers
import borehole_analysis.domaining as domaining
from borehole_analysis.domaining import Domainer
from borehole_analysis.domains import Domain, \
    SamplingDomain, IntervalDomain, Property, PropertyType
import borehole_analysis.plotting as plotting

# Reassign the data classes to the base namespace
OBJECTS = [Borehole, Analyst, Domainer, Domain, \
    SamplingDomain, IntervalDomain, Property, PropertyType]
for obj in OBJECTS:
    obj.__module__ = 'borehole_analysis'