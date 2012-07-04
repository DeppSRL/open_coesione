import numpy as np
from pysal.esda import mapclassify as mc

class DataClassifier:

    def __init__(self, data, classifier_class=mc.Fisher_Jenks, classifier_args=None, colors_map=None):
        self.classifier_class = classifier_class
        self.classifier_args = classifier_args
        self.colors_map = colors_map
        self.data = data
        self.dc = self.classifier_class(np.array(self.data), **self.classifier_args)


    def get_class(self, value):
        for n, b in enumerate(self.dc.bins):
            if n == 0 and value <= self.dc.bins[n]:
                return 'c0'
            if self.dc.bins[n-1] < value <= self.dc.bins[n]:
                return 'c%s' % n

    def get_color(self, value):
        if not self.colors_map:
            raise Exception("colors map not specified")
        else:
            return self.colors_map[self.get_class(value)]

    def get_bins(self):
        return self.dc.bins