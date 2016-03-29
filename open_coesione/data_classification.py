# -*- coding: utf-8 -*-
import numpy as np


class DataClassifier:
    def __init__(self, data, classifier_class=None, classifier_args=None, colors_map=None):
        if not classifier_class:
            from pysal.esda import mapclassify as mc
            classifier_class = mc.Fisher_Jenks

        self.classifier_class = classifier_class
        self.classifier_args = classifier_args
        self.colors_map = colors_map
        self.data = data

        nu = len(np.unique(self.data))

        if nu == 0:
            self.dc = None
        else:
            self.classifier_args['k'] = min(self.classifier_args['k'], nu)
            self.dc = self.classifier_class(np.array(self.data), **self.classifier_args)

    def get_class(self, value):
        if value == 0:
            return 'c0'

        for n, b in enumerate(self.dc.bins):
            if (n == 0 and value <= self.dc.bins[n]) or (self.dc.bins[n - 1] < value <= self.dc.bins[n]):
                return 'c{}'.format(n + 1)

    def get_color(self, value):
        if not self.colors_map:
            raise Exception('Colors map not specified')
        else:
            return self.colors_map[self.get_class(value)]

    def get_bins_ranges(self):
        """
        returns bins ranges in a dictionaries array:
        start, end
        """
        bins = list(self.dc.bins)
        return [{'start': current, 'end': next} for current, next in zip([1] + bins, bins)]
        # ranges = []
        # for n, b in enumerate(self.dc.bins):
        #     bin_start = 1 if n == 0 else self.dc.bins[n - 1]
        #     bin_end = self.dc.bins[n]
        #
        #     ranges.append({
        #         'start': bin_start,
        #         'end': bin_end,
        #     })
        #
        # return ranges
