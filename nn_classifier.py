#!/usr/bin/env python

'''Wrapper for nearest-neighbor classifier

This script defines the NNClassifier class, which is used from train_myo_ros and
classify_myo_ros for training of gestures and their classification. It stores the
training data in the files vals0.dat, vals1.dat, ..., vals9.dat.
When the library sklearn is available a KNeighborsClassifier will be used for 
classification, otherwise the class of the nearest neighbor is returned.
This script is based on the myo.py file of the myo-raw project. 
(see https://github.com/dzhu/myo-raw/ which is available under the MIT LICENSE)

Following changes where made:
  - Removed code for the myo device, keeping the NNClassifier class.
'''

from __future__ import print_function

import struct

import numpy as np
try:
    from sklearn import neighbors, svm
    HAVE_SK = True
except ImportError:
    HAVE_SK = False

def pack(fmt, *args):
    return struct.pack('<' + fmt, *args)

SUBSAMPLE = 3
K = 15

class NNClassifier(object):
    '''A wrapper for sklearn's nearest-neighbor classifier that stores
    training data in vals0, ..., vals9.dat.'''

    def __init__(self):
        for i in range(10):
            with open('vals%d.dat' % i, 'ab') as f: pass
        self.read_data()

    def store_data(self, cls, vals):
        with open('vals%d.dat' % cls, 'ab') as f:
            f.write(pack('8H', *vals))
            # for i in range(8):
            #    f.write("%d " % vals[i])
            # f.write("\n")
        self.train(np.vstack([self.X, vals]), np.hstack([self.Y, [cls]]))

    def read_data(self):
        X = []
        Y = []
        for i in range(10):
            X.append(np.fromfile('vals%d.dat' % i, dtype=np.uint16).reshape((-1, 8)))
            # X.append(np.fromfile('vals%d.dat' % i, dtype=np.uint16, sep=" ").reshape((-1, 8)))
            Y.append(i + np.zeros(X[-1].shape[0]))
        self.train(np.vstack(X), np.hstack(Y))

    def train(self, X, Y):
        self.X = X
        self.Y = Y
        if HAVE_SK and self.X.shape[0] >= K * SUBSAMPLE:
            self.nn = neighbors.KNeighborsClassifier(n_neighbors=K, algorithm='kd_tree')
            self.nn.fit(self.X[::SUBSAMPLE], self.Y[::SUBSAMPLE])
        else:
            self.nn = None

    def nearest(self, d):
        dists = ((self.X - d)**2).sum(1)
        ind = dists.argmin()
        return self.Y[ind]

    def classify(self, d):
        if self.X.shape[0] < K * SUBSAMPLE: return 0
        if not HAVE_SK: return self.nearest(d)
        return int(self.nn.predict(d)[0])
    
    def clearGestureFiles(self):
        for i in range(10):
            with open('vals%d.dat' % i, 'w') as f:
                f.truncate()
            self.read_data()