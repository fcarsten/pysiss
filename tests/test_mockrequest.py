""" file:  test_borehole_collection.py
    author: Jess Robertson
            Minerals Down Under
    date:   today

    description: Tests for mock Resource class.
"""

from mocks.resource import Resource

import unittest
import simplejson
import httmock
import os


class TestResource(unittest.TestCase):

    def setUp(self):
        fname = os.path.join(os.path.dirname(__file__),
                             'mocks', 'mocks.json')
        with open(fname, 'rb') as fhandle:
            self.mocks = simplejson.load(fhandle)
        self.test_key, self.test_endpoint = self.mocks.items()[0]

    def test_init(self):
        """ Resource should initialize with no errors
        """
        resource = Resource(**self.test_endpoint)
        expected_attrs = ['data', 'method', 'params', 'url']
        for attr in expected_attrs:
            self.assertTrue(getattr(resource, attr) is not None)

    def test_wrong_url(self):
        """ Resource should return a 404 on error
        """
        self.test_endpoint['params'] = {'quux': 'foobar'}
        resource = Resource(**self.test_endpoint)
        response = resource.response()
        self.assertTrue(response.status_code == 404)