#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# hours_plot.py

"""
Generate a plot of total hours vs. survival rate, given an Excel spreadsheet of
total hours in the first column and subject status in the second column.
"""

import math
import sys

import numpy as np
import matplotlib.pyplot as plt
import xlrd


CMD_LINE_HELP = '''
Usage: python3 {} [options] [filename]
Options:
    --help, -H          Display this help
            -T          Display a trendline
            -B          Display the variation using boxplots
            -E          Display the variation using error bars
'''

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


def binify(hours, bin_scheme):
    """Return the hours bin for the supplied #hours and bin scheme."""
    if hours < 0:
        raise ValueError, "Negative elapsed time passed to binify()."
    if hours is None:
        return -10
    for (lowerbound, upperbound), increment in bin_scheme.items():
        if lowerbound <= hours < upperbound:
            return int(math.ceil(hours / increment) * increment)
    raise ValueError, "Unhandled value in binify(): {}".format(hours)


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
    if n is None:
        n = len(X)

    resample_i = np.floor(np.random.rand(n) * len(X)).astype(int)
    return X[resample_i]


mapping = dict()  # Key: hours, value: list of subject statuses
bin_scheme = {
    # Key: (lowerbound inclusive, upperbound), value: increment size
    (0, 12): 1,
    (12, 24): 3,
    (24, 48): 6,
    (48, 96): 12,
    (96, float('inf')): 48
}

hours_slice = np.array(days_slice) * 24
hrs_slice = np.array([binify(x, bin_scheme) for x in hours_slice])
assert len(hrs_slice) == len(status_slice)

# Add the status to this hrs bin
# noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
for hrs, status in zip(hrs_slice, status_slice):
    try:
        mapping[hrs].append(status)
    except KeyError:
        mapping[hrs] = list()


def percent_survival(lst):
    return (1.0 - 1.0 * lst.count('DOA') / len(lst)) * 100


def is_doa(x):
    if x == 'DOA':
        return 1
    return 0

x = list(sorted(mapping.keys()))
y = [percent_survival(mapping[hours]) for hours in x]
N = [len(mapping[hours]) for hours in x]
for hours, survival_rate, n in zip(x, y, N):
    print('Survival rate at {} hours = {:.1f}% (N={})'.format(hours, survival_rate, N))

if '-T' in sys.argv:
    z = np.polyfit(x, y, 1, w=N)
    p = np.poly1d(z)
    plt.plot(x, p(x), 'b-', alpha=.7)
    print('Trendline: y = {:.3f}x + {:.3f}'.format(*z))

if '-E' in sys.argv:
    for i, hrs in enumerate(x):
        resampled_rates = np.ones(10)
        outcomes = mapping[hrs]
        bitmask = np.array([is_doa(status) for status in outcomes])
        # print('bitmask: {}'.format(bitmask))
        for j in range(10):
            samples = bootstrap_resample(bitmask, len(outcomes) / 2)
            resampled_rates[j] = np.average(1.0 * samples)
            # print('  samples: {}  <{:.2f}>'.format(samples, resampled_rates[j]))

        # Variation using standard deviations
        stdev_y = 100 * np.std(resampled_rates)
        print('σ of survival rates of bin {} = {:.1f}'.format(hrs, stdev_y))
        # Add 1.96 * stddev_x as fourth argument if you want an xerr errorbar
        plt.errorbar(hrs, y[i], 1.96 * stdev_y, ecolor='b', alpha=.2)

elif '-B' in sys.argv:
    data, positions, widths = list(), list(), list()
    for (lowerbound, upperbound), increment in bin_scheme.items():
        bin_x = [hours for hours in x if lowerbound < hours <= upperbound]
        bin_y = [y[x.index(hours)] for hours in bin_x]
        data.append(bin_y)
        positions.append(np.average(bin_x))
        widths.append(min(20, (upperbound - lowerbound) // 1.5))

    # To set the whiskers to the 95% range, use the optional argument whis=[2.5, 97.5]
    # Only works in matplotlib version > 1.4
    plt.boxplot(data, positions=positions, widths=widths)

plt.title('Total Hours vs. Survival Rate')
plt.xlabel('Total Hours (hours)')
plt.ylabel('Survival Rate (percent)')
plt.xlim((0, 275))
plt.ylim((0, 100))
plt.xticks(range(0, 275, 50))
plt.yticks(range(0, 101, 20))
plt.scatter(x, y, s=N, alpha=.5)
plt.get_current_fig_manager().resize(1250, 881)
plt.show()
