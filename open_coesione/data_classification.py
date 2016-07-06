# -*- coding: utf-8 -*-
import numpy as np


class DataClassifier:
    def __init__(self, data, classifier_class=None, classifier_args=None):
        if not classifier_class:
            from pysal.esda import mapclassify as mc
            classifier_class = mc.Fisher_Jenks

        nu = len(np.unique(data))

        if nu == 0:
            self.dc = None
        else:
            classifier_args['k'] = min(classifier_args['k'], nu)
            self.dc = classifier_class(np.array(data), **classifier_args)

    def get_bins_ranges(self):
        bins = list(self.dc.bins)
        return [{'start': current, 'end': next} for current, next in zip([0] + bins, bins)]

    def get_class(self, value):
        if value == 0:
            return 'c0'
        else:
            for n, bin_range in enumerate(self.get_bins_ranges(), 1):
                if bin_range['start'] < value <= bin_range['end']:
                    return 'c{}'.format(n)
