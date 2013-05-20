#!/usr/bin/env python
""" file:   borehole.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Data munging utilities for the borehole_analysis module.
"""

import numpy
import functools
import itertools
from csv import DictReader
from borehole_analysis.utilities import ReSampler

def mask_all_nans(*arrays):
    """ Mask all indices where any array has a NaN.

        Example usage:

            >>> mask = mask_all_nans(array1, array2)
            >>> array1[mask]            # Both of these are guarenteed 
            >>> array2[mask]            # to be nan-free

        :param *arrays: The arrays to generate masks for. They should all have the same size or a ValueError will be raised.
        :type *arrays: `numpy.ndarrays` 
        :returns: A `numpy.boolean_array` which can be used as a mask.
    """
    # Convert arrays to numpy arrays if required
    try:
        arrays = [numpy.asarray(a, dtype=numpy.float_) for a in arrays]
    except ValueError:
        raise ValueError("Arrays supplied to mask_all_nans must be able to be "
            "converted to floats!")

    # Check that everything has the same shape
    shapes = [a.shape for a in arrays]
    if any([s != shapes[0] for s in shapes]):
        raise ValueError("Arrays supplied to mask_all_nans must be the same "
            "size (arrays have shapes {0})".format(shapes))

    # Return the non-nan indices
    return numpy.logical_not(functools.reduce(numpy.logical_or, 
                                    [numpy.isnan(a) for a in arrays]))

