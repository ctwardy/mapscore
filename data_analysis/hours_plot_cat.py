#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# hours_plot_cat.py

"""
Generate a plot of total hours vs. survival rate, given an Excel spreadsheet of
cases, each with the total hours in the first column, the subject status in 
the second column, and the subject category in the third.
"""

import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import xlrd

from resample import *


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
   a. Categories are separated by spaces.
   b. To include all categories, omit -C. 

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


def percent_survival(lst):
    """Return the percentage of non-DOA entries in the Status list."""
    return (1.0 - 1.0 * lst.count('DOA') / len(lst)) * 100


def is_doa(x):
    return x == 'DOA'

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

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
    print('Number of cases in file : {:5d}'.format(len(days_slice)))

SCATTER = True
TRENDLINE = False
BOXPLOTS = False
ERRORBARS = False
CATEGORIES = set(category_slice)
cat_str = 'All'

if '-s' in sys.argv:
    SCATTER = False
if '-T' in sys.argv:
    TRENDLINE = True
if '-B' in sys.argv:
    BOXPLOTS = True
if '-E' in sys.argv:
    ERRORBARS = True
if '-C' in sys.argv:
    start = sys.argv.index('-C')+1
    CATEGORIES = [arg.upper() for arg in sys.argv[start:-1]]    
    cat_str = ','.join(sorted(CATEGORIES))

# Define a bin scheme
# Default increments: [ 6, 12, 24, 48, 256]
# Increments for All: [ 3,  4,  6, 24,  96]
# Increments for Des: [ 6, 12, 24, 48, 128]
# Pfau Bins         : [24, 48, 72, 96, INF]
# Pfau Increments   : [24, 24, 24, 24, 256]
INF = float('inf')
bin_scheme = {
    # Key: (lowerbound inclusive, upperbound), value: increment size
    ( 0, 24):  24,
    (24, 48): 24,
    (48, 72): 24,
    (72, 96): 24,
    (96, INF): 256
}

# Create hours and binified hours columns, and zip everything into 'data'
hours_slice = np.array(days_slice)*24
binhours_slice = np.array([binify(days * 24, bin_scheme) for days in days_slice])
assert len(binhours_slice) == len(hours_slice) == len(status_slice) == len(category_slice)
data = zip(binhours_slice, hours_slice, status_slice, category_slice)

# Populate dictionaries for status and hours keyed on binhours
statuses = {}     # Key: binhours, value: subject status list
real_hours = {}   # Key: binhours, value: real hours list
for binhours, hours, status, category in data:
    if status != '' and category in CATEGORIES:
        try:
            statuses[binhours].append(status)
        except KeyError:
            statuses[binhours] = [status]
        try:
            real_hours[binhours].append(hours)
        except KeyError:
            real_hours[binhours] = [hours]
print('Number of cases selected: {:5d}'.format(len(statuses)))

# Create a datapoint <x,y,n,s> for each binhours entry.
Xs, Ys, Ns, Ss = [], [], [], []
for binhours in sorted(statuses.keys()):
    outcomes = statuses[binhours]
    survival_rate = percent_survival(outcomes)
    num_cases = len(outcomes)
    times = real_hours[binhours]
    meantime = np.mean(times)
    DOAs = np.array([is_doa(x) for x in outcomes])
    surv_rates = [1-np.mean(bootstrap_resample(DOAs)) for i in range(20)]
    stdev = np.std(surv_rates)*100
    print('Survival rate at {} hours = {:.1f}% (N={}, sigma={:.1f}%, <t>={:.0f})'.format(
        binhours, survival_rate, num_cases, stdev, meantime))
    Xs.append(meantime)
    Ys.append(survival_rate)
    Ns.append(num_cases)
    Ss.append(stdev)
Xs = np.array(Xs)
Ys = np.array(Ys)
Ns = np.array(Ns)
Ss = np.array(Ss)

if TRENDLINE:
    Zs = np.polyfit(Xs, Ys, 1, w=Ns)
    P = np.poly1d(Zs)
    plt.plot(Xs, P(Xs), 'b-', alpha=0.7)
    trend_str = 'Trendline: y = {:.3f}x + {:.3f}'.format(*Zs)
    print(trend_str)
    plt.text(.02, .02, trend_str, ha='left', va='bottom',
             transform=plt.gca().transAxes, fontsize=10)

if BOXPLOTS and not ERRORBARS:
    # TODO: Revisit this -- seems a bit dodgy.   -crt
    print "***** Check the boxplot code *****"
    x_pts, y_pts, N_pts = list(), list(), list()
    box_data = list() # For boxplots, if necessary
    for lowerbound, upperbound in bin_scheme:
        selected_hours = list(hours for hours in x
                            if lowerbound <= hours < upperbound)
        survival_rates = [y[x.index(hours)] for hours in selected_hours]
        x_pts.append(np.average(selected_hours))
        y_pts.append(np.average(survival_rates))
        N_pts.append(sum(N[x.index(hours)] for hours in selected_hours))
        box_data.append(survival_rates)
    plt.boxplot(box_data, positions=x_pts, widths=[10] * len(x_pts))

plt.suptitle('Total Hours vs. Survival Rate', fontsize=16)
plt.title('%s $(N=%d)$' % (cat_str, sum(Ns)), fontsize=12)
plt.xlabel('Total Hours')
plt.ylabel('Survival Rate (percent)')
plt.xticks(range(0, 240, 24))
plt.yticks(range(0, 101, 20))
plt.xlim((-2, 170))
plt.ylim((0, 100))
if SCATTER:
    plt.scatter(Xs, Ys, s=Ns, alpha=.5)
if ERRORBARS:
    plt.errorbar(Xs, Ys, 1.96*Ss, ecolor='b', alpha=0.2)
plt.get_current_fig_manager().resize(1250, 881)
plt.savefig(cat_str + '.png')
plt.show()
