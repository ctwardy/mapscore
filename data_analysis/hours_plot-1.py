#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# hours_plot.py

"""
Generate a plot of total hours vs. survival rate, given an Excel spreadsheet of
total hours in the first column and subject status in the second column.
"""

import math
import sys

import matplotlib.pyplot as plt
import numpy as np
import xlrd


CMD_LINE_HELP = '''Usage: python3 {} [options] [filename]
Options:
    --help, -H          Display this help
            -T          Display a trendline
            -B          Display the variation using boxplots
            -E          Display the variation using error bars

If both -B and -E are included, -E will override -B.
'''


def binify(hours, bin_scheme):
    """Return the hours bin for the supplied #hours and bin scheme."""
    if hours < 0:
        raise ValueError("Negative elapsed time passed to binify().")
    if hours is None:
        return -10
    for (lowerbound, upperbound), increment in bin_scheme.items():
        if lowerbound <= hours < upperbound:
            return int(math.ceil(hours / increment) * increment)
    raise ValueError("Unhandled value in binify(): {}".format(hours))


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


def percent_survival(lst):
    return (1.0 - 1.0 * lst.count('DOA') / len(lst)) * 100


def is_doa(x):
    if x == 'DOA':
        return 1
    return 0


if len(sys.argv) < 2 or '--help' in sys.argv or '-H' in sys.argv:
    print(CMD_LINE_HELP.format(sys.argv[0]))
    exit(1)
else:
    filename = sys.argv[-1]
    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_index(0)
    days_slice, status_slice = sheet.col_values(0), sheet.col_values(1)
    assert len(days_slice) == len(status_slice)
    print('Number of cases: {}'.format(len(days_slice)))

mapping = dict()    # Key: (lowerbound inclusive, upperbound), value: subject status list
bin_scheme = {
    # Key: (lowerbound inclusive, upperbound), value: increment size
    (0, 12): 1,
    (12, 24): 3,
    (24, 48): 6,
    (48, 96): 12,
    (96, float('inf')): 48
}

hours_slice = np.array([binify(days * 24, bin_scheme) for days in days_slice])
assert len(hours_slice) == len(status_slice)
for hours, status in zip(hours_slice, status_slice):
    try:
        mapping[hours].append(status)
    except KeyError:
        mapping[hours] = [status]

x, y, N = list(), list(), list()
for hours in sorted(mapping.keys()):
    survival_rate = percent_survival(mapping[hours])
    n = len(mapping[hours])
    print('Survival rate at {} hours = {:.1f}% (N={})'.format(hours, survival_rate, n))
    x.append(hours)
    y.append(survival_rate)
    N.append(n)

if '-T' in sys.argv:
    z = np.polyfit(x, y, 1, w=N)
    p = np.poly1d(z)
    plt.plot(x, p(x), 'b-', alpha=0.7)
    print('Trendline: y = {:.3f}x + {:.3f}'.format(*z))

x_pts, y_pts, N_pts = list(), list(), list()

data = list() # For boxplots, if necessary
for lowerbound, upperbound in bin_scheme:
    selected_hours = list(hours for hours in x
                        if lowerbound <= hours < upperbound)
    survival_rates = [y[x.index(hours)] for hours in selected_hours]
    x_pts.append(np.average(selected_hours))
    y_pts.append(np.average(survival_rates))
    N_pts.append(sum(N[x.index(hours)] for hours in selected_hours))
    if '-E' in sys.argv:
        stdev_y = np.std(survival_rates)
        plt.errorbar(x_pts[-1], y_pts[-1], 1.96 * stdev_y, ecolor='b', alpha=0.2)
    elif '-B' in sys.argv:
        data.append(survival_rates)

if '-B' in sys.argv and '-E' not in sys.argv:
    plt.boxplot(data, positions=x_pts, widths=[10] * len(x_pts))

plt.title('Total Hours vs. Survival Rate')
plt.xlabel('Total Hours (hours)')
plt.ylabel('Survival Rate (percent)')
plt.xlim((0, 275))
plt.ylim((0, 100))
plt.xticks(range(0, 275, 50))
plt.yticks(range(0, 101, 20))
plt.scatter(x_pts, y_pts, s=N_pts, alpha=.5)
plt.get_current_fig_manager().resize(1250, 881)
plt.show()
