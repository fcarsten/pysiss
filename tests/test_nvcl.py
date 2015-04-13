""" file:   test_nvcl.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   Tuesday 13 May, 2014

    description: Tests for NVCL importer
"""

from __future__ import print_function, division

from pysiss.webservices import nvcl

import unittest
import httmock

from .mocks.resource import mock_resource


class TestNVCLEndpointRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = nvcl.NVCLEndpointRegistry()

    def test_noclobber_ident(self):
        """ Check that existing idents are not clobbered
        """
        urls = ('a/url', 'b/url', 'c/url')
        self.assertRaises(KeyError, self.registry.register, 'CSIRO', *urls)

    def test_update(self):
        """ Check that endpoint data is updated
        """
        # Add a new key and then update it
        keys = ('wfsurl', 'dataurl', 'downloadurl')
        urls = ('a/url', 'b/url', 'c/url')
        self.registry.register('myendpoint', *urls)
        for url, key in zip(urls, keys):
            self.assertEqual(url, self.registry['myendpoint'][key])

        # Update the keys
        updated_urls = ('d/url', 'e/url', 'f/url')
        self.registry.register('myendpoint', *updated_urls,
                               update=True)
        for url, key in zip(updated_urls, keys):
            self.assertEqual(url, self.registry['myendpoint'][key])

        # Remove bogus data
        del self.registry['myendpoint']

    def test_singleton(self):
        """ Check that only one instance of the registry
            is instantiated
        """
        self.assertEqual(nvcl.NVCLEndpointRegistry(),
                          self.registry)

    def tearDown(self):
        # Remove test changes to registry
        try:
            del self.registry['myendpoint']
        except KeyError:
            # It's already deleted, or never existed anyway
            pass


class TestNVCLImporter(unittest.TestCase):

    """ Test NVCLImporter class
    """

    def setUp(self):
        # Get a pointer to the NVCL endpoint registry
        self.registry = nvcl.NVCLEndpointRegistry()

        # Make importers for each default endpoint
        self.importers = {}
        for ept in self.registry.keys():
            self.importers[ept] = nvcl.NVCLImporter(ept)

    def test_usage_1(self):
        """ Test some sample usage using the GSWA endpoint
        """
        with httmock.HTTMock(mock_resource):
            bh_info = self.importers['GSWA'].get_borehole_idents_and_urls()

            for ident, url in dict(bh_info).items():
                self.assertTrue(ident != '')
                self.assertTrue(url != '')

    def test_usage_2(self):
        """ Test some sample usage using the GSWA endpoint
        """
        borehole_ident = 'PDP2C'
        with httmock.HTTMock(mock_resource):
            # Get the datasets assocated with the borehole ident
            self.importers['GSWA'].get_dataset_idents(borehole_ident)

    def test_usage_3(self):
        """ Test some sample usage using the GSWA endpoint
        """
        with httmock.HTTMock(mock_resource):
            self.importers['GSWA'].get_borehole('PDP2C', get_analytes=True)
