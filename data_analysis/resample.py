#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# resample.py

"""
Utilities for resampling statistics.

"""

import numpy as np




def bootstrap_resample(X, n=None):
    """ Bootstrap resample an array_like.

    Used for example, to estimate the variance for a single list of binary outcomes.

    Parameters
    ----------
    X : array_like
      data to resample
    n : int, optional
      length of resampled array, equal to len(X) if n==None
    Results
    -------
    returns X_resamples

    From http://nbviewer.ipython.org/gist/aflaxman/6871948
    """
    if n == None:
        n = len(X)

    resample_i = np.floor(np.random.rand(n) * len(X)).astype(int)
    X_resample = X[resample_i]
    return X_resample