class Borehole(object):

    """ A class to manage borehole data

        :param data: A dict containing the following keys: 'ID', with an ID 
            for the dataset, 'label', with the label of the dataset as a 
            value, 'domain', with the sample locations, and 'signal', with the 
            signal values corresponding to the sample locations in 'domain'.
        :type data: tuple
    """

    def __init__(self, verbose=False):
        super(Borehole, self).__init__()
        
        # Initialise attributes
        self.verbose = verbose
        self.samplers = {}
        self.labels = {}
        self.data = None
        self.domain = None
        self.default_sprops = {
            'nsamples': None,
            'domain_bounds': None
        }

    def add_datum(self, domain, signal, key, label=None):
        """ Add a single dataset to the Borehole
        """
        # Update names and symbols
        if label is None:
            label = key
        self.labels.update({key: (None, label)})
        self.print_info(
            'Adding dataset {0} with {1} entries, and label {2}'.format(
                key, len(signal), label), 'info')

        # Mask out Nans before generating resampler instance
        nan_mask = mask_all_nans(domain, signal)
        self.samplers[key] = ReSampler(
            domain = domain[nan_mask],
            signal = signal[nan_mask], 
            order=1)

        # Check whether this will change the bounds of the domain
        if self.default_sprops['nsamples'] is None:
            self.default_sprops['nsamples'] = len(domain[nan_mask])
            self.default_sprops['domain_bounds'] = (domain[nan_mask].min(), 
                domain[nan_mask].max())
        else:
            self.default_sprops['nsamples'] = max(
                self.default_sprops['nsamples'], 
                len(domain[nan_mask]))
            self.default_sprops['domain_bounds'] = (
                max(self.default_sprops['domain_bounds'][0], 
                    domain[nan_mask].min()),
                min(self.default_sprops['domain_bounds'][1], 
                    domain[nan_mask].max()))

    def resample(self, nsamples=None, domain_bounds=None, normalize=False):
        """ Aligns and resamples data so that all vectors have the same length
            and sample spacing.

            This generates `data` and `domain` attributes for the Borehole 
            instance. The domain is a one-dimensional vector of length 
            `nsamples` containing the sample locations, and the `data` 
            instance is an array where each column contains the resampled data 
            for one of the datasets in the borehole.

            This uses masked arrays to remove NaN values from a series, and 
            then realigns the data sampling so that all signals are sampled at 
            the same time. It does this using linear interpolation.

            If `normalize=True`, then the data is then normalised so that 
            each column has zero mean and unit variance. To clear this (and go 
            back to unnormalised data), just call resample again wiht 
            `normalize=False`
        """
        # Align data
        self.print_info('Aligning datasets', 'info')

        # Define domain vector
        sampler_properties = self.default_sprops
        if nsamples is not None:
            sampler_properties['nsamples'] = nsamples
        if domain_bounds is None:
            sampler_properties['domain_bounds'] = domain_bounds

        # Generate empty data array and populate with data
        ndata = len(self.samplers)
        self.data = numpy.empty((ndata, sampler_properties['nsamples']), 
                                dtype=numpy.float)
        for index, key_and_sampler in enumerate(self.samplers.items()):
            key, sampler = key_and_sampler
            resampled_domain, resampled_signal = \
                sampler.resample(**sampler_properties) 
            self.data[index] = resampled_signal
            self.labels[key] = (index, self.labels[key][1])

        # Transpose data
        self.data = self.data.T
        self.domain = resampled_domain

        # Generate normalised data if required
        if normalize:
            self.print_info('Normalising datasets', 'info')
            self.data = (self.data - self.data.mean(axis=0)) \
                        / self.data.std(axis=0)

    def get_raw_data(self, *keys):
        """ Returns the raw data used in the Borehole resamplers.
        """
        if keys is None:
            keys = self.labels.keys()

        data = {}
        for key in keys:
            data[key] = dict(
                key=key,
                signal=self.samplers[key].signal, 
                domain=self.samplers[key].domain, 
                label=self.labels[key])

        return data

    def get_labels(self, *keys):
        """ Return the labels for the given keys. If no keys are specified, 
            return labels for all keys.
        """
        if not keys:
            return [v[1] for v in self.labels.values()]
        else:
            return [value[1] for key, value in self.labels.items()
                             if key in keys]

    def get_domain(self):
        """ Returns a view of the current domain
        """
        return self.domain

    def get_signal(self, *keys):
        """ Returns views of the current data for the given keys. If no keys 
            are specified, return views for all keys.
        """
        if keys is None:
            keys = self.labels.keys()
        indices = [self.labels[k][0] for k in keys]
        return dict((k, self.data.T[i]) for k, i in zip(keys, indices))

    def import_from_csv(self, filename, domain_key, data_keys, labels=None):
        """ Import table from a CSV file. 

            Don't try to read massive files in with this - it will probably 
            fall over.
        """
        if labels is None:
            labels = {}

        # Parse data from csv file
        with open(filename, 'rb') as fhandle:
            # Read in data to DictReader
            reader = DictReader(fhandle)
            data_dicts = [l for l in reader]
            
            # Generate the list of dicts
            all_keys = [domain_key] + data_keys
            all_data = dict([(k, []) for k in all_keys])
            
            # Cycle through and convert where necessady
            for ddict in data_dicts:
                current_dict = dict(zip(all_keys, itertools.repeat(numpy.nan)))
                current_dict.update(ddict)
                for key, value in current_dict.items():
                    if key in all_keys:
                        try:
                            # This should work 99% of the time because most 
                            # things are numbers
                            all_data[key].append(float(value))
                        except ValueError:
                            # We need floats, so just tag with NaN
                            all_data[key].append(numpy.nan)

        # Convert arrays to numpy arrays
        all_data = dict([(k, numpy.asarray(all_data[k])) for k in all_keys])
        domain_data = numpy.asarray(all_data[domain_key])
        del all_data[domain_key]

        # Add the datasets that need adding
        for key, dataset in all_data.items():
            try:
                label = labels[key]
            except KeyError:
                label = None
            self.add_datum(
                domain=domain_data,
                signal=dataset,
                key=key,
                label=label)

    def print_info(self, message, flag=None):
        """ Print a message if we're tracking transformations
        """
        header_dict = {
            'default': '         ',
            'info': '   info: ',
            'warn': 'warning: '
        }
        if self.verbose:
            try:
                header = header_dict[flag]
            except KeyError:
                header = header_dict['default']
            print header, message