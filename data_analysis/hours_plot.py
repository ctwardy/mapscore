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

mapping = dict()  # Key: hours, value: list of subject statuses
bin_scheme = {
    # Key: (lowerbound, upperbound inclusive), value: increment size
    (0, 12): 1,
    (12, 24): 3,
    (24, 48): 6,
    (48, 96): 12,
    (96, float('inf')): 24
}

# noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
for days, status in zip(days_slice, status_slice):
    hours = days * 24
    for (lowerbound, upperbound), increment in bin_scheme.items():
        if lowerbound < hours <= upperbound:
            hours = math.ceil(hours / increment) * increment
            if hours not in mapping:
                mapping[hours] = list()
            mapping[hours].append(status)
            break

percent_survival = lambda lst: (1.0 - lst.count('DOA') / len(lst)) * 100
x = list(sorted(mapping.keys()))
y = list(percent_survival(mapping[hours]) for hours in x)
for hours, survival_rate in zip(x, y):
    print('Survival rate at {} hours = {:.3f}%'.format(hours, survival_rate))

if '-T' in sys.argv:
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    plt.plot(x, p(x), 'r-')
    print('Trendline: y = {:.3f}x + {:.3f}'.format(*z))

if '-E' in sys.argv:
    for (lowerbound, upperbound), increment in bin_scheme.items():
        bin_x = list(hours for hours in x if lowerbound < hours <= upperbound)
        bin_y = list(y[x.index(hours)] for hours in bin_x)
        # Variation using standard deviations
        stddev_y = np.std(bin_y)
        stddev_x = np.std(bin_x)
        print('σ of survival rates of bin from {} to {} = {:.3f}'.format(
            lowerbound, upperbound, stddev_y))
        # Add 1.96 * stddev_x as fourth argument if you want an xerr errorbar
        plt.errorbar(np.average(bin_x), np.average(bin_y), 1.96 * stddev_y)

elif '-B' in sys.argv:
    data, positions, widths = list(), list(), list()
    for (lowerbound, upperbound), increment in bin_scheme.items():
        bin_x = list(hours for hours in x if lowerbound < hours <= upperbound)
        bin_y = list(y[x.index(hours)] for hours in bin_x)
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
plt.scatter(x, y)
plt.get_current_fig_manager().resize(1250, 881)
plt.show()
