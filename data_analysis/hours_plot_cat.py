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
    --help, -H                  Display this help
            -T                  Display a trendline
            -B                  Display the variation using boxplots
            -E                  Display the variation using error bars
            -s                  Suppress the default scatterplot
            -C [categories]     Use data from only the listed categories

1. If both -B and -E are included, -E will override -B.
2. If -C [categories] is present, it must be the last option.
3. Categories are separated by spaces.
4. A "*" will include all categories, which is the same as not using -C.

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
    days_slice = sheet.col_values(0)
    status_slice = sheet.col_values(1)
    category_slice = [category.upper() for category in sheet.col_values(2)]
    assert len(days_slice) == len(status_slice) == len(category_slice)
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

selected_categories = set(category_slice)
if '-C' in sys.argv:
    start = sys.argv.index('-C')+1
    if sys.argv[start] != '*':
        selected_categories = [arg.upper() for arg in sys.argv[start:-1]]    

hours_slice = np.array([binify(days * 24, bin_scheme) for days in days_slice])
assert len(hours_slice) == len(status_slice) == len(category_slice)
for hours, status, category in zip(hours_slice, status_slice, category_slice):
    if status != '': # Ignore cases without a known subject status
        if category in selected_categories:
            try:
                mapping[hours].append(status)
            except KeyError:
                mapping[hours] = [status]

x, y, N = list(), list(), list()
for hours in sorted(mapping.keys()):
    survival_rate = percent_survival(mapping[hours])
    num_bins = len(mapping[hours])
    print('Survival rate at {} hours = {:.1f}% (N={})'.format(hours, survival_rate, num_bins))
    x.append(hours)
    y.append(survival_rate)
    N.append(num_bins)

if '-T' in sys.argv:
    z = np.polyfit(x, y, 1, w=N)
    p = np.poly1d(z)
    plt.plot(x, p(x), 'b-', alpha=0.7)
    trend_str = 'Trendline: y = {:.3f}x + {:.3f}'.format(*z)
    print(trend_str)
    plt.text(.02, .02, trend_str, ha='left', va='bottom',
             transform=plt.gca().transAxes, fontsize=10)

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

cat_str = 'All'
cat_list = sorted(selected_categories)
if '-C' in sys.argv and '*' not in sys.argv:
    cat_str = ','.join(cat_list)

plt.suptitle('Total Hours vs. Survival Rate', fontsize=16)
plt.title('%s $(N=%d)$' % (cat_str, sum(N)), fontsize=12)
plt.xlabel('Total Hours (hours)')
plt.ylabel('Survival Rate (percent)')
plt.xlim((0, 250))
plt.ylim((0, 100))
plt.xticks(range(0, 250, 50))
plt.yticks(range(0, 101, 20))
if not '-s' in sys.argv:
    plt.scatter(x_pts, y_pts, s=N_pts, alpha=.5)
plt.get_current_fig_manager().resize(1250, 881)
plt.savefig(cat_str + '.png')
plt.show()
